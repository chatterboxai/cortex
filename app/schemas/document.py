from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from app.models.document import SyncStatus


# region: Base
class DocumentBaseResponse(BaseModel):
    id: Annotated[UUID, Field(description='The ID of the document')]
    chatbot_id: Annotated[
        UUID, 
        Field(description='The ID of the chatbot this document belongs to')
    ]
    title: Annotated[str, Field(description='The title of the document')]
    file_url: Annotated[
        str, 
        Field(description='The URL of the uploaded file')
    ]
    mime_type: Annotated[
        str, 
        Field(description='The MIME type of the document')
    ]
    sync_status: Annotated[
        SyncStatus, 
        Field(description='The synchronization status of the document')
    ]
    created_at: Annotated[
        datetime, 
        Field(description='The date and time the document was created')
    ]
    updated_at: Annotated[
        datetime, 
        Field(description='The date and time the document was last updated')
    ]

    model_config = ConfigDict(from_attributes=True)
# endregion: Base


# region: Create Document
class DocumentCreate(BaseModel):
    chatbot_id: Annotated[
        UUID, 
        Field(description='The ID of the chatbot this document belongs to')
    ]
    title: Annotated[str, Field(description='The title of the document')]
    key: Annotated[
        str, 
        Field(description='The key of the uploaded file')
    ]
    mime_type: Annotated[
        str, 
        Field(description='The MIME type of the document')
    ]


class DocumentCreateResponse(DocumentBaseResponse):
    pass
# endregion: Create Document 

class DocumentGetAllFromChatbotResponse(BaseModel):
    documents: Annotated[list[DocumentBaseResponse], Field(description='The list of dialogues for the chatbot')]