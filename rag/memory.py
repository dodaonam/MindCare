import uuid
from typing import Optional
from llama_index.core.memory import Memory

TOKEN_LIMIT = 8000  # Total tokens for memory
TOKEN_FLUSH_SIZE = 800  # Tokens to flush when limit exceeded (10% of limit)
CHAT_HISTORY_TOKEN_RATIO = 0.7  # 70% for chat history, 30% for memory blocks

# Cache memories by session_id
_memory_cache: dict[str, Memory] = {}

def create_memory(session_id: str) -> Memory:
    """
    Create a new Memory instance for a session
    """
    # Create Memory with configuration
    memory = Memory.from_defaults(
        session_id=session_id,
        token_limit=TOKEN_LIMIT,
        token_flush_size=TOKEN_FLUSH_SIZE,
        chat_history_token_ratio=CHAT_HISTORY_TOKEN_RATIO,
    )
    
    return memory

def get_memory(session_id: Optional[str] = None) -> tuple[Memory, str]:
    """
    Get or create a Memory instance for a session
    """
    # Generate new session_id if not provided
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    # Return cached memory if exists
    if session_id in _memory_cache:
        return _memory_cache[session_id], session_id
    
    # Create new memory for this session
    memory = create_memory(session_id)
    _memory_cache[session_id] = memory
    
    print(f"Memory created for session: {session_id}")
    return memory, session_id

def clear_memory(session_id: str) -> bool:
    """
    Clear memory for a specific session
    """
    if session_id in _memory_cache:
        del _memory_cache[session_id]
        print(f"Memory cleared for session: {session_id}")
        return True
    return False

def clear_all_memories() -> int:
    """
    Clear all cached memories
    """
    count = len(_memory_cache)
    _memory_cache.clear()
    print(f"Cleared {count} memory sessions.")
    return count

def list_sessions() -> list[str]:
    """
    List all active session IDs
    """
    return list(_memory_cache.keys())
