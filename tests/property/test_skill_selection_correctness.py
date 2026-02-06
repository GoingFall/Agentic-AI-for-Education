"""
属性基测试 8.3.4：技能选择正确性——系统根据用户输入正确触发技能（select_skills_for_input 与设计一致）。
"""
from __future__ import annotations

import sys
from pathlib import Path

from hypothesis import given, strategies as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# 与 test_chat.py 对齐
USER_MESSAGE_CASES = [
    "什么是卷积？",
    "傅里叶变换的定义",
    "如何理解线性时不变系统？",
    "解释一下离散时间信号",
    "第3讲讲了什么？",
    "LTI system explain",
    "推荐下一步练习",
    "学完第2讲想巩固一下，有什么作业推荐？",
    "recommend practice for me",
    "你好",
    "谢谢",
]
MESSAGE_EXPECTED_SKILLS = [
    ["qa", "exercise-recommend"],
    ["qa", "exercise-recommend"],
    ["qa", "exercise-recommend"],
    ["qa", "exercise-recommend"],
    [],
    ["qa", "exercise-recommend"],
    ["exercise-recommend"],
    ["exercise-recommend"],
    ["exercise-recommend"],
    [],
    [],
]


@given(message=st.sampled_from(USER_MESSAGE_CASES))
def test_skill_selection_matches_design_for_sampled_messages(message: str):
    """对设计用例采样：select_skills_for_input 返回的 selected_ids 与 MESSAGE_EXPECTED_SKILLS 一致。"""
    from src.agent.skills.trigger import select_skills_for_input
    from src.agent.tools import get_all_tools
    names = [t.name for t in get_all_tools()]
    selected_ids, _ = select_skills_for_input(message, default_allowed_tools=[], all_tool_names=names)
    idx = USER_MESSAGE_CASES.index(message)
    expected = MESSAGE_EXPECTED_SKILLS[idx]
    assert selected_ids == expected, f"message={message!r} 预期 {expected}，实际 {selected_ids}"


@given(text=st.text(min_size=1, max_size=100))
def test_skill_selection_contains_trigger_keyword_skill(text: str):
    """若输入含答疑关键词（如「什么是」），则 qa 应在 selected_ids 中。"""
    from src.agent.skills.trigger import select_skills_for_input
    from src.agent.tools import get_all_tools
    names = [t.name for t in get_all_tools()]
    selected_ids, _ = select_skills_for_input(text, default_allowed_tools=[], all_tool_names=names)
    if "什么是" in text or "解释" in text or "如何" in text or "help" in text.lower() or "explain" in text.lower():
        assert "qa" in selected_ids, f"含答疑关键词的输入应触发 qa: {text!r} -> {selected_ids}"
    if "推荐" in text or "练习" in text or "作业" in text or "recommend" in text.lower() or "practice" in text.lower():
        assert "exercise-recommend" in selected_ids, f"含推荐关键词的输入应触发 exercise-recommend: {text!r} -> {selected_ids}"
