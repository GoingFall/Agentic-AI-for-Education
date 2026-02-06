"""
任务2（API）：触发词/关键词增强。使用 OpenRouter API 判断是否命中 recommend / practice / explain。
用例与本地版一致。运行：python tests/test_qwen3_trigger_enhancement_api.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CASES = [
    ("推荐一些作业", "recommend"),
    ("帮我解释一下卷积", "explain"),
    ("我想做练习", "practice"),
    ("你好呀", ""),
    ("Laplace transform 那讲我不太懂，能解释一下吗？另外推荐点题做做。", "explain, recommend"),
]


def run_one(llm, user_input, expected_triggers, generate_fn):
    prompt = f"""判断用户输入是否包含：推荐(recommend)、练习(practice)、解释(explain)。只输出命中的英文词，多个用逗号分隔，没有则输出 none。不要解释。
用户输入：{user_input}
命中的意图："""
    return generate_fn(llm, prompt)


def main():
    from utils_qwen3_api import get_llm, generate_api

    print("Using OpenRouter API for trigger enhancement...")
    llm = get_llm()
    print("=" * 60)
    for i, (user_input, expected) in enumerate(CASES, 1):
        out = run_one(llm, user_input, expected, generate_api)
        print(f"Case {i} (expected triggers: {expected})")
        print(f"  Input: {user_input[:50]}{'...' if len(user_input) > 50 else ''}")
        print(f"  Model output: {out}")
        print()
    print("Trigger enhancement (API) test done.")


if __name__ == "__main__":
    main()
