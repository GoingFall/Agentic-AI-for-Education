"""
3.2.3 学习路径：从 Topic 或 Concept 沿 PREREQUISITE/DEPENDS_ON 查询后续学习序列。
供推荐 Skill 调用，仅读图不写。
"""
from __future__ import annotations


def get_learning_path_from_topic(session, topic_id: str) -> list[str]:
    """
    从某 Topic 沿 PREREQUISITE 到后续 Topic 的 id 序列（含自身）。
    例如 topic_id=lec02 返回 ['lec02', 'lec03', 'lec04', 'lec05']。
    """
    result = session.run(
        """
        MATCH (start:Topic {id: $topic_id})
        OPTIONAL MATCH (start)-[:PREREQUISITE*0..]->(t:Topic)
        WHERE t.id STARTS WITH 'lec'
        WITH t ORDER BY t.order
        WITH collect(DISTINCT t.id) AS ids
        RETURN [x IN ids WHERE x IS NOT NULL | x] AS path
        """,
        topic_id=topic_id,
    )
    row = result.single()
    if not row or not row["path"]:
        return [topic_id]
    return list(row["path"])


def get_learning_path_from_concept(
    session, concept_id: str
) -> list[dict]:
    """
    从某 Concept 沿 DEPENDS_ON 到后续 Concept 的路径。
    返回 list[dict]，每项含 topic_id、concept_id、difficulty（供推荐 Skill 使用）。
    """
    result = session.run(
        """
        MATCH (start:Concept {id: $concept_id})
        OPTIONAL MATCH (start)-[:DEPENDS_ON*0..]->(c:Concept)
        WHERE c.id STARTS WITH 'lec'
        WITH collect(DISTINCT c) AS nodes
        UNWIND nodes AS c
        WITH c ORDER BY c.source_lecture, c.order
        RETURN c.id AS concept_id, c.source_lecture AS topic_id, c.difficulty AS difficulty
        """,
        concept_id=concept_id,
    )
    out: list[dict] = []
    seen: set[str] = set()
    for rec in result:
        cid = rec.get("concept_id")
        if not cid or cid in seen:
            continue
        seen.add(cid)
        out.append({
            "topic_id": rec.get("topic_id") or "",
            "concept_id": cid,
            "difficulty": rec.get("difficulty") or "intermediate",
        })
    return out
