from typing import Optional, AsyncGenerator
from rag.agent_core import get_agent, run_agent, run_agent_stream, clear_agent_session
from rag.agent_tools import get_last_sources, clear_last_sources


async def chat(message: str, session_id: Optional[str] = None) -> tuple[str, str, list[dict]]:
    """
    Chat with the agent and return response with sources
    """
    # Clear previous sources before new query
    clear_last_sources()
    
    # Run agent with memory support
    response, session_id = await run_agent(message, session_id)
    
    # Get sources from the last DSM-5 query (if any)
    sources = get_last_sources()
    
    return response, session_id, sources

async def chat_stream(message: str, session_id: Optional[str] = None) -> AsyncGenerator[tuple[str, str], None]:
    """
    Chat with the agent using streaming
    """
    # Clear previous sources before new query
    clear_last_sources()
    
    # Run agent with streaming
    async for token, sid in run_agent_stream(message, session_id):
        yield token, sid


async def new_session() -> str:
    """
    Create a new chat session
    """
    _, session_id, _ = get_agent(None)
    return session_id


async def end_session(session_id: str) -> bool:
    """
    End and clear a chat session
    """
    return clear_agent_session(session_id)
