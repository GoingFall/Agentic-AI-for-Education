"""
PyMuPDF 测试：打开 PDF、读取页数、提取首页文本；使用统一接口 backend=pymupdf 导出 .md。
运行：在项目根目录执行 python tests/test_pymupdf.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

# 使用 data 下已有 PDF（若不存在则跳过文件相关断言）
SAMPLE_PDF = ROOT / "data" / "res.6-007-spring-2011" / "static_resources" / "0400ba59406d52d94c079d99928156ee_MITRES_6_007S11_lec04.pdf"
RESULTS_DIR = ROOT / "results"


def main():
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("ERROR: PyMuPDF not installed. Run: pip install pymupdf")
        sys.exit(1)

    try:
        # 测试 1：版本与空文档
        print("PyMuPDF version:", fitz.version[0])
        empty_doc = fitz.open()
        assert empty_doc.page_count == 0
        empty_doc.close()
        print("Empty document test passed.")

        # 测试 2：若有样本 PDF，使用统一接口（PyMuPDF 后端）导出为 results/*.md
        if SAMPLE_PDF.exists():
            from src.preprocessing.pdf_parser import export_pdf_to_md
            doc = fitz.open(SAMPLE_PDF)
            assert doc.page_count >= 1
            page = doc.load_page(0)
            text = page.get_text()
            doc.close()
            print("Sample PDF test passed: page_count >= 1, first page text length =", len(text))
            out_md = export_pdf_to_md(SAMPLE_PDF, RESULTS_DIR, backend="pymupdf")
            if out_md:
                print("Exported to:", out_md)
        else:
            print("Sample PDF not found, skip file test:", SAMPLE_PDF)

        print("PyMuPDF test passed.")
    except Exception as e:
        print("PyMuPDF test failed:", repr(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
