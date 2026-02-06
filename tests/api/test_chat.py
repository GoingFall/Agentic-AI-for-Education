"""POST /api/chat 测试（7.1.1、7.2.1）。含用户可能发送的典型字符串。"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# 用户可能用到的典型输入（与 skills 触发词、results 知识库对应）
USER_MESSAGE_CASES = [
    # 答疑类（触发 qa；设计上 qa 命中时同时带 exercise-recommend，先答疑后推荐）
    "什么是卷积？",
    "傅里叶变换的定义",
    "如何理解线性时不变系统？",
    "解释一下离散时间信号",
    "第3讲讲了什么？",
    "LTI system explain",
    # 推荐类（触发 exercise-recommend）
    "推荐下一步练习",
    "我学了第1讲，该做什么题",
    "学完第2讲想巩固一下，有什么作业推荐？",
    "recommend practice for me",
    # 闲聊/短句（不命中任何 trigger_keywords）
    "你好",
    "谢谢",
    "帮我看看这道题",
]

# 按功能设计（trigger 规则 + qa 命中时附带推荐）每条消息预期触发的 skill_ids，用于断言
# 规则：qa 关键词=什么是/如何/为什么/解释/help/explain/怎么/第几讲/第几页/区别/定义；推荐=推荐/练习/作业/下一步/巩固/recommend/practice；命中 qa 时自动加 exercise-recommend
MESSAGE_EXPECTED_SKILLS = [
    ["qa", "exercise-recommend"],   # 什么是卷积？
    ["qa", "exercise-recommend"],   # 傅里叶变换的定义
    ["qa", "exercise-recommend"],   # 如何理解线性时不变系统？
    ["qa", "exercise-recommend"],   # 解释一下离散时间信号
    [],                             # 第3讲讲了什么？（当前无「第几讲」子串匹配，若需答疑可考虑扩展 trigger）
    ["qa", "exercise-recommend"],   # LTI system explain
    ["exercise-recommend"],         # 推荐下一步练习
    [],                             # 我学了第1讲，该做什么题（无「推荐/练习/作业」等，若需推荐可扩展 trigger）
    ["exercise-recommend"],         # 学完第2讲想巩固一下，有什么作业推荐？
    ["exercise-recommend"],         # recommend practice for me
    [],                             # 你好
    [],                             # 谢谢
    [],                             # 帮我看看这道题（无关键词，若需答疑可扩展如「题」/「看看」）
]
assert len(MESSAGE_EXPECTED_SKILLS) == len(USER_MESSAGE_CASES)


def test_select_skills_matches_design_for_message_cases():
    """不 mock：校验 select_skills_for_input 对每条 USER_MESSAGE_CASES 的返回与功能设计一致。"""
    from src.agent.skills.trigger import select_skills_for_input

    for message, expected in zip(USER_MESSAGE_CASES, MESSAGE_EXPECTED_SKILLS):
        selected_ids, _ = select_skills_for_input(message, default_allowed_tools=[])
        assert selected_ids == expected, (
            f"message={message!r} 预期 selected_ids={expected}，实际={selected_ids}"
        )


@patch("src.agent.run.invoke_with_skills")
def test_chat_returns_reply_and_session_id(mock_invoke, client):
    """正常 message 返回 reply、session_id、selected_skill_ids。概念问句按设计应带 qa + exercise-recommend。"""
    mock_invoke.return_value = {
        "reply": "测试回复",
        "session_id": "fake-id",
        "selected_skill_ids": ["qa", "exercise-recommend"],
    }
    resp = client.post(
        "/api/chat",
        json={"message": "什么是卷积？"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert data["reply"] == "测试回复"
    assert "session_id" in data
    assert len(data["session_id"]) > 0
    assert "selected_skill_ids" in data
    assert data["selected_skill_ids"] == ["qa", "exercise-recommend"]


@patch("src.agent.run.invoke_with_skills")
def test_chat_creates_session_when_no_session_id(mock_invoke, client):
    """不传 session_id 时自动创建新会话。"""
    mock_invoke.return_value = {
        "reply": "ok",
        "session_id": "new-session",
        "selected_skill_ids": [],
    }
    resp = client.post("/api/chat", json={"message": "你好"})
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]
    assert session_id
    # 续聊应使用同一会话
    mock_invoke.return_value = {
        "reply": "第二句",
        "session_id": session_id,
        "selected_skill_ids": [],
    }
    resp2 = client.post(
        "/api/chat",
        json={"message": "再问一句", "session_id": session_id},
    )
    assert resp2.status_code == 200
    assert resp2.json()["session_id"] == session_id


def test_chat_validation_empty_message(client):
    """空 message 返回 422。"""
    resp = client.post("/api/chat", json={"message": ""})
    assert resp.status_code == 422
    body = resp.json()
    assert body.get("error") is True
    assert body.get("code") == "validation_error"


def test_chat_validation_missing_message(client):
    """缺少 message 返回 422。"""
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 422


def test_chat_validation_message_too_long(client):
    """message 超过 4096 返回 422。"""
    resp = client.post(
        "/api/chat",
        json={"message": "x" * 4097},
    )
    assert resp.status_code == 422


@patch("src.agent.run.invoke_with_skills")
def test_chat_user_context_passed(mock_invoke, client):
    """user_context.learned_topic_ids 传入 invoke_with_skills。"""
    mock_invoke.return_value = {
        "reply": "推荐 lec02",
        "session_id": "sid",
        "selected_skill_ids": ["exercise-recommend"],
    }
    resp = client.post(
        "/api/chat",
        json={
            "message": "推荐下一步练习",
            "user_context": {"learned_topic_ids": ["lec01"]},
        },
    )
    assert resp.status_code == 200
    assert mock_invoke.called
    call_kw = mock_invoke.call_args.kwargs
    assert call_kw.get("user_context") == {"learned_topic_ids": ["lec01"]}


# ---------- 用户可能用到的字符串：发送后应 200 且返回完整结构，且 selected_skill_ids 符合设计 ----------
@patch("src.agent.run.invoke_with_skills")
@pytest.mark.parametrize("message,expected_skills", zip(USER_MESSAGE_CASES, MESSAGE_EXPECTED_SKILLS))
def test_chat_accepts_realistic_user_messages(mock_invoke, client, message, expected_skills):
    """用户可能发送的典型字符串（答疑、推荐、闲聊）均应被接受并返回 reply/session_id/selected_skill_ids；技能与设计一致。"""
    mock_invoke.return_value = {
        "reply": "模拟回复",
        "session_id": "any",
        "selected_skill_ids": expected_skills,
    }
    resp = client.post("/api/chat", json={"message": message})
    assert resp.status_code == 200, f"message={message!r} 应返回 200"
    data = resp.json()
    assert "reply" in data
    assert "session_id" in data
    assert "selected_skill_ids" in data
    assert data["selected_skill_ids"] == expected_skills, (
        f"message={message!r} 预期 selected_skill_ids={expected_skills}，实际={data['selected_skill_ids']}"
    )
    # 确认 API 把用户原文传给 agent（可带 strip）
    assert mock_invoke.called
    call_msg = mock_invoke.call_args.args[0] if mock_invoke.call_args.args else mock_invoke.call_args.kwargs.get("user_message")
    assert call_msg is not None
    assert message.strip() == call_msg.strip()


@patch("src.agent.run.invoke_with_skills")
def test_chat_strips_leading_trailing_whitespace(mock_invoke, client):
    """前后空格应被 strip 后传给 Agent，接口仍返回 200；strip 后为概念问句应带 qa+exercise-recommend。"""
    mock_invoke.return_value = {
        "reply": "ok",
        "session_id": "x",
        "selected_skill_ids": ["qa", "exercise-recommend"],
    }
    resp = client.post(
        "/api/chat",
        json={"message": "  什么是卷积？  "},
    )
    assert resp.status_code == 200
    assert resp.json()["selected_skill_ids"] == ["qa", "exercise-recommend"]
    assert mock_invoke.called
    call_msg = mock_invoke.call_args.args[0] if mock_invoke.call_args.args else mock_invoke.call_args.kwargs.get("user_message")
    assert call_msg == "什么是卷积？"


@patch("src.agent.run.invoke_with_skills")
def test_chat_single_character_message(mock_invoke, client):
    """单字符输入（如「好」）应被接受。"""
    mock_invoke.return_value = {
        "reply": "收到",
        "session_id": "s",
        "selected_skill_ids": [],
    }
    resp = client.post("/api/chat", json={"message": "好"})
    assert resp.status_code == 200
    assert resp.json().get("reply") == "收到"


@patch("src.agent.run.invoke_with_skills")
def test_chat_unicode_and_common_symbols(mock_invoke, client):
    """含中文、英文、数字、常见符号的输入应正常处理；含「怎么」触发 qa+exercise-recommend。"""
    mock_invoke.return_value = {
        "reply": "ok",
        "session_id": "s",
        "selected_skill_ids": ["qa", "exercise-recommend"],
    }
    msg = "第1讲中 x(t)*h(t) 的卷积怎么算？"
    resp = client.post("/api/chat", json={"message": msg})
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data and "session_id" in data
    assert data["selected_skill_ids"] == ["qa", "exercise-recommend"]
    assert mock_invoke.called
    call_msg = mock_invoke.call_args.args[0] if mock_invoke.call_args.args else mock_invoke.call_args.kwargs.get("user_message")
    assert call_msg == msg
