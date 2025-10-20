from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[Dict[str, str]]
    created_at: datetime
    updated_at: datetime
