# Agentic AI for Science & Engineering Education

HackaStone 2026 团队项目：面向《信号与系统》的答疑 + 练习推荐教育 AI 助手。方案与技术栈见 [discussion.md](discussion.md)。

## 环境

- **Conda**：项目使用环境名 `agent-edu`。启动开发前执行：
  ```bash
  conda activate agent-edu
  ```
- **依赖**：在激活环境后安装：
  ```bash
  pip install -r requirements.txt
  ```
  国内镜像可选：`pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`

## LLM 接入（OpenRouter）

首版使用 [OpenRouter](https://openrouter.ai/) API，模型可换、便于演示。在项目根目录创建 `.env`（可复制 `.env.example`），配置：

- `OPENROUTER_API_KEY`：在 [OpenRouter Keys](https://openrouter.ai/keys) 创建后填入。
- 可选 `OPENROUTER_MODEL`：默认 `openai/gpt-3.5-turbo`。

**连接测试**：在激活 `agent-edu` 环境后执行：

```bash
python test/test_openrouter_connection.py
```

## 仓库

[https://github.com/GoingFall/Agentic-AI-for-Education](https://github.com/GoingFall/Agentic-AI-for-Education)
