import uuid
from typing import Any
from pydantic import BaseModel

from app.services.chatbot import ChatbotService
from llama_index.core import VectorStoreIndex
from app.services.rag.embeddings import EmbeddingsService
from app.schemas.chatbot_settings import ChatbotSettings
from app.services.rag.vectorstore import VectorStoreService
import logging

logger = logging.getLogger(__name__)


class VsiService(BaseModel):
    
    @staticmethod
    def get_vsi(chatbot_id: uuid.UUID, **kwargs: Any) -> VectorStoreIndex:
        try:
            
            chatbot = ChatbotService.find_by_id(chatbot_id)
            if not chatbot:
                raise ValueError("Chatbot not found")

            # get the embedding model
            chatbot_settings = ChatbotSettings.model_validate(chatbot.settings)
            embedding_model = EmbeddingsService.get_embedding_model(chatbot_settings.embedding_model)
            logger.debug('embedding model found for chatbot')
            
            vector_store = VectorStoreService.get_vector_store(
                table_name=f'{str(chatbot_id)}',
                embed_dim=chatbot_settings.embedding_model.dimensions
            )
            logger.debug('vector store gotten for chatbot')
            
            vsi = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=embedding_model
            )
            logger.debug('vsi created for chatbot')
            return vsi
        except Exception as e:
            logger.error(f'error in get_vsi: {e}')
            raise e
