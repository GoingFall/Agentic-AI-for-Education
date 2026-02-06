"""
Markdown 加载与预处理测试：clean_md_text、parse_md_headings、load_md。
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pytest
from src.preprocessing.md_loader import clean_md_text, parse_md_headings, load_md


def test_clean_md_text():
    text = "Line 1\n\n\n\nLine 2\r\nLine 3"
    out = clean_md_text(text)
    assert "Line 1" in out and "Line 2" in out and "Line 3" in out
    assert "\n\n\n" not in out

    footer = "---\nMIT OpenCourseWare\n[http://ocw.mit.edu](http://ocw.mit.edu)\nResource: Signals\nProfessor Alan V. Oppenheim\n"
    out2 = clean_md_text("Content here\n\n" + footer)
    assert "Content here" in out2
    assert "MIT OpenCourseWare" not in out2 or "Professor Alan V. Oppenheim" not in out2


def test_parse_md_headings():
    text = "# Title\n\n## Section 1\n\nBody 1\n\n### Sub\n\nBody 2\n\n## Section 2\n\nEnd"
    sections = parse_md_headings(text)
    assert len(sections) >= 2
    assert sections[0]["level"] == 1 and sections[0]["title"] == "Title"
    assert sections[1]["level"] == 2 and sections[1]["title"] == "Section 1"
    assert sections[1]["start_line"] == 3
    assert sections[1]["end_line"] >= 3


def test_load_md():
    results_dir = ROOT / "results"
    if not results_dir.is_dir():
        pytest.skip("results/ not found")
    md_files = list(results_dir.glob("*.md"))
    if not md_files:
        pytest.skip("no .md in results/")
    path = md_files[0]
    cleaned, sections = load_md(path)
    assert isinstance(cleaned, str)
    assert isinstance(sections, list)
    for s in sections:
        assert "level" in s and "title" in s and "start_line" in s and "end_line" in s
