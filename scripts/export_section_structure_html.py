"""
3.2.4.2 / 3.2.4.3 基于 section_chunk_map 生成章节结构 HTML，并展示切片在知识图谱中的定位（concept_id）。
用法：在项目根执行 python scripts/export_section_structure_html.py
输出：docs/task2/section_structure.html
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from src.knowledge_graph.concepts import slugify


def main() -> None:
    map_path = ROOT / "config" / "section_chunk_map.json"
    index_path = ROOT / "config" / "doc_index.json"
    out_path = ROOT / "docs" / "task2" / "section_structure.html"

    if not map_path.is_file():
        print(f"Run scripts/build_section_chunk_map.py first. Missing {map_path}")
        return

    with open(map_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    documents = data.get("documents", {})

    doc_index: list[dict] = []
    if index_path.is_file():
        with open(index_path, "r", encoding="utf-8") as f:
            doc_index = json.load(f)
    doc_id_to_info: dict[str, dict] = {e["doc_id"]: e for e in doc_index if e.get("doc_id")}

    # 按 doc_id 排序，讲义优先
    def sort_key(did: str) -> tuple[int, str]:
        if did.startswith("lec"):
            return 0, did
        if did.startswith("hw") and "_sol" not in did:
            return 1, did
        return 2, did

    sorted_doc_ids = sorted(documents.keys(), key=sort_key)

    rows: list[str] = []
    for doc_id in sorted_doc_ids:
        info = doc_id_to_info.get(doc_id, {})
        doc_type = info.get("doc_type", "")
        title = info.get("title", doc_id)
        sections = documents.get(doc_id, [])
        is_lecture = doc_type == "lecture"

        rows.append(f'<div class="doc-block" id="doc-{doc_id}">')
        rows.append(f'<h2>{doc_id} — {title}</h2>')
        if is_lecture:
            rows.append(
                '<p class="note">讲义章节对应知识图谱中的 Concept 节点；图中示例见 '
                '<a href="knowledge_graph_concepts_sample_lec01.png">knowledge_graph_concepts_sample_lec01.png</a>。</p>'
            )
        rows.append("<table><thead><tr><th>章节</th><th>层级</th><th>切片数</th><th>切片索引</th>")
        if is_lecture:
            rows.append("<th>知识图谱概念节点 (concept_id)</th>")
        rows.append("</tr></thead><tbody>")

        for sec in sections:
            st = sec.get("section_title") or ""
            level = sec.get("section_level", 0)
            chunks = sec.get("chunks", [])
            indices = [c.get("chunk_index", 0) for c in chunks]
            indices_str = ",".join(str(i) for i in indices[:10])
            if len(indices) > 10:
                indices_str += f", ... (+{len(indices) - 10})"
            concept_id = ""
            if is_lecture and st:
                slug = slugify(st)
                concept_id = f"{doc_id}_{slug}"
            elif is_lecture and not st:
                concept_id = f"{doc_id}_overview"

            rows.append("<tr>")
            rows.append(f"<td>{_escape(st) or '(无标题)'}</td>")
            rows.append(f"<td>{level}</td>")
            rows.append(f"<td>{len(chunks)}</td>")
            rows.append(f"<td>{indices_str}</td>")
            if is_lecture:
                rows.append(f"<td><code>{_escape(concept_id)}</code></td>")
            rows.append("</tr>")
        rows.append("</tbody></table>")
        rows.append("</div>")

    nav = "".join(
        f'<a href="#doc-{doc_id}">{doc_id}</a> ' for doc_id in sorted_doc_ids
    )
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>章节结构与切片映射</title>
<style>
body {{ font-family: sans-serif; margin: 1rem 2rem; }}
.nav {{ margin-bottom: 1.5rem; }}
.nav a {{ margin-right: 1rem; }}
.doc-block {{ margin-bottom: 2rem; }}
table {{ border-collapse: collapse; }}
th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.8rem; text-align: left; }}
th {{ background: #f0f0f0; }}
.note {{ color: #666; font-size: 0.9rem; }}
code {{ font-size: 0.85em; }}
</style>
</head>
<body>
<h1>章节结构与切片在知识图谱中的定位</h1>
<p class="nav">按文档跳转：{nav}</p>
{"".join(rows)}
</body>
</html>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")


def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


if __name__ == "__main__":
    main()
