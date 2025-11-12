from rag.ingest_pipeline import ingest_documents
from rag.index_builder import get_or_build_index

if __name__ == "__main__":
    try:
        # Ingest documents (split, summarize, embed)
        nodes = ingest_documents()
        if not nodes:
            raise ValueError("No nodes were created during ingestion.")

        # Load or build vector index
        index = get_or_build_index(nodes)

        print("Pipeline completed successfully.")
        print(f"Total nodes processed: {len(nodes)}")
    except Exception as e:
        print(f"Pipeline failed: {e}")
