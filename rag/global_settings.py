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

def init_llm_settings():
    """Initialize global LLM settings once across the system."""
    Settings.llm = Groq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=GROQ_API_KEY,
        temperature=0.6,
    )