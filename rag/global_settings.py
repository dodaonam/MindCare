import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.core import Settings

load_dotenv()

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Paths
CACHE_FILE = "data/cache/pipeline_cache.json"
STORAGE_PATH = "data/ingestion_storage/"
FILES_PATH = [f"{STORAGE_PATH}/dsm-5-sach-tieng-viet.docx"]
ASSESSMENT_DIR = "data/assessments"
CHROMA_DIR = "data/chroma/"
NODES_FILE = "data/nodes/nodes.pkl"

# Hybrid Search
VECTOR_TOP_K = 10          # Number of results from vector search
BM25_TOP_K = 10            # Number of results from BM25 search
FUSION_TOP_K = 15          # Number of results after RRF fusion

# Reranker
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"
RERANK_TOP_N = 5           # Final number of results after reranking

# Fallback
RELEVANCE_THRESHOLD = 0.6  # reranker score

# Embedding Model
EMBEDDING_MODEL_NAME = "AITeamVN/Vietnamese_Embedding"

# Citation
MAX_SOURCES_RETURN = 5  # Maximum number of sources to return in response

# Memory
TOKEN_LIMIT = 10000  # Total tokens for memory
TOKEN_FLUSH_SIZE = 1000  # Tokens to flush when limit exceeded
CHAT_HISTORY_TOKEN_RATIO = 0.7  # 70% for chat history, 30% for memory blocks

def init_llm_settings():
    """Initialize global LLM settings once across the system."""
    Settings.llm = Groq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=GROQ_API_KEY,
        temperature=0.6,
    )