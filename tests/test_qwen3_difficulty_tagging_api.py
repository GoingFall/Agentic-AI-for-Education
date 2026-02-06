"""
任务5（API）：难度/标签打标。使用 OpenRouter API 将题目或知识点标为 easy / medium / hard。
用例与本地版一致。运行：python tests/test_qwen3_difficulty_tagging_api.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CASES = [
    ("Introduction", "easy"),
    ("Signals and systems: Part I", "easy"),
    ("Continuous-time Fourier series", "medium"),
    ("The Laplace transform", "medium"),
    ("Feedback example: The inverted pendulum", "hard"),
    ("Mapping continuous-time filters to discrete-time filters", "hard"),
]


def run_one(llm, topic_or_problem, expected_difficulty, generate_fn):
    prompt = f"""将下列课程题目或知识点的难度标为 easy / medium / hard 之一。只输出一个英文词，不要解释。
题目或知识点：{topic_or_problem}
难度："""
    return generate_fn(llm, prompt)


def main():
    from utils_qwen3_api import get_llm, generate_api

    print("Using OpenRouter API for difficulty tagging...")
    llm = get_llm()
    print("=" * 60)
    for i, (topic, expected) in enumerate(CASES, 1):
        out = run_one(llm, topic, expected, generate_api)
        print(f"Case {i} (expected: {expected})")
        print(f"  Input: {topic}")
        print(f"  Model output: {out}")
        print()
    print("Difficulty tagging (API) test done.")


if __name__ == "__main__":
    main()
