from typing import Annotated
from pydantic import BaseModel, Field


class EmbeddingModel(BaseModel):
    provider: Annotated[str, Field(
        description="The provider of the embedding model"
    )]
    name: Annotated[str, Field(
        description="The name of the embedding model"
    )]
    dimensions: Annotated[int, Field(
        description="The dimensions of the embedding model"
    )]


class ChatbotSettings(BaseModel):
    embedding_model: EmbeddingModel
    