from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# region: Base
class ChatbotBaseResponse(BaseModel):
    id: Annotated[UUID, Field(description='The ID of the chatbot')]
    name: Annotated[str, Field(description='The name of the chatbot')]
    description: Annotated[str, Field(description='The description of the chatbot')]
    is_public: Annotated[bool, Field(default=False, description='Whether the chatbot is public')]
    created_at: Annotated[datetime, Field(description='The date and time the chatbot was created')]
    updated_at: Annotated[datetime, Field(description='The date and time the chatbot was last updated')]

    model_config = ConfigDict(from_attributes=True)
# endregion: Base


# region: Create Chatbot
class ChatbotCreateRequest(BaseModel):
    name: Annotated[str, Field(description='The name of the chatbot')]
    description: Annotated[str, Field(description='The description of the chatbot')]
    is_public: Annotated[bool, Field(default=False, description='Whether the chatbot is public')]


class ChatbotCreate(BaseModel):
    name: Annotated[str, Field(description='The name of the chatbot')]
    description: Annotated[str, Field(description='The description of the chatbot')]
    owner_id: Annotated[UUID, Field(description='The ID of the owner of the chatbot')]
    is_public: Annotated[bool, Field(default=False, description='Whether the chatbot is public')]


class ChatbotCreateResponse(ChatbotBaseResponse):
    pass
# endregion: Create Chatbot


# region: Get All Chatbots
class ChatbotGetAllResponse(BaseModel):
    chatbots: Annotated[list[ChatbotBaseResponse], Field(description='The list of chatbots for the owner')]


# endregion: Get All Chatbots