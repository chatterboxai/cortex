from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

@workflow.defn
class DocumentSyncWorkflow:
    @workflow.run
    async def run(self, document_id: str) -> str:
        await workflow.execute_activity(
            "sync_document_activity", 
            document_id,
            schedule_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(
            initial_interval=timedelta(seconds=5),
            maximum_interval=timedelta(minutes=1),
            maximum_attempts=5,
        ),
        )
        return "Document synced"

@workflow.defn
class DialogueSyncWorkflow:
    @workflow.run
    async def run(self, dialogue_id: str) -> str:
        await workflow.execute_activity(
            "sync_dialogue_activity",
            dialogue_id,
            schedule_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(
            initial_interval=timedelta(seconds=5),
            maximum_interval=timedelta(minutes=1),
            maximum_attempts=5,
        ),
        )
        return "Dialogue synced"