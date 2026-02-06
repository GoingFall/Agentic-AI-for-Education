"""
3.3.1 重复内容检测报告：对 results 对应切片做 hash 去重检测，输出重复率与样例。
用法：在项目根执行 python scripts/report_dedup.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from src.preprocessing.doc_index import load_doc_index, build_doc_index
from src.preprocessing.splitter import slice_document
from src.preprocessing.dedup import find_duplicate_chunks, dedup_chunks


def main() -> None:
    index_path = ROOT / "config" / "doc_index.json"
    results_dir = ROOT / "results"
    data_root = ROOT / "data" / "res.6-007-spring-2011"

    if index_path.is_file():
        entries = load_doc_index(index_path)
    else:
        entries = build_doc_index(results_dir, data_root)

    all_chunks: list = []
    for e in entries:
        path = Path(e["file_path"])
        if not path.is_file():
            path = results_dir / path.name
        if not path.is_file():
            continue
        chunks = slice_document(path, e)
        all_chunks.extend(chunks)

    n_total = len(all_chunks)
    pairs = find_duplicate_chunks(all_chunks, method="hash")
    duplicate_indices = {j for _, j in pairs}
    n_dupes = len(duplicate_indices)
    rate = (n_dupes / n_total * 100) if n_total else 0.0

    print(f"总切片数: {n_total}")
    print(f"重复切片数: {n_dupes}")
    print(f"重复率: {rate:.2f}%")
    print(f"去重后数量: {n_total - n_dupes}")

    if pairs:
        print("\n重复对样例（前 5 个，显示 doc_id / chunk_index）:")
        for i, (a, b) in enumerate(pairs[:5]):
            ca, cb = all_chunks[a], all_chunks[b]
            print(f"  [{a}] {ca.get('doc_id')} chunk {ca.get('chunk_index')} <-> [{b}] {cb.get('doc_id')} chunk {cb.get('chunk_index')}")

    out_txt = ROOT / "docs" / "task2" / "dedup_report.txt"
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(f"总切片数: {n_total}\n")
        f.write(f"重复切片数: {n_dupes}\n")
        f.write(f"重复率: {rate:.2f}%\n")
        f.write(f"去重后数量: {n_total - n_dupes}\n")
    print(f"\n报告已写入 {out_txt}")


if __name__ == "__main__":
    main()
