"""
调用真实 Agent 看回复（不 mock）。可传一条消息，不传则用默认示例。
在项目根目录执行：
  python scripts/call_real_agent.py
  python scripts/call_real_agent.py "什么是卷积？"
  python scripts/call_real_agent.py "推荐下一步练习"
需已配置 .env（OPENROUTER_API_KEY 等）。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

DEFAULT_MESSAGE = "什么是卷积？"


def main():
    from src.agent.run import invoke_with_skills

    message = (sys.argv[1].strip() if len(sys.argv) > 1 else DEFAULT_MESSAGE) or DEFAULT_MESSAGE
    session_id = "call-real-agent-1"
    skills_dir = ROOT / "skills"
    session_store = {}

    print("输入:", message)
    print("-" * 40)
    try:
        result = invoke_with_skills(
            message,
            session_id=session_id,
            session_store=session_store,
            skills_dir=skills_dir,
        )
        reply = result.get("reply", "")
        skill_ids = result.get("selected_skill_ids") or []
        print("回复:\n", reply)
        print("-" * 40)
        print("session_id:", result.get("session_id"))
        print("selected_skill_ids:", skill_ids)
    except Exception as e:
        print("请求出错:", e)
        if "OPENROUTER_API_KEY" in str(e) or "API_KEY" in str(e):
            print("请先在项目根目录 .env 中配置 OPENROUTER_API_KEY 后重试。")
        raise


if __name__ == "__main__":
    main()
