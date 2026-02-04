# CrewAI 调研

> 与项目「Agentic AI for Science & Engineering Education」相关：CrewAI 是**多智能体编排**开源框架，可将多个 AI Agent 组织成「Crew」协作完成任务；可作为教育助手的**另一种实现路径**（多角色：答疑 Agent + 推荐 Agent + 报告 Agent 等），或与当前「单循环 + Skill」方案对比选型。

## 定义与定位

**CrewAI** 是一个**开源、多智能体编排（multi-agent orchestration）**框架，用 Python 编写，**不依赖 LangChain**，从零构建。

- **官网**：[crewai.com](https://www.crewai.com/) | **开源页**：[crewai.com/open-source](https://www.crewai.com/open-source)
- **仓库**：[github.com/crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
- **文档**：[docs.crewai.com](https://docs.crewai.com/)
- **创始人**：João Moura（IBM 等报道）

核心理念：将多个 AI Agent 组织成 **Crew（班组）**，通过**上下文共享与任务委托**协作完成复杂任务；支持 YAML/代码或两者混合定义，兼顾无代码速度与全代码能力。

## 核心概念

### Agent（智能体）

- **必选属性**：`role`（角色/职能）、`goal`（目标）、`backstory`（背景/人设）。
- **可选**：`llm`、`tools`、`memory`、`reasoning`、`knowledge_sources`、`allow_delegation`、`max_iter`、`verbose` 等。
- **创建方式**：YAML 配置（推荐）或代码中直接实例化 `Agent`。
- **能力**：执行任务、调用工具、与其他 Agent 协作、委托子任务、保持记忆（短/长/实体/上下文）。

### Task（任务）

- **描述**：`description`（任务说明）、`expected_output`（期望输出，如 Markdown/JSON）。
- **归属**：指定执行该任务的 `agent`；可设置 `context` 依赖其他任务的输出。
- **可选**：`output_file`、guardrails、HITL（人工介入）等。

### Crew（班组）

- **组成**：一组 Agent + 一组 Task；可选 **Process**（如 `sequential` 顺序执行、`hierarchical` 层级+管理 Agent）。
- **协作**：通过上下文共享与委托完成多步任务；可选 **Planning**（规划 Agent 先制定步骤）、**Manager Agent** 分配任务。
- **运行**：`crew.kickoff(inputs=...)` 传入输入（如 `topic`），执行后得到各 Task 输出。

## 主要能力（官网总结）

| 能力 | 说明 |
|------|------|
| **Planning** | 专用规划 Agent 为整支 Crew 制定分步计划并共享。 |
| **Reasoning** | Agent 可先对当前目标进行反思、制定执行计划再注入任务描述。 |
| **Tools** | 内置/生态提供大量工具（搜索、网页、向量库查询等），Agent 可配置使用。 |
| **Memory** | 短期、长期、实体、上下文等多类记忆，供 Agent 跨任务使用。 |
| **Knowledge** | **Agentic RAG**：整合文件、网站、向量库等知识源，支持查询重写以优化检索。 |
| **Collaboration** | 通过上下文共享与委托，将多个 Agent 组织成协作班组。 |

## 技术要点

- **定义方式**：Agent/Task/Crew 均支持 **YAML + 代码**；YAML 中可用变量（如 `{topic}`），由 `kickoff(inputs)` 注入。
- **项目结构**：CLI `crewai create crew <name>` 生成项目；内含 `config/agents.yaml`、`config/tasks.yaml`、`crew.py`（`@CrewBase`、`@agent`、`@task`、`@crew`）、`main.py`。
- **工具生态**：CrewAI Toolkit、LangChain Tools 等；文档支持将 **MCP Server 作为 Tool** 接入。
- **可观测**：Tracing 等，便于调试多 Agent 流程。
- **企业版**：CrewAI AMP（Studio 可视化、托管部署）、AMP Factory（自建部署）。

## 实战与教程要点（菜鸟教程）

> 来源：[菜鸟教程 - CrewAI 构建智能体](https://www.runoob.com/ai-agent/crewai-agent.html)

### 对比理解

- **单 Agent**：一个大模型从头干到尾。
- **CrewAI**：产品经理 + 工程师 + 分析师 + 编辑，各司其职；结构化定义「谁（Agent）在什么流程（Process）下完成哪些事（Task）」。

### 环境与安装

- **Python**：≥ 3.10 且 < 3.14；不满足时后续问题多，建议先检查 `python --version`。
- **包管理**：推荐用 **UV** 做依赖与包管理，保证多 Agent 项目环境稳定。
- **安装**：`pip install crewai`；可选 `pip install 'crewai[tools]'` 以使用网络搜索等高级工具；需配合 `langchain`、`openai` 或 LiteLLM（第三方模型如 DeepSeek）。
- **第三方模型**：通过 **LiteLLM** 接入，例如 DeepSeek：`pip install -U litellm`，LLM 配置中 `model="deepseek/deepseek-chat"`（必须带服务商前缀）、`api_base`、`api_key`。

### 核心属性速查（易错点）

| 组件 | 属性 | 说明 / 易错后果 |
|------|------|------------------|
| **LLM** | `model` | LiteLLM 规范：`服务商/模型名`，缺服务商前缀会报 LLM Provider NOT provided。 |
| **LLM** | `api_key` / `api_base` | 鉴权与地址；错误会 401 / LLM Failed。 |
| **Agent** | `allow_delegation` | **极易踩坑**：顺序流水线中，下游 Agent（如写作）应设为 `False`，否则可能二次委托导致失败。 |
| **Task** | `context` | 依赖的上游任务列表；**顺序执行核心**，用于「先研究再写作」等流水线。 |
| **Crew** | `process` | `Process.sequential` 按列表顺序执行；`Process.hierarchical` 需配合 Manager Agent 分配任务。 |

### kickoff() 与输出结构

| 表达式 | 类型 | 用途 |
|--------|------|------|
| `crew.kickoff()` | CrewOutput | 执行结果容器。 |
| `result.raw` | str | **最终文本输出**。 |
| `result.tasks_output` | list/dict | 每个 Task 的输出。 |
| `result.token_usage` | dict | 统计信息。 |

### CLI 与项目结构

- **创建项目**：`crewai create crew <项目名>`，按提示选择模型提供商（含 other/DeepSeek 等）。
- **安装依赖**：进入项目根目录后 `crewai install`。
- **运行**：`crewai run` 或 `python src/<项目名>/main.py`。
- **生成结构示例**：`.env`（API Key）、`pyproject.toml`、`src/<项目名>/main.py`、`crew.py`、`tools/`、`config/agents.yaml`、`config/tasks.yaml`。
- **API 密钥**：建议用 `.env` + `python-dotenv` 加载，避免硬编码。

### Process 类型

- **`Process.sequential`**：任务按列表顺序依次执行，适合有严格依赖的流水线（如先研究后写作）。
- **`Process.hierarchical`**：配合管理者（Manager）Agent 协调与分配任务，适合更复杂、动态的协作。

### 进阶：为 Agent 配备工具 (Tools)

- Agent 可绑定 `tools`，如网络搜索、计算器等；示例：`SerperDevTool`（需 [serper.dev](https://serper.dev/) API Key）、`CalculatorTool`。
- 在创建 Agent 时传入 `tools=[search_tool, calc_tool]`，在 Task 的 `description` 中说明需要调用这些工具完成的分析或计算。

## 与项目关联（Agentic AI for Education）

- **多角色教育 Crew**：例如「研究员 Agent」查课程材料 + 「答疑 Agent」生成带引用的回答 + 「推荐 Agent」根据知识图谱推荐练习；Task 按顺序或带上下文依赖编排。
- **Knowledge / RAG**：Agent 可配置 `knowledge_sources` 或 RAG 类工具，与现有「RAG + 知识图谱」方案兼容；可用 CrewAI 的 Agentic RAG 能力做课程知识检索。
- **与 discussion 方案对比**：当前 discussion 采用「单循环 + Skill」，便于一周内落地、可调试；若希望**演示多角色分工与协作**，可考虑用 CrewAI 实现「答疑 + 推荐」双 Agent 或小型 Crew，作为技术选型之一。
- **注意**：多 Agent 会增加编排与调试复杂度，首版若以「可演示、可讲清」为主，单 Agent + Skill 更易控制；CrewAI 适合作为扩展或备选实现。

## 参考链接

- [CrewAI 官网](https://www.crewai.com/)
- [CrewAI 开源页](https://www.crewai.com/open-source)
- [CrewAI 文档 - Agents](https://docs.crewai.com/en/concepts/agents)
- [CrewAI 文档 - Quickstart](https://docs.crewai.com/en/quickstart)
- [GitHub - crewAI](https://github.com/crewAIInc/crewAI)
- [菜鸟教程 - CrewAI 构建智能体](https://www.runoob.com/ai-agent/crewai-agent.html)（环境、属性表、踩坑、CLI、Tools 示例）
- [IBM - What is crewAI?](https://www.ibm.com/think/topics/crew-ai)
- [DeepLearning.AI - Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/)
- [Building a multi agent system using CrewAI - Medium](https://medium.com/pythoneers/building-a-multi-agent-system-using-crewai-a7305450253e)
