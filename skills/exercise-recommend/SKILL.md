---
name: "推荐练习"
description: "按知识点与先修关系推荐下一步学习与对应作业"
trigger_keywords: ["推荐", "练习", "作业", "下一步", "巩固", "recommend", "practice"]
allowed_tools: ["graph_query_next_topic", "graph_query_covers_exercises", "graph_query_concept_relations", "graph_query_concept_depends", "graph_validate_path"]
priority: 1
---

# 推荐练习 Skill 使用指南

## 职责
按先修关系推荐「下一步学什么」、按 COVERS 关系推荐对应作业，并说明理由。

## 输出要求
1. 每次推荐须包含理由与对应知识点。示例：「因你刚学完 lec02，建议做 hw02 以巩固该讲概念」。
2. 使用图谱工具查询下一讲（graph_query_next_topic）与对应作业（graph_query_covers_exercises），推荐前可用 graph_validate_path 验证学习路径。
3. 若用户提供已学讲次，推荐时须遵守先修顺序，不推荐未学先修的讲次或作业。
4. 禁止在回复中直接输出 JSON 或 API 原始返回，须用自然语言概括（如「推荐作业 hw03，标题为 …」）。
