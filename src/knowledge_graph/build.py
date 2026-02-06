"""
从文档索引与讲义信息构建知识图谱：Topic、Exercise 节点及 PREREQUISITE、COVERS 关系，并导入 Neo4j。
对应任务 2.4.1～2.4.4。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TypedDict

# 从项目根可导入 preprocessing
try:
    from src.preprocessing.doc_index import load_doc_index, build_doc_index
except ImportError:
    from preprocessing.doc_index import load_doc_index, build_doc_index


class Topic(TypedDict):
    id: str
    name: str
    name_en: str
    order: int
    difficulty: str
    description: str


class Exercise(TypedDict):
    id: str
    title: str
    difficulty: str
    source: str
    problem_type: str


def _lecture_entries(doc_index: list[dict]) -> list[dict]:
    """从文档索引中取出所有 lecture 条目，按 lecture_index 排序。"""
    lectures = [e for e in doc_index if e.get("doc_type") == "lecture"]
    return sorted(lectures, key=lambda e: e.get("lecture_index", 0))


def _homework_entries(doc_index: list[dict]) -> list[dict]:
    """从文档索引中取出所有 homework 条目（不含 solution），按序号排序。"""
    hw = [e for e in doc_index if e.get("doc_type") == "homework"]
    return sorted(hw, key=lambda e: e.get("lecture_index", 0))


def build_topics_and_exercises(doc_index: list[dict]) -> tuple[list[Topic], list[Exercise]]:
    """
    2.4.1 / 2.4.3：从文档索引生成 Topic 列表（lec01～lec05）和 Exercise 列表（hw01～hw05）。
    Topic 使用 data.json 的 title 作为 name_en，doc_id 作为 id；先修关系按 order 在导入时建立。
    """
    topics: list[Topic] = []
    for e in _lecture_entries(doc_index):
        doc_id = e["doc_id"]
        order = e.get("lecture_index", 0)
        name_en = e.get("title", doc_id)
        topics.append({
            "id": doc_id,
            "name": doc_id,
            "name_en": name_en,
            "order": order,
            "difficulty": "intermediate",
            "description": e.get("description", ""),
        })

    exercises: list[Exercise] = []
    for e in _homework_entries(doc_index):
        doc_id = e["doc_id"]
        exercises.append({
            "id": doc_id,
            "title": e.get("title", doc_id),
            "difficulty": "intermediate",
            "source": f"homework-{doc_id[2:]}",
            "problem_type": "mixed",
        })

    return topics, exercises


def ingest_to_neo4j(
    topics: list[Topic],
    exercises: list[Exercise],
    *,
    uri: str | None = None,
    user: str | None = None,
    password: str | None = None,
    clear_first: bool = True,
    doc_index: list[dict] | None = None,
    results_dir: Path | None = None,
) -> None:
    """
    2.4.4：将 Topic、Exercise 及 PREREQUISITE、COVERS 写入 Neo4j；
    若提供 doc_index 与 results_dir，则再写入 2.4.2 的 Concept 与 TEACHES/PRACTICES/DEPENDS_ON。
    clear_first: 是否先删除本课程相关节点与关系（含 Concept），避免重复导入。
    """
    uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = user or os.getenv("NEO4J_USER", "neo4j")
    password = password or os.getenv("NEO4J_PASSWORD")
    if not password:
        raise ValueError("NEO4J_PASSWORD is required for Neo4j ingest")

    from neo4j import GraphDatabase

    try:
        from src.knowledge_graph import concepts as concepts_module
    except ImportError:
        from . import concepts as concepts_module

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            if clear_first:
                session.run("MATCH (c:Concept) WHERE c.id STARTS WITH 'lec' DETACH DELETE c")
                session.run("MATCH (t:Topic) WHERE t.id STARTS WITH 'lec' OR t.id STARTS WITH 'hw' DETACH DELETE t")
                session.run("MATCH (e:Exercise) WHERE e.id STARTS WITH 'hw' DETACH DELETE e")

            for t in topics:
                session.run(
                    """
                    MERGE (t:Topic {id: $id})
                    SET t.name = $name, t.name_en = $name_en, t.order = $order,
                        t.difficulty = $difficulty, t.description = $description
                    """,
                    id=t["id"],
                    name=t["name"],
                    name_en=t["name_en"],
                    order=t["order"],
                    difficulty=t["difficulty"],
                    description=t["description"],
                )

            for e in exercises:
                session.run(
                    """
                    MERGE (e:Exercise {id: $id})
                    SET e.title = $title, e.difficulty = $difficulty, e.source = $source, e.problem_type = $problem_type
                    """,
                    id=e["id"],
                    title=e["title"],
                    difficulty=e["difficulty"],
                    source=e["source"],
                    problem_type=e["problem_type"],
                )

            # PREREQUISITE: lec01 -> lec02 -> ... -> lec05（3.2.2 按讲次细化 strength：首尾稍低、中间稍高）
            n_t = len(topics)
            for i in range(n_t - 1):
                strength = 0.75 if (i == 0 or i == n_t - 2) else 0.85
                session.run(
                    """
                    MATCH (a:Topic {id: $from_id}), (b:Topic {id: $to_id})
                    MERGE (a)-[r:PREREQUISITE]->(b)
                    SET r.strength = $strength
                    """,
                    from_id=topics[i]["id"],
                    to_id=topics[i + 1]["id"],
                    strength=strength,
                )

            # COVERS: lec0i -> hw0i（3.2.2 relevance 固定 0.9，与 design 一致）
            for t, ex in zip(topics, exercises):
                session.run(
                    """
                    MATCH (t:Topic {id: $topic_id}), (e:Exercise {id: $ex_id})
                    MERGE (t)-[r:COVERS]->(e)
                    SET r.relevance = $relevance
                    """,
                    topic_id=t["id"],
                    ex_id=ex["id"],
                    relevance=0.9,
                )

            # 2.4.2 概念抽取与细粒度关系
            if doc_index is not None and results_dir is not None:
                concepts_module.ingest_concepts_and_relations_to_neo4j(
                    session, doc_index, Path(results_dir)
                )

            # 2.4.3.3 索引（优化 MATCH 查询）
            try:
                from src.knowledge_graph import validate as validate_module
            except ImportError:
                from . import validate as validate_module
            validate_module.ensure_indexes(session)
    finally:
        driver.close()


def build_and_ingest_graph(
    doc_index_path: Path | None = None,
    results_dir: Path | None = None,
    data_root: Path | None = None,
    *,
    clear_neo4j_first: bool = True,
) -> tuple[int, int]:
    """
    一站式：加载或构建文档索引 -> 生成 Topic/Exercise -> 写入 Neo4j（含 2.4.2 概念与关系）。
    返回 (topic_count, exercise_count)。
    """
    if doc_index_path and Path(doc_index_path).is_file():
        doc_index = load_doc_index(Path(doc_index_path))
        if results_dir is None and doc_index:
            # 从索引中任一条目的 file_path 推导 results 目录
            for e in doc_index:
                fp = e.get("file_path")
                if fp:
                    results_dir = Path(fp).parent
                    break
    elif results_dir is not None:
        results_dir = Path(results_dir)
        data_root = Path(data_root) if data_root else None
        doc_index = build_doc_index(results_dir, data_root)
    else:
        raise ValueError("Provide doc_index_path or results_dir to build doc index")

    results_dir = Path(results_dir) if results_dir else None
    topics, exercises = build_topics_and_exercises(doc_index)
    ingest_to_neo4j(
        topics,
        exercises,
        clear_first=clear_neo4j_first,
        doc_index=doc_index,
        results_dir=results_dir,
    )
    return len(topics), len(exercises)


if __name__ == "__main__":
    import sys
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    os.chdir(root)
    from dotenv import load_dotenv
    load_dotenv(root / ".env")

    index_path = root / "config" / "doc_index.json"
    results_dir = root / "results"
    data_root = root / "data" / "res.6-007-spring-2011"
    n_t, n_e = build_and_ingest_graph(doc_index_path=index_path, clear_neo4j_first=True)
    print(f"Neo4j: {n_t} topics, {n_e} exercises (PREREQUISITE + COVERS created).")
