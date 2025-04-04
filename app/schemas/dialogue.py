from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
import uuid

class DialogueCreateRequest(BaseModel):
    name: Annotated[str, Field(description="name of dialogue")]
    questions: Annotated[list[str], Field(description="list of questions in dialogue")]
    answer: Annotated[str, Field(description="answer to dialogue questions")]
    chatbot_id: Annotated[uuid.UUID, Field(description="chatbot related to dialogue")]
    
class DialogueEditRequest(BaseModel):
    id: Annotated[uuid.UUID, Field(description="dialogue's uuid")]
    questions: Annotated[list[str], Field(description="list of questions in dialogue")]
    answer: Annotated[str, Field(description="answer to dialogue questions")]
    
class DialogueResponse(BaseModel):
    id: Annotated[uuid.UUID, Field(description="dialogue's uuid")]
    name: Annotated[str, Field(description="name of dialogue")]
    questions: Annotated[list[str], Field(description="list of questions in dialogue")]
    answer: Annotated[str, Field(description="answer to dialogue questions")]
    chatbot_id: Annotated[uuid.UUID, Field(description="chatbot related to dialogue")]
    created_at: Annotated[datetime, Field(description='The date and time the dialogue was created')]
    updated_at: Annotated[datetime, Field(description='The date and time the dialogue was last updated')]
    
    class Config:
        orm_mode = True  # This ensures proper serialization of SQLAlchemy model results
        
class DialogueGetAllFromChatbotResponse(BaseModel):
    dialogues: Annotated[list[DialogueResponse], Field(description='The list of dialogues for the chatbot')]
    class Config:
        orm_mode = True  # This ensures proper serialization of SQLAlchemy model results
# class DialogueGetAllFromUserResponse(BaseModel):
#     dialogues: Annotated[list[DialogueResponse], Field(description='The list of dialogues for the chatbot')]

class DialogueAnswerResponse(BaseModel):
    answer: Annotated[str, Field(description="answer to question")]
    