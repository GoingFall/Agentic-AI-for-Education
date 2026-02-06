"""API 请求/响应 Pydantic 模型。"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# 与 app.py 中 message 长度、会话格式对齐
MESSAGE_MAX_LENGTH = 4096


class UserContextSchema(BaseModel):
    """用户上下文，如已学讲次，供推荐 Skill 使用。"""
    learned_topic_ids: list[str] | None = Field(default=None, description="已学讲次 ID 列表")


class ChatRequestSchema(BaseModel):
    """POST /api/chat 请求体。"""
    message: str = Field(..., min_length=1, max_length=MESSAGE_MAX_LENGTH, description="用户消息")
    session_id: str | None = Field(default=None, description="会话 ID，不传则自动创建")
    user_context: UserContextSchema | None = Field(default=None, description="用户上下文（如已学讲次）")


class ChatResponseSchema(BaseModel):
    """POST /api/chat 响应。"""
    reply: str = Field(..., description="助手回复")
    session_id: str = Field(..., description="会话 ID")
    selected_skill_ids: list[str] = Field(default_factory=list, description="本回合命中的 Skill ID")


class SessionMetaSchema(BaseModel):
    """单条会话元数据（列表项）。"""
    title: str
    updated_at: str
    messages: list[dict[str, Any]] = Field(default_factory=list)


class SessionDetailSchema(SessionMetaSchema):
    """单会话详情（含 id）。"""
    id: str


class SessionListResponseSchema(BaseModel):
    """GET /api/sessions 响应。"""
    sessions: dict[str, SessionMetaSchema] = Field(default_factory=dict)
    current_id: str | None = None


class StatusResponseSchema(BaseModel):
    """GET /api/status 响应。"""
    ok: bool = True
    service: str = "agent-edu-api"
    chroma: str | None = Field(default=None, description="Chroma 状态：ok / error")
    neo4j: str | None = Field(default=None, description="Neo4j 状态：ok / error")
