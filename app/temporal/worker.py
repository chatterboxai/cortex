import logging
import asyncio
from temporalio.worker import Worker
from app.temporal.activities import sync_document_activity, sync_dialogue_activity
from app.temporal.workflows import DocumentSyncWorkflow, DialogueSyncWorkflow
from app.temporal.client import get_client

# Can change to logging.DEBUG for more detailed errors if needed
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)

async def main():
    client = await get_client()
    worker = Worker(
        client,
        task_queue="sync-tasks",
        workflows=[DocumentSyncWorkflow, DialogueSyncWorkflow],
        activities=[sync_document_activity, sync_dialogue_activity],
    )
    logger.info("Starting Temporal worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
