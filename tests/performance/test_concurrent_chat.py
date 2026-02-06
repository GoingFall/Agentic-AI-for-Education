"""
性能测试 8.4.2：并发用户压力。多线程并发 POST /api/chat，统计成功数、延迟分位。
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CONCURRENCY = 5
REQUESTS_PER_THREAD = 2


@pytest.mark.performance
@pytest.mark.slow
def test_concurrent_chat_requests(client_no_mock):
    """并发 CONCURRENCY 线程各发 REQUESTS_PER_THREAD 次请求，统计 200 数与延迟。"""
    with patch("src.agent.run.invoke_with_skills") as m:
        m.return_value = {"reply": "ok", "session_id": "c1", "selected_skill_ids": []}
        latencies_ms = []
        errors = []

        def do_request(i: int):
            start = time.perf_counter()
            try:
                r = client_no_mock.post("/api/chat", json={"message": f"req-{i}"})
                return r.status_code, (time.perf_counter() - start) * 1000
            except Exception as e:
                return None, str(e)

        with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
            futures = [ex.submit(do_request, i) for i in range(CONCURRENCY * REQUESTS_PER_THREAD)]
            for f in as_completed(futures):
                code, lat_or_err = f.result()
                if code == 200:
                    latencies_ms.append(lat_or_err)
                else:
                    errors.append(lat_or_err)

        success = len(latencies_ms)
        total = CONCURRENCY * REQUESTS_PER_THREAD
        assert success == total, f"期望全部 200，成功 {success}/{total}，错误: {errors}"
        if latencies_ms:
            latencies_ms.sort()
            p95 = latencies_ms[int(len(latencies_ms) * 0.95)] if len(latencies_ms) >= 20 else latencies_ms[-1]
            print(f"\n[performance] 并发 {CONCURRENCY}x{REQUESTS_PER_THREAD} 请求: 成功 {success}, P95 延迟 {p95:.1f} ms")
