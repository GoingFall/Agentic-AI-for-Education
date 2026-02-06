"""
多 Skill 协同工作集成测试：先发答疑类消息（qa + exercise-recommend），再发推荐类（仅 exercise-recommend），断言 selected_skill_ids。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@patch("src.agent.run.invoke_with_skills")
def test_multi_skill_qa_then_recommend(mock_invoke, client):
    """先发答疑类消息触发 qa+exercise-recommend，再发推荐类仅 exercise-recommend；session_id 一致。"""
    mock_invoke.side_effect = [
        {"reply": "答疑回复", "session_id": "multi-s1", "selected_skill_ids": ["qa", "exercise-recommend"]},
        {"reply": "推荐回复", "session_id": "multi-s1", "selected_skill_ids": ["exercise-recommend"]},
    ]
    resp1 = client.post("/api/chat", json={"message": "什么是卷积？"})
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["selected_skill_ids"] == ["qa", "exercise-recommend"]
    sid = data1["session_id"]

    resp2 = client.post("/api/chat", json={"message": "推荐下一步练习", "session_id": sid})
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["session_id"] == sid
    assert data2["selected_skill_ids"] == ["exercise-recommend"]
    assert mock_invoke.call_count == 2


@patch("src.agent.run.invoke_with_skills")
def test_multi_skill_select_skills_consistency(mock_invoke, client):
    """多轮消息下 select_skills_for_input 与设计一致（由 run 内部调用，通过 mock 返回值断言）。"""
    mock_invoke.return_value = {
        "reply": "ok",
        "session_id": "s",
        "selected_skill_ids": ["qa", "exercise-recommend"],
    }
    resp = client.post("/api/chat", json={"message": "如何理解线性时不变系统？"})
    assert resp.status_code == 200
    assert set(resp.json()["selected_skill_ids"]) >= {"qa", "exercise-recommend"}
