"""
OpenRouter LLM 集成。从 .env 读取 OPENROUTER_API_KEY、OPENROUTER_MODEL。
供 Agent 核心与工具调用使用；调用方需在项目根目录加载 dotenv。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_llm(
    *,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    temperature: float = 0,
) -> BaseChatModel:
    """
    获取 OpenRouter ChatOpenAI 实例。
    若未传 api_key/model/base_url，则从环境变量读取（OPENROUTER_API_KEY、OPENROUTER_MODEL）。
    """
    from langchain_openai import ChatOpenAI

    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set. Add it to .env in project root.")
    return ChatOpenAI(
        model=model or os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
        openai_api_key=key,
        openai_api_base=base_url or OPENROUTER_BASE_URL,
        temperature=temperature,
    )
