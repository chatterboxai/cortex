from sqlalchemy import select
from typing import Sequence
from app.models.chatbot import Chatbot
from app.db.client import async_session_factory
from app.schemas.chatbot import ChatbotCreate
import uuid

class ChatbotService:
    """Service for chatbot related operations."""

    @staticmethod
    async def create(c: ChatbotCreate) -> Chatbot:
        """Create a new chatbot."""
        async with async_session_factory() as session:
            chatbot = Chatbot(
                name=c.name,
                description=c.description,
                owner_id=c.owner_id,
                is_public=c.is_public
            )
            session.add(chatbot)
            await session.commit()
            await session.refresh(chatbot)
            return chatbot
        
    @staticmethod
    async def find_all(owner_id: uuid.UUID) -> Sequence[Chatbot]:
        """Find all chatbots belong to the current user."""
        async with async_session_factory() as session:
            query = select(Chatbot).where(Chatbot.owner_id == owner_id)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def find_by_id(id: str) -> Chatbot:
        """Find a chatbot by its ID."""
        async with async_session_factory() as session:
            chatbot = await session.get(Chatbot, id)
            return chatbot

    @staticmethod
    async def find_by_owner(owner_id: str) -> Chatbot:
        """Find a chatbot by its owner ID."""
        async with async_session_factory() as session:
            query = select(Chatbot).where(Chatbot.owner_id == owner_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()


