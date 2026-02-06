# Task3 实现说明

本文档归档 Task3（数据扩展和优化中的 3.2 / 3.3）的完成思路、模块与脚本、复现方式及本目录文件说明。详细技术细节见 [docs/task2 的 §9 与 task2_data_preprocessing_and_knowledge_base.md](../task2/task2_data_preprocessing_and_knowledge_base.md)。

---

## 1. 范围

- **不实现**：3.1 全量数据处理（继续使用 results 下 15 个 .md）。
- **3.2 知识图谱完善和可视化**：3.2.1 概念覆盖兜底；3.2.2 先修关系权重与类型；3.2.3 难度与学习路径；3.2.4 章节-切片映射与可视化。
- **3.3 数据质量优化**：3.3.1 重复检测与去重；3.3.2 切片策略优化；3.3.3 质量评估指标。

---

## 2. 完成思路

- **数据源**：沿用 `results/` 下 15 个 .md（lec01～lec05、hw01～hw05、hw01_sol～hw05_sol）。
- **3.2.1**：若某讲无 section 或仅 level 1，生成兜底概念 `{doc_id}_overview`，保证每讲至少一个 Concept。
- **3.2.2**：PREREQUISITE 按讲次设 strength（首尾 0.75、中间 0.85）；DEPENDS_ON 增加 `type`（same_lecture / cross_lecture）、`weight`（1.0 / 0.8）；COVERS 固定 relevance 0.9；导出图图例标注权重。
- **3.2.3**：Concept 增加 `difficulty`（按 section 顺序 basic / intermediate / advanced）；新增学习路径模块，提供从 Topic/Concept 沿 PREREQUISITE/DEPENDS_ON 的后续序列查询。
- **3.2.4**：先建章节-切片映射（section_chunk_map.json），再生成 HTML 展示每讲章节结构及每个 section 对应 concept_id（切片在知识图谱中的定位）。
- **3.3.1**：基于文本归一化 hash 检测重复切片，提供去重函数；ingest 可选去重；脚本输出重复率与样例。
- **3.3.2**：扩展公式边界（`\[...\]`、`$...$`）、避免在列表项/表格行中间切；切片参数可通过环境变量配置。
- **3.3.3**：按 doc 统计 chunk 数、长度、重复率、section 覆盖率，输出 JSON 与 Markdown 报告。

---

## 3. 模块与脚本一览

| 类型 | 路径 | 说明 |
|------|------|------|
| 模块 | `src/knowledge_graph/concepts.py` | 概念兜底、DEPENDS_ON 类型/权重、Concept difficulty |
| 模块 | `src/knowledge_graph/build.py` | PREREQUISITE/COVERS 权重 |
| 模块 | `src/knowledge_graph/learning_path.py` | get_learning_path_from_topic / get_learning_path_from_concept |
| 模块 | `src/preprocessing/section_chunk_map.py` | 构建章节-切片映射 |
| 模块 | `src/preprocessing/dedup.py` | find_duplicate_chunks、dedup_chunks |
| 模块 | `src/preprocessing/quality_metrics.py` | compute_quality_metrics |
| 模块 | `src/preprocessing/splitter.py` | 公式/列表边界优化、环境变量配置 |
| 模块 | `src/preprocessing/chroma_ingest.py` | dedup_before_ingest 参数 |
| 脚本 | `scripts/build_section_chunk_map.py` | 生成 config/section_chunk_map.json |
| 脚本 | `scripts/export_section_structure_html.py` | 生成章节结构 HTML（含 concept_id） |
| 脚本 | `scripts/report_dedup.py` | 重复率与样例报告 |
| 脚本 | `scripts/report_quality.py` | 质量报告 JSON + MD |
| 脚本 | `scripts/export_knowledge_graph_figure.py` | 知识图谱导出 PNG（需 Neo4j） |

---

## 4. 复现说明

在项目根目录执行：

```bash
# 章节-切片映射（无需 Neo4j）
python scripts/build_section_chunk_map.py

# 章节结构 HTML（依赖 config/section_chunk_map.json）
python scripts/export_section_structure_html.py

# 去重报告
python scripts/report_dedup.py

# 质量报告
python scripts/report_quality.py

# 知识图谱导出图（需配置 .env 中 NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD，且已导入图谱）
python scripts/export_knowledge_graph_figure.py -c sample -l lec01 -o docs/task3/knowledge_graph_concepts_sample_lec01.png
```

单元测试（不依赖 Neo4j 的用例可单独跑）：

```bash
pytest tests/test_splitter.py tests/test_doc_index.py tests/test_md_loader.py tests/test_knowledge_graph.py -v
```

说明：`test_build_and_ingest_graph_from_index` 依赖 Neo4j，若未启动可能超时，可跳过或单独在有 Neo4j 环境运行。

---

## 5. 本目录文件说明

| 文件 | 用途 |
|------|------|
| `task3_实现说明.md` | 本文档：完成思路、模块/脚本、复现、文件索引 |
| `测试运行结果.txt` | 上述脚本与单元测试的控制台输出归档 |
| `section_structure.html` | 章节结构及切片在知识图谱中的定位（concept_id） |
| `knowledge_graph_concepts_sample_lec01.png` | 知识图谱单讲示例图（Topic/Exercise/Concept、TEACHES/PRACTICES/DEPENDS_ON） |
| `quality_report.md` | 数据质量评估报告（Markdown） |
| `quality_report.json` | 数据质量评估报告（JSON） |
| `dedup_report.txt` | 重复内容检测报告 |

若需“真实截图”（浏览器打开 `section_structure.html` 的截图），可手动打开该 HTML 截图保存为 `section_structure_screenshot.png`。
