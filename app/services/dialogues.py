from typing import Sequence
import uuid
from sqlalchemy import select

from app.models.dialogue import Dialogue
from app.db.client import async_session_factory


async def create_dialogue(
        user_id: str,
        chatbot: uuid.UUID,
        name: str,
        questions: list[str],
        answer: str
    ):
    async with async_session_factory() as session:
        dialogue = Dialogue(
            user_id,
            chatbot,
            name,
            questions,
            answer
        )
        session.add(dialogue)
        await session.commit()
        await session.refresh(dialogue)
        return dialogue
    
    
async def find_dialogue_by_id(dialogue_id: uuid.UUID) -> Dialogue | None:
    """Find specific dialogue"""
    async with async_session_factory() as session:
        query = select(Dialogue).where(Dialogue.id == dialogue_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    
async def find_dialogue_by_chatbot(chatbot_id: uuid.UUID) -> Sequence[Dialogue]:
        """Find all dialogue belonging to chatbot"""
        async with async_session_factory() as session:
            query = select(Dialogue).where(Dialogue.chatbot_id == chatbot_id)
            result = await session.execute(query)
            return result.scalars().all()
        

async def find_answer_by_question(question:str, chatbot_id: uuid.UUID) -> Dialogue:
        """Find all dialogue belonging to chatbot"""
        async with async_session_factory() as session:
            query = (
            select(Dialogue)
            .where(Dialogue.chatbot_id == chatbot_id)
            .where(Dialogue.question.in_(Dialogue.questions))  # Filter by question list
        )
            result = await session.execute(query)
            return result.scalar_one_or_none()
                
# async def find_dialogue_by_user(user_id: uuid.UUID) -> Sequence[Dialogue]:
#         """Find all dialogue belonging to user"""
#         async with async_session_factory() as session:
#             query = select(Dialogue).where(Dialogue._id == user_id)
#             result = await session.execute(query)
#             return result.scalars().all()