from dataclasses import dataclass
from typing import List
from .document_entities import Document


@dataclass
class RAGContext:
    """Value object representing RAG context for AI generation."""

    context: str
    sources: List[Document]
    included_docs: int
    total_found: int

    def __post_init__(self):
        """Validate RAG context."""
        if self.included_docs > self.total_found:
            raise ValueError("Included docs cannot exceed total found")
        if self.included_docs < 0 or self.total_found < 0:
            raise ValueError("Document counts must be non-negative")
