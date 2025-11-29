from dataclasses import dataclass
from llama_index.core import Settings
from llama_index.core.schema import NodeWithScore

from rag.hybrid_retriever import hybrid_retrieve_with_fallback, clear_retriever_cache
from rag.global_settings import (
    init_llm_settings,
    RERANK_TOP_N,
    RELEVANCE_THRESHOLD,
    MAX_SOURCES_RETURN,
)

RESPONSE_TEMPLATE_VI = """Dựa trên thông tin ngữ cảnh được cung cấp bên dưới, hãy trả lời câu hỏi.
Nếu câu trả lời không có trong ngữ cảnh, hãy nói "Tôi không tìm thấy thông tin này trong tài liệu DSM-5."

Ngữ cảnh:
{context_str}

Câu hỏi: {query_str}

Hãy trả lời bằng tiếng Việt, ngắn gọn và chính xác."""

FALLBACK_RESPONSE = "Tôi không tìm thấy thông tin liên quan trong tài liệu DSM-5. Bạn có thể mô tả chi tiết hơn hoặc hỏi về một chủ đề cụ thể về sức khỏe tâm thần không?"

@dataclass
class SourceInfo:
    """Information about a source citation"""
    text: str
    score: float
    source_file: str
    node_id: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text[:500] + "..." if len(self.text) > 500 else self.text,
            "score": round(self.score, 3) if self.score else 0.0,
            "source_file": self.source_file,
            "node_id": self.node_id,
        }

@dataclass 
class CitationResponse:
    """Response with citations"""
    answer: str
    sources: list[SourceInfo]
    is_fallback: bool = False  # True if no relevant results found
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "answer": self.answer,
            "sources": [s.to_dict() for s in self.sources],
            "is_fallback": self.is_fallback,
        }

def extract_sources_from_nodes(nodes: list[NodeWithScore]) -> list[SourceInfo]:
    """
    Extract source information from NodeWithScore list
    """
    sources = []
    
    for node in nodes:
        # Extract metadata
        metadata = node.node.metadata if hasattr(node.node, 'metadata') else {}
        source_file = metadata.get('file_name', metadata.get('source', 'DSM-5'))
        
        # Handle score which might be None
        score = 0.0
        if hasattr(node, 'score') and node.score is not None:
            score = float(node.score)
        
        source_info = SourceInfo(
            text=node.node.get_content() if hasattr(node.node, 'get_content') else str(node.node),
            score=score,
            source_file=source_file,
            node_id=node.node.node_id if hasattr(node.node, 'node_id') else "",
        )
        sources.append(source_info)
    
    return sources

def synthesize_response(query: str, nodes: list[NodeWithScore]) -> str:
    """
    Generate response from LLM using retrieved nodes as context.
    """
    init_llm_settings()
    
    # Build context from nodes
    context_parts = []
    for i, node in enumerate(nodes, 1):
        content = node.node.get_content() if hasattr(node.node, 'get_content') else str(node.node)
        context_parts.append(f"[{i}] {content}")
    
    context_str = "\n\n".join(context_parts)
    
    # Create prompt
    prompt = RESPONSE_TEMPLATE_VI.format(context_str=context_str, query_str=query)
    
    # Get response from LLM
    response = Settings.llm.complete(prompt)
    
    return str(response)

def query_with_citations(query: str) -> CitationResponse:
    """
    Query DSM-5 knowledge base using Hybrid Retrieval + Reranker
    """
    # Hybrid retrieval with reranking and fallback check
    nodes, should_fallback = hybrid_retrieve_with_fallback(
        query=query,
        top_n=RERANK_TOP_N,
        threshold=RELEVANCE_THRESHOLD,
    )
    
    # Handle fallback case
    if should_fallback or not nodes:
        return CitationResponse(
            answer=FALLBACK_RESPONSE,
            sources=[],
            is_fallback=True,
        )
    
    # Generate response with LLM
    answer = synthesize_response(query, nodes)
    
    # Extract sources
    sources = extract_sources_from_nodes(nodes)[:MAX_SOURCES_RETURN]
    
    return CitationResponse(
        answer=answer,
        sources=sources,
        is_fallback=False,
    )

def query_dsm5_with_sources(query: str) -> dict:
    """
    Query DSM-5 and return structured response with sources
    Main entry point for the agent tool
    """
    result = query_with_citations(query)
    return result.to_dict()

def reset_citation_engine():
    """Reset all cached instances"""
    clear_retriever_cache()
    print("Citation engine reset complete")