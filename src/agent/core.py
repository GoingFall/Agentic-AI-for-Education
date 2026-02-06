"""
基于 LangChain 的 Agent 核心：create_tool_calling_agent + AgentExecutor，支持会话历史。
对外暴露 invoke(session_id, user_message, tools, system_prompt)。
无 tool_calling_agent 子模块时使用 langchain_core.bind_tools 自实现循环（fallback）。
"""
from __future__ import annotations

import re
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda

from . import session as session_module
from .llm import get_llm

# 优先使用官方 agent；部分环境无 langchain.agents.tool_calling_agent 子模块则用 fallback
_USE_LEGACY_AGENT = False
try:
    from langchain.agents import create_tool_calling_agent
    from langchain.agents import AgentExecutor
except ImportError:
    try:
        from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
        from langchain.agents.agent import AgentExecutor
    except ImportError:
        _USE_LEGACY_AGENT = True
        create_tool_calling_agent = None
        AgentExecutor = None

# 与 session.bind_message_history 使用的 key 一致，供 RunnableWithMessageHistory 注入历史
HISTORY_KEY = "chat_history"
INPUT_KEY = "input"
AGENT_SCRATCHPAD_KEY = "agent_scratchpad"

# 默认最大工具调用轮次，防止死循环
DEFAULT_MAX_ITERATIONS = 15

# 回复中常见泄露的 JSON 键名，用于后处理移除裸 JSON 片段（兜底）
_REPLY_JSON_KEY_PATTERN = re.compile(
    r'\{[^{}]*(?:"exercise_id"|"valid"|"message"|"title")[^{}]*\}',
    re.DOTALL,
)


def _sanitize_reply_json(reply: str) -> str:
    """移除回复中明显来自工具/API 的裸 JSON 片段，避免展示给用户。"""
    if not reply or not reply.strip():
        return reply
    cleaned = _REPLY_JSON_KEY_PATTERN.sub("", reply)
    # 合并因删除产生的多余空白
    return re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned).strip() or reply


def build_agent_prompt(system_tpl: str = "你是一个有帮助的助手。") -> ChatPromptTemplate:
    """构建带历史与 agent_scratchpad 的 prompt，system 内容由调用方传入时覆盖。"""
    return ChatPromptTemplate.from_messages([
        ("system", system_tpl),
        MessagesPlaceholder(variable_name=HISTORY_KEY, optional=True),
        ("human", "{" + INPUT_KEY + "}"),
        MessagesPlaceholder(variable_name=AGENT_SCRATCHPAD_KEY),
    ])


def _run_tool_calling_loop(
    tools: list[Any],
    system_prompt: str,
    max_iterations: int,
    llm: Any,
) -> Any:
    """无 create_tool_calling_agent 时：用 bind_tools + 消息循环实现 tool-calling 执行器。"""
    name_to_tool = {getattr(t, "name", str(i)): t for i, t in enumerate(tools)}
    if not name_to_tool:
        name_to_tool = {t.name: t for t in tools if getattr(t, "name", None)}

    def _invoke(input_dict: dict[str, Any]) -> dict[str, Any]:
        user_input = input_dict.get(INPUT_KEY, "")
        history = input_dict.get(HISTORY_KEY) or []
        messages = [SystemMessage(content=system_prompt)]
        if history:
            messages.extend(list(history))
        messages.append(HumanMessage(content=user_input))
        llm_with_tools = llm.bind_tools(tools)
        for _ in range(max_iterations):
            response = llm_with_tools.invoke(messages)
            if not getattr(response, "tool_calls", None):
                content = getattr(response, "content", "") or ""
                return {"output": content if isinstance(content, str) else str(content)}
            messages.append(response)
            for tc in response.tool_calls:
                name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {}) or {}
                tool = name_to_tool.get(name) if name else None
                if tool is None:
                    out = f"未知工具: {name}"
                else:
                    try:
                        out = tool.invoke(args)
                    except Exception as e:
                        out = f"工具执行错误: {e}"
                tid = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
                messages.append(ToolMessage(content=str(out), tool_call_id=tid or ""))
        last = messages[-1] if messages else None
        content = getattr(last, "content", "") or "达到最大轮次。"
        return {"output": content if isinstance(content, str) else str(content)}

    return RunnableLambda(_invoke)


