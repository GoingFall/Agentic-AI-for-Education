# maven-rag 参考项目分析

## 分析目的

本文件夹对参考项目 **maven-rag**（`D:\PythonWorkSpace\maven-rag`）进行系统性分析，针对本项目 [.kiro/specs/agentic-edu-helper/tasks.md](../.kiro/specs/agentic-edu-helper/tasks.md) 中**尚未完成**的每个小需求，评估其参考价值与可复用的工程设计，便于在实现 agent-edu 时借鉴或复用。

- **参考项目**：智能法律咨询助手（RAG + Agent + GraphRAG + 记忆，FastAPI 后端 + React 前端）
- **本项目**：Agentic AI 科学与工程教育助手（答疑 + 推荐练习 + 知识图谱，任务要求含 Dash Web、API、测试等）

## 参考项目路径

- **绝对路径**：`D:\PythonWorkSpace\maven-rag`
- **技术栈**：Python 3.11、FastAPI、sentence-transformers、FAISS、NetworkX、React 19 + TypeScript + Vite、D3.js

## 文档索引

| 文档 | 内容 |
|------|------|
| [01_requirement_mapping.md](01_requirement_mapping.md) | 按 tasks.md 条目的逐条参考性（高/中/低）与可复用点，及对应 maven-rag 关键文件 |
| [02_reusable_design.md](02_reusable_design.md) | 可复用工程设计摘要：后端/前端/测试/脚本与配置、数据流 |
| [03_file_reference.md](03_file_reference.md) | 需求/功能 → 参考文件路径 → 一行说明的速查表 |

## 与 tasks 优先级对应

| 优先级 | tasks 范围 | 本分析覆盖 |
|--------|------------|------------|
| **P0** | 6.1-6.2 Web 基础与对话界面、8.1 单元测试 | 01 中 6.1.x、6.2.x、8.1.x；02 前端与测试设计 |
| **P1** | 3.1、6.3-6.4、7.1-7.2、8.2-8.3、9.1-9.2 | 01 中 3.1、6.3-6.4、7.x、8.2-8.3、9.x |
| **P2** | 7.3、8.4、9.3、10、11、12 | 01 中 7.3、8.4、9.3、10.x、11.x、12.x；02/03 全量 |

## 使用说明

- 实现某条需求时，先在 **01_requirement_mapping.md** 中查该条目的参考性与可复用点。
- 需要整体架构或目录/文件级设计时，查阅 **02_reusable_design.md**。
- 需要快速定位参考代码文件时，使用 **03_file_reference.md** 按需求或功能查路径。

**注意**：tasks 要求 Web 为 **Dash**，参考项目为 **React**；文档中已标注“若采用 React 可复用度更高，若坚持 Dash 则仅借鉴交互与信息架构”。领域为法律 vs 教育，文档中区分“直接复用”“需适配”“仅思路借鉴”。
