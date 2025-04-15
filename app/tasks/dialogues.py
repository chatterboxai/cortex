import logging
from celery import shared_task, Task
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.dialogue import Dialogue, SyncStatus
from app.services.dialogues import DialogueService
from app.db.client import sync_session_factory
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import Document as LlamaIndexDocument
from llama_index.core.ingestion import IngestionPipeline

from app.services.rag.embeddings import EmbeddingsService
from app.services.rag.vectorstore import VectorStoreService
from app.schemas.chatbot_settings import ChatbotSettings, EmbeddingModel

import asyncio
from app.temporal.client import get_client
from app.temporal.workflows import DialogueSyncWorkflow
from typing import Optional

logger = logging.getLogger(__name__)

markdown_parser = MarkdownNodeParser()


async def process_dialogue_queue_temporal(dialogue_id: Optional[UUID] = None):
    logger.info("Scanning for dialogues to sync (Temporal)")

    try:
        if dialogue_id:
            logger.info(f"Fetching dialogue {dialogue_id}")
            dialogue = DialogueService.get_by_id(dialogue_id)
            if not dialogue:
                logger.warning(f"No dialogue found for ID: {dialogue_id}")
                return
            dialogues = [dialogue]
        else:
            dialogues = DialogueService.get_dialogues_to_sync()

        client = await get_client()

        for dialogue in dialogues:
            logger.info(f"Submitting Temporal workflow for dialogue {dialogue.id}")
            await client.start_workflow(
                DialogueSyncWorkflow.run,
                str(dialogue.id),
                id=f"dialogue-sync-{dialogue.id}",
                task_queue="sync-tasks"
            )

        logger.info(f"Queued {len(dialogues)} dialogues via Temporal")

    except Exception as e:
        logger.exception("Error while queuing dialogues with Temporal")


# @shared_task(
#     name="app.tasks.dialogues.process_dialogue",
#     bind=True,
#     autoretry_for=(Exception,),
#     retry_backoff=True,
#     retry_backoff_max=60,
#     retry_kwargs={'max_retries': 5}
# )
# def process_dialogue(self: Task, dialogue_id: str) -> None:
#     """
#     Process a single dialogue.
    
#     Args:
#         dialogue_id: UUID string of the dialogue to process
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
    
#     logger.info(f"Processing dialogue {dialogue_id}")
    
#     # Convert string to UUID
#     _dialogue_id = UUID(dialogue_id)
    
#     with sync_session_factory() as session:
#         # load chatbot when dialogue is loaded
#         query = select(Dialogue).options(selectinload(Dialogue.chatbot)).where(Dialogue.id == _dialogue_id)
#         dialogue = session.execute(query).scalar_one_or_none()
#         if not dialogue:
#             logger.error(f"Dialogue {_dialogue_id} not found")
#             return
#         try:
            
#             dialogue.sync_status = SyncStatus.IN_PROGRESS
#             session.commit()
            
#             logger.debug(f"Dialogue chatbot settings: {dialogue.chatbot.settings}")
#             chatbot_settings = ChatbotSettings.model_validate(dialogue.chatbot.settings)
#             logger.debug("Chatbot settings validated")

#             em_settings = EmbeddingModel.model_validate(chatbot_settings.embedding_model)
#             logger.debug("Embedding model validated")

#             vector_store = VectorStoreService.get_vector_store(str(dialogue.chatbot.id), em_settings.dimensions)
#             logger.debug("Vector store gotten")
            
#             questions = "\n".join(dialogue.questions)
#             text_to_sync = f"Questions: {questions}\n\nAnswer: {dialogue.answer}\n\n"
#             doc_to_sync = LlamaIndexDocument(id_=str(_dialogue_id), text=text_to_sync)

#             embedding_model = EmbeddingsService.get_embedding_model(em_settings)

#             logger.debug('running ingestion pipeline to sync dialogue to vector store')

#             pipeline = IngestionPipeline(
#                 transformations=[
#                     embedding_model
#                 ],
#                 vector_store=vector_store
#             )

#             pipeline.run(documents=[doc_to_sync])  # TODO: this doesnt delete previous documents but ignore for now
#             logger.debug('pipeline run complete')
            
#             # Update dialogue status to success using synchronous method
#             dialogue.sync_status = SyncStatus.SYNCED
#             session.commit()

#             logger.debug(f"Document {dialogue_id} synced to vector store")
#         except Exception as e:
#             logger.error(f"Error processing dialogue {dialogue_id}: {e}")
            
#             dialogue.sync_status = SyncStatus.FAILED
#             dialogue.sync_msg = str(e)
#             session.commit()

#             # Re-raise to trigger retry
#             raise
