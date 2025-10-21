"""
Custom exceptions for the RAG system.
"""

from typing import Optional, Dict, Any


class RAGBaseException(Exception):
    """Base exception for RAG system."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DocumentNotFoundError(RAGBaseException):
    """Raised when a document is not found."""

    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document with ID '{document_id}' not found",
            status_code=404,
            details={"document_id": document_id},
        )


class DocumentProcessingError(RAGBaseException):
    """Raised when document processing fails."""

    def __init__(self, filename: str, reason: str):
        super().__init__(
            message=f"Failed to process document '{filename}': {reason}",
            status_code=400,
            details={"filename": filename, "reason": reason},
        )


class UnsupportedFileTypeError(RAGBaseException):
    """Raised when file type is not supported."""

    def __init__(self, filename: str, supported_types: list):
        super().__init__(
            message=f"Unsupported file type for '{filename}'. Supported types: {', '.join(supported_types)}",
            status_code=400,
            details={"filename": filename, "supported_types": supported_types},
        )


class FileSizeExceededError(RAGBaseException):
    """Raised when file size exceeds limit."""

    def __init__(self, filename: str, file_size: int, max_size: int):
        super().__init__(
            message=f"File '{filename}' too large. Size: {file_size} bytes, Max: {max_size} bytes",
            status_code=400,
            details={
                "filename": filename,
                "file_size": file_size,
                "max_size": max_size,
            },
        )


class ChromaDBError(RAGBaseException):
    """Raised when ChromaDB operation fails."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"ChromaDB {operation} failed: {reason}",
            status_code=500,
            details={"operation": operation, "reason": reason},
        )


class GeminiAPIError(RAGBaseException):
    """Raised when Gemini API operation fails."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Gemini API {operation} failed: {reason}",
            status_code=500,
            details={"operation": operation, "reason": reason},
        )


class ValidationError(RAGBaseException):
    """Raised when input validation fails."""

    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Validation error for field '{field}': {reason}",
            status_code=400,
            details={"field": field, "reason": reason},
        )


class ServiceUnavailableError(RAGBaseException):
    """Raised when a service is unavailable."""

    def __init__(self, service: str, reason: str):
        super().__init__(
            message=f"Service '{service}' is unavailable: {reason}",
            status_code=503,
            details={"service": service, "reason": reason},
        )
