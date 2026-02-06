"""
属性基测试 8.3.3：会话连续性——同一 session_id 下多轮对话保持上下文（历史递增、返回相同 session_id）。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given, strategies as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@given(session_id=st.sampled_from(["s1", "session-abc", "cont-123"]))
def test_same_session_id_returned(session_id: str):
    """同一 session_id 传入时，API 返回的 session_id 与传入一致（mock 下）。"""
    from fastapi.testclient import TestClient
    from src.api.app import app
    import src.api.session_store as store
    store.SESSIONS_DIR = Path(ROOT) / "data" / "sessions"
    store.SESSIONS_FILE = store.SESSIONS_DIR / "sessions.json"
    store.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    with patch("src.agent.run.invoke_with_skills") as m:
        m.return_value = {"reply": "ok", "session_id": session_id, "selected_skill_ids": []}
        client = TestClient(app)
        resp = client.post("/api/chat", json={"message": "hi", "session_id": session_id})
    assert resp.status_code == 200
    assert resp.json()["session_id"] == session_id


def test_multi_round_history_length_increases():
    """多轮 invoke_with_skills 同一 session_id 时，session_store 中该会话消息数随轮次递增。"""
    from src.agent import session as session_module
    from src.agent.core import INPUT_KEY
    session_store = {}
    store, get_session_history = session_module.get_session_history_factory(session_store)
    dummy = lambda inp, config=None: {"output": "ok"}
    from langchain_core.runnables import RunnableLambda
    runnable = RunnableLambda(dummy)
    with_history = session_module.bind_message_history(
        runnable, get_session_history,
        history_messages_key="chat_history",
        input_messages_key=INPUT_KEY,
    )
    config = {"configurable": {"session_id": "cont-s1"}}
    with_history.invoke({INPUT_KEY: "第一轮"}, config=config)
    n1 = len(session_store["cont-s1"].messages)
    with_history.invoke({INPUT_KEY: "第二轮"}, config=config)
    n2 = len(session_store["cont-s1"].messages)
    assert n2 > n1
    assert n1 >= 2 and n2 >= 4
