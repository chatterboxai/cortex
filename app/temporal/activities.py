import logging
from uuid import UUID
from temporalio import activity

from app.services.document import DocumentService
from app.services.dialogues import DialogueService

logger = logging.getLogger(__name__)

@activity.defn(name="sync_document_activity")
async def sync_document_activity(document_id: str):
    logger.info(f"Running sync_document_activity for {document_id}")
    try:
        DocumentService.sync_to_vector_store(UUID(document_id))
    except Exception as e:
        logger.exception("Failed to sync document")
        raise

@activity.defn(name="sync_dialogue_activity")
async def sync_dialogue_activity(dialogue_id: str):
    logger.info(f"Running sync_dialogue_activity for {dialogue_id}")
    try:
        DialogueService.sync_to_vector_store(UUID(dialogue_id))
    except Exception as e:
        logger.exception("Failed to sync dialogue")
        raise
