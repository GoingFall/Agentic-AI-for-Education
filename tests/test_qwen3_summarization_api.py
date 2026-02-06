"""
任务6（API）：简短摘要。使用 OpenRouter API 将长段压缩为 1～2 句摘要。
用例与本地版一致。运行：python tests/test_qwen3_summarization_api.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SHORT_INPUT = "Signals and Systems is an introduction to analog and digital signal processing. The course covers the Fourier transform and filtering."

MEDIUM_INPUT = "This course was developed in 1987 by the MIT Center for Advanced Engineering Studies. It was designed as a distance-education course for engineers and scientists in the workplace. Signals and Systems is an introduction to analog and digital signal processing, a topic that forms an integral part of engineering systems in many diverse areas."


def get_course_description():
    p = ROOT / "data" / "res.6-007-spring-2011" / "data.json"
    if not p.exists():
        return "Signals and Systems introduces analog and digital signal processing. The course presents basic concepts for continuous-time and discrete-time signals and systems. Signal representations are developed for time and frequency domains, related through the Fourier transform. Filtering, modulation, sampling, and feedback systems are discussed."
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return (data.get("course_description") or "")[:1200]


def get_cases():
    long_input = get_course_description()
    return [
        (SHORT_INPUT, "信号与系统介绍模拟与数字信号处理，涉及傅里叶变换与滤波。"),
        (MEDIUM_INPUT, "MIT 1987 年开发的远程教育课程，面向工程师，介绍信号与系统与信号处理。"),
        (long_input[:400], "课程介绍连续与离散时间信号与系统、傅里叶变换及滤波等。"),
        (long_input[:800], "信号与系统课程涵盖时域频域表示、傅里叶变换、滤波与调制、采样与反馈。"),
        (long_input, "本课程介绍模拟与数字信号处理基础，包括连续/离散信号与系统、傅里叶变换、滤波、调制、采样与反馈系统。"),
    ]


def run_one(llm, long_text, expected_summary, generate_fn):
    prompt = f"""将下面长文压缩为 1～2 句话的摘要。只输出摘要，不要解释、不要加「摘要：」等前缀。
长文：
{long_text[:600]}{"..." if len(long_text) > 600 else ""}

摘要："""
    return generate_fn(llm, prompt)


def main():
    from utils_qwen3_api import get_llm, generate_api

    print("Using OpenRouter API for summarization...")
    llm = get_llm()
    cases = get_cases()
    print("=" * 60)
    for i, (long_text, expected) in enumerate(cases, 1):
        out = run_one(llm, long_text, expected, generate_api)
        print(f"Case {i} (expected approx: {expected[:50]}...)")
        print(f"  Input length: {len(long_text)} chars")
        print(f"  Model output: {out}")
        print()
    print("Summarization (API) test done.")


if __name__ == "__main__":
    main()
