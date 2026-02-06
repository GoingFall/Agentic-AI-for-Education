"""GET /api/status 与 /api/health 测试（7.1.3）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def test_status_returns_200(client):
    """GET /api/status 返回 200 及 ok、service 等字段。"""
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("ok") is True
    assert data.get("service") == "agent-edu-api"
    assert "chroma" in data
    assert "neo4j" in data


def test_health_returns_200(client):
    """GET /api/health 返回 200。"""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json().get("ok") is True
