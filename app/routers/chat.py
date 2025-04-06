from fastapi import APIRouter, Request
from app.core.limiter import limiter

router = APIRouter()

@router.post("/chat")
@limiter.limit("5/minute")  # 5 requests per minute per IP
async def send_message(request: Request):
    return {"message": "Hello! This is a rate-limited chat endpoint."}