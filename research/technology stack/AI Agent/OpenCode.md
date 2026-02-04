# OpenCode 调研笔记

> 对「Agentic AI for Education」项目的参考：OpenCode 作为开源 AI 编程代理，在 Agent 设计、权限与工具配置、多形态入口（终端/桌面/IDE）等方面具有参考价值。

---

## 1. 概述与定位

**OpenCode** 是开源的 AI 编程代理（AI coding agent），支持在**终端（Terminal）、桌面应用和主流 IDE（如 VS Code）**中与 AI 交互完成代码相关任务。

- **官网**: [https://opencode.ai/](https://opencode.ai/)
- **文档**: [https://opencode.ai/docs](https://opencode.ai/docs)
- **下载**: [https://opencode.ai/download](https://opencode.ai/download)

### 1.1 与同类产品对比

| 对比项     | OpenCode                         | Claude Code / Cursor Agent   |
|------------|----------------------------------|------------------------------|
| 开源       | 是                               | 否 / 部分                   |
| 隐私       | 不存储代码与上下文，隐私优先     | 依赖厂商策略                 |
| 模型       | 75+ 提供商，含免费模型与 Zen 集合 | 绑定单一/少数厂商            |
| 形态       | 终端 TUI、桌面 App、IDE 扩展     | 多为 IDE/Web                 |

**核心价值**：理解代码库、编写新功能、重构、修 Bug，并可通过 **Build / Plan 双模式** 与 **主 Agent + 子 Agent** 控制「只读规划」与「可执行编辑」的边界，适合做教育场景下的可控 Agent 设计参考。

### 1.2 名称与仓库说明

- **当前产品**：品牌名为 **OpenCode**，由 [Anomaly](https://anoma.ly/) 运营，安装脚本与文档以 `opencode.ai` 为准。
- **历史仓库**：GitHub 上的 [opencode-ai/opencode](https://github.com/opencode-ai/opencode) 已被归档，项目延续为 [Crush](https://github.com/charmbracelet/crush)（原作者与 Charm 团队）。若查阅「Go 版 TUI、MCP、LSP」等实现细节，可同时参考 Crush 与官方文档。

---

## 2. 关键特性（对项目的参考点）

- **LSP 集成**：自动为 LLM 加载合适的语言服务，提升代码理解与补全质量。
- **多会话**：同一项目可并行开多个 Agent 会话，便于「多角色/多任务」教学或协作演示。
- **分享链接**：会话可生成链接，便于答疑、评审、协作（与教育场景中的「提交作业/展示过程」契合）。
- **双模式 Agent**：**Build**（全权限执行）与 **Plan**（默认只读、需确认），便于讲解「规划与执行分离」。
- **主 Agent + 子 Agent**：主 Agent 可调用专用子 Agent（如 General、Explore），对应「任务分解与角色分工」。
- **多模型**：支持 75+ 提供商，内置免费模型（如 GLM-4.7、MiniMax M2.1），可接 OpenAI、Anthropic、Google、本地模型等，便于教学环境按成本与合规选型。
- **隐私**：不存储代码与上下文，适合校内/敏感环境。

---

## 3. Agent 体系（与教育/多角色设计高度相关）

来源：[Agents | OpenCode](https://opencode.ai/docs/agents/)

### 3.1 类型

- **Primary Agent（主 Agent）**：用户直接对话的对象，用 **Tab** 或配置的 `switch_agent` 切换。负责主对话与任务编排。
- **Subagent（子 Agent）**：被主 Agent 或用户通过 **@提及** 调用，用于专项任务（如代码审查、探索代码库）。

### 3.2 内置 Agent

| Agent   | 模式    | 说明 |
|---------|---------|------|
| **Build**  | primary | 默认主 Agent，**全部工具开启**，可编辑文件、执行命令。 |
| **Plan**   | primary | **受限**：文件编辑、bash 默认均为 `ask`，只做分析与规划，不直接改代码。 |
| **General**| subagent| 通用研究、多步任务，除 todo 外工具齐全，可做文件修改。 |
| **Explore**| subagent| **只读**，快速浏览代码库、按模式找文件、关键词搜索。 |

对教育项目的启示：

- 用 **Plan** 做「先规划再实现」的教学流程。
- 用 **Explore** 做「代码阅读/理解」练习，避免学生误操作。
- 自定义 subagent（如「代码审查员」「文档撰写员」）可对应不同学习角色。

### 3.3 使用方式

1. **主 Agent**：会话中按 **Tab** 在 Build / Plan 等之间切换。
2. **子 Agent**：在输入中 **@子 Agent 名**，例如：`@general 帮我查一下这个函数的用法`。
3. **子会话导航**：子 Agent 可创建子会话，用 `<Leader>+Left/Right`（或配置的 `session_child_cycle`）在主会话与子会话间切换。

### 3.4 配置方式

支持两种：

- **JSON**：在 `opencode.json` 的 `agent` 下配置。
- **Markdown**：在 `~/.config/opencode/agents/`（全局）或 `.opencode/agents/`（项目）下，一个 `.md` 文件对应一个 Agent，文件名即 Agent 名。

**JSON 示例**（节选）：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "{file:./prompts/build.txt}",
      "tools": { "write": true, "edit": true, "bash": true }
    },
    "plan": {
      "mode": "primary",
      "model": "anthropic/claude-haiku-4-20250514",
      "tools": { "write": false, "edit": false, "bash": false }
    },
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "mode": "subagent",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "tools": { "write": false, "edit": false }
    }
  }
}
```

**Markdown 示例**（文件名如 `review.md` → Agent 名 `review`）：

```markdown
---
description: Reviews code for quality and best practices
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
tools:
  write: false
  edit: false
  bash: false
---
You are in code review mode. Focus on:
- Code quality and best practices
- Potential bugs and edge cases
- Performance implications
- Security considerations
Provide constructive feedback without making direct changes.
```

### 3.5 常用配置项

| 选项 | 说明 |
|------|------|
| **description** | 简短描述，**必填**，用于子 Agent 的 @ 列表与任务分配。 |
| **mode** | `primary` / `subagent` / `all`。 |
| **model** | 该 Agent 使用的模型（如 `provider/model-id`）。 |
| **temperature** | 创造性/随机性，规划类建议偏低（如 0.1），创意类可 0.7–0.8。 |
| **prompt** | 系统提示，可用 `{file:./path/to.txt}` 引用文件。 |
| **tools** | 各工具开关（write, edit, bash, webfetch 等），可 `true`/`false`。 |
| **permission** | 对 edit、bash、webfetch 等设置 `ask` / `allow` / `deny`，可按命令粒度（如 bash 下 `git push: ask`）配置。 |
| **steps** | 最大 Agent 步数，用于控制成本与回合数。 |
| **hidden** | 子 Agent 是否从 @ 自动补全中隐藏（仅被 Task 工具调用）。 |
| **permission.task** | 控制该 Agent 能通过 Task 工具调用哪些子 Agent（glob 匹配）。 |

教育场景可重点用：**description**（角色说明）、**tools**（限制写盘/执行）、**permission**（敏感操作一律 ask）。

---

## 4. 工具（Tools）与权限

OpenCode 的 Agent 通过一组**工具**操作代码库与系统，权限在配置中设为 **allow / deny / ask**。

| 工具 | 说明 | 典型教育用途 |
|------|------|--------------|
| **bash** | 执行 shell 命令 | 运行测试、构建；可对 `git push` 等设为 ask。 |
| **write / edit / patch** | 写文件、编辑、打补丁 | Build 可用；Plan 或「只读练习」可关闭。 |
| **read** | 读文件（可带行范围） | 所有角色都可给。 |
| **grep / glob / list** | 搜索内容、按模式列文件 | 代码阅读、检索。 |
| **webfetch** | 抓取网页 | 查文档、教程。 |
| **question** | 向用户提问确认 | 关键步骤二次确认。 |
| **todo** | 任务清单 | 拆解任务、进度可见。 |
| **LSP**（实验） | 诊断、跳转等 | 理解项目、定位错误。 |
| **MCP** | 外部协议扩展 | 数据库、API、自定义教具。 |

**权限示例**（按 Agent 覆盖）：

```json
"agent": {
  "plan": {
    "permission": {
      "edit": "ask",
      "bash": "ask"
    }
  }
}
```

子 Agent 若仅做代码审查，可 `edit: deny`、`bash: deny`，只保留 read、grep、glob 等。

---

## 5. 安装与启动（便于实验与演示）

### 5.1 一键安装

```bash
curl -fsSL https://opencode.ai/install | bash
```

安装后可用 `opencode --version` 验证。

### 5.2 包管理器

- **macOS / Linux**：`brew install opencode` 或 `npm install -g opencode-ai`
- **Windows**：`choco install opencode` 或 `scoop bucket add extras && scoop install extras/opencode`
- **Arch**：`paru -S opencode-bin`

### 5.3 桌面应用

从 [opencode.ai/download](https://opencode.ai/download) 或 [GitHub Releases](https://github.com/anomalyco/opencode/releases) 下载对应平台安装包（macOS aarch64/x64、Windows x64、Linux .deb/.rpm/AppImage）。

### 5.4 首次使用

1. 终端执行：`opencode`。
2. 按引导选模型（可选标注 Free 的免费模型，如 MiniMax M2.1、GLM-4.7）。
3. 可选 `/connect` 或 `opencode auth login` 配置 API Key 或 Zen。
4. 在项目目录下执行 `/init` 会生成 `.opencode/` 与 **AGENTS.md**（项目结构摘要），便于 Agent 理解项目。

---

## 6. TUI 常用 Slash 命令（教学/演示用）

| 命令 | 描述 |
|------|------|
| `/init` | 创建/更新项目 AGENTS.md，分析代码库。 |
| `/connect` | 添加/配置 LLM 与 API Key。 |
| `/models` | 列出并切换可用模型。 |
| `/new` | 新会话。 |
| `/sessions` | 列出并切换会话。 |
| `/share` | 生成当前会话分享链接。 |
| `/undo` / `/redo` | 撤销/重做（需 Git 仓库）。 |
| `/compact` | 压缩/总结当前会话，节省上下文。 |
| `/exit` | 退出。 |

更多见官方 TUI 文档：[https://opencode.ai/docs/tui](https://opencode.ai/docs/tui)。

---

## 7. CLI 非交互模式（脚本/自动化）

适合做批处理、CI 或「单次问答」演示：

```bash
opencode -p "解释这段代码的作用"
opencode -p "修复 login 函数中的 bug" -f json
opencode -p "生成 README" -q
```

- `-p`：单次提示，输出后退出。  
- `-f`：输出格式（text / json）。  
- `-q`：静默，不显示 spinner。  
- `-c`：指定工作目录。  
- `-d`：调试模式。

---

## 8. 扩展：oh-my-opencode（多 Agent 协作增强）

[oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) 在 OpenCode 上增加多智能体协作层，可作为「多角色协作」的进阶参考：

- **Sisyphus** 主智能体：持续执行复杂任务直到完成。
- 子智能体：Oracle、Librarian、Frontend Engineer、Explore 等，分工明确。
- 关键词触发（如 `ultrawork` / `ulw`）：进入「全自动」多 Agent 流程。
- 多模型调度：不同任务分配给不同模型（如规划用 Claude、前端用 Gemini）。
- 钩子与 MCP：事件驱动、扩展工具。

安装方式：在 OpenCode 对话中粘贴其安装说明链接，按提示完成即可。对「Agentic AI for Education」而言，可借鉴其**角色划分与任务分配**思路，不必直接依赖该插件。

---

## 9. 与本研究项目的关联小结

| 项目需求 | OpenCode 可借鉴点 |
|----------|-------------------|
| Agentic AI for Education | 双模式（Plan / Build）、主 Agent + 子 Agent、权限与工具细粒度控制。 |
| 可控、可解释 | Plan 只读规划；permission 的 ask/deny；步骤数 steps 限制。 |
| 多角色/多任务 | Primary vs Subagent；自定义 Agent（Markdown/JSON）；@ 与 Task 调用。 |
| 教学/演示友好 | 分享链接、多会话、Slash 命令、CLI 非交互、免费模型与多提供商。 |
| 隐私与部署 | 不存代码与上下文；支持本地/自建模型。 |

以上内容整理自 [opencode.ai](https://opencode.ai/)、[OpenCode Agents 文档](https://opencode.ai/docs/agents/)、[菜鸟教程 - OpenCode 入门](https://www.runoob.com/ai-agent/opencode-coding-agent.html)，以及 GitHub 上的 opencode-ai/opencode（已归档，延续为 Crush）与 oh-my-opencode 仓库。撰写时以官方文档与 runoob 教程为准，便于后续做方案对比与选型。
