from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from api.agent import chat, new_session, end_session
from rag.safety import safety_check
from rag.global_settings import init_llm_settings

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    success: bool


@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    session_id = req.session_id
    
    init_llm_settings()

    # Safety check
    safety = safety_check(user_msg)
    level = safety["level"]
    print("SAFETY CHECK:", safety)

    messages = []
    sources = []

    # Crisis case
    if level == "crisis":
        messages.append({
            "type": "crisis",
            "text": (
                "⚠️ Mình rất tiếc khi nghe điều đó. An toàn của bạn lúc này là quan trọng nhất.\n\n"
                "👉 Bạn có thể gọi ngay **1900 1267 (phím 1)** — đường dây hỗ trợ khủng hoảng tâm lý và trầm cảm, trực 24/7.\n\n"
                "👉 Nếu bạn muốn một lựa chọn khác, bạn có thể gọi **096 306 1414** – đường dây 'Ngày Mai'.\n\n"
                "Nếu bạn cảm thấy mình đang gặp nguy hiểm ngay lúc này, hãy gọi **115** hoặc đến cơ sở y tế gần nhất.\n\n"
                "Bạn không đơn độc — hãy tìm sự hỗ trợ ngay lúc này."
            )
        })

        return {
            "session_id": session_id,
            "messages": messages,
            "sources": [],
            "safety": safety
        }

    # Warning case
    if level == "warning":
        messages.append({
            "type": "warning",
            "text": (
                "⚠️ Mình cảm nhận được là bạn đang trải qua một giai đoạn khó khăn. "
                "Cảm xúc như vậy hoàn toàn có thật và đáng để lắng nghe. Mình sẽ luôn ở đây để hỗ trợ bạn trong khả năng của mình.\n\n"
                "Nếu những cảm xúc này kéo dài hoặc trở nên nặng nề hơn, "
                "bạn có thể cân nhắc chia sẻ với một chuyên gia tâm lý hoặc người thân mà bạn tin tưởng. "
                "Bạn không cần phải tự mình vượt qua tất cả đâu."
            )
        })

    # Normal chat response
    bot_reply, session_id, sources = await chat(user_msg, session_id)

    # Prepend warning message
    messages.append({
        "type": "reply",
        "text": bot_reply
    })

    return {
        "session_id": session_id,
        "messages": messages,
        "sources": sources,
        "safety": safety
    }

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