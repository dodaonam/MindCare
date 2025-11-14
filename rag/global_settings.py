import os
from dotenv import load_dotenv

load_dotenv()

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Paths
CACHE_FILE = "data/cache/pipeline_cache.json"
STORAGE_PATH = "data/ingestion_storage/"
INDEX_STORAGE = "data/index_storage/"
FILES_PATH = [f"{STORAGE_PATH}/dsm-5-sach-tieng-viet.docx"]
DATASET_PATH = "test/eval_dataset.json"
OUTPUT_FILE = "test/evaluate_output.txt"