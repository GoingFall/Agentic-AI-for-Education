# RAG（检索增强生成）调研

> 与项目「Agentic AI for Science & Engineering Education」相关：为教育场景下的 AI 助手提供权威、可追溯的知识来源，减少幻觉、支持领域与时效性更新。

## 定义与价值

**RAG (Retrieval-Augmented Generation)** 是在大语言模型生成前，从外部权威知识库检索相关信息并纳入上下文的流程，从而优化输出、引用可追溯来源。

- **来源**：[AWS - What is RAG?](https://aws.amazon.com/what-is/retrieval-augmented-generation/)、[ScienceDirect - RAG for educational application](https://www.sciencedirect.com/science/article/pii/S2666920X25000578)

### 为何重要（尤其教育场景）

- LLM 存在**幻觉**、**知识截止**、**术语歧义**等问题。
- RAG 将模型引导到**预先确定的权威知识源**进行检索，再生成回答。
- 组织可更好控制生成内容，用户可查看引用来源，利于教育场景的**可信与可验证**。

### 主要优势

| 维度 | 说明 |
|------|------|
| **成本** | 无需重训大模型即可接入领域/机构知识，成本更低。 |
| **时效** | 可连接文档、数据库、API 等，便于更新教材、大纲、政策。 |
| **可信** | 输出可带引用，支持溯源与核查。 |
| **可控** | 可限定检索范围、权限与数据源，便于教育合规。 |

## 工作流程（简要）

1. **构建外部数据**：教材、课件、题库等 → 切片、向量化 → 写入向量库。
2. **检索**：用户问题向量化，在向量库中检索最相关片段。
3. **增强提示**：将检索到的片段与用户问题一起作为 LLM 的输入。
4. **生成**：LLM 基于「问题 + 检索内容」生成回答。
5. **更新**：通过批量或实时流程更新文档与向量，保持知识新鲜。

## 教育应用综述（ScienceDirect）

- **文献**：*Retrieval-augmented generation for educational application: A systematic survey* (Computers and Education: Artificial Intelligence, 2025).
- **要点**：
  - 综述 RAG 在多种教育场景下的应用。
  - 技术组件：索引策略、检索器类型、生成与优化方法。
  - 覆盖 51 项研究，涉及教育目标、学习情境、应用场景。
  - 挑战：幻觉缓解、知识完整性与时效性、计算成本、多模态支持。

## 与项目关联

- 科学/工程教育 AI 助手需要：**课程大纲、教材、实验规范、安全条例**等权威文本。
- RAG 可提供「检索 + 引用」的问答与讲解，适合答疑、复习、实验指导等场景。
- 可与知识图谱结合：图谱提供结构与关系，RAG 提供段落级证据与生成。

## 参考链接

- [AWS - What is RAG?](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
- [Retrieval-augmented generation for educational application (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S2666920X25000578)
- [RAG Agents in Higher Education (UT Dallas)](https://atlas.utdallas.edu/TDClient/30/Portal/KB/PrintArticle?ID=1386)
