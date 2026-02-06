"""
数据质量评估指标模块测试：compute_quality_metrics。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
from src.preprocessing.quality_metrics import compute_quality_metrics
from src.preprocessing.doc_index import build_doc_index, load_doc_index


def test_compute_quality_metrics():
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
    metrics = compute_quality_metrics(entries, results_dir)
    assert "by_doc" in metrics
    assert "total_chunks" in metrics
    assert "total_unique_after_dedup" in metrics
    assert "duplicate_rate" in metrics
    assert "section_coverage" in metrics
    assert isinstance(metrics["by_doc"], dict)
    for doc_id, stat in metrics["by_doc"].items():
        assert "chunk_count" in stat
        assert "avg_len" in stat
        assert "min_len" in stat
        assert "max_len" in stat
    assert metrics["duplicate_rate"] >= 0 and metrics["duplicate_rate"] <= 1
    sc = metrics["section_coverage"]
    assert "by_doc" in sc
    assert "overall" in sc
    assert 0 <= sc["overall"] <= 1
