"""
RAG 检索工具：封装 Chroma 检索，支持元数据过滤与排序，暴露为 LangChain @tool。
与 design 2.2.1 对齐：retrieve_documents(query, top_k, filters) -> Document 列表。
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.tools import tool

# 与 chroma_ingest 一致
COLLECTION_NAME = "course_docs"

# 轻量 query 扩展：检索时追加英文/同义词，提高与讲义表述的匹配率（数据中常含英文术语）
_QUERY_EXPAND_TERMS: list[tuple[str, str]] = [
    ("卷积", "convolution"),
    ("傅里叶", "Fourier"),
    ("线性时不变", "LTI linear time-invariant"),
    ("离散时间信号", "discrete-time signal"),
    ("LTI", "linear time-invariant"),
]

_logger = logging.getLogger(__name__)


def _chroma_where(filters: dict[str, Any] | None) -> dict[str, Any] | None:
    """将 filters 转为 Chroma where 格式；标量值视为 $eq。Chroma 要求顶层为单一运算符，多条件用 $and。"""
    if not filters:
        return None
    clauses = []
    for k, v in filters.items():
        if v is None:
            continue
        if isinstance(v, dict) and any(str(x).startswith("$") for x in v):
            clauses.append({k: v})
        else:
            clauses.append({k: {"$eq": v}})
    if not clauses:
        return None
    # Chroma：多键时顶层须为单一运算符；$and 至少需 2 个表达式，故单条件直接返回
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def _expand_query_for_retrieve(query: str) -> str:
    """在 query 后追加中英对照词，便于向量检索命中讲义中的英文表述。"""
    if not query or not query.strip():
        return query
    q = query.strip()
    added: list[str] = []
    for zh, en in _QUERY_EXPAND_TERMS:
        if zh in q and en not in q:
            added.append(en)
    if added:
        return q + " " + " ".join(added)
    return q


def retrieve_documents(
    query: str,
    top_k: int = 5,
    filters: dict[str, Any] | None = None,
    *,
    persist_dir: str | None = None,
    min_score: float | None = None,
) -> list[Document]:
    """
    从 Chroma 检索相关文档片段。
    - query: 查询文本
    - top_k: 返回条数
    - filters: 元数据过滤，如 {"doc_id": "lec01", "doc_type": "lecture"}；与 splitter.chunk_metadata_for_chroma 字段一致
    - persist_dir: Chroma 持久化目录，默认从 CHROMA_PERSIST_DIR 或项目 chroma_db 读取
    - min_score: 可选最小相似度阈值，Chroma 返回的 distance 为越小越相似，部分版本返回 similarity 则越大越相似；不设则不按分数过滤
    返回 LangChain Document 列表（content + metadata）。
    """
    try:
        import chromadb
    except ImportError:
        raise RuntimeError("chromadb not installed. Run: pip install chromadb")

    persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR")
    if not persist_dir:
        # 与 chroma_ingest 默认一致：项目根下 chroma_db
        root = Path(__file__).resolve().parents[3]
        persist_dir = str(root / "chroma_db")

    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(COLLECTION_NAME, metadata={"description": "course docs RAG"})

    # 轻量扩展 query，提高与讲义中英混合表述的匹配
    search_query = _expand_query_for_retrieve(query)
    where = _chroma_where(filters)
    res = collection.query(
        query_texts=[search_query],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    docs: list[Document] = []
    if not res or not res.get("documents") or not res["documents"][0]:
        if os.environ.get("RAG_DEBUG"):
            _logger.info("RAG retrieve_documents query=%r expanded=%r top_k=%s -> 0 docs", query, search_query, top_k)
        return docs
    if os.environ.get("RAG_DEBUG"):
        _logger.info(
            "RAG retrieve_documents query=%r expanded=%r top_k=%s -> %s docs",
            query,
            search_query,
            top_k,
            len(res["documents"][0]),
        )
    for i, content in enumerate(res["documents"][0]):
        meta = (res.get("metadatas") or [[]])[0]
        m = dict(meta[i]) if i < len(meta) else {}
        distances = (res.get("distances") or [[]])[0]
        if distances and i < len(distances):
            m["_distance"] = float(distances[i])
        if min_score is not None and m.get("_distance") is not None:
            # Chroma 默认 L2：距离越小越相似；若需按 similarity 过滤可后续扩展
            if m["_distance"] > min_score:
                continue
        docs.append(Document(page_content=content or "", metadata=m))
    return docs


# 默认 top_k 略增以提高召回，便于概念类问题命中
DEFAULT_RAG_TOP_K = 8


@tool
def rag_retrieve(
    query: str,
    top_k: int = DEFAULT_RAG_TOP_K,
    doc_id: str | None = None,
    doc_type: str | None = None,
    content_type: str | None = None,
) -> str:
    """
    从课程文档向量库中检索与问题相关的片段。用于答疑时查找讲义/作业中的依据。
    - query: 用户问题或关键词
    - top_k: 返回最多几条片段（默认 8）
    - doc_id: 可选，限定文档 id，如 lec01、hw02
    - doc_type: 可选，限定类型：lecture、homework、solution
    - content_type: 可选，限定内容类型
    返回检索到的片段摘要文本，供生成带引用的回答。
    """
    filters: dict[str, Any] = {}
    if doc_id is not None:
        filters["doc_id"] = doc_id
    if doc_type is not None:
        filters["doc_type"] = doc_type
    if content_type is not None:
        filters["content_type"] = content_type
    documents = retrieve_documents(query, top_k=top_k, filters=filters or None)
    if not documents:
        return "未在课程材料中找到相关片段。"
    parts = []
    for i, doc in enumerate(documents, 1):
        meta = doc.metadata
        doc_id = meta.get("doc_id") or meta.get("source_file", "") or ""
        section = meta.get("section_title", "") or ""
        # 引用格式：lec01 → 第1讲，hw01 → 作业01；便于回答中写「参见第 X 讲 / 章节 Y」
        if doc_id.startswith("lec") and len(doc_id) >= 5 and doc_id[3:5].isdigit():
            cite_source = f"第{int(doc_id[3:5])}讲"
        elif doc_id.startswith("hw") and len(doc_id) >= 4 and doc_id[2:4].isdigit():
            cite_source = f"作业{int(doc_id[2:4])}"
        else:
            cite_source = doc_id or "课程材料"
        line = f"[{i}] 参见：{cite_source}" + (f"，章节：{section}" if section else "") + f"\n{doc.page_content[:500]}{'...' if len(doc.page_content) > 500 else ''}"
        parts.append(line)
    return "以下为检索到的课程材料片段（引用时请用「参见第 X 讲 / 章节 Y」）：\n\n" + "\n\n".join(parts)
