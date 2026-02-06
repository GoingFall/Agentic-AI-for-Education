# 知识图谱展示与控制（防止内存溢出）— maven-rag 参考

本文档说明 maven-rag 中**前端知识图谱展示**与**防止内存溢出**的实现方式，并给出结合到本项目的建议。参考项目路径：`D:\PythonWorkSpace\maven-rag`。

---

## 1. maven-rag 实现概览

### 1.1 后端：子图与节点数量上限

- **子图来源**：不一次性拉全图，而是通过**查询/遍历**得到子图：
  - `GraphService.traverse_subgraph(start_nodes, max_depth)`：从起始节点 BFS 双向扩展，得到子图。
  - GraphRAG / Agentic Traversal 的查询结果中，将子图转为前端用的 `nodes` / `edges`。
- **节点数上限（后端）**：在序列化为可视化格式时统一截断：
  - `graph_rag_service.py`、`agentic_traversal_service.py` 中的 `_graph_to_visualization_format()` 内：
    - 常量 `MAX_NODES = 100`。
    - 若 `len(all_nodes) > MAX_NODES`：按**节点度数**排序，保留度数最高的前 100 个节点，再 `subgraph.subgraph(selected_nodes)`，只输出该子图的 nodes/edges。
  - 这样接口返回的 nodes 数量不超过 100，从源头控制数据量。

**关键代码位置**：

- `src/services/graph_service.py`：`traverse_subgraph(start_nodes, max_depth=2)`
- `src/services/graph_rag_service.py`：`_graph_to_visualization_format()`，约 400–410 行（MAX_NODES=100）
- `src/services/agentic_traversal_service.py`：同上，约 697–706 行

### 1.2 前端：展示与二次保护

- **组件**：`frontend/components/business/GraphVisualizer.tsx`
- **数据**：接收 `{ nodes, edges }`，由父组件从 API 响应（如 GraphRAG/Agentic Traversal）传入。
- **防溢出策略**：
  1. **节点数量上限**：`MAX_NODES = 100`。若 `data.nodes.length > 100`，只取 `data.nodes.slice(0, 100)`。
  2. **边过滤**：只保留两端都在上述节点集合内的边，避免悬空边和无效数据。
  3. **重绘前清空**：`useEffect` 里在每次用新 data 绘制前执行 `svg.selectAll("*").remove()`，避免 D3 节点/边堆积导致 DOM 与内存增长。
  4. **标签截断**：节点标签超过 12 字显示为 `name.substring(0, 12) + '...'`，减少渲染负担。
- **交互**：D3 力导向图、缩放、拖拽、节点点击回调（如 `onNodeClick`），无“按需加载相邻节点”的 API 调用（当前仅用已有 nodes/edges）。

### 1.3 会话侧图谱与存储

- **GraphContext**（见 `docs/FRONTEND_DESIGN.md`）：  
  当前查询子图 + 历史累积图谱；合并时对 nodes/edges 去重，历史图谱可存 `localStorage`。
- **设计要点**：  
  单次展示的数据已由后端与前端双重限制在 100 节点内，因此合并进历史时仍可控制规模；若需更严，可在合并前再次截断（例如历史节点总数上限）。

---

## 2. 与本项目需求的对应（tasks.md 11.1）

