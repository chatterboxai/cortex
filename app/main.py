from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.auth.middleware import CognitoAuthMiddleware
from app.routers import users
from app.routers import chat
from app.core.logging import setup_logging
from app.db.client import engine, async_session_factory

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.core.limiter import limiter

# Setup logging
logger = logging.getLogger(__name__)
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = await engine.connect()
    try:
        yield
    finally:
        await conn.close()
        await engine.dispose()

app = FastAPI(
    title="ChatterBox API",
    description="API for ChatterBox application",
    version="0.1.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Cognito authentication middleware
app.add_middleware(
    CognitoAuthMiddleware,
    exclude_paths=["/docs", "/redoc", "/openapi.json", "/", "/health", "/health/db", "/chat"],
    exclude_methods=["OPTIONS"],
)

# Include routers
app.include_router(users.router)
app.include_router(chat.router)

@app.get("/")
async def read_root():
    return {
        "message": "Welcome to ChatterBox API",
        "docs": "/docs",
        "version": app.version
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/db")
async def db_health_check():
    try:
        async with async_session_factory() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503