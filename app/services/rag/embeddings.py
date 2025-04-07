
from llama_index.core.base.embeddings.base import BaseEmbedding
import os
from llama_index.embeddings.openai import OpenAIEmbedding
from app.schemas.chatbot_settings import EmbeddingModel

class EmbeddingsService:
    
    @staticmethod
    def get_embedding_model(em_settings: EmbeddingModel) -> BaseEmbedding:
        if em_settings.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")

            if em_settings.name == "text-embedding-ada-002":
                return OpenAIEmbedding(api_key=api_key, model="text-embedding-ada-002")
            elif em_settings.name == "text-embedding-3-large":
                return OpenAIEmbedding(api_key=api_key, model="text-embedding-3-large")
            elif em_settings.name == "text-embedding-3-small":
                return OpenAIEmbedding(api_key=api_key, model="text-embedding-3-small")
            else:
                raise ValueError("Invalid embedding model")
        
        else:
            raise ValueError("Invalid embedding model")
