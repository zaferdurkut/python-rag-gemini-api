from typing import Optional
from datetime import datetime
import uuid
from app.domain.entities import ChatRequest, ChatResponse, ConversationHistory
from app.domain.repositories import ChatRepository
from app.infrastructure.gemini_client import GeminiClient


class ChatUseCase:
    """Chat use case implementation."""

    def __init__(self, chat_repository: ChatRepository, gemini_client: GeminiClient):
        self.chat_repository = chat_repository
        self.gemini_client = gemini_client

    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Process chat request with Gemini AI."""
        # Get or create conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())
        conversation = await self.chat_repository.get_conversation(conversation_id)

        if not conversation:
            conversation = ConversationHistory(
                conversation_id=conversation_id,
                messages=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

        # Add user message to conversation
        conversation.messages.append(
            {
                "role": "user",
                "content": request.message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Get response from Gemini
        response_text = await self.gemini_client.generate_response(
            request.message, request.context
        )

        # Add assistant response to conversation
        conversation.messages.append(
            {
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()

        # Save conversation
        await self.chat_repository.save_conversation(conversation)

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            metadata={"message_count": len(conversation.messages)},
        )

    async def get_conversation_history(
        self, conversation_id: str
    ) -> Optional[ConversationHistory]:
        """Get conversation history."""
        return await self.chat_repository.get_conversation(conversation_id)

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation."""
        return await self.chat_repository.delete_conversation(conversation_id)
