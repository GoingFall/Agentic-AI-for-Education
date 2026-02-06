"""
知识图谱查询工具：先修关系、COVERS 推荐作业、TEACHES/PRACTICES 概念关联、学习路径验证。
封装 Neo4j 查询，暴露为 LangChain @tool，供推荐与答疑 Skill 使用。
"""
from __future__ import annotations

import os
from typing import Any

from langchain_core.tools import tool

# 与 knowledge_graph 一致
EXPECTED_LECTURE_IDS = ["lec01", "lec02", "lec03", "lec04", "lec05"]


def _get_driver():
    from neo4j import GraphDatabase
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        raise ValueError("NEO4J_PASSWORD is required for Neo4j. Set it in .env")
    return GraphDatabase.driver(uri, auth=(user, password))


def _run_cypher(fn):
    """在 Neo4j session 上执行 fn(session)，返回 fn 的返回值。"""
    driver = _get_driver()
    try:
        with driver.session() as session:
            return fn(session)
    finally:
        driver.close()


def query_next_topic(topic_id: str) -> list[dict[str, Any]]:
    """先修关系：当前 topic 的下一讲（沿 PREREQUISITE 的后继）。"""
    def run(session):
        result = session.run(
            """
            MATCH (t:Topic {id: $topic_id})-[:PREREQUISITE]->(next:Topic)
            RETURN next.id AS id, next.name_en AS name_en, next.order AS order
            ORDER BY next.order
            """,
            topic_id=topic_id,
        )
        return [{"id": r["id"], "name_en": r["name_en"], "order": r["order"]} for r in result]
    return _run_cypher(run)


def query_covers_exercises(topic_id: str) -> list[dict[str, Any]]:
    """COVERS：该讲对应的作业列表。"""
    def run(session):
        result = session.run(
            """
            MATCH (t:Topic {id: $topic_id})-[:COVERS]->(e:Exercise)
            RETURN e.id AS id, e.title AS title, e.difficulty AS difficulty
            """,
            topic_id=topic_id,
        )
        return [{"id": r["id"], "title": r["title"], "difficulty": r["difficulty"]} for r in result]
    return _run_cypher(run)


def query_teaches_concepts(topic_id: str) -> list[dict[str, Any]]:
    """TEACHES：该讲教授的概念。"""
    def run(session):
        result = session.run(
            """
            MATCH (t:Topic {id: $topic_id})-[:TEACHES]->(c:Concept)
            RETURN c.id AS id, c.name AS name, c.difficulty AS difficulty
            ORDER BY c.order
            """,
            topic_id=topic_id,
        )
        return [{"id": r["id"], "name": r["name"], "difficulty": r["difficulty"]} for r in result]
    return _run_cypher(run)


def query_practices_concepts(exercise_id: str) -> list[dict[str, Any]]:
    """PRACTICES：该作业练习的概念。"""
    def run(session):
        result = session.run(
            """
            MATCH (e:Exercise {id: $exercise_id})-[:PRACTICES]->(c:Concept)
            RETURN c.id AS id, c.name AS name
            """,
            exercise_id=exercise_id,
        )
        return [{"id": r["id"], "name": r["name"]} for r in result]
    return _run_cypher(run)


def validate_path(learned_topic_ids: list[str], recommended_topic_id: str) -> tuple[bool, str]:
    """
    学习路径验证：推荐目标 recommended_topic_id 的先修是否都在 learned_topic_ids 中。
    返回 (是否合法, 说明文本)。
    """
    learned = set(learned_topic_ids)
    if recommended_topic_id in learned:
        return True, "该目标已在已学列表中。"

    def run(session):
        result = session.run(
            """
            MATCH (t:Topic)-[:PREREQUISITE*]->(end:Topic {id: $recommended_id})
            WHERE t.id <> end.id
            RETURN DISTINCT t.id AS id
            """,
            recommended_id=recommended_topic_id,
        )
        return [r["id"] for r in result]

    prereqs = _run_cypher(run)
    missing = [p for p in prereqs if p not in learned]
    if not missing:
        return True, "推荐目标的所有先修均已在已学列表中。"
    return False, f"推荐前需先学习：{', '.join(missing)}。"


