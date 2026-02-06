"""
3.2.4.1 从 doc_index + results 生成章节-切片映射，写入 config/section_chunk_map.json。
用法：在项目根执行 python scripts/build_section_chunk_map.py
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
from src.preprocessing.section_chunk_map import build_section_chunk_map


def main() -> None:
    index_path = ROOT / "config" / "doc_index.json"
    results_dir = ROOT / "results"
    data_root = ROOT / "data" / "res.6-007-spring-2011"
    out_path = ROOT / "config" / "section_chunk_map.json"

    if index_path.is_file():
        entries = load_doc_index(index_path)
    else:
        entries = build_doc_index(results_dir, data_root)

    if not entries:
        print("No doc index entries.")
        return

    mapping = build_section_chunk_map(entries, results_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path} ({len(mapping.get('documents', {}))} documents).")


if __name__ == "__main__":
    main()
