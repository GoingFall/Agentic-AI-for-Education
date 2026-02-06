"""
Markdown 加载与预处理：文本清洗、章节结构识别与标注。
对应任务 2.1.2 文本清洗和格式化、2.1.3 章节结构识别和标注。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import TypedDict


# 常见页脚/版权块，清洗时去掉
FOOTER_PATTERNS = [
    re.compile(r"---\s*\nMIT OpenCourseWare\s*\n\[.*?\]\(.*?\).*", re.DOTALL | re.IGNORECASE),
    re.compile(r"Resource:.*?Professor Alan V\. Oppenheim\s*$", re.DOTALL | re.IGNORECASE),
]


def clean_md_text(text: str) -> str:
    """
    2.1.2：对 .md 做轻量清洗。
    - 统一换行为 \\n
    - 合并连续多余空行（最多保留一个）
    - 去除页脚（如 MIT OpenCourseWare 块）
    """
    if not text:
        return ""
    # 统一换行
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # 去除页脚
    for pat in FOOTER_PATTERNS:
        text = pat.sub("", text)
    # 合并连续空行（保留单个 \n\n）
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class Section(TypedDict):
    level: int
    title: str
    start_line: int
    end_line: int
    start_offset: int
    end_offset: int


def parse_md_headings(text: str) -> list[Section]:
    """
    2.1.3：按 Markdown 标题（#, ##, ###）解析层级，为后续切片提供 section 边界与标题。
    返回 Section 列表，包含 level(1-3)、title、start_line/end_line（1-based）、start_offset/end_offset（字符偏移）。
    """
    lines = text.splitlines()
    sections: list[Section] = []
    current_offset = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        line_len = len(line) + 1  # +1 for \n
        stripped = line.strip()
        level = 0
        if stripped.startswith("### "):
            level = 3
            title = stripped[4:].strip()
        elif stripped.startswith("## "):
            level = 2
            title = stripped[3:].strip()
        elif stripped.startswith("# "):
            level = 1
            title = stripped[2:].strip()
        if level > 0:
            start_line = i + 1
            start_offset = current_offset
            # 该 section 的 end 为下一个同级或更高级标题之前，或文件末尾
            j = i + 1
            end_offset = current_offset + line_len
            while j < len(lines):
                s = lines[j].strip()
                next_level = 0
                if s.startswith("### "):
                    next_level = 3
                elif s.startswith("## "):
                    next_level = 2
                elif s.startswith("# "):
                    next_level = 1
                if next_level > 0 and next_level <= level:
                    break
                end_offset += len(lines[j]) + 1
                j += 1
            end_line = j - 1 if j > i + 1 else start_line
            sections.append({
                "level": level,
                "title": title,
                "start_line": start_line,
                "end_line": end_line,
                "start_offset": start_offset,
                "end_offset": end_offset,
            })
        current_offset += line_len
        i += 1
    return sections


def load_md(path: Path) -> tuple[str, list[Section]]:
    """
    加载 .md 文件：读取内容、清洗、解析章节结构。
    返回 (cleaned_text, sections)。
    """
    path = Path(path)
    raw = path.read_text(encoding="utf-8", errors="replace")
    cleaned = clean_md_text(raw)
    sections = parse_md_headings(cleaned)
    return cleaned, sections
