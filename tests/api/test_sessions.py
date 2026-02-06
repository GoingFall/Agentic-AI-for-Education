"""会话管理接口测试（7.1.2）。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def test_get_sessions_empty(client):
    """初始 GET /api/sessions 返回空列表或已有 sessions。"""
    resp = client.get("/api/sessions")
    assert resp.status_code == 200
    data = resp.json()
    assert "sessions" in data
    assert isinstance(data["sessions"], dict)


def test_post_sessions_create(client):
    """POST /api/sessions 创建新会话并返回 id、title、messages。"""
    resp = client.post("/api/sessions")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data.get("title") == "新会话"
    assert "updated_at" in data
    assert data.get("messages") == []
    session_id = data["id"]
    # GET 列表应包含新会话
    list_resp = client.get("/api/sessions")
    assert list_resp.status_code == 200
    assert session_id in list_resp.json().get("sessions", {})


def test_get_session_detail(client):
    """GET /api/sessions/{id} 返回单会话详情。"""
    create = client.post("/api/sessions")
    session_id = create.json()["id"]
    resp = client.get(f"/api/sessions/{session_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == session_id
    assert "title" in data
    assert "messages" in data


def test_get_session_404(client):
    """不存在的 session_id 返回 404。"""
    resp = client.get("/api/sessions/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    body = resp.json()
    assert body.get("error") is True
    assert "不存在" in str(body.get("detail", ""))


def test_delete_session(client):
    """DELETE /api/sessions/{id} 删除会话。"""
    create = client.post("/api/sessions")
    session_id = create.json()["id"]
    resp = client.delete(f"/api/sessions/{session_id}")
    assert resp.status_code == 204
    get_resp = client.get(f"/api/sessions/{session_id}")
    assert get_resp.status_code == 404


def test_delete_session_404(client):
    """删除不存在的会话返回 404。"""
    resp = client.delete("/api/sessions/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
