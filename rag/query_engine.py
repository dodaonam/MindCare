from rag.index_builder import load_index
from rag.global_settings import init_llm_settings

_query_engine = None

def get_query_engine():
    global _query_engine
    if _query_engine is not None:
        return _query_engine

    init_llm_settings()
    index = load_index()
    if index is None:
        raise ValueError("No ChromaDB index found. Please ingest again.")

    _query_engine = index.as_query_engine(
        similarity_top_k=5,
        response_mode="compact"
    )

    print("Query engine initialized successfully.")
    return _query_engine