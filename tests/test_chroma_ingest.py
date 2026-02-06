"""
Chroma 写入流水线测试：ingest_results_to_chroma 返回切片数并创建集合（需 chromadb）。
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pytest
from src.preprocessing.chroma_ingest import ingest_results_to_chroma, COLLECTION_NAME


def test_ingest_results_to_chroma():
    results_dir = ROOT / "results"
    if not results_dir.is_dir():
        pytest.skip("results/ not found")
    index_path = ROOT / "config" / "doc_index.json"
    if not index_path.is_file():
        pytest.skip("config/doc_index.json not found")
    try:
        import chromadb
    except ImportError:
        pytest.skip("chromadb not installed")
    persist_dir = str(ROOT / "chroma_db_test_ingest")
    n, name = ingest_results_to_chroma(
        results_dir,
        ROOT / "data" / "res.6-007-spring-2011",
        persist_dir=persist_dir,
        index_path=index_path,
    )
    assert name == COLLECTION_NAME
    assert n > 0
    client = chromadb.PersistentClient(path=persist_dir)
    col = client.get_collection(COLLECTION_NAME)
    assert col.count() == n
    # 清理测试库
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    import shutil
    if Path(persist_dir).is_dir():
        try:
            shutil.rmtree(persist_dir)
        except Exception:
            pass
