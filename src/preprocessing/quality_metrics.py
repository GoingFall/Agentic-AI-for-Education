"""
3.3.3 数据质量评估指标：基于切片与 section 映射计算 chunk 数、长度、重复率、section 覆盖率等。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .doc_index import load_doc_index, build_doc_index
from .splitter import slice_document
from .dedup import find_duplicate_chunks
from .section_chunk_map import build_section_chunk_map


def compute_quality_metrics(
    entries: list[dict],
    results_dir: Path,
) -> dict[str, Any]:
    """
    计算数据质量指标。
    返回包含以下键的字典：
    - by_doc: doc_id -> { chunk_count, avg_len, min_len, max_len }
    - total_chunks, total_unique_after_dedup
    - duplicate_rate (0~1)
    - section_coverage: { doc_id -> ratio } 及 overall
    """
    results_dir = Path(results_dir)
    all_chunks: list[dict] = []
    doc_chunks: dict[str, list[dict]] = {}

    for e in entries:
        path = Path(e.get("file_path", ""))
        if not path.is_file():
            path = results_dir / path.name
        if not path.is_file():
            continue
        doc_id = e.get("doc_id", "")
        if not doc_id:
            continue
        chunks = slice_document(path, e)
        doc_chunks[doc_id] = chunks
        all_chunks.extend(chunks)

    n_total = len(all_chunks)
    pairs = find_duplicate_chunks(all_chunks, method="hash")
    duplicate_indices = {j for _, j in pairs}
    n_unique = n_total - len(duplicate_indices)
    duplicate_rate = (len(duplicate_indices) / n_total) if n_total else 0.0

    by_doc: dict[str, dict[str, Any]] = {}
    for doc_id, chunks in doc_chunks.items():
        if not chunks:
            by_doc[doc_id] = {"chunk_count": 0, "avg_len": 0, "min_len": 0, "max_len": 0}
            continue
        lengths = [len(c.get("content", "")) for c in chunks]
        by_doc[doc_id] = {
            "chunk_count": len(chunks),
            "avg_len": round(sum(lengths) / len(lengths), 1),
            "min_len": min(lengths),
            "max_len": max(lengths),
        }

    mapping = build_section_chunk_map(entries, results_dir)
    documents_map = mapping.get("documents", {})
    section_coverage_by_doc: dict[str, float] = {}
    total_sections_with_chunk = 0
    total_sections = 0
    for doc_id, sections in documents_map.items():
        n_sec = len(sections)
        n_covered = sum(1 for s in sections if s.get("chunks"))
        total_sections += n_sec
        total_sections_with_chunk += n_covered
        section_coverage_by_doc[doc_id] = (n_covered / n_sec) if n_sec else 1.0
    overall_coverage = (total_sections_with_chunk / total_sections) if total_sections else 1.0

    return {
        "by_doc": by_doc,
        "total_chunks": n_total,
        "total_unique_after_dedup": n_unique,
        "duplicate_rate": round(duplicate_rate, 4),
        "section_coverage": {
            "by_doc": section_coverage_by_doc,
            "overall": round(overall_coverage, 4),
        },
    }
