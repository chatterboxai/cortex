import logging
from celery import shared_task, Task
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.dialogue import Dialogue, SyncStatus
from app.services.dialogues import DialogueService
from app.services.s3 import S3Service
from app.services.parse import DocumentParserService
from app.db.client import sync_session_factory
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import Document as LlamaIndexDocument
from llama_index.core.ingestion import IngestionPipeline

from app.services.rag.embeddings import EmbeddingsService
from app.services.rag.vectorstore import VectorStoreService
from app.schemas.chatbot_settings import ChatbotSettings, EmbeddingModel

logger = logging.getLogger(__name__)

markdown_parser = MarkdownNodeParser()

@shared_task(name="app.tasks.documents.process_document_queue")
def process_document_queue():
    """
    Scheduled task that runs every 10 seconds to find documents
    that need processing and queue individual processing tasks.
    """
    logger.info("Checking for documents that need processing")
    
    try:
        dialogues = DialogueService.get_dialogues_to_sync()
        
        # Queue each dialogue for individual processing
        for dialogue in dialogues:
            dia_id = dialogue.id
            process_dialogue.delay(str(dia_id))
            
        return f"Queued {len(dialogues)} documents for syncing to vector store"
    
    except Exception as e:
        logger.error(f"Error queueing documents to sync to vector store: {e}")
        raise


@shared_task(
    name="app.tasks.documents.process_document",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={'max_retries': 5}
)
def process_dialogue(self: Task, dialogue_id: str) -> None:
    """
    Process a single dialogue.
    
    1. Retrieves the dialogue from the database
    2. Gets a signed URL from S3
    3. Uses Mistral OCR to parse text
    
    Args:
        document_id: UUID string of the dialogue to process
    """
    # Check if this is a retry
    if self.request.retries:
        logger.warning(
            f"Task {self.request.id} is being retried "
            f"for the {self.request.retries} time"
        )
    else:
        logger.info(
            f"Task {self.request.id} is running for the first time"
        )
    
    logger.info(f"Processing dialogue {dialogue_id}")
    
    # Convert string to UUID
    dia_uuid = UUID(dialogue_id)
    
    with sync_session_factory() as session:
        # load chatbot when dialogue is loaded
        query = select(Dialogue).options(selectinload(Dialogue.chatbot)).where(Dialogue.id == dia_uuid)
        dialogue = session.execute(query).scalar_one_or_none()
        if not dialogue:
            return
        try:
            
            dialogue.sync_status = SyncStatus.IN_PROGRESS
            session.commit()
            
            logger.debug(f"Document chatbot settings: {dialogue.chatbot.settings}")
            chatbot_settings = ChatbotSettings.model_validate(dialogue.chatbot.settings)
            em_settings = EmbeddingModel.model_validate(chatbot_settings.embedding_model)
            vector_store = VectorStoreService.get_vector_store(str(dialogue.chatbot.id), em_settings.dimensions)
            logger.debug(f"Vector store gotten")
            
            dia_to_parse = LlamaIndexDocument(id_=str(dia_uuid), text=dialogue.questions)
            # nodes = markdown_parser.get_nodes_from_documents([doc_to_parse])
            # vsi.add_nodes(nodes)

            embedding_model = EmbeddingsService.get_embedding_model(em_settings)

            logger.debug('running ingestion pipeline to vector store')
            pipeline = IngestionPipeline(
                transformations=[
                    MarkdownNodeParser(),
                    embedding_model
                ],
                vector_store=vector_store
            )

            pipeline.run(documents=[dia_to_parse])
            
            # Update dialogue status to success using synchronous method
            dialogue.sync_status = SyncStatus.SYNCED
            session.commit()

            logger.debug(f"Document {dialogue_id} synced to vector store")
        except Exception as e:
            logger.error(f"Error processing dialogue {dialogue_id}: {e}")
            
            dialogue.sync_status = SyncStatus.FAILED
            dialogue.sync_msg = str(e)
            session.commit()

            # Re-raise to trigger retry
            raise
