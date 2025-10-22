from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Document:
    """Domain entity representing a document in the RAG system."""

    id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

    def update_content(
        self, new_content: str, new_metadata: Optional[Dict[str, Any]] = None
    ):
        """Update document content and metadata."""
        self.content = new_content
        if new_metadata is not None:
            self.metadata.update(new_metadata)
        self.updated_at = datetime.utcnow()

    def add_metadata(self, key: str, value: Any):
        """Add or update a metadata field."""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()


@dataclass
class SearchResult:
    """Value object representing a search result."""

    document: Document
    similarity_score: float
    rank: int

    def __post_init__(self):
        """Validate similarity score."""
        if not 0.0 <= self.similarity_score <= 1.0:
            raise ValueError("Similarity score must be between 0.0 and 1.0")


@dataclass
class CollectionStats:
    """Value object representing collection statistics."""

    total_documents: int
    collection_name: str
    last_updated: Optional[datetime] = None
