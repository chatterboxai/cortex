from sqlalchemy import select

from app.models.users import User
from app.db.client import async_session_factory


async def find_user_by_cognito_id(cognito_id: str) -> User | None:
    async with async_session_factory() as session:
        query = select(User).where(User.cognito_id == cognito_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def create_user(cognito_id: str, handle: str) -> User:
    async with async_session_factory() as session:
        user = User(
            cognito_id=cognito_id,
            handle=handle,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
