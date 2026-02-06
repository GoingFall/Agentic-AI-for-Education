# 知识图谱：Topic/Exercise 节点与 PREREQUISITE、COVERS 关系，Neo4j 导入
# 延迟导入，避免 python -m src.knowledge_graph.build 时触发 RuntimeWarning
def __getattr__(name: str):
    if name == "build_and_ingest_graph":
        from .build import build_and_ingest_graph
        return build_and_ingest_graph
    if name == "Topic":
        from .build import Topic
        return Topic
    if name == "Exercise":
        from .build import Exercise
        return Exercise
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["build_and_ingest_graph", "Topic", "Exercise"]
