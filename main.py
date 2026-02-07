"""
NextSoundWave - Self-hosted Music/Podcast Streaming Service
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from api.routes import router
from api.errors import setup_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: initialize services
    print("🚀 NextSoundWave server starting...")
    yield
    # Shutdown: cleanup
    print("👋 NextSoundWave server shutting down...")


# Create FastAPI application
app = FastAPI(
    title="NextSoundWave",
    description="Self-hosted music and podcast streaming via YouTube",
    version="1.0.0",
    lifespan=lifespan
)

# Setup error handlers
setup_error_handlers(app)

# Include API routes
app.include_router(router, prefix="/api", tags=["API"])

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="web"), name="static")


@app.get("/")
async def root():
    """Serve the main frontend page."""
    return {
        "service": "NextSoundWave",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
