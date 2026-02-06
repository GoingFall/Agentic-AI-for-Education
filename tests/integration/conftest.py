"""集成测试 fixture：复用 API 的临时会话目录与 TestClient。"""
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _patch_session_store_to_tmp(tmp_path: Path):
    import src.api.session_store as store
    store.SESSIONS_DIR = tmp_path
    store.SESSIONS_FILE = tmp_path / "sessions.json"
    store.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def tmp_sessions_dir(tmp_path):
    _patch_session_store_to_tmp(tmp_path)
    return tmp_path


@pytest.fixture
def client(tmp_sessions_dir):
    from src.api.app import app
    return TestClient(app)
