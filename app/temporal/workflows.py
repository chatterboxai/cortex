from datetime import timedelta
from uuid import UUID
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.schemas.document import DocumentSyncStatusUpdateRequest
    from app.temporal.activities.documents import DocumentActivities
    from app.temporal.activities.documents import PdfDocumentActivities
    from app.models.dialogue import SyncStatus
    from app.models.document import Document
    from app.temporal.activities.documents import DocumentSyncDTO



@workflow.defn
class DocumentSyncWorkflow:

    document_retry_policy = RetryPolicy(
        initial_interval=timedelta(seconds=5),
        maximum_attempts=5,
        maximum_interval=timedelta(seconds=5),
        non_retryable_error_types=['DocumentNotFoundError', 'DocumentUnsupportedError'],
    )

    document_parse_retry_policy = RetryPolicy(
        initial_interval=timedelta(minutes=1),
        maximum_attempts=5,
        maximum_interval=timedelta(minutes=1),
    )

    document_sync_retry_policy = RetryPolicy(
        initial_interval=timedelta(seconds=5),
        maximum_attempts=5,
        maximum_interval=timedelta(seconds=5),
    )
    
    @workflow.run
    async def run(self, document_id: UUID) -> str:
        document_sync_status_update_request = DocumentSyncStatusUpdateRequest(
            document_id=document_id,
            sync_status=SyncStatus.IN_PROGRESS,
            sync_msg='Document sync started',
        )

        document_with_chatbot_dto = await workflow.execute_activity_method(
            DocumentActivities.update_sync_status,
            document_sync_status_update_request,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=self.document_retry_policy,
        )

        
        parsed_markdown = await workflow.execute_activity_method(
            PdfDocumentActivities.parse_document,
            document_with_chatbot_dto.document,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=self.document_parse_retry_policy,
        )

        document_sync_dto = DocumentSyncDTO(
            document=document_with_chatbot_dto.document,
            chatbot=document_with_chatbot_dto.chatbot,
            text_to_sync=parsed_markdown,
        )
        
        await workflow.execute_activity_method(
            PdfDocumentActivities.sync_to_vector_store,
            document_sync_dto,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=self.document_sync_retry_policy,
        )

        document_sync_status_update_request = DocumentSyncStatusUpdateRequest(
            document_id=document_id,
            sync_status=SyncStatus.SYNCED,
            sync_msg='Document sync completed',
        )

        document: Document = await workflow.execute_activity_method(
            DocumentActivities.update_sync_status,
            document_sync_status_update_request,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=self.document_retry_policy,
        )
        
        return f"Document {str(document_id)} synced"

# @workflow.defn
# class DialogueSyncWorkflow:
#     @workflow.run
#     async def run(self, dialogue_id: str) -> str:
#         await workflow.execute_activity(
#             "sync_dialogue_activity",
#             dialogue_id,
#             schedule_to_close_timeout=timedelta(minutes=3),
#             retry_policy=RetryPolicy(
#             initial_interval=timedelta(seconds=5),
#             maximum_interval=timedelta(minutes=1),
#             maximum_attempts=5,
#         ),
#         )
#         return "Dialogue synced"