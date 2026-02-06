"""
Skill 加载与触发、工具绑定单元测试。不依赖 Neo4j/Chroma/OpenRouter。
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.agent.skills.loader import load_skills, get_skill_registry, get_skill
from src.agent.skills.trigger import select_skills_for_input
from src.agent.skills.bind import filter_tools_by_allowed
from src.agent.tools import get_all_tools


def test_load_skills():
    reg = load_skills(PROJECT_ROOT)
    assert isinstance(reg, dict)
    assert "qa" in reg or "exercise-recommend" in reg
    for sid, cfg in reg.items():
        assert "name" in cfg
        assert "trigger_keywords" in cfg
        assert "allowed_tools" in cfg
        assert "body" in cfg


def test_get_skill():
    reg = get_skill_registry(PROJECT_ROOT)
    skill = get_skill("qa", PROJECT_ROOT)
    if skill:
        assert skill.get("allowed_tools") == ["rag_retrieve"]


def test_get_skill_nonexistent_returns_none():
    """get_skill 对不存在的 skill_id 返回 None。"""
    assert get_skill("nonexistent-skill-id", PROJECT_ROOT) is None


def test_skill_registry_has_trigger_keywords_and_priority():
    """多 Skill 的 trigger_keywords 与 priority 加载正确，qa、exercise-recommend 的 body 非空。"""
    reg = get_skill_registry(PROJECT_ROOT)
    assert "qa" in reg or "exercise-recommend" in reg
    for sid in ("qa", "exercise-recommend"):
        if sid not in reg:
            continue
        cfg = reg[sid]
        assert "trigger_keywords" in cfg and isinstance(cfg["trigger_keywords"], list)
        assert "body" in cfg and isinstance(cfg["body"], str) and len(cfg["body"].strip()) > 0
        if "priority" in cfg:
            assert isinstance(cfg["priority"], (int, float))


def test_select_skills_trigger():
    tools = get_all_tools()
    names = [t.name for t in tools]
    ids, allowed = select_skills_for_input("I need help", all_tool_names=names)
    assert "qa" in ids or not ids
    if ids:
        assert "rag_retrieve" in allowed
    ids2, _ = select_skills_for_input("recommend next", all_tool_names=names)
    assert "exercise-recommend" in ids2 or not ids2


def test_filter_tools_by_allowed():
    tools = get_all_tools()
    filtered = filter_tools_by_allowed(tools, ["rag_retrieve"])
    assert len(filtered) == 1
    assert filtered[0].name == "rag_retrieve"


def test_invoke_with_skills_returns_selected_skill_ids():
    """invoke_with_skills 返回 selected_skill_ids（需 mock core.invoke 避免真实调用）。"""
    from unittest.mock import patch
    from src.agent.run import invoke_with_skills
    with patch("src.agent.run.core.invoke", return_value={"reply": "ok", "session_id": "t1"}):
        out = invoke_with_skills("什么是卷积？", session_id="t1")
    assert "selected_skill_ids" in out
    assert isinstance(out["selected_skill_ids"], list)
    assert out["reply"] == "ok" and out["session_id"] == "t1"
