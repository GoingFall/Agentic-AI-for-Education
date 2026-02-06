"""
Dash 整体布局：侧栏（会话列表、折叠）+ 主区（对话 Tab + 知识图谱 Tab）。
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

# 11.1 知识图谱 Tab
TAB_DIALOG_ID = "tab-dialog"
TAB_GRAPH_ID = "tab-graph"
GRAPH_ELEMENTS_STORE_ID = "graph-elements-store"
GRAPH_LEARNING_PATH_STORE_ID = "graph-learning-path-store"
GRAPH_LOAD_BTN_ID = "graph-load-btn"
GRAPH_SEED_DROPDOWN_ID = "graph-seed-dropdown"
GRAPH_DEPTH_INPUT_ID = "graph-depth-input"
GRAPH_LEARNING_POSITION_DROPDOWN_ID = "graph-learning-position-dropdown"
GRAPH_SEARCH_INPUT_ID = "graph-search-input"
GRAPH_FILTER_CHECKLIST_ID = "graph-filter-checklist"
GRAPH_LAYOUT_DROPDOWN_ID = "graph-layout-dropdown"
GRAPH_STATUS_ALERT_ID = "graph-status-alert"
CYTO_COMPONENT_ID = "cyto-graph"

# 拖拽调整：侧边栏 / 底边栏 resizer
SIDEBAR_RESIZER_ID = "sidebar-resizer"
BOTTOM_RESIZER_ID = "bottom-resizer"
MESSAGE_SECTION_ID = "message-section"
INPUT_SECTION_ID = "input-section"
APP_LAYOUT_ID = "app-layout"
MAIN_AREA_ID = "main-area"


def build_sidebar():
    """侧栏：会话列表 + 新建会话。宽度可由侧边 resizer 拖拽调整。"""
    return html.Div(
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
        className="sidebar-panel bg-light border-end",
    )


# 首次加载触发初始化
INIT_TRIGGER_STORE_ID = "init-trigger-store"


def _build_dialog_tab():
    """Tab 1：对话（消息区 + 底边 resizer + 输入区）。底边高度可拖拽调整。"""
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        id=MESSAGE_CONTAINER_ID,
                        className="mb-3 overflow-auto",
                        style={"minHeight": "200px"},
                    ),
                    dcc.Loading(
                        id=LOADING_ID,
                        type="default",
                        children=html.Div(id="loading-placeholder"),
                    ),
                ],
                id=MESSAGE_SECTION_ID,
                className="message-section p-3",
            ),
            html.Div(
                [
                    html.Div(id=BOTTOM_RESIZER_ID, className="resizer resizer-horizontal", title="拖动调整输入区高度"),
                    html.Div(
                        [
                            dbc.InputGroup(
                                [
                                    html.Label("输入问题", htmlFor=USER_INPUT_ID, className="visually-hidden"),
                                    dcc.Textarea(
                                        id=USER_INPUT_ID,
                                        name="user-message",
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
                        id=INPUT_SECTION_ID,
                        className="input-section p-3",
                    ),
                ],
                id="dialog-bottom-bar",
                className="dialog-bottom-bar",
            ),
        ],
        className="dialog-tab-layout",
    )


def _build_graph_tab():
    """Tab 2：知识图谱（控制区 + Cytoscape）。"""
    try:
        import dash_cytoscape as cyto
    except ImportError:
        cyto = None
    seed_options = [{"label": f"lec0{i}", "value": f"lec0{i}"} for i in range(1, 6)]
    learning_position_options = [{"label": "无", "value": ""}] + seed_options
    controls = dbc.Row(
        [
            dbc.Col(
                [
                    html.Label("起始节点", className="form-label small"),
                    dcc.Dropdown(
                        id=GRAPH_SEED_DROPDOWN_ID,
                        options=seed_options,
                        value="lec01",
                        clearable=False,
                        style={"minWidth": "100px"},
                    ),
                ],
                width="auto",
            ),
            dbc.Col(
                [
                    html.Label("深度", htmlFor=GRAPH_DEPTH_INPUT_ID, className="form-label small"),
                    dbc.Input(
                        id=GRAPH_DEPTH_INPUT_ID,
                        name="graph-depth",
                        type="number",
                        min=1,
                        max=3,
                        value=2,
                        style={"width": "60px"},
                    ),
                ],
                width="auto",
            ),
            dbc.Col(dbc.Button("加载子图", id=GRAPH_LOAD_BTN_ID, color="primary", size="sm"), width="auto", className="d-flex align-items-end"),
            dbc.Col(
                [
                    html.Label("当前学习位置", className="form-label small"),
                    dcc.Dropdown(
                        id=GRAPH_LEARNING_POSITION_DROPDOWN_ID,
                        options=learning_position_options,
                        value="",
                        clearable=False,
                        style={"minWidth": "100px"},
                    ),
                ],
                width="auto",
            ),
            dbc.Col(
                [
                    html.Label("搜索节点", htmlFor=GRAPH_SEARCH_INPUT_ID, className="form-label small"),
                    dbc.Input(
                        id=GRAPH_SEARCH_INPUT_ID,
                        name="graph-search",
                        placeholder="id",
                        size="sm",
                        style={"width": "100px"},
                    ),
                ],
                width="auto",
            ),
            dbc.Col(
                [
                    html.Label("类型过滤", className="form-label small"),
                    dcc.Checklist(
                        id=GRAPH_FILTER_CHECKLIST_ID,
                        options=[
                            {"label": "Topic", "value": "Topic"},
                            {"label": "Exercise", "value": "Exercise"},
                            {"label": "Concept", "value": "Concept"},
                        ],
                        value=["Topic", "Exercise", "Concept"],
                        inline=True,
                        className="small",
                    ),
                ],
                width="auto",
            ),
            dbc.Col(
                [
                    html.Label("布局", className="form-label small"),
                    dcc.Dropdown(
                        id=GRAPH_LAYOUT_DROPDOWN_ID,
                        options=[
                            {"label": "力导向（宽松）", "value": "cose"},
                            {"label": "层次展开", "value": "breadthfirst"},
                            {"label": "同心圆", "value": "concentric"},
                        ],
                        value="cose",
                        clearable=False,
                        style={"minWidth": "120px"},
                    ),
                ],
                width="auto",
            ),
        ],
        className="g-2 mb-2 align-items-end",
    )
    # 默认用宽松力导向，减少节点重叠；layout 会由回调根据用户选择动态更新
    _default_layout = {
        "name": "cose",
        "idealEdgeLength": 180,
        "nodeOverlap": 40,
        "nodeRepulsion": 700000,
        "padding": 60,
        "animate": True,
    }
    if cyto is not None:
        cyto_el = html.Div(
            cyto.Cytoscape(
                id=CYTO_COMPONENT_ID,
                elements=[],
                layout=_default_layout,
                style={"width": "100%", "height": "100%", "minHeight": "300px"},
                responsive=True,
                stylesheet=[
                    {"selector": "node", "style": {"label": "data(label)", "width": 24, "height": 24, "text-max-width": "90px", "text-wrap": "ellipsis"}},
                    {"selector": ".Topic", "style": {"background-color": "#1f77b4"}},
                    {"selector": ".Exercise", "style": {"background-color": "#2ca02c"}},
                    {"selector": ".Concept", "style": {"background-color": "#ff7f0e"}},
                    {"selector": ".highlight", "style": {"border-width": 3, "border-color": "#d62728"}},
                    {"selector": ".path", "style": {"border-width": 2, "border-color": "#bcbd22"}},
                    {"selector": "edge", "style": {"width": 1, "line-color": "#ccc", "target-arrow-color": "#ccc", "curve-style": "bezier"}},
                ],
            ),
            className="graph-cyto-wrapper",
        )
    else:
        cyto_el = html.Div("请安装 dash-cytoscape 以显示图谱。", className="text-muted p-3")
    status_alert = html.Div(id=GRAPH_STATUS_ALERT_ID, className="mb-2")
    return html.Div([controls, status_alert, cyto_el], id="graph-tab-content", className="graph-tab-content p-3")


def build_main():
    """主区：Stores + Tabs（对话 / 知识图谱）。"""
    return html.Div(
        [
            dcc.Store(id=INIT_TRIGGER_STORE_ID, data=0),
            dcc.Store(id=CURRENT_SESSION_STORE_ID, data=None),
            dcc.Store(id=MESSAGES_STORE_ID, data=[]),
            dcc.Store(id=SESSIONS_META_STORE_ID, data={}),
            dcc.Store(id=AGENT_REQUEST_STORE_ID, data=None),
            dcc.Store(id=SCROLL_DUMMY_STORE_ID, data=0),
            dcc.Store(id=GRAPH_ELEMENTS_STORE_ID, data=[]),
            dcc.Store(id=GRAPH_LEARNING_PATH_STORE_ID, data=[]),
            dcc.Interval(id=STREAMING_INTERVAL_ID, interval=86400000, n_intervals=0),
            dcc.Download(id=EXPORT_DOWNLOAD_ID),
            dbc.Tabs(
                [
                    dbc.Tab(_build_dialog_tab(), label="对话", tab_id=TAB_DIALOG_ID),
                    dbc.Tab(_build_graph_tab(), label="知识图谱", tab_id=TAB_GRAPH_ID),
                ],
                id="main-tabs",
                active_tab=TAB_DIALOG_ID,
            ),
        ],
        id=MAIN_AREA_ID,
        className="main-area",
    )


def build_layout():
    """整体布局：侧栏 | 侧边 resizer | 主区，侧栏与底边栏均可拖拽调整。"""
    return dbc.Container(
        [
            html.Div(
                [
                    build_sidebar(),
                    html.Div(id=SIDEBAR_RESIZER_ID, className="resizer resizer-vertical", title="拖动调整侧边栏宽度"),
                    build_main(),
                ],
                id=APP_LAYOUT_ID,
                className="app-layout",
            )
        ],
        fluid=True,
        className="p-0",
    )
