import logging
import asyncio
from temporalio.worker import Worker
from app.temporal.activities.documents import DocumentActivities, PdfDocumentActivities
from app.temporal.workflows import DocumentSyncWorkflow
from app.temporal.client import get_client
from app.temporal.shared import SYNC_DOCUMENT_TASK_QUEUE

# Can change to logging.DEBUG for more detailed errors if needed
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    client = await get_client()
    # Create instances of the activity classes
    document_activities = DocumentActivities()
    pdf_document_activities = PdfDocumentActivities()

    # Register the instance methods
    worker = Worker(
        client,
        task_queue=SYNC_DOCUMENT_TASK_QUEUE,
        workflows=[DocumentSyncWorkflow],
        activities=[
            document_activities.update_sync_status, 
            pdf_document_activities.parse_document, 
            pdf_document_activities.sync_to_vector_store
        ],
    )
    logger.info("Starting Temporal worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
