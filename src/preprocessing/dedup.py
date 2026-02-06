"""
3.3.1 重复内容检测和去重：基于文本 hash 或向量相似度，对切片列表去重。
供 chroma_ingest 或独立脚本调用。
"""
from __future__ import annotations

import hashlib
from typing import List, Tuple

from .splitter import ChunkWithMeta


def _normalize_text(content: str) -> str:
    """归一化文本：去首尾空白、合并空白，便于 hash 判重。"""
    return " ".join(content.split())


def find_duplicate_chunks(
    chunks: List[ChunkWithMeta],
    method: str = "hash",
) -> List[Tuple[int, int]]:
    """
    检测重复切片，返回重复对 (index_first, index_duplicate) 列表。
    method="hash"：文本归一化后 MD5，相同 hash 视为重复（保留首次出现的索引为 first）。
    """
    if method != "hash":
        raise ValueError(f"Unsupported method: {method}")
    seen: dict[str, int] = {}
    pairs: List[Tuple[int, int]] = []
    for i, c in enumerate(chunks):
        text = _normalize_text(c.get("content", ""))
        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        if h in seen:
            pairs.append((seen[h], i))
        else:
            seen[h] = i
    return pairs


def dedup_chunks(
    chunks: List[ChunkWithMeta],
    method: str = "hash",
) -> List[ChunkWithMeta]:
    """
    去重：保留首次出现的切片，后续重复项丢弃。
    返回去重后的切片列表（顺序保持首次出现顺序）。
    """
    if method != "hash":
        raise ValueError(f"Unsupported method: {method}")
    seen: dict[str, int] = {}
    out: List[ChunkWithMeta] = []
    for c in chunks:
        text = _normalize_text(c.get("content", ""))
        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        if h in seen:
            continue
        seen[h] = len(out)
        out.append(c)
    return out
