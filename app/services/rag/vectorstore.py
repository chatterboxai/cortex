from typing import Any
from llama_index.vector_stores.postgres import PGVectorStore
import os

from pydantic import BaseModel

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


class VectorStoreService:
    
    @staticmethod
    def get_vector_store(table_name: str, embed_dim: int, **kwargs: Any) -> PGVectorStore:
        vector_store = PGVectorStore.from_params(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            table_name=table_name,
            perform_setup=False,
            embed_dim=embed_dim,
            **kwargs
        )

        return vector_store
    
    @staticmethod
    async def create_vector_store(table_name: str, embed_dim: int, **kwargs: Any) -> None:
        vector_store = PGVectorStore.from_params(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            table_name=table_name,
            perform_setup=True,
            embed_dim=embed_dim,
            **kwargs
        )
        vector_store._initialize()
        await vector_store.close()
