# API 与 Web 验收测试用例（6.1–6.4 + 7.1–7.3）

本文档用于本地逐项验收 tasks.md 第 6、7 节需求。每项标注对应子条，便于勾选与需求追溯。

---

## 前置条件

- 项目根目录已执行：`pip install -r requirements.txt`
- 可选：`.env` 已配置（OpenRouter、Neo4j、Chroma），用于真实对话与状态检查

---

## 自动化测试（.env 就绪时）

- **集成测试（模拟前端「你好？」）**：在项目根执行  
  `pytest tests/agent/test_invoke_integration.py -v`  
  会读取 `.env` 中的 `OPENROUTER_API_KEY`；未配置时自动 skip，配置后校验 `invoke_with_skills("你好？", ...)` 返回结构且无 `'str' object has no attribute "get"` 等异常。
- **脚本模拟**：`python scripts/simulate_chat_hello.py` 同样调用「你好？」并打印回复与 Skill IDs（脚本内会加载 `.env`）。

---

## 一、Web 界面验收（6.1–6.4）

### 启动 Web

```bash
python -m src.web.app
```

浏览器访问：**http://127.0.0.1:8050/**（勿用 http://0.0.0.0:8050/）

---

### 6.1 Dash 应用基础框架

| 用例编号 | tasks | 步骤 | 预期 | 勾选 |
|----------|-------|------|------|------|
| 6.1.1 | 6.1.1 | 启动后查看页面 | 存在 Dash 主框架，标题为「课程助教」 | [ ] |
| 6.1.2 | 6.1.2 | 查看布局 | 侧栏（会话列表、新建会话）+ 主区（消息区、输入区）；响应式（可缩放窗口） | [ ] |
| 6.1.3 | 6.1.3 | 查看样式 | 使用 FLATLY 主题，样式一致 | [ ] |

---

### 6.2 对话界面实现

| 用例编号 | tasks | 步骤 | 预期 | 勾选 |
|----------|-------|------|------|------|
| 6.2.1 | 6.2.1 | 发送一条消息 | 用户消息右对齐、助手消息左对齐；助手内容支持 Markdown 渲染 | [ ] |
| 6.2.2 | 6.2.2 | 在输入框输入内容后点「发送」 | 消息发出、输入框清空、发送按钮短暂禁用后恢复 | [ ] |
| 6.2.3 | 6.2.3 | 发送消息过程中观察 | 出现「正在思考」等加载状态（dcc.Loading） | [ ] |

**建议输入（与 results 知识库对应）：**

- 答疑：`什么是卷积？`（对应 lec04）、`傅里叶变换的定义`（对应讲义内容）
- 推荐：`推荐下一步练习`、`我学了第1讲，该做什么题`（触发 exercise-recommend）

---

### 6.3 结果展示功能

| 用例编号 | tasks | 步骤 | 预期 | 勾选 |
|----------|-------|------|------|------|
| 6.3.1 | 6.3.1 | 发送「什么是卷积？」等答疑问题 | 回复中引用来源以 Markdown 形式体现（如「第 X 讲」「章节 Y」） | [ ] |
| 6.3.2 | 6.3.2 | 发送「推荐下一步练习」等 | 若回复含「## 推荐练习」，该段以卡片（Card）形式展示 | [ ] |
| 6.3.3 | 6.3.3 | 查看助手消息下方 | 显示 Skill 标签（如 qa、exercise-recommend）的 Badge | [ ] |

---

### 6.4 会话管理功能

| 用例编号 | tasks | 步骤 | 预期 | 勾选 |
|----------|-------|------|------|------|
| 6.4.1 | 6.4.1 | 点击「新建会话」、再点击侧栏不同会话 | 多会话以标签/按钮形式存在，切换后主区显示对应会话消息 | [ ] |
| 6.4.2 | 6.4.2 | 刷新页面或重启应用 | 会话列表与当前选中会话从 `data/sessions/sessions.json` 恢复 | [ ] |
| 6.4.3 | 6.4.3 | 点击「导出当前会话」 | 浏览器下载 JSON 文件（含 id、title、updated_at、messages） | [ ] |

---

## 二、API 接口验收（7.1–7.3）

### 启动 API

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Base URL：**http://127.0.0.1:8000**

---

### 7.1.1 对话接口（POST /api/chat）

| 用例编号 | tasks | 步骤与示例 | 预期 | 勾选 |
|----------|-------|------------|------|------|
| 7.1.1-a | 7.1.1 | 不传 session_id，发送一条消息 | 200；响应含 `reply`、`session_id`、`selected_skill_ids` | [ ] |
| 7.1.1-b | 7.1.1 | 使用上一步返回的 session_id 再发一条 | 200；同一 session_id，会话延续 | [ ] |

**curl 示例（7.1.1-a）：**

```bash
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"什么是卷积?\"}"
```

**预期响应结构：** `{"reply":"...", "session_id":"...", "selected_skill_ids":[...]}`

**使用 data/sessions 已有 session_id 续聊（可选）：**

从 `data/sessions/sessions.json` 中取任意 `sessions` 下的 key 作为 `session_id`：

```bash
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"推荐下一步练习\", \"session_id\": \"<从 sessions.json 复制的 id>\"}"
```

