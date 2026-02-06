"""
任务3（API）：查询压缩/关键词抽取。使用 OpenRouter API 将长问句压缩为 3～5 个关键词或短问。
用例与本地版一致。运行：python tests/test_qwen3_query_compression_api.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CASES = [
    ("什么是傅里叶变换？", "傅里叶变换 定义"),
    ("Continuous-time Fourier series 和 discrete-time 的区别是什么？", "Fourier series 连续 离散 区别"),
    ("Signals and Systems 这门课里，filtering 和 modulation 分别在讲什么？", "filtering modulation 信号与系统"),
    ("我想问一下卷积的性质以及它和 LTI 系统的关系。", "卷积 性质 LTI"),
    ("The course presents signal and system representations for both time and frequency domains, related through the Fourier transform. 请问频域分析有什么应用？", "频域 傅里叶 应用"),
]


def run_one(llm, long_query, expected_short, generate_fn):
    prompt = f"""将下面的长问题压缩为 3～5 个关键词或一句短问。只输出关键词或短问，不要解释、不要编号。
长问题：{long_query}
关键词或短问："""
    return generate_fn(llm, prompt)


def main():
    from utils_qwen3_api import get_llm, generate_api

    print("Using OpenRouter API for query compression...")
    llm = get_llm()
    print("=" * 60)
    for i, (long_query, expected) in enumerate(CASES, 1):
        out = run_one(llm, long_query, expected, generate_api)
        safe_out = (out or "").encode("utf-8", errors="replace").decode("utf-8")
        print(f"Case {i} (expected approx: {expected})")
        print(f"  Input: {long_query[:60]}{'...' if len(long_query) > 60 else ''}")
        print(f"  Model output: {safe_out}")
        print()
    print("Query compression (API) test done.")


if __name__ == "__main__":
    main()
