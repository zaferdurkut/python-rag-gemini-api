from fastapi import APIRouter, HTTPException, status
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

from app.application.use_cases import DocumentUseCase
from app.infrastructure.gemini_adapter import gemini_adapter
from app.presentation.chat.dto import (
    ChatRequest,
    ChatResponse,
    ConversationRequest,
    ConversationResponse,
    TestGeminiRequest,
)

# Initialize dependencies
document_use_case = DocumentUseCase()
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["chat"])

# Conversation Management (Simple in-memory storage for demo)
# In production, use Redis or database
conversation_storage = {}


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with Gemini AI using RAG (Retrieval-Augmented Generation)."""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Get RAG context if enabled
        rag_context = ""
        sources = []

        if request.use_rag:
            try:
                # Search for relevant documents
                search_results = await document_use_case.search_documents(
                    request.message, n_results=request.max_context_docs
                )

                if search_results:
                    # Extract context from search results
                    context_parts = []
                    for result in search_results:
                        distance = result.get("distance", 1.0)
                        # Extremely lenient threshold - include results with distance < 2.0
                        if distance < 2.0:
                            context_parts.append(result["document"])
                            sources.append(
                                {
                                    "document": (
                                        result["document"][:200] + "..."
                                        if len(result["document"]) > 200
                                        else result["document"]
                                    ),
                                    "score": 1 - distance,
                                    "metadata": result.get("metadata", {}),
                                }
                            )

                    rag_context = "\n\n".join(context_parts)
                    logger.info(
                        f"RAG context found: {len(context_parts)} documents, {len(rag_context)} characters"
                    )
                    # Log distance values for debugging
                    for i, result in enumerate(search_results):
                        distance = result.get("distance", 1.0)
                        logger.info(
                            f"Result {i}: distance={distance:.4f}, included={distance < 2.0}"
                        )
                else:
                    logger.warning("No search results found for RAG context")

                # Additional debug info
                if not rag_context:
                    logger.warning("RAG context is empty - no relevant documents found")
            except Exception as e:
                # If RAG fails, continue without context
                logger.error(f"RAG search failed: {e}")
                rag_context = ""

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
            conversation_id=conversation_id,
            sources=sources if sources else None,
            rag_used=bool(rag_context),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat: {str(e)}",
        )


@router.post("/test", response_model=Dict[str, Any])
async def test_gemini(request: TestGeminiRequest):
    """Test Gemini AI without RAG context."""
    try:
        response = await gemini_adapter.generate_response(
            request.prompt, context=request.context
        )
        return {
            "response": response,
            "model_info": await gemini_adapter.get_model_info(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing Gemini: {str(e)}",
        )


@router.get("/debug-rag", response_model=Dict[str, Any])
async def debug_rag(query: str, max_results: int = 5):
    """Debug RAG system - see what documents are found."""
    try:
        # First check if we have any documents in the collection
        collection_stats = await document_use_case.get_collection_stats()
        logger.info(f"Collection stats: {collection_stats}")

        # Test embedding service
        try:
            from app.infrastructure.embedding_service import embedding_service
            import numpy as np

            test_embedding = embedding_service.generate_single_embedding("test query")
            logger.info(f"Embedding service working: {len(test_embedding)} dimensions")

            # Test similarity between similar texts
            embedding1 = embedding_service.generate_single_embedding("test query")
            embedding2 = embedding_service.generate_single_embedding("test query")
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            logger.info(f"Self-similarity test: {similarity:.4f} (should be ~1.0)")
        except Exception as e:
            logger.error(f"Embedding service error: {e}")

        # Search for documents
        search_results = await document_use_case.search_documents(query, max_results)

        # Analyze results
        debug_info = {
            "query": query,
            "collection_stats": collection_stats,
            "total_results": len(search_results),
            "results": [],
        }

        for i, result in enumerate(search_results):
            debug_info["results"].append(
                {
                    "index": i,
                    "distance": result.get("distance", 1.0),
                    "score": 1 - result.get("distance", 1.0),
                    "document_preview": (
                        result["document"][:100] + "..."
                        if len(result["document"]) > 100
                        else result["document"]
                    ),
                    "metadata": result.get("metadata", {}),
                    "would_be_included": result.get("distance", 1.0) < 2.0,
                }
            )

        return debug_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error debugging RAG: {str(e)}",
        )


@router.get("/list-documents", response_model=Dict[str, Any])
async def list_all_documents():
    """List all documents in the collection."""
    try:
        documents = await document_use_case.list_documents()
        return {"total_documents": len(documents), "documents": documents}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}",
        )


# Session Management Endpoints
@router.post("/session/start", response_model=Dict[str, str])
async def start_chat_session():
    """Start a new chat session."""
    session_id = str(uuid.uuid4())
    conversation_storage[session_id] = {
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    return {"session_id": session_id, "message": "Chat session started"}


@router.get("/session/{session_id}", response_model=ConversationResponse)
async def get_chat_session(session_id: str):
    """Get chat session history."""
    if session_id not in conversation_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    session = conversation_storage[session_id]
    return ConversationResponse(
        conversation_id=session_id,
        messages=session["messages"],
        created_at=session["created_at"],
        updated_at=session["updated_at"],
    )


@router.delete("/session/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session."""
    if session_id not in conversation_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    del conversation_storage[session_id]
    return {"message": "Chat session deleted"}


@router.post("/session/reset")
async def reset_all_sessions():
    """Reset all chat sessions."""
    conversation_storage.clear()
    return {"message": "All chat sessions reset"}
