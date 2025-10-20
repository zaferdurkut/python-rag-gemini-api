import google.generativeai as genai
from typing import Optional, List, Dict, Any
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """Gemini API client adapter."""

    def __init__(self):
        """Initialize Gemini client."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self.chat_session = None

    async def generate_response(
        self, message: str, context: Optional[str] = None
    ) -> str:
        """Generate response using Gemini API."""
        try:
            # Prepare the prompt
            prompt = message
            if context:
                prompt = f"Context: {context}\n\nQuestion: {message}"

            # Generate response
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def start_chat_session(self) -> str:
        """Start a new chat session."""
        try:
            self.chat_session = self.model.start_chat()
            return "Chat session started"
        except Exception as e:
            logger.error(f"Error starting chat session: {e}")
            raise

    async def send_message(self, message: str) -> str:
        """Send message to existing chat session."""
        if not self.chat_session:
            await self.start_chat_session()

        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def get_chat_history(self) -> List[Dict[str, str]]:
        """Get chat history from current session."""
        if not self.chat_session:
            return []

        try:
            history = []
            for message in self.chat_session.history:
                history.append(
                    {
                        "role": message.role,
                        "content": message.parts[0].text if message.parts else "",
                    }
                )
            return history
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []

    async def reset_chat_session(self) -> None:
        """Reset the chat session."""
        self.chat_session = None
