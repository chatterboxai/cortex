from typing import Annotated
from fastapi import APIRouter, Body, Depends
import logging
from app.auth.dependencies import get_authenticated_user
from app.auth.dependencies import security
from app.schemas.chatbot import (
    ChatbotCreate, ChatbotCreateResponse, ChatbotCreateRequest
)
from app.models.users import User
from app.services.chatbot import ChatbotService

logger = logging.getLogger(__name__)

# Define router
router = APIRouter(
    prefix='/api/v1/chatbots',
    tags=['chatbots'],
    dependencies=[Depends(security)],
)


@router.post(
    '/',
    response_model=ChatbotCreateResponse,
    summary='Create a new chatbot',
    description=(
        'Creates a new chatbot with the given name, description, and owner ID.'
        ' Requires a valid AWS Cognito JWT token in the Authorization header.'
    )
)
async def create_chatbot(
    create_request: Annotated[ChatbotCreateRequest, Body(...)],
    user: Annotated[User, Depends(get_authenticated_user)],
):
    create_model = ChatbotCreate(
        name=create_request.name,
        description=create_request.description,
        owner_id=user.id,
        is_public=create_request.is_public,
    )
    
    chatbot = await ChatbotService.create(create_model)
    return chatbot


@router.get(
    '/',
    response_model=ChatbotGetAllResponse,
    summary='Get all chatbots',
    description='Get all chatbots for the current authenticated user.'
)
async def get_all_chatbots(
    user: Annotated[User, Depends(get_authenticated_user)],
):
    chatbots = await ChatbotService.find_all(user.id)
    return ChatbotGetAllResponse(chatbots=chatbots)

