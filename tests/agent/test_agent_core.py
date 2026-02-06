"""
Agent 核心与 run 入口单元测试。使用占位工具，不调用真实 LLM。
"""
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

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


def test_create_executor_with_history_different_sessions_isolated():
    """带 session_store 时，不同 session_id 的会话历史互不干扰。"""
    from src.agent import session as session_module
    from src.agent.core import INPUT_KEY
    session_store = {}
    store, get_session_history = session_module.get_session_history_factory(session_store)
    dummy_runnable = lambda inp, config=None: {"output": "ok"}
    from langchain_core.runnables import RunnableLambda
    runnable = RunnableLambda(dummy_runnable)
    with_history = session_module.bind_message_history(
        runnable, get_session_history,
        history_messages_key="chat_history",
        input_messages_key=INPUT_KEY,
    )
    config1 = {"configurable": {"session_id": "s1"}}
    config2 = {"configurable": {"session_id": "s2"}}
    with_history.invoke({INPUT_KEY: "hello"}, config=config1)
    with_history.invoke({INPUT_KEY: "hi"}, config=config2)
    with_history.invoke({INPUT_KEY: "again"}, config=config1)
    assert "s1" in session_store and "s2" in session_store
    assert len(session_store["s1"].messages) >= 4
    assert len(session_store["s2"].messages) >= 2


def test_invoke_return_structure():
    """invoke 返回 dict 含 reply、session_id，reply 为 str。"""
    from src.agent.core import invoke
    with patch("src.agent.core.create_executor") as m:
        m.return_value.invoke.return_value = {"output": "reply text"}
        out = invoke(
            "sid",
            "hello",
            [_dummy_tool],
            system_prompt="Test.",
            session_store={},
        )
    assert isinstance(out, dict)
    assert "reply" in out and "session_id" in out
    assert out["session_id"] == "sid"
    assert isinstance(out["reply"], str)
    assert "reply text" in out["reply"]


def test_invoke_stream_yields_string_chunks():
    """invoke_stream 为生成器，产出 str 块。"""
    from src.agent.core import invoke_stream, INPUT_KEY
    mock_executor = MagicMock()
    mock_executor.stream_events.return_value = iter([])
    mock_executor.invoke.return_value = {"output": "streamed"}
    with patch("src.agent.core.create_executor", return_value=mock_executor):
        gen = invoke_stream("sid", "hi", [_dummy_tool], system_prompt="Test.", session_store={})
        chunks = list(gen)
    assert len(chunks) >= 1
    assert isinstance(chunks[0], str)
    assert "streamed" in "".join(chunks)
