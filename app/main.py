from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import logging

from fastapi.responses import JSONResponse

from app.auth.middleware import CognitoAuthMiddleware
from app.routers import users

from app.routers import chat

from app.routers import chatbot
from app.routers import dialogues

from app.routers import document
from app.core.logging import setup_logging
from app.db.client import engine, async_session_factory

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler


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
    title='ChatterBox API',
    description='API for ChatterBox application',
    version='0.1.0',
    lifespan=lifespan
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.exception(f'error caught in http_exception_handler: {exc}')
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,

    allow_origins=['*'],  # In production, replace with specific origins

    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Add Cognito authentication middleware
app.add_middleware(
    CognitoAuthMiddleware,

    exclude_paths=['/docs', '/redoc', '/openapi.json', '/', '/health', '/health/db', '/api/v1/chatbots/public/chat-test', '/api/v1/chatbots/public/chat'],
    exclude_methods=['OPTIONS'],

)

# Include routers
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(chatbot.router)
app.include_router(chatbot.public_router)
app.include_router(dialogues.router)
app.include_router(document.router)


@app.get('/')
async def read_root():
    return {
        'message': 'Welcome to ChatterBox API',
        'docs': '/docs',
        'version': app.version
    }


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/db")
async def db_health_check():
    try:
        async with async_session_factory() as session:
            from sqlalchemy import text

            await session.execute(text('SELECT 1'))
            
        return {'status': 'healthy', 'database': 'connected'}
    except Exception as e:
        # Return 503 Service Unavailable to indicate database issues
        return {'status': 'unhealthy', 'error': str(e)}, 503

