"""
2.4.3 图谱验证与优化：先修链合理性、概念覆盖完整性、Neo4j 索引。
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# 本课程期望的讲次顺序
EXPECTED_LECTURE_IDS = ["lec01", "lec02", "lec03", "lec04", "lec05"]


def validate_prerequisite_chain(session) -> tuple[bool, list[str]]:
    """
    2.4.3.1：检查 PREREQUISITE 链是否连续（lec01→lec02→…→lec05），无断链、无反向。
    返回 (是否通过, 问题描述列表)。
    """
    problems: list[str] = []
    result = session.run(
        """
        MATCH (a:Topic)-[r:PREREQUISITE]->(b:Topic)
        WHERE a.id STARTS WITH 'lec' AND b.id STARTS WITH 'lec'
        RETURN a.id AS from_id, b.id AS to_id
        ORDER BY from_id
        """
    )
    edges = [(r["from_id"], r["to_id"]) for r in result]
    expected_pairs = list(zip(EXPECTED_LECTURE_IDS[:-1], EXPECTED_LECTURE_IDS[1:]))
    for from_id, to_id in expected_pairs:
        if (from_id, to_id) not in edges:
            problems.append(f"缺失先修边: {from_id} -> {to_id}")
    for from_id, to_id in edges:
        if (from_id, to_id) not in expected_pairs:
            problems.append(f"多余或反向先修边: {from_id} -> {to_id}")
    return len(problems) == 0, problems


def validate_concept_coverage(session) -> tuple[bool, dict[str, Any]]:
    """
    2.4.3.2：检查每讲是否有至少一个 Concept、每个 Topic 是否有 TEACHES 边。
    返回 (是否通过, 详情 { lecture_id: concept_count, missing_teaches: [...] } )。
    """
    details: dict[str, Any] = {"by_lecture": {}, "missing_teaches": []}
    for lid in EXPECTED_LECTURE_IDS:
        result = session.run(
            """
            MATCH (c:Concept)
            WHERE c.source_lecture = $lid
            RETURN count(c) AS n
            """,
            lid=lid,
        )
        n = result.single()["n"] if result else 0
        details["by_lecture"][lid] = n
    result = session.run(
        """
        MATCH (t:Topic)
        WHERE t.id STARTS WITH 'lec'
        OPTIONAL MATCH (t)-[:TEACHES]->(c:Concept)
        WITH t, count(c) AS teach_count
        WHERE teach_count = 0
        RETURN t.id AS topic_id
        """
    )
    details["missing_teaches"] = [r["topic_id"] for r in result]
    ok = all(details["by_lecture"].get(lid, 0) >= 1 for lid in EXPECTED_LECTURE_IDS) and len(details["missing_teaches"]) == 0
    return ok, details


def ensure_indexes(session) -> None:
    """
    2.4.3.3：为 Topic.id、Concept.id、Exercise.id 创建索引（若不存在），优化 MATCH 查询。
    """
    index_specs = [
        ("topic_id", "Topic", "id"),
        ("concept_id", "Concept", "id"),
        ("exercise_id", "Exercise", "id"),
        ("concept_source_lecture", "Concept", "source_lecture"),
    ]
    for name, label, prop in index_specs:
        try:
            session.run(
                f"CREATE INDEX {name} IF NOT EXISTS FOR (n:{label}) ON (n.{prop})"
            )
        except Exception as e:
            logger.warning("创建索引 %s 失败: %s", name, e)


def run_validation(session) -> dict[str, Any]:
    """执行全部验证并返回汇总结果。"""
    prereq_ok, prereq_problems = validate_prerequisite_chain(session)
    concept_ok, concept_details = validate_concept_coverage(session)
    return {
        "prerequisite_chain": {"ok": prereq_ok, "problems": prereq_problems},
        "concept_coverage": {"ok": concept_ok, "details": concept_details},
    }
