from fastapi import APIRouter
from pydantic import BaseModel
from api.agent import chat

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    reply = await chat(req.message)
    return {"reply": reply}
