from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

# Remove direct import that causes circular dependency
from app.schemas.chatbot_settings import ChatbotSettings


def get_default_settings():
    # Import at function call time to avoid circular imports
    from app.config.settings import load_default_chatbot_settings
    return load_default_chatbot_settings()


# region: Base
class ChatbotBaseResponse(BaseModel):
    id: Annotated[UUID, Field(description='The ID of the chatbot')]
    name: Annotated[str, Field(description='The name of the chatbot')]
    description: Annotated[str, Field(
        description='The description of the chatbot')]
    is_public: Annotated[bool, Field(
        default=False, description='Whether the chatbot is public')]
    settings: Annotated[ChatbotSettings, Field(
        description='Configurable settings for the chatbot')]
    created_at: Annotated[datetime, Field(
        description='The date and time the chatbot was created')]
    updated_at: Annotated[datetime, Field(
        description='The date and time the chatbot was last updated')]

    model_config = ConfigDict(from_attributes=True)
# endregion: Base


# region: Create Chatbot
class ChatbotCreateRequest(BaseModel):
    name: Annotated[str, Field(description='The name of the chatbot')]
    description: Annotated[str, Field(
        description='The description of the chatbot')]
    is_public: Annotated[bool, Field(
        default=False, description='Whether the chatbot is public')]
    settings: Optional[ChatbotSettings] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "My Chatbot",
                "description": "A description of my chatbot",
                "is_public": False
            }
        }
    )


class ChatbotCreate(BaseModel):
    name: Annotated[str, Field(description='The name of the chatbot')]
    description: Annotated[str, Field(
        description='The description of the chatbot')]
    owner_id: Annotated[UUID, Field(
        description='The ID of the owner of the chatbot')]
    is_public: Annotated[bool, Field(
        default=False, description='Whether the chatbot is public')]
    settings: Annotated[ChatbotSettings, Field(
        default_factory=get_default_settings,
        description='Configurable settings for the chatbot')]


class ChatbotCreateResponse(ChatbotBaseResponse):
    pass
# endregion: Create Chatbot


# region: Get All Chatbots
class ChatbotGetAllResponse(BaseModel):
    chatbots: Annotated[list[ChatbotBaseResponse], Field(
        description='The list of chatbots for the owner')]


# endregion: Get All Chatbots