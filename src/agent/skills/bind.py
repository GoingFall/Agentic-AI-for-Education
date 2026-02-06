"""
工具与 Skill 绑定：根据 allowed_tools 从全局工具列表中筛选本回合可用工具。
"""
from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool


def filter_tools_by_allowed(
    all_tools: list[BaseTool],
    allowed_tool_names: list[str],
) -> list[BaseTool]:
    """
    按工具名筛选：仅保留 name 在 allowed_tool_names 中的工具。
    保证 SKILL.md 的 allowed_tools 与 @tool 的函数名（或显式 name）一致。
    """
    name_set = set(allowed_tool_names)
    return [t for t in all_tools if getattr(t, "name", None) in name_set]
