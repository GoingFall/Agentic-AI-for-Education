# 需求与参考性逐条映射

本文档按 [tasks.md](../../.kiro/specs/agentic-edu-helper/tasks.md) 中**未完成**的小需求逐条给出：参考性（高/中/低）、可复用点、对应 maven-rag 关键文件。参考项目路径：`D:\PythonWorkSpace\maven-rag`。

---

## 2. 数据预处理和知识库构建

### 2.1.1 实现PDF到文本的转换功能

| 项目 | 说明 |
|------|------|
| **参考性** | **低** |
| **可复用点** | maven-rag 无 PDF 支持，仅支持 .txt / .json / .html。可借鉴：**文本解析流水线**（按条文/章节分割、正则、可选 LLM 关键词）、**多格式分支**（按 suffix 选择解析器）、**结果落盘 JSON**。PDF 实现需自行引入 PyMuPDF、pdfplumber 等。 |
| **关键文件** | `scripts/convert_legal_text_to_json.py`（文本→JSON、条文分割、LLM 关键词抽取）、`scripts/parse_legal_docs.py`（多格式解析、_parse_text_file / _parse_html_file） |

---

## 3. 数据扩展和优化

### 3.1.1 处理剩余的所有PDF文档

| 项目 | 说明 |
|------|------|
| **参考性** | **中高** |
| **可复用点** | **批量脚本结构**：遍历目录、按类型分发、进度与日志、配置从 config 读取路径；全量数据一次性或分批写入。 |
| **关键文件** | `scripts/parse_legal_docs.py`（目录 rglob、多格式）、`scripts/build_index.py`（全量构建向量索引）、`config/settings.py`（DATA_DIR、*_PATH） |

### 3.1.2 建立完整的文档关联关系

| 项目 | 说明 |
|------|------|
| **参考性** | **中高** |
| **可复用点** | 法律条文→章节→条文、案例→罪名/法条的**层次索引**；知识库目录索引的构建与持久化。 |
| **关键文件** | `scripts/build_knowledge_index.py`、`data/knowledge_index.json`、`src/services/knowledge_index_service.py` |

### 3.1.3 优化向量检索性能

| 项目 | 说明 |
|------|------|
| **参考性** | **中** |
| **可复用点** | 向量索引构建脚本（batch、设备选择）、索引与分块分开存储；maven-rag 用 FAISS，agent-edu 用 Chroma，仅流程与配置方式可借鉴。 |
| **关键文件** | `scripts/build_index.py`、`config/settings.py`（EMBEDDING_MODEL_NAME、CHUNKS_PATH） |

---

## 6. Web界面开发

### 6.1 Dash应用基础框架

#### 6.1.1 创建Dash应用主框架

| 项目 | 说明 |
|------|------|
| **参考性** | **中（技术栈不同）** |
| **可复用点** | 应用入口、路由划分（首页/问答/文档/案例）；若坚持 Dash 则仅借鉴**页面划分与信息架构**；若改用 React 可复用 maven-rag 的 App + Router 结构。 |
| **关键文件** | `frontend/App.tsx`、`frontend/index.tsx`、`frontend/pages/`（Home, Query, Documents, Cases） |

#### 6.1.2 设计响应式布局结构

| 项目 | 说明 |
|------|------|
| **参考性** | **中** |
| **可复用点** | 主内容区 + 侧边栏（可折叠）、不同页面共用布局；Dash 需用 dash-bootstrap-components 等自行实现等价布局。 |
| **关键文件** | `frontend/components/layout/Sidebar.tsx`、`frontend/pages/Query.tsx`（showSidebar、主区+侧栏） |

#### 6.1.3 实现基础样式和主题

| 项目 | 说明 |
|------|------|
| **参考性** | **中** |
| **可复用点** | 全局样式、主题色与字体约定；maven-rag 为 React+CSS，Dash 使用自身主题机制，可借鉴**视觉层次与组件划分**。 |
| **关键文件** | `frontend/index.html`、各页面/组件的 className 与布局约定 |

### 6.2 对话界面实现

#### 6.2.1 实现聊天消息显示组件

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 用户/助手消息区分、Markdown 渲染、来源/引用与答案同屏展示。 |
| **关键文件** | `frontend/components/legal/AnswerViewer.tsx`、`frontend/pages/Query.tsx`（消息列表与 result 展示） |

#### 6.2.2 实现用户输入框和发送功能

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 输入框、发送按钮、与当前模式绑定（RAG/Agent/GraphRAG 等）、防重复提交、清空或保留上次输入。 |
| **关键文件** | `frontend/pages/Query.tsx`（query state、handleSubmit、mode 选择） |

