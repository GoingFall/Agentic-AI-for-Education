"""
Agent 运行入口：加载 config/agent.yaml 与 Skill，按用户输入触发 Skill、绑定工具后调用 core.invoke。
完成 4.3.3 工具与 Skill 绑定机制与配置整合。
"""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from . import core
from . import skills
from .tools import get_all_tools


def _agent_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "agent.yaml"


def load_agent_system_prompt(config_path: Path | None = None) -> str:
    """从 config/agent.yaml 加载 role、goal、backstory，拼成一段 system 提示词。"""
    path = config_path or _agent_config_path()
    if not path.is_file():
        return "你是一个有帮助的助手。"
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not data:
            return "你是一个有帮助的助手。"
        parts = []
        if data.get("role"):
            parts.append(f"角色：{data['role']}")
        if data.get("goal"):
            parts.append(f"目标：{data['goal']}")
        if data.get("backstory"):
            parts.append(f"背景：{data['backstory']}")
        return "\n".join(parts) if parts else "你是一个有帮助的助手。"
    except Exception:
        return "你是一个有帮助的助手。"


def build_system_prompt(
    base_prompt: str,
    skill_bodies: list[str],
    *,
    user_context: dict[str, Any] | None = None,
) -> str:
    """将 base_prompt 与选中 Skill 的正文拼接为最终 system prompt。多 Skill 时追加协同说明；可选注入 user_context（如已学讲次）。"""
    if not skill_bodies:
        out = base_prompt
    else:
        out = base_prompt + "\n\n" + "\n\n".join(skill_bodies)
    if user_context:
        learned = user_context.get("learned_topic_ids")
        if learned is not None and learned:
            ids_str = ", ".join(learned) if isinstance(learned, (list, tuple)) else str(learned)
            out = out + "\n\n用户已学讲次：" + ids_str + "。推荐时请遵守先修顺序，可使用 graph_validate_path 验证。"
    if len(skill_bodies) > 1:
        out = out + "\n\n若本回合同时涉及答疑与推荐，请先完整回答知识问题，再在单独段落给出学习/练习推荐。回答结构可分段：先「答疑」再「推荐练习」（可用 ## 答疑、## 推荐练习 标题）。"
    return out


def invoke_with_skills(
    user_message: str,
    session_id: str | None = None,
    *,
    session_store: dict[str, Any] | None = None,
    skills_dir: Path | None = None,
    user_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    带 Skill 触发与工具绑定的单次调用：
    1) 根据 user_message 选择命中的 Skill 及 allowed_tools（多命中时合并工具与 prompt）；
    2) 从全局工具中筛出本回合可用工具；
    3) 拼接 system prompt（config/agent.yaml + 选中 Skill 正文 + 可选 user_context + 多 Skill 协同说明）；
    4) 调用 core.invoke，返回 reply、session_id、selected_skill_ids。
    """
    session_id = session_id or str(uuid.uuid4())
    all_tools = get_all_tools()
    all_tool_names = [getattr(t, "name", "") for t in all_tools]
    selected_ids, allowed_names = skills.select_skills_for_input(
        user_message,
        all_tool_names=all_tool_names,
        default_allowed_tools=all_tool_names,
    )
    tools = skills.filter_tools_by_allowed(all_tools, allowed_names)
    if not tools:
        tools = all_tools
    reg = skills.get_skill_registry(skills_dir)
    skill_bodies = [reg[sid]["body"] for sid in selected_ids if sid in reg]
    base_prompt = load_agent_system_prompt()
    system_prompt = build_system_prompt(base_prompt, skill_bodies, user_context=user_context)
    result = core.invoke(
        session_id,
        user_message,
        tools,
        system_prompt=system_prompt,
        session_store=session_store,
    )
    result["selected_skill_ids"] = list(selected_ids)
    return result


def invoke_with_skills_stream(
    user_message: str,
    session_id: str | None = None,
    *,
    session_store: dict[str, Any] | None = None,
    skills_dir: Path | None = None,
    user_context: dict[str, Any] | None = None,
):
    """
    带 Skill 的流式调用：先 yield 文本块（"chunk"），最后 yield 结束事件（"done", full_reply, skill_ids）。
    调用方应迭代此生成器，累积 content，收到 "done" 后写回 selected_skill_ids。
    """
    session_id = session_id or str(uuid.uuid4())
    all_tools = get_all_tools()
    all_tool_names = [getattr(t, "name", "") for t in all_tools]
    selected_ids, allowed_names = skills.select_skills_for_input(
        user_message,
        all_tool_names=all_tool_names,
        default_allowed_tools=all_tool_names,
    )
    tools = skills.filter_tools_by_allowed(all_tools, allowed_names)
    if not tools:
        tools = all_tools
    reg = skills.get_skill_registry(skills_dir)
    skill_bodies = [reg[sid]["body"] for sid in selected_ids if sid in reg]
    base_prompt = load_agent_system_prompt()
    system_prompt = build_system_prompt(base_prompt, skill_bodies, user_context=user_context)
    accumulated = []
    try:
        for chunk in core.invoke_stream(
            session_id,
            user_message,
            tools,
            system_prompt=system_prompt,
            session_store=session_store,
        ):
            accumulated.append(chunk)
            yield {"type": "chunk", "content": chunk}
        full = "".join(accumulated)
        yield {"type": "done", "content": full, "skill_ids": list(selected_ids)}
    except Exception as e:
        full = "".join(accumulated)
        yield {"type": "done", "content": full or f"请求出错：{e}", "skill_ids": list(selected_ids)}
