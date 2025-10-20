from fastapi import APIRouter, HTTPException, status
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.application.use_cases import DocumentUseCase
from app.infrastructure.gemini_adapter import gemini_adapter

router = APIRouter()

# Initialize dependencies
document_use_case = DocumentUseCase()


# Document Management Models
class DocumentRequest(BaseModel):
    documents: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None
    ids: Optional[List[str]] = None


class DocumentSearchRequest(BaseModel):
    query: str
    n_results: int = 5
    where: Optional[Dict[str, Any]] = None


class DocumentUpdateRequest(BaseModel):
    document: str
    metadata: Optional[Dict[str, Any]] = None


# Document Management Endpoints
@router.post("/documents/", response_model=Dict[str, Any])
async def add_documents(request: DocumentRequest):
    """Add documents to the knowledge base."""
    try:
        document_ids = await document_use_case.add_documents(
            request.documents, request.metadatas, request.ids
        )
        return {
            "message": f"Successfully added {len(document_ids)} documents",
            "document_ids": document_ids,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding documents: {str(e)}",
        )


@router.post("/documents/search", response_model=List[Dict[str, Any]])
async def search_documents(request: DocumentSearchRequest):
    """Search for similar documents."""
    try:
        results = await document_use_case.search_documents(
            request.query, request.n_results, request.where
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}",
        )


@router.get("/documents/{document_id}", response_model=Dict[str, Any])
async def get_document(document_id: str):
    """Get a specific document by ID."""
    try:
        document = await document_use_case.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting document: {str(e)}",
        )


@router.put("/documents/{document_id}")
async def update_document(document_id: str, request: DocumentUpdateRequest):
    """Update a document."""
    try:
        success = await document_use_case.update_document(
            document_id, request.document, request.metadata
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )
        return {"message": "Document updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating document: {str(e)}",
        )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document."""
    try:
        success = await document_use_case.delete_document(document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}",
        )


@router.get("/documents/stats", response_model=Dict[str, Any])
async def get_collection_stats():
    """Get collection statistics."""
    try:
        stats = await document_use_case.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting collection stats: {str(e)}",
        )


@router.post("/documents/reset")
async def reset_collection():
    """Reset the collection (delete all documents)."""
    try:
        success = await document_use_case.reset_collection()
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset collection",
            )
        return {"message": "Collection reset successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting collection: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for all services."""
    try:
        # Check ChromaDB
        chroma_stats = await document_use_case.get_collection_stats()

        # Check Gemini
        gemini_info = await gemini_adapter.get_model_info()

        return {
            "status": "healthy",
            "services": {
                "chromadb": {
                    "status": "connected",
                    "total_documents": chroma_stats.get("total_documents", 0),
                    "collection": chroma_stats.get("collection_name", "unknown"),
                },
                "gemini": {
                    "status": (
                        "connected"
                        if gemini_info.get("model_ready")
                        else "disconnected"
                    ),
                    "model": gemini_info.get("model_name", "unknown"),
                    "api_configured": gemini_info.get("api_configured", False),
                },
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}",
        )


# Test Models
class TestGeminiRequest(BaseModel):
    prompt: str
    context: Optional[str] = None


@router.post("/test/gemini")
async def test_gemini(request: TestGeminiRequest):
    """Test Gemini AI adapter."""
    try:
        response = await gemini_adapter.generate_response(
            prompt=request.prompt, context=request.context
        )
        return {
            "prompt": request.prompt,
            "response": response,
            "context_used": bool(request.context),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing Gemini: {str(e)}",
        )


@router.post("/test/rag")
async def test_rag_with_gemini(request: TestGeminiRequest):
    """Test RAG system with Gemini AI."""
    try:
        # Search for relevant documents
        if request.context:
            # Use provided context
            rag_context = request.context
        else:
            # Search ChromaDB for relevant context
            rag_context = await document_use_case.search_for_rag_context(
                request.prompt, max_results=3
            )

        # Generate response with RAG context
        response = await gemini_adapter.generate_with_rag_context(
            query=request.prompt, rag_context=rag_context
        )

        return {
            "prompt": request.prompt,
            "response": response,
            "rag_context": rag_context,
            "context_length": len(rag_context) if rag_context else 0,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing RAG with Gemini: {str(e)}",
        )
