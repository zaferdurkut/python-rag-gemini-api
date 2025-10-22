from fastapi import APIRouter
from typing import Dict, Any

from app.application.use_cases import DocumentUseCase
from app.infrastructure.gemini_adapter import gemini_adapter
from app.core.config import settings
from app.core.exceptions import RAGBaseException
from app.core.logging import get_logger
from app.presentation.chat.dto import (
    ChatRequest,
    ChatResponse,
)

# Initialize dependencies
document_use_case = DocumentUseCase()
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with Gemini AI using RAG (Retrieval-Augmented Generation)."""
    # Get RAG context if enabled
    rag_context = ""
    sources = []

    if request.use_rag:
        # Use the new RAG context method from use case
        rag_result = await document_use_case.get_rag_context(
            query=request.message, max_docs=request.max_context_docs
        )

        rag_context = rag_result["context"]
        sources = rag_result["sources"]

        logger.info(
            f"RAG result: {rag_result['included_docs']}/{rag_result['total_found']} docs, "
            f"{len(rag_context)} characters"
        )

        if not rag_context:
            logger.warning("RAG context is empty - no relevant documents found")

    # Generate response using Gemini
    if rag_context:
        logger.info(f"Using RAG context: {len(rag_context)} characters")
        response = await gemini_adapter.generate_with_rag_context(
            query=request.message, rag_context=rag_context
        )
    else:
        logger.warning("No RAG context available, using general response")
        response = await gemini_adapter.generate_response(request.message)

    return ChatResponse(
        response=response,
        sources=sources if sources else None,
        rag_used=bool(rag_context),
    )
