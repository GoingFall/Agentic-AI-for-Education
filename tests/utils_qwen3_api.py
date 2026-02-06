"""
六任务 API 测试公共逻辑：使用 OpenRouter API（.env 中 OPENROUTER_API_KEY）。
运行：在项目根目录执行各 test_qwen3_*_api.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")


def get_llm():
    """获取 OpenRouter ChatOpenAI 实例。"""
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set. Add it to .env in project root.")
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=MODEL,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=BASE_URL,
        temperature=0,
    )


def generate_api(llm, prompt):
    """调用 API 生成回复，返回首段文本（strip）。"""
    resp = llm.invoke(prompt)
    return (resp.content or "").strip()
