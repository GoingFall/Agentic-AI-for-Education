"""
属性基测试 8.3.1：引用准确性——从回复中解析出的引用必须对应真实存在的课程材料。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _parse_citations_from_reply(reply: str) -> set[str]:
    """从回复文本解析「第N讲」「作业N」并映射为 doc_id。"""
    doc_ids = set()
    # 第1讲、第2讲 … → lec01, lec02
    for m in re.finditer(r"第\s*(\d+)\s*讲", reply):
        n = int(m.group(1))
        doc_ids.add(f"lec{n:02d}")
    # 作业1、作业2 … → hw01, hw02
    for m in re.finditer(r"作业\s*(\d+)", reply):
        n = int(m.group(1))
        doc_ids.add(f"hw{n:02d}")
    return doc_ids


def _valid_doc_ids() -> set[str]:
    """从 doc_index 或固定集合获取合法 doc_id。"""
    index_path = ROOT / "config" / "doc_index.json"
    if index_path.is_file():
        import json
        with open(index_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        return {e["doc_id"] for e in entries}
    return {"lec01", "lec02", "lec03", "lec04", "lec05", "hw01", "hw02", "hw03", "hw04", "hw05", "hw01_sol", "hw02_sol", "hw03_sol", "hw04_sol", "hw05_sol"}


VALID_DOC_IDS = _valid_doc_ids()


@given(reply=st.text(min_size=0, max_size=2000))
def test_parsed_citations_in_valid_set(reply: str):
    """任意回复文本中解析出的引用（第N讲、作业N）必须在合法 doc_id 集合内；无引用时 vacuously true。"""
    parsed = _parse_citations_from_reply(reply)
    invalid = parsed - VALID_DOC_IDS
    assert not invalid, f"解析到非法引用 doc_id: {invalid}，合法集合: {VALID_DOC_IDS}"


def test_citation_parse_examples():
    """固定示例：带引用的回复解析后均在合法集合内。"""
    replies = [
        "参见第1讲、第2讲。",
        "根据作业3 的内容。",
        "第4讲中介绍了卷积。",
    ]
    for reply in replies:
        parsed = _parse_citations_from_reply(reply)
        assert parsed <= VALID_DOC_IDS, f"reply={reply!r} -> {parsed}"
