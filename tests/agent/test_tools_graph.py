"""
知识图谱工具单元测试：validate_path、graph_validate_path、query_next_topic 等。
通过 mock Neo4j _run_cypher 避免依赖真实数据库。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.agent.tools import graph as graph_module


def test_validate_path_already_learned():
    """推荐目标已在已学列表中时返回 (True, ...)。"""
    with patch.object(graph_module, "_run_cypher", return_value=[]):
        ok, msg = graph_module.validate_path(["lec01", "lec02"], "lec02")
    assert ok is True
    assert "已学" in msg or "已在" in msg


def test_validate_path_prereqs_met():
    """先修均满足时返回 (True, ...)。"""
    with patch.object(graph_module, "_run_cypher", return_value=["lec01", "lec02"]):
        ok, msg = graph_module.validate_path(["lec01", "lec02", "lec03"], "lec04")
    assert ok is True


def test_validate_path_prereqs_missing():
    """缺少先修时返回 (False, ...) 且说明缺失。"""
    with patch.object(graph_module, "_run_cypher", return_value=["lec01", "lec02", "lec03"]):
        ok, msg = graph_module.validate_path(["lec01"], "lec04")
    assert ok is False
    assert "lec02" in msg or "先学习" in msg or "推荐前" in msg


def test_graph_validate_path_tool_invoke():
    """graph_validate_path 工具接受字符串参数，返回可解析的说明。"""
    with patch.object(graph_module, "validate_path", return_value=(True, "通过")):
        out = graph_module.graph_validate_path.invoke({
            "learned_topic_ids": "lec01,lec02",
            "recommended_topic_id": "lec03",
        })
    assert isinstance(out, str)
    assert "验证" in out or "通过" in out


def test_graph_query_next_topic_tool_invoke():
    """graph_query_next_topic 工具返回字符串，可解析为 id: name。"""
    with patch.object(graph_module, "query_next_topic", return_value=[
        {"id": "lec02", "name_en": "Lecture 2", "order": 2},
    ]):
        out = graph_module.graph_query_next_topic.invoke({"topic_id": "lec01"})
    assert isinstance(out, str)
    assert "lec02" in out


def test_graph_query_covers_exercises_tool_invoke():
    """graph_query_covers_exercises 工具返回字符串。"""
    with patch.object(graph_module, "query_covers_exercises", return_value=[
        {"id": "hw01", "title": "Problem Set 1", "difficulty": "medium"},
    ]):
        out = graph_module.graph_query_covers_exercises.invoke({"topic_id": "lec01"})
    assert isinstance(out, str)
    assert "hw01" in out


def test_get_all_graph_tools():
    """get_all_graph_tools 返回工具列表，含 graph_validate_path、graph_query_next_topic 等。"""
    tools = graph_module.get_all_graph_tools()
    names = [getattr(t, "name", None) for t in tools]
    assert "graph_validate_path" in names
    assert "graph_query_next_topic" in names
    assert "graph_query_covers_exercises" in names
