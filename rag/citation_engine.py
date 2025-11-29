from typing import Optional
from dataclasses import dataclass
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.base.response.schema import Response
from rag.index_builder import load_index
from rag.global_settings import init_llm_settings

CITATION_CHUNK_SIZE = 512  # Size of citation chunks
SIMILARITY_TOP_K = 5  # Number of similar documents to retrieve
MAX_SOURCES_RETURN = 3  # Maximum number of sources to return
CITATION_QA_TEMPLATE_VI = """
Dựa trên thông tin ngữ cảnh được cung cấp bên dưới, hãy trả lời câu hỏi.
Nếu câu trả lời không có trong ngữ cảnh, hãy nói "Tôi không tìm thấy thông tin này trong tài liệu DSM-5."

Ngữ cảnh:
{context_str}

Câu hỏi: {query_str}

Hãy trả lời bằng tiếng Việt và trích dẫn nguồn bằng cách sử dụng [số] cho mỗi đoạn tham khảo.
"""

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
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "answer": self.answer,
            "sources": [s.to_dict() for s in self.sources],
        }

_citation_engine: Optional[CitationQueryEngine] = None

def get_citation_query_engine() -> CitationQueryEngine:
    """
    Get or create a CitationQueryEngine instance
    """
    global _citation_engine
    
    if _citation_engine is not None:
        return _citation_engine
    
    init_llm_settings()
    
    index = load_index()
    if index is None:
        raise ValueError("No ChromaDB index found. Please run ingestion first.")
    
    # Create CitationQueryEngine
    _citation_engine = CitationQueryEngine.from_args(
        index=index,
        similarity_top_k=SIMILARITY_TOP_K,
        citation_chunk_size=CITATION_CHUNK_SIZE,
    )
    
    print("Citation query engine initialized successfully.")
    return _citation_engine

def extract_sources(response) -> list[SourceInfo]:
    """
    Extract source information from a query response
    """
    sources = []
    
    if not hasattr(response, 'source_nodes') or not response.source_nodes:
        return sources
    
    for node in response.source_nodes:
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

def query_with_citations(query: str) -> CitationResponse:
    """
    Query the DSM-5 knowledge base and return answer with citations
    """
    engine = get_citation_query_engine()
    
    # Execute query
    response = engine.query(query)
    
    # Extract sources and limit to MAX_SOURCES_RETURN
    sources = extract_sources(response)[:MAX_SOURCES_RETURN]
    
    return CitationResponse(
        answer=str(response),
        sources=sources,
    )

def query_dsm5_with_sources(query: str) -> dict:
    """
    Query DSM-5 and return structured response with sources
    """
    result = query_with_citations(query)
    return result.to_dict()