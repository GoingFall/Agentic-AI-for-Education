# PDF-Extract-Kit Docker 镜像

用于在 **Python 3.11** 的 agent-edu 项目中通过 Docker 调用 PDF-Extract-Kit（镜像内为 Python 3.10），无需在宿主机安装其依赖。

## 构建

在 **项目根目录** 执行：

```bash
docker build -t pdf-extract-kit -f tools/docker/pdf-extract-kit/Dockerfile tools/docker/pdf-extract-kit
```

## 模型

镜像内不包含模型权重，需按 [PDF-Extract-Kit 文档](https://pdf-extract-kit.readthedocs.io/en/latest/get_started/pretrained_model.html) 下载到宿主机某目录，运行时挂载：

- 环境变量 `PDF_EXTRACT_KIT_MODELS_PATH` 指向该目录，agent-edu 会将其挂载为容器内 `/app/models`。

## 在 agent-edu 中使用

1. 设置 `PDF_EXTRACT_KIT_DOCKER_IMAGE=pdf-extract-kit`（或你构建的镜像名）。
2. 可选：设置 `PDF_EXTRACT_KIT_MODELS_PATH` 为模型目录绝对路径。
3. 调用 `export_pdf_to_md(pdf_path, out_dir, backend="pdf_extract_kit")` 或运行 `python tests/test_pdf_extract_kit.py`。

## 手动运行容器（调试用）

```bash
docker run --rm -v /path/to/images:/input -v /path/to/output:/output -e INPUT_DIR=/input -e OUTPUT_DIR=/output pdf-extract-kit
```

输入目录需为按页命名的图片（如 `0001.png`, `0002.png`），输出目录将生成 Markdown。
