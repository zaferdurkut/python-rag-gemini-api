from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

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
    get_cors_middleware,
    get_trusted_host_middleware,
)

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
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
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# TrustedHostMiddleware removed to avoid "Invalid host header" error


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to FastAPI Hexagonal Architecture",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["chat", "gemini"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
