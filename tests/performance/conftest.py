"""性能测试：禁用限流；提供 client_no_mock。"""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("API_RATE_LIMIT_DISABLED", "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _patch_session_store(tmp_path: Path):
    import src.api.session_store as store
    store.SESSIONS_DIR = tmp_path
    store.SESSIONS_FILE = tmp_path / "sessions.json"
    store.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def tmp_sessions_dir(tmp_path):
    _patch_session_store(tmp_path)
    return tmp_path


@pytest.fixture
def client_no_mock(tmp_sessions_dir):
    from src.api.app import app
    return TestClient(app)
