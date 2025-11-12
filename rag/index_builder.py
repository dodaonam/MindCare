import os
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    Settings,
    load_index_from_storage,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from rag.global_settings import INDEX_STORAGE

os.makedirs(INDEX_STORAGE, exist_ok=True)

EMBEDDING_MODEL_NAME = "AITeamVN/Vietnamese_Embedding"

def get_embed_model():
    """Initialize and return the embedding model."""
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
    Settings.embed_model = embed_model
    return embed_model


def build_index(nodes):
    """
    Build a new vector index from processed nodes and persist it.
    """
    print("Building vector index...")

    embed_model = get_embed_model()
    storage = StorageContext.from_defaults()

    index = VectorStoreIndex(nodes, storage_context=storage, embed_model=embed_model)
    index.storage_context.persist(persist_dir=INDEX_STORAGE)

    print(f"Index successfully built and saved to {INDEX_STORAGE}")
    return index


def load_index():
    """
    Load an existing vector index from storage if available.
    """
    docstore_path = os.path.join(INDEX_STORAGE, "docstore.json")
    if not os.path.exists(docstore_path):
        print("No existing index found.")
        return None

    print("Loading existing index from storage...")
    embed_model = get_embed_model()
    storage = StorageContext.from_defaults(persist_dir=INDEX_STORAGE)
    index = load_index_from_storage(storage)
    print("Index loaded successfully.")
    return index


def get_or_build_index(nodes=None):
    """
    Loads index if it exists else builds a new one
    """
    index = load_index()
    if index:
        return index
    if nodes is None:
        raise ValueError("No index found and no nodes provided to build a new one.")
    return build_index(nodes)
