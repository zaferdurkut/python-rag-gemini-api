import google.generativeai as genai
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.exceptions import GeminiAPIError
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiAdapter:
    """Adapter for Google Gemini AI API."""

    def __init__(self):
        """Initialize Gemini adapter."""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL

        # Validate API key
        if not self.api_key or self.api_key == "your-gemini-api-key-here":
            logger.warning(
                "Gemini API key not configured. Chat functionality will be limited."
            )
            self.model = None
            return

        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini adapter initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini adapter: {e}")
            raise GeminiAPIError(
                operation="initialization",
                reason=f"Failed to initialize model '{self.model_name}': {str(e)}",
            )

    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Generate response using Gemini AI with optional context."""
        if self.model is None:
            raise GeminiAPIError(
                operation="generate_response",
                reason="Model not initialized. Please configure a valid API key.",
            )

        try:
            # Prepare the full prompt
            full_prompt = self._prepare_prompt(prompt, context, system_instruction)

            # Generate response
            response = self.model.generate_content(full_prompt)

            if response.text:
                logger.info("Successfully generated response from Gemini")
                return response.text
            else:
                logger.warning("Empty response from Gemini")
                raise GeminiAPIError(
                    operation="generate_response",
                    reason="Empty response from Gemini model",
                )

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise GeminiAPIError(
                operation="generate_response",
                reason=f"Failed to generate response: {str(e)}",
            )

    def _prepare_prompt(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Prepare the full prompt with context and system instruction."""
        parts = []

        # Add system instruction if provided
        if system_instruction:
            parts.append(f"System: {system_instruction}")

        # Add context if provided
        if context:
            logger.info(f"Using RAG context: {len(context)} characters")
            parts.append(f"Context: {context}")
        else:
            logger.warning("No RAG context provided")

        # Add the main prompt
        parts.append(f"Question: {prompt}")

        full_prompt = "\n\n".join(parts)
        logger.info(f"Full prompt length: {len(full_prompt)} characters")
        return full_prompt

    async def generate_with_rag_context(
        self, query: str, rag_context: str, system_instruction: Optional[str] = None
    ) -> str:
        """Generate response with RAG context."""
        if self.model is None:
            raise GeminiAPIError(
                operation="generate_with_rag_context",
                reason="Model not initialized. Please configure a valid API key.",
            )

        system_instruction = system_instruction or (
            "You are a helpful AI assistant. Use the provided context to answer questions accurately. "
            "If the context doesn't contain relevant information, say so and provide a general answer."
        )

        return await self.generate_response(
            prompt=query, context=rag_context, system_instruction=system_instruction
        )

    async def chat_with_history(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        context: Optional[str] = None,
    ) -> str:
        """Generate response with chat history."""
        if self.model is None:
            raise GeminiAPIError(
                operation="chat_with_history",
                reason="Model not initialized. Please configure a valid API key.",
            )

        try:
            # Start a chat session
            chat = self.model.start_chat(history=[])

            # Add context to the first message if provided
            if context and not chat_history:
                message = f"Context: {context}\n\nQuestion: {message}"

            # Send the message
            response = chat.send_message(message)

            if response.text:
                logger.info("Successfully generated chat response from Gemini")
                return response.text
            else:
                logger.warning("Empty chat response from Gemini")
                raise GeminiAPIError(
                    operation="chat_with_history",
                    reason="Empty response from Gemini model",
                )

        except Exception as e:
            logger.error(f"Error in chat with history: {e}")
            raise GeminiAPIError(
                operation="chat_with_history",
                reason=f"Failed to generate chat response: {str(e)}",
            )

    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        try:
            return {
                "model_name": self.model_name,
                "api_configured": bool(self.api_key),
                "model_ready": True,
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                "model_name": self.model_name,
                "api_configured": bool(self.api_key),
                "model_ready": False,
                "error": str(e),
            }


# Global instance
gemini_adapter = GeminiAdapter()
