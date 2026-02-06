"""
RAG 检索工具单元测试：_expand_query_for_retrieve、_chroma_where、retrieve_documents、rag_retrieve。
纯逻辑测试不依赖 Chroma；需 Chroma 的用例在无库或未安装时 skip。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.agent.tools.rag import (
    _expand_query_for_retrieve,
    _chroma_where,
    retrieve_documents,
    rag_retrieve,
)


def test_expand_query_for_retrieve():
    """_expand_query_for_retrieve 纯逻辑：含中文关键词时追加英文。"""
    assert "convolution" in _expand_query_for_retrieve("卷积")
    assert "Fourier" in _expand_query_for_retrieve("傅里叶变换")
    assert "linear time-invariant" in _expand_query_for_retrieve("线性时不变")
    assert _expand_query_for_retrieve("") == ""
    assert _expand_query_for_retrieve("  ") == "  "
    assert _expand_query_for_retrieve("only English") == "only English"


def test_chroma_where():
    """_chroma_where 将 filters 转为 Chroma where 格式。"""
    assert _chroma_where(None) is None
    assert _chroma_where({}) is None
    assert _chroma_where({"doc_id": "lec01"}) == {"doc_id": {"$eq": "lec01"}}
    out = _chroma_where({"doc_id": "lec01", "doc_type": "lecture"})
    assert "$and" in out
    assert len(out["$and"]) == 2


def test_retrieve_documents_mock_chroma():
    """retrieve_documents 在 mock Chroma 下返回 Document 列表及 metadata。"""
    import sys as _sys
    fake_docs = [
        ("content one", {"doc_id": "lec01", "source_file": "lec01.md", "section_title": "Intro"}),
        ("content two", {"doc_id": "lec01", "source_file": "lec01.md", "section_title": ""}),
    ]
    mock_chroma = MagicMock()
    client = MagicMock()
    col = MagicMock()
    col.query.return_value = {
        "documents": [[c for c, _ in fake_docs]],
        "metadatas": [[m for _, m in fake_docs]],
        "distances": [[0.1, 0.2]],
    }
    client.get_or_create_collection.return_value = col
    mock_chroma.PersistentClient.return_value = client
    with patch.dict(_sys.modules, {"chromadb": mock_chroma}):
        docs = retrieve_documents("test query", top_k=2, persist_dir="/tmp/test")
    assert len(docs) == 2
    assert docs[0].page_content == "content one"
    assert docs[0].metadata.get("doc_id") == "lec01"
    assert docs[0].metadata.get("source_file") == "lec01.md"


def test_rag_retrieve_tool_returns_string_with_cite_format():
    """rag_retrieve 工具返回字符串，含「第X讲」等引用格式。"""
    from langchain_core.documents import Document
    with patch("src.agent.tools.rag.retrieve_documents") as m:
        m.return_value = [
            Document(page_content="convolution definition", metadata={"doc_id": "lec04", "section_title": "卷积"}),
        ]
        out = rag_retrieve.invoke({"query": "卷积", "top_k": 5})
    assert isinstance(out, str)
    assert "第4讲" in out or "参见" in out
    assert "课程材料" in out or "检索" in out


def test_rag_retrieve_empty_result():
    """无检索结果时返回提示字符串。"""
    with patch("src.agent.tools.rag.retrieve_documents", return_value=[]):
        out = rag_retrieve.invoke({"query": "nonexistent"})
    assert "未在课程材料" in out or "相关片段" in out
