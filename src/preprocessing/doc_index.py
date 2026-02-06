"""
文档索引：扫描 results/*.md，解析文件名得到 doc_id/doc_type，可选从 content_map + data.json 补全 title/description。
对应任务 2.2：现有数据分析和整理。
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, TypedDict

# 文件名模式: {hash}_MITRES_6_007S11_{lec01|hw01|hw01_sol|...}.md
FILENAME_PATTERN = re.compile(
    r"^([0-9a-f]{32})_MITRES_6_007S11_(lec\d{2}|hw\d{2}_sol|hw\d{2})\.md$",
    re.IGNORECASE,
)


def hash_to_uuid(hash_str: str) -> str:
    """将 32 位无连字符 hash 转为 8-4-4-4-12 格式的 UUID 字符串，用于查 content_map。"""
    if len(hash_str) != 32:
        return hash_str
    return f"{hash_str[:8]}-{hash_str[8:12]}-{hash_str[12:16]}-{hash_str[16:20]}-{hash_str[20:]}"


class DocEntry(TypedDict, total=False):
    file_path: str
    file_name: str
    hash: str
    doc_id: str
    doc_type: str
    lecture_index: int | None
    title: str
    description: str
    related_hw: str | None
    related_sol: str | None
    related_lec: str | None


def parse_md_filename(name: str) -> tuple[str, str, str] | None:
    """
    解析 results 下的 .md 文件名。
    返回 (hash, doc_id, doc_type) 或 None。
    doc_type: "lecture" | "homework" | "solution"
    doc_id: lec01, hw01, hw01_sol 等
    """
    m = FILENAME_PATTERN.match(name)
    if not m:
        return None
    hash_part, doc_id = m.group(1), m.group(2)
    if doc_id.startswith("lec"):
        doc_type = "lecture"
    elif doc_id.endswith("_sol"):
        doc_type = "solution"
    else:
        doc_type = "homework"
    return (hash_part, doc_id, doc_type)


def load_content_map(data_root: Path) -> dict[str, str]:
    """加载 content_map.json，key 为带连字符的 UUID，value 为 data.json 相对路径。"""
    path = data_root / "content_map.json"
    if not path.is_file():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_data_json(data_root: Path, resource_path: str) -> dict[str, Any] | None:
    """
    content_map 的 value 形如 /resources/mitres_6_007s11_lec01/data.json，
    需要去掉开头的 / 再与 data_root 拼接。
    """
    rel = resource_path.lstrip("/")
    path = data_root / rel
    if not path.is_file():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_doc_index(
    results_dir: Path,
    data_root: Path | None = None,
    *,
    include_relations: bool = True,
) -> list[DocEntry]:
    """
    扫描 results_dir 下所有 .md，构建文档索引。
    若提供 data_root（如 data/res.6-007-spring-2011），则通过 content_map + data.json 补全 title/description。
    include_relations 为 True 时填充 related_hw / related_sol / related_lec。
    """
    results_dir = Path(results_dir)
    data_root = Path(data_root) if data_root else None
    content_map = load_content_map(data_root) if data_root else {}

    entries: list[DocEntry] = []
    md_files = sorted(results_dir.glob("*.md"))

    for path in md_files:
        name = path.name
        parsed = parse_md_filename(name)
        if not parsed:
            continue
        hash_str, doc_id, doc_type = parsed
        entry: DocEntry = {
            "file_path": str(path.resolve()),
            "file_name": name,
            "hash": hash_str,
            "doc_id": doc_id,
            "doc_type": doc_type,
        }
        if doc_type == "lecture":
            entry["lecture_index"] = int(doc_id[3:], 10)
        elif doc_type == "homework":
            entry["lecture_index"] = int(doc_id[2:], 10)
        else:
            # hw01_sol -> 1
            entry["lecture_index"] = int(doc_id[2:].replace("_sol", ""), 10)

        uuid_key = hash_to_uuid(hash_str)
        if uuid_key in content_map:
            data_json = load_data_json(data_root, content_map[uuid_key])
            if data_json:
                if "title" in data_json:
                    entry["title"] = data_json["title"]
                if "description" in data_json:
                    entry["description"] = data_json["description"]

        if include_relations:
            if doc_type == "lecture":
                idx = entry["lecture_index"]
                entry["related_hw"] = f"hw{idx:02d}"
                entry["related_sol"] = f"hw{idx:02d}_sol"
            elif doc_type == "homework":
                idx = entry["lecture_index"]
                entry["related_lec"] = f"lec{idx:02d}"
                entry["related_sol"] = f"hw{idx:02d}_sol"
            else:
                idx = entry["lecture_index"]
                entry["related_lec"] = f"lec{idx:02d}"
                entry["related_hw"] = f"hw{idx:02d}"

        entries.append(entry)

    return entries


def analyze_md_structure(entries: list[DocEntry]) -> list[dict[str, Any]]:
    """
    2.2.1：分析每个 .md 的结构和内容（标题层级、段落数、长度）。
    返回每文件的简单统计，便于后续切片策略调参。
    """
    report = []
    for e in entries:
        path = Path(e["file_path"])
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        h1, h2, h3 = 0, 0, 0
        for line in lines:
            s = line.strip()
            if s.startswith("# "):
                h1 += 1
            elif s.startswith("## "):
                h2 += 1
            elif s.startswith("### "):
                h3 += 1
        report.append({
            "file_name": e["file_name"],
            "doc_id": e["doc_id"],
            "doc_type": e["doc_type"],
            "char_count": len(text),
            "line_count": len(lines),
            "headings": {"h1": h1, "h2": h2, "h3": h3},
        })
    return report


def save_doc_index(entries: list[DocEntry], out_path: Path) -> None:
    """将文档索引写入 JSON 文件（如 config/doc_index.json）。"""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def load_doc_index(index_path: Path) -> list[DocEntry]:
    """从 JSON 文件加载文档索引。"""
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import os
    import sys

    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    os.chdir(root)

    results_dir = root / "results"
    data_root = root / "data" / "res.6-007-spring-2011"
    config_dir = root / "config"
    index_path = config_dir / "doc_index.json"

    entries = build_doc_index(results_dir, data_root)
    print(f"Indexed {len(entries)} documents.")
    save_doc_index(entries, index_path)
    print(f"Saved to {index_path}")

    report = analyze_md_structure(entries)
    print("\nStructure report (first 3):")
    for r in report[:3]:
        print(r)
