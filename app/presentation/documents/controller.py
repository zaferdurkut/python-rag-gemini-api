from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Depends
from typing import Optional, List, Dict, Any

from app.application.use_cases import DocumentUseCase, FILE_PROCESSOR_AVAILABLE
from app.infrastructure.file_processor import FileProcessor
from app.infrastructure.embedding_service import embedding_service
from app.core.logging import get_logger
from app.core.dependencies import get_document_use_case, get_file_processor
from app.presentation.documents.dto import (
    DocumentRequest,
    DocumentUpdateRequest,
)
from app.core.exceptions import (
    DocumentNotFoundError,
    DocumentProcessingError,
    UnsupportedFileTypeError,
    FileSizeExceededError,
    ChromaDBError,
    ValidationError,
)

# Create router
router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize dependencies
logger = get_logger(__name__)


# Document Management Endpoints
@router.post("/", response_model=Dict[str, Any])
async def add_documents(
    request: DocumentRequest,
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
):
    """Add documents to the knowledge base.

    - If `ids` is not provided, auto-generated UUIDs will be used
    - If `metadatas` is not provided, default metadata with timestamp will be used
    - Returns the document IDs (auto-generated or provided)
    """
    document_ids = await document_use_case.add_documents(
        request.documents, request.metadatas, request.ids
    )
    return {
        "message": f"Successfully added {len(document_ids)} documents",
        "document_ids": document_ids,
        "auto_generated_ids": request.ids is None,
    }


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_documents(
    query: str,
    n_results: int = 5,
    where: Optional[str] = None,
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
):
    """Search for similar documents."""
    # Parse where parameter if provided
    where_dict = None
    if where:
        import json

        try:
            where_dict = json.loads(where)
        except json.JSONDecodeError:
            raise ValidationError("where", "Invalid JSON format")

    results = await document_use_case.search_documents(query, n_results, where_dict)
    # Convert SearchResult objects to dictionaries for API response
    return [
        {
            "id": result.document.id,
            "document": result.document.content,
            "metadata": result.document.metadata,
            "distance": 1.0 - result.similarity_score,
            "similarity_score": result.similarity_score,
            "rank": result.rank,
        }
        for result in results
    ]


@router.get("/supported-types", response_model=Dict[str, Any])
async def get_supported_file_types(
    file_processor: FileProcessor = Depends(get_file_processor),
):
    """Get list of supported file types."""
    response = {
        "supported_extensions": file_processor.supported_types,
        "max_file_size_mb": file_processor.MAX_FILE_SIZE / (1024 * 1024),
        "supported_mime_types": list(file_processor.SUPPORTED_EXTENSIONS.values()),
        "full_processor_available": FILE_PROCESSOR_AVAILABLE,
    }

    # Add image size limit only if full processor is available
    if FILE_PROCESSOR_AVAILABLE and hasattr(file_processor, "MAX_IMAGE_SIZE"):
        response["max_image_size_mb"] = file_processor.MAX_IMAGE_SIZE / (1024 * 1024)

    return response


@router.get("/stats", response_model=Dict[str, Any])
async def get_collection_stats(
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
):
    """Get collection statistics."""
    stats = await document_use_case.get_collection_stats()
    return {
        "total_documents": stats.total_documents,
        "collection_name": stats.collection_name,
        "last_updated": stats.last_updated.isoformat() if stats.last_updated else None,
    }


@router.get("", response_model=List[Dict[str, Any]])
async def list_documents(
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
):
    """List all documents with their IDs and metadata."""
    documents = await document_use_case.list_documents()

    # Convert Document entities to dictionaries for API response
    return [
        {
            "id": doc.id,
            "content_preview": (
                doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
            ),
            "content_length": len(doc.content),
            "metadata": doc.metadata,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
        }
        for doc in documents
    ]


@router.get("/{document_id}", response_model=Dict[str, Any])
async def get_document(
    document_id: str,
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
):
    """Get a specific document by ID."""
    document = await document_use_case.get_document(document_id)
    if not document:
        raise DocumentNotFoundError(document_id)
    return {
        "id": document.id,
        "document": document.content,
        "metadata": document.metadata,
        "created_at": document.created_at.isoformat() if document.created_at else None,
        "updated_at": document.updated_at.isoformat() if document.updated_at else None,
    }


