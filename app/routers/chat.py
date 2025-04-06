from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.core.limiter import limiter

router = APIRouter()

class ChatInput(BaseModel):
    message: str

@router.post("/chat")
@limiter.limit("5/minute")  # Rate limit based on IP
async def send_message(request: Request, body: ChatInput):
    return {"message": f"Echo: {body.message}"}
