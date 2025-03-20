from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from app.routers import users

app = FastAPI(
    title="ChatterBox API",
    description="API for ChatterBox application",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# app.include_router(users.router)


@app.get("/")
async def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to ChatterBox API",
        "docs": "/docs",
        "version": app.version
    }

