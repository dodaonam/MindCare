from llama_index.core.tools import QueryEngineTool
from llama_index.core.tools import FunctionTool
from rag.query_engine import get_query_engine
from rag.safety import detect_safety_issue

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

def get_safety_tool():
    """
    Return a FunctionTool that evaluates user input for safety risks.
    """
    tool =  FunctionTool.from_defaults(
        fn=detect_safety_issue,
        name="SafetyTool",
        description="Kiểm tra nguy cơ (tự hại, tuyệt vọng, bạo lực). Trả về level, crisis_matches và warning_matches."
    )

    return tool