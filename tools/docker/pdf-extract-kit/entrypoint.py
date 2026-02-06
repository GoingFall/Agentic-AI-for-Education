"""
容器内入口：根据环境变量 INPUT_DIR / OUTPUT_DIR 生成 config 并执行 pdf2markdown。
供 agent-edu 通过 docker run 调用，宿主机 Python 3.11 无需安装 PDF-Extract-Kit 依赖。
"""
import os
import subprocess
import sys

import yaml

APP_ROOT = "/app"
DEFAULT_CONFIG = os.path.join(APP_ROOT, "project", "pdf2markdown", "configs", "pdf2markdown.yaml")
RUN_SCRIPT = os.path.join(APP_ROOT, "project", "pdf2markdown", "scripts", "run_project.py")


def main():
    input_dir = os.environ.get("INPUT_DIR", "/input")
    output_dir = os.environ.get("OUTPUT_DIR", "/output")

    with open(DEFAULT_CONFIG, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    config["inputs"] = input_dir
    config["outputs"] = output_dir
    config["merge2markdown"] = True

    config_path = "/tmp/pdf2markdown_config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    os.chdir(APP_ROOT)
    env = os.environ.copy()
    env["PYTHONPATH"] = APP_ROOT
    ret = subprocess.run(
        [sys.executable, RUN_SCRIPT, "--config", config_path],
        cwd=APP_ROOT,
        env=env,
    )
    sys.exit(ret.returncode)


if __name__ == "__main__":
    main()
