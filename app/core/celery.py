import os
from celery import Celery

# Get connection URLs from environment variables or use defaults
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
BACKEND_URL = (f'db+postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:'
               f'{DB_PORT}/{DB_NAME}')

# Create a Celery instance
celery_app = Celery(
    'chatterbox',
    broker=REDIS_URL,
    # Use PostgreSQL as the result backend
    backend=BACKEND_URL,
)

# Configure PostgreSQL result backend
celery_app.conf.update(
    result_backend_transport_options={
        'max_retries': 3,
        'retry_policy': {
            'timeout': 5.0
        }
    }
)

# Set up Celery Beat schedule for recurring tasks
celery_app.conf.beat_schedule = {
    'process-documents-every-10-seconds': {
        'task': 'app.tasks.documents.process_document_queue',
        'schedule': 10.0,  # Run every 10 seconds
    },
    'sync-dialogues-every-10-seconds': {
        'task': 'app.tasks.dialogues.process_dialogue_queue',
        'schedule': 10.0,  # Run every 10 seconds
    },
}

# Include all task modules here
celery_app.conf.task_routes = {
    # 'app.tasks.documents.*': {'queue': 'documents'},
    'app.tasks.documents.process_document': {'queue': 'celery'},
    'app.tasks.documents.process_document_queue': {'queue': 'celery'},
    'app.tasks.dialogues.process_dialogue': {'queue': 'celery'},
    'app.tasks.dialogues.process_dialogue_queue': {'queue': 'celery'},
}

# Set timezone
celery_app.conf.timezone = 'UTC'

# Configure task serialization
celery_app.conf.accept_content = ['json']
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'

# Import tasks directly to ensure they're registered
import app.tasks  # noqa

# Automatically discover tasks in the project
celery_app.autodiscover_tasks(['app.tasks']) 