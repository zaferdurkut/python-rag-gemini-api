from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities import ChatResponse, ConversationHistory


class ChatRepository(ABC):
    """Abstract repository for chat functionality."""

    @abstractmethod
    async def save_conversation(self, conversation: ConversationHistory) -> None:
        """Save conversation to storage."""
        pass

    @abstractmethod
    async def get_conversation(
        self, conversation_id: str
    ) -> Optional[ConversationHistory]:
        """Get conversation by ID."""
        pass

    @abstractmethod
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation."""
        pass
