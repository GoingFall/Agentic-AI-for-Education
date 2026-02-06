"""
模拟前端输入「你好？」：调用 invoke_with_skills，直到不报错并打印正常反馈。
在项目根目录执行：python scripts/simulate_chat_hello.py
需已配置 .env（OpenRouter 等）；Chroma/Neo4j 未就绪时可能报工具相关错误，但不应再出现 'str' object has no attribute 'get'。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# 与 pytest conftest 一致：加载 .env 以便读取 OPENROUTER_API_KEY 等
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")


def main():
    from src.agent.run import invoke_with_skills

    session_id = "sim-hello-1"
    user_message = "你好？"
    skills_dir = ROOT / "skills"
    session_store = {}

    print("输入:", user_message)
    print("调用 invoke_with_skills ...")
    try:
        result = invoke_with_skills(
            user_message,
            session_id=session_id,
            session_store=session_store,
            skills_dir=skills_dir,
        )
        reply = result.get("reply", "")
        skill_ids = result.get("selected_skill_ids") or []
        print("回复:", reply)
        print("Skill IDs:", skill_ids)
        print("正常反馈。")
    except Exception as e:
        print("请求出错:", e)
        if "OPENROUTER_API_KEY" in str(e) or "API_KEY" in str(e):
            print("请先在项目根目录 .env 中配置 OPENROUTER_API_KEY 后重试。")
        raise

if __name__ == "__main__":
    main()
