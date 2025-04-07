from typing import Annotated
from fastapi import (
    APIRouter, Depends, Path, UploadFile, File, Form, HTTPException, status
)
import logging
from uuid import UUID
from app.auth.dependencies import get_authenticated_user, security
from app.models.users import User
from app.schemas.document import DocumentCreate
from app.schemas.document import DocumentCreateResponse
from app.schemas.document import DocumentBaseResponse

from app.services.document import DocumentService
from app.services.s3 import S3Service
import uuid

from app.services.chatbot import ChatbotService
from app.models.document import SyncStatus

logger = logging.getLogger(__name__)

# Define router
router = APIRouter(
    prefix='/api/v1/documents',
    tags=['documents'],
    dependencies=[Depends(security)],
)


@router.post(
    '/',
    response_model=DocumentCreateResponse,
    summary='Index a new document for a chatbot',
    description=(
        'Index a new document for a chatbot. The document will be queued '
        'for processing and indexing in the background.'
    )
)
async def create_document(
    file: Annotated[UploadFile, File(...)],
    title: Annotated[str, Form(...)],
    chatbot_id: Annotated[UUID, Form(...)],
    user: Annotated[User, Depends(get_authenticated_user)]
):
    # Verify the chatbot exists
    chatbot = await ChatbotService.afind_by_id(chatbot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    
    # Verify the user owns the chatbot
    if chatbot.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to access this chatbot"
        )
    
    # Create a document model and upload the file
    try:
        # upload to s3
        key = file.filename or str(uuid.uuid4())
        await S3Service.upload_file(file, key)
        
        # create document
        document = await DocumentService.acreate(
            DocumentCreate(
                chatbot_id=chatbot_id,
                title=title,
                key=key,
                mime_type=file.content_type or 'application/octet-stream'
            )
        )
        
        return document
    except Exception as e:
        logger.exception(f"Error creating document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating document: {str(e)}"
        )


# @router.patch(
#     '/{document_id}',
#     response_model=DocumentBaseResponse,
#     summary='Update a document',
#     description='Update a document'
# )
# async def update_document_sync_status_test(
#     document_id: Annotated[UUID, Path(...)],
#     sync_status: Annotated[SyncStatus, Form(...)],
#     user: Annotated[User, Depends(get_authenticated_user)]
# ):
#     document = await DocumentService.update_sync_status(
#         document_id,
#         sync_status
#     )
#     return document