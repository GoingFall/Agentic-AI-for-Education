"""
Neo4j 连接测试：从 .env 读取 NEO4J_URI/USER/PASSWORD，验证数据库连通性。
运行：在项目根目录执行 python tests/test_neo4j_connection.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


def main():
    if not NEO4J_PASSWORD:
        print("SKIP: NEO4J_PASSWORD not set. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env to test Neo4j.")
        return
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("ERROR: neo4j package not installed. Run: pip install neo4j")
        sys.exit(1)
    driver = None
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        with driver.session() as session:
            result = session.run("RETURN 1 AS n")
            row = result.single()
            if row and row["n"] == 1:
                print("Neo4j connection test passed.")
            else:
                print("Neo4j connection test: connectivity OK but query returned unexpected result.")
    except Exception as e:
        print("Neo4j connection test failed:", repr(e))
        print("Tip: Start Neo4j (e.g. Docker) and set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env.")
        sys.exit(1)
    finally:
        if driver:
            driver.close()


if __name__ == "__main__":
    main()