| 需求项 | maven-rag 做法 | 本项目建议 |
|--------|----------------|------------|
| **11.1.1.2 增量加载** | 通过“查询得到子图”实现增量：不拉全图，只拉当前查询/遍历得到的子图。 | 提供「按起始节点 + max_depth + max_nodes 取子图」的 API，前端按需请求。 |
| **11.1.1.3 分页查询** | 无显式分页；通过 top_k、max_depth、MAX_NODES 控制单次子图大小。 | 可做：子图接口支持 `offset`/`limit` 或“第 N 批邻居”；或仅用 max_nodes 单次限制。 |
| **11.1.1.4 单次最多 50 节点** | 后端与前端均为 100。 | 将上限改为 50（或可配置），后端序列化子图时与前端展示时均应用同一上限。 |
| **11.1.2.1 节点点击展开** | 有节点点击回调，但未实现“按需加载相邻节点”。 | 点击节点时请求「以该节点为起点的子图」（max_depth=1, max_nodes=50），合并进当前展示图。 |
| **11.1.4.1 视口裁剪/虚拟滚动** | 未做；依赖节点数上限与清空重绘。 | Dash 若用 cytoscape/vis 等，可查是否有视口内渲染；或保持“单次节点数上限”为主手段。 |
| **11.1.4.2 限制同时渲染节点数** | 后端 100 + 前端 100 + 边过滤。 | 与 11.1.1.4 统一：例如 50，后端与前端一致。 |
| **11.1.4.3 缓存与懒加载** | 子图来自每次查询；GraphContext 合并历史。 | 前端缓存「已请求过的 node_id → 子图」，按需合并；历史图谱可设节点总数上限再落盘。 |
| **11.1.4.4 内存监控与告警** | 无。 | 可选：前端定时采样 `performance.memory`（若可用）或监控当前 nodes/edges 数量，超阈值提示或自动收缩。 |

---

## 3. 结合到本项目的实现建议

### 3.1 后端（agent-edu）

- **图存储**：当前为 Neo4j，已有 `learning_path` 等只读查询；**不**一次性导出全图。
- **新增/扩展示意**：
  - **子图接口**（示例）：  
    `GET /api/graph/subgraph?seed_id=lec01&max_depth=2&max_nodes=50`  
    或 `POST /api/graph/subgraph` 请求体：`{ "seed_ids": ["lec01"], "max_depth": 2, "max_nodes": 50 }`  
    在 Neo4j 中做有界 BFS（或 Cypher 的 `*1..max_depth`）+ 在应用层截断为最多 `max_nodes` 个节点，再返回 `{ nodes, edges }`。
  - **序列化格式**：与 maven-rag 一致：nodes 为 `{ id, type, name?, ... }`，edges 为 `{ source, target, type? }`，便于前端复用同一套展示逻辑。
  - **节点选择策略**：若子图节点数超过 `max_nodes`，可仿 maven-rag：按度数或与 seed 的距离排序，保留前 `max_nodes` 个。

### 3.2 前端（Dash 或后续 React）

- **若沿用 Dash**：
  - 使用 dash-cytoscape 或 dash-vis-network 等组件，只将当前子图的 `nodes`/`edges` 传入，**不**传全图。
  - 节点数上限在服务端与前端各做一次（例如 50）：后端子图接口限制 + 前端在收到数据后若仍超限则 slice 并过滤边。
- **若后续引入 React**：
  - 可直接参考 `GraphVisualizer.tsx`：同一套「nodes/edges 上限 + 边过滤 + 清空再绘」策略；上限改为 50 并与后端一致。
  - “节点点击展开”：点击时用当前节点 id 调子图 API（max_depth=1, max_nodes=50），将返回的 nodes/edges 与当前图合并并去重后再渲染。

### 3.3 常量与配置

- 建议在配置或常量中统一**单次展示节点上限**（如 50），后端子图接口与前端展示共用该值，避免前后端不一致导致前端仍拿到过大 payload。

---

## 4. 关键文件索引（maven-rag）

| 用途 | 文件路径 |
|------|----------|
| 前端图谱组件与 100 节点截断、边过滤、清空重绘 | `frontend/components/business/GraphVisualizer.tsx` |
| 子图遍历 | `src/services/graph_service.py`（`traverse_subgraph`） |
| 后端 100 节点截断与可视化格式 | `src/services/graph_rag_service.py`（`_graph_to_visualization_format`） |
| 同上（Agentic） | `src/services/agentic_traversal_service.py`（`_graph_to_visualization_format`） |
| 图谱统计/模式接口 | `main.py`（`/api/graph-stats`、`/api/graph-schema`） |
| 前端图谱状态与合并 | `docs/FRONTEND_DESIGN.md`（GraphContext、GraphManagementTabs） |

---

以上内容可直接用于实现 tasks 11.1（知识图谱可视化与内存控制）时对照 maven-rag 的设计与代码。
