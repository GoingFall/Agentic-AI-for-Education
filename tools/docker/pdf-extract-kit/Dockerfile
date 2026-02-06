# PDF-Extract-Kit 运行环境（Python 3.10），供 agent-edu 在 Python 3.11 下通过 docker 调用
# 构建：在项目根目录执行 docker build -t pdf-extract-kit -f tools/docker/pdf-extract-kit/Dockerfile tools/docker/pdf-extract-kit
# 模型需单独下载并挂载到 /app/models，见 README

FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN git clone --depth 1 https://github.com/opendatalab/PDF-Extract-Kit.git .

# CPU 版依赖（GPU 可改用 requirements.txt）
RUN pip install --no-cache-dir -r requirements-cpu.txt

COPY entrypoint.py /entrypoint.py
ENV INPUT_DIR=/input
ENV OUTPUT_DIR=/output
ENTRYPOINT ["python", "/entrypoint.py"]
