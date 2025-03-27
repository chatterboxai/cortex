from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine and session factory
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,                # Default connections in pool
    max_overflow=10,            # Additional connections when pool is full
    pool_timeout=30,            # Seconds to wait for a connection
    pool_recycle=1800,          # Recycle connections older than 30 min
    pool_pre_ping=True,         # Verify connection is valid before using
    echo=False                  # Set to True for SQL query logging
)

async_session_factory = async_sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)