"""
Dash 应用入口：布局、全局 session_store/session_meta、callbacks。
运行：python -m src.web.app
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import dash_bootstrap_components as dbc
import httpx
import diskcache
import markdown as md_lib
from dash import (
    ALL,
    DiskcacheManager,
    Input,
    Output,
    State,
    callback_context,
    clientside_callback,
    dcc,
    html,
    no_update,
)
from dash.exceptions import PreventUpdate

from .layout import (
    AGENT_REQUEST_STORE_ID,
    CURRENT_SESSION_STORE_ID,
    CYTO_COMPONENT_ID,
    EXPORT_BTN_ID,
    EXPORT_DOWNLOAD_ID,
    GRAPH_DEPTH_INPUT_ID,
    GRAPH_ELEMENTS_STORE_ID,
    GRAPH_FILTER_CHECKLIST_ID,
    GRAPH_LAYOUT_DROPDOWN_ID,
    GRAPH_LEARNING_PATH_STORE_ID,
    GRAPH_LEARNING_POSITION_DROPDOWN_ID,
    GRAPH_LOAD_BTN_ID,
    GRAPH_SEARCH_INPUT_ID,
    GRAPH_SEED_DROPDOWN_ID,
    GRAPH_STATUS_ALERT_ID,
    INIT_TRIGGER_STORE_ID,
    LOADING_ID,
    MESSAGE_ANCHOR_ID,
    MESSAGE_CONTAINER_ID,
    MESSAGES_STORE_ID,
    NEW_SESSION_BTN_ID,
    SEND_BTN_ID,
    SESSIONS_LIST_ID,
    SESSIONS_META_STORE_ID,
    SCROLL_DUMMY_STORE_ID,
    STREAMING_INTERVAL_ID,
    USER_INPUT_ID,
    build_layout,
)

# 服务端状态：LangChain 历史 + UI 用会话元数据与消息列表
SESSION_STORE: dict = {}  # session_id -> BaseChatMessageHistory（由 agent.session 使用）
SESSION_META: dict = {}   # session_id -> { "title": str, "updated_at": str, "messages": list }

MAX_SESSIONS = 20
MAX_MESSAGES_PER_SESSION = 100

_SESSIONS_DIR = Path(__file__).resolve().parents[2] / "data" / "sessions"
_SESSIONS_FILE = _SESSIONS_DIR / "sessions.json"
_STREAMING_DIR = Path(__file__).resolve().parents[2] / "data" / "streaming"

# 11.1 知识图谱：请求 FastAPI 子图/学习路径（Dash 与 API 分端口时使用）
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MAX_GRAPH_NODES = 50


def _api_subgraph(seed_id: str, max_depth: int, max_nodes: int = MAX_GRAPH_NODES) -> tuple[list, list, str | None]:
    """请求 /api/graph/subgraph，返回 (nodes, edges, error_msg)；成功时 error_msg 为 None。"""
    try:
        r = httpx.get(
            f"{API_BASE}/api/graph/subgraph",
            params={"seed_id": seed_id, "max_depth": max_depth, "max_nodes": max_nodes},
            timeout=10.0,
        )
        if r.status_code != 200:
            return [], [], f"API 返回状态码 {r.status_code}"
        data = r.json()
        return data.get("nodes") or [], data.get("edges") or [], None
    except httpx.ConnectError as e:
        return [], [], f"无法连接 API（{API_BASE}），请确认 API 服务已启动（如：python -m src.api.app）"
    except httpx.TimeoutException:
        return [], [], "请求超时，请稍后重试"
    except Exception as e:
        return [], [], f"子图加载失败：{e!s}"


def _api_learning_path(topic_id: str) -> list:
    """请求 /api/graph/learning-path，返回 path 列表。"""
    if not topic_id:
        return []
    try:
        r = httpx.get(f"{API_BASE}/api/graph/learning-path", params={"topic_id": topic_id}, timeout=10.0)
        if r.status_code != 200:
            return []
        return r.json().get("path") or []
    except Exception:
        return []


def _nodes_edges_to_cyto_elements(
    nodes: list,
    edges: list,
    path_ids: list | None = None,
    current_id: str | None = None,
    type_filter: list | None = None,
    search_id: str | None = None,
) -> list:
    """将 API 的 nodes/edges 转为 Cytoscape elements，并应用 path/高亮/类型过滤/搜索高亮。"""
    path_set = set(path_ids or [])
    type_ok = set(type_filter or ["Topic", "Exercise", "Concept"])
    el = []
    node_ids_ok = set()
    for n in nodes:
        if n.get("type") not in type_ok:
            continue
        nid = n.get("id", "")
        if not nid:
            continue
        node_ids_ok.add(nid)
        classes = [n.get("type", "Node")]
        if nid in path_set:
            classes.append("path")
        if current_id and nid == current_id:
            classes.append("highlight")
        if search_id and search_id.strip() and (search_id.strip() in nid or nid == search_id.strip()):
            classes.append("highlight")
        el.append({"data": {"id": nid, "label": n.get("label") or nid}, "classes": " ".join(classes)})
    for e in edges:
        a, b = e.get("source"), e.get("target")
        if a in node_ids_ok and b in node_ids_ok:
            el.append({"data": {"source": a, "target": b, "type": e.get("type", "")}})
    return el


def _merge_and_cap_subgraph(
    current_nodes: list, current_edges: list, new_nodes: list, new_edges: list, cap: int = MAX_GRAPH_NODES
) -> tuple[list, list]:
    """合并新旧节点/边并去重，截断至 cap 个节点，边只保留两端均在节点集合内的。"""
    by_id = {n.get("id"): n for n in current_nodes if n.get("id")}
    for n in new_nodes:
        if n.get("id"):
            by_id[n["id"]] = n
    nodes_list = list(by_id.values())[:cap]
    node_ids = {n["id"] for n in nodes_list}
    edges_seen = set()
    edges_list = []
    for e in current_edges + new_edges:
        a, b = e.get("source"), e.get("target")
        if a in node_ids and b in node_ids and (a, b) not in edges_seen:
            edges_seen.add((a, b))
            edges_list.append(e)
    return nodes_list, edges_list


def _load_sessions():
    """从磁盘加载会话；无文件或异常时返回 (None, None)。"""
    if not _SESSIONS_FILE.is_file():
        return None, None
    try:
        data = json.loads(_SESSIONS_FILE.read_text(encoding="utf-8"))
        sessions_data = data.get("sessions") or {}
        current_id = data.get("current_id")
        if sessions_data and not current_id:
            current_id = next(iter(sessions_data.keys()))
        return sessions_data, current_id
    except Exception:
        return None, None


def _save_sessions(sessions_data: dict, current_id: str | None):
    """将会话与当前 id 写入磁盘。"""
    try:
        _SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {"sessions": sessions_data, "current_id": current_id}
        _SESSIONS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


_diskcache = diskcache.Cache(Path(__file__).resolve().parents[2] / "data" / "cache")
_background_callback_manager = DiskcacheManager(_diskcache)

app = __import__("dash").Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    background_callback_manager=_background_callback_manager,
)
app.title = "课程助教"
app.layout = build_layout()


# ---------- SSE 流式接口（供外部或 EventSource 消费）----------
@app.server.route("/api/chat/stream")
def stream_chat():
    """GET /api/chat/stream?session_id=...&message=... 流式返回助手回复，每块为 SSE data 行。"""
    from flask import Response, request

    session_id = request.args.get("session_id") or ""
    message = request.args.get("message") or ""
    if not message.strip():
        return Response("missing message\n", status=400, mimetype="text/plain")

    def generate():
        try:
            from langchain_core.chat_history import InMemoryChatMessageHistory

            from src.agent.run import invoke_with_skills_stream

            session_store = {session_id: InMemoryChatMessageHistory()}
            skills_dir = Path(__file__).resolve().parents[2] / "skills"
            for event in invoke_with_skills_stream(
                user_message=message.strip(),
                session_id=session_id or None,
                session_store=session_store,
                skills_dir=skills_dir,
            ):
                if event.get("type") == "chunk":
                    content = event.get("content", "")
                    if content:
                        yield f"data: {json.dumps({'chunk': content}, ensure_ascii=False)}\n\n"
                elif event.get("type") == "done":
                    yield f"data: {json.dumps({'done': True, 'skill_ids': event.get('skill_ids', [])}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------- 首次加载：从磁盘恢复或创建默认会话 ----------
@app.callback(
    Output(CURRENT_SESSION_STORE_ID, "data"),
    Output(SESSIONS_META_STORE_ID, "data"),
    Output(MESSAGES_STORE_ID, "data"),
    Input(INIT_TRIGGER_STORE_ID, "data"),
)
def init_default_session(_trigger):
    loaded, current_id = _load_sessions()
    if loaded and current_id and current_id in loaded:
        messages = loaded[current_id].get("messages", [])
        return current_id, loaded, messages
    sid = str(uuid.uuid4())
    sessions_data = {
        sid: {
            "title": "新会话",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "messages": [],
        }
    }
    _save_sessions(sessions_data, sid)
    return sid, sessions_data, []


def _ensure_session(session_meta: dict, current_id: str | None):
    """若当前无会话则创建并返回新 session_id；否则返回 current_id。"""
    if current_id and current_id in session_meta:
        return current_id
    sid = str(uuid.uuid4())
    session_meta[sid] = {
        "title": "新会话",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "messages": [],
    }
    return sid


def _markdown_content(text: str):
    """将 Markdown 转为 HTML 并用 iframe(srcDoc) 展示，避免 dcc.Markdown 的 defaultProps 警告；高度由前端 resize.js 按内容自适应。"""
    if not (text or "").strip():
        return html.Div()
    try:
        body_html = md_lib.markdown(text, extensions=["nl2br", "fenced_code", "tables"])
        styled = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>body{font-family:inherit;font-size:14px;line-height:1.5;margin:0;padding:6px;} "
            "a{color:#0d6efd;} pre,code{background:rgba(0,0,0,.06);border-radius:4px;} pre{padding:8px 10px;} code{padding:2px 6px;}</style></head><body>"
            + body_html
            + "</body></html>"
        )
        return html.Div(
            html.Iframe(
                srcDoc=styled,
                className="message-content-iframe",
                style={"width": "100%", "minHeight": "24px", "border": "none", "display": "block"},
                title="",
            ),
            className="message-markdown-wrapper",
        )
    except Exception:
        return html.Pre((text or "").strip())


def _trim_sessions(session_meta: dict):
    """限制会话数量与单会话消息数。"""
    if len(session_meta) <= MAX_SESSIONS:
        return
    # 按 updated_at 排序，删最旧的
    order = sorted(
        session_meta.keys(),
        key=lambda k: session_meta[k]["updated_at"],
        reverse=True,
    )
    for k in order[MAX_SESSIONS:]:
        session_meta.pop(k, None)
    for v in session_meta.values():
        if len(v["messages"]) > MAX_MESSAGES_PER_SESSION:
            v["messages"] = v["messages"][-MAX_MESSAGES_PER_SESSION:]


# ---------- 会话列表渲染（每行：会话按钮 + 删除按钮）----------
@app.callback(
    Output(SESSIONS_LIST_ID, "children"),
    Input(SESSIONS_META_STORE_ID, "data"),
    Input(CURRENT_SESSION_STORE_ID, "data"),
)
def render_sessions_list(sessions_data, current_id):
    if not sessions_data:
        return []
    current_id = current_id or ""
    # 固定迭代顺序，并用数字 index 避免 Dash 前端用长 UUID 作键时出现 undefined
    order = sorted(
        sessions_data.keys(),
        key=lambda k: (sessions_data[k].get("updated_at") or "", k),
        reverse=True,
    )
    out = []
    for i, sid in enumerate(order):
        meta = sessions_data[sid]
        title = meta.get("title") or sid[:8]
        updated = meta.get("updated_at", "")[:19].replace("T", " ")
        is_current = sid == current_id
        row = dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        [html.Div(title, className="text-truncate"), html.Small(updated, className="text-muted d-block")],
                        id={"type": "session-btn", "index": i},
                        color="primary" if is_current else "light",
                        outline=is_current,
                        className="w-100 text-start",
                    ),
                    width=9,
                ),
                dbc.Col(
                    dbc.Button("删", id={"type": "session-delete", "index": i}, color="danger", outline=True, size="sm", className="py-0"),
                    width=3,
                    className="d-flex align-items-center",
                ),
            ],
            className="g-1 mb-1",
        )
        out.append(row)
    return out


# ---------- 删除会话 ----------
@app.callback(
    Output(SESSIONS_META_STORE_ID, "data", allow_duplicate=True),
    Output(CURRENT_SESSION_STORE_ID, "data", allow_duplicate=True),
    Output(MESSAGES_STORE_ID, "data", allow_duplicate=True),
    Input({"type": "session-delete", "index": ALL}, "n_clicks"),
    State(SESSIONS_META_STORE_ID, "data"),
    State(CURRENT_SESSION_STORE_ID, "data"),
    prevent_initial_call=True,
)
def delete_session(_n_clicks_list, sessions_data, current_id):
    if not sessions_data:
        raise PreventUpdate
    triggered = callback_context.triggered
    if not triggered or not (triggered[0].get("value") or 0):
        raise PreventUpdate
    ctx = callback_context.triggered_id
    if ctx is None or not isinstance(ctx, dict) or ctx.get("type") != "session-delete":
        raise PreventUpdate
    idx = ctx.get("index")
    # 仅响应用户真实点击：列表因“删后新建会话”重渲染时，新按钮 n_clicks=0 会再次触发，需忽略
    if _n_clicks_list is None or not (0 <= idx < len(_n_clicks_list)) or not (_n_clicks_list[idx] or 0):
        raise PreventUpdate
    order = sorted(
        sessions_data.keys(),
        key=lambda k: (sessions_data[k].get("updated_at") or "", k),
        reverse=True,
    )
    if not isinstance(idx, int) or idx < 0 or idx >= len(order):
        raise PreventUpdate
    sid = order[idx]
    if sid not in sessions_data:
        raise PreventUpdate
    sessions_data = dict(sessions_data)
    sessions_data.pop(sid, None)
    new_current = current_id
    new_messages = []
    if current_id == sid:
        if sessions_data:
            new_current = max(
                sessions_data.keys(),
                key=lambda k: sessions_data[k].get("updated_at", ""),
            )
            new_messages = sessions_data[new_current].get("messages", [])
        else:
            new_current = str(uuid.uuid4())
            sessions_data[new_current] = {
                "title": "新会话",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "messages": [],
            }
    _save_sessions(sessions_data, new_current)
    return sessions_data, new_current, new_messages


# ---------- 点击会话切换 ----------
@app.callback(
    Output(CURRENT_SESSION_STORE_ID, "data", allow_duplicate=True),
    Output(MESSAGES_STORE_ID, "data", allow_duplicate=True),
    Input({"type": "session-btn", "index": ALL}, "n_clicks"),
    State(SESSIONS_META_STORE_ID, "data"),
    prevent_initial_call=True,
)
def switch_session(_n_clicks_list, sessions_data):
    if not sessions_data:
        raise PreventUpdate
    triggered = callback_context.triggered
    if not triggered or not (triggered[0].get("value") or 0):
        raise PreventUpdate
    ctx = callback_context.triggered_id
    if ctx is None or not isinstance(ctx, dict) or ctx.get("type") != "session-btn":
        raise PreventUpdate
    idx = ctx.get("index")
    # 仅响应用户真实点击，避免列表重渲染导致 n_clicks 变化误触发
    if _n_clicks_list is None or not (0 <= idx < len(_n_clicks_list)) or not (_n_clicks_list[idx] or 0):
        raise PreventUpdate
    order = sorted(
        sessions_data.keys(),
        key=lambda k: (sessions_data[k].get("updated_at") or "", k),
        reverse=True,
    )
    if not isinstance(idx, int) or idx < 0 or idx >= len(order):
        raise PreventUpdate
    sid = order[idx]
    if sid not in sessions_data:
        raise PreventUpdate
    messages = sessions_data[sid].get("messages", [])
    _save_sessions(sessions_data, sid)
    return sid, messages


# ---------- 新建会话 ----------
@app.callback(
    Output(CURRENT_SESSION_STORE_ID, "data", allow_duplicate=True),
    Output(MESSAGES_STORE_ID, "data", allow_duplicate=True),
    Output(SESSIONS_META_STORE_ID, "data", allow_duplicate=True),
    Input(NEW_SESSION_BTN_ID, "n_clicks"),
    State(SESSIONS_META_STORE_ID, "data"),
    State(CURRENT_SESSION_STORE_ID, "data"),
    prevent_initial_call=True,
)
def new_session(n_clicks, sessions_data, _current_id):
    if not n_clicks:
        raise PreventUpdate
    sessions_data = sessions_data or {}
    sid = str(uuid.uuid4())
    sessions_data[sid] = {
        "title": "新会话",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "messages": [],
    }
    _trim_sessions(sessions_data)
    _save_sessions(sessions_data, sid)
    return sid, [], sessions_data


# ---------- 发送消息（第一段）：立即追加用户消息并触发后台 Agent ----------
@app.callback(
    Output(LOADING_ID, "children"),
    Output(SESSIONS_META_STORE_ID, "data", allow_duplicate=True),
    Output(MESSAGES_STORE_ID, "data", allow_duplicate=True),
    Output(USER_INPUT_ID, "value"),
    Output(SEND_BTN_ID, "disabled"),
    Output(AGENT_REQUEST_STORE_ID, "data"),
    Input(SEND_BTN_ID, "n_clicks"),
    State(USER_INPUT_ID, "value"),
    State(CURRENT_SESSION_STORE_ID, "data"),
    State(SESSIONS_META_STORE_ID, "data"),
    State(MESSAGES_STORE_ID, "data"),
    prevent_initial_call=True,
)
def on_send_first(n_clicks, user_text, current_id, sessions_data, messages_data):
    """仅追加用户消息、写盘、写入待处理请求并禁用发送；不调用 Agent。"""
    if not n_clicks or not (user_text or "").strip():
        raise PreventUpdate
    user_text = user_text.strip()
    sessions_data = sessions_data or {}
    messages_data = messages_data or []

    current_id = _ensure_session(sessions_data, current_id)
    meta = sessions_data[current_id]
    meta["messages"] = meta.get("messages") or []

    meta["messages"].append({"role": "user", "content": user_text, "selected_skill_ids": None})
    meta["messages"].append({"role": "assistant", "content": "", "selected_skill_ids": []})
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    if meta.get("title") == "新会话" and len(user_text) <= 30:
        meta["title"] = user_text

    new_messages = list(meta["messages"])
    _save_sessions(sessions_data, current_id)

    request_payload = {
        "current_id": current_id,
        "user_text": user_text,
        "request_id": str(uuid.uuid4()),
    }
    return (
        html.Div(),
        sessions_data,
        new_messages,
        "",
        True,  # 禁用发送按钮，由 background 完成后通过 running 恢复
        request_payload,
    )


# ---------- 发送消息（第二段）：后台调用 Agent 并追加助手消息 ----------
@app.callback(
    Output(SESSIONS_META_STORE_ID, "data", allow_duplicate=True),
    Output(MESSAGES_STORE_ID, "data", allow_duplicate=True),
    Output(AGENT_REQUEST_STORE_ID, "data", allow_duplicate=True),
    Input(AGENT_REQUEST_STORE_ID, "data"),
    background=True,
    running=[
        (Output(SEND_BTN_ID, "disabled"), True, False),
    ],
    manager=_background_callback_manager,
    prevent_initial_call=True,
)
def on_send_agent_background(request_data):
    """由 AGENT_REQUEST_STORE 触发：从磁盘加载会话、流式调用 Agent、写文件供轮询，最后写回结果并清空请求。"""
    if not request_data or not isinstance(request_data, dict):
        return no_update, no_update, None
    current_id = request_data.get("current_id")
    user_text = request_data.get("user_text")
    request_id = request_data.get("request_id")
    if not current_id or not (user_text or "").strip():
        return no_update, no_update, None

    loaded, _ = _load_sessions()
    if not loaded or current_id not in loaded:
        return no_update, no_update, None
    sessions_data = dict(loaded)
    meta = sessions_data[current_id]
    meta["messages"] = list(meta.get("messages") or [])
    # 最后一条应为占位 assistant，替换为真实回复
    if meta["messages"] and meta["messages"][-1].get("role") == "assistant":
        meta["messages"].pop()

    _STREAMING_DIR.mkdir(parents=True, exist_ok=True)
    stream_file = _STREAMING_DIR / f"{request_id}.txt" if request_id else None
    accumulated = []
    skill_ids = []

    try:
        from langchain_core.chat_history import InMemoryChatMessageHistory

        from src.agent.run import invoke_with_skills_stream

        history = InMemoryChatMessageHistory()
        for m in meta["messages"]:
            role = m.get("role")
            content = (m.get("content") or "").strip()
            if not content:
                continue
            if role == "user":
                history.add_user_message(content)
            else:
                history.add_ai_message(content)
        session_store = {current_id: history}
        skills_dir = Path(__file__).resolve().parents[2] / "skills"

        for event in invoke_with_skills_stream(
            user_message=user_text,
            session_id=current_id,
            session_store=session_store,
            skills_dir=skills_dir,
        ):
            if event.get("type") == "chunk":
                content = event.get("content", "")
                if content:
                    accumulated.append(content)
                    if stream_file is not None:
                        stream_file.write_text("".join(accumulated), encoding="utf-8")
            elif event.get("type") == "done":
                accumulated = [event.get("content", "")]
                skill_ids = event.get("skill_ids") or []
    except Exception as e:
        accumulated = [f"请求出错：{e}"]

    reply = "".join(accumulated)
    if stream_file is not None and stream_file.exists():
        try:
            stream_file.unlink()
        except Exception:
            pass

    meta["messages"].append({
        "role": "assistant",
        "content": reply,
        "selected_skill_ids": skill_ids,
    })
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    _trim_sessions(sessions_data)
    new_messages = list(meta["messages"])
    _save_sessions(sessions_data, current_id)

    return sessions_data, new_messages, None


# ---------- 仅在有 Agent 请求时启用流式 Interval（无请求时 86400000ms 不频繁触发）----------
@app.callback(
    Output(STREAMING_INTERVAL_ID, "interval"),
    Input(AGENT_REQUEST_STORE_ID, "data"),
)
def set_streaming_interval(request_data):
    if request_data and isinstance(request_data, dict):
        return 400
    return 86400000


# ---------- 流式轮询：读取后台写入的片段并更新最后一条助手消息 ----------
@app.callback(
    Output(MESSAGES_STORE_ID, "data", allow_duplicate=True),
    Input(STREAMING_INTERVAL_ID, "n_intervals"),
    State(AGENT_REQUEST_STORE_ID, "data"),
    State(MESSAGES_STORE_ID, "data"),
    prevent_initial_call=True,
)
def streaming_poll(_n_intervals, request_data, messages_data):
    if not request_data or not isinstance(request_data, dict):
        return no_update
    request_id = request_data.get("request_id")
    if not request_id or not messages_data:
        return no_update
    stream_file = _STREAMING_DIR / f"{request_id}.txt"
    if not stream_file.is_file():
        return no_update
    try:
        content = stream_file.read_text(encoding="utf-8")
    except Exception:
        return no_update
    if not content:
        return no_update
    new_messages = list(messages_data)
    if not new_messages or new_messages[-1].get("role") != "assistant":
        return no_update
    new_messages[-1] = dict(new_messages[-1])
    new_messages[-1]["content"] = content
    return new_messages


# ---------- 根据 messages_store 渲染消息区 ----------
@app.callback(
    Output(MESSAGE_CONTAINER_ID, "children"),
    Input(MESSAGES_STORE_ID, "data"),
)
def render_messages(messages_data):
    if not messages_data:
        return [
            html.Div("暂无消息。发送一条问题开始对话。", className="text-muted p-3"),
            html.Div(id=MESSAGE_ANCHOR_ID),
        ]
    out = []
    for m in messages_data:
        role = m.get("role") or "assistant"
        content = m.get("content") or ""
        skill_ids = m.get("selected_skill_ids") or []
        if role == "user":
            out.append(
                dbc.Row(
                    dbc.Col(
                        dbc.Card([dbc.CardBody(_markdown_content(content))], color="primary", outline=True, className="ms-auto"),
                        width=10,
                    ),
                    className="mb-2 justify-content-end",
                )
            )
        else:
            badges = [dbc.Badge(sid, color="info", className="me-1") for sid in skill_ids]
            # 按 ## 答疑 / ## 推荐练习 分段；推荐练习段落用卡片展示
            main_block = content
            recommend_block = None
            if "## 推荐练习" in content:
                parts = content.split("## 推荐练习", 1)
                main_block = parts[0].strip()
                recommend_block = parts[1].strip() if len(parts) > 1 else None
            body = [_markdown_content(main_block)]
            if recommend_block:
                body.append(
                    dbc.Card(
                        [dbc.CardHeader("推荐练习"), dbc.CardBody(_markdown_content(recommend_block))],
                        color="info",
                        outline=True,
                        className="mt-2",
                    )
                )
            if badges:
                body.append(html.Div(badges, className="mt-2"))
            out.append(
                dbc.Row(
                    dbc.Col(
                        dbc.Card([dbc.CardBody(body)], color="light"),
                        width=10,
                    ),
                    className="mb-2",
                )
            )
    out.append(html.Div(id=MESSAGE_ANCHOR_ID))
    return out


# ---------- 消息更新后滚动到底部（clientside）----------
clientside_callback(
    """
    function(_) {
        var el = document.getElementById('message-container');
        if (el) el.scrollTop = el.scrollHeight;
        return window.dash_clientside.no_update;
    }
    """,
    Output(SCROLL_DUMMY_STORE_ID, "data"),
    Input(MESSAGES_STORE_ID, "data"),
)


# ---------- 导出当前会话 ----------
@app.callback(
    Output(EXPORT_DOWNLOAD_ID, "data"),
    Input(EXPORT_BTN_ID, "n_clicks"),
    State(CURRENT_SESSION_STORE_ID, "data"),
    State(SESSIONS_META_STORE_ID, "data"),
    prevent_initial_call=True,
)
def export_session(n_clicks, current_id, sessions_data):
    if not n_clicks or not current_id or not sessions_data or current_id not in sessions_data:
        raise PreventUpdate
    meta = sessions_data[current_id]
    export_data = {
        "id": current_id,
        "title": meta.get("title"),
        "updated_at": meta.get("updated_at"),
        "messages": meta.get("messages", []),
    }
    content = json.dumps(export_data, ensure_ascii=False, indent=2)
    return dcc.send_string(content, filename=f"session_{current_id[:8]}.json")


# ---------- 11.1 知识图谱：加载子图 ----------
@app.callback(
    [Output(GRAPH_ELEMENTS_STORE_ID, "data"), Output(GRAPH_STATUS_ALERT_ID, "children")],
    Input(GRAPH_LOAD_BTN_ID, "n_clicks"),
    State(GRAPH_SEED_DROPDOWN_ID, "value"),
    State(GRAPH_DEPTH_INPUT_ID, "value"),
    prevent_initial_call=True,
)
def graph_load_subgraph(n_clicks, seed_id, depth_val):
    if not n_clicks:
        raise PreventUpdate
    seed_id = seed_id or "lec01"
    try:
        depth = int(depth_val) if depth_val is not None else 2
        depth = max(1, min(3, depth))
    except (TypeError, ValueError):
        depth = 2
    nodes, edges, error_msg = _api_subgraph(seed_id, depth, MAX_GRAPH_NODES)
    if error_msg:
        return {"nodes": [], "edges": []}, dbc.Alert(error_msg, color="danger", dismissable=True)
    if not nodes and not edges:
        hint = "未获取到节点。请确认 Neo4j 已启动并已执行图谱构建（如 python -m src.knowledge_graph.build）。"
        return {"nodes": [], "edges": []}, dbc.Alert(hint, color="warning", dismissable=True)
    node_ids = {n.get("id") for n in nodes[:MAX_GRAPH_NODES] if n.get("id")}
    nodes = nodes[:MAX_GRAPH_NODES]
    edges = [e for e in edges if e.get("source") in node_ids and e.get("target") in node_ids]
    success_msg = f"已加载 {len(nodes)} 个节点、{len(edges)} 条边。"
    return {"nodes": nodes, "edges": edges}, dbc.Alert(success_msg, color="success", dismissable=True)


# ---------- 11.1 知识图谱：当前学习位置 -> 拉取 path 存 Store ----------
@app.callback(
    Output(GRAPH_LEARNING_PATH_STORE_ID, "data"),
    Input(GRAPH_LEARNING_POSITION_DROPDOWN_ID, "value"),
)
def graph_learning_path_store(topic_id):
    if not topic_id:
        return []
    return _api_learning_path(topic_id)


# ---------- 11.1 知识图谱：Store + path/过滤/搜索 -> Cytoscape elements + layout ----------
def _build_cyto_layout(layout_name: str, node_ids: set[str], seed_id: str | None) -> dict:
    """根据布局类型与当前节点/起点生成 Cytoscape layout 配置，减少重叠、提高可读性。"""
    if layout_name == "breadthfirst":
        root = [seed_id] if seed_id and seed_id in node_ids else (list(node_ids)[:1] if node_ids else [])
        return {"name": "breadthfirst", "roots": root, "directed": True, "padding": 50, "animate": True}
    if layout_name == "concentric":
        return {"name": "concentric", "padding": 50, "animate": True}
    # 默认 cose：力导向且参数偏宽松
    return {
        "name": "cose",
        "idealEdgeLength": 180,
        "nodeOverlap": 40,
        "nodeRepulsion": 700000,
        "padding": 60,
        "animate": True,
    }


@app.callback(
    [Output(CYTO_COMPONENT_ID, "elements"), Output(CYTO_COMPONENT_ID, "layout")],
    Input(GRAPH_ELEMENTS_STORE_ID, "data"),
    Input(GRAPH_LEARNING_PATH_STORE_ID, "data"),
    Input(GRAPH_SEARCH_INPUT_ID, "value"),
    Input(GRAPH_LAYOUT_DROPDOWN_ID, "value"),
    State(GRAPH_LEARNING_POSITION_DROPDOWN_ID, "value"),
    State(GRAPH_FILTER_CHECKLIST_ID, "value"),
    State(GRAPH_SEED_DROPDOWN_ID, "value"),
)
def graph_cyto_elements(store_data, path_data, search_val, layout_name, learning_position, type_filter, seed_id):
    if not store_data or not isinstance(store_data, dict):
        return [], no_update
    nodes = store_data.get("nodes") or []
    edges = store_data.get("edges") or []
    path_ids = path_data if isinstance(path_data, list) else []
    elements = _nodes_edges_to_cyto_elements(
        nodes,
        edges,
        path_ids=path_ids,
        current_id=learning_position or None,
        type_filter=type_filter or ["Topic", "Exercise", "Concept"],
        search_id=search_val,
    )
    node_ids = set()
    for el in elements:
        d = el.get("data") or {}
        if d.get("id") and "source" not in d:
            node_ids.add(d["id"])
    layout_config = _build_cyto_layout(layout_name or "cose", node_ids, seed_id)
    return elements, layout_config


# ---------- 11.1 知识图谱：节点点击展开（按需加载相邻）---------
@app.callback(
    Output(GRAPH_ELEMENTS_STORE_ID, "data", allow_duplicate=True),
    Input(CYTO_COMPONENT_ID, "tapNodeData"),
    State(GRAPH_ELEMENTS_STORE_ID, "data"),
    prevent_initial_call=True,
)
def graph_tap_node_expand(tap_node_data, current_store):
    if not tap_node_data or not isinstance(tap_node_data, dict):
        raise PreventUpdate
    clicked_id = tap_node_data.get("id")
    if not clicked_id:
        raise PreventUpdate
    nodes, edges, _ = _api_subgraph(clicked_id, max_depth=1, max_nodes=MAX_GRAPH_NODES)
    if not nodes and not edges:
        return no_update
    cur_nodes = (current_store or {}).get("nodes") or []
    cur_edges = (current_store or {}).get("edges") or []
    merged_nodes, merged_edges = _merge_and_cap_subgraph(cur_nodes, cur_edges, nodes, edges, cap=MAX_GRAPH_NODES)
    return {"nodes": merged_nodes, "edges": merged_edges}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
