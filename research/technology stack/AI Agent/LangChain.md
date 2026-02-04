# LangChain 调研

> 与项目「Agentic AI for Science & Engineering Education」相关：可作为构建教育场景下 AI 助手/Agent 的编排框架与开发平台选型参考。

## 定义与定位

**LangChain** 是用于构建、测试与部署可靠 AI Agent 的工程平台与开源框架。开发者可用其快速连接多种 LLM（OpenAI、Anthropic、Google 等），并以少量代码搭建具备工具调用、记忆与检索等能力的 Agent 应用。

- **来源**：[LangChain 官网](https://www.langchain.com/)、[LangChain 文档 - Overview](https://docs.langchain.com/oss/python/langchain/overview)

### 与 LangGraph 的关系

- **LangChain**：高层抽象，适合快速搭建 Agent 与自治应用；内置预置 Agent 架构与模型集成，约 10 行代码即可跑通。
- **LangGraph**：底层编排框架与运行时，适合需要「确定性 + Agent 工作流」混合、重度定制与精细控制延迟的场景。
- LangChain 的 Agent 基于 LangGraph 实现，从而获得持久化执行、流式输出、人机协同、状态持久化等能力；基础使用 LangChain 时无需直接学 LangGraph。

## 核心能力与组件（文档结构）

| 维度 | 内容 |
|------|------|
| **模型** | 统一模型接口，可无缝切换不同厂商，避免供应商锁定。 |
| **Agent** | 易用且灵活：简单场景少量代码即可，复杂场景支持上下文工程与定制。 |
| **工具 (Tools)** | 与外部 API、函数等集成，供 Agent 按需调用。 |
| **记忆** | 短期记忆、长期记忆，支持多轮对话与状态持久化。 |
| **检索 (Retrieval)** | 与 RAG、向量库等结合，为生成提供外部知识。 |
| **高级** | Guardrails、人机协同 (Human-in-the-loop)、MCP、多 Agent 等。 |
| **开发与部署** | LangSmith：可观测性、评估、部署；Agent Builder 支持无代码/低代码搭建。 |

## 平台与生态（LangSmith）

- **可观测性**：追踪执行路径、状态转换与运行时指标，便于调试复杂 Agent 行为。
- **评估**：将线上数据转为测试集，用自动评估器与人工反馈打分，持续迭代质量。
- **部署**：针对长时间运行、需人工协作的 Agent 工作流，提供内存、弹性伸缩与企业级安全等能力。
- **框架中立**：可与现有技术栈并存，通过 TypeScript/Python SDK 接入。

## 简要代码示例（文档）

```python
# pip install -qU langchain "langchain[anthropic]"
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
```

## 与项目关联

- 科学/工程教育 AI 助手可考虑用 **LangChain** 做：统一模型接口、Agent 编排、工具（如题库/实验 API）、检索（RAG）与记忆。
- 若首版追求**快速上线**，LangChain 的「少量代码建 Agent + 多模型/多工具集成」可降低开发成本。
- 若后续需要**强可控流程**（如固定答疑步骤、练习推荐流水线），可再评估是否深入 **LangGraph** 或保持「单主循环 + 工具」的简单形态以符合 AGENTS.md 中的控制循环设计原则。

## 实战与教程要点（菜鸟教程）

> 来源：[菜鸟教程 - LangChain 制作智能体](https://www.runoob.com/ai-agent/langchain-agent.html)

### LangChain 解决的核心问题

LangChain 重点不在于「怎么调模型」，而在于：

- **多步骤推理**如何组织
- **外部数据**如何接入
- **工具**如何被模型安全调用
- **上下文**如何被长期管理

核心价值：**让语言模型变得有用**，针对 LLM 的典型限制：知识时效性、领域专精性、可操作性（计算/查库/调 API）、多轮对话连贯性。通过标准化链（Chains）与组件（Components）像搭积木一样构建 AI 应用。

### 模块总览

| 模块 | 作用 |
|------|------|
| **LLMs / ChatModels** | 模型接口 |
| **Prompt Templates** | Prompt 结构化 |
| **Chains** | 流程编排 |
| **Memory** | 上下文管理 |
| **Retrievers / VectorStores** | 知识检索 |
| **Agents & Tools** | 自动决策与执行 |

### 环境与安装

- **安装**：`pip install langchain langchain-openai langchain-community python-dotenv`；国内可用 `-i https://mirrors.aliyun.com/pypi/simple/`。
- **第三方模型（如 DeepSeek）**：底层通过 **LiteLLM**，需 `pip install -U litellm`；`ChatOpenAI` 配置 `openai_api_base="https://api.deepseek.com"`、`openai_api_key`、`model="deepseek-chat"`。
- **密钥**：建议用 `.env` + `load_dotenv()`，变量如 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`。

### LCEL 链（推荐写法）

- **重要**：`LLMChain` 已弃用，推荐使用 **LCEL**（管道符 `|`）组织流程，支持异步与流式。
- **标准流程**：`输入字典 → 填充 Prompt → 发给 LLM → OutputParser`；代码形式：`chain = prompt | llm | StrOutputParser()`，调用 `chain.invoke({"question": "..."})`。
- **流式输出**：用 `chain.stream(...)` 替代 `invoke`，逐 chunk 输出，适合聊天界面。

### 核心组件要点

- **Models**：推荐 **Chat Models**，输入输出为结构化消息（`SystemMessage`、`HumanMessage`、`AIMessage`）。
- **Prompts**：推荐 `ChatPromptTemplate.from_messages([("system", "..."), ("user", "{x}")])`，变量由 `invoke` 传入。
- **OutputParser**：模型输出为 `Message`，`StrOutputParser()` 做显式类型转换，便于工程可控。
- **检索 (RAG)**：流程为 DocumentLoaders → TextSplitter → Embeddings → VectorStore；`vectorstore.as_retriever()` 可在链中作为 `context` 来源。
- **记忆 (Memory)**：传统 `ConversationBufferMemory` 在 LCEL 链中较难集成；推荐 **`ChatMessageHistory` + `RunnableWithMessageHistory`**，通过 `session_id` 区分用户，支持 Redis/PostgreSQL 等持久化。
- **代理 (Agents)**：基础代理可用 `create_tool_calling_agent` + `AgentExecutor`；工具用 `@tool` 装饰器定义；复杂代理推荐 **LangGraph**。

### 快速开始示例

- **基础问答链**：`prompt | llm | StrOutputParser()`，`.env` 中配置模型与 API，`chain.invoke({"question": "..."})`。
- **带记忆的对话链**：`ChatPromptTemplate` 中加 `MessagesPlaceholder(variable_name="history")`，用 `get_session_history(session_id)` 提供 `ChatMessageHistory`，以 `RunnableWithMessageHistory` 包装链，`invoke(..., config={"configurable": {"session_id": "user_001"}})` 实现多轮记忆。

### 小结（教程侧重点）

- LangChain 不增强模型能力，主要增强**可控性**（结构化 Prompt、链式编排、Parser、记忆、检索、工具）。
- Prompt 视为**结构化输入函数**而非裸字符串；无 Parser 时工程难以控制输出类型。
- 国内落地可优先用 DeepSeek + LiteLLM + `.env`，与官方文档中的 `create_agent` 示例可并存（后者偏新版 Agent API）。

## 参考链接

- [LangChain 官网](https://www.langchain.com/)
- [LangChain 文档 - Overview](https://docs.langchain.com/oss/python/langchain/overview)
- [LangChain 文档 - 安装与 Quickstart](https://docs.langchain.com/oss/python/langchain/install)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [菜鸟教程 - LangChain 制作智能体](https://www.runoob.com/ai-agent/langchain-agent.html)（LCEL、模块总览、环境、记忆、Agent 示例）
- [LangSmith](https://smith.langchain.com/)
