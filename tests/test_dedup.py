"""
重复内容检测与去重模块测试：_normalize_text、find_duplicate_chunks、dedup_chunks。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
from src.preprocessing.dedup import (
    _normalize_text,
    find_duplicate_chunks,
    dedup_chunks,
)
from src.preprocessing.splitter import ChunkWithMeta


def test_normalize_text():
    assert _normalize_text("  a  b  c  ") == "a b c"
    assert _normalize_text("Line1\n\n\nLine2") == "Line1 Line2"
    assert _normalize_text("") == ""


def test_find_duplicate_chunks_empty():
    pairs = find_duplicate_chunks([], method="hash")
    assert pairs == []


def test_find_duplicate_chunks_no_duplicate():
    chunks: list[ChunkWithMeta] = [
        {"content": "A", "source_file": "f", "doc_type": "lecture", "doc_id": "d1",
         "section_title": "", "chunk_index": 0, "total_chunks": 2, "content_type": "text", "title": None},
        {"content": "B", "source_file": "f", "doc_type": "lecture", "doc_id": "d1",
         "section_title": "", "chunk_index": 1, "total_chunks": 2, "content_type": "text", "title": None},
    ]
    pairs = find_duplicate_chunks(chunks, method="hash")
    assert pairs == []


def test_find_duplicate_chunks_with_duplicate():
    chunks: list[ChunkWithMeta] = [
        {"content": "Same", "source_file": "f1", "doc_type": "lecture", "doc_id": "d1",
         "section_title": "", "chunk_index": 0, "total_chunks": 3, "content_type": "text", "title": None},
        {"content": "Other", "source_file": "f1", "doc_type": "lecture", "doc_id": "d1",
         "section_title": "", "chunk_index": 1, "total_chunks": 3, "content_type": "text", "title": None},
        {"content": "  Same  ", "source_file": "f2", "doc_type": "lecture", "doc_id": "d2",
         "section_title": "", "chunk_index": 0, "total_chunks": 1, "content_type": "text", "title": None},
    ]
    pairs = find_duplicate_chunks(chunks, method="hash")
    assert len(pairs) == 1
    assert pairs[0] == (0, 2)


def test_find_duplicate_chunks_unsupported_method():
    with pytest.raises(ValueError, match="Unsupported method"):
        find_duplicate_chunks([], method="vector")


def test_dedup_chunks():
    chunks: list[ChunkWithMeta] = [
        {"content": "First", "source_file": "f", "doc_type": "lecture", "doc_id": "d1",
         "section_title": "", "chunk_index": 0, "total_chunks": 3, "content_type": "text", "title": None},
        {"content": "Second", "source_file": "f", "doc_type": "lecture", "doc_id": "d1",
         "section_title": "", "chunk_index": 1, "total_chunks": 3, "content_type": "text", "title": None},
        {"content": "  First  ", "source_file": "f", "doc_type": "lecture", "doc_id": "d1",
         "section_title": "", "chunk_index": 2, "total_chunks": 3, "content_type": "text", "title": None},
    ]
    out = dedup_chunks(chunks, method="hash")
    assert len(out) == 2
    assert out[0]["content"] == "First"
    assert out[1]["content"] == "Second"


def test_dedup_chunks_unsupported_method():
    with pytest.raises(ValueError, match="Unsupported method"):
        dedup_chunks([], method="other")
