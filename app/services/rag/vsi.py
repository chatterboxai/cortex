
import uuid
from typing import Any
from pydantic import BaseModel

from app.services.chatbot import ChatbotService
from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from app.models.chatbot import Chatbot
from app.services.rag.embeddings import EmbeddingsService


class VsiService(BaseModel):
    
    @staticmethod
    def get_vsi(chatbot_id: uuid.UUID, **kwargs: Any) -> VectorStoreIndex:
        chatbot = ChatbotService.find_by_id(chatbot_id)
        if not chatbot:
            raise ValueError("Chatbot not found")
        
        # get the embedding model
        embedding_model = EmbeddingsService.get_embedding_model(chatbot.settings.embedding_model)
        
        vsi = VectorStoreIndex(embed_model=embedding_model)
        return vsi
