"""
从 Neo4j 读取本课程知识图谱（Topic、Exercise、PREREQUISITE、COVERS），
可选含 Concept 与 TEACHES/PRACTICES/DEPENDS_ON，绘制为图片并保存到 docs/。
需配置 .env 中的 NEO4J_URI、NEO4J_USER、NEO4J_PASSWORD，且已运行过知识图谱导入。

用法:
  python scripts/export_knowledge_graph_figure.py                    # 仅 Topic + Exercise（主图）
  python scripts/export_knowledge_graph_figure.py -c full            # 含全量 Concept（易拥挤）
  python scripts/export_knowledge_graph_figure.py -c sample -l lec01 # 单讲示例图（推荐，可读性高）
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")


def _fetch_base_graph(session) -> tuple[list[tuple[str, str]], list[tuple[str, str, str]]]:
    """从 Neo4j 拉取 Topic、Exercise 及 PREREQUISITE、COVERS。"""
    nodes: list[tuple[str, str]] = []
    edges: list[tuple[str, str, str]] = []
    r = session.run("""
        MATCH (t:Topic) WHERE t.id STARTS WITH 'lec' RETURN t.id AS id, 'Topic' AS label
        UNION
        MATCH (e:Exercise) WHERE e.id STARTS WITH 'hw' RETURN e.id AS id, 'Exercise' AS label
    """)
    for rec in r:
        nodes.append((rec["id"], rec["label"]))
    r = session.run("""
        MATCH (a:Topic)-[:PREREQUISITE]->(b:Topic)
        WHERE a.id STARTS WITH 'lec'
        RETURN a.id AS from_id, b.id AS to_id, 'PREREQUISITE' AS type
    """)
    for rec in r:
        edges.append((rec["from_id"], rec["to_id"], rec["type"]))
    r = session.run("""
        MATCH (t:Topic)-[:COVERS]->(e:Exercise)
        WHERE t.id STARTS WITH 'lec'
        RETURN t.id AS from_id, e.id AS to_id, 'COVERS' AS type
    """)
    for rec in r:
        edges.append((rec["from_id"], rec["to_id"], rec["type"]))
    return nodes, edges


def _fetch_concepts(session) -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str]]]:
    """拉取 Concept 节点（id, label=Concept, source_lecture）及 TEACHES/PRACTICES/DEPENDS_ON 边。"""
    nodes: list[tuple[str, str, str]] = []  # (id, label, source_lecture)
    edges: list[tuple[str, str, str]] = []
    r = session.run("""
        MATCH (c:Concept) WHERE c.id STARTS WITH 'lec'
        RETURN c.id AS id, c.source_lecture AS source_lecture
    """)
    for rec in r:
        nodes.append((rec["id"], "Concept", rec["source_lecture"]))
    r = session.run("""
        MATCH (t:Topic)-[:TEACHES]->(c:Concept)
        WHERE t.id STARTS WITH 'lec'
        RETURN t.id AS from_id, c.id AS to_id, 'TEACHES' AS type
    """)
    for rec in r:
        edges.append((rec["from_id"], rec["to_id"], rec["type"]))
    r = session.run("""
        MATCH (e:Exercise)-[:PRACTICES]->(c:Concept)
        WHERE e.id STARTS WITH 'hw'
        RETURN e.id AS from_id, c.id AS to_id, 'PRACTICES' AS type
    """)
    for rec in r:
        edges.append((rec["from_id"], rec["to_id"], rec["type"]))
    r = session.run("""
        MATCH (a:Concept)-[:DEPENDS_ON]->(b:Concept)
        WHERE a.id STARTS WITH 'lec' AND b.id STARTS WITH 'lec'
        RETURN a.id AS from_id, b.id AS to_id, 'DEPENDS_ON' AS type
    """)
    for rec in r:
        edges.append((rec["from_id"], rec["to_id"], rec["type"]))
    return nodes, edges


def _filter_concepts_to_lecture(
    concept_nodes: list[tuple[str, str, str]],
    concept_edges: list[tuple[str, str, str]],
    lecture: str,
) -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str]]]:
    """保留指定讲（如 lec01）的 Concept 及与之相关的 TEACHES/PRACTICES/同讲内 DEPENDS_ON。"""
    hw_id = "hw" + lecture[-2:]
    nodes = [(nid, label, src) for nid, label, src in concept_nodes if src == lecture]
    cids = {nid for nid, _, _ in nodes}
    edges: list[tuple[str, str, str]] = []
    for a, b, typ in concept_edges:
        if typ == "TEACHES" and a == lecture and b in cids:
            edges.append((a, b, typ))
        elif typ == "PRACTICES" and a == hw_id and b in cids:
            edges.append((a, b, typ))
        elif typ == "DEPENDS_ON" and a in cids and b in cids:
            edges.append((a, b, typ))
    return nodes, edges


def _draw_lecture_sample(
    lecture: str,
    concept_nodes: list[tuple[str, str, str]],
    concept_edges: list[tuple[str, str, str]],
    out_path: Path,
) -> None:
    """单讲示例图：1 Topic + 1 Exercise + 该讲 Concept，TEACHES/PRACTICES/DEPENDS_ON；可读性高。"""
    import networkx as nx
    import matplotlib.pyplot as plt

    hw_id = "hw" + lecture[-2:]
    base_nodes = [(lecture, "Topic"), (hw_id, "Exercise")]
    base_edges = [(lecture, hw_id, "COVERS")]
    G = nx.DiGraph()
    for nid, label in base_nodes:
        G.add_node(nid, label=label)
    for nid, label, src in concept_nodes:
        G.add_node(nid, label=label, source_lecture=src)
    for a, b, typ in base_edges + concept_edges:
        G.add_edge(a, b, type=typ)

    topic_nodes = [n for n in G.nodes() if G.nodes[n].get("label") == "Topic"]
    exercise_nodes = [n for n in G.nodes() if G.nodes[n].get("label") == "Exercise"]
    concept_nodes_list = [n for n in G.nodes() if G.nodes[n].get("label") == "Concept"]

    # 布局：Topic 上、Exercise 下；概念分两行，左右均匀排开，减少边重叠
    pos = {}
    pos[lecture] = (0.0, 2.2)
    pos[hw_id] = (0.0, 0.0)
    n_c = len(concept_nodes_list)
    half = (n_c + 1) // 2
    width = 5.0
    for j, cid in enumerate(concept_nodes_list):
        if j < half:
            # 上行
            x = (j / max(half - 1, 1) - 0.5) * width
            pos[cid] = (x, 1.35)
        else:
            # 下行
            x = ((j - half) / max(n_c - half - 1, 1) - 0.5) * width
            pos[cid] = (x, 0.65)

    plt.figure(figsize=(12, 7))
    nx.draw_networkx_nodes(G, pos, nodelist=topic_nodes, node_color="lightblue", node_size=1800, label="Topic")
    nx.draw_networkx_nodes(G, pos, nodelist=exercise_nodes, node_color="lightgreen", node_size=1400, label="Exercise")
    nx.draw_networkx_nodes(G, pos, nodelist=concept_nodes_list, node_color="wheat", node_size=500, label="Concept", edgecolors="gray")

    teaches = [(a, b) for a, b, t in concept_edges if t == "TEACHES"]
    practices = [(a, b) for a, b, t in concept_edges if t == "PRACTICES"]
    depends = [(a, b) for a, b, t in concept_edges if t == "DEPENDS_ON"]
    covers = [(a, b) for a, b, t in base_edges if t == "COVERS"]
    # 边带弧度，减少多边重合
    connectionstyle = "arc3,rad=0.15"
    nx.draw_networkx_edges(G, pos, edgelist=depends, edge_color="orange", arrowsize=10, width=0.9, alpha=0.85)
    nx.draw_networkx_edges(G, pos, edgelist=practices, edge_color="forestgreen", style="dotted", arrowsize=12, width=1.0, alpha=0.85, connectionstyle=connectionstyle)
    nx.draw_networkx_edges(G, pos, edgelist=teaches, edge_color="steelblue", arrowsize=12, width=1.0, alpha=0.85, connectionstyle=connectionstyle)
    nx.draw_networkx_edges(G, pos, edgelist=covers, edge_color="darkgreen", style="dashed", arrowsize=14, width=2)

    labels = {lecture: lecture, hw_id: hw_id}
    prefix = lecture + "_"
    for n in concept_nodes_list:
        short = n[len(prefix):] if n.startswith(prefix) else n
        if len(short) > 16:
            short = short[:13] + ".."
        labels[n] = short
    nx.draw_networkx_labels(G, pos, labels, font_size=8, verticalalignment="center", horizontalalignment="center")
    plt.legend(scatterpoints=1)
    plt.title(f"Knowledge Graph: Concept Layer Sample ({lecture})\nTEACHES / PRACTICES / DEPENDS_ON / COVERS")
    plt.axis("off")
    # 左下角图例：说明概念节点标签含义（英文避免 CJK 字体缺失）
    ax = plt.gca()
    note = (
        "Concept labels = slug of section headings.\n"
        "DEPENDS_ON: same_lecture weight=1.0, cross_lecture weight=0.8."
    )
    ax.text(0.02, 0.02, note, transform=ax.transAxes, fontsize=7, verticalalignment="bottom",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="wheat", alpha=0.9, edgecolor="gray"))
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def _draw_base_only(
    nodes: list[tuple[str, str]],
    edges: list[tuple[str, str, str]],
    out_path: Path,
) -> None:
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph()
    for nid, label in nodes:
        G.add_node(nid, label=label)
    for a, b, typ in edges:
        G.add_edge(a, b, type=typ)

    topic_nodes = [n for n in G.nodes() if G.nodes[n].get("label") == "Topic"]
    exercise_nodes = [n for n in G.nodes() if G.nodes[n].get("label") == "Exercise"]
    pos = {}
    for i, n in enumerate(sorted(topic_nodes)):
        pos[n] = (i * 1.5, 1.0)
    for i, n in enumerate(sorted(exercise_nodes)):
        pos[n] = (i * 1.5, 0.0)

    plt.figure(figsize=(10, 5))
    nx.draw_networkx_nodes(G, pos, nodelist=topic_nodes, node_color="lightblue", node_size=1200, label="Topic")
    nx.draw_networkx_nodes(G, pos, nodelist=exercise_nodes, node_color="lightgreen", node_size=1000, label="Exercise")
    prereq_edges = [(a, b) for a, b, t in edges if t == "PREREQUISITE"]
    covers_edges = [(a, b) for a, b, t in edges if t == "COVERS"]
    nx.draw_networkx_edges(G, pos, edgelist=prereq_edges, edge_color="gray", arrowsize=20, width=2)
    nx.draw_networkx_edges(G, pos, edgelist=covers_edges, edge_color="darkgreen", style="dashed", arrowsize=16, width=1.5)
    nx.draw_networkx_labels(G, pos, font_size=10)
    plt.legend(scatterpoints=1)
    plt.title("Knowledge Graph: Topic (lec) & Exercise (hw)\nGray = PREREQUISITE (strength 0.75/0.85), Dashed = COVERS (relevance 0.9)")
    plt.axis("off")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def _draw_with_concepts(
    base_nodes: list[tuple[str, str]],
    base_edges: list[tuple[str, str, str]],
    concept_nodes: list[tuple[str, str, str]],
    concept_edges: list[tuple[str, str, str]],
    out_path: Path,
) -> None:
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph()
    for nid, label in base_nodes:
        G.add_node(nid, label=label)
    for nid, label, src in concept_nodes:
        G.add_node(nid, label=label, source_lecture=src)
    for a, b, typ in base_edges + concept_edges:
        G.add_edge(a, b, type=typ)

    topic_nodes = [n for n in G.nodes() if G.nodes[n].get("label") == "Topic"]
    exercise_nodes = [n for n in G.nodes() if G.nodes[n].get("label") == "Exercise"]
    concept_nodes_list = [n for n in G.nodes() if G.nodes[n].get("label") == "Concept"]

    # 布局：Topic 上排，Concept 中排（按 source_lecture 分组），Exercise 下排
    pos = {}
    lec_order = [f"lec{i:02d}" for i in range(1, 6)]
    for i, n in enumerate(sorted(topic_nodes)):
        pos[n] = (i * 3.0, 2.0)
    for i, n in enumerate(sorted(exercise_nodes)):
        pos[n] = (i * 3.0, 0.0)
    # 每讲概念放在该讲 Topic 下方一横条，按 order 稀疏排
    by_lecture: dict[str, list[str]] = {}
    for nid, _label, src in concept_nodes:
        by_lecture.setdefault(src, []).append(nid)
    for src in lec_order:
        cids = by_lecture.get(src, [])
        base_x = lec_order.index(src) * 3.0 if src in lec_order else 0.0
        if not cids:
            continue
        for j, cid in enumerate(cids):
            # 在 base_x 两侧均匀排开，最多占宽 2
            n = len(cids)
            x = base_x + (j / max(n - 1, 1) - 0.5) * 2.0
            pos[cid] = (x, 1.0)

    plt.figure(figsize=(14, 8))
    nx.draw_networkx_nodes(G, pos, nodelist=topic_nodes, node_color="lightblue", node_size=1400, label="Topic")
    nx.draw_networkx_nodes(G, pos, nodelist=exercise_nodes, node_color="lightgreen", node_size=1000, label="Exercise")
    nx.draw_networkx_nodes(G, pos, nodelist=concept_nodes_list, node_color="wheat", node_size=400, label="Concept", edgecolors="gray")
    prereq = [(a, b) for a, b, t in base_edges + concept_edges if t == "PREREQUISITE"]
    covers = [(a, b) for a, b, t in base_edges + concept_edges if t == "COVERS"]
    teaches = [(a, b) for a, b, t in concept_edges if t == "TEACHES"]
    practices = [(a, b) for a, b, t in concept_edges if t == "PRACTICES"]
    depends = [(a, b) for a, b, t in concept_edges if t == "DEPENDS_ON"]
    # 先画细/半透明边，最后画 COVERS 和 PREREQUISITE，避免被遮挡
    nx.draw_networkx_edges(G, pos, edgelist=depends, edge_color="orange", arrowsize=8, width=0.6, alpha=0.6)
    nx.draw_networkx_edges(G, pos, edgelist=practices, edge_color="forestgreen", style="dotted", arrowsize=10, width=0.8, alpha=0.7)
    nx.draw_networkx_edges(G, pos, edgelist=teaches, edge_color="steelblue", arrowsize=12, width=1.0, alpha=0.8)
    nx.draw_networkx_edges(G, pos, edgelist=prereq, edge_color="gray", arrowsize=18, width=2)
    nx.draw_networkx_edges(G, pos, edgelist=covers, edge_color="darkgreen", style="dashed", arrowsize=14, width=2)
    # 仅标 Topic/Exercise，Concept 不标避免重叠不可读
    labels = {n: n for n in topic_nodes + exercise_nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=10)
    plt.legend(scatterpoints=1)
    plt.title("Knowledge Graph (with Concepts)\nGray=PREREQUISITE, Dashed=COVERS, Blue=TEACHES, Green dotted=PRACTICES, Orange=DEPENDS_ON")
    plt.axis("off")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export knowledge graph from Neo4j to PNG.")
    parser.add_argument("--concept", "-c", choices=["full", "sample"], default=None, help="full=全量概念图, sample=单讲示例图（可读性高）")
    parser.add_argument("--lecture", "-l", default="lec01", metavar="LEC", help="与 -c sample 配合，指定讲次（如 lec01）。")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output path (default 见下).")
    args = parser.parse_args()

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        print("SKIP: NEO4J_PASSWORD not set. Set in .env and run: python -m src.knowledge_graph.build")
        sys.exit(0)

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("ERROR: neo4j not installed. pip install neo4j")
        sys.exit(1)

    driver = GraphDatabase.driver(uri, auth=(user, password))
    base_nodes: list[tuple[str, str]] = []
    base_edges: list[tuple[str, str, str]] = []
    concept_nodes: list[tuple[str, str, str]] = []
    concept_edges: list[tuple[str, str, str]] = []
    try:
        with driver.session() as session:
            base_nodes, base_edges = _fetch_base_graph(session)
            if args.concept:
                concept_nodes, concept_edges = _fetch_concepts(session)
    finally:
        driver.close()

    if not base_nodes:
        print("No Topic/Exercise in Neo4j; drawing from expected structure (lec01..lec05, hw01..hw05).")
        base_nodes = [(f"lec{i:02d}", "Topic") for i in range(1, 6)] + [(f"hw{i:02d}", "Exercise") for i in range(1, 6)]
        base_edges = [(f"lec{i:02d}", f"lec{i+1:02d}", "PREREQUISITE") for i in range(1, 5)]
        base_edges += [(f"lec{i:02d}", f"hw{i:02d}", "COVERS") for i in range(1, 6)]

    try:
        import networkx as nx
        import matplotlib.pyplot as plt
    except ImportError:
        print("Install graph deps: pip install networkx matplotlib")
        sys.exit(1)

    use_sample = args.concept == "sample"
    if use_sample:
        concept_nodes, concept_edges = _filter_concepts_to_lecture(concept_nodes, concept_edges, args.lecture)

    docs_task2 = ROOT / "docs" / "task2"
    if args.output is not None:
        out_path = Path(args.output)
    else:
        if use_sample:
            out_path = docs_task2 / f"knowledge_graph_concepts_sample_{args.lecture}.png"
        elif args.concept == "full":
            out_path = docs_task2 / "knowledge_graph_with_concepts.png"
        else:
            out_path = docs_task2 / "knowledge_graph.png"

    if use_sample:
        if concept_nodes:
            _draw_lecture_sample(args.lecture, concept_nodes, concept_edges, out_path)
            print(f"Saved (concept sample {args.lecture}): {out_path}")
        else:
            base_one = [(args.lecture, "Topic"), ("hw" + args.lecture[-2:], "Exercise")]
            edge_one = [(args.lecture, "hw" + args.lecture[-2:], "COVERS")]
            _draw_base_only(base_one, edge_one, out_path)
            print(f"No concepts for {args.lecture}; saved base-only: {out_path}")
    elif args.concept == "full" and concept_nodes:
        _draw_with_concepts(base_nodes, base_edges, concept_nodes, concept_edges, out_path)
        print(f"Saved (full concepts): {out_path}")
    elif args.concept == "full" and not concept_nodes:
        print("No Concept nodes in Neo4j; falling back to base-only figure.")
        _draw_base_only(base_nodes, base_edges, out_path)
        print(f"Saved: {out_path}")
    else:
        _draw_base_only(base_nodes, base_edges, out_path)
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
