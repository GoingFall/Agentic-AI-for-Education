"""
统一 PDF 解析接口：支持 PyMuPDF 与 PDF-Extract-Kit 两种后端。
- PDF-Extract-Kit 本地：设置 PDF_EXTRACT_KIT_ROOT（Python 3.10 环境）。
- PDF-Extract-Kit Docker：设置 PDF_EXTRACT_KIT_DOCKER_IMAGE，由 Python 3.11 通过 docker 调用。
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

Backend = Literal["pymupdf", "pdf_extract_kit"]


def _stem_from_pdf_path(pdf_path: Path) -> str:
    """从 PDF 路径得到输出文件名用 stem，去掉哈希前缀。"""
    stem = pdf_path.stem
    if "_" in stem and len(stem) > 20:
        stem = stem.split("_", 1)[1]
    return stem


def _export_pymupdf(pdf_path: Path, out_dir: Path, stem: str) -> Path | None:
    """使用 PyMuPDF 将 PDF 按页提取文本并写入单个 .md 文件。"""
    import fitz

    if not pdf_path.exists():
        return None
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stem}.md"
    doc = fitz.open(pdf_path)
    parts = [f"# {pdf_path.name}\n\n", f"页数: {doc.page_count}\n\n"]
    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text().strip()
        parts.append(f"## 第 {i + 1} 页\n\n{text}\n\n")
    doc.close()
    out_path.write_text("".join(parts), encoding="utf-8")
    return out_path


def _pdf_to_images(pdf_path: Path, images_dir: Path) -> None:
    """将 PDF 每一页渲染为 PNG 到 images_dir，文件名按页序 0001.png, 0002.png, ..."""
    import fitz

    doc = fitz.open(pdf_path)
    images_dir.mkdir(parents=True, exist_ok=True)
    for i in range(doc.page_count):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=150)
        out_name = f"{(i + 1):04d}.png"
        pix.save(images_dir / out_name)
    doc.close()


def _export_pdf_extract_kit_docker(pdf_path: Path, out_dir: Path, stem: str) -> Path | None:
    """
    通过 Docker 调用 PDF-Extract-Kit 的 pdf2markdown。
    要求：设置 PDF_EXTRACT_KIT_DOCKER_IMAGE；可选 PDF_EXTRACT_KIT_MODELS_PATH 挂载模型目录。
    """
    image = os.environ.get("PDF_EXTRACT_KIT_DOCKER_IMAGE")
    if not image:
        return None
    # 检查 docker 可用
    ret = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        timeout=10,
    )
    if ret.returncode != 0:
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stem}.md"

    with tempfile.TemporaryDirectory(prefix="agent_edu_pdf_kit_") as tmp:
        tmp_path = Path(tmp)
        images_dir = tmp_path / "images"
        result_dir = tmp_path / "output"
        result_dir.mkdir()

        _pdf_to_images(pdf_path, images_dir)

        # Windows 下 Docker Desktop 接受绝对路径，如 C:\Users\...
        host_images = str(images_dir.resolve())
        host_output = str(result_dir.resolve())
        cmd = [
            "docker",
            "run",
            "--rm",
            "-v", f"{host_images}:/input",
            "-v", f"{host_output}:/output",
            "-e", "INPUT_DIR=/input",
            "-e", "OUTPUT_DIR=/output",
        ]
        models_path = os.environ.get("PDF_EXTRACT_KIT_MODELS_PATH")
        if models_path and Path(models_path).is_dir():
            cmd.extend(["-v", f"{str(Path(models_path).resolve())}:/app/models"])
        cmd.append(image)

        ret = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if ret.returncode != 0:
            return None

        md_files = sorted(result_dir.rglob("*.md"))
        if not md_files:
            return None
        if len(md_files) == 1:
            shutil.copy(md_files[0], out_path)
        else:
            parts = [f"# {pdf_path.name}\n\n"]
            for m in md_files:
                parts.append(m.read_text(encoding="utf-8", errors="replace"))
                parts.append("\n\n")
            out_path.write_text("".join(parts), encoding="utf-8")
    return out_path


def _export_pdf_extract_kit(pdf_path: Path, out_dir: Path, stem: str) -> Path | None:
    """
    使用 PDF-Extract-Kit 的 pdf2markdown 流程：PDF→图片→layout/OCR/公式等→Markdown。
    要求：已克隆 PDF-Extract-Kit，安装依赖并下载模型，设置环境变量 PDF_EXTRACT_KIT_ROOT。
    """
    kit_root = os.environ.get("PDF_EXTRACT_KIT_ROOT")
    if not kit_root or not Path(kit_root).is_dir():
        return None

    kit_path = Path(kit_root).resolve()
    run_script = kit_path / "project" / "pdf2markdown" / "scripts" / "run_project.py"
    default_config = kit_path / "project" / "pdf2markdown" / "configs" / "pdf2markdown.yaml"
    if not run_script.is_file() or not default_config.is_file():
        return None

    try:
        import yaml
    except ImportError:
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stem}.md"

    with tempfile.TemporaryDirectory(prefix="agent_edu_pdf_kit_") as tmp:
        tmp_path = Path(tmp)
        images_dir = tmp_path / "images"
        result_dir = tmp_path / "output"

        # 1. PDF 转图片（pdf2markdown 的 input 为图片目录）
        _pdf_to_images(pdf_path, images_dir)

        # 2. 生成临时 config：仅覆盖 inputs/outputs，其余与默认一致
        with open(default_config, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        config["inputs"] = str(images_dir.resolve())
        config["outputs"] = str(result_dir.resolve())
        config["merge2markdown"] = True
        temp_config = tmp_path / "config.yaml"
        with open(temp_config, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        # 3. 在 PDF-Extract-Kit 根目录执行 run_project.py
        cmd = [os.environ.get("PYTHON", "python"), str(run_script), "--config", str(temp_config)]
        ret = subprocess.run(
            cmd,
            cwd=str(kit_path),
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "PYTHONPATH": str(kit_path)},
        )
        if ret.returncode != 0:
            return None

        # 4. 收集生成的 .md：可能多页多个文件或单个 merge 文件
        md_files = sorted(result_dir.rglob("*.md"))
        if not md_files:
            return None
        if len(md_files) == 1:
            shutil.copy(md_files[0], out_path)
        else:
            parts = [f"# {pdf_path.name}\n\n"]
            for m in md_files:
                parts.append(m.read_text(encoding="utf-8", errors="replace"))
                parts.append("\n\n")
            out_path.write_text("".join(parts), encoding="utf-8")
    return out_path


def export_pdf_to_md(
    pdf_path: Path,
    out_dir: Path,
    backend: Backend = "pymupdf",
) -> Path | None:
    """
    将 PDF 导出为 Markdown 文件到 out_dir，返回输出文件路径。

    - backend="pymupdf"：使用 PyMuPDF 按页提取文本（轻量、无需额外环境）。
    - backend="pdf_extract_kit"：使用 PDF-Extract-Kit 的 pdf2markdown 流程。
      优先通过 Docker 调用（设置 PDF_EXTRACT_KIT_DOCKER_IMAGE，适合 Python 3.11 宿主）；
      否则使用本地环境（设置 PDF_EXTRACT_KIT_ROOT，需 Python 3.10 与模型）。
    """
    stem = _stem_from_pdf_path(Path(pdf_path))
    if backend == "pdf_extract_kit":
        # 优先 Docker（宿主机 Python 3.11 无需安装 PDF-Extract-Kit）
        out = _export_pdf_extract_kit_docker(Path(pdf_path), Path(out_dir), stem)
        if out is not None:
            return out
        out = _export_pdf_extract_kit(Path(pdf_path), Path(out_dir), stem)
        if out is not None:
            return out
        return None
    return _export_pymupdf(Path(pdf_path), Path(out_dir), stem)
