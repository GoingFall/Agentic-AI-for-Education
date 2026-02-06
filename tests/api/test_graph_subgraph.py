"""GET /api/graph/subgraph 与 GET /api/graph/learning-path 测试（11.1）。"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


@pytest.fixture
def mock_subgraph():
    """返回符合子图结构的 mock 数据，节点数 ≤ 50。"""
    return {
        "nodes": [
            {"id": "lec01", "label": "Lecture 1", "type": "Topic"},
            {"id": "lec02", "label": "Lecture 2", "type": "Topic"},
            {"id": "hw01", "label": "HW01", "type": "Exercise"},
        ],
        "edges": [
            {"source": "lec01", "target": "lec02", "type": "PREREQUISITE"},
            {"source": "lec01", "target": "hw01", "type": "COVERS"},
        ],
    }


def test_subgraph_returns_structure_and_node_cap(client, mock_subgraph):
    """子图接口返回 nodes/edges，且 nodes 数量不超过 max_nodes。"""
    from src.knowledge_graph import subgraph as subgraph_mod
    with patch.object(subgraph_mod, "get_subgraph", return_value=mock_subgraph):
        resp = client.get(
            "/api/graph/subgraph",
            params={"seed_id": "lec01", "max_depth": 2, "max_nodes": 50},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) <= 50
    for n in data["nodes"]:
        assert "id" in n
        assert "label" in n
        assert "type" in n
    for e in data["edges"]:
        assert "source" in e
        assert "target" in e
        assert "type" in e


def test_subgraph_accepts_params(client, mock_subgraph):
    """子图接口接受 seed_id、max_depth、max_nodes 参数。"""
    from src.knowledge_graph import subgraph as subgraph_mod
    with patch.object(subgraph_mod, "get_subgraph", return_value=mock_subgraph) as m:
        client.get(
            "/api/graph/subgraph",
            params={"seed_id": "lec03", "max_depth": 1, "max_nodes": 20},
        )
        m.assert_called_once()
        call_kw = m.call_args[1]
        assert call_kw["seed_id"] == "lec03"
        assert call_kw["max_depth"] == 1
        assert call_kw["max_nodes"] == 20


def test_learning_path_returns_list(client):
    """学习路径接口返回 path 数组。"""
    from unittest.mock import MagicMock

    with patch("src.knowledge_graph.learning_path.get_learning_path_from_topic", return_value=["lec01", "lec02", "lec03"]):
        with patch("src.agent.tools.graph._get_driver") as mock_driver:
            mock_cm = MagicMock()
            mock_cm.__enter__.return_value = MagicMock()
            mock_cm.__exit__.return_value = None
            mock_driver.return_value.session.return_value = mock_cm
            resp = client.get("/api/graph/learning-path", params={"topic_id": "lec01"})
    assert resp.status_code == 200
    data = resp.json()
    assert "path" in data
    assert isinstance(data["path"], list)
    assert data["path"] == ["lec01", "lec02", "lec03"]
