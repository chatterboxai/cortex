import logging
import uuid
from uuid import UUID
from app.db.client import async_session_factory, sync_session_factory
from app.models.document import Document, SyncStatus
from app.schemas.document import DocumentCreate
from sqlalchemy import select
from app.services.s3 import S3Service
from app.services.parse import DocumentParserService
from app.services.rag.embeddings import EmbeddingsService
from app.services.rag.vectorstore import VectorStoreService
from app.schemas.chatbot_settings import ChatbotSettings, EmbeddingModel
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import Document as LlamaIndexDocument
from llama_index.core.ingestion import IngestionPipeline

logger = logging.getLogger(__name__)


class DocumentService:
    
    @classmethod
    async def acreate(cls, document_create: DocumentCreate) -> Document:
        """Create a document record in the database."""
        async with async_session_factory() as session:
            document = Document(
                chatbot_id=document_create.chatbot_id,
                title=document_create.title,
                file_url=document_create.key,
                mime_type=document_create.mime_type,
                sync_status=SyncStatus.NA,
                sync_msg=''
            )
            
            session.add(document)
            await session.commit()
            await session.refresh(document)
            
            return document
            
    @classmethod
    async def aget_document(cls, document_id: uuid.UUID) -> Document:
        """Get a document by ID."""
        async with async_session_factory() as session:
            document = await session.get(Document, document_id)
            return document
    
    @classmethod
    def get_document(cls, document_id: uuid.UUID) -> Document:
        """Synchronous version of get_document."""
        with sync_session_factory() as session:
            document = session.get(Document, document_id)
            return document

    @classmethod
    async def get_documents_by_chatbot_id(cls, chatbot_id: uuid.UUID) -> list[Document]:
        """Return a list of documents associated with the given chatbot_id."""
        with sync_session_factory() as session:
            documents = session.query(Document).filter(Document.chatbot_id == chatbot_id).all()
            return documents

    @classmethod
    def update_sync_status(
        cls, 
        document_id: uuid.UUID, 
        sync_status: SyncStatus,
        sync_msg: str = None
    ) -> Document:
        """
        Synchronous version of update_sync_status.
        Update the sync status of a document using synchronous SQLAlchemy.
        """
        from sqlalchemy.orm import Session
        from app.db.client import sync_engine

        with Session(sync_engine) as session:
            document = session.get(Document, document_id)
            if not document:
                raise ValueError(f"Document with id {document_id} not found")
            
            document.sync_status = sync_status
            if sync_msg:
                document.sync_msg = sync_msg
            
            session.add(document)
            session.commit()
            session.refresh(document)
            
            return document
    
    @classmethod
    def get_documents_to_sync(cls, limit: int = 10) -> list[Document]:
        with sync_session_factory() as session:
            query = select(Document).where(
                Document.sync_status.in_([SyncStatus.NA, SyncStatus.FAILED])
            ).limit(limit)
            
            result = session.execute(query)
            return list(result.scalars().all())

    @classmethod
    def sync_to_vector_store(cls, document_id: UUID):
        logger.info(f"Syncing document {document_id} to vector store")
        from sqlalchemy.orm import Session
        from app.db.client import sync_engine

        with Session(sync_engine) as session:
            document = session.get(Document, document_id)
            if not document:
                raise ValueError("Document not found")

            if document.mime_type != "application/pdf":
                document.sync_status = SyncStatus.SYNCED
                document.sync_msg = 'Only PDF documents are supported for now'
                session.commit()
                return

            document.sync_status = SyncStatus.IN_PROGRESS
            session.commit()

            signed_url = S3Service.generate_presigned_url(document.file_url)
            parsed_markdown = DocumentParserService.parse_pdf_to_markdown(signed_url)

            chatbot_settings = ChatbotSettings.model_validate(document.chatbot.settings)
            em_settings = EmbeddingModel.model_validate(chatbot_settings.embedding_model)
            vector_store = VectorStoreService.get_vector_store(str(document.chatbot.id), em_settings.dimensions)
            embedding_model = EmbeddingsService.get_embedding_model(em_settings)

            doc_to_parse = LlamaIndexDocument(id_=str(document_id), text=parsed_markdown)

            pipeline = IngestionPipeline(
                transformations=[MarkdownNodeParser(), embedding_model],
                vector_store=vector_store
            )
            pipeline.run(documents=[doc_to_parse])

            document.sync_status = SyncStatus.SYNCED
            session.commit()

    @staticmethod
    def get_by_id(document_id: UUID) -> Document:
        with sync_session_factory() as session:
            return session.get(Document, document_id)
