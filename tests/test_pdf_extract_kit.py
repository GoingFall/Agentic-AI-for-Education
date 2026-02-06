"""
PDF-Extract-Kit 后端测试：优先 Docker（PDF_EXTRACT_KIT_DOCKER_IMAGE），否则本地（PDF_EXTRACT_KIT_ROOT）。
运行：在项目根目录执行 python tests/test_pdf_extract_kit.py
若两者均未设置或样本 PDF 不存在，则跳过。
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

SAMPLE_PDF = ROOT / "data" / "res.6-007-spring-2011" / "static_resources" / "0400ba59406d52d94c079d99928156ee_MITRES_6_007S11_lec04.pdf"
RESULTS_DIR = ROOT / "results"


def main():
    docker_image = os.environ.get("PDF_EXTRACT_KIT_DOCKER_IMAGE")
    kit_root = os.environ.get("PDF_EXTRACT_KIT_ROOT")
    if not docker_image and not kit_root:
        print("SKIP: Set PDF_EXTRACT_KIT_DOCKER_IMAGE (Docker) or PDF_EXTRACT_KIT_ROOT (local) to run.")
        return
    if kit_root and not Path(kit_root).is_dir():
        print("SKIP: PDF_EXTRACT_KIT_ROOT is not a directory:", kit_root)
        return

    from src.preprocessing.pdf_parser import export_pdf_to_md

    if not SAMPLE_PDF.exists():
        print("SKIP: Sample PDF not found:", SAMPLE_PDF)
        return

    if docker_image:
        print("Using PDF-Extract-Kit via Docker image:", docker_image)
    else:
        print("Using PDF-Extract-Kit at:", kit_root)
    out_md = export_pdf_to_md(SAMPLE_PDF, RESULTS_DIR, backend="pdf_extract_kit")
    if out_md:
        print("Exported to:", out_md)
    else:
        print("PDF-Extract-Kit export returned None (Docker: check image and PDF_EXTRACT_KIT_MODELS_PATH; local: check models).")


if __name__ == "__main__":
    main()
