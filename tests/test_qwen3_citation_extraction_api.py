"""
任务4（API）：引用句抽取。使用 OpenRouter API 从段落中抽取与问题最相关的一句。
用例与本地版一致。运行：python tests/test_qwen3_citation_extraction_api.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CASES = [
    (
        "The course presents and integrates the basic concepts for both continuous-time and discrete-time signals and systems. Signal and system representations are developed for both time and frequency domains. These representations are related through the Fourier transform.",
        "What relates time and frequency domains?",
        "related through the Fourier transform",
    ),
    (
        "Filtering and filter design, modulation, and sampling for both analog and digital systems are discussed. Feedback systems for both analog and digital systems are also illustrated.",
        "What does the course say about feedback?",
        "Feedback systems",
    ),
    (
        "LEC 1: Introduction. LEC 2: Signals and systems Part I. LEC 3: Signals and systems Part II. LEC 4: Convolution. LEC 5: Properties of linear, time-invariant systems.",
        "Which lecture is about convolution?",
        "LEC 4: Convolution",
    ),
    (
        "Signals and Systems is an introduction to analog and digital signal processing. The course was designed as a distance-education course for engineers. The Fourier transform and its generalizations are explored in detail.",
        "Who is the course for?",
        "distance-education course for engineers",
    ),
    (
        "Continuous-time Fourier series (PDF). Continuous-time Fourier transform (PDF). Fourier transform properties (PDF). Discrete-time Fourier series (PDF). Discrete-time Fourier transform (PDF). Filtering (PDF).",
        "Where do we see discrete-time Fourier transform?",
        "Discrete-time Fourier transform",
    ),
]


def run_one(llm, paragraph, question, expected_cite, generate_fn):
    prompt = f"""从下面段落中抽取与问题最相关的一句话。只输出那一句话，不要解释、不要重复。
段落：
{paragraph}

问题：{question}

最相关的一句："""
    return generate_fn(llm, prompt)


def main():
    from utils_qwen3_api import get_llm, generate_api

    print("Using OpenRouter API for citation extraction...")
    llm = get_llm()
    print("=" * 60)
    for i, (paragraph, question, expected) in enumerate(CASES, 1):
        out = run_one(llm, paragraph, question, expected, generate_api)
        print(f"Case {i} (expected contains: {expected[:40]}...)")
        print(f"  Question: {question}")
        print(f"  Model output: {out}")
        print()
    print("Citation extraction (API) test done.")


if __name__ == "__main__":
    main()
