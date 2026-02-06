"""
3.3.3 数据质量评估报告：输出 quality_report.json 与简短 Markdown 摘要到 docs/task2/。
用法：在项目根执行 python scripts/report_quality.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from src.preprocessing.doc_index import load_doc_index, build_doc_index
from src.preprocessing.quality_metrics import compute_quality_metrics


def main() -> None:
    index_path = ROOT / "config" / "doc_index.json"
    results_dir = ROOT / "results"
    data_root = ROOT / "data" / "res.6-007-spring-2011"
    out_dir = ROOT / "docs" / "task2"

    if index_path.is_file():
        entries = load_doc_index(index_path)
    else:
        entries = build_doc_index(results_dir, data_root)

    if not entries:
        print("No doc index entries.")
        return

    metrics = compute_quality_metrics(entries, results_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "quality_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"Wrote {json_path}")

    md_lines = [
        "# 数据质量评估报告（3.3.3）",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| 总切片数 | {metrics['total_chunks']} |",
        f"| 去重后切片数 | {metrics['total_unique_after_dedup']} |",
        f"| 重复率 | {metrics['duplicate_rate'] * 100:.2f}% |",
        f"| Section 覆盖率（整体） | {metrics['section_coverage']['overall'] * 100:.2f}% |",
        "",
        "## 按文档",
        "",
        "| doc_id | chunk 数 | 平均长度 | 最小 | 最大 | Section 覆盖率 |",
        "|--------|----------|----------|------|------|----------------|",
    ]
    for doc_id, doc_meta in sorted(metrics["by_doc"].items()):
        cov = metrics["section_coverage"]["by_doc"].get(doc_id, 0)
        cov_pct = f"{cov * 100:.0f}%"
        md_lines.append(
            f"| {doc_id} | {doc_meta['chunk_count']} | {doc_meta['avg_len']} | "
            f"{doc_meta['min_len']} | {doc_meta['max_len']} | {cov_pct} |"
        )
    md_path = out_dir / "quality_report.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
