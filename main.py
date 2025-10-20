from fastapi import FastAPI, Request

# TrustedHostMiddleware import removed
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.presentation.api import router
from app.presentation.middleware import (
    LoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
)

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up the application...")
    logger.info("Application started successfully.")

    yield

    # Shutdown
    logger.info("Shutting down the application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to RAG System with ChromaDB",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "features": ["Document Management", "Vector Search", "ChromaDB Integration"],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["documents"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=2000, reload=settings.DEBUG)
