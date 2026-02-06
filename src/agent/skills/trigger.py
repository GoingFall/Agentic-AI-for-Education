"""
Skill 触发与选择：根据用户输入匹配 trigger_keywords，返回本回合选中的 Skill 及 allowed_tools。
"""
from __future__ import annotations

from .loader import get_skill_registry


def select_skills_for_input(
    user_input: str,
    *,
    all_tool_names: list[str] | None = None,
    default_allowed_tools: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """
    根据用户输入选择命中的 Skill，返回 (选中的 skill_id 列表, 本回合允许的工具名列表)。
    - 匹配规则：用户消息中包含某 Skill 的任一 trigger_keyword 即命中；
    - 若命中多个 Skill，按 priority 降序取前若干，并合并其 allowed_tools（多 Skill 同时触发时，调用方用合并后的 prompt 与工具传入 Agent）。
    - 若未命中任何 Skill，返回 ([], default_allowed_tools)；若 default_allowed_tools 为 None，则使用 all_tool_names 作为默认（即全部工具）。
    """
    reg = get_skill_registry()
    if not reg:
        default = default_allowed_tools if default_allowed_tools is not None else (all_tool_names or [])
        return [], default

    text = (user_input or "").strip().lower()
    matched: list[tuple[str, int]] = []  # (skill_id, priority)
    for skill_id, cfg in reg.items():
        keywords = cfg.get("trigger_keywords") or []
        for kw in keywords:
            if (kw or "").lower() in text:
                matched.append((skill_id, cfg.get("priority", 0)))
                break
    if not matched:
        default = default_allowed_tools if default_allowed_tools is not None else (all_tool_names or [])
        return [], default
    # 按 priority 降序，再按 skill_id 稳定排序
    matched.sort(key=lambda x: (-x[1], x[0]))
    selected_ids = [x[0] for x in matched]
    # 设计（requirements 2.1.2、design 4.4.1）：概念类答疑命中 qa 时，同时触发推荐，实现「先答疑后推荐」、推荐与当前知识点相关
    if "qa" in selected_ids and "exercise-recommend" not in selected_ids and "exercise-recommend" in reg:
        selected_ids = list(selected_ids) + ["exercise-recommend"]
    allowed: list[str] = []
    seen: set[str] = set()
    for sid in selected_ids:
        for t in reg[sid].get("allowed_tools") or []:
            if t not in seen:
                seen.add(t)
                allowed.append(t)
    return selected_ids, allowed if allowed else (all_tool_names or [])
