from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Sequence
from app.models.chatbot import Chatbot
from app.db.client import async_session_factory, sync_session_factory
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
                is_public=c.is_public,
                settings=c.settings.model_dump()
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
    async def afind_by_id(id: uuid.UUID,
                         load_owner: bool = False,
                         load_documents: bool = False,
                         load_dialogues: bool = False) -> Chatbot | None:
        """Find a chatbot by its ID."""
        async with async_session_factory() as session:
            query = select(Chatbot)
            if load_owner:
                query = query.options(selectinload(Chatbot.owner))
            if load_documents:
                query = query.options(selectinload(Chatbot.documents))
            if load_dialogues:
                query = query.options(selectinload(Chatbot.dialogues))
            query = query.where(Chatbot.id == id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
    @staticmethod
    def find_by_id(
        id: uuid.UUID,
        load_owner: bool = False,
        load_documents: bool = False,
        load_dialogues: bool = False) -> Chatbot | None:
        
        with sync_session_factory() as session:
            query = select(Chatbot)
            if load_owner:
                query = query.options(selectinload(Chatbot.owner))
            if load_documents:
                query = query.options(selectinload(Chatbot.documents))
            if load_dialogues:
                query = query.options(selectinload(Chatbot.dialogues))
            query = query.where(Chatbot.id == id)
            result = session.execute(query)
            return result.scalar_one_or_none()
        
    @staticmethod
    async def find_by_owner(owner_id: uuid.UUID) -> Chatbot:
        """Find a chatbot by its owner ID."""
        async with async_session_factory() as session:
            query = select(Chatbot).where(Chatbot.owner_id == owner_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()


