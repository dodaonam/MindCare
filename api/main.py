from fastapi import FastAPI
from api.chat import router as chat_router
from api.assessments import router as assess_router

app = FastAPI(
    title="Mental Health Assistant API",
    version="1.0.0",
)

app.include_router(chat_router)
app.include_router(assess_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
