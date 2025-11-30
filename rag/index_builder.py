import os
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from rag.global_settings import CHROMA_DIR, EMBEDDING_MODEL_NAME

os.makedirs(CHROMA_DIR, exist_ok=True)

def get_embed_model():
    """Initialize and return the embedding model."""
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
    Settings.embed_model = embed_model
    return embed_model

def build_index(nodes):
    print("Building ChromaDB index...")

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection("dsm5_collection")

    vector_store = ChromaVectorStore(chroma_collection=collection)

    embed_model = get_embed_model()
    storage = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex(
        nodes,
        storage_context=storage,
        embed_model=embed_model
    )

    print(f"Chroma index created at {CHROMA_DIR}")
    return index

def load_index():
    try:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        collection = client.get_or_create_collection("dsm5_collection")

        if collection.count() == 0:
            print("Chroma collection empty — no index to load.")
            return None

        vector_store = ChromaVectorStore(chroma_collection=collection)
        embed_model = get_embed_model()

        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embed_model
        )

        print("Chroma index loaded successfully.")
        return index

    except Exception as e:
        print("Failed to load Chroma index:", e)
        return None

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
