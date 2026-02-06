"""
知识图谱构建测试：build_topics_and_exercises、build_and_ingest_graph（Neo4j 需配置 NEO4J_PASSWORD 才执行导入）。
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pytest
from src.knowledge_graph.build import (
    build_topics_and_exercises,
    build_and_ingest_graph,
    _lecture_entries,
    _homework_entries,
)


def test_build_topics_and_exercises():
    doc_index = [
        {"doc_id": "lec01", "doc_type": "lecture", "lecture_index": 1, "title": "Lecture 1, Introduction", "description": "Intro"},
        {"doc_id": "lec02", "doc_type": "lecture", "lecture_index": 2, "title": "Lecture 2", "description": ""},
        {"doc_id": "hw01", "doc_type": "homework", "lecture_index": 1, "title": "Homework 1"},
        {"doc_id": "hw02", "doc_type": "homework", "lecture_index": 2, "title": "Homework 2"},
    ]
    topics, exercises = build_topics_and_exercises(doc_index)
    assert len(topics) == 2
    assert topics[0]["id"] == "lec01" and topics[0]["name_en"] == "Lecture 1, Introduction"
    assert len(exercises) == 2
    assert exercises[0]["id"] == "hw01"
    assert _lecture_entries(doc_index) == [doc_index[0], doc_index[1]]
    assert _homework_entries(doc_index) == [doc_index[2], doc_index[3]]


def test_build_and_ingest_graph_from_index():
    index_path = ROOT / "config" / "doc_index.json"
    if not index_path.is_file():
        pytest.skip("config/doc_index.json not found")
    if not os.getenv("NEO4J_PASSWORD"):
        pytest.skip("NEO4J_PASSWORD not set, skipping Neo4j ingest")
    n_t, n_e = build_and_ingest_graph(doc_index_path=index_path, clear_neo4j_first=True)
    assert n_t == 5
    assert n_e == 5
