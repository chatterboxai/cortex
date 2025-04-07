from typing import Annotated
import uuid
from fastapi import APIRouter, Body, Depends
import logging
from app.auth.dependencies import get_authenticated_user
from app.auth.dependencies import security
from app.schemas.chatbot import (
    ChatbotBaseResponse, ChatbotCreate, ChatbotCreateResponse, ChatbotCreateRequest, ChatbotGetAllResponse
)
from app.models.users import User
from app.services.chatbot import ChatbotService
from app.config.settings import load_default_chatbot_settings
from app.services.rag.vectorstore import VectorStoreService
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
    # If settings is None, load default settings
    if create_request.settings is None:
        from app.schemas.chatbot import get_default_settings
        chatbot_settings = get_default_settings()
        # logger.info(f'chatbot settings: {chatbot_settings}')
    else:
        chatbot_settings = create_request.settings
        # Ensure chatbot_settings is a ChatbotSettings object, not a dict
        if isinstance(chatbot_settings, dict):
            from app.schemas.chatbot_settings import ChatbotSettings
            chatbot_settings = ChatbotSettings.model_validate(chatbot_settings)
        
    create_model = ChatbotCreate(
        name=create_request.name,
        description=create_request.description,
        owner_id=user.id,
        is_public=create_request.is_public,
        settings=chatbot_settings,
    )
    
    chatbot = await ChatbotService.create(create_model)
    logger.info(f'chatbot settings: {chatbot_settings}')
    # create vector store
    VectorStoreService.create_vector_store(
        table_name=str(chatbot.id),
        embed_dim=chatbot_settings.embedding_model.dimensions,
    )
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

@router.get(
    '/{chatbot_id}',
    response_model=ChatbotBaseResponse,
    summary='Get chatbot by id',
    description='Get chatbot by given id.'
)
async def get_chatbots_by_id(
    chatbot_id: uuid.UUID
):
    chatbot = ChatbotService.find_by_id(str(chatbot_id))
    return chatbot

@router.get(
    '/test',
)
async def get_chatbot_settings_test(
    user: Annotated[User, Depends(get_authenticated_user)],
):
    settings = load_default_chatbot_settings()
    model_dump = settings.model_dump()
    logger.info(f'Settings: {model_dump}')
    return model_dump
