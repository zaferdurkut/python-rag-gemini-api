"""
Test script for file upload functionality.
This script demonstrates how to use the new file upload endpoints.
"""

import pytest
import requests
import json
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
from app.app import app

# Test client for FastAPI
client = TestClient(app)


def test_supported_types():
    """Test getting supported file types."""
    response = client.get("/api/v1/documents/supported-types")
    assert response.status_code == 200
    data = response.json()
    assert "supported_extensions" in data
    assert "max_file_size_mb" in data
    assert "max_image_size_mb" in data


def test_single_file_upload():
    """Test uploading a single file."""
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is a test document for file upload testing.")
        temp_file_path = f.name

    try:
        with open(temp_file_path, "rb") as f:
            files = {"file": (Path(temp_file_path).name, f, "text/plain")}
            data = {"metadata": json.dumps({"source": "test", "category": "sample"})}

            response = client.post("/api/v1/documents/upload", files=files, data=data)

            assert response.status_code == 200
            result = response.json()
            assert "document_id" in result
            assert "text_length" in result
            assert "metadata" in result
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)


def test_multiple_file_upload():
    """Test uploading multiple files."""
    # Create temporary files
    temp_files = []
    try:
        for i in range(2):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as f:
                f.write(
                    f"This is test document {i+1} for multiple file upload testing."
                )
                temp_files.append(f.name)

        files = []
        for temp_file in temp_files:
            with open(temp_file, "rb") as f:
                files.append(("files", (Path(temp_file).name, f.read(), "text/plain")))

        data = {"metadatas": json.dumps([{"source": "test"}, {"source": "test"}])}

        response = client.post(
            "/api/v1/documents/upload-multiple", files=files, data=data
        )

        assert response.status_code == 200
        result = response.json()
        assert "document_ids" in result
        assert "failed_uploads" in result
        assert "message" in result
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            os.unlink(temp_file)


def test_search_uploaded_documents():
    """Test searching for uploaded documents."""
    # Search for common terms
    search_queries = ["document", "text", "content", "file"]

    for query in search_queries:
        response = client.get(f"/api/v1/documents/search?query={query}&n_results=3")

        # Search might return 200 even if no results found
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)


# Pytest will automatically discover and run the test functions
