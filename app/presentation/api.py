from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.application.use_cases import DocumentUseCase, FILE_PROCESSOR_AVAILABLE
from app.infrastructure.gemini_adapter import gemini_adapter
from app.infrastructure.file_processor import FileProcessor
from app.presentation.dto import (
    DocumentRequest,
    DocumentUpdateRequest,
    TestGeminiRequest,
)
from app.core.exceptions import (
    DocumentNotFoundError,
    DocumentProcessingError,
    UnsupportedFileTypeError,
    FileSizeExceededError,
    ChromaDBError,
    ValidationError,
)


router = APIRouter()

# Initialize dependencies
document_use_case = DocumentUseCase()
file_processor = FileProcessor()


# Document Management Endpoints
@router.post("/documents/", response_model=Dict[str, Any])
async def add_documents(request: DocumentRequest):
    """Add documents to the knowledge base."""
    document_ids = await document_use_case.add_documents(
        request.documents, request.metadatas, request.ids
    )
    return {
        "message": f"Successfully added {len(document_ids)} documents",
        "document_ids": document_ids,
    }


@router.get("/documents/search", response_model=List[Dict[str, Any]])
async def search_documents(query: str, n_results: int = 5, where: Optional[str] = None):
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
    return results


@router.get("/documents/supported-types", response_model=Dict[str, Any])
async def get_supported_file_types():
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


@router.get("/documents/stats", response_model=Dict[str, Any])
async def get_collection_stats():
    """Get collection statistics."""
    stats = await document_use_case.get_collection_stats()
    return stats


@router.get("/documents", response_model=List[Dict[str, Any]])
async def list_documents():
    """List all documents with their IDs and metadata."""
    documents = await document_use_case.list_documents()
    return documents


@router.get("/documents/{document_id}", response_model=Dict[str, Any])
async def get_document(document_id: str):
    """Get a specific document by ID."""
    document = await document_use_case.get_document(document_id)
    if not document:
        raise DocumentNotFoundError(document_id)
    return document


@router.put("/documents/{document_id}")
async def update_document(document_id: str, request: DocumentUpdateRequest):
    """Update a document."""
    success = await document_use_case.update_document(
        document_id, request.document, request.metadata
    )
    if not success:
        raise DocumentNotFoundError(document_id)
    return {"message": "Document updated successfully"}


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document."""
    success = await document_use_case.delete_document(document_id)
    if not success:
        raise DocumentNotFoundError(document_id)
    return {"message": "Document deleted successfully"}


@router.post("/documents/reset")
async def reset_collection():
    """Reset the collection (delete all documents)."""
    success = await document_use_case.reset_collection()
    if not success:
        raise ChromaDBError("reset_collection", "Failed to reset collection")
    return {"message": "Collection reset successfully"}


# File Upload Endpoints
@router.post("/documents/upload", response_model=Dict[str, Any])
async def upload_single_file(
    file: UploadFile = File(...), metadata: Optional[str] = Form(None)
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


@router.post("/documents/upload-multiple", response_model=Dict[str, Any])
async def upload_multiple_files(
    files: List[UploadFile] = File(...), metadatas: Optional[str] = Form(None)
):
    """Upload multiple files and add them to the knowledge base."""
    if not files:
        raise ValidationError("files", "No files provided")

    # Validate all files
    for file in files:
        if not file_processor.is_supported_file(file.filename):
            raise UnsupportedFileTypeError(
                file.filename, file_processor.supported_types
            )

    # Read file contents
    file_data = []
    for file in files:
        content = await file.read()
        file_data.append({"filename": file.filename, "content": content})

    # Parse metadatas if provided
    file_metadatas = None
    if metadatas:
        import json

        try:
            file_metadatas = json.loads(metadatas)
            if not isinstance(file_metadatas, list) or len(file_metadatas) != len(
                files
            ):
                raise ValidationError(
                    "metadatas", "Must be a list with same length as files"
                )
        except json.JSONDecodeError:
            # If not valid JSON, treat as simple string and create basic metadata for all files
            file_metadatas = [{"source": metadatas} for _ in files]

    # Process and add files
    result = await document_use_case.process_and_add_files(file_data, file_metadatas)

    return {
        "message": f"Processed {result['total_processed']} files",
        "successful_uploads": result["successful_uploads"],
        "failed_uploads": result["failed_uploads"],
        "document_ids": result["document_ids"],
        "failed_files": result["failed_files"],
    }
