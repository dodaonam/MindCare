from rag.ingest_pipeline import ingest_documents
from rag.index_builder import build_index

def main():
    print("\n[1/2] Ingesting documents...")
    nodes = ingest_documents()
    
    if not nodes:
        print("ERROR: No nodes created!")
        return
    
    print(f" Created {len(nodes)} nodes")
    
    print("\n[2/2] Building ChromaDB index...")
    build_index(nodes)
    
    print("\nINGEST COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print(f"- Nodes: {len(nodes)}")
    print(f"- ChromaDB: data/chroma/")
    print(f"- BM25 Pickle: data/nodes/nodes.pkl")
    print(f"- Pipeline Cache: data/cache/pipeline_cache.json")

if __name__ == "__main__":
    main()