"""
章节-切片映射模块测试：build_section_chunk_map。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
from src.preprocessing.doc_index import build_doc_index, load_doc_index
from src.preprocessing.section_chunk_map import build_section_chunk_map


def test_build_section_chunk_map():
    results_dir = ROOT / "results"
    if not results_dir.is_dir():
        pytest.skip("results/ not found")
    index_path = ROOT / "config" / "doc_index.json"
    if index_path.is_file():
        entries = load_doc_index(index_path)
    else:
        entries = build_doc_index(results_dir, None)
    if not entries:
        pytest.skip("no doc index entries")
    mapping = build_section_chunk_map(entries, results_dir)
    assert "documents" in mapping
    documents = mapping["documents"]
    assert isinstance(documents, dict)
    for doc_id, sections in documents.items():
        assert isinstance(doc_id, str)
        assert isinstance(sections, list)
        for sec in sections:
            assert "section_title" in sec
            assert "section_level" in sec
            assert "chunks" in sec
            for c in sec["chunks"]:
                assert "chunk_index" in c


def test_build_section_chunk_map_empty_entries():
    mapping = build_section_chunk_map([], None)
    assert mapping == {"documents": {}}
