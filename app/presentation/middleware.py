import time
import logging
import traceback
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url}")

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {response.status_code} - " f"Process time: {process_time:.4f}s"
        )

        # Add process time to response headers
        response.headers["X-Process-Time"] = str(process_time)

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Clean old entries
        self.clients = {
            ip: timestamps
            for ip, timestamps in self.clients.items()
            if any(t > current_time - self.period for t in timestamps)
        }

        # Check rate limit
        if client_ip in self.clients:
            self.clients[client_ip] = [
                t for t in self.clients[client_ip] if t > current_time - self.period
            ]

            if len(self.clients[client_ip]) >= self.calls:
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={"Retry-After": str(self.period)},
                )

        # Add current request
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        self.clients[client_ip].append(current_time)

        response = await call_next(request)
        return response


def get_cors_middleware():
    """Get CORS middleware with configured settings."""
    return CORSMiddleware(
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def get_trusted_host_middleware():
    """Get trusted host middleware."""
    return TrustedHostMiddleware(
        allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
    )


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to catch any unhandled errors and ensure JSON responses."""

    async def dispatch(self, request: Request, call_next):
        try:
            logger.debug(f"Processing request: {request.method} {request.url}")
            response = await call_next(request)
            logger.debug(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Unhandled error in middleware: {str(e)}", exc_info=True)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Request path: {request.url.path}")

            # Ensure we always return a JSON response
            try:
                error_response = JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "type": "MiddlewareError",
                            "message": "An unexpected error occurred in middleware",
                            "path": str(request.url.path),
                            "exception_type": type(e).__name__,
                            "exception_message": str(e),
                        }
                    },
                )
                logger.info("Created JSON error response successfully")
                return error_response
            except Exception as json_error:
                logger.critical(
                    f"Failed to create JSON error response in middleware: {json_error}"
                )
                # Return a basic text response as last resort
                return Response(
                    content="Internal Server Error",
                    status_code=500,
                    media_type="text/plain",
                )