#### 6.2.3 实现实时状态显示（正在思考等）

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | loading 状态、流式答案逐字显示（streamingAnswer）、步骤列表（streamingSteps）、EventSource 事件解析与 UI 更新。 |
| **关键文件** | `frontend/pages/Query.tsx`（loading、streamingAnswer、streamingSteps、agentStream）、`frontend/api/services.ts`（agentStream、SSE 事件类型） |

### 6.3 结果展示功能

#### 6.3.1 实现引用来源的格式化显示

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 来源列表（法律名称、条文/案例 ID、标题等）、与答案分区展示、可折叠或展开。 |
| **关键文件** | `frontend/components/legal/AnswerViewer.tsx`（sources 展示）、API 响应中的 `SourceInfo`/sources 结构 |

#### 6.3.2 实现推荐内容的卡片式展示

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 案例推荐卡片（标题、罪名、摘要）、列表+详情；教育场景可改为“推荐讲义/作业”卡片。 |
| **关键文件** | `frontend/pages/Cases.tsx`、`frontend/pages/Query.tsx`（result 中推荐列表的展示方式） |

#### 6.3.3 实现Skill使用状态指示器

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 当前查询模式（RAG/Agent/GraphRAG 等）作为“技能/模式”指示；步骤列表（search_steps/query_steps）即过程状态，可映射为“当前 Skill 执行状态”。 |
| **关键文件** | `frontend/pages/Query.tsx`（modes、mode 选择、streamingSteps 展示） |

### 6.4 会话管理功能

#### 6.4.1 实现多会话标签页支持

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 会话列表、当前会话高亮、切换会话时恢复 lastQuery/lastResult/lastGraph、新建会话入口。 |
| **关键文件** | `frontend/contexts/AppContext.tsx`（conversations、currentConversation、switchConversation、createConversation） |

#### 6.4.2 实现会话历史保存和加载

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | localStorage 持久化、数量上限（MAX_CONVERSATIONS）、单会话数据大小限制（如图谱节点数裁剪）、序列化/反序列化。 |
| **关键文件** | `frontend/contexts/AppContext.tsx`（useEffect 读写 localStorage、sanitizedConversations、QuotaExceededError 处理） |

#### 6.4.3 实现会话分享和导出功能

| 项目 | 说明 |
|------|------|
| **参考性** | **低** |
| **可复用点** | maven-rag 未实现分享/导出；可借鉴会话元数据结构（id、title、updatedAt、lastQuery、lastResult）作为导出格式设计。 |
| **关键文件** | `frontend/contexts/AppContext.tsx`（Conversation 类型）、`frontend/types.ts` |

---

## 7. API接口开发

### 7.1 RESTful API实现

#### 7.1.1 实现对话接口（POST /api/chat）

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | POST /api/query、/api/agent-query 等：Pydantic 请求体（query、session_id、top_k 等）、响应体（answer、sources）、服务层调用与异常转 HTTP。 |
| **关键文件** | `main.py`（StandardQueryRequest、AgentQueryRequest、query_legal、agent_query） |

#### 7.1.2 实现会话管理接口

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 记忆/会话：POST /api/memory/store、POST /api/memory/retrieve、DELETE /api/memory/clear，按 session_id 隔离；可映射为“会话创建、历史拉取、清空”。 |
| **关键文件** | `main.py`（MemoryStoreRequest、MemoryRetrieveRequest、store_memory、retrieve_memory、clear_memory） |

#### 7.1.3 实现系统状态查询接口

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | GET / 返回 status、version、docs；各服务 _check_*_availability()，503 与 startup_error 详情。 |
| **关键文件** | `main.py`（read_root、_check_service_availability 等） |

### 7.2 错误处理和验证

#### 7.2.1 实现输入验证和清理

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | Pydantic BaseModel + Field（类型、description、默认值）、请求体自动校验；业务层可再做长度/敏感词等清理。 |
| **关键文件** | `main.py`（所有 *Request 模型） |

#### 7.2.2 实现统一错误响应格式

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | HTTPException(status_code, detail=...)；try/except 中 logger.error + raise HTTPException(500, detail=str(e))。 |
| **关键文件** | `main.py`（各端点 except、_check_*_availability） |

#### 7.2.3 实现请求频率限制

| 项目 | 说明 |
|------|------|
| **参考性** | **低** |
| **可复用点** | maven-rag 未实现限流；可自行引入 slowapi 或中间件计数，仅“在 FastAPI 中加中间件”的模式可参考 main 的 log 中间件。 |
| **关键文件** | `main.py`（@app.middleware("http")） |

