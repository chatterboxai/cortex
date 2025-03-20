from prisma import Prisma
from contextlib import asynccontextmanager

# Create a singleton Prisma client instance
db = Prisma()


async def init_db():
    """Initialize the database connection."""
    await db.connect()


async def close_db():
    """Close the database connection."""
    await db.disconnect()


@asynccontextmanager
async def get_db():
    """Get a database connection context manager."""
    try:
        yield db
    finally:
        # Connection is managed by the singleton
        pass 