from fastapi import FastAPI, Request, HTTPException
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
    ErrorHandlingMiddleware,
)
from app.presentation.error_handler import (
    rag_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
    catch_all_exception_handler,
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

    # Add middleware (order matters - first added is outermost)
    app.add_middleware(ErrorHandlingMiddleware)  # Catch any remaining errors
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, calls=100, period=60)

    # Add exception handlers (order matters - most specific first)
    app.add_exception_handler(RAGBaseException, rag_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Add a comprehensive exception handler for all remaining exceptions
    @app.exception_handler(Exception)
    async def comprehensive_exception_handler(request: Request, exc: Exception):
        """Comprehensive exception handler to ensure JSON responses."""
        logger.error(
            f"Comprehensive exception handler caught: {str(exc)}", exc_info=True
        )
        logger.error(f"Exception type: {type(exc).__name__}")
        logger.error(f"Request path: {request.url.path}")

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "ComprehensiveExceptionHandler",
                    "message": "An unexpected error occurred",
                    "path": str(request.url.path),
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                }
            },
        )

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
