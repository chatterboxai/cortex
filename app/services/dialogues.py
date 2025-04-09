from typing import Sequence
import uuid
from app.models.chatbot import Chatbot
from app.models.users import User
from sqlalchemy import select

from app.models.dialogue import Dialogue, SyncStatus
from app.db.client import async_session_factory, sync_session_factory
from sqlalchemy.orm import selectinload

class DialogueService:
    
    @classmethod
    async def create_dialogue(
            cls,
            chatbot: uuid.UUID,
            name: str,
            questions: list[str],
            answer: str
        ):
        async with async_session_factory() as session:
            dialogue = Dialogue(
                chatbot_id=chatbot,
                name=name,
                questions=questions,
                answer=answer,
                sync_status=SyncStatus.NA,
                sync_msg=''
            )
            session.add(dialogue)
            await session.commit()
            await session.refresh(dialogue)
            return dialogue
        
    @classmethod
    async def find_dialogue_by_id(cls, dialogue_id: uuid.UUID) -> Dialogue | None:
        """Find specific dialogue"""
        async with async_session_factory() as session:
            query = select(Dialogue).where(Dialogue.id == dialogue_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
    @classmethod    
    async def find_dialogue_by_chatbot(cls, chatbot_id: uuid.UUID) -> Sequence[Dialogue]:
        """Find all dialogue belonging to chatbot"""
        async with async_session_factory() as session:
            query = select(Dialogue).where(Dialogue.chatbot_id == chatbot_id)
            result = await session.execute(query)
            return result.scalars().all()
            
    # @classmethod
    # async def find_answer_by_question(cls, question:str, chatbot_id: uuid.UUID) -> Dialogue:
    #     """Find all dialogue belonging to chatbot"""
    #     async with async_session_factory() as session:
    #         query = (
    #         select(Dialogue)
    #         .where(Dialogue.chatbot_id == chatbot_id)
    #         .where(Dialogue.questions.any(question))  # Filter by question list
    #     )
    #         result = await session.execute(query)
    #         return result.scalar_one_or_none()
                    
    # async def find_dialogue_by_user(user_id: uuid.UUID) -> Sequence[Dialogue]:
    #         """Find all dialogue belonging to user"""
    #         async with async_session_factory() as session:
    #             query = select(Dialogue).where(Dialogue._id == user_id)
    #             result = await session.execute(query)
    #             return result.scalars().all()

    @classmethod
    async def edit_dialogue(
            cls, 
            dialogue_id: uuid.UUID, 
            questions: list[str], 
            answer: str
        ) -> Dialogue:
        """Find all dialogue belonging to chatbot"""
        async with async_session_factory() as session:
            query = (
            select(Dialogue)
            .where(Dialogue.id == dialogue_id)
        )
            result = await session.execute(query)
            dialogue =  result.scalar_one_or_none()
            
            dialogue.questions = questions
            dialogue.answer = answer
            dialogue.sync_status = SyncStatus.NA

            await session.commit()
            await session.refresh(dialogue)

            return dialogue
                
    @classmethod            
    async def delete_dialogue_by_id(cls, dialogue_id: uuid.UUID) -> Dialogue:
        async with async_session_factory() as session:
                query = (
                select(Dialogue)
                .where(Dialogue.id == dialogue_id)
            )
                result = await session.execute(query)
                dialogue =  result.scalar_one_or_none()
                await session.delete(dialogue)
                await session.commit()
                return dialogue
            
    @classmethod
    def update_sync_status(
            cls, 
            dialogue_id: uuid.UUID, 
            sync_status: SyncStatus,
            sync_msg: str = None
        ) -> Dialogue:
            """
            Synchronous version of update_sync_status.
            Update the sync status of a dialogue using synchronous SQLAlchemy.
            """
            from sqlalchemy.orm import Session
            from app.db.client import sync_engine

            with Session(sync_engine) as session:
                dialogue = session.get(Dialogue, dialogue_id)
                if not dialogue:
                    raise ValueError(f"dialogue with id {dialogue_id} not found")
                
                dialogue.sync_status = sync_status
                if sync_msg:
                    dialogue.sync_msg = sync_msg
                
                session.add(dialogue)
                session.commit()
                session.refresh(dialogue)
                
                return dialogue
        
    @classmethod
    def get_dialogues_to_sync(cls, limit: int = 10) -> list[Dialogue]:
        with sync_session_factory() as session:
            query = select(Dialogue).where(
                Dialogue.sync_status.in_([SyncStatus.NA, SyncStatus.FAILED])
            ).limit(limit)

            result = session.execute(query)
            return list(result.scalars().all())
