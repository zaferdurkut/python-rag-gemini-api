from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Chat DTOs
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    use_rag: bool = True
    max_context_docs: int = 3

    class Config:
        schema_extra = {
            "example": {
                "message": "What is Python programming?",
                "conversation_id": "optional-conversation-id",
                "use_rag": True,
                "max_context_docs": 3,
            }
        }


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    rag_used: bool = False

    class Config:
        schema_extra = {
            "example": {
                "response": "Python is a versatile programming language...",
                "conversation_id": "conv-123",
                "sources": [
                    {"document": "Python is a programming language", "score": 0.95}
                ],
                "rag_used": True,
            }
        }


class ConversationRequest(BaseModel):
    conversation_id: str


class ConversationResponse(BaseModel):
    conversation_id: str
    messages: List[Dict[str, str]]
    created_at: str
    updated_at: str


class TestGeminiRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