### 7.3 API文档和测试

#### 7.3.1 生成API文档（OpenAPI/Swagger）

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | FastAPI 自带 /docs、/openapi.json；tags 分组、summary、description、请求/响应模型自动出现在文档。 |
| **关键文件** | `main.py`（app = FastAPI(..., title=..., description=..., version=...)、各路由 tags=） |

#### 7.3.2 创建API测试用例

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 黑盒冒烟：按用例文件逐个请求、记录状态码与耗时、结果写入 Markdown 日志；拒答重试等启发式。 |
| **关键文件** | `scripts/run_api_smoke_tests.py`、`docs/API_EXAMPLES.md`（每接口示例请求/响应） |

#### 7.3.3 实现API性能监控

| 项目 | 说明 |
|------|------|
| **参考性** | **中** |
| **可复用点** | 请求 middleware 内计时（process_time）、日志输出；可扩展为打点上报或 Prometheus。 |
| **关键文件** | `main.py`（@app.middleware("http")、start_time、process_time） |

---

## 8. 测试和质量保证

### 8.1 单元测试

#### 8.1.1 编写数据预处理模块测试

| 项目 | 说明 |
|------|------|
| **参考性** | **中** |
| **可复用点** | 解析器/构建脚本的**输入-输出**单测、mock 文件路径；conftest 中 mock 重依赖（如 torch、faiss）避免 CI 安装成本。 |
| **关键文件** | `tests/conftest.py`（mock sentence_transformers、faiss、torch）、各 test_*_service.py 的 fixture 用法 |

#### 8.1.2 编写Agent核心功能测试

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 服务类方法级单测、mock LLM/RAG/图服务、断言返回结构与关键字段。 |
| **关键文件** | `tests/test_agentic_traversal_service.py`、`tests/test_graph_rag_service.py` |

#### 8.1.3 编写Skill功能测试

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 与 8.1.2 类似：对“答疑/推荐”等业务服务的输入输出单测；maven-rag 为 RAG/GraphRAG/Agent，可参考用例结构。 |
| **关键文件** | `tests/test_graph_service.py`、`tests/test_memory_service.py` |

#### 8.1.4 编写工具接口测试

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 对“检索/图查询”等工具接口的单元测试；mock 底层依赖后只测工具层逻辑。 |
| **关键文件** | `tests/test_graph_service.py`（find_nodes、get_neighbors 等）、`tests/test_graph_rag_service.py` |

### 8.2 集成测试

#### 8.2.1 端到端对话流程测试

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 从请求到响应的完整链路、多组件协同（RAG+LLM、图+检索）；使用真实或轻量 fixture 数据。 |
| **关键文件** | `tests/test_integration_agentic.py`、`tests/test_integration_graphrag.py` |

#### 8.2.2 多Skill协同工作测试

| 项目 | 说明 |
|------|------|
| **参考性** | **中** |
| **可复用点** | maven-rag 为多“查询模式”（RAG/Agent/GraphRAG）而非多 Skill；可借鉴“多模式/多服务组合”的集成测例设计。 |
| **关键文件** | `tests/test_integration_agentic.py`（agentic_traversal 完整流程） |

#### 8.2.3 异常情况处理测试

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 服务不可用、错误输入、超时等；断言 HTTP 状态码与错误信息。 |
| **关键文件** | 各 test_* 中的 try/except 与 assert、main 中的 HTTPException 分支 |

### 8.3 属性基测试（Property-Based Testing）

#### 8.3.1～8.3.4 引用准确性 / 推荐一致性 / 会话连续性 / 技能选择正确性

| 项目 | 说明 |
|------|------|
| **参考性** | **中** |
| **可复用点** | maven-rag 无现成 property-based 测试；**需求–测试追溯表**可复用为上述属性的用例设计依据（哪些接口/数据需满足哪条性质）。 |
| **关键文件** | `tests/REQUIREMENTS_TRACE.md`（需求ID、测试文件、测试用例、状态） |

### 8.4 性能测试

#### 8.4.1～8.4.3 响应时间基准 / 并发压力 / 内存与CPU监控

| 项目 | 说明 |
|------|------|
| **参考性** | **低** |
| **可复用点** | 无专门性能/压力脚本；可参考 main 的 middleware 计时与日志，自行引入 pytest-benchmark、locust 或监控 SDK。 |
| **关键文件** | `main.py`（middleware 中 process_time） |

---

