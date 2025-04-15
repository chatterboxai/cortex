import logging
from celery import shared_task, Task
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.document import Document, SyncStatus
from app.services.document import DocumentService
from app.services.s3 import S3Service
from app.services.parse import DocumentParserService
from app.db.client import sync_session_factory
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import Document as LlamaIndexDocument
from llama_index.core.ingestion import IngestionPipeline

from app.services.rag.embeddings import EmbeddingsService
from app.services.rag.vectorstore import VectorStoreService
from app.schemas.chatbot_settings import ChatbotSettings, EmbeddingModel

import asyncio
from app.temporal.client import get_client
from app.temporal.workflows import DocumentSyncWorkflow
from typing import Optional

logger = logging.getLogger(__name__)

markdown_parser = MarkdownNodeParser()

async def process_document_queue_temporal(document_id: Optional[UUID] = None):
    logger.info("Scanning for documents to sync (Temporal)")

    try:
        if document_id:
            documents = [DocumentService.get_by_id(document_id)]
        else:
            documents = DocumentService.get_documents_to_sync()

        client = await get_client()

        for document in documents:
            logger.info(f"Submitting Temporal workflow for document {document.id}")
            await asyncio.sleep(0.5)
            await client.start_workflow(
                DocumentSyncWorkflow.run,
                str(document.id),
                id=f"document-sync-{document.id}",
                task_queue="sync-tasks"
            )

        logger.info(f"Queued {len(documents)} documents via Temporal")

    except Exception as e:
        logger.exception("Error while queuing documents with Temporal")


# @shared_task(
#     name="app.tasks.documents.process_document",
#     bind=True,
#     autoretry_for=(Exception,),
#     retry_backoff=True,
#     retry_backoff_max=60,
#     retry_kwargs={'max_retries': 5}
# )
# def process_document(self: Task, document_id: str) -> None:
#     """
#     Process a single document.
    
#     1. Retrieves the document from the database
#     2. Gets a signed URL from S3
#     3. Uses Mistral OCR to parse text
    
#     Args:
#         document_id: UUID string of the document to process
#     """
#     # Check if this is a retry
#     if self.request.retries:
#         logger.warning(
#             f"Task {self.request.id} is being retried "
#             f"for the {self.request.retries} time"
#         )
#     else:
#         logger.info(
#             f"Task {self.request.id} is running for the first time"
#         )
    
#     logger.info(f"Processing document {document_id}")
    
#     # Convert string to UUID
#     doc_uuid = UUID(document_id)
    
#     with sync_session_factory() as session:
#         # load chatbot when document is loaded
#         query = select(Document).options(selectinload(Document.chatbot)).where(Document.id == doc_uuid)
#         document = session.execute(query).scalar_one_or_none()
#         if not document:
#             return
#         try:
            
#             if document.mime_type != "application/pdf":
#                 document.sync_status = SyncStatus.SYNCED
#                 document.sync_msg = 'Only PDF documents are supported for now'
#                 session.commit() # only support pdf for now
#                 return
            
#             document.sync_status = SyncStatus.IN_PROGRESS
#             session.commit()

#             # Get signed URL from S3
#             signed_url = S3Service.generate_presigned_url(document.file_url)
            
#             # Send to Mistral OCR for processing using synchronous method
#             logger.info(f"Sending signed URL to Mistral OCR: {signed_url}")
#             parsed_markdown = DocumentParserService.parse_pdf_to_markdown(signed_url)
            
#             logger.debug(f"Document chatbot settings: {document.chatbot.settings}")
#             chatbot_settings = ChatbotSettings.model_validate(document.chatbot.settings)
#             em_settings = EmbeddingModel.model_validate(chatbot_settings.embedding_model)
#             vector_store = VectorStoreService.get_vector_store(str(document.chatbot.id), em_settings.dimensions)
#             logger.debug(f"Vector store gotten")
            
#             doc_to_parse = LlamaIndexDocument(id_=str(doc_uuid), text=parsed_markdown)
#             # nodes = markdown_parser.get_nodes_from_documents([doc_to_parse])
#             # vsi.add_nodes(nodes)

#             embedding_model = EmbeddingsService.get_embedding_model(em_settings)

#             logger.debug('running ingestion pipeline to vector store')
#             pipeline = IngestionPipeline(
#                 transformations=[
#                     MarkdownNodeParser(),
#                     embedding_model
#                 ],
#                 vector_store=vector_store
#             )

#             pipeline.run(documents=[doc_to_parse])
            
#             # Update document status to success using synchronous method
#             document.sync_status = SyncStatus.SYNCED
#             session.commit()

#             logger.debug(f"Document {document_id} synced to vector store")
#         except Exception as e:
#             logger.error(f"Error processing document {document_id}: {e}")
            
#             document.sync_status = SyncStatus.FAILED
#             document.sync_msg = str(e)
#             session.commit()

#             # Re-raise to trigger retry
#             raise
