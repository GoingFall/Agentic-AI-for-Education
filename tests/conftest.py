"""pytest 根 conftest：在跑测试前加载项目根目录的 .env。"""
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