## 9. 演示准备和优化

### 9.1.1～9.1.3 演示脚本准备

| 项目 | 说明 |
|------|------|
| **参考性** | **中** |
| **可复用点** | README 中的运行步骤、API 使用示例；API_EXAMPLES.md 的“每接口一个可执行示例”可作为演示用例与备用请求。 |
| **关键文件** | `README.md`、`docs/API_EXAMPLES.md` |

### 9.2.1～9.2.3 项目视频制作

| 项目 | 说明 |
|------|------|
| **参考性** | **低** |
| **可复用点** | 无视频脚本；可借鉴 README 的功能列表与“使用方式”作为视频大纲。 |
| **关键文件** | `README.md`（功能特性、API 端点说明） |

### 9.3.1～9.3.3 文档完善

| 项目 | 说明 |
|------|------|
| **参考性** | **中** |
| **可复用点** | 用户手册：安装、运行、API 使用、FAQ；技术文档：DEVELOPER_GUIDE、API_EXAMPLES；展示材料：README 结构。 |
| **关键文件** | `README.md`、`docs/API_EXAMPLES.md`、`docs/DEVELOPER_GUIDE.md` |

---

## 10. 部署和运维

### 10.1.1～10.3.3 部署环境 / 应用部署 / 监控和日志

| 项目 | 说明 |
|------|------|
| **参考性** | **低** |
| **可复用点** | 无 Docker/编排/监控示例；仅 .env 配置、uvicorn 启动方式、logging 配置可参考。 |
| **关键文件** | `config/settings.py`、`config/logging_config.py`、`main.py`（`if __name__ == "__main__"`、uvicorn.run） |

---

## 11. 扩展功能开发（可选）

### 11.1 知识框架展示功能

#### 11.1.1 实现知识图谱可视化组件

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 使用 D3 的图谱组件、接收 nodes/edges、与查询结果联动（API 返回 nodes/edges）。 |
| **关键文件** | `frontend/components/business/GraphVisualizer.tsx`、`main.py`（GraphRAG/Agentic 响应中的 nodes、edges） |

#### 11.1.2 添加交互式图谱浏览功能

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | 缩放、拖拽、节点高亮/选中、侧边栏展示选中节点详情。 |
| **关键文件** | `frontend/components/business/GraphVisualizer.tsx`、`frontend/pages/Query.tsx`（selectedNode、setActiveSidebarTab） |

#### 11.1.3 实现学习路径可视化

| 项目 | 说明 |
|------|------|
| **参考性** | **中** |
| **可复用点** | 图谱本身可表达“先修/顺序”关系；学习路径可作为子图或高亮路径在 GraphVisualizer 上展示，需适配教育图谱 schema。 |
| **关键文件** | `frontend/components/business/GraphVisualizer.tsx`、图数据中的 path/reasoning_path 等 |

#### 11.1.4 内存优化和性能控制

| 项目 | 说明 |
|------|------|
| **参考性** | **高** |
| **可复用点** | **后端**：子图序列化前按度数排序截断为最多 MAX_NODES（100）；`traverse_subgraph(start_nodes, max_depth)` 控制遍历范围，不拉全图。**前端**：接收的 nodes 超过上限时 slice + 过滤边；每次重绘前 `svg.selectAll("*").remove()` 避免 DOM/内存堆积；标签截断。本项目可将上限改为 50，并增加子图 API（seed + max_depth + max_nodes）。 |
| **关键文件** | `frontend/components/business/GraphVisualizer.tsx`（MAX_NODES=100、边过滤、清空重绘）、`src/services/graph_rag_service.py` 与 `agentic_traversal_service.py` 的 `_graph_to_visualization_format()`（MAX_NODES=100）、`src/services/graph_service.py`（`traverse_subgraph`）。 |
| **详细说明** | 见 [04_knowledge_graph_display_and_memory_control.md](04_knowledge_graph_display_and_memory_control.md) |

### 11.2～11.3、12.x 学情分析 / 高级交互 / 多课程与硬件扩展等

| 项目 | 说明 |
|------|------|
| **参考性** | **低** |
| **可复用点** | 领域不同（法律 vs 教育），无直接复用代码；仅通用模式（统计、多模态、配置化）可思路借鉴。 |
| **关键文件** | 无一一对应；可泛览 `src/services/`、`frontend/pages/` 的扩展方式。 |

---

以上为未完成需求的完整映射；实现时请结合 [02_reusable_design.md](02_reusable_design.md) 与 [03_file_reference.md](03_file_reference.md) 定位具体文件与架构。
