# 测试案例与 PDF 转化清单

根据 [.kiro/specs/agentic-edu-helper/tasks.md](../.kiro/specs/agentic-edu-helper/tasks.md) 中的任务 2（数据预处理）、任务 8（测试与质量保证）及优先级说明，本文档说明：**为满足后续测试需要，应优先转化哪些 PDF**。

---

## 一、测试需求与所需数据的对应关系

| 任务/测试项 | 需求简述 | 依赖的已转化内容 |
|------------|----------|------------------|
| **2.2.4** 优先处理前 5 个讲义 | 建立初始数据集 | 前 5 讲讲义 PDF → 文本/结构化内容 |
| **8.1.1** 数据预处理模块测试 | PDF→文本、清洗、章节识别 | 至少 1 个讲义 + 1 个作业（类型差异） |
| **8.2.1** 端到端对话流程测试 | RAG 检索、引用、回答 | 讲义文本已切片并入向量库 |
| **8.3.1** 引用准确性属性测试 | 回答中的引用必须对应真实课程材料 | 与 RAG 一致：前 5 讲讲义已处理 |
| **8.3.2** 推荐一致性属性测试 | 推荐内容符合知识图谱先修/习题关系 | 讲义 + 作业/答案 → 知识点与习题关联 |
| **2.4.x** 知识图谱构建 | 知识点、先修关系、习题关联 | 课程大纲/讲义 + 习题与答案 |

结论：  
- **必须转化**：前 5 个讲义（lec01～lec05），用于初始数据集、预处理测试、RAG、引用测试、知识图谱知识点提取。  
- **建议转化**：前 5 讲对应的作业与答案（hw01～hw05、hw01_sol～hw05_sol），用于知识图谱习题关联与推荐一致性测试。

---

## 二、需转化的 PDF 清单

路径均相对于 `data/res.6-007-spring-2011/static_resources/`，文件名格式为 `{uid}_MITRES_6_007S11_{资源名}.pdf`。

### 2.1 必须转化：前 5 个讲义（初始数据集 + 8.1.1 / 8.2.1 / 8.3.1）

| 序号 | 课程资源名 | 文件名（static_resources 下） | 说明 |
|------|------------|------------------------------|------|
| 1 | Lecture 1, Introduction | `e6c75426e220f1a406b0b9be1f55bbc1_MITRES_6_007S11_lec01.pdf` | 第 1 讲 |
| 2 | Lecture 2, Signals and systems: Part I | `defeabeacb2b0ffecfbda27d7cc0b1dd_MITRES_6_007S11_lec02.pdf` | 第 2 讲 |
| 3 | Lecture 3, Signals and systems: Part II | `13f950129c8ddfd54c7c0d91edfd7d93_MITRES_6_007S11_lec03.pdf` | 第 3 讲 |
| 4 | Lecture 4, Convolution | `0400ba59406d52d94c079d99928156ee_MITRES_6_007S11_lec04.pdf` | 第 4 讲（已有 results：`MITRES_6_007S11_lec04.md`） |
| 5 | Lecture 5, Properties of LTI systems | `bfea8f0475c54f2846cee5c14c4875fe_MITRES_6_007S11_lec05.pdf` | 第 5 讲 |

**共 5 个 PDF**。其中 lec04 若已按现有 pipeline 产出 `results/MITRES_6_007S11_lec04.md`，可视为已转化，只需再转化 lec01、lec02、lec03、lec05。

### 2.2 建议转化：前 5 讲对应作业与答案（知识图谱 + 8.3.2）

| 类型 | 资源名 | 文件名（static_resources 下） |
|------|--------|------------------------------|
| 作业 | HW01 | `d367a3c05c298bed00aae37754dd2631_MITRES_6_007S11_hw01.pdf` |
| 答案 | HW01 Solution | `e7e527598f89cf8dbd91432500ac53b3_MITRES_6_007S11_hw01_sol.pdf` |
| 作业 | HW02 | `8fbf4451c622e6efbcf7452222d21ea5_MITRES_6_007S11_hw02.pdf` |
| 答案 | HW02 Solution | `dfac4e2a745cc45c870bba07aa55885b_MITRES_6_007S11_hw02_sol.pdf` |
| 作业 | HW03 | `5ef8ecc5a7d42a418c1db014c951ac9c_MITRES_6_007S11_hw03.pdf` |
| 答案 | HW03 Solution | `aa6f4739cf29d78a12a23fcf2033e298_MITRES_6_007S11_hw03_sol.pdf` |
| 作业 | HW04 | `cab2602ff858c51113591d17321a80fc_MITRES_6_007S11_hw04.pdf` |
| 答案 | HW04 Solution | `0a374ee9df1ba2a9cd985807c735afa6_MITRES_6_007S11_hw04_sol.pdf` |
| 作业 | HW05 | `7b78bd1fa3c324d9fc38d2cd4712fa85_MITRES_6_007S11_hw05.pdf` |
| 答案 | HW05 Solution | `1e8612f9dfd2b6b1c7fc293d862efbef_MITRES_6_007S11_hw05_sol.pdf` |

**共 10 个 PDF**。用于 2.4 习题与知识点关联、8.3.2 推荐一致性测试。

### 2.3 可选：数据预处理测试的类型覆盖（8.1.1）

若希望 8.1.1 同时覆盖「讲义」与「作业/答案」两种文档结构，在 2.1 基础上至少再转化 **1 个作业 + 1 个答案** 即可（例如 hw01 + hw01_sol），其余作业/答案可归入 2.2 按需扩展。

---

## 三、转化结果放置约定（建议）

- 讲义：`results/MITRES_6_007S11_lec{01..26}.md`（与现有 lec04 一致）。  
- 作业/答案：例如 `results/MITRES_6_007S11_hw{01..26}.md`、`results/MITRES_6_007S11_hw{01..26}_sol.md`，或按项目现有命名规范统一。

---

## 四、最小可行集（仅做通 pipeline 与基础测试）

若资源有限，**最小集合**为：

1. **lec01**（`e6c75426e220f1a406b0b9be1f55bbc1_MITRES_6_007S11_lec01.pdf`）  
2. **lec04**（已存在 `results/MITRES_6_007S11_lec04.md` 时可跳过转化）  
3. **lec05**（`bfea8f0475c54f2846cee5c14c4875fe_MITRES_6_007S11_lec05.pdf`）  
4. 任选 **1 个作业 + 1 个答案**（如 hw01 + hw01_sol）

即可支撑：预处理单测（8.1.1）、初始 RAG/引用（8.2.1/8.3.1）和简单的知识图谱/推荐测试（8.3.2）。

---

## 五、与 tasks.md 的对应关系小结

- **2.2.4**：前 5 讲 → 转化 2.1 中 5 个讲义 PDF。  
- **8.1.1**：数据预处理测试 → 至少 2.1 全部 + 建议 2.2 中至少 1 作业 1 答案。  
- **8.2.1 / 8.3.1**：端到端与引用准确性 → 2.1 讲义转化并入库即可。  
- **8.3.2 / 2.4**：推荐一致性与知识图谱 → 2.1 + 2.2 全部或部分（建议至少 hw01～hw05 及对应 sol）。

按上述清单完成转化后，即可覆盖 tasks.md 中「接下来的测试」所需的数据基础。

---

## 六、已复制待转化 PDF 的文件夹

上述 15 个 PDF 已复制到 **`data/pdf_to_convert/`**。**已全部转化完成**，产出在 **`results/`**（共 15 个 .md 文件：lec01～lec05、hw01～hw05、hw01_sol～hw05_sol）。
