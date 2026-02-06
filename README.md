# Agentic AI for Science & Engineering Education

HackaStone 2026 团队项目：面向《信号与系统》的答疑 + 练习推荐教育 AI 助手。方案与技术栈见 [discussion.md](docs/discussion.md)。

## 环境

- **Conda**：项目使用环境名 `agent-edu`。首次搭建执行：
  ```bash
  conda create -n agent-edu python=3.11
  conda activate agent-edu
  pip install -r requirements.txt
  ```
  国内镜像可选：`pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`
- **日常开发**：启动前执行 `conda activate agent-edu` 即可。

## 环境变量

在项目根目录创建 `.env`（可复制 `.env.example` 后填入真实值），配置：

| 变量 | 必填 | 说明 |
|------|------|------|
| `OPENROUTER_API_KEY` | 是 | [OpenRouter Keys](https://openrouter.ai/keys) 创建后填入，用于 LLM 调用 |
| `OPENROUTER_MODEL` | 否 | 默认 `openai/gpt-3.5-turbo` |
| `NEO4J_URI` | 否 | Neo4j 连接地址，默认 `bolt://localhost:7687` |
| `NEO4J_USER` | 否 | Neo4j 用户名，默认 `neo4j` |
| `NEO4J_PASSWORD` | 否 | Neo4j 密码，未设置时 Neo4j 连接测试会跳过 |
| `CHROMA_PERSIST_DIR` | 否 | Chroma 持久化目录，默认项目下 `chroma_db` |

## PDF 解析（可选：PDF-Extract-Kit）

默认使用 **PyMuPDF** 将 PDF 按页提取文本并导出为 Markdown（见 `src/preprocessing/pdf_parser.py`）。若希望使用 [PDF-Extract-Kit](https://github.com/opendatalab/PDF-Extract-Kit) 的版面检测 + OCR + 公式识别流程（质量更高、依赖与模型较重），可用 **Docker**（推荐，与 Python 3.11 兼容）或 **本地安装**。

### 方式一：Docker（推荐，宿主机保持 Python 3.11）

1. 构建镜像（在项目根目录执行）：
   ```bash
   docker build -t pdf-extract-kit -f tools/docker/pdf-extract-kit/Dockerfile tools/docker/pdf-extract-kit
   ```
2. 按 [PDF-Extract-Kit 文档](https://pdf-extract-kit.readthedocs.io/en/latest/get_started/pretrained_model.html) 下载模型到某目录（如 `D:\models\pdf-extract-kit`）。
3. 设置环境变量后调用：
   ```powershell
   $env:PDF_EXTRACT_KIT_DOCKER_IMAGE = "pdf-extract-kit"
   $env:PDF_EXTRACT_KIT_MODELS_PATH = "D:\models\pdf-extract-kit"   # 可选，挂载模型目录
   python tests/test_pdf_extract_kit.py
   ```
   或在代码中：`export_pdf_to_md(pdf_path, out_dir, backend="pdf_extract_kit")`。

### 方式二：本地安装（需 Python 3.10 环境）

1. 克隆并安装 PDF-Extract-Kit（建议 Python 3.10）：
   ```bash
   git clone https://github.com/opendatalab/PDF-Extract-Kit.git tools/PDF-Extract-Kit
   cd tools/PDF-Extract-Kit
   pip install -r requirements.txt   # 或 requirements-cpu.txt
   ```
2. 按官方文档下载所需模型权重。
3. 设置 `PDF_EXTRACT_KIT_ROOT` 指向克隆目录，再使用 `backend="pdf_extract_kit"`。  
   （未设置 `PDF_EXTRACT_KIT_DOCKER_IMAGE` 时，会退回到本地 `PDF_EXTRACT_KIT_ROOT`。）

## 验证外部服务连接

在激活 `agent-edu` 环境后，在项目根目录执行：

1. **OpenRouter**：
   ```bash
   python tests/test_openrouter_connection.py
   ```
2. **Neo4j**（需已配置 `NEO4J_*` 并启动 Neo4j）：
   ```bash
   python tests/test_neo4j_connection.py
   ```
3. **Chroma**：
   ```bash
   python tests/test_chroma_init.py
   ```

## 仓库

[https://github.com/GoingFall/Agentic-AI-for-Education](https://github.com/GoingFall/Agentic-AI-for-Education)
