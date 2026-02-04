"""
OpenRouter API 连接测试：从 .env 读取 OPENROUTER_API_KEY，发起一次简单对话以验证连通性。
运行：在项目根目录执行 python test/test_openrouter_connection.py
"""
import os
import sys
from pathlib import Path

# 项目根目录，用于加载 .env
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("ERROR: OPENROUTER_API_KEY not set. Add it to .env in project root.")
    sys.exit(1)

# OpenRouter 使用 OpenAI 兼容接口
from langchain_openai import ChatOpenAI

BASE_URL = "https://openrouter.ai/api/v1"
# 可选：使用免费模型，如 openai/gpt-3.5-turbo 或 google/gemma-2-9b-it:free
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

llm = ChatOpenAI(
    model=MODEL,
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=BASE_URL,
    temperature=0,
)

if __name__ == "__main__":
    print(f"Testing OpenRouter (base={BASE_URL}, model={MODEL}) ...")
    try:
        resp = llm.invoke("Reply with one short sentence: connection OK.")
        # ASCII-safe output for Windows/conda
        out = (resp.content or "").encode("utf-8", errors="replace").decode("ascii", errors="replace")
        print("Response:", out or "(empty)")
        print("OpenRouter connection test passed.")
    except Exception as e:
        print("OpenRouter connection test failed:", repr(e))
        sys.exit(1)
