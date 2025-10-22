from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.exceptions import RAGBaseException
from app.core.logging import get_logger
from app.presentation.documents.controller import router as documents_router
from app.presentation.chat.controller import router as chat_router
from app.presentation.middleware import (
    LoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
)
from app.presentation.error_handler import (
    rag_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up the application...")
    logger.info("Application started successfully.")

    yield

    # Shutdown
    logger.info("Shutting down the application...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
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

    # Add exception handlers
    app.add_exception_handler(RAGBaseException, rag_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    @app.get("/")
    async def read_root():
        """Root endpoint."""
        return {"message": "Welcome to RAG System with ChromaDB"}

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    # Include API routes
    app.include_router(documents_router, prefix="/api/v1", tags=["documents"])
    app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

    return app


# Create the app instance
app = create_app()
