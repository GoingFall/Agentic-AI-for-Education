"""
3.2.4.1 章节-切片映射：基于 slice_document 结果构建 doc_id -> sections -> chunks 结构。
供 3.2.4.2/3.2.4.3 展示与 concept_id 关联使用。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .doc_index import load_doc_index, build_doc_index
from .md_loader import load_md
from .splitter import slice_document, ChunkWithMeta


def build_section_chunk_map(
    entries: list[dict],
    results_dir: Path | None = None,
) -> dict[str, Any]:
    """
    从文档索引与切片结果构建章节-切片映射。
    返回形如：
    {
      "documents": {
        "doc_id": [
          { "section_title": str, "section_level": int, "chunks": [{"chunk_index": int}, ...] },
          ...
        ],
        ...
      }
    }
    按文档内出现顺序排列 section；无章节的 chunk 归入 section_title=""、section_level=0。
    """
    results_dir = Path(results_dir) if results_dir else None
    documents: dict[str, list[dict[str, Any]]] = {}

    for e in entries:
        path = Path(e.get("file_path", ""))
        if not path.is_file() and results_dir:
            path = results_dir / path.name
        if not path.is_file():
            continue
        doc_id = e.get("doc_id", "")
        if not doc_id:
            continue
        _, sections = load_md(path)
        chunks = slice_document(path, e)
        if not chunks:
            documents[doc_id] = []
            continue

        # section_title -> level（从 sections 取，仅 level>=2）
        title_to_level: dict[str, int] = {}
        for sec in sections:
            if sec.get("level", 0) >= 2:
                t = (sec.get("title") or "").strip()
                if t:
                    title_to_level[t] = sec.get("level", 2)

        # 按 chunk 顺序分组：相同 section_title 的连续 chunk 归为一 section
        doc_sections: list[dict[str, Any]] = []
        current_title: str | None = None
        current_chunks: list[dict[str, int]] = []

        for c in chunks:
            title = c.get("section_title") or ""
            if title != current_title:
                if current_title is not None and current_chunks:
                    doc_sections.append({
                        "section_title": current_title,
                        "section_level": title_to_level.get(current_title, 0),
                        "chunks": current_chunks,
                    })
                current_title = title
                current_chunks = []
            current_chunks.append({"chunk_index": c["chunk_index"]})

        if current_title is not None and current_chunks:
            doc_sections.append({
                "section_title": current_title,
                "section_level": title_to_level.get(current_title, 0),
                "chunks": current_chunks,
            })

        documents[doc_id] = doc_sections

    return {"documents": documents}
