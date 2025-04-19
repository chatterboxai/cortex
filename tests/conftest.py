import os
import asyncio
import logging
from fastapi.testclient import TestClient
from app.main import app
from fastapi import Depends
from app.auth.dependencies import get_authenticated_user, security
from app.schemas.cognito import CognitoClaims
from app.models.users import User
from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker
import pytest
from app.auth import middleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.services.users import create_user, find_user_by_cognito_id
import pytest_asyncio
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest_asyncio.fixture
async def postgres_db():
    """Set up PostgreSQL engine and session factory per test."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set. Example: postgresql+asyncpg://user:password@localhost:5432/testdb")
    
    logger.debug(f"Creating AsyncEngine in loop: {asyncio.get_running_loop()}")
    engine = create_async_engine(DATABASE_URL, echo=True, pool_size=5, max_overflow=10)
    TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False)
    
    logger.debug("Creating schema")
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield TestSessionLocal, engine
    
    logger.debug("Dropping schema")
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    logger.debug("Disposing engine")
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(postgres_db):
    """Provide a fresh async session for each test with dedicated connection."""
    TestSessionLocal, engine = postgres_db
    logger.debug(f"Creating session in loop: {asyncio.get_running_loop()}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        async with TestSessionLocal(bind=conn) as session:
            logger.debug("Starting transaction")
            await session.begin()
            yield session
            logger.debug("Rolling back transaction")
            await session.rollback()

@pytest.fixture
def client(postgres_db):
    """FastAPI TestClient with PostgreSQL setup."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_verify_cognito_token(monkeypatch):
    """Mock for cognito token verification."""
    from app.auth import cognito, middleware

    async def fake_verify_cognito_token(token: str) -> CognitoClaims:
        now = int(datetime.now(timezone.utc).timestamp())
        return CognitoClaims(
            sub="fake-cognito-id",
            username="testuser",
            iss="https://cognito-idp.us-east-1.amazonaws.com/us-east-1_Example",
            client_id="example-client-id",
            origin_jti="example-origin-jti",
            event_id="example-event-id",
            token_use="id",
            scope="openid profile email",
            auth_time=now,
            exp=now + 3600,
            iat=now,
            jti="example-jti"
        )

    monkeypatch.setattr(cognito, "verify_cognito_token", fake_verify_cognito_token)
    monkeypatch.setattr(middleware, "verify_cognito_token", fake_verify_cognito_token)

# async def override_get_authenticated_user():
#     """Override dependency to return fake user."""
#     return User(
#         cognito_id="fake-cognito-id",
#         handle="testuser"
#     )

async def override_get_authenticated_user():
    user = await find_user_by_cognito_id("fake-cognito-id")
    if not user:
        user = await create_user("fake-cognito-id", "testuser")
    return user


class FakeSecurity:
    """Mock security dependency."""
    async def __call__(self):
        return "fake.token.value"

@pytest.fixture(scope="session", autouse=True)
def override_dependencies():
    """Override FastAPI dependencies for testing."""
    app.dependency_overrides[get_authenticated_user] = override_get_authenticated_user
    app.dependency_overrides[security] = FakeSecurity()

