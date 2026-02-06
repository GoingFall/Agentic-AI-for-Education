"""
端到端集成测试：模拟前端输入「你好？」调用 invoke_with_skills，校验返回结构且不出现 .get 等异常。
需 .env 中配置 OPENROUTER_API_KEY；未配置时自动 skip。
运行：pytest tests/agent/test_invoke_integration.py -v
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# conftest 已加载 .env，这里仅做存在性判断
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


@pytest.mark.skipif(not OPENROUTER_API_KEY, reason="OPENROUTER_API_KEY not set in .env")
def test_invoke_hello_e2e():
    """模拟前端输入「你好？」：invoke_with_skills 返回 dict 含 reply/session_id/selected_skill_ids，且不报 'str' object has no attribute 'get'。"""
    from src.agent.run import invoke_with_skills

    session_id = "test-hello-e2e"
    session_store = {}
    skills_dir = ROOT / "skills"

    result = invoke_with_skills(
        "你好？",
        session_id=session_id,
        session_store=session_store,
        skills_dir=skills_dir,
    )

    assert isinstance(result, dict), "返回值应为 dict"
    assert "reply" in result, "应包含 reply"
    assert "session_id" in result, "应包含 session_id"
    assert "selected_skill_ids" in result, "应包含 selected_skill_ids"
    assert isinstance(result["reply"], str), "reply 应为 str"
    assert result["session_id"] == session_id
    assert isinstance(result["selected_skill_ids"], list), "selected_skill_ids 应为 list"
    # 确保未出现此前出现的属性错误（若异常被吞掉会出现在 reply 里）
    assert "'str' object has no attribute 'get'" not in result["reply"], (
        "不应出现 .get 属性错误"
    )


@pytest.mark.skipif(not OPENROUTER_API_KEY, reason="OPENROUTER_API_KEY not set in .env")
def test_invoke_returns_same_session_id_when_provided():
    """传入 session_id 时，返回的 session_id 与传入一致。"""
    from src.agent.run import invoke_with_skills

    session_id = "test-session-id-fixed"
    result = invoke_with_skills(
        "hi",
        session_id=session_id,
        session_store={},
        skills_dir=ROOT / "skills",
    )
    assert result.get("session_id") == session_id
