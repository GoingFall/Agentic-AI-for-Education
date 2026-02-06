"""
Chroma 向量库初始化测试：创建/连接 Chroma 并执行一次简单 add + query。
运行：在项目根目录执行 python tests/test_chroma_init.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(ROOT / "chroma_db"))
TEST_COLLECTION = "test_connection"


def main():
    try:
        import chromadb
    except ImportError:
        print("ERROR: chromadb not installed. Run: pip install chromadb")
        sys.exit(1)
    client = None
    try:
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        col = client.get_or_create_collection(TEST_COLLECTION, metadata={"description": "connection test"})
        col.add(
            ids=["id1"],
            documents=["Chroma connection test document"],
            metadatas=[{"source": "test"}],
        )
        out = col.query(query_texts=["connection test"], n_results=1)
        if out and out["ids"] and out["ids"][0]:
            print("Chroma initialization test passed.")
        else:
            print("Chroma initialization test: add/query completed but result unexpected.")
        client.delete_collection(TEST_COLLECTION)
    except Exception as e:
        print("Chroma initialization test failed:", repr(e))
        sys.exit(1)
    finally:
        if client:
            try:
                client.delete_collection(TEST_COLLECTION)
            except Exception:
                pass


if __name__ == "__main__":
    main()
