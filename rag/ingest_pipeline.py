import os
import asyncio
import time
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.core.extractors import SummaryExtractor
from llama_index.core import Settings
from rag.global_settings import FILES_PATH, CACHE_FILE, GROQ_API_KEY

os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

Settings.llm = Groq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=GROQ_API_KEY,
    temperature=0.6,
)

class SequentialSummaryExtractor(SummaryExtractor):
    """SummaryExtractor that runs sequentially with rate limiting."""
    def __init__(self, rate_per_minute: int = 30, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "min_interval", 60.0 / rate_per_minute)
        object.__setattr__(self, "_last_call", 0.0)

    async def aextract(self, nodes):
        results = []
        for node in nodes:
            elapsed = time.time() - self._last_call
            wait_time = self.min_interval - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self._last_call = time.time()
            res = await super().aextract([node])
            results.extend(res)
        return results

def ingest_documents():
    print("Loading documents...")
    documents = SimpleDirectoryReader(input_files=FILES_PATH).load_data()

    try:
        cache = IngestionCache.from_persist_path(CACHE_FILE)
        print("Cache file found. Using existing cache.")
    except Exception:
        cache = None
        print("No cache file found. Creating a new pipeline.")

    embed_model = HuggingFaceEmbedding(model_name="AITeamVN/Vietnamese_Embedding")

    semantic_parser = SemanticSplitterNodeParser(
        buffer_size=1,
        breakpoint_percentile_threshold=95,
        embed_model=embed_model,
    )

    pipeline = IngestionPipeline(
        transformations=[
            semantic_parser,
            # SequentialSummaryExtractor(rate_per_minute=30, summaries=["self"]),
            embed_model,
        ],
        cache=cache,
    )

    nodes = pipeline.run(documents=documents)
    pipeline.cache.persist(CACHE_FILE)
    print(f"Created {len(nodes)} nodes from DSM-5 documents.")
    return nodes
