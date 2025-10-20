import json
from typing import Optional
from datetime import datetime
from app.domain.entities import ConversationHistory
from app.domain.repositories import ChatRepository
from app.infrastructure.redis import redis_service


class RedisChatRepository(ChatRepository):
    """Redis implementation of ChatRepository."""

    def __init__(self):
        self.redis = redis_service

    async def save_conversation(self, conversation: ConversationHistory) -> None:
        """Save conversation to Redis."""
        key = f"conversation:{conversation.conversation_id}"
        data = {
            "conversation_id": conversation.conversation_id,
            "messages": conversation.messages,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
        await self.redis.set_json(key, data, expire=86400)  # 24 hours TTL

    async def get_conversation(
        self, conversation_id: str
    ) -> Optional[ConversationHistory]:
        """Get conversation from Redis."""
        key = f"conversation:{conversation_id}"
        data = await self.redis.get_json(key)

        if not data:
            return None

        return ConversationHistory(
            conversation_id=data["conversation_id"],
            messages=data["messages"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation from Redis."""
        key = f"conversation:{conversation_id}"
        return await self.redis.delete(key)
