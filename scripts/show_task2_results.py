"""
任务 2 展示用脚本：用 Rich 输出文档索引、结构报告与测试结果，便于截图或导出 HTML。
运行：在项目根目录执行 python scripts/show_task2_results.py
导出 HTML：python scripts/show_task2_results.py --html docs/task2/task2_results.html
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main() -> None:
    export_html = "--html" in sys.argv
    html_path = None
    if "--html" in sys.argv:
        idx = sys.argv.index("--html")
        if idx + 1 < len(sys.argv):
            html_path = Path(sys.argv[idx + 1])
        else:
            html_path = ROOT / "docs" / "task2" / "task2_results.html"

    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich import print as rprint
    except ImportError:
        print("请先安装 Rich: pip install rich")
        sys.exit(1)

    console = Console(record=bool(export_html), force_terminal=not export_html)
    if export_html and html_path:
        console.print(Panel("[bold cyan]任务 2：数据预处理与知识库 — 运行结果展示[/]", border_style="cyan"))

    # 1. 文档索引
    from src.preprocessing.doc_index import (
        build_doc_index,
        save_doc_index,
        analyze_md_structure,
    )
    results_dir = ROOT / "results"
    data_root = ROOT / "data" / "res.6-007-spring-2011"
    config_dir = ROOT / "config"
    index_path = config_dir / "doc_index.json"
    entries = build_doc_index(results_dir, data_root if data_root.is_dir() else None)
    if config_dir.is_dir() or config_dir.mkdir(parents=True, exist_ok=True):
        save_doc_index(entries, index_path)

    table = Table(title="文档索引 (config/doc_index.json)", show_header=True, header_style="bold magenta")
    table.add_column("doc_id", style="cyan")
    table.add_column("doc_type", style="green")
    table.add_column("lecture_index", justify="center")
    table.add_column("title", max_width=40, overflow="fold")
    table.add_column("related", style="dim")
    for e in entries:
        rel = []
        if e.get("related_lec"):
            rel.append(f"lec→{e['related_lec']}")
        if e.get("related_hw"):
            rel.append(f"hw→{e['related_hw']}")
        if e.get("related_sol"):
            rel.append(f"sol→{e['related_sol']}")
        table.add_row(
            e["doc_id"],
            e["doc_type"],
            str(e.get("lecture_index", "")),
            (e.get("title") or "")[:40],
            " ".join(rel) if rel else "-",
        )
    console.print(table)
    console.print(f"[green]已索引 {len(entries)} 个文档，已保存到 {index_path}[/]\n")

    # 2. 结构报告
    report = analyze_md_structure(entries)
    tbl2 = Table(title="文档结构统计 (前 6 个)", show_header=True, header_style="bold yellow")
    tbl2.add_column("file_name", max_width=28, overflow="fold")
    tbl2.add_column("doc_id", style="cyan")
    tbl2.add_column("doc_type", style="green")
    tbl2.add_column("字符数", justify="right")
    tbl2.add_column("行数", justify="right")
    tbl2.add_column("h1 / h2 / h3", justify="center")
    for r in report[:6]:
        h = r["headings"]
        tbl2.add_row(
            r["file_name"][:28],
            r["doc_id"],
            r["doc_type"],
            str(r["char_count"]),
            str(r["line_count"]),
            f"{h['h1']} / {h['h2']} / {h['h3']}",
        )
    console.print(tbl2)
    console.print()

    # 3. 测试结果
    console.print(Panel("单元测试 (pytest)", title="[bold]测试结果[/]", border_style="blue"))
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "tests/test_doc_index.py",
                "tests/test_md_loader.py",
                "tests/test_splitter.py",
                "tests/test_knowledge_graph.py",
                "-v", "--tb=no", "-q",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        out = result.stdout + result.stderr
        for line in out.splitlines():
            if "PASSED" in line:
                console.print(f"  [green]{line.strip()}[/]")
            elif "SKIPPED" in line:
                console.print(f"  [yellow]{line.strip()}[/]")
            elif "FAILED" in line:
                console.print(f"  [red]{line.strip()}[/]")
            elif "passed" in line or "skipped" in line:
                console.print(f"  [bold]{line.strip()}[/]")
    except Exception as e:
        console.print(f"  [red]运行 pytest 时出错: {e}[/]")
    console.print()

    if export_html and html_path:
        html_path.parent.mkdir(parents=True, exist_ok=True)
        console.save_html(str(html_path))
        console.print("[green]已导出 HTML 到[/]", str(html_path), "[green]，用浏览器打开后可截图或打印为 PDF。[/]")


if __name__ == "__main__":
    main()
