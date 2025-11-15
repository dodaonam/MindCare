from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.groq import Groq
from llama_index.core import Settings
from rag.agent_tools import get_dsm5_tool, get_safety_tool
from rag.global_settings import GROQ_API_KEY

SYSTEM_PROMPT = """
Bạn là một Trợ lý AI hỗ trợ sức khỏe tâm thần. Nhiệm vụ của bạn:

1. Giao tiếp với giọng điệu nhẹ nhàng, tôn trọng, hỗ trợ và không phán xét.
2. Thu thập và làm rõ thông tin khi người dùng mô tả vấn đề tâm lý.
3. Khi cần kiến thức chuyên môn, hãy sử dụng tool "DSM5Query" để truy vấn thông tin dựa trên DSM-5.
4. Không được đưa ra chẩn đoán y khoa chính thức. Chỉ được cung cấp phân tích sơ bộ hoặc hướng dẫn an toàn.
5. Với các dấu hiệu nguy cơ (tự hại, tuyệt vọng, ý định làm đau bản thân), hãy phản hồi khẩn cấp và hướng người dùng tìm sự giúp đỡ ngay lập tức.
6. Giữ nội dung ngắn gọn, dễ hiểu, và luôn hỗ trợ lấy thêm thông tin từ người dùng.
7. Khi dùng tool, chỉ truy vấn đúng ý, không mở rộng quá mức.

Mục tiêu: hỗ trợ người dùng hiểu rõ hơn về triệu chứng, cung cấp thông tin đáng tin cậy và khuyến khích họ tìm hỗ trợ từ chuyên gia khi cần thiết.
"""

_agent = None

def get_agent():
    """
    Return a cached instance of the mental health agent.
    """
    global _agent
    if _agent is not None:
        return _agent

    Settings.llm = Groq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=GROQ_API_KEY,
        temperature=0.6,
    )

    tools = [get_dsm5_tool(), get_safety_tool()]

    _agent = FunctionAgent(
        name="MentalHealthAgent",
        description="Trợ lý AI hỗ trợ sức khỏe tâm thần, sử dụng DSM-5 qua RAG.",
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        verbose=True,
    )

    print("Agent initialized successfully.")
    return _agent