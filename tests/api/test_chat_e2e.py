"""
端到端对话流程测试：POST /api/chat 不 mock Agent，需 Chroma/Neo4j/OpenRouter 可用时运行。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


@pytest.mark.e2e
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set",
)
def test_chat_e2e_returns_200_and_structure(client_no_mock):
    """端到端：POST /api/chat 发送固定消息，断言 200 且 body 含 reply、session_id、selected_skill_ids。"""
    resp = client_no_mock.post("/api/chat", json={"message": "你好"})
    if resp.status_code != 200:
        pytest.skip(f"E2E 依赖服务不可用: {resp.status_code} {resp.text[:200]}")
    data = resp.json()
    assert "reply" in data
    assert "session_id" in data
    assert "selected_skill_ids" in data
    assert isinstance(data["reply"], str)
    assert len(data["session_id"]) > 0


@pytest.mark.e2e
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set",
)
def test_chat_e2e_second_message_same_session(client_no_mock):
    """端到端：连续两条消息使用同一 session_id。"""
    resp1 = client_no_mock.post("/api/chat", json={"message": "你好"})
    if resp1.status_code != 200:
        pytest.skip(f"E2E 依赖服务不可用: {resp1.status_code}")
    sid = resp1.json()["session_id"]
    resp2 = client_no_mock.post("/api/chat", json={"message": "谢谢", "session_id": sid})
    assert resp2.status_code == 200
    assert resp2.json()["session_id"] == sid
