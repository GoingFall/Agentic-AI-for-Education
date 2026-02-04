# OpenClaw 调研

> 与项目「Agentic AI for Science & Engineering Education」相关：OpenClaw 是当前最受关注的**自主个人 AI 助手**开源项目之一，可作为教育场景下「能真正执行任务」的 Agent 参考架构——本地运行、持久记忆、多通道交互、Skill 扩展、MCP 生态。

## 定义与定位

**OpenClaw** 是一款**开源、自主的个人 AI 助手**，在用户设备上本地运行，通过消息应用（WhatsApp、Telegram、Discord、Signal、iMessage 等）接收指令并**代为执行任务**，而非仅做对话。

- **曾用名**：ClawdBot → Moltbot → OpenClaw（因 Anthropic 商标等原因更名，见下「名称演进」）
- **开发者**：Peter Steinberger（PSPDFKit 创始人）
- **首次发布**：2025 年 11 月；2026 年 1 月因更名与社区传播而受关注
- **许可**：MIT
- **官网**：[openclaw.ai](https://openclaw.ai/) | **仓库**：[github.com/openclaw/openclaw](https://github.com/openclaw/openclaw) | **技能合集**：[awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)

### 名称演进（菜鸟教程）

Clawbot、Moltbot 与 OpenClaw 为同一开源项目，演进顺序：**Clawdbot → Moltbot → OpenClaw**。2026 年 1 月 27 日 Anthropic 发律师函称 Clawd/Clawdbot 与 Claude 太像，项目当日更名为 Moltbot（脱皮龙虾，吉祥物小龙虾 Molty）；OpenClaw 为当前官方最终名称，旧命令 `clawdbot` 仍兼容。

| 名称 | 时间线 | 背景/原因 | 本质关系 |
|------|--------|-----------|----------|
| **Clawdbot / Clawbot** | 2025 年末至 2026 年 1 月初 | 最初项目名；灵感来自 Claude + claw（龙虾爪） | 原始名称 |
| **Moltbot** | 2026 年 1 月 27 日 | Anthropic 商标顾虑被要求更名 | 过渡名；功能与 Clawdbot 一致 |
| **OpenClaw** | 2026 年 1 月 30 日之后 | 避免版权冲突、强调开源性/长线品牌 | 当前官方名称 |

## 核心特点

| 维度 | 说明 |
|------|------|
| **本地/自托管** | 运行在 Mac、Windows、Linux 或自建服务器，数据默认留在本机，隐私可控。 |
| **模型无关** | 支持 Anthropic、OpenAI、本地模型等，自带 API Key 即可。 |
| **持久记忆** | 以本地 Markdown 等形式存储偏好与上下文，跨会话保持。 |
| **多通道交互** | 通过 WhatsApp、Telegram、Discord、Slack、Signal、iMessage 等收发指令与结果。 |
| **系统与浏览器** | 可读写文件、执行 Shell、控制浏览器（填表、抓取等），支持沙箱或全权限。 |
| **Skill 与插件** | 100+ 预置 AgentSkill，可扩展；Agent 可自主编写新 Skill。 |
| **MCP** | 通过 Model Context Protocol 对接 100+ 第三方服务与工具。 |

## 能做什么（典型能力）

- **收件箱/邮件**：清空收件箱、发邮件、退订等。
- **日历与行程**：管理日历、值机、提醒出发时间（结合交通）。
- **开发与运维**：运行测试、接 Sentry 等 webhook 自动修 bug、开 PR；管理 Codex/Claude Code 会话。
- **自动化**：定时任务、提醒、后台任务；从 Obsidian、Notion 等读写。
- **浏览器**：浏览网页、填表、提取数据。
- **智能家居与健康**：Philips Hue、WHOOP 等；按目标控制设备或汇总健康数据。
- **教育相关用例**：用户反馈包括「让 Agent 访问课程/作业并自己写 Skill」「用 OpenClaw 支持学生学 vibe coding」等——说明其「任务执行 + Skill 自扩展」模式适合做教育 Agent 底座。

## 技术架构要点

- **本地网关（Gateway）**：连接 AI 模型与本地工具/文件/浏览器，可沙箱或全权限。
- **持久化**：配置与交互历史存于本地，便于长期个性化与手动调参。
- **Lobster 工作流 Shell**：底层基于 Lobster 工作流能力，支撑自动化与编排。
- **Heartbeat**：支持主动「心跳」式联系用户，而非仅被动响应。

## 安全与隐私

- **权限大**：需访问邮件、日历、消息、文件等，配置不当或暴露会带来风险。
- **已知风险**：提示注入、管理界面暴露、凭据存于本地配置等；安全研究建议仅在**隔离沙箱**中运行，避免接生产系统或高敏感账号。
- **适用对象**：更适合**理解自主 Agent 与高权限风险**的进阶用户；企业场景需严格管控部署与权限。

## 生态与周边

- **Moltbook**：面向 AI Agent 的社交网络（2026 年 1 月）。
- **Molthub / ClawdHub**：AgentSkill 目录与分享，可搜索、安装、贡献自定义 Skill；社区已有 **500+** 技能（Slack、Discord、GitHub、浏览器控制、macOS UI 自动化等）。
- **1-Click 部署**：如 DigitalOcean 等提供加固镜像的一键部署（约 $7–24/月），便于快速体验或小团队使用。

## 实战与教程要点（菜鸟教程）

> 来源：[菜鸟教程 - OpenClaw (Clawdbot) 教程](https://www.runoob.com/ai-agent/openclaw-clawdbot-tutorial.html)

### 定位一句话

OpenClaw 是可**执行任务**的智能体：给指令后不仅回答，还能主动操作系统、访问网页、处理邮件、整理文件、发起提醒甚至自动编写代码；目标是让 AI **直接完成完整工程任务**，而不只是给建议。本地算力 + 大模型 Agent 自动化，偏开发者效率工具。

### 系统要求与安装

- **硬件**：极低，2GB RAM 即可；支持 Mac、Windows、Linux；需 **Node.js ≥22** 或 Docker。
- **一键安装**：
  - macOS/Linux：`curl -fsSL https://openclaw.ai/install.sh | bash`
  - Windows PowerShell：`iwr -useb https://openclaw.ai/install.ps1 | iex`
  - Windows CMD：`curl -fsSL https://openclaw.ai/install.cmd -o install.cmd && install.cmd && del install.cmd`
- **手动安装**：`npm i -g openclaw` 或 `pnpm add -g openclaw`，然后 `openclaw onboard`（会安装 launchd/systemd 等后台服务）。
- **从源码**：`git clone` → `pnpm install` → `pnpm ui:build`、`pnpm build` → `pnpm openclaw onboard --install-daemon`；开发模式用 `pnpm gateway:watch`。

### 配置与首次使用

- 一键脚本会做环境检测、依赖安装并启动 **onboarding**；选择 QuickStart 后配置 **Model/Auth Provider**（国内外供应商均支持，如 Qwen、MiniMax、智谱等）。
- **Gateway Port** 默认 **18789**；可勾选 Skills、包管理器（npm 等）；最后可开启内容引导日志与会话记录。
- 安装完成后自动打开 **http://127.0.0.1:18789/chat** 进入聊天界面。

### 常用命令速查

| 命令 | 作用 |
|------|------|
| `openclaw status` | 查看 Gateway 状态 |
| `openclaw health` | 健康检查（core、依赖） |
| `openclaw doctor` | 综合诊断与修复建议（可 `--yes` 自动执行） |
| `openclaw configure` | 交互式配置向导（模型、通道、凭据） |
| `openclaw config get/set/unset <path>` | 读取/设置/清除配置项 |
| `openclaw channels list/login` | 列出或登录通道（WhatsApp、Telegram 等） |
| `openclaw skills list` / `openclaw skills info <skill>` | 列出技能 / 查看技能详情 |
| `openclaw plugins list/install/enable` | 插件列表、安装、启用 |
| `openclaw logs --follow` | 查看日志（可 `--json` / `--plain` / `--limit`） |
| `openclaw gateway start/stop/restart/install` | 启动/停止/重启/安装系统服务 |
| `openclaw uninstall` | 卸载（可 `--all --yes`、`--state`、`--workspace`、`--service`、`--dry-run`） |

### 第三方云一键部署

- **阿里云**：[轻量级服务器 / 活动页](https://www.aliyun.com/activity/ecs/clawdbot) 提供镜像一键安装。
- **腾讯云**：[开发者文档](https://cloud.tencent.com/developer/article/2624973) 提供轻量服务器安装说明。

### 为何受关注（教程归纳）

- 真正「像 JARVIS」：读写文件、跑终端、操作浏览器、邮件、日历、写代码、订机票、清空收件箱等。
- **本地优先 + 长期记忆**：对话跨平台共享上下文，`USER.md` 与 `memory/` 目录越用越聪明。
- **多模型**：Claude、Gemini、OpenAI、Ollama、Pi 等几乎都支持。
- **技能生态**：ClawdHub 上 500+ 社区技能，安装简单（类似 npm install），能力却很强（开发者称 "spicy"）。

### 核心能力（执行层面）

- 将自然语言目标**拆解为可执行步骤**
- 自动调用**终端命令**
- **创建与修改**项目文件
- **运行代码**并检测结果
- 根据**报错自动修复**

### 与 Claude Code / OpenCode 对比

| 能力维度 | OpenClaw | Claude Code | OpenCode |
|----------|----------|-------------|----------|
| 任务规划 | 强 | 中 | 中 |
| 自动执行 | 完整 | 部分 | 部分 |
| 自我修复 | 有 | 无 | 无 |
| 工程级操作 | 强 | 强 | 中 |
| 本地自动化 | 原生支持 | 较弱 | 较弱 |

Claude Code / OpenCode 强在代码质量与理解；OpenClaw 强在**自动完成整个工程流程**，更接近具备执行权限的工程型智能体。

---

## 段小草笔记摘录：OpenClaw 工作原理分析

> 来源：`research/technology stack/temp.md`（段小草 · Clawdbot 工作原理分析，原文 *everyone talks about Clawdbot, but here's how it works*）。以下为架构与实现上有参考价值的内容摘录。

### 技术本质与运行机制

- **本质**：OpenClaw（Clawd）是一个 **TypeScript CLI 应用**，不是 Python、Next.js 或 Web 应用。
- **运行机制**：
  - 在本地运行并开放**网关服务器**，处理所有**渠道连接**（Telegram、WhatsApp、Slack 等）；
  - 调用 **LLM API**（Anthropic、OpenAI、本地模型等）；
  - **在本地执行工具**，在用户电脑上执行操作。

了解底层原理有助于判断**擅长与不擅长**的场景，便于选型与设计教育 Agent。

### 消息到输出的架构流程

从用户在消息应用里发送提示，到得到输出的全过程可简化为：

| 阶段 | 组件 | 作用 |
|------|------|------|
| 1 | **渠道适配器** | 接收消息并处理（规范化、提取附件）；不同消息应用有专用适配器。 |
| 2 | **网关服务器** | 任务/会话的**协调器**，把消息交给对应会话；使用**基于通道的命令队列**：一个会话一个通道，串行化默认，低风险任务可并行（如 cron）。与「到处 async/await」相比，**Lane 抽象**把串行化作为默认架构，心智模型从「我要锁什么？」变为「什么可以安全并行？」。 |
| 3 | **AI 智能体运行器** | 选模型、API Key（无效则标记冷却并尝试下一个）、主模型失败时回退；用**工具、技能、内存**动态组装系统提示词，并加入会话历史（来自 **.jsonl**）；经**上下文窗口守卫**：快满时压缩会话（总结）或优雅失败。 |
| 4 | **LLM API 调用** | 流式返回，多提供商抽象；若模型支持可请求**扩展思考**。 |
| 5 | **智能体循环 (Agentic Loop)** | 若 LLM 返回工具调用，Clawd **在本地执行**并将结果加入对话；重复直到返回最终文本或达到**最大轮次**（默认约 20 轮）。 |
| 6 | **响应路径** | 经渠道返回用户；会话以 **jsonl** 持久化（每行一条消息/工具调用/结果等）。 |

要点：**默认串行、按需并行**，避免多 Agent 交错日志与竞争条件；与「Don’t Build Multi-Agents」类观点一致——先保证单会话可靠，再考虑并行。

### 记忆系统

- **会话记录**：以 **JSONL** 格式存储，每行一个 JSON 对象（用户消息、工具调用、结果、响应等）。
- **长期记忆**：以 **Markdown** 存在 **MEMORY[.]md** 或 **memory/** 目录；Agent 用标准**写文件**工具写入 `memory/*.md`，无专用内存 API。
- **检索**：**向量搜索 + 关键词匹配**混合（向量用 SQLite，关键词用 FTS5）；嵌入提供商可配置。例如搜「authentication bug」既能命中「auth issues」（语义）也能命中完全匹配短语。
- **同步**：**智能同步**：文件监视器检测到变更时触发同步。
- **新对话**：一个 **hook** 会把上一轮对话写成 Markdown 摘要写入记忆。
- **特点**：无内存合并、无月度/周度压缩；**旧记忆与新记忆权重基本相等**（无遗忘曲线）；与 CamelAI 等工作流内存实现类似，**简单可解释**，便于调试与教育场景复现。

### 如何使用计算机（工具层）

- **exec**：在以下环境运行 shell 命令——**沙盒（Docker，默认）** / **宿主机** / **远程设备**。
- **文件系统**：读、写、编辑。
- **浏览器**：基于 **Playwright**，配合**语义快照**（见下）。
- **进程管理**：后台长期命令、终止进程等。

理念：**在用户允许的范围内，给予尽可能多的自主权**；与 Claude Code 类似，有命令白名单与「允许一次 / 始终允许 / 拒绝」的审批流程。

### 安全：命令审批

- 用户可对命令**批准一次、始终允许、拒绝**；配置示例位于 `~/.clawdbot/exec-approvals.json`（按 agent、allowlist 等配置）。
- **安全命令**（如 jq, grep, cut, sort, uniq, head, tail, tr, wc）可预批准。
- **危险 shell 结构**默认拒绝，例如：命令替换 `$(...)`、重定向 `>`、链式 `||`、子 shell `(sudo rm -rf /)` 等。

教育场景下应对**可执行命令范围**做更严格限制（如仅允许指定目录、禁止网络等）。

### 浏览器：语义快照

- 浏览器工具**主要不用截图**，而用**语义快照**——页面**可访问性树（ARIA）的文本表示**，例如：
  - `button "Sign In" [ref=1]`
  - `textbox "Email" [ref=2]`
  - `heading "Welcome back"`
- **优势**：浏览行为不必依赖视觉；语义快照体积小（约 50 KB vs 截图数 MB），**Token 成本低**，且便于可访问性与自动化测试。

对教育项目：若需「自动填表、交作业页面」等，语义快照 + Playwright 是轻量且可复用的方案。

### 动态系统提示词

- 系统提示词**非静态**，而是根据**技能、内存回忆、用户身份、时区**等**动态组装**。
- 基础模板包含：身份（如在 Moltbot 中运行的个人助理）、**工具列表**（按策略过滤，仅列出该 Agent 可用工具）、工具调用风格（低风险直接调用、多步骤/敏感时再描述）、工作区路径、Runtime 信息（agent、host、os、model、channel、thinking 等）。

便于做**多技能、多场景**的 Agent：同一套运行时，通过「可用工具 + 记忆 + 身份」切换行为。

### 子智能体

- **主 Agent 可生成子智能体**（子智能体不可再生成）；子智能体拥有**单独会话**。
- 父子通过 **session_send** 通信，子智能体结果**流回**父智能体；父可**轮询**子会话进度。

可与「Skill + 专用子任务」结合：例如教育 Agent 把「批改作业」委托给子智能体，主 Agent 只做编排与汇总。

### 上下文压缩

- 当**接近上下文限制**时：Agent 将事实**写入记忆**；历史被**分块**，由 LLM 对各块**总结**，再**组合成连贯摘要**替换旧消息，从而腾出空间继续对话。

对长对话、多轮教学辅导场景，这种「分块摘要 + 记忆落盘」模式可直接借鉴。

### 小结（与 CamelAI / Eigent 等对比）

- OpenClaw 的许多设计（串行队列、记忆格式、工具审批、语义快照、动态提示词、上下文压缩）与 **CamelAI**、**Eigent** 等开源智能体**相当类似**，说明在 AI 智能体层面**常见模式已趋同**，差异多在工程细节与生态。教育项目可把这些模式当作**通用参考**，再按合规与权限做裁剪。

---

## 与项目关联（Agentic AI for Education）

- **参考架构**：教育 Agent 可借鉴「本地网关 + 多通道 + 持久记忆 + Skill/MCP」的思路，做**可执行任务**的助学助手（查课表、提醒作业、推荐练习、操作 LMS 等）。
- **Skill 与教育**：可为教育场景设计专用 Skill（如课程查询、作业提醒、实验指导），或让 Agent 根据对话自行创建/调用教育类 Skill。
- **MCP**：与现有 [MCP](research/MCP.md)、[Skill](research/skill.md) 调研一致，可作为「连接数据与工具」的标准方式，用于对接 LMS、题库、日历等。
- **注意**：教育场景需**严格限制权限与数据范围**（仅教学相关系统、脱敏数据），并做好审计与合规，不宜直接照搬「全权限个人助手」配置。

## 参考链接

- [OpenClaw 官网](https://openclaw.ai/)
- [菜鸟教程 - OpenClaw (Clawdbot) 教程](https://www.runoob.com/ai-agent/openclaw-clawdbot-tutorial.html)（名称演进、安装、配置、常用命令、云部署、与 Claude Code 对比）
- [OpenClaw - Wikipedia](https://en.wikipedia.org/wiki/OpenClaw)
- [What is OpenClaw? - DigitalOcean](https://www.digitalocean.com/resources/articles/what-is-openclaw)
- [It's OpenClaw - 1Password Blog](https://1password.com/blog/its-openclaw)
- [OpenClaw: When AI Agents Get Full System Access – innFactory](https://innfactory.ai/en/blog/openclaw-ai-agent-security/)
- [Personal AI Agents like OpenClaw Are a Security Nightmare - Cisco](https://blogs.cisco.com/ai/personal-ai-agents-like-openclaw-are-a-security-nightmare)
- [IBM Think - OpenClaw](https://www.ibm.com/think/news/clawdbot-ai-agent-testing-limits-vertical-integration)
- 段小草 · [Clawdbot 工作原理分析](temp.md)（本仓库 `research/technology stack/temp.md`）
