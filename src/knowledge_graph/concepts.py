"""
2.4.2 概念抽取与细粒度关系：从讲义章节标题抽取 Concept，建立 TEACHES、PRACTICES、DEPENDS_ON。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import TypedDict

try:
    from src.preprocessing.md_loader import load_md
except ImportError:
    from preprocessing.md_loader import load_md


class Concept(TypedDict):
    id: str
    name: str
    name_en: str
    source_lecture: str
    description: str
    order: int
    difficulty: str  # 3.2.3 basic | intermediate | advanced


def slugify(title: str) -> str:
    """将标题转为可作 id 后缀的 slug（小写、空格与非法字符替换为下划线）。"""
    s = title.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "_", s)
    s = s.strip("_")
    return s or "section"


def extract_concepts_from_lecture(path: Path, doc_id: str) -> list[Concept]:
    """
    从讲义 .md 的章节标题（## / ###）抽取概念列表。
    使用 md_loader.load_md 与 parse_md_headings 的 section 列表，跳过 level 1（文档标题）。
    """
    path = Path(path)
    if not path.is_file():
        return []
    _, sections = load_md(path)
    concepts: list[Concept] = []
    order = 0
    for sec in sections:
        if sec["level"] < 2:
            continue
        title = (sec.get("title") or "").strip()
        if not title:
            continue
        slug = slugify(title)
        cid = f"{doc_id}_{slug}"
        # 避免同讲内重复 slug（如多个 "Signals"）
        seen = {c["id"] for c in concepts}
        if cid in seen:
            cid = f"{doc_id}_{slug}_{order}"
        concepts.append({
            "id": cid,
            "name": title,
            "name_en": title,
            "source_lecture": doc_id,
            "description": "",
            "order": order,
        })
        order += 1
    # 3.2.1 无 section 或仅 level 1 的讲义兜底：保证每讲至少一个 Concept
    if not concepts:
        concepts.append({
            "id": f"{doc_id}_overview",
            "name": "Overview",
            "name_en": "Overview",
            "source_lecture": doc_id,
            "description": "",
            "order": 0,
        })
    # 3.2.3 按 section 顺序赋难度：前 1/3 basic、中 intermediate、后 1/3 advanced
    n = len(concepts)
    for i, c in enumerate(concepts):
        if n <= 1:
            c["difficulty"] = "intermediate"
        elif i < n // 3:
            c["difficulty"] = "basic"
        elif i >= (2 * n) // 3:
            c["difficulty"] = "advanced"
        else:
            c["difficulty"] = "intermediate"
    return concepts


def _lecture_entries(doc_index: list[dict]) -> list[dict]:
    """从文档索引中取出所有 lecture 条目，按 lecture_index 排序。"""
    lectures = [e for e in doc_index if e.get("doc_type") == "lecture"]
    return sorted(lectures, key=lambda e: e.get("lecture_index", 0))


def _homework_entries(doc_index: list[dict]) -> list[dict]:
    """从文档索引中取出所有 homework 条目，按序号排序。"""
    hw = [e for e in doc_index if e.get("doc_type") == "homework"]
    return sorted(hw, key=lambda e: e.get("lecture_index", 0))


def ingest_concepts_and_relations_to_neo4j(
    session,
    doc_index: list[dict],
    results_dir: Path | None = None,
) -> int:
    """
    将 Concept 节点及 TEACHES、PRACTICES、DEPENDS_ON 关系写入当前 Neo4j session。
    使用 doc_index 中的 file_path 定位讲义；results_dir 未用时由 file_path 推导。
    返回写入的 Concept 数量。
    """
    lectures = _lecture_entries(doc_index)
    homework = _homework_entries(doc_index)
    concepts_by_lecture: dict[str, list[Concept]] = {}

    for entry in lectures:
        doc_id = entry["doc_id"]
        path = Path(entry.get("file_path", ""))
        if not path.is_file() and results_dir:
            path = Path(results_dir) / path.name
        if not path.is_file():
            continue
        concepts = extract_concepts_from_lecture(path, doc_id)
        concepts_by_lecture[doc_id] = concepts

        for c in concepts:
            session.run(
                """
                MERGE (c:Concept {id: $id})
                SET c.name = $name, c.name_en = $name_en, c.source_lecture = $source_lecture,
                    c.description = $description, c.order = $order, c.difficulty = $difficulty
                """,
                id=c["id"],
                name=c["name"],
                name_en=c["name_en"],
                source_lecture=c["source_lecture"],
                description=c["description"],
                order=c["order"],
                difficulty=c.get("difficulty", "intermediate"),
            )

        topic_id = doc_id
        for c in concepts:
            session.run(
                """
                MATCH (t:Topic {id: $topic_id}), (c:Concept {id: $concept_id})
                MERGE (t)-[:TEACHES]->(c)
                """,
                topic_id=topic_id,
                concept_id=c["id"],
            )

    # PRACTICES: hw0i -> 该讲下全部 Concept（related_lec 对应）
    for hw_entry in homework:
        ex_id = hw_entry["doc_id"]
        related_lec = hw_entry.get("related_lec")
        if not related_lec or related_lec not in concepts_by_lecture:
            continue
        for c in concepts_by_lecture[related_lec]:
            session.run(
                """
                MATCH (e:Exercise {id: $ex_id}), (c:Concept {id: $concept_id})
                MERGE (e)-[:PRACTICES]->(c)
                """,
                ex_id=ex_id,
                concept_id=c["id"],
            )

    # DEPENDS_ON: 同讲内按 order 链（3.2.2 type=same_lecture, weight=1.0）；跨讲（type=cross_lecture, weight=0.8）
    for doc_id, concepts in concepts_by_lecture.items():
        for i in range(len(concepts) - 1):
            session.run(
                """
                MATCH (a:Concept {id: $from_id}), (b:Concept {id: $to_id})
                MERGE (a)-[r:DEPENDS_ON]->(b)
                SET r.type = $rel_type, r.weight = $weight
                """,
                from_id=concepts[i]["id"],
                to_id=concepts[i + 1]["id"],
                rel_type="same_lecture",
                weight=1.0,
            )
    # 跨讲：前一讲最后一个概念 -> 下一讲第一个概念
    for k in range(len(lectures) - 1):
        curr_id = lectures[k]["doc_id"]
        next_id = lectures[k + 1]["doc_id"]
        curr_c = concepts_by_lecture.get(curr_id, [])
        next_c = concepts_by_lecture.get(next_id, [])
        if curr_c and next_c:
            session.run(
                """
                MATCH (a:Concept {id: $from_id}), (b:Concept {id: $to_id})
                MERGE (a)-[r:DEPENDS_ON]->(b)
                SET r.type = $rel_type, r.weight = $weight
                """,
                from_id=curr_c[-1]["id"],
                to_id=next_c[0]["id"],
                rel_type="cross_lecture",
                weight=0.8,
            )

    return sum(len(cs) for cs in concepts_by_lecture.values())
