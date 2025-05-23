from datetime import datetime
from typing import Annotated
from app.models.dialogue import SyncStatus
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
    sync_status: Annotated[SyncStatus, Field(description='The synchronization status of the document')]
    created_at: Annotated[datetime, Field(description='The date and time the dialogue was created')]
    updated_at: Annotated[datetime, Field(description='The date and time the dialogue was last updated')]

    model_config = ConfigDict(from_attributes=True)
        
class DialogueGetAllFromChatbotResponse(BaseModel):
    dialogues: Annotated[list[DialogueResponse], Field(description='The list of dialogues for the chatbot')]

class DialogueAnswerResponse(BaseModel):
    answer: Annotated[str, Field(description="answer to question")]
    