"""Dependency injection setup for the application."""

from app.infrastructure.chroma_repository import ChromaRepository
from app.infrastructure.file_processor import FileProcessor
from app.application.use_cases import DocumentUseCase
from app.core.config import settings


def get_document_repository() -> ChromaRepository:
    """Get the document repository instance."""
    return ChromaRepository(
        persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
        collection_name=settings.CHROMA_COLLECTION_NAME,
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_SERVER_PORT,
    )


def get_file_processor() -> FileProcessor:
    """Get the file processor instance."""
    return FileProcessor()


def get_document_use_case() -> DocumentUseCase:
    """Get the document use case instance."""
    repository = get_document_repository()
    file_processor = get_file_processor()
    return DocumentUseCase(
        document_repository=repository,
        rag_repository=repository,  # Same repository implements both interfaces
        file_processor=file_processor,
    )
