"""
对话接口异常情况处理测试：空消息、超长、无效 session_id、依赖服务不可用。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def test_chat_empty_message_422(client):
    """空 message 返回 422。"""
    resp = client.post("/api/chat", json={"message": ""})
    assert resp.status_code == 422
    body = resp.json()
    assert body.get("error") is True
    assert body.get("code") == "validation_error"


def test_chat_message_too_long_422(client):
    """message 超过 4096 返回 422。"""
    resp = client.post("/api/chat", json={"message": "x" * 4097})
    assert resp.status_code == 422


def test_chat_invalid_session_id_creates_or_uses(client):
    """传入不存在的 session_id 时仍 200，使用该 id 创建新会话或沿用。"""
    with patch("src.agent.run.invoke_with_skills") as m:
        m.return_value = {"reply": "ok", "session_id": "invalid-uuid-style", "selected_skill_ids": []}
        resp = client.post("/api/chat", json={"message": "hi", "session_id": "invalid-uuid-style"})
    assert resp.status_code == 200
    assert resp.json()["session_id"] == "invalid-uuid-style"


def test_chat_dependency_failure_returns_200_with_error_in_reply(client):
    """invoke_with_skills 抛出异常时 API 仍返回 200，reply 中含错误信息。"""
    with patch("src.agent.run.invoke_with_skills") as m:
        m.side_effect = RuntimeError("Chroma connection failed")
        resp = client.post("/api/chat", json={"message": "你好"})
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert "请求出错" in data["reply"] or "error" in data["reply"].lower() or "Chroma" in data["reply"]
    assert data.get("selected_skill_ids") == []
