from fastapi import APIRouter
from pydantic import BaseModel
from api.agent import chat
from rag.safety import safety_check
from rag.global_settings import init_llm_settings

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    init_llm_settings()

    # Safety check
    safety = safety_check(user_msg)
    level = safety["level"]
    print("SAFETY CHECK:", safety)

    messages = []

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
            "messages": messages,
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
    bot_reply = await chat(user_msg)

    # Prepend warning message
    messages.append({
        "type": "reply",
        "text": bot_reply
    })

    return {
        "messages": messages,
        "safety": safety
    }