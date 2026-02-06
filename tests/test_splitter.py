"""
文档切片模块测试：slice_document、chunk_metadata_for_chroma。
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pytest
from src.preprocessing.splitter import slice_document, chunk_metadata_for_chroma, ChunkWithMeta
from src.preprocessing.doc_index import build_doc_index


def test_slice_document_and_metadata():
    results_dir = ROOT / "results"
    if not results_dir.is_dir():
        pytest.skip("results/ not found")
    entries = build_doc_index(results_dir, None)
    entry = next(e for e in entries if e["doc_id"] == "lec01")
    path = Path(entry["file_path"])
    if not path.is_file():
        pytest.skip("lec01 .md not found")
    chunks = slice_document(path, entry)
    assert len(chunks) >= 1
    for c in chunks:
        assert "content" in c and "doc_id" in c and "chunk_index" in c and "total_chunks" in c
        assert c["doc_id"] == "lec01"
        assert c["total_chunks"] == len(chunks)
    meta = chunk_metadata_for_chroma(chunks[0])
    assert meta["source_file"] and meta["doc_type"] == "lecture" and meta["doc_id"] == "lec01"
    assert isinstance(meta["chunk_index"], int) and isinstance(meta["total_chunks"], int)
