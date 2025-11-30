from llama_index.core.tools import FunctionTool
from rag.citation_engine import query_dsm5_with_sources

# Store the last query sources for retrieval by the API
_last_query_sources: list[dict] = []

def get_last_sources() -> list[dict]:
    """
    Get the sources from the last DSM-5 query
    """
    return _last_query_sources.copy()

def clear_last_sources():
    """Clear the stored sources."""
    global _last_query_sources
    _last_query_sources = []

def dsm5_query_with_citations(query: str) -> str:
    """
    Query DSM-5 knowledge base and store sources for later retrieval
    """
    global _last_query_sources
    
    print(f"\n🔍 DSM5Query TOOL CALLED with query: {query}")
    
    # Query with citations
    result = query_dsm5_with_sources(query)
    
    # Store sources for API to retrieve
    _last_query_sources = result.get("sources", [])
    
    print(f"📚 Found {len(_last_query_sources)} sources")
    
    # Return just the answer for the agent
    return result.get("answer", "Không tìm thấy thông tin.")

def get_dsm5_tool() -> FunctionTool:
    """
    Return a FunctionTool for querying DSM-5 content with citations
    """
    tool = FunctionTool.from_defaults(
        fn=dsm5_query_with_citations,
        name="DSM5Query",
        description=(
            "Truy vấn kiến thức DSM-5 (Sổ tay Chẩn đoán và Thống kê Rối loạn Tâm thần) "
            "và trả lời bằng tiếng Việt. Sử dụng tool này khi cần thông tin về: "
            "tiêu chuẩn chẩn đoán, triệu chứng rối loạn tâm thần, phân loại bệnh, "
            "hoặc bất kỳ kiến thức chuyên môn nào về sức khỏe tâm thần. "
            "Tool sẽ trả về câu trả lời kèm trích dẫn từ DSM-5."
        ),
    )
    
    return tool