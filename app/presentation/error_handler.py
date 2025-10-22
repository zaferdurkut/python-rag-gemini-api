"""
Error handlers for the RAG system.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback
from typing import Any, Dict

from app.core.exceptions import RAGBaseException

logger = logging.getLogger(__name__)


async def rag_exception_handler(request: Request, exc: RAGBaseException):
    """Handle custom RAG exceptions."""
    logger.error(f"RAG Exception: {exc.message} - {exc.details}")

    error_content = {
        "error": {
            "type": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "path": str(request.url.path),
        }
    }

    return create_safe_json_response(exc.status_code, error_content, request)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation Error: {exc.errors()}")

    error_content = {
        "error": {
            "type": "ValidationError",
            "message": "Request validation failed",
            "details": exc.errors(),
            "path": str(request.url.path),
        }
    }

    return create_safe_json_response(422, error_content, request)


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.detail}")

    error_content = {
        "error": {
            "type": "HTTPException",
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
        }
    }

    return create_safe_json_response(exc.status_code, error_content, request)


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    # Ensure we always return a proper JSON response
    try:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "details": {"exception": str(exc)},
                    "path": str(request.url.path),
                }
            },
        )
    except Exception as json_error:
        # If even JSON response fails, return a basic error
        logger.critical(f"Failed to create JSON error response: {json_error}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "CriticalError",
                    "message": "An unexpected error occurred and error handling failed",
                    "path": str(request.url.path),
                }
            },
        )


def create_safe_json_response(
    status_code: int, content: Dict[str, Any], request: Request
) -> JSONResponse:
    """Create a safe JSON response that handles any serialization errors."""
    try:
        return JSONResponse(status_code=status_code, content=content)
    except Exception as e:
        logger.critical(f"Failed to create JSON response: {e}")
        # Return a minimal safe response
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "SerializationError",
                    "message": "Failed to serialize error response",
                    "path": str(request.url.path),
                }
            },
        )


async def catch_all_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for any unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    # Get traceback for debugging (only in debug mode)
    traceback_str = None
    if logger.isEnabledFor(logging.DEBUG):
        traceback_str = traceback.format_exc()

    error_content = {
        "error": {
            "type": "UnhandledException",
            "message": "An unhandled error occurred",
            "path": str(request.url.path),
            "exception_type": type(exc).__name__,
        }
    }

    # Add traceback only in debug mode
    if traceback_str:
        error_content["error"]["traceback"] = traceback_str

    return create_safe_json_response(500, error_content, request)


def safe_endpoint_wrapper(func):
    """Decorator to wrap endpoint functions with error handling."""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in endpoint {func.__name__}: {str(e)}", exc_info=True)
            # Let the global exception handler deal with it
            raise

    return wrapper
