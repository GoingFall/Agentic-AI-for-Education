# Agent 工具：RAG 检索、知识图谱查询

from .rag import rag_retrieve, retrieve_documents
from .graph import (
    graph_query_next_topic,
    graph_query_covers_exercises,
    graph_query_concept_relations,
    graph_query_concept_depends,
    graph_validate_path,
    get_all_graph_tools,
)


def get_all_tools():
    """返回全局工具列表（RAG + 图谱），供 Skill 按 allowed_tools 筛选后传入 Agent。"""
    return [rag_retrieve] + get_all_graph_tools()


__all__ = [
    "rag_retrieve",
    "retrieve_documents",
    "graph_query_next_topic",
    "graph_query_covers_exercises",
    "graph_query_concept_relations",
    "graph_query_concept_depends",
    "graph_validate_path",
    "get_all_graph_tools",
    "get_all_tools",
]
