from llama_index.core.tools import QueryEngineTool
from llama_index.core.tools import FunctionTool
from rag.query_engine import get_query_engine

def get_dsm5_tool():
    """
    Return a QueryEngineTool for querying DSM-5 content.
    """
    qe = get_query_engine()

    tool = QueryEngineTool.from_defaults(
        query_engine=qe,
        name="DSM5Query",
        description="Truy vấn kiến thức DSM-5 và trả lời bằng tiếng Việt. Sử dụng cho việc phân tích triệu chứng và hỗ trợ đánh giá sức khỏe tâm thần.",
        )

    return tool