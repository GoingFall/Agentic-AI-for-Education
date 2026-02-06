"""
会话持久化：与 src.web.app 使用同一文件 data/sessions/sessions.json。
提供 load_sessions / save_sessions，供 API 与 Web 共享会话存储。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SESSIONS_DIR = Path(__file__).resolve().parents[2] / "data" / "sessions"
SESSIONS_FILE = SESSIONS_DIR / "sessions.json"

MAX_SESSIONS = 20
MAX_MESSAGES_PER_SESSION = 100


def load_sessions() -> tuple[dict[str, Any] | None, str | None]:
    """从磁盘加载会话；无文件或异常时返回 (None, None)。"""
    if not SESSIONS_FILE.is_file():
        return None, None
    try:
        data = json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
        sessions_data = data.get("sessions") or {}
        current_id = data.get("current_id")
        if sessions_data and not current_id:
            current_id = next(iter(sessions_data.keys()))
        return sessions_data, current_id
    except Exception:
        return None, None


def save_sessions(sessions_data: dict[str, Any], current_id: str | None) -> None:
    """将会话与当前 id 写入磁盘。"""
    try:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {"sessions": sessions_data, "current_id": current_id}
        SESSIONS_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


def trim_sessions(session_meta: dict[str, Any]) -> None:
    """限制会话数量与单会话消息数。"""
    if len(session_meta) <= MAX_SESSIONS:
        pass
    else:
        order = sorted(
            session_meta.keys(),
            key=lambda k: session_meta[k].get("updated_at", ""),
            reverse=True,
        )
        for k in order[MAX_SESSIONS:]:
            session_meta.pop(k, None)
    for v in session_meta.values():
        messages = v.get("messages") or []
        if len(messages) > MAX_MESSAGES_PER_SESSION:
            v["messages"] = messages[-MAX_MESSAGES_PER_SESSION:]
