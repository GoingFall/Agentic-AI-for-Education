"""
Agent 核心与 run 入口单元测试。使用占位工具，不调用真实 LLM。
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from langchain_core.tools import tool


@tool
def _dummy_tool(x: str) -> str:
    """占位工具。"""
    return f"dummy: {x}"


def test_build_agent_prompt():
    from src.agent.core import build_agent_prompt
    prompt = build_agent_prompt("You are helpful.")
    assert prompt.input_variables


def test_create_executor_no_history():
    from src.agent.core import create_executor
    executor = create_executor(
        [_dummy_tool],
        system_prompt="Test.",
        use_message_history=False,
    )
    assert executor is not None


def test_load_agent_system_prompt():
    from src.agent.run import load_agent_system_prompt
    prompt = load_agent_system_prompt(PROJECT_ROOT / "config" / "agent.yaml")
    assert prompt and ("助手" in prompt or "助教" in prompt or len(prompt) > 0)


def test_build_system_prompt_multi_skill_and_user_context():
    from src.agent.run import build_system_prompt
    base = "角色：助教"
    bodies = ["# 答疑\n先 RAG。", "# 推荐\n先查图谱。"]
    out = build_system_prompt(base, bodies)
    assert "答疑" in out and "推荐" in out
    assert "先完整回答知识问题" in out and "推荐练习" in out
    out2 = build_system_prompt(base, bodies, user_context={"learned_topic_ids": ["lec01", "lec02"]})
    assert "用户已学讲次" in out2 and "lec01" in out2 and "graph_validate_path" in out2
