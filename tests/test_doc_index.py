"""
文档索引模块测试：parse_md_filename、hash_to_uuid、build_doc_index、analyze_md_structure。
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pytest
from src.preprocessing.doc_index import (
    parse_md_filename,
    hash_to_uuid,
    build_doc_index,
    analyze_md_structure,
    load_doc_index,
    save_doc_index,
)


def test_parse_md_filename():
    assert parse_md_filename("e6c75426e220f1a406b0b9be1f55bbc1_MITRES_6_007S11_lec01.md") == (
        "e6c75426e220f1a406b0b9be1f55bbc1",
        "lec01",
        "lecture",
    )
    assert parse_md_filename("d367a3c05c298bed00aae37754dd2631_MITRES_6_007S11_hw01.md") == (
        "d367a3c05c298bed00aae37754dd2631",
        "hw01",
        "homework",
    )
    assert parse_md_filename("e7e527598f89cf8dbd91432500ac53b3_MITRES_6_007S11_hw01_sol.md") == (
        "e7e527598f89cf8dbd91432500ac53b3",
        "hw01_sol",
        "solution",
    )
    assert parse_md_filename("other.pdf") is None
    assert parse_md_filename("bad_MITRES_6_007S11_lec1.md") is None


def test_hash_to_uuid():
    h = "e6c75426e220f1a406b0b9be1f55bbc1"
    assert hash_to_uuid(h) == "e6c75426-e220-f1a4-06b0-b9be1f55bbc1"


def test_build_doc_index_and_relations():
    results_dir = ROOT / "results"
    if not results_dir.is_dir():
        pytest.skip("results/ not found")
    data_root = ROOT / "data" / "res.6-007-spring-2011"
    entries = build_doc_index(results_dir, data_root if data_root.is_dir() else None)
    assert len(entries) == 15
    doc_ids = {e["doc_id"] for e in entries}
    assert "lec01" in doc_ids and "lec05" in doc_ids
    assert "hw01" in doc_ids and "hw05_sol" in doc_ids
    lec01 = next(e for e in entries if e["doc_id"] == "lec01")
    assert lec01["doc_type"] == "lecture"
    assert lec01.get("related_hw") == "hw01"
    assert lec01.get("related_sol") == "hw01_sol"
    hw01 = next(e for e in entries if e["doc_id"] == "hw01")
    assert hw01.get("related_lec") == "lec01"
    assert hw01.get("related_sol") == "hw01_sol"


def test_analyze_md_structure():
    results_dir = ROOT / "results"
    if not results_dir.is_dir():
        pytest.skip("results/ not found")
    entries = build_doc_index(results_dir, None)
    report = analyze_md_structure(entries)
    assert len(report) == len(entries)
    for r in report:
        assert "char_count" in r and "headings" in r
        assert r["headings"]["h1"] >= 0


def test_save_and_load_doc_index(tmp_path):
    entries = [
        {"file_path": "/a/lec01.md", "file_name": "x_lec01.md", "hash": "a" * 32, "doc_id": "lec01", "doc_type": "lecture", "lecture_index": 1},
    ]
    p = tmp_path / "index.json"
    save_doc_index(entries, p)
    assert p.is_file()
    loaded = load_doc_index(p)
    assert len(loaded) == 1
    assert loaded[0]["doc_id"] == "lec01"
