from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import logging

from fastapi.responses import JSONResponse

from app.auth.middleware import CognitoAuthMiddleware
from app.routers import users
from app.routers import chatbot
from app.core.logging import setup_logging
from app.db.client import engine
from app.db.client import async_session_factory

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
    exclude_paths=[
        '/docs', '/redoc', '/openapi.json', '/', 
        '/health', '/health/db'
    ],
    exclude_methods=['OPTIONS'],
)

# Include routers
app.include_router(users.router)
app.include_router(chatbot.router)


@app.get('/')
async def read_root():
    return {
        'message': 'Welcome to ChatterBox API',
        'docs': '/docs',
        'version': app.version
    }


@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.get('/health/db')
async def db_health_check():
    try:
        # Get current database connection status
        async with async_session_factory() as session:
            # Simple query to test database connectivity
            from sqlalchemy import text
            await session.execute(text('SELECT 1'))
            
        return {'status': 'healthy', 'database': 'connected'}
    except Exception as e:
        # Return 503 Service Unavailable to indicate database issues
        return {'status': 'unhealthy', 'error': str(e)}, 503
