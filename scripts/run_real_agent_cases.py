"""
用真实 Agent 逐个跑测试用例中的消息，打印 selected_skill_ids 与回复。
与 tests/api/test_chat.py 中 USER_MESSAGE_CASES 保持一致。
在项目根目录执行：
  python scripts/run_real_agent_cases.py           # 跑全部
  python scripts/run_real_agent_cases.py 0         # 只跑第 0 条
  python scripts/run_real_agent_cases.py --index 2 # 只跑第 2 条
需已配置 .env（OPENROUTER_API_KEY 等）。
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

# Windows 控制台 GBK 无法编码回复中的 Unicode 时避免崩溃
if hasattr(sys.stdout, "buffer") and (not getattr(sys.stdout, "encoding", None) or sys.stdout.encoding.lower() not in ("utf-8", "utf8")):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# 与 tests/api/test_chat.py 中 USER_MESSAGE_CASES 一致
USER_MESSAGE_CASES = [
    "什么是卷积？",
    "傅里叶变换的定义",
    "如何理解线性时不变系统？",
    "解释一下离散时间信号",
    "第3讲讲了什么？",
    "LTI system explain",
    "推荐下一步练习",
    "我学了第1讲，该做什么题",
    "学完第2讲想巩固一下，有什么作业推荐？",
    "recommend practice for me",
    "你好",
    "谢谢",
    "帮我看看这道题",
]

# 预期 skill_ids（与 MESSAGE_EXPECTED_SKILLS 一致，用于对比）
EXPECTED_SKILLS = [
    ["qa", "exercise-recommend"],
    ["qa", "exercise-recommend"],
    ["qa", "exercise-recommend"],
    ["qa", "exercise-recommend"],
    [],
    ["qa", "exercise-recommend"],
    ["exercise-recommend"],
    [],
    ["exercise-recommend"],
    ["exercise-recommend"],
    [],
    [],
    [],
]


def main():
    from src.agent.run import invoke_with_skills

    # 解析只跑某一条： run_real_agent_cases.py 3  或  --index 3
    run_index: int | None = None
    args = [a for a in sys.argv[1:] if a != ""]
    for i, a in enumerate(args):
        if a == "--index" and i + 1 < len(args):
            try:
                run_index = int(args[i + 1])
            except ValueError:
                run_index = None
            break
        if a.isdigit():
            run_index = int(a)
            break

    skills_dir = ROOT / "skills"
    session_store = {}
    session_id = "run-real-agent-cases"

    indices = [run_index] if run_index is not None else range(len(USER_MESSAGE_CASES))
    if run_index is not None and (run_index < 0 or run_index >= len(USER_MESSAGE_CASES)):
        print(f"无效索引 {run_index}，共 {len(USER_MESSAGE_CASES)} 条")
        return

    for idx in indices:
        message = USER_MESSAGE_CASES[idx]
        expected = EXPECTED_SKILLS[idx]
        print()
        print("=" * 60)
        print(f"[{idx}] 输入: {message}")
        print(f"     预期 skill_ids: {expected}")
        print("-" * 60)
        try:
            result = invoke_with_skills(
                message,
                session_id=session_id,
                session_store=session_store,
                skills_dir=skills_dir,
            )
            reply = result.get("reply", "")
            skill_ids = result.get("selected_skill_ids") or []
            print(f"     实际 skill_ids: {skill_ids}")
            ok = "Y" if skill_ids == expected else "N"
            print(f"     与预期一致: {ok}")
            print()
            print("回复:")
            print(reply if len(reply) <= 800 else reply[:800] + "\n... (已截断)")
        except Exception as e:
            print(f"     请求出错: {e}")
            if "OPENROUTER_API_KEY" in str(e) or "API_KEY" in str(e):
                print("请先在项目根目录 .env 中配置 OPENROUTER_API_KEY 后重试。")
            raise
        print()

    print("=" * 60)
    print("全部完成。")


if __name__ == "__main__":
    main()
