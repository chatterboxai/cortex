from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from app.schemas.dialogue import DialogueAnswerResponse, DialogueEditRequest, DialogueGetAllFromChatbotResponse, DialogueResponse, DialogueCreateRequest
from app.auth.dependencies import get_authenticated_user
from app.auth.dependencies import security
from app.models.users import User
from app.services.dialogues import DialogueService
#from app.services.dialogues import

# from app.tasks.dialogues import process_dialogue_queue_temporal

logger = logging.getLogger(__name__)

# Define router
router = APIRouter(
    prefix="/dialogues",
    tags=["dialogues"],
    dependencies=[Depends(security)],
)

@router.post(
    "/", 
    response_model=DialogueResponse,
    summary="create Dialogue",
    description="creates the dialogue object"
)
async def create_dialogue_endpoint(
    dialogue_data: DialogueCreateRequest,
    user: Annotated[User, Depends(get_authenticated_user)]
):
    new_dialogue = await DialogueService.create_dialogue(
        chatbot=dialogue_data.chatbot_id,
        name=dialogue_data.name,
        questions=dialogue_data.questions,
        answer=dialogue_data.answer
    )

    # await process_dialogue_queue_temporal(new_dialogue.id)
    
    return new_dialogue


@router.get(
    "/{dialogue_id}", 
    response_model=DialogueResponse,
    summary="Get Dialogue",
    description="find the dialogue object using id"
)
async def find_dialogue_endpoint(
    dialogue_id: uuid.UUID
):
    dialogue = await DialogueService.find_dialogue_by_id(dialogue_id)
    
    return dialogue

@router.patch(
    "/edit", 
    response_model=DialogueResponse,
    summary="edit dialogue",
    description="edit question and answers of a dialogue"
)
async def find_dialogue_endpoint(
    dialogue_data: DialogueEditRequest
):
    dialogue = await DialogueService.edit_dialogue(
        dialogue_id = dialogue_data.id,
        questions = dialogue_data.questions,
        answer = dialogue_data.answer
    )
    
    return dialogue


@router.delete(
    "/{dialogue_id}", 
    response_model=DialogueResponse,
    summary="Get Dialogue",
    description="find the dialogue object using id"
)
async def delete_dialogue_endpoint(
    dialogue_id: uuid.UUID
):
    dialogue = await DialogueService.delete_dialogue_by_id(dialogue_id)
    
    return dialogue


@router.get(
    "/chatbot/{chatbot_id}", 
    response_model=DialogueGetAllFromChatbotResponse,
    summary="Get Dialogue",
    description="find the dialogue object using id"
)
async def find_dialogue_by_chatbot_endpoint(
    chatbot_id: uuid.UUID
):
    dialogues = await DialogueService.find_dialogue_by_chatbot(chatbot_id)
    
    return DialogueGetAllFromChatbotResponse(dialogues=dialogues)

# @router.get(
#     "/question/{question}/{chatbot_id}", 
#     response_model=DialogueAnswerResponse,
#     summary="Get Dialogue answer to question",
#     description="find answer to the question from the dialogue object using chatbot"
# )
# async def find_dialogue_answer_endpoint(
#     question: str,
#     chatbot_id: uuid.UUID
# ):
#     dialogue = await DialogueService.find_answer_by_question(question, chatbot_id)
    
#     return DialogueAnswerResponse(answer=dialogue.answer)

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