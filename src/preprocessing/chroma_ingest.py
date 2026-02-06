"""
将 results/*.md 经文档索引与切片后向量化并写入 Chroma。
对应任务 2.3.3：向量化并存储到 Chroma。
使用 Chroma 默认嵌入（或可选的 LangChain Embeddings），集合名 course_docs。
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import List

from .doc_index import build_doc_index, load_doc_index, DocEntry
from .splitter import slice_document, chunk_metadata_for_chroma, ChunkWithMeta
from .dedup import dedup_chunks

COLLECTION_NAME = "course_docs"


def _ensure_chroma_metadata(meta: dict) -> dict:
    """Chroma 要求 metadata 值为 str、int、float 或 bool；列表仅部分版本支持。确保所有值为标量。"""
    out = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = str(v)
    return out


def ingest_results_to_chroma(
    results_dir: Path,
    data_root: Path | None,
    persist_dir: str | None = None,
    index_path: Path | None = None,
    *,
    use_langchain_embeddings: bool = False,
    dedup_before_ingest: bool = False,
) -> tuple[int, str]:
    """
    从 results_dir 的 .md 构建索引、切片、写入 Chroma。
    返回 (写入的切片数, 集合名)。
    persist_dir: Chroma 持久化目录，默认从环境变量 CHROMA_PERSIST_DIR 或项目 chroma_db 读取。
    index_path: 若提供则从该 JSON 加载文档索引，否则从 results_dir + data_root 构建。
    use_langchain_embeddings: 若 True 且已配置，使用 LangChain Embeddings；否则使用 Chroma 默认嵌入。
    dedup_before_ingest: 若 True，写入前按文本 hash 去重（3.3.1）。
    """
    results_dir = Path(results_dir)
    persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", str(results_dir.parent / "chroma_db"))
    if index_path and Path(index_path).is_file():
        entries = load_doc_index(Path(index_path))
    else:
        entries = build_doc_index(results_dir, data_root)

    all_chunks: List[ChunkWithMeta] = []
    for e in entries:
        path = Path(e["file_path"])
        if not path.is_file():
            continue
        chunks = slice_document(path, e)
        all_chunks.extend(chunks)

    if dedup_before_ingest and all_chunks:
        all_chunks = dedup_chunks(all_chunks, method="hash")

    if not all_chunks:
        return 0, COLLECTION_NAME

    try:
        import chromadb
    except ImportError:
        raise RuntimeError("chromadb not installed. Run: pip install chromadb")

    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(COLLECTION_NAME, metadata={"description": "course docs RAG"})

    ids = [str(uuid.uuid4()) for _ in all_chunks]
    documents = [c["content"] for c in all_chunks]
    metadatas = [_ensure_chroma_metadata(chunk_metadata_for_chroma(c)) for c in all_chunks]

    if use_langchain_embeddings:
        try:
            from langchain_openai import OpenAIEmbeddings
            emb = OpenAIEmbeddings()
            embeddings = emb.embed_documents(documents)
            collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        except Exception:
            # 回退：不传 embeddings，让 Chroma 用默认
            collection.add(ids=ids, documents=documents, metadatas=metadatas)
    else:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    return len(all_chunks), COLLECTION_NAME


if __name__ == "__main__":
    import sys
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    os.chdir(root)
    from dotenv import load_dotenv
    load_dotenv(root / ".env")

    results_dir = root / "results"
    data_root = root / "data" / "res.6-007-spring-2011"
    index_path = root / "config" / "doc_index.json"
    n, name = ingest_results_to_chroma(results_dir, data_root, index_path=index_path)
    print(f"Ingested {n} chunks into collection '{name}'.")
