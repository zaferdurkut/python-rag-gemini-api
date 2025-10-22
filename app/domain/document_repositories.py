from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from .document_entities import Document, SearchResult, CollectionStats


class DocumentRepository(ABC):
    """Abstract repository interface for document operations."""

    @abstractmethod
    async def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to the repository.

        Args:
            documents: List of document contents
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs

        Returns:
            List of document IDs (generated or provided)
        """
        pass

    @abstractmethod
    async def search_documents(
        self, query: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents.

        Args:
            query: Search query
            n_results: Maximum number of results
            where: Optional metadata filter

        Returns:
            List of search results with similarity scores
        """
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a specific document by ID.

        Args:
            document_id: Document identifier

        Returns:
            Document if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_document(
        self, document_id: str, document: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a document.

        Args:
            document_id: Document identifier
            document: New document content
            metadata: Optional new metadata

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document.

        Args:
            document_id: Document identifier

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_collection_stats(self) -> CollectionStats:
        """Get collection statistics.

        Returns:
            Collection statistics
        """
        pass

    @abstractmethod
    async def list_documents(self) -> List[Document]:
        """List all documents with their IDs and metadata.

        Returns:
            List of all documents in the collection
        """
        pass
