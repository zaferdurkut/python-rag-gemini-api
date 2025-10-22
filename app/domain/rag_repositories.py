from abc import ABC, abstractmethod
from .rag_entities import RAGContext


class RAGRepository(ABC):
    """Abstract repository interface for RAG operations."""

    @abstractmethod
    async def get_rag_context(
        self, query: str, max_docs: int = 5, similarity_threshold: float = 0.7
    ) -> RAGContext:
        """Get RAG context for a query.

        Args:
            query: User query
            max_docs: Maximum number of documents to include
            similarity_threshold: Minimum similarity score

        Returns:
            RAG context with relevant documents
        """
        pass
