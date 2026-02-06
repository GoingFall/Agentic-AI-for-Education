"""
性能测试 8.4.1：响应时间基准。对 POST /api/chat 单次或少量请求记录耗时，mock 时断言低于阈值。
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# 使用 mock 时单次请求应在 2s 内完成（不含真实 LLM）
MOCK_RESPONSE_TIME_THRESHOLD_SEC = 2.0


@pytest.mark.performance
@pytest.mark.slow
def test_chat_response_time_with_mock(client_no_mock):
    """Mock invoke_with_skills 时，单次 POST /api/chat 响应时间应低于阈值。"""
    with patch("src.agent.run.invoke_with_skills") as m:
        m.return_value = {"reply": "ok", "session_id": "perf", "selected_skill_ids": []}
        start = time.perf_counter()
        resp = client_no_mock.post("/api/chat", json={"message": "hi"})
        elapsed = time.perf_counter() - start
    assert resp.status_code == 200
    assert elapsed < MOCK_RESPONSE_TIME_THRESHOLD_SEC, (
        f"Mock 下响应时间 {elapsed:.2f}s 应 < {MOCK_RESPONSE_TIME_THRESHOLD_SEC}s"
    )


@pytest.mark.performance
@pytest.mark.slow
def test_chat_response_time_report(client_no_mock):
    """记录 3 次请求平均耗时并输出（mock），便于人工查看。"""
    with patch("src.agent.run.invoke_with_skills") as m:
        m.return_value = {"reply": "ok", "session_id": "perf", "selected_skill_ids": []}
        times = []
        for _ in range(3):
            start = time.perf_counter()
            client_no_mock.post("/api/chat", json={"message": "bench"})
            times.append(time.perf_counter() - start)
    mean_ms = sum(times) / len(times) * 1000
    print(f"\n[performance] POST /api/chat 3 次平均: {mean_ms:.1f} ms")
    assert mean_ms < MOCK_RESPONSE_TIME_THRESHOLD_SEC * 1000 * 1.5
