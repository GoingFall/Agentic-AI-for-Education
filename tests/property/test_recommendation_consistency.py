"""
属性基测试 8.3.2：推荐一致性——推荐的学习内容必须满足知识图谱先修关系（validate_path 通过）。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given, settings, strategies as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# 已知合法 topic 及先修顺序（lec01→lec02→…）
VALID_TOPICS = ["lec01", "lec02", "lec03", "lec04", "lec05"]


@settings(deadline=None)
@given(
    learned=st.lists(st.sampled_from(VALID_TOPICS), min_size=0, max_size=5),
    recommended=st.sampled_from(VALID_TOPICS),
)
def test_validate_path_consistent_when_recommended_in_learned(learned: list[str], recommended: str):
    """当 recommended 已在 learned 中时，validate_path 应返回 True。"""
    from src.agent.tools import graph as graph_module
    with patch.object(graph_module, "_run_cypher", return_value=[]):
        ok, _ = graph_module.validate_path(learned, recommended)
    if recommended in learned:
        assert ok is True


def test_validate_path_prereq_order():
    """固定用例：按顺序学 lec01→lec02 时推荐 lec02 通过；只学 lec01 推荐 lec03 不通过（需 mock 图）。"""
    from src.agent.tools import graph as graph_module
    # 推荐 lec02，先修仅 lec01；若图返回 prereqs=[lec01]，则 [lec01] 应通过
    with patch.object(graph_module, "_run_cypher", return_value=["lec01"]):
        ok, msg = graph_module.validate_path(["lec01"], "lec02")
    assert ok is True
    # 推荐 lec03，先修 lec01,lec02；只学 lec01 则缺 lec02
    with patch.object(graph_module, "_run_cypher", return_value=["lec01", "lec02"]):
        ok2, msg2 = graph_module.validate_path(["lec01"], "lec03")
    assert ok2 is False
    assert "lec02" in msg2 or "先学习" in msg2
