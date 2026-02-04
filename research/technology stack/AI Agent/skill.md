# Agent Skill 调研

> 与项目「Agentic AI for Science & Engineering Education」相关：用 Skill 封装教育领域的工作流与规范（如出题、批改、实验指导），使 Agent 具备可复用、可版本管理的领域能力。

## 定义

**Agent Skills** 是一种**开放标准**，用于为 AI Agent 扩展**领域化能力**。Skill 将领域知识和工作流打包成可被 Agent 发现和调用的单元。

- **来源**：[Cursor Docs - Agent Skills](https://cursor.com/docs/context/skills)、[agentskills.io](https://agentskills.io/)

特点：

- **可移植**：支持该标准的任意 Agent 均可使用。
- **可版本管理**：以文件形式存放，可进 Git、或通过 GitHub 链接安装。
- **可执行**：可包含脚本/代码，由 Agent 在合适时机执行。
- **按需加载**：按需加载资源，有利于控制上下文与成本。

## Skill 的形态

- 一个 **Skill** 对应一个目录，内含 `SKILL.md`（必选）及可选的 `scripts/`、`references/`、`assets/`。
- `SKILL.md` 使用 YAML frontmatter：`name`、`description` 等，正文描述何时用、如何用、步骤与规范。
- Agent 启动时从约定目录（如 `.cursor/skills/`、`~/.cursor/skills/`）发现 Skill，根据上下文或用户输入（如 `/skill-name`）决定是否调用。

## 与项目关联

- **教育 Agent** 可设计多种 Skill，例如：
  - 「出题/组卷」：按难度、知识点、题型生成或筛选题目。
  - 「批改与反馈」：按评分标准生成评语与改进建议。
  - 「实验指导」：按步骤检查操作、安全规范、结果解读。
- Skill 与 **MCP** 配合：Skill 定义「做什么、按什么流程」，MCP 提供「连什么数据、调什么接口」。
- 适合一周内落地：先做 1～2 个核心 Skill（如答疑 + 练习推荐），再迭代扩展。

---

## 菜鸟教程补充：Skills 机制与 Claude Code 实践

> 来源：[Skills 教程 | 菜鸟教程](https://www.runoob.com/ai-agent/skills-agent.html)

### Skills 与普通 Prompt 的区别

Skills 本质是**教 AI 按固定流程做事的操作说明书**，写好后可像函数一样反复调用；把「某类事情应该怎么专业做」封装成**可复用、可自动触发**的能力模块。

| 对比项       | 普通 Prompt       | Skills 机制                 |
| ----------- | ----------------- | --------------------------- |
| 每次都要重新描述 | 是                | 否（只描述一次）             |
| 上下文长度占用  | 每次全量塞入      | 渐进式加载（触发时才读完整） |
| 一致性       | 依赖每次 prompt 质量 | 高（固定 SOP + 模板）        |
| 复用性       | 手动复制粘贴      | 自动匹配 / slash 命令 / 项目共享 |
| 维护方式      | 改一次 prompt 就要重新发 | 修改 SKILL.md，全局/项目生效   |

**比喻**：把 AI 当成刚毕业的聪明但没经验的实习生——

- **普通 Prompt** = 每次从头教他怎么做事（今天教一遍，明天还得重新教）
- **Rule / 记忆** = 工位上贴「公司行为守则」（一直生效，但只管态度和格式）
- **MCP / Tools** = 给他装一堆软件和 API（能调外部工具，但不知道何时用、怎么组合）
- **Skills** = 给一整套**岗位培训大礼包**（SOP + 流程图 + 话术模板 + 脚本），告诉他：「做这类事时按这个文件夹里的方法来做」

### 支持 Skills 的客户端（节选）

| 工具           | 是否免费使用 Skills | 技能存放默认路径     | 备注           |
| -------------- | ------------------- | -------------------- | -------------- |
| Claude Code   | 是（官方）          | `~/.claude/skills`   | 标准制定者，生态最全 |
| Cursor        | 是                  | `~/.cursor/skills`   | 几乎无缝兼容 Claude Skills |
| OpenCode      | 是                  | 看工具设置           | 国内用户较多   |
| VS Code + 插件 | 部分支持            | 插件设置里配置       | 正在快速跟进   |

### SKILL.md 基本模板与字段

一个 Skill 即一个**以 SKILL.md 为核心的目录**（文件名固定为 `SKILL.md`），内容大致由 **YAML frontmatter + 正文** 组成：

```markdown
---
name: your-skill-name
description: What it does and when Claude should use it
---

# Skill Title

## Instructions
Clear, concrete, actionable rules.

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

| 字段             | 必需 | 作用                 |
| ---------------- | ---- | -------------------- |
| name             | 是   | 唯一标识，小写+连字符；常对应 /slash 命令名 |
| description      | 是   | **触发条件（最重要）**，Agent 靠它判断是否加载 |
| allowed-tools    | 否   | 限制该 Skill 可用工具 |
| model            | 否   | 指定模型             |
| context          | 否   | 如 fork = 独立上下文  |
| agent            | 否   | fork 时使用的子代理   |
| hooks            | 否   | Skill 生命周期钩子    |
| user-invocable   | 否   | 是否显示在 / 菜单     |
| trigger_keywords | 推荐 | 关键词列表，**大幅提升自动触发率** |

### Claude Code 的 Skill 查找顺序

Claude Code 按以下顺序查找并加载 Skill（**越具体的位置优先级越高**）：

| 级别   | 路径                                   | 生效范围     |
| ------ | -------------------------------------- | ------------ |
| 企业级 | 管理控制台配置（managed settings）     | 组织内所有用户 |
| 个人级 | `~/.claude/skills/<skill-name>/SKILL.md` | 所有项目     |
| 项目级 | `.claude/skills/<skill-name>/SKILL.md`  | 仅当前项目   |
| 插件级 | `<plugin>/skills/<skill-name>/SKILL.md` | 启用该插件的环境 |

每个 Skill 对应一个**文件夹**，文件夹名即技能标识（推荐 kebab-case 小写+连字符）。**最简结构**：该文件夹下仅需一个 `SKILL.md`（必须全大写 `SKILL` + 小写 `.md`）。

### 完整示例：代码注释专家 Skill

```markdown
---
name: code-comment-expert
description: >-
  为代码添加专业、清晰的中英双语注释。
  适合缺少文档、可读性差、需要分享审查的代码。
  常见触发场景：加注释、注释一下、加文档、explain this、improve readability

trigger_keywords:
  - 加注释
  - 注释
  - 加文档
  - explain code
  - document
  - comment this
  - readability

version: 1.0
---
# 这里开始是正文——Claude 真正执行时的指令

你现在是「专业代码注释专家」。

## 核心原则
- 只在缺少注释或可读性明显不足处添加
- 优先使用英文 JSDoc / TSDoc 风格
- 复杂逻辑处额外加一行中文解释
- 注释精炼，每行不超过 80 字符
- 绝不修改原有逻辑

## 输出格式（严格遵守）
1. 先输出完整修改后的代码块（用 ```语言 包裹）
2. 再用 diff 形式展示只改动注释的部分
3. 最后说明加了哪些注释、理由

现在直接开始处理用户提供的代码，不要闲聊。
```

### 进阶文件结构（Skill 变复杂时）

当 Skill 超过约 500–800 行或需要模板/脚本/参考资料时，可这样组织：

```
~/.claude/skills/react-component-review/
├── SKILL.md              # 核心指令 + 元数据（建议控制在 400 行内）
├── templates/            # 常用模板（Agent 按需读取）
│   ├── functional.tsx.md
│   └── class-component.md
├── examples/              # 优秀/反例（给 Agent 看标准）
│   ├── good.md
│   └── anti-pattern.md
├── references/            # 规范、规则、禁用词表
│   ├── hooks-rules.md
│   └── naming-convention.md
└── scripts/               # 可执行脚本（需开启 code execution）
    ├── validate-props.py
    └── check-cycle-deps.sh
```

在 `SKILL.md` 中通过**路径引用**让 Agent 按需加载，例如：

- 「需要标准函数组件时，参考 `templates/functional.tsx.md`。」
- 「若违反 Hooks 规则，对照 `references/hooks-rules.md` 第 3–5 条。」
- 「校验 propTypes 可执行 `scripts/validate-props.py "{代码片段}"`。」

这样避免一次性把全部内容塞进上下文，**节省 token**。

### 项目级示例：Python 命名规范 Skill

项目目录下可放 `.claude/skills/python-naming-standard/SKILL.md`：

```markdown
---
name: Python 内部命名规范技能
description: 当用户要求重构、审查或编写 Python 代码时，请参考此规范。
---

## 指令
1. 所有的内部辅助函数必须以 `_internal_` 前缀命名。
2. 如果发现不符合此规则的代码，请自动提出修改建议。
3. 在执行 `claude commit` 前，必须检查此规范。

## 参考示例
- 正确：`def _internal_calculate_risk():`
- 错误：`def _calculate_risk():`
```

字段要求：**name** 小写字母、数字、连字符（最多 64 字符）；**description** 最多 1024 字符。用户说「帮我写一个计算用户折扣的函数」时，Agent 会匹配该 Skill 并按规范生成如 `_internal_get_discount(...)` 的代码。

### 与教育项目的对应关系

- **按需加载 + 渐进式披露**：教学 SOP（如出题流程、批改标准）写成 Skill，只在相关任务时加载，控制上下文与成本。
- **trigger_keywords / description**：用「出题」「组卷」「批改」「实验步骤」等关键词与描述，让教育 Agent 自动选用对应 Skill。
- **templates / examples / references**：把题型模板、标准答案示例、评分细则放在子目录，在 SKILL.md 中引用，便于迭代与版本管理。
- **项目级 vs 个人级**：课程/班级专用规范放在项目 `.claude/skills/` 或等价路径，通用能力放在用户目录。

---

## 段小草笔记摘录：Skill 设计哲学与边界

> 来源：`research/technology stack/temp.md`（段小草 · Agent Skill 相关资料、笔记和思考）。以下为有参考性的概念与结论摘录，便于方案设计时对照。

### 行业背景：谁在定义 Agent 标准

- Agent 领域当前通行的事实标准（Tool Use、Coding Agent、MCP、Skill 等）多出自 **Anthropic**；OpenAI 虽有 Agents.md 等，整体上在 Coding Agent / MCP / Skill 上相对滞后。
- Anthropic 的路线可以概括为：**相信模型编程能力** → 用 **bash + 文件系统 + 文本指令** 构建上下文工程，让模型通过读/写文件和执行命令完成任务。Claude Code、MCP、Claude.md、Skill 都沿这一方向，且已被广泛模仿。
- 结论：做 Skill 设计时，以 Anthropic 官方文档与示例为锚点，兼容性最好；同时 Skill 与 MCP 已形成事实标准，教育项目可在此基础上做「规范 + 工具」分层。

### 渐进式披露：Skill 与 MCP 的上下文差异

- **MCP 的劣势**：在还没拿到有效结果前，工具描述就可能把 Context 占满。
- **Skill 的改进**：通过**控制本地文件读取**，**只在需要时加载内容**——即「渐进式披露」。
- 具体机制（比喻）：实习生不会一次性背完公司所有手册；而是有很多文件柜和目录，按需一级一级展开。对应到实现：
  1. Agent 先只加载**多个 Skill 的元数据**（每个几百 token）；
  2. 当认为需要某个 Skill 时，再读取该 **SKILL.md**（几千 token）；
  3. Skill 内可继续指引 Agent 读取更深层文件；
  4. 若需执行工具，可运行**本地预置脚本**，脚本在本地环境执行，**运行过程不占模型上下文**，只把结果返回给 Agent。

因此：Skill 的工程价值不仅在于「写清楚说明」，更在于**何时、加载哪些内容**的调度设计。

### Skill vs MCP：定位与共存

| 维度       | Skill                          | MCP                                    |
| ---------- | ------------------------------ | -------------------------------------- |
| 形式       | 文件夹下的**文本文件**，可极简（几句 Prompt）也可很复杂 | C/S 架构，需服务端/客户端，对非程序员有门槛   |
| 本质       | 可复用的 **Prompt + 能力/资源包**；本地、模块化、可发现、**可渐进加载** | 让 Agent 与**外部数据/应用/服务**通信，结果注入上下文 |
| 抽象       | 像**代码/文件库**：Agent 需知道「**如何**运行、**读哪个**文件」 | 像 **API**：Agent 关心「提交什么参数、得到什么结果」 |
| 分享与安装 | 纯文本 → 分享简单；「安装」= 把文件夹放到约定路径   | 需部署/配置，相对重                     |

- **二者不互斥**：Skill 与 MCP 应**共存**；Skill 可以调用 MCP，MCP 理论上也能触发 Skill，但实际中「MCP 调 Skill」必要性不大。
- **选择建议**：按设计哲学区分——**流程、规范、何时读什么**用 Skill；**连什么数据、调什么接口**用 MCP。教育场景下：Skill 管「出题/批改/实验的 SOP」，MCP 管「题库 API、成绩库、实验平台」。

### Skill vs Workflow vs MCP：层次与组合

- **Skill**：原子能力是「**技能**」（如处理 PPT、Excel、PDF 的单项能力）。
- **Workflow**：做**一件事的流程**（先 A 后 B，如博客→PPT、播客→博客）。
- **MCP**：**工具/API**，参数进、结果出，填充 Context。

可组合方式：

- 把「下载音频」「播客转博客」分别做成 Skill；或做一个端到端 Workflow 型 Skill，内部再引用更小 Skill。
- 一种推荐的层次（不绝对）：**Workflow → Skill → MCP**；在 Claude Code 语境下可理解为：「端到端工作流 Skill」→「具体技能 Skill」→「调用外部工具/数据的 MCP」。
- **Sub-Agent** 在概念上与 Skill/Workflow 有重叠，边界在演进中；实践中「能用、可组合」优先于严格分层。

### 触发与稳定性：Skill 未解决的问题

- Skill 与 MCP 一样，**依赖模型根据上下文中的「技能描述」「工具描述」自行 decide**：是否调用、调用哪个。
- 因此 **Skill 并没有解决**：Agent 有时会忽略某 Skill、或选错 Skill/工具。核心都在模型的 **decide** 这一步。
- 可探索方向：**hook**（生命周期钩子）、更精准的 **description / trigger_keywords**、或与 Sub-Agent / 斜杠命令结合，减少误判。

### 比喻小结（与菜鸟教程互补）

- **模型**：刚毕业的实习生，有基础认知和 bash 等内化能力。
- **Skill**：一沓**技能手册**（+ 工具）；先读标题，按需求选一本展开，再按说明在本地动手完成。
- **MCP**：**外部服务窗口**（查询/审批/打饭）；实习生按格式发请求，拿结果，不关心窗口背后实现。
- **Sub-Agent**：下一层的**外包**，交付某一类任务（前提是已具备较完整能力、Skill、MCP）。

### 延伸阅读与官方入口（来自 temp 参考）

- **Anthropic 官方**  
  - [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/news/agent-skills)（建议精读）  
  - [anthropics/skills](https://github.com/anthropics/skills)（官方 Skill 库）  
  - [Introduction to Claude Skills (Cookbook)](https://cookbook.anthropic.com/)  
  - [Agent Skills - Claude Docs](https://docs.anthropic.com/)  
  - [Agent Skills (Specification)](https://github.com/anthropics/agent-skills)
- **观点与讨论**  
  - Simon Willison: [Claude Skills are awesome, maybe a bigger deal than MCP](https://simonwillison.net/)  
  - Skill 与 Memory：如 [memU](https://github.com/NevaMind-AI/memU) 等将 Skill 视为一种上下文/Memory 管理方式  
  - [Subagents, Commands and Skills Are Converging](https://www.anthropic.com/news)（斜杠命令、Sub-Agent、Skill 边界在收敛）  
  - [Why OpenAI’s Move to Skills Matters](https://www.anthropic.com/) / [Skills Are All You Need](https://www.anthropic.com/)（Skill 重要性）  
- **反例与安全**  
  - [Notes on SKILL.md vs MCP - Tao of Mac](https://taoofmac.com/)：某些场景下 Skill 不如 MCP 合适的案例  
  - 使用第三方 Skill 时需注意**安全**（不要轻易信任未知来源）；可考虑「代码审查类 Skill」审查第三方 Skill。

---

## 参考链接

- [Cursor - Agent Skills](https://cursor.com/docs/context/skills)
- [Agent Skills 开放标准 - agentskills.io](https://agentskills.io/)
- [Agents | Cursor Learn](https://cursor.com/learn/agents)
- [Skills 教程 | 菜鸟教程](https://www.runoob.com/ai-agent/skills-agent.html)
- [Anthropic - Equipping agents with Agent Skills](https://www.anthropic.com/news/agent-skills)
- [anthropics/skills (GitHub)](https://github.com/anthropics/skills)
