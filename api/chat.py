from typing import Optional
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from api.agent import chat_stream, new_session, end_session
from rag.agent_tools import get_last_sources
from rag.safety import safety_check
from rag.global_settings import init_llm_settings

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    success: bool

@router.post("/session/new", response_model=SessionResponse)
async def create_session():
    """Create a new chat session."""
    session_id = await new_session()
    return SessionResponse(session_id=session_id, success=True)

@router.delete("/session/{session_id}", response_model=SessionResponse)
async def delete_session(session_id: str):
    """End and clear a chat session."""
    success = await end_session(session_id)
    return SessionResponse(session_id=session_id, success=success)


@router.post("/chat")
async def chat_stream_endpoint(req: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events (SSE)
    """
    user_msg = req.message
    session_id = req.session_id
    
    init_llm_settings()

    # Safety check
    safety = safety_check(user_msg)
    level = safety["level"]
    print("SAFETY CHECK:", safety)

    async def generate():
        nonlocal session_id
        
        # Send safety status first
        yield f"data: {json.dumps({'type': 'safety', 'data': safety})}\n\n"
        
        # Crisis case - don't stream, send full message
        if level == "crisis":
            crisis_msg = (
                "⚠️ Mình rất tiếc khi nghe điều đó. An toàn của bạn lúc này là quan trọng nhất.\n\n"
                "👉 Bạn có thể gọi ngay **1900 1267 (phím 1)** — đường dây hỗ trợ khủng hoảng tâm lý và trầm cảm, trực 24/7.\n\n"
                "👉 Nếu bạn muốn một lựa chọn khác, bạn có thể gọi **096 306 1414** – đường dây 'Ngày Mai'.\n\n"
                "Nếu bạn cảm thấy mình đang gặp nguy hiểm ngay lúc này, hãy gọi **115** hoặc đến cơ sở y tế gần nhất.\n\n"
                "Bạn không đơn độc — hãy tìm sự hỗ trợ ngay lúc này."
            )
            yield f"data: {json.dumps({'type': 'crisis', 'data': crisis_msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"
            return
        
        # Warning case - send warning first
        if level == "warning":
            warning_msg = (
                "⚠️ Mình cảm nhận được là bạn đang trải qua một giai đoạn khó khăn. "
                "Cảm xúc như vậy hoàn toàn có thật và đáng để lắng nghe. Mình sẽ luôn ở đây để hỗ trợ bạn trong khả năng của mình.\n\n"
                "Nếu những cảm xúc này kéo dài hoặc trở nên nặng nề hơn, "
                "bạn có thể cân nhắc chia sẻ với một chuyên gia tâm lý hoặc người thân mà bạn tin tưởng. "
                "Bạn không cần phải tự mình vượt qua tất cả đâu."
            )
            yield f"data: {json.dumps({'type': 'warning', 'data': warning_msg})}\n\n"
        
        # Stream the response
        try:
            async for token, sid in chat_stream(user_msg, session_id):
                session_id = sid  # Update session_id
                if token:
                    yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"
            
            # Send sources at the end
            sources = get_last_sources()
            yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
        
        # Signal completion
        yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )