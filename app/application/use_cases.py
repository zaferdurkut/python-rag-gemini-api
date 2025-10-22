from typing import Optional, List, Dict, Any
from app.domain.document_repositories import DocumentRepository
from app.domain.rag_repositories import RAGRepository
from app.domain.document_entities import Document, SearchResult, CollectionStats
from app.domain.rag_entities import RAGContext
from app.core.config import settings
from app.infrastructure.file_processor import FileProcessor
from app.core.logging import get_logger


FILE_PROCESSOR_AVAILABLE = True

logger = get_logger(__name__)


class DocumentUseCase:
    """Document management use case implementation."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        rag_repository: RAGRepository,
        file_processor: FileProcessor,
    ):
        self.document_repository = document_repository
        self.rag_repository = rag_repository
        self.file_processor = file_processor

    async def add_documents(
        self,
        documents: list[str],
        metadatas: Optional[list[dict]] = None,
        ids: Optional[list[str]] = None,
    ) -> list[str]:
        """Add documents to the knowledge base."""
        return await self.document_repository.add_documents(documents, metadatas, ids)

    async def search_documents(
        self, query: str, n_results: int = 5, where: Optional[dict] = None
    ) -> List[SearchResult]:
        """Search for similar documents."""
        return await self.document_repository.search_documents(query, n_results, where)

    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a specific document by ID."""
        return await self.document_repository.get_document(document_id)

    async def update_document(
        self, document_id: str, document: str, metadata: Optional[dict] = None
    ) -> bool:
        """Update a document."""
        return await self.document_repository.update_document(
            document_id, document, metadata
        )

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        return await self.document_repository.delete_document(document_id)

    async def get_collection_stats(self) -> CollectionStats:
        """Get collection statistics."""
        return await self.document_repository.get_collection_stats()

    async def list_documents(self) -> List[Document]:
        """List all documents with their IDs and metadata."""
        return await self.document_repository.list_documents()

    async def get_rag_context(
        self, query: str, max_docs: Optional[int] = None
    ) -> RAGContext:
        """Get RAG context for a query with configurable parameters."""
        # Use config values or provided max_docs
        max_docs = max_docs or settings.RAG_MAX_CONTEXT_DOCS

        # Get RAG context using the repository
        return await self.rag_repository.get_rag_context(
            query=query,
            max_docs=max_docs,
            similarity_threshold=settings.RAG_DISTANCE_THRESHOLD,
        )

    async def process_and_add_files(
        self,
        files: List[Dict[str, Any]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Process uploaded files and add them to the knowledge base."""
        # Process all files
        processed_files = await self.file_processor.process_multiple_files(files)

        # Separate successful and failed processing
        successful_files = []
        failed_files = []

        for i, result in enumerate(processed_files):
            if result["success"] and result["content"].strip():
                successful_files.append(
                    {"content": result["content"], "metadata": result["metadata"]}
                )
            else:
                failed_files.append(
                    {
                        "filename": result["metadata"].get("filename", f"file_{i}"),
                        "error": result["metadata"].get("error", "Unknown error"),
                    }
                )

        # Add successful files to ChromaDB
        document_ids = []
        if successful_files:
            documents = [f["content"] for f in successful_files]
            file_metadatas = [f["metadata"] for f in successful_files]

            # Merge with provided metadatas if any
            if metadatas and len(metadatas) == len(successful_files):
                for i, metadata in enumerate(metadatas):
                    file_metadatas[i].update(metadata)

            document_ids = await self.document_repository.add_documents(
                documents, file_metadatas, ids
            )

        return {
            "successful_uploads": len(successful_files),
            "failed_uploads": len(failed_files),
            "document_ids": document_ids,
            "failed_files": failed_files,
            "total_processed": len(processed_files),
        }

    async def process_single_file(
        self,
        file_content: bytes,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a single file and add it to the knowledge base."""
        # Process the file
        result = await self.file_processor.process_file(file_content, filename)

        if not result["success"]:
            return {
                "success": False,
                "error": result["metadata"].get("error", "Unknown error"),
                "filename": filename,
            }

        if not result["content"].strip():
            return {
                "success": False,
                "error": "No text content extracted from file",
                "filename": filename,
            }

        # Prepare metadata
        file_metadata = result["metadata"]
        if metadata:
            file_metadata.update(metadata)

        # Add to repository
        document_ids = await self.document_repository.add_documents(
            [result["content"]],
            [file_metadata],
            [document_id] if document_id else None,
        )

        return {
            "success": True,
            "document_id": document_ids[0],
            "filename": filename,
            "text_length": len(result["content"]),
            "metadata": file_metadata,
        }
