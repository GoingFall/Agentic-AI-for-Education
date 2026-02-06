"""
任务1（API）：意图/Skill 路由。使用 OpenRouter API 将用户输入分类为 qa / exercise_recommend / chitchat。
用例与本地版一致。运行：python tests/test_qwen3_intent_routing_api.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

VALID_INTENTS = {"qa", "exercise_recommend", "chitchat", "none"}
INTENT_PRIORITY = ["qa", "exercise_recommend", "chitchat", "none"]

CASES = [
    ("什么是傅里叶变换？", ["qa"]),
    ("推荐一些练习", ["exercise_recommend"]),
    ("你好", ["chitchat"]),
    ("我想巩固一下连续时间傅里叶级数，有什么作业可以推荐？", ["exercise_recommend"]),
    ("傅里叶变换的性质和滤波那一讲的内容我有点混，能解释一下吗？顺便有没有相关题目？", ["qa", "exercise_recommend"]),
]


def _is_placeholder(s):
    if not s or not s.strip():
        return True
    t = s.strip()
    meaningful = t.replace("_", "").replace(" ", "").replace("，", "").replace(",", "")
    meaningful = meaningful.replace("（", "").replace("）", "")
    if len(meaningful) <= 1 or "空格" in t or "逗号" in t:
        return True
    return False


def run_one(llm, user_input, _expected, generate_fn):
    prompt = f"""意图分类。只输出标签，不要解释。标签只能是：qa / exercise_recommend / chitchat。
用户：什么是傅里叶变换？ 标签：qa
用户：推荐一些练习 标签：exercise_recommend
用户：你好 标签：chitchat
用户：{user_input}
标签："""
    raw = generate_fn(llm, prompt)
    found = []
    for intent in INTENT_PRIORITY:
        if intent in raw and intent not in found:
            found.append(intent)
    if found:
        return found
    if _is_placeholder(raw):
        return ["none"]
    first = (raw.split()[0].strip(".,;:?") if raw else "").strip()
    if first and first in VALID_INTENTS:
        return [first]
    return ["none"]


def main():
    from utils_qwen3_api import get_llm, generate_api

    print("Using OpenRouter API for intent routing...")
    llm = get_llm()
    print("=" * 60)
    for i, (user_input, expected) in enumerate(CASES, 1):
        out = run_one(llm, user_input, expected, generate_api)
        ok = set(out) == set(expected)
        print(f"Case {i} (expected: {expected}) {'OK' if ok else ''}")
        print(f"  Input: {user_input[:50]}{'...' if len(user_input) > 50 else ''}")
        print(f"  Model output: {out}")
        print()
    print("Intent routing (API) test done.")


if __name__ == "__main__":
    main()
