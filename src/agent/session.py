"""
会话管理：按 session_id 维护 ChatMessageHistory，供 RunnableWithMessageHistory 注入历史。
首版为内存存储；可选 JSONL 落盘。可选限制注入历史的轮数以减少多轮污染。
"""
from __future__ import annotations

import os
from typing import Any

from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


def _max_history_turns() -> int:
    """从环境变量 AGENT_HISTORY_MAX_TURNS 读取，0 表示不限制。"""
    try:
        v = os.environ.get("AGENT_HISTORY_MAX_TURNS", "0")
        return max(0, int(v))
    except (TypeError, ValueError):
        return 0


class _BoundedChatMessageHistory(BaseChatMessageHistory):
    """包装一层 ChatMessageHistory，读取 messages 时只返回最近 N 轮，减少多轮污染。写入仍写入底层。"""

    def __init__(self, underlying: BaseChatMessageHistory, max_turns: int) -> None:
        super().__init__()
        self._underlying = underlying
        self._max_turns = max_turns

    @property
    def messages(self) -> list:
        msgs = self._underlying.messages
        if self._max_turns <= 0 or len(msgs) <= self._max_turns * 2:
            return msgs
        return list(msgs[-self._max_turns * 2 :])

    def add_message(self, message: Any) -> None:
        self._underlying.add_message(message)

    def add_user_message(self, message: str) -> None:
        self._underlying.add_user_message(message)

    def add_ai_message(self, message: str) -> None:
        self._underlying.add_ai_message(message)

    def clear(self) -> None:
        self._underlying.clear()


def get_session_history_factory(
    store: dict[str, BaseChatMessageHistory] | None = None,
) -> tuple[dict[str, BaseChatMessageHistory], Any]:
    """
    返回 (store, get_session_history)：
    - store: session_id -> ChatMessageHistory，调用方可持有以便清理或持久化；
    - get_session_history: 供 RunnableWithMessageHistory 使用，签名为 (config) -> BaseChatMessageHistory。
    若环境变量 AGENT_HISTORY_MAX_TURNS 大于 0，返回的 history 在读取时只暴露最近 N 轮，写入仍写入同一 store。
    """
    if store is None:
        store = {}

    max_turns = _max_history_turns()

    def get_session_history(config: dict[str, Any] | str) -> BaseChatMessageHistory:
        # 新版 langchain_core 以位置参数传入 session_id 字符串，旧版传入 config 字典
        if isinstance(config, str):
            sid = config
        else:
            sid = (config.get("configurable") or {}).get("session_id")
        if not sid:
            sid = "default"
        if sid not in store:
            store[sid] = InMemoryChatMessageHistory()
        base = store[sid]
        if max_turns > 0:
            return _BoundedChatMessageHistory(base, max_turns)
        return base

    return store, get_session_history


def bind_message_history(
    runnable: Any,
    get_session_history: Any,
    *,
    history_messages_key: str = "chat_history",
    input_messages_key: str = "input",
) -> RunnableWithMessageHistory:
    """
    使用 RunnableWithMessageHistory 包装 Agent 链，按 configurable.session_id 注入历史。
    history_messages_key：prompt 中历史消息占位符的变量名；
    input_messages_key：当前用户输入的变量名。
    """
    return RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key=input_messages_key,
        history_messages_key=history_messages_key,
    )