@tool
def graph_query_next_topic(topic_id: str) -> str:
    """
    查询指定讲次的「下一步学什么」：沿先修关系返回下一讲。
    - topic_id: 当前讲次 id，如 lec01、lec02
    返回下一讲的 id 与名称，供生成推荐理由。
    """
    items = query_next_topic(topic_id)
    if not items:
        return f"未找到 {topic_id} 的后续讲次（可能已是最后一讲）。"
    return "；".join(f"{x['id']}: {x.get('name_en') or x['id']}" for x in items)


@tool
def graph_query_covers_exercises(topic_id: str) -> str:
    """
    查询某讲对应的推荐作业（COVERS 关系）。
    - topic_id: 讲次 id，如 lec03
    返回该讲对应的作业 id 与标题，供推荐练习时使用。
    """
    items = query_covers_exercises(topic_id)
    if not items:
        return f"未找到 {topic_id} 对应的作业。"
    return "；".join(f"{x['id']}: {x.get('title') or x['id']}" for x in items)


@tool
def graph_query_concept_relations(
    topic_or_exercise_id: str,
    query_type: str = "teaches",
) -> str:
    """
    查询讲次或作业与概念的关联（TEACHES：该讲教什么概念；PRACTICES：该作业练什么概念）。
    - topic_or_exercise_id: 讲次 id（lec0x）或作业 id（hw0x）
    - query_type: "teaches" 表示按讲查概念，"practices" 表示按作业查概念
    返回概念 id 与名称列表。
    """
    if query_type == "teaches":
        items = query_teaches_concepts(topic_or_exercise_id)
    elif query_type == "practices":
        items = query_practices_concepts(topic_or_exercise_id)
    else:
        return f"query_type 需为 teaches 或 practices，当前为 {query_type}。"
    if not items:
        return f"未找到 {topic_or_exercise_id} 的关联概念。"
    return "；".join(f"{x['id']}: {x.get('name') or x['id']}" for x in items)


def query_concept_depends(concept_id: str) -> list[dict[str, Any]]:
    """沿 DEPENDS_ON 查询该概念的后继概念（学习顺序上的后续）。"""
    def run(session):
        result = session.run(
            """
            MATCH (start:Concept {id: $concept_id})-[:DEPENDS_ON*1..]->(c:Concept)
            RETURN DISTINCT c.id AS id, c.name AS name, c.source_lecture AS topic_id, c.difficulty AS difficulty
            ORDER BY c.source_lecture, c.id
            """,
            concept_id=concept_id,
        )
        return [{"id": r["id"], "name": r["name"], "topic_id": r["topic_id"], "difficulty": r["difficulty"]} for r in result]
    return _run_cypher(run)


@tool
def graph_query_concept_depends(concept_id: str) -> str:
    """
    查询某概念沿 DEPENDS_ON 的后续概念（用于概念推荐）。
    - concept_id: 概念 id，如 lec01_xxx
    返回后续概念 id、名称、所属讲次，供推荐相关概念时使用。
    """
    items = query_concept_depends(concept_id)
    if not items:
        return f"未找到 {concept_id} 的后续依赖概念。"
    return "；".join(f"{x['id']}: {x.get('name') or x['id']}（{x.get('topic_id') or ''}）" for x in items)


@tool
def graph_validate_path(learned_topic_ids: str, recommended_topic_id: str) -> str:
    """
    验证推荐目标是否满足先修：确保推荐不跳过先修。
    - learned_topic_ids: 已学讲次 id，逗号分隔，如 "lec01,lec02,lec03"
    - recommended_topic_id: 待推荐的讲次 id，如 lec04
    返回是否合法及说明，供推荐逻辑使用。
    """
    learned = [x.strip() for x in learned_topic_ids.split(",") if x.strip()]
    ok, msg = validate_path(learned, recommended_topic_id.strip())
    return f"验证结果：{'通过' if ok else '不通过'}。{msg}"


def get_all_graph_tools() -> list[Any]:
    """返回所有知识图谱相关 LangChain 工具，供全局注册与 Skill 按 allowed_tools 筛选。"""
    return [
        graph_query_next_topic,
        graph_query_covers_exercises,
        graph_query_concept_relations,
        graph_query_concept_depends,
        graph_validate_path,
    ]
