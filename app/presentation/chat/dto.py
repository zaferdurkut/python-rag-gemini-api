from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Chat DTOs
class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True
    max_context_docs: int = 3

    class Config:
        schema_extra = {
            "example": {
                "message": "What is Python programming?",
                "use_rag": True,
                "max_context_docs": 3,
            }
        }


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[Dict[str, Any]]] = None
    rag_used: bool = False

    class Config:
        schema_extra = {
            "example": {
                "response": "Python is a versatile programming language...",
                "sources": [
                    {"document": "Python is a programming language", "score": 0.95}
                ],
                "rag_used": True,
            }
        }
