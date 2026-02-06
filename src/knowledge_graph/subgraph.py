"""
子图查询：从指定节点出发有界 BFS 遍历，返回 nodes/edges 供前端可视化。
防止一次性加载全图，单次最多返回 max_nodes 个节点（默认 50）。
"""
from __future__ import annotations

import os
from typing import Any

MAX_SUBGRAPH_NODES = 50
REL_TYPES = "PREREQUISITE", "COVERS", "TEACHES", "PRACTICES", "DEPENDS_ON"


def _get_driver():
    from neo4j import GraphDatabase
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        raise ValueError("NEO4J_PASSWORD is required for Neo4j. Set it in .env")
    return GraphDatabase.driver(uri, auth=(user, password))


def _node_label_and_display(node) -> tuple[str, str]:
    """从 Neo4j Node 得到 type（Topic/Exercise/Concept）和展示用 label。"""
    labels = list(node.labels) if hasattr(node, "labels") else []
    node_type = labels[0] if labels else "Node"
    node_id = node.get("id", "") if hasattr(node, "get") else ""
    if node_type == "Topic":
        label = node.get("name_en") or node.get("name") or node_id
    elif node_type == "Exercise":
        label = node.get("title") or node_id
    elif node_type == "Concept":
        label = node.get("name") or node_id
    else:
        label = node_id
    return node_type, (label or node_id)[:24]


def get_subgraph(
    seed_id: str,
    max_depth: int = 2,
    max_nodes: int = MAX_SUBGRAPH_NODES,
) -> dict[str, Any]:
    """
    从 seed_id 出发 BFS 遍历，返回 { "nodes": [ { "id", "label", "type" } ], "edges": [ { "source", "target", "type" } ] }。
    节点数超过 max_nodes 时按与 seed 的距离优先保留，再按度数截断；边只保留两端均在节点集合内的。
    """
    driver = _get_driver()
    nodes_list: list[dict[str, Any]] = []
    edges_list: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    edges_set: set[tuple[str, str, str]] = set()
    node_info: dict[str, dict[str, Any]] = {}

    try:
        with driver.session() as session:
            # 解析关系类型用于 Cypher
            rel_pattern = "|".join(REL_TYPES)

            # 1) 取种子节点
            r = session.run(
                """
                MATCH (n) WHERE n.id = $seed_id
                RETURN n LIMIT 1
                """,
                seed_id=seed_id,
            )
            rec = r.single()
            if not rec or not rec.get("n"):
                return {"nodes": [], "edges": [], "error": None}

            seed_node = rec["n"]
            node_type, label = _node_label_and_display(seed_node)
            node_info[seed_id] = {"id": seed_id, "label": label, "type": node_type}
            node_ids.add(seed_id)

            frontier = {seed_id}
            depth = 0

            while depth < max_depth:
                if not frontier:
                    break
                next_frontier = set()
                # 2) 从当前 frontier 沿所有关系类型找邻居（无向）
                q = (
                    f"MATCH (a)-[r:{rel_pattern}]-(b) "
                    "WHERE a.id IN $frontier RETURN a.id AS aid, type(r) AS rel, b AS bnode"
                )
                result = session.run(q, frontier=list(frontier))
                for row in result:
                    aid = row["aid"]
                    rel = row["rel"]
                    bnode = row["bnode"]
                    bid = bnode.get("id") if hasattr(bnode, "get") else None
                    if not bid:
                        continue
                    edges_set.add((aid, bid, rel))
                    next_frontier.add(bid)
                    if bid not in node_ids:
                        node_ids.add(bid)
                        b_type, b_label = _node_label_and_display(bnode)
                        node_info[bid] = {"id": bid, "label": b_label, "type": b_type}
                frontier = next_frontier
                depth += 1
                if len(node_ids) >= max_nodes:
                    break
    finally:
        driver.close()

    # 3) 若超过 max_nodes，按“距离”优先：先保留 seed，再保留 1 跳、2 跳…（此处用 BFS 顺序即距离），再按度数截断
    if len(node_ids) > max_nodes:
        # 简单策略：按 node_info 键顺序截断到 max_nodes（BFS 时插入顺序近似距离）
        ordered_ids = [seed_id] + [i for i in node_info if i != seed_id][: max_nodes - 1]
        node_ids = set(ordered_ids[:max_nodes])
        edges_set = {(a, b, t) for a, b, t in edges_set if a in node_ids and b in node_ids}

    for nid in node_ids:
        if nid in node_info:
            nodes_list.append(node_info[nid])
    for a, b, t in edges_set:
        edges_list.append({"source": a, "target": b, "type": t})

    return {"nodes": nodes_list, "edges": edges_list}
