from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.application.use_cases import DocumentUseCase
from app.infrastructure.gemini_adapter import gemini_adapter
from app.core.config import settings
from app.core.exceptions import RAGBaseException
from app.core.logging import get_logger
from app.core.dependencies import get_document_use_case
from app.presentation.chat.dto import (
    ChatRequest,
    ChatResponse,
)

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
):
    """Chat with Gemini AI using RAG (Retrieval-Augmented Generation)."""
    try:
        logger.info(f"Chat request received: {request.message[:100]}...")

        # Get RAG context if enabled
        rag_context = ""
        sources = []

        if request.use_rag:
            logger.info("RAG enabled, getting context...")
            # Use the new RAG context method from use case
            rag_result = await document_use_case.get_rag_context(
                query=request.message, max_docs=request.max_context_docs
            )

            rag_context = rag_result.context
            sources = [
                {
                    "document": (
                        doc.content[: settings.RAG_DOCUMENT_PREVIEW_LENGTH] + "..."
                        if len(doc.content) > settings.RAG_DOCUMENT_PREVIEW_LENGTH
                        else doc.content
                    ),
                    "score": 1.0,  # We could calculate this from similarity if needed
                    "metadata": doc.metadata,
                }
                for doc in rag_result.sources
            ]

            logger.info(
                f"RAG result: {rag_result.included_docs}/{rag_result.total_found} docs, "
                f"{len(rag_context)} characters"
            )

            if not rag_context:
                logger.warning("RAG context is empty - no relevant documents found")

        # Generate response using Gemini
        logger.info("Generating response with Gemini...")
        if rag_context:
            logger.info(f"Using RAG context: {len(rag_context)} characters")
            response = await gemini_adapter.generate_with_rag_context(
                query=request.message, rag_context=rag_context
            )
        else:
            logger.warning("No RAG context available, using general response")
            response = await gemini_adapter.generate_response(request.message)

        logger.info("Response generated successfully")
        return ChatResponse(
            response=response,
            sources=sources if sources else None,
            rag_used=bool(rag_context),
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        # Re-raise to let the global exception handler deal with it
        raise
