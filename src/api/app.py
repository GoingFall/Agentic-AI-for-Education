"""
FastAPI 应用：对话、会话管理、系统状态。
与 data/sessions/sessions.json 共享存储；与 Dash 可共用同一会话文件。
启动：uvicorn src.api.app:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .schemas import (
    ChatRequestSchema,
    ChatResponseSchema,
    SessionDetailSchema,
    SessionListResponseSchema,
    SessionMetaSchema,
    StatusResponseSchema,
)
from .session_store import load_sessions, save_sessions, trim_sessions

logger = logging.getLogger(__name__)

# Agent 会话历史（LangChain 用），与 web.app 的 SESSION_STORE 用途一致
SESSION_STORE: dict[str, Any] = {}

app = FastAPI(
    title="课程助教 API",
    description="Agentic Edu Helper：对话、会话管理、系统状态（tasks 7.1-7.3）",
    version="0.1.0",
    openapi_tags=[
        {"name": "chat", "description": "7.1.1 对话接口"},
        {"name": "sessions", "description": "7.1.2 会话管理"},
        {"name": "status", "description": "7.1.3 系统状态"},
    ],
)


# ---------- 7.2.2 统一错误格式 ----------
@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": "http_error",
            "detail": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "code": "validation_error",
            "detail": exc.errors() if hasattr(exc, "errors") else str(exc),
        },
    )


@app.exception_handler(Exception)
def internal_exception_handler(request: Request, exc: Exception):
    logger.exception("Internal error")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": "internal_error",
            "detail": "服务器内部错误",
        },
    )


# ---------- 7.2.3 请求频率限制（可配置关闭） ----------
_RATE_LIMIT_DISABLED = os.getenv("API_RATE_LIMIT_DISABLED", "").strip().lower() in ("1", "true", "yes")
_RATE_LIMIT_PER_MINUTE = int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "60"))
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def _rate_limit_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(request: Request) -> None:
    if _RATE_LIMIT_DISABLED:
        return
    if request.url.path != "/api/chat":
        return
    key = _rate_limit_key(request)
    now = time.time()
    window = 60.0  # 1 分钟
    timestamps = _rate_limit_store[key]
    timestamps[:] = [t for t in timestamps if now - t < window]
    if len(timestamps) >= _RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
    timestamps.append(now)


# ---------- 7.3.3 请求耗时日志 ----------
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    _check_rate_limit(request)
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s %.2f ms", request.method, request.url.path, elapsed_ms)
    return response


def _check_chroma() -> str:
    """返回 'ok' 或 'error'。"""
    try:
        from src.agent.tools.rag import retrieve_documents
        retrieve_documents("test", top_k=1)
        return "ok"
    except Exception:
        return "error"


def _check_neo4j() -> str:
    """返回 'ok' 或 'error'。"""
    try:
        from src.agent.tools.graph import _get_driver
        driver = _get_driver()
        driver.verify_connectivity()
        driver.close()
        return "ok"
    except Exception:
        return "error"


# ---------- 7.1.1 对话接口 ----------
@app.post(
    "/api/chat",
    response_model=ChatResponseSchema,
    tags=["chat"],
    summary="发送消息并获取助手回复",
)
def post_chat(body: ChatRequestSchema):
    """调用 Agent（invoke_with_skills），返回 reply、session_id、selected_skill_ids。"""
    session_id = body.session_id or str(uuid.uuid4())
    sessions_data, _ = load_sessions()
    sessions_data = sessions_data or {}

    if session_id not in sessions_data:
        sessions_data[session_id] = {
            "title": "新会话",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "messages": [],
        }

    meta = sessions_data[session_id]
    meta["messages"] = meta.get("messages") or []
    meta["messages"].append({
        "role": "user",
        "content": body.message.strip(),
        "selected_skill_ids": None,
    })
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    if meta.get("title") == "新会话" and len(body.message) <= 30:
        meta["title"] = body.message.strip()

    user_ctx = body.user_context.model_dump() if body.user_context else None
    if user_ctx and user_ctx.get("learned_topic_ids") is None:
        user_ctx = None

    try:
        from src.agent.run import invoke_with_skills
        skills_dir = Path(__file__).resolve().parents[2] / "skills"
        result = invoke_with_skills(
            body.message.strip(),
            session_id=session_id,
            session_store=SESSION_STORE,
            skills_dir=skills_dir,
            user_context=user_ctx,
        )
        reply = result.get("reply", "")
        skill_ids = result.get("selected_skill_ids") or []
    except Exception as e:
        reply = f"请求出错：{e}"
        skill_ids = []
        logger.exception("invoke_with_skills failed")

    meta["messages"].append({
        "role": "assistant",
        "content": reply,
        "selected_skill_ids": skill_ids,
    })
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    trim_sessions(sessions_data)
    save_sessions(sessions_data, session_id)

    return ChatResponseSchema(
        reply=reply,
        session_id=session_id,
        selected_skill_ids=skill_ids,
    )


# ---------- 7.1.2 会话管理 ----------
@app.get(
    "/api/sessions",
    response_model=SessionListResponseSchema,
    tags=["sessions"],
    summary="获取会话列表",
)
def get_sessions():
    """返回与 sessions.json 一致的 sessions 与 current_id。"""
    sessions_data, current_id = load_sessions()
    return SessionListResponseSchema(
        sessions=sessions_data or {},
        current_id=current_id,
    )


@app.post(
    "/api/sessions",
    response_model=SessionDetailSchema,
    tags=["sessions"],
    summary="创建新会话",
)
def create_session():
    """创建新会话并返回 id、title、updated_at、messages。"""
    sessions_data, current_id = load_sessions()
    sessions_data = sessions_data or {}
    session_id = str(uuid.uuid4())
    sessions_data[session_id] = {
        "title": "新会话",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "messages": [],
    }
    trim_sessions(sessions_data)
    save_sessions(sessions_data, session_id)
    return SessionDetailSchema(
        id=session_id,
        title="新会话",
        updated_at=sessions_data[session_id]["updated_at"],
        messages=[],
    )


@app.get(
    "/api/sessions/{session_id}",
    response_model=SessionDetailSchema,
    tags=["sessions"],
    summary="获取单会话详情",
)
def get_session(session_id: str):
    """返回指定会话的 id、title、updated_at、messages。"""
    sessions_data, _ = load_sessions()
    if not sessions_data or session_id not in sessions_data:
        raise HTTPException(status_code=404, detail="会话不存在")
    meta = sessions_data[session_id]
    return SessionDetailSchema(
        id=session_id,
        title=meta.get("title", "新会话"),
        updated_at=meta.get("updated_at", ""),
        messages=meta.get("messages", []),
    )


@app.delete(
    "/api/sessions/{session_id}",
    status_code=204,
    tags=["sessions"],
    summary="删除会话",
)
def delete_session(session_id: str):
    """删除指定会话。"""
    sessions_data, current_id = load_sessions()
    if not sessions_data or session_id not in sessions_data:
        raise HTTPException(status_code=404, detail="会话不存在")
    sessions_data.pop(session_id, None)
    if current_id == session_id:
        new_current = next(iter(sessions_data.keys()), None) if sessions_data else None
        save_sessions(sessions_data, new_current)
    else:
        save_sessions(sessions_data, current_id)
    return None


# ---------- 7.1.3 系统状态 ----------
@app.get(
    "/api/status",
    response_model=StatusResponseSchema,
    tags=["status"],
    summary="系统状态与依赖健康",
)
def get_status():
    """返回服务存活及可选的 Chroma、Neo4j 状态。"""
    return StatusResponseSchema(
        ok=True,
        service="agent-edu-api",
        chroma=_check_chroma(),
        neo4j=_check_neo4j(),
    )


@app.get("/api/health")
def health():
    """简单存活探针。"""
    return {"ok": True}
