# 需求/功能 → 参考文件速查表

下表按**需求或功能**列出 maven-rag 中的**参考文件路径**与**一行说明**。路径相对于 maven-rag 根目录（`D:\PythonWorkSpace\maven-rag`）。便于实现时快速定位可复制或借鉴的代码。

---

## 数据与预处理

| 需求/功能 | 参考文件路径 | 说明 |
|-----------|--------------|------|
| 2.1.1 文本解析流水线、多格式分支 | scripts/convert_legal_text_to_json.py | 文本→JSON、条文分割、可选 LLM 关键词 |
| 2.1.1 多格式解析 | scripts/parse_legal_docs.py | JSON/txt/html 分支、条文提取、落盘 JSON |
| 3.1 全量构建、配置与路径 | config/settings.py | DATA_DIR、*_PATH、模型与 API 配置 |
| 3.1 全量向量索引 | scripts/build_index.py | 分块、嵌入、FAISS 写入、设备选择 |
| 3.1 知识库目录索引 | scripts/build_knowledge_index.py | 层次索引构建、knowledge_index.json |
| 3.1 知识图谱构建 | scripts/build_knowledge_graph.py | 实体/关系抽取、图 JSON |

---

## Web 界面（前端）

| 需求/功能 | 参考文件路径 | 说明 |
|-----------|--------------|------|
| 6.1 应用入口与路由 | frontend/App.tsx | AppProvider、Router、Routes、Layout |
| 6.1 入口 HTML | frontend/index.tsx | React 挂载 |
| 6.1 响应式布局、侧边栏 | frontend/components/layout/Sidebar.tsx | 导航、折叠 |
| 6.2 对话页（多模式、输入、发送、流式） | frontend/pages/Query.tsx | mode、query、loading、streamingAnswer/Steps、EventSource |
| 6.2 聊天/答案与引用展示 | frontend/components/legal/AnswerViewer.tsx | Markdown、sources 格式化 |
| 6.3 引用与卡片展示 | frontend/components/legal/AnswerViewer.tsx | 同上；Cases 页为卡片列表 |
| 6.3 图谱可视化 | frontend/components/business/GraphVisualizer.tsx | D3、nodes/edges、交互 |
| 6.4 多会话与持久化 | frontend/contexts/AppContext.tsx | conversations、currentConversation、localStorage、上限与裁剪 |
| 6.4 会话类型定义 | frontend/types.ts | Conversation、GraphData 等 |
| API 客户端与封装 | frontend/api/client.ts | Axios baseURL、实例 |
| 对话/流式/记忆 API 调用 | frontend/api/services.ts | queryService（rag/agent/graphRag/agentStream）、storeMemory |
| 案例列表与卡片 | frontend/pages/Cases.tsx | 筛选、分页、卡片展示 |

---

## API 与后端

| 需求/功能 | 参考文件路径 | 说明 |
|-----------|--------------|------|
| 7.1 对话接口、请求/响应模型 | main.py | StandardQueryRequest、AgentQueryRequest、query_legal、agent_query |
| 7.1 会话/记忆接口 | main.py | MemoryStoreRequest、MemoryRetrieveRequest、store_memory、retrieve_memory、clear_memory |
| 7.1 系统状态与健康检查 | main.py | read_root、_check_*_availability、503 |
| 7.2 统一错误与校验 | main.py | HTTPException、Pydantic 模型、try/except 500 |
| 7.2 中间件（日志/计时） | main.py | @app.middleware("http") |
| 7.3 OpenAPI/Swagger | main.py | FastAPI(title, description, version)、tags= |
| 7.3 API 示例与冒烟测试 | docs/API_EXAMPLES.md | 每接口示例请求/响应 |
| 7.3 冒烟测试脚本 | scripts/run_api_smoke_tests.py | 黑盒请求、写 API_TEST_LOG.md |
| RAG 服务实现 | src/services/rag_service.py | 检索、LLM 生成、sources |
| Agent 服务实现 | src/services/agent_service.py | 多轮检索、流式 |
| 图服务与 GraphRAG | src/services/graph_service.py、graph_rag_service.py | 图查询、子图、推理路径 |
| 记忆服务 | src/services/memory_service.py | 短期/长期记忆、检索 |
| 图数据返回（nodes/edges） | main.py | GraphRAGQueryResponse、AgenticTraversalResponse 的 nodes、edges |

---

## 测试

| 需求/功能 | 参考文件路径 | 说明 |
|-----------|--------------|------|
| 8.1 全局 mock 重依赖 | tests/conftest.py | sentence_transformers、faiss、torch、langchain |
| 8.1 图服务单测 | tests/test_graph_service.py | 实体/关系、图操作 |
| 8.1 图 RAG 单测 | tests/test_graph_rag_service.py | 混合检索、子图、上下文 |
| 8.1 Agentic 单测 | tests/test_agentic_traversal_service.py | schema、迭代查询、答案生成 |
| 8.1 记忆服务单测 | tests/test_memory_service.py | 短期/长期、检索、总结 |
| 8.2 端到端 Agentic | tests/test_integration_agentic.py | 完整 agentic_traversal 流程 |
| 8.2 端到端 GraphRAG | tests/test_integration_graphrag.py | 完整 graph_rag 查询流程 |
| 8.3 需求–测试追溯 | tests/REQUIREMENTS_TRACE.md | 需求ID、测试文件、测试用例、状态 |

---

## 演示与文档

| 需求/功能 | 参考文件路径 | 说明 |
|-----------|--------------|------|
| 9.x 安装、运行、API、FAQ | README.md | 项目说明、运行步骤、curl 示例 |
| 9.x API 示例文档 | docs/API_EXAMPLES.md | 每接口可执行示例与响应摘要 |
| 9.x 技术/实现说明 | docs/DEVELOPER_GUIDE.md | 实现细节、评估入口 |

---

## 配置与部署（参考有限）

| 需求/功能 | 参考文件路径 | 说明 |
|-----------|--------------|------|
| 10.x 环境与启动 | config/settings.py、main.py | .env、API_HOST/PORT、uvicorn.run |
| 10.x 日志配置 | config/logging_config.py | setup_logging |

---

## 扩展功能

| 需求/功能 | 参考文件路径 | 说明 |
|-----------|--------------|------|
| 11.1 知识图谱可视化 | frontend/components/business/GraphVisualizer.tsx | D3、nodes/edges、选中与侧栏 |
| 11.1 API 返回图数据 | main.py | graph_rag_query、agentic_traversal_query 返回 nodes、edges |

---

使用说明：实现某条需求时，先查 [01_requirement_mapping.md](01_requirement_mapping.md) 得参考性与可复用点，再在本表找到对应路径，到 maven-rag 中打开该文件进行复制或改造。
