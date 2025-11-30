from typing import Optional
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.retrievers.bm25 import BM25Retriever

from rag.index_builder import load_index, get_embed_model
from rag.ingest_pipeline import load_nodes
from rag.global_settings import (
    VECTOR_TOP_K,
    BM25_TOP_K, 
    FUSION_TOP_K,
    RERANKER_MODEL,
    RERANK_TOP_N,
    RELEVANCE_THRESHOLD,
)

# Cached instances
_hybrid_retriever: Optional[QueryFusionRetriever] = None
_reranker: Optional[SentenceTransformerRerank] = None
_bm25_retriever: Optional[BM25Retriever] = None


def get_bm25_retriever() -> BM25Retriever:
    """Get or create BM25 retriever from saved nodes"""
    global _bm25_retriever
    
    if _bm25_retriever is not None:
        return _bm25_retriever
    
    nodes = load_nodes()
    _bm25_retriever = BM25Retriever.from_defaults(
        nodes=nodes,
        similarity_top_k=BM25_TOP_K,
    )
    
    print(f"BM25 retriever initialized with {len(nodes)} nodes")
    return _bm25_retriever


def get_hybrid_retriever() -> QueryFusionRetriever:
    """
    Get or create Hybrid Retriever combining Vector + BM25 with RRF fusion
    """
    global _hybrid_retriever
    
    if _hybrid_retriever is not None:
        return _hybrid_retriever
    
    # Load vector index
    index = load_index()
    if index is None:
        raise ValueError("No ChromaDB index found. Please run ingestion first.")
    
    # Create vector retriever
    vector_retriever = index.as_retriever(similarity_top_k=VECTOR_TOP_K)
    
    # Create BM25 retriever
    bm25_retriever = get_bm25_retriever()
    
    # Create hybrid retriever with Reciprocal Rank Fusion
    _hybrid_retriever = QueryFusionRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        mode="reciprocal_rerank",  # RRF fusion
        similarity_top_k=FUSION_TOP_K,
        num_queries=1,  # No query expansion
        use_async=False,
    )
    
    print("Hybrid retriever initialized (Vector + BM25 + RRF)")
    return _hybrid_retriever


def get_reranker() -> SentenceTransformerRerank:
    """Get or create BGE Reranker"""
    global _reranker
    
    if _reranker is not None:
        return _reranker
    
    _reranker = SentenceTransformerRerank(
        model=RERANKER_MODEL,
        top_n=RERANK_TOP_N,
        keep_retrieval_score=True,  # Keep original scores for debugging
    )
    
    print(f"Reranker initialized: {RERANKER_MODEL}")
    return _reranker


def hybrid_retrieve_with_rerank(
    query: str,
    top_n: Optional[int] = None,
) -> list[NodeWithScore]:
    """
    Perform hybrid retrieval with reranking
    """
    if top_n is None:
        top_n = RERANK_TOP_N
    
    # Hybrid retrieval (Vector + BM25 + RRF)
    retriever = get_hybrid_retriever()
    nodes = retriever.retrieve(query)
    
    if not nodes:
        print("No nodes retrieved from hybrid search")
        return []
    
    print(f"Hybrid retrieval: {len(nodes)} candidates")
    
    # Rerank
    reranker = get_reranker()
    query_bundle = QueryBundle(query_str=query)
    reranked_nodes = reranker.postprocess_nodes(nodes, query_bundle)
    
    print(f"After reranking: {len(reranked_nodes)} results")
    
    return reranked_nodes[:top_n]


def hybrid_retrieve_with_fallback(
    query: str,
    top_n: Optional[int] = None,
    threshold: Optional[float] = None,
) -> tuple[list[NodeWithScore], bool]:
    """
    Perform hybrid retrieval with reranking and fallback check
    """
    if threshold is None:
        threshold = RELEVANCE_THRESHOLD
    
    nodes = hybrid_retrieve_with_rerank(query, top_n)
    
    # Check if we should fallback
    if not nodes:
        return [], True
    
    # Check if best result is below threshold
    best_score = nodes[0].score if nodes[0].score is not None else 0.0
    
    if best_score < threshold:
        print(f"Best score ({best_score:.3f}) below threshold ({threshold})")
        return nodes, True
    
    # Filter nodes below threshold
    relevant_nodes = [n for n in nodes if n.score is not None and n.score >= threshold]
    
    if not relevant_nodes:
        return nodes, True
    
    print(f"Found {len(relevant_nodes)} relevant nodes (score >= {threshold})")
    return relevant_nodes, False


def clear_retriever_cache():
    """Clear all cached retriever instances"""
    global _hybrid_retriever, _reranker, _bm25_retriever
    _hybrid_retriever = None
    _reranker = None
    _bm25_retriever = None
    print("Retriever cache cleared")
