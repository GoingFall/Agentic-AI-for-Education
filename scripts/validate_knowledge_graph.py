"""
2.4.3 知识图谱验证脚本：先修链合理性、概念覆盖完整性；可选创建索引。
供 CI 或手动运行。需配置 NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from dotenv import load_dotenv
load_dotenv(root / ".env")

from neo4j import GraphDatabase

try:
    from src.knowledge_graph.validate import (
        validate_prerequisite_chain,
        validate_concept_coverage,
        ensure_indexes,
        run_validation,
    )
except ImportError:
    from knowledge_graph.validate import (
        validate_prerequisite_chain,
        validate_concept_coverage,
        ensure_indexes,
        run_validation,
    )


def main() -> None:
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        print("NEO4J_PASSWORD 未设置，跳过验证。")
        return
    create_indexes = "--index" in sys.argv or "-i" in sys.argv

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            if create_indexes:
                ensure_indexes(session)
                print("索引已创建或已存在。")
            out = run_validation(session)
            prereq = out["prerequisite_chain"]
            concept = out["concept_coverage"]
            print("先修链:", "通过" if prereq["ok"] else "失败", prereq.get("problems", []))
            print("概念覆盖:", "通过" if concept["ok"] else "失败", concept.get("details", {}))
    finally:
        driver.close()


if __name__ == "__main__":
    main()