def create_executor(
    tools: list[Any],
    system_prompt: str = "你是一个有帮助的助手。",
    *,
    llm: Any = None,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    use_message_history: bool = True,
    session_store: dict[str, Any] | None = None,
) -> Any:
    """
    创建 Agent 执行器（可选带会话历史）。
    - tools: LangChain 工具列表（@tool 定义）。
    - system_prompt: 系统提示词（可与 config/agent.yaml + Skill 正文拼接后传入）。
    - use_message_history: 若 True，返回 RunnableWithMessageHistory 包装的 executor，invoke 时需传 config={"configurable": {"session_id": ...}}。
    - session_store: 若 use_message_history 且提供，则用此 dict 存 session_id -> ChatMessageHistory，否则使用内部新建的 dict。
    返回 runnable，invoke(input_dict, config=...) 时 input_dict 需含 key "input"（用户本轮消息）。
    """
    if llm is None:
        llm = get_llm()
    if _USE_LEGACY_AGENT:
        executor = _run_tool_calling_loop(tools, system_prompt, max_iterations, llm)
    else:
        prompt = build_agent_prompt(system_tpl=system_prompt)
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            max_iterations=max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=False,
        )
    if not use_message_history:
        return executor
    store, get_session_history = session_module.get_session_history_factory(session_store)
    with_history = session_module.bind_message_history(
        executor,
        get_session_history,
        history_messages_key=HISTORY_KEY,
        input_messages_key=INPUT_KEY,
    )
    return with_history


def invoke(
    session_id: str,
    user_message: str,
    tools: list[Any],
    system_prompt: str = "你是一个有帮助的助手。",
    *,
    llm: Any = None,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    session_store: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    单入口：根据 session_id、用户消息、工具与系统提示词执行 Agent，返回助手回复及可选结构化字段。
    返回格式：{"reply": str, "session_id": str}；citations/recommendations 可由后续从 intermediate_steps 或解析回复得到。
    """
    executor = create_executor(
        tools,
        system_prompt=system_prompt,
        llm=llm,
        max_iterations=max_iterations,
        use_message_history=True,
        session_store=session_store,
    )
    config = {"configurable": {"session_id": session_id}}
    result = executor.invoke({INPUT_KEY: user_message}, config=config)
    # AgentExecutor / fallback 返回 dict 含 "output"；少数情况下可能为 str，做兼容
    if isinstance(result, dict):
        reply = result.get("output", "")
    else:
        reply = result if isinstance(result, str) else str(result)
    reply = reply if isinstance(reply, str) else str(reply)
    reply = _sanitize_reply_json(reply)
    return {
        "reply": reply,
        "session_id": session_id,
    }


def invoke_stream(
    session_id: str,
    user_message: str,
    tools: list[Any],
    system_prompt: str = "你是一个有帮助的助手。",
    *,
    llm: Any = None,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    session_store: dict[str, Any] | None = None,
):
    """
    流式入口：执行 Agent 并逐块 yield 助手回复文本。
    使用 stream_events 收集 on_chat_model_stream 的 content，最后再 yield 完整 output（若与流式内容一致可省略）。
    """
    executor = create_executor(
        tools,
        system_prompt=system_prompt,
        llm=llm,
        max_iterations=max_iterations,
        use_message_history=True,
        session_store=session_store,
    )
    config = {"configurable": {"session_id": session_id}}
    accumulated = []
    try:
        streamer = getattr(executor, "stream_events", None)
        if streamer:
            for event in streamer(
                {INPUT_KEY: user_message},
                config=config,
                version="v2",
            ):
                if event.get("event") != "on_chat_model_stream":
                    continue
                data = event.get("data") or {}
                chunk = data.get("chunk", data) if isinstance(data, dict) else data
                if isinstance(chunk, dict):
                    content = chunk.get("content", "")
                else:
                    content = getattr(chunk, "content", None) or ""
                if content:
                    accumulated.append(content)
                    yield content
        # 若无 stream_events 或未产出任何内容，回退到 invoke 取完整 output
        if not accumulated:
            result = executor.invoke({INPUT_KEY: user_message}, config=config)
            if isinstance(result, dict):
                reply = result.get("output", "")
            else:
                reply = result if isinstance(result, str) else str(result)
            reply = reply if isinstance(reply, str) else str(reply)
            if reply:
                yield reply
    except Exception:
        full_reply = "".join(accumulated) if accumulated else ""
        if full_reply:
            yield full_reply
        raise
