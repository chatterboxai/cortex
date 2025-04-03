from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from app.schemas.dialogue import DialogueAnswerResponse, DialogueGetAllFromChatbotResponse, DialogueResponse, DialogueCreateRequest
from app.auth.dependencies import get_authenticated_user
from app.auth.dependencies import security
from app.services.dialogues import create_dialogue, find_answer_by_question, find_dialogue_by_chatbot, find_dialogue_by_id
from app.models.users import User
#from app.services.dialogues import

logger = logging.getLogger(__name__)

# Define router
router = APIRouter(
    prefix="/dialogues",
    tags=["dialogues"],
)
security = HTTPBearer(
    scheme_name="AWS Cognito JWT",
    description="AWS Cognito JWT Bearer token",
    auto_error=False
)

@router.post(
    "/dialogue", 
    response_model=DialogueResponse,
    summary="create Dialogue",
    description="creates the dialogue object"
)
async def create_dialogue_endpoint(
    dialogue_data: DialogueCreateRequest,
    user: Annotated[User, Depends(get_authenticated_user)]
):
    new_dialogue = await create_dialogue(
        user_id=user.id,
        chatbot=dialogue_data.chatbot_id,
        name=dialogue_data.name,
        questions=dialogue_data.questions,
        answer=dialogue_data.answer
    )
    
    return new_dialogue


@router.get(
    "/dialogue/{dialogue_id}", 
    response_model=DialogueResponse,
    summary="Get Dialogue",
    description="find the dialogue object using id"
)
async def find_dialogue_endpoint(
    dialogue_id: uuid.UUID
):
    dialogue = await find_dialogue_by_id(dialogue_id)
    
    return dialogue


@router.get(
    "/dialogue/chatbot/{chatbot_id}", 
    response_model=DialogueGetAllFromChatbotResponse,
    summary="Get Dialogue",
    description="find the dialogue object using id"
)
async def find_dialogue_by_chatbot_endpoint(
    chatbot_id: uuid.UUID
):
    dialogues = await find_dialogue_by_chatbot(chatbot_id)
    
    return dialogues

@router.get(
    "/dialogue/question/{question}/{chatbot_id}", 
    response_model=DialogueAnswerResponse,
    summary="Get Dialogue answer to question",
    description="find answer to the question from the dialogue object using chatbot"
)
async def find_dialogue_answer_endpoint(
    question: str,
    chatbot_id: uuid.UUID
):
    dialogue = await find_answer_by_question(question, chatbot_id)
    
    return dialogue.answer

# @router.get(
#     "/dialogue/user", 
#     response_model=DialogueGetAllFromUserResponse,
#     summary="Get Dialogue",
#     description="find the dialogue object using id"
# )
# async def find_dialogue_by_user_endpoint(
#     user: Annotated[User, Depends(get_authenticated_user)]
# ):
#     dialogue = await find_dialogue_by_user(user.id)
    
#     return dialogue