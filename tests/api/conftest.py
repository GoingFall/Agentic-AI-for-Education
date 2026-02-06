"""API 测试 fixture：临时会话目录、TestClient、mock invoke_with_skills。"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# 确保项目根在 path 中
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 在导入 app 前 patch 会话路径，由 fixture 在需要时应用
def _patch_session_store_to_tmp(tmp_path: Path):
    import src.api.session_store as store
    store.SESSIONS_DIR = tmp_path
    store.SESSIONS_FILE = tmp_path / "sessions.json"
    store.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def tmp_sessions_dir(tmp_path):
    """临时会话目录，并让 session_store 使用该目录。"""
    _patch_session_store_to_tmp(tmp_path)
    return tmp_path


@pytest.fixture
def client(tmp_sessions_dir):
    """使用临时会话目录的 FastAPI TestClient。"""
    from src.api.app import app
    return TestClient(app)


@pytest.fixture
def client_no_mock(tmp_sessions_dir):
    """不 mock Agent 的 TestClient，用于集成测试（需 Chroma/Neo4j 时可能被 skip）。"""
    from src.api.app import app
    return TestClient(app)
