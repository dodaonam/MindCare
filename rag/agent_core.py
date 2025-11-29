from typing import Optional
from llama_index.core.agent.workflow import FunctionAgent
from rag.agent_tools import get_dsm5_tool, clear_last_sources
from rag.global_settings import init_llm_settings
from rag.memory import get_memory, Memory

SYSTEM_PROMPT = """
Bạn là một Trợ lý AI hỗ trợ sức khỏe tâm thần. Nhiệm vụ của bạn:

1. Giao tiếp với giọng điệu nhẹ nhàng, tôn trọng, hỗ trợ và không phán xét.
2. Thu thập và làm rõ thông tin khi người dùng mô tả vấn đề tâm lý.
3. Khi cần kiến thức chuyên môn, hãy sử dụng tool "DSM5Query" để truy vấn thông tin dựa trên DSM-5.
4. Không được đưa ra chẩn đoán y khoa chính thức. Chỉ được cung cấp phân tích sơ bộ hoặc hướng dẫn an toàn.
5. Với các dấu hiệu nguy cơ (tự hại, tuyệt vọng, ý định làm đau bản thân), hãy phản hồi khẩn cấp và hướng người dùng tìm sự giúp đỡ ngay lập tức.
6. Giữ nội dung ngắn gọn, dễ hiểu, và luôn hỗ trợ lấy thêm thông tin từ người dùng.
7. Khi dùng tool, chỉ truy vấn đúng ý, không mở rộng quá mức.
8. QUAN TRỌNG: Nhớ và sử dụng các thông tin người dùng đã chia sẻ trong cuộc trò chuyện (như tên, tuổi, tình trạng) để cá nhân hóa phản hồi.

Mục tiêu: hỗ trợ người dùng hiểu rõ hơn về triệu chứng, cung cấp thông tin đáng tin cậy và khuyến khích họ tìm hỗ trợ từ chuyên gia khi cần thiết.
"""

# Cache: agent and memory by session_id
_agent_cache: dict[str, FunctionAgent] = {}
_memory_cache: dict[str, Memory] = {}

def get_agent(session_id: Optional[str] = None) -> tuple[FunctionAgent, str, Memory]:
    """
    Return a cached instance of the mental health agent
    """
    global _agent_cache, _memory_cache
    
    init_llm_settings()
    
    # Get or create memory (this also generates session_id if needed)
    memory, session_id = get_memory(session_id)
    
    # Cache memory
    _memory_cache[session_id] = memory
    
    # Return cached agent if exists for this session
    if session_id in _agent_cache:
        return _agent_cache[session_id], session_id, memory
    
    # Create tools
    tools = [get_dsm5_tool()]
    
    # Create new agent (memory is passed to run(), not constructor)
    agent = FunctionAgent(
        name="MentalHealthAgent",
        description="Trợ lý AI hỗ trợ sức khỏe tâm thần, sử dụng DSM-5 qua RAG.",
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        verbose=False,
    )
    
    # Cache the agent
    _agent_cache[session_id] = agent
    
    print(f"Agent initialized for session: {session_id}")
    return agent, session_id, memory

async def run_agent(message: str, session_id: Optional[str] = None) -> tuple[str, str]:
    """
    Run the agent with memory support
    """
    # Get agent and memory
    agent, session_id, memory = get_agent(session_id)
    
    # Run agent with memory
    response = await agent.run(user_msg=message, memory=memory)
    
    return str(response), session_id

def clear_agent_session(session_id: str) -> bool:
    """
    Clear agent and memory for a specific session
    """
    from rag.memory import clear_memory
    
    cleared = False
    
    if session_id in _agent_cache:
        del _agent_cache[session_id]
        cleared = True
    
    if session_id in _memory_cache:
        del _memory_cache[session_id]
        cleared = True
        
    if clear_memory(session_id):
        cleared = True
        
    # Clear any stored sources
    clear_last_sources()
    
    if cleared:
        print(f"Session cleared: {session_id}")
    
    return cleared

def list_active_sessions() -> list[str]:
    """
    List all active session IDs
    """
    return list(_agent_cache.keys())