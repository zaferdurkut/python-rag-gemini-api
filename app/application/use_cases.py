from typing import Optional
from app.infrastructure.chroma_repository import ChromaRepository
from app.core.config import settings


class DocumentUseCase:
    """Document management use case implementation."""

    def __init__(self):
        self.chroma_repository = ChromaRepository(
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
            collection_name=settings.CHROMA_COLLECTION_NAME,
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_SERVER_PORT,
        )

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

    async def reset_collection(self) -> bool:
        """Reset the collection."""
        return await self.chroma_repository.reset_collection()

    async def search_for_rag_context(self, query: str, max_results: int = 3) -> str:
        """Search for relevant documents to use as RAG context."""
        try:
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

        except Exception as e:
            return ""
