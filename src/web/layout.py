"""
Dash 整体布局：侧栏（会话列表、折叠）+ 主区（消息区 + 输入区）。
"""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

# 侧栏：会话列表容器、新建会话按钮、折叠按钮
SIDEBAR_ID = "sidebar"
SESSIONS_LIST_ID = "sessions-list"
NEW_SESSION_BTN_ID = "new-session-btn"
TOGGLE_SIDEBAR_BTN_ID = "toggle-sidebar-btn"

# 主区：当前会话 id 显示、消息区、loading、输入与发送
CURRENT_SESSION_STORE_ID = "current-session-store"
MESSAGES_STORE_ID = "messages-store"
SESSIONS_META_STORE_ID = "sessions-meta-store"
MESSAGE_CONTAINER_ID = "message-container"
LOADING_ID = "chat-loading"
USER_INPUT_ID = "user-input"
SEND_BTN_ID = "send-btn"
EXPORT_BTN_ID = "export-session-btn"

# 导出下载
EXPORT_DOWNLOAD_ID = "export-download"

# 后台 Agent 请求（第一段回调写入，第二段 background 消费后清空）
AGENT_REQUEST_STORE_ID = "agent-request-store"

# 消息区底部锚点（用于滚动到底部）
MESSAGE_ANCHOR_ID = "message-anchor"
# 仅用于 clientside 滚动回调的占位 Store
SCROLL_DUMMY_STORE_ID = "scroll-dummy-store"

# 流式轮询
STREAMING_INTERVAL_ID = "streaming-interval"


def build_sidebar():
    return dbc.Col(
        [
            html.Div(
                [
                    html.H5("会话", className="mb-3"),
                    html.Div(id=SESSIONS_LIST_ID, children=[]),
                    dbc.Button("新建会话", id=NEW_SESSION_BTN_ID, color="primary", className="mt-2 w-100"),
                ],
                className="p-2",
            )
        ],
        id=SIDEBAR_ID,
        width=12,
        lg=3,
        className="bg-light border-end",
    )


# 首次加载触发初始化
INIT_TRIGGER_STORE_ID = "init-trigger-store"


def build_main():
    return dbc.Col(
        [
            dcc.Store(id=INIT_TRIGGER_STORE_ID, data=0),
            dcc.Store(id=CURRENT_SESSION_STORE_ID, data=None),
            dcc.Store(id=MESSAGES_STORE_ID, data=[]),
            dcc.Store(id=SESSIONS_META_STORE_ID, data={}),
            dcc.Store(id=AGENT_REQUEST_STORE_ID, data=None),
            dcc.Store(id=SCROLL_DUMMY_STORE_ID, data=0),
            dcc.Interval(id=STREAMING_INTERVAL_ID, interval=86400000, n_intervals=0),
            dcc.Download(id=EXPORT_DOWNLOAD_ID),
            html.Div(
                [
                    html.Div(
                        id=MESSAGE_CONTAINER_ID,
                        className="mb-3 overflow-auto",
                        style={"minHeight": "300px", "maxHeight": "60vh"},
                    ),
                    dcc.Loading(
                        id=LOADING_ID,
                        type="default",
                        children=html.Div(id="loading-placeholder"),
                    ),
                    dbc.InputGroup(
                        [
                            dcc.Textarea(
                                id=USER_INPUT_ID,
                                placeholder="输入问题…",
                                rows=2,
                                style={"resize": "vertical"},
                                className="form-control",
                            ),
                            dbc.Button("发送", id=SEND_BTN_ID, color="primary"),
                        ],
                        className="mb-2",
                    ),
                    dbc.Button("导出当前会话", id=EXPORT_BTN_ID, color="secondary", outline=True, size="sm"),
                ],
                className="p-3",
            ),
        ],
        width=12,
        lg=9,
    )


def build_layout():
    return dbc.Container(
        [
            dbc.Row(
                [
                    build_sidebar(),
                    build_main(),
                ],
                className="g-0 min-vh-100",
            )
        ],
        fluid=True,
        className="p-0",
    )
