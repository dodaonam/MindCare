from llama_index.core import Settings
from llama_index.llms.groq import Groq
from rag.index_builder import load_index
from rag.global_settings import GROQ_API_KEY

_query_engine = None

def init_llm():
    Settings.llm = Groq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=GROQ_API_KEY,
        temperature=0.6,
        )

def get_query_engine():
    global _query_engine
    if _query_engine is not None:
        return _query_engine

    init_llm()
    index = load_index()
    if index is None:
        raise ValueError("No ChromaDB index found. Please ingest again.")

    _query_engine = index.as_query_engine(
        similarity_top_k=5,
        response_mode="compact"
    )

    print("Query engine initialized successfully.")
    return _query_engine