@router.put("/{document_id}", response_model=Dict[str, Any])
async def update_document(
    document_id: str,
    request: DocumentUpdateRequest,
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
):
    """Update a document."""
    success = await document_use_case.update_document(
        document_id, request.document, request.metadata
    )
    if not success:
        raise DocumentNotFoundError(document_id)
    return {"message": "Document updated successfully", "document_id": document_id}


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
):
    """Delete a document."""
    success = await document_use_case.delete_document(document_id)
    if not success:
        raise DocumentNotFoundError(document_id)
    return {"message": "Document deleted successfully", "document_id": document_id}


@router.post("/reset")
async def reset_collection(
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
):
    """Reset the collection."""
    # Note: reset_collection method is not in the domain interface
    # This would need to be added to the domain interface or handled differently
    return {"message": "Collection reset not implemented in domain layer"}


# Embedding Endpoints
@router.get("/embeddings/info", response_model=Dict[str, Any])
async def get_embedding_info():
    """Get information about the embedding model."""
    return embedding_service.get_model_info()


@router.post("/embeddings/generate", response_model=Dict[str, Any])
async def generate_embeddings(texts: List[str]):
    """Generate embeddings for given texts."""
    if not texts:
        raise ValidationError("texts", "No texts provided")

    try:
        embeddings = embedding_service.generate_embeddings(texts)
        return {
            "embeddings": [embedding.tolist() for embedding in embeddings],
            "count": len(embeddings),
            "dimension": len(embeddings[0]) if len(embeddings) > 0 else 0,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embeddings: {str(e)}",
        )


# File Upload Endpoints
@router.post("/upload", response_model=Dict[str, Any])
async def upload_single_file(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
    file_processor: FileProcessor = Depends(get_file_processor),
):
    """Upload a single file and add it to the knowledge base."""
    # Validate file type
    if not file_processor.is_supported_file(file.filename):
        raise UnsupportedFileTypeError(file.filename, file_processor.supported_types)

    # Read file content
    file_content = await file.read()

    # Validate file size
    if not file_processor.validate_file_size(len(file_content)):
        raise FileSizeExceededError(
            file.filename, len(file_content), file_processor.MAX_FILE_SIZE
        )

    # Parse metadata if provided
    file_metadata = None
    if metadata:
        import json

        try:
            # Try to parse as JSON first
            file_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            # If not valid JSON, treat as simple string and create a basic metadata object
            file_metadata = {"source": metadata}

    # Process and add file
    result = await document_use_case.process_single_file(
        file_content, file.filename, file_metadata
    )

    if not result["success"]:
        raise DocumentProcessingError(file.filename, result["error"])

    return {
        "message": "File uploaded and processed successfully",
        "document_id": result["document_id"],
        "filename": result["filename"],
        "text_length": result["text_length"],
        "metadata": result["metadata"],
    }


@router.post("/upload-multiple", response_model=Dict[str, Any])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    metadatas: Optional[str] = Form(None),
    document_use_case: DocumentUseCase = Depends(get_document_use_case),
    file_processor: FileProcessor = Depends(get_file_processor),
):
    """Upload multiple files and add them to the knowledge base."""
    # Validate all files
    for file in files:
        if not file_processor.is_supported_file(file.filename):
            raise UnsupportedFileTypeError(
                file.filename, file_processor.supported_types
            )

    # Read all file contents
    file_contents = []
    for file in files:
        content = await file.read()
        if not file_processor.validate_file_size(len(content)):
            raise FileSizeExceededError(
                file.filename, len(content), file_processor.MAX_FILE_SIZE
            )
        file_contents.append(content)

    # Parse metadatas if provided
    file_metadatas = None
    if metadatas:
        import json

        try:
            file_metadatas = json.loads(metadatas)
        except json.JSONDecodeError:
            # If not valid JSON, create basic metadata for each file
            file_metadatas = [{"source": f"file_{i}"} for i in range(len(files))]

    # Prepare files for processing
    files_data = []
    for i, (file, content) in enumerate(zip(files, file_contents)):
        files_data.append(
            {
                "filename": file.filename,
                "content": content,
                "metadata": (
                    file_metadatas[i] if file_metadatas else {"source": f"file_{i}"}
                ),
            }
        )

    # Process and add files
    result = await document_use_case.process_and_add_files(files_data, file_metadatas)

    return {
        "message": f"Processed {result['total_processed']} files",
        "successful_uploads": result["successful_uploads"],
        "failed_uploads": result["failed_uploads"],
        "document_ids": result["document_ids"],
        "failed_files": result["failed_files"],
    }
