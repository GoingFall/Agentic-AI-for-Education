"""
文档切片：按章节边界与长度切分，附加元数据，避免在公式中间切断。
对应任务 2.3.1 智能文档切片、2.3.2 元数据标注、3.3.2 优化切片策略。
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, TypedDict

from .doc_index import DocEntry
from .md_loader import load_md, Section

# design 3.1.2: 300-800 字符，重叠 50-100；3.3.2 可从环境变量覆盖
def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None:
        return default
    try:
        return int(v)
    except ValueError:
        return default


CHUNK_SIZE = _env_int("SPLITTER_CHUNK_SIZE", 600)
CHUNK_OVERLAP = _env_int("SPLITTER_CHUNK_OVERLAP", 75)
MIN_CHUNK = _env_int("SPLITTER_MIN_CHUNK", 300)
MAX_CHUNK = _env_int("SPLITTER_MAX_CHUNK", 800)


class ChunkWithMeta(TypedDict):
    content: str
    source_file: str
    doc_type: str
    doc_id: str
    section_title: str
    chunk_index: int
    total_chunks: int
    content_type: str
    title: str | None


def _find_safe_break(segment: str, search_from: int, end: int, text: str, start: int) -> int:
    """在 segment 内找切分点：优先段落、再句子、再换行；避免列表/表行中间。返回绝对 end。"""
    # 优先在 \n\n 处切
    last_break = segment.rfind("\n\n")
    if last_break != -1:
        end = search_from + last_break + 2
    else:
        last_n = segment.rfind("\n")
        if last_n != -1:
            end = search_from + last_n + 1
            # 3.3.2 避免在列表项、表格行中间切：若 end 落在以 "- " 或 "|" 开头的行内，向前移到该行前
            line_start = text.rfind("\n", start, end)
            line_start = line_start + 1 if line_start >= start else start
            line = text[line_start:end].lstrip()
            if line.startswith("- ") or line.startswith("|"):
                end = line_start
        else:
            for sep in (". ", "。 ", " "):
                idx = segment.rfind(sep)
                if idx != -1:
                    end = search_from + idx + len(sep)
                    break
    return end


def _extend_past_formula(text: str, end: int, start: int) -> int:
    """若 end 落在公式内，向后延到公式结束；返回新的 end。"""
    # 避免切断 $$ ... $$
    if "$$" in text[start:end]:
        after = text[end:]
        d = after.find("$$")
        if d != -1 and (end + d + 2) - start <= MAX_CHUNK:
            return end + d + 2
    # 避免切断 \( ... \)
    if r"\(" in text[max(0, end - 20):end] or text[end:end + 2] == r"\)":
        close = text[end:].find(r"\)")
        if close != -1 and (end + close + 2) - start <= MAX_CHUNK:
            return end + close + 2
    # 3.3.2 避免切断 \[ ... \] 块公式
    if r"\[" in text[max(0, end - 10):end] or text[end:end + 2] == r"\]":
        close = text[end:].find(r"\]")
        if close != -1 and (end + close + 2) - start <= MAX_CHUNK:
            return end + close + 2
    # 3.3.2 避免切断单 $ ... $ 行内公式（不含 $$）
    slice_before = text[start:end]
    if slice_before.count("$") % 2 == 1 and "$$" not in slice_before[-10:]:
        after = text[end:]
        d = after.find("$")
        if d != -1 and (end + d + 1) - start <= MAX_CHUNK:
            return end + d + 1
    return end


def _split_by_size(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    在不超过 chunk_size 的前提下按句子/段落边界切分，保留 overlap 字符重叠。
    避免在 $$...$$、\\(...\\)、\\[...\\]、$...$ 中间切断；避免在列表项、表格行中间切（3.3.2）。
    """
    if not text or len(text) <= chunk_size:
        return [text] if text and text.strip() else []

    chunks: list[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        if end < text_len:
            search_from = max(start, end - 150)
            segment = text[search_from : end + 100]
            end = _find_safe_break(segment, search_from, end, text, start)
            end = _extend_past_formula(text, end, start)
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(chunk_text)
        next_start = end - overlap
        if next_start <= start:
            next_start = end
        start = next_start
        if start >= text_len:
            break
    return chunks


def slice_document(
    path: Path,
    entry: DocEntry,
    *,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    max_section_chars: int = MAX_CHUNK,
) -> list[ChunkWithMeta]:
    """
    对单个 .md 文档切片：优先按章节（##/###）边界，若单节过长则按长度+重叠二次切分。
    返回带元数据的切片列表。
    """
    cleaned, sections = load_md(path)
    if not cleaned.strip():
        return []

    title = entry.get("title") or entry.get("doc_id", "")
    doc_type = entry["doc_type"]
    doc_id = entry["doc_id"]
    file_name = entry.get("file_name") or path.name
    content_type = doc_type  # lecture | homework | solution

    chunks_out: list[ChunkWithMeta] = []
    # 若无章节，整篇按长度切
    if not sections:
        sub_chunks = _split_by_size(cleaned, chunk_size=chunk_size, overlap=overlap)
        for idx, c in enumerate(sub_chunks):
            chunks_out.append({
                "content": c,
                "source_file": file_name,
                "doc_type": doc_type,
                "doc_id": doc_id,
                "section_title": "",
                "chunk_index": idx,
                "total_chunks": 0,  # 稍后统一填
                "content_type": content_type,
                "title": title,
            })
    else:
        for sec in sections:
            sec_text = cleaned[sec["start_offset"]:sec["end_offset"]].strip()
            if not sec_text:
                continue
            section_title = sec.get("title", "")
            if len(sec_text) <= max_section_chars:
                chunks_out.append({
                    "content": sec_text,
                    "source_file": file_name,
                    "doc_type": doc_type,
                    "doc_id": doc_id,
                    "section_title": section_title,
                    "chunk_index": len(chunks_out),
                    "total_chunks": 0,
                    "content_type": content_type,
                    "title": title,
                })
            else:
                sub_chunks = _split_by_size(sec_text, chunk_size=chunk_size, overlap=overlap)
                for idx, c in enumerate(sub_chunks):
                    chunks_out.append({
                        "content": c,
                        "source_file": file_name,
                        "doc_type": doc_type,
                        "doc_id": doc_id,
                        "section_title": section_title,
                        "chunk_index": len(chunks_out),
                        "total_chunks": 0,
                        "content_type": content_type,
                        "title": title,
                    })

    total = len(chunks_out)
    for c in chunks_out:
        c["total_chunks"] = total
    return chunks_out


def chunk_metadata_for_chroma(chunk: ChunkWithMeta) -> dict[str, str | int]:
    """
    转为 Chroma 可接受的 metadata（标量；Chroma 要求 str/int/float）。
    """
    meta: dict[str, str | int] = {
        "source_file": chunk["source_file"],
        "doc_type": chunk["doc_type"],
        "doc_id": chunk["doc_id"],
        "section_title": chunk["section_title"],
        "chunk_index": chunk["chunk_index"],
        "total_chunks": chunk["total_chunks"],
        "content_type": chunk["content_type"],
    }
    if chunk.get("title"):
        meta["title"] = chunk["title"]
    return meta
