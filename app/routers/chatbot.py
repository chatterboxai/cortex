from typing import Annotated
import uuid
from fastapi import APIRouter, Body, Depends, Request, HTTPException
from pydantic import BaseModel
from app.core.limiter import limiter
import logging
from app.auth.dependencies import get_authenticated_user
from app.auth.dependencies import security
from app.schemas.chatbot import (
    ChatRequest, ChatbotBaseResponse, ChatbotCreate, ChatbotCreateResponse, ChatbotCreateRequest, ChatbotGetAllResponse
)
from app.models.users import User
from app.services.chatbot import ChatbotService
from app.services.rag.vectorstore import VectorStoreService
import asyncio
from fastapi.responses import StreamingResponse
import json
from app.agents.qa import QaAgentWorkflow

logger = logging.getLogger(__name__)

# Define router
router = APIRouter(
    prefix='/api/v1/chatbots',
    tags=['chatbots'],
    dependencies=[Depends(security)],
)

# Define a separate router for unauthenticated endpoints
public_router = APIRouter(
    prefix='/api/v1/chatbots/public',
    tags=['chatbots-public'],
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


# Testing endpoint
# async def streamer():
#     # Sends an event every second with data: "Message {i}"
#     message = ""
#     streamed_words = ["Hello", "world", "this", "is", "a", "test."]
#     for word in streamed_words:
#         message += ' ' + word
#         event_name = 'event: stream_chat'
#         event_data = f'data: {message}'
#         yield f'{event_name}\n{event_data}\n\n'
#         await asyncio.sleep(1)


# @router.post(
#     '/chat',
#     summary='Chat with chatbot',
#     description='Chat with chatbot by given id.'
# )
# async def streaming_test():
#     return StreamingResponse(
#         streamer(), media_type='text/event-stream', headers={'Content-Encoding': 'none'}
#     )




# ---------------------- Streaming Chat -----------------------

class ChatInput(BaseModel):
    chatbot_id: str
    message: str

@router.post(
    '/chat',
    summary='Chat with chatbot (streamed)',
    description='Stream chat response from the chatbot word by word.'
)
@limiter.limit("5/minute")  # ✅ Rate limit by IP
async def stream_chat(request: Request, body: ChatInput):
    user_message = body.message
    chatbot_id = body.chatbot_id

    # TODO: Replace this mock logic with RAG / dialogue matching
    mock_response = "Singapore Management University is located at 81 Victoria St, Singapore 188065"
    words = mock_response.split()

    async def event_generator():
        partial = ""
        for word in words:
            partial += word + " "
            yield f"data: {partial.strip()}\n\n"
            await asyncio.sleep(0.2)  # Simulate typing effect

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={'Content-Encoding': 'none'}
    )


@public_router.post(
    '/chat',
    summary='Chat with chatbot',
    description='Chat with chatbot by given id.',
    response_model=None,
)
async def chat_with_chatbot(
    chat_request: Annotated[ChatRequest, Body(...)],
):
    chatbot = ChatbotService.find_by_id(chat_request.chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail='Chatbot not found')
    # logger.info(f'chatbot found: {chatbot.id}')

    # create thread id if not provided (new chat)
    thread_id = chat_request.thread_id
    if not thread_id:
        thread_id = uuid.uuid4()
    thread_id = str(thread_id)

    qa_agent = QaAgentWorkflow(str(chat_request.chatbot_id))

    message_id = str(uuid.uuid4())

    async def generate_response():
        async for response in qa_agent.arespond(chat_request.message, thread_id):
            event_name = 'event: response'
            event_data = f'data: {json.dumps({"thread_id": thread_id, "message_id": message_id, "message": response})}'
            yield f'{event_name}\n{event_data}\n\n'
    
    return StreamingResponse(
        generate_response(),
        media_type='text/event-stream',
        headers={'Content-Encoding': 'none'}
    )