---

### 7.1.2 会话管理接口

| 用例编号 | tasks | 步骤与示例 | 预期 | 勾选 |
|----------|-------|------------|------|------|
| 7.1.2-a | 7.1.2 | GET 会话列表 | 200；body 含 `sessions`（对象）、`current_id` | [ ] |
| 7.1.2-b | 7.1.2 | POST 创建会话 | 200；body 含 `id`、`title`、`updated_at`、`messages` | [ ] |
| 7.1.2-c | 7.1.2 | GET 单会话详情 | 200；含该会话的 id、title、messages | [ ] |
| 7.1.2-d | 7.1.2 | DELETE 会话 | 204；再 GET 该 id 返回 404 | [ ] |

**curl 示例：**

```bash
# GET 列表
curl -s http://127.0.0.1:8000/api/sessions

# POST 创建
curl -s -X POST http://127.0.0.1:8000/api/sessions

# GET 详情（将 <session_id> 替换为实际 id）
curl -s http://127.0.0.1:8000/api/sessions/<session_id>

# DELETE（将 <session_id> 替换为实际 id）
curl -s -X DELETE http://127.0.0.1:8000/api/sessions/<session_id> -w "%{http_code}"
```

**边界：** 对不存在的 `session_id` 执行 GET 或 DELETE，预期 404，且 body 含 `error: true`、`code`、`detail`。

---

### 7.1.3 系统状态查询接口

| 用例编号 | tasks | 步骤与示例 | 预期 | 勾选 |
|----------|-------|------------|------|------|
| 7.1.3-a | 7.1.3 | GET /api/status | 200；body 含 `ok: true`、`service`、`chroma`、`neo4j` | [ ] |
| 7.1.3-b | 7.1.3 | GET /api/health | 200；body 含 `ok: true` | [ ] |

```bash
curl -s http://127.0.0.1:8000/api/status
curl -s http://127.0.0.1:8000/api/health
```

---

### 7.2 错误处理和验证

| 用例编号 | tasks | 步骤与示例 | 预期 | 勾选 |
|----------|-------|------------|------|------|
| 7.2.1 | 7.2.1 | POST /api/chat 空 message | 422；body 含 `error`、`code: "validation_error"` | [ ] |
| 7.2.1-b | 7.2.1 | POST /api/chat message 超长（>4096 字符） | 422 | [ ] |
| 7.2.2 | 7.2.2 | 任意 4xx/5xx | 统一格式：`{"error": true, "code": "...", "detail": "..."}` | [ ] |
| 7.2.3 | 7.2.3 | 在限流开启时对 /api/chat 短时间大量请求 | 超过限制后返回 429（可选；本地可设 API_RATE_LIMIT_DISABLED=1 关闭限流） | [ ] |

```bash
# 空 message
curl -s -X POST http://127.0.0.1:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"\"}" -w "\n%{http_code}"
```

---

### 7.3 API 文档和测试

| 用例编号 | tasks | 步骤 | 预期 | 勾选 |
|----------|-------|------|------|------|
| 7.3.1 | 7.3.1 | 浏览器打开 http://127.0.0.1:8000/docs | Swagger UI 展示 OpenAPI；含 chat、sessions、status 标签 | [ ] |
| 7.3.1-b | 7.3.1 | GET http://127.0.0.1:8000/openapi.json | 返回 OpenAPI JSON | [ ] |
| 7.3.2 | 7.3.2 | 在项目根执行 `pytest tests/api/ -v` | 全部 API 用例通过 | [ ] |
| 7.3.3 | 7.3.3 | 发送若干 API 请求后查看启动 API 的终端 | 有请求耗时日志（方法、路径、毫秒） | [ ] |

---

## 三、与 results / data/sessions 的模拟数据对应

- **答疑类**：`什么是卷积?`、`傅里叶变换的定义` —— 对应 results 中 lec04、lec05 等讲义内容，便于核对引用。
- **推荐类**：`推荐下一步练习`、`我学了第1讲，该做什么题` —— 对应知识图谱 PREREQUISITE/COVERS，可核对推荐是否合理。
- **会话**：可直接使用 `data/sessions/sessions.json` 里已有的 `sessions` 的 key 作为 `session_id` 做 GET 详情或续聊，验证 API 与文件存储一致。

---

## 四、需求追溯汇总

| 大项 | 子条 | 本文档用例 |
|------|------|------------|
| 6.1 | 6.1.1–6.1.3 | 6.1.1–6.1.3 |
| 6.2 | 6.2.1–6.2.3 | 6.2.1–6.2.3 |
| 6.3 | 6.3.1–6.3.3 | 6.3.1–6.3.3 |
| 6.4 | 6.4.1–6.4.3 | 6.4.1–6.4.3 |
| 7.1 | 7.1.1–7.1.3 | 7.1.1-a/b, 7.1.2-a~d, 7.1.3-a/b |
| 7.2 | 7.2.1–7.2.3 | 7.2.1, 7.2.1-b, 7.2.2, 7.2.3 |
| 7.3 | 7.3.1–7.3.3 | 7.3.1, 7.3.1-b, 7.3.2, 7.3.3 |
