from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Document Management DTOs
class DocumentRequest(BaseModel):
    documents: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None
    ids: Optional[List[str]] = None


class DocumentUpdateRequest(BaseModel):
    document: str
    metadata: Optional[Dict[str, Any]] = None


# Test DTOs
class TestGeminiRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
