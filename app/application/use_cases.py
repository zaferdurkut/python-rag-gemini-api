from typing import Optional, List, Dict, Any
from app.infrastructure.chroma_repository import ChromaRepository
from app.core.config import settings
from app.infrastructure.file_processor import FileProcessor
from app.core.logging import get_logger


FILE_PROCESSOR_AVAILABLE = True

logger = get_logger(__name__)


class DocumentUseCase:
    """Document management use case implementation."""

    def __init__(self):
        self.chroma_repository = ChromaRepository(
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
            collection_name=settings.CHROMA_COLLECTION_NAME,
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_SERVER_PORT,
        )
        self.file_processor = FileProcessor()

    async def add_documents(
        self,
        documents: list[str],
        metadatas: Optional[list[dict]] = None,
        ids: Optional[list[str]] = None,
    ) -> list[str]:
        """Add documents to the knowledge base."""
        return await self.chroma_repository.add_documents(documents, metadatas, ids)

    async def search_documents(
        self, query: str, n_results: int = 5, where: Optional[dict] = None
    ) -> list[dict]:
        """Search for similar documents."""
        return await self.chroma_repository.search_documents(query, n_results, where)

    async def get_document(self, document_id: str) -> Optional[dict]:
        """Get a specific document by ID."""
        return await self.chroma_repository.get_document(document_id)

    async def update_document(
        self, document_id: str, document: str, metadata: Optional[dict] = None
    ) -> bool:
        """Update a document."""
        return await self.chroma_repository.update_document(
            document_id, document, metadata
        )

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        return await self.chroma_repository.delete_document(document_id)

    async def get_collection_stats(self) -> dict:
        """Get collection statistics."""
        return await self.chroma_repository.get_collection_stats()

    async def list_documents(self) -> list[dict]:
        """List all documents with their IDs and metadata."""
        return await self.chroma_repository.list_documents()

    async def reset_collection(self) -> bool:
        """Reset the collection."""
        return await self.chroma_repository.reset_collection()

    async def search_for_rag_context(self, query: str, max_results: int = 3) -> str:
        """Search for relevant documents to use as RAG context."""
        results = await self.search_documents(query, max_results)

        if not results:
            return ""

        # Combine the most relevant documents as context
        context_parts = []
        for result in results:
            if (
                result.get("distance", 1.0) < 0.8
            ):  # Only include highly relevant results
                context_parts.append(result["document"])

        context = "\n\n".join(context_parts)
        return context

    async def get_rag_context(
        self, query: str, max_docs: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get RAG context for a query with configurable parameters."""
        # Use config values or provided max_docs
        max_docs = max_docs or settings.RAG_MAX_CONTEXT_DOCS

        # Search for relevant documents
        search_results = await self.chroma_repository.search_documents(
            query, n_results=max_docs
        )

        if not search_results:
            logger.warning("No search results found for RAG context")
            return {
                "context": "",
                "sources": [],
                "total_found": 0,
                "included_docs": 0,
            }

        # Extract context from search results using config threshold
        context_parts = []
        sources = []
        included_docs = 0

        for result in search_results:
            distance = result.get("distance", 1.0)

            # Use config threshold
            if distance < settings.RAG_DISTANCE_THRESHOLD:
                context_parts.append(result["document"])
                included_docs += 1

                # Create source with config preview length
                preview_length = settings.RAG_DOCUMENT_PREVIEW_LENGTH
                document_preview = (
                    result["document"][:preview_length] + "..."
                    if len(result["document"]) > preview_length
                    else result["document"]
                )

                sources.append(
                    {
                        "document": document_preview,
                        "score": 1 - distance,
                        "metadata": result.get("metadata", {}),
                        "distance": distance,
                    }
                )

                logger.info(f"Result included: distance={distance:.4f}")
            else:
                logger.info(
                    f"Result excluded: distance={distance:.4f} (threshold: {settings.RAG_DISTANCE_THRESHOLD})"
                )

        # Combine context
        rag_context = "\n\n".join(context_parts)

        logger.info(
            f"RAG context: {included_docs}/{len(search_results)} docs, "
            f"{len(rag_context)} characters"
        )

        return {
            "context": rag_context,
            "sources": sources,
            "total_found": len(search_results),
            "included_docs": included_docs,
        }

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

            document_ids = await self.chroma_repository.add_documents(
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

        # Add to ChromaDB
        document_ids = await self.chroma_repository.add_documents(
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
