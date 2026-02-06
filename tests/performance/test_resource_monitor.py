"""
性能测试 8.4.3：内存/CPU 可观测。在若干次 /api/chat 调用前后采样进程资源（需 psutil），输出报告。
若未安装 psutil 则 skip；不强制断言，便于人工查看。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not installed")
def test_chat_memory_delta(client_no_mock):
    """若干次 chat 请求前后采样当前进程内存，输出增量（MB）。"""
    process = psutil.Process()
    with patch("src.agent.run.invoke_with_skills") as m:
        m.return_value = {"reply": "ok", "session_id": "r1", "selected_skill_ids": []}
        before_mb = process.memory_info().rss / 1024 / 1024
        for _ in range(5):
            client_no_mock.post("/api/chat", json={"message": "memory test"})
        after_mb = process.memory_info().rss / 1024 / 1024
    delta = after_mb - before_mb
    print(f"\n[performance] 5 次 /api/chat 后进程内存增量: {delta:.2f} MB (before={before_mb:.1f}, after={after_mb:.1f})")
    # 可选：断言增长不超过某值，如 50MB
    # assert delta < 50, f"内存增长 {delta:.1f} MB 超过 50 MB"
