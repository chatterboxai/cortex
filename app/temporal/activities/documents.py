from temporalio import activity
from uuid import UUID
from app.services.document import DocumentService
from app.models.document import Document, SyncStatus
from app.services.s3 import S3Service
from app.services.parse import DocumentParserService
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import Document as LlamaIndexDocument
from llama_index.core.ingestion import IngestionPipeline
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.rag.embeddings import EmbeddingsService
from app.services.rag.vectorstore import VectorStoreService
from app.schemas.chatbot_settings import ChatbotSettings, EmbeddingModel
from app.temporal.errors import DocumentNotFoundError, DocumentUnsupportedError
from app.db.client import async_session_factory
from app.schemas.document import DocumentSyncStatusUpdateRequest
from app.models.chatbot import Chatbot
from app.models.document import Document
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

import logging

logger = logging.getLogger(__name__)

class ChatbotDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID
    name: str
    settings: ChatbotSettings


class DocumentDTO(BaseModel):
    id: UUID
    file_url: str
    mime_type: str
    sync_status: str
    sync_msg: str | None = None
    chatbot_id: UUID


class DocumentWithChatbotDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    document: DocumentDTO
    chatbot: ChatbotDTO


class DocumentSyncDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    document: DocumentDTO
    chatbot: ChatbotDTO
    text_to_sync: str


class DocumentActivities:

    @activity.defn
    async def update_sync_status(self, request: DocumentSyncStatusUpdateRequest) -> DocumentWithChatbotDTO:
        async with async_session_factory() as session:
            query = select(Document).options(selectinload(Document.chatbot)).where(Document.id == request.document_id)
            document = (await session.execute(query)).scalar_one_or_none()
            
            if not document:
                raise DocumentNotFoundError(f'Document with id {request.document_id} not found')
            
            if document.mime_type != 'application/pdf':
                raise DocumentUnsupportedError(f'Document with id {request.document_id} is not a PDF')
            
            document.sync_status = request.sync_status
            if request.sync_msg:
                document.sync_msg = request.sync_msg
            session.add(document)
            await session.commit()
            await session.refresh(document)

        # Convert to DTOs
        document_dto = DocumentDTO(
            id=document.id,
            file_url=document.file_url,
            mime_type=document.mime_type,
            sync_status=document.sync_status,
            sync_msg=document.sync_msg,
            chatbot_id=document.chatbot.id
        )
        
        chatbot_dto = ChatbotDTO(
            id=document.chatbot.id,
            name=document.chatbot.name,
            settings=document.chatbot.settings
        )
        
        return DocumentWithChatbotDTO(document=document_dto, chatbot=chatbot_dto)


class PdfDocumentActivities:

    @activity.defn
    async def parse_document(self, document: DocumentDTO) -> str:
        signed_url = S3Service.generate_presigned_url(document.file_url)
        return DocumentParserService.parse_pdf_to_markdown(signed_url)
        
    @activity.defn
    async def sync_to_vector_store(self, dto: DocumentSyncDTO) -> None:

        chatbot_settings = ChatbotSettings.model_validate(dto.chatbot.settings)
        em_settings = EmbeddingModel.model_validate(chatbot_settings.embedding_model)
        vector_store = VectorStoreService.get_vector_store(str(dto.chatbot.id), em_settings.dimensions)

        activity.logger.info(f'Vector store gotten')
        
        doc_to_parse = LlamaIndexDocument(id_=str(dto.document.id), text=dto.text_to_sync)

        embedding_model = EmbeddingsService.get_embedding_model(em_settings)

        activity.logger.info('running ingestion pipeline to vector store')
        pipeline = IngestionPipeline(
            transformations=[
                MarkdownNodeParser(),
                embedding_model
            ],
            vector_store=vector_store
        )

        pipeline.run(documents=[doc_to_parse])
