"""
Skill 加载与管理：扫描 skills/*/SKILL.md，解析 YAML frontmatter，维护注册表。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# 项目根：从 src/agent/skills 往上 3 级
def _skills_root() -> Path:
    return Path(__file__).resolve().parents[3]


SKILL_FILENAME = "SKILL.md"
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """解析 SKILL.md：返回 (frontmatter_dict, body_without_frontmatter)。"""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content.strip()
    try:
        import yaml
        meta = yaml.safe_load(match.group(1))
        if meta is None:
            meta = {}
        body = content[match.end() :].strip()
        return meta, body
    except Exception:
        return {}, content.strip()


def load_skills(skills_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """
    扫描 skills_dir 下各子目录中的 SKILL.md，解析 YAML frontmatter 与正文。
    返回 registry: skill_name -> { "name", "description", "trigger_keywords", "allowed_tools", "priority", "body" }。
    skill_name 使用目录名（如 qa、exercise-recommend）。
    """
    root = skills_dir or _skills_root()
    skills_base = root / "skills"
    if not skills_base.is_dir():
        return {}
    registry: dict[str, dict[str, Any]] = {}
    for path in skills_base.iterdir():
        if not path.is_dir():
            continue
        skill_file = path / SKILL_FILENAME
        if not skill_file.is_file():
            continue
        text = skill_file.read_text(encoding="utf-8", errors="replace")
        meta, body = _parse_frontmatter(text)
        name = meta.get("name") or path.name
        trigger_keywords = meta.get("trigger_keywords")
        if isinstance(trigger_keywords, str):
            trigger_keywords = [trigger_keywords]
        if trigger_keywords is None:
            trigger_keywords = []
        allowed_tools = meta.get("allowed_tools")
        if allowed_tools is None:
            allowed_tools = []
        registry[path.name] = {
            "name": name,
            "description": meta.get("description", ""),
            "trigger_keywords": list(trigger_keywords),
            "allowed_tools": list(allowed_tools),
            "priority": meta.get("priority", 0),
            "body": body,
        }
    return registry


# 模块级缓存，首次 load_skills 后填充
_registry: dict[str, dict[str, Any]] | None = None


def get_skill_registry(skills_dir: Path | None = None, reload: bool = False) -> dict[str, dict[str, Any]]:
    """获取 Skill 注册表；若未加载或 reload=True 则先执行 load_skills。"""
    global _registry
    if _registry is None or reload:
        _registry = load_skills(skills_dir)
    return _registry


def get_skill(skill_id: str, skills_dir: Path | None = None) -> dict[str, Any] | None:
    """按 skill_id（目录名）获取单个 Skill 配置与正文；不存在则返回 None。"""
    reg = get_skill_registry(skills_dir)
    return reg.get(skill_id)
