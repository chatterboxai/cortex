import logging
import uuid
from app.db.client import async_session_factory, sync_session_factory
from app.models.document import Document, SyncStatus
from app.schemas.document import DocumentCreate
from sqlalchemy import select

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
