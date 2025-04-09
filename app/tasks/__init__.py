# Tasks package for celery tasks
from .documents import process_document_queue, process_document
from .dialogues import process_dialogue_queue, process_dialogue