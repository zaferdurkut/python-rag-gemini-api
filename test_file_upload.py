#!/usr/bin/env python3
"""
Test script for file upload functionality.
This script demonstrates how to use the new file upload endpoints.
"""

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"


def test_supported_types():
    """Test getting supported file types."""
    print("Testing supported file types...")
    response = requests.get(f"{BASE_URL}/documents/supported-types")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Supported extensions: {data['supported_extensions']}")
        print(f"✅ Max file size: {data['max_file_size_mb']} MB")
        print(f"✅ Max image size: {data['max_image_size_mb']} MB")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")


def test_single_file_upload(file_path: str, metadata: dict = None):
    """Test uploading a single file."""
    print(f"\nTesting single file upload: {file_path}")

    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return

    try:
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f, "application/octet-stream")}
            data = {}
            if metadata:
                data["metadata"] = json.dumps(metadata)

            response = requests.post(
                f"{BASE_URL}/documents/upload", files=files, data=data
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   Document ID: {result['document_id']}")
                print(f"   Text length: {result['text_length']}")
                print(f"   Metadata: {result['metadata']}")
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error uploading file: {e}")


def test_multiple_file_upload(file_paths: list, metadatas: list = None):
    """Test uploading multiple files."""
    print(f"\nTesting multiple file upload: {file_paths}")

    # Check if all files exist
    existing_files = []
    for file_path in file_paths:
        if Path(file_path).exists():
            existing_files.append(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")

    if not existing_files:
        print("❌ No valid files to upload")
        return

    try:
        files = []
        for file_path in existing_files:
            with open(file_path, "rb") as f:
                files.append(
                    (
                        "files",
                        (Path(file_path).name, f.read(), "application/octet-stream"),
                    )
                )

        data = {}
        if metadatas:
            data["metadatas"] = json.dumps(metadatas)

        response = requests.post(
            f"{BASE_URL}/documents/upload-multiple", files=files, data=data
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Multiple upload successful!")
            print(f"   Total processed: {result['total_processed']}")
            print(f"   Successful: {result['successful_uploads']}")
            print(f"   Failed: {result['failed_uploads']}")
            if result["failed_files"]:
                print(f"   Failed files: {result['failed_files']}")
        else:
            print(
                f"❌ Multiple upload failed: {response.status_code} - {response.text}"
            )

    except Exception as e:
        print(f"❌ Error uploading files: {e}")


def test_search_uploaded_documents():
    """Test searching for uploaded documents."""
    print("\nTesting search for uploaded documents...")

    try:
        # Search for common terms that might be in uploaded documents
        search_queries = ["document", "text", "content", "file"]

        for query in search_queries:
            response = requests.post(
                f"{BASE_URL}/documents/search", json={"query": query, "n_results": 3}
            )

            if response.status_code == 200:
                results = response.json()
                print(f"✅ Search for '{query}': Found {len(results)} results")
                for i, result in enumerate(results[:2]):  # Show first 2 results
                    print(f"   Result {i+1}: {result['document'][:100]}...")
            else:
                print(f"❌ Search failed for '{query}': {response.status_code}")

    except Exception as e:
        print(f"❌ Error searching: {e}")


def main():
    """Main test function."""
    print("🚀 Testing File Upload Functionality")
    print("=" * 50)

    # Test 1: Get supported file types
    test_supported_types()

    # Test 2: Create a sample text file and upload it
    sample_text_file = "sample_document.txt"
    with open(sample_text_file, "w", encoding="utf-8") as f:
        f.write(
            """
This is a sample document for testing the file upload functionality.
It contains some text that can be used to test the RAG system.
The document includes various topics like technology, programming, and AI.
This text will be processed and stored in the vector database.
        """.strip()
        )

    print(f"\n📝 Created sample file: {sample_text_file}")

    # Test 3: Upload single file
    test_single_file_upload(sample_text_file, {"source": "test", "category": "sample"})

    # Test 4: Upload multiple files (if more files exist)
    test_files = [sample_text_file]
    if Path("README.md").exists():
        test_files.append("README.md")

    if len(test_files) > 1:
        test_multiple_file_upload(test_files)

    # Test 5: Search for uploaded documents
    test_search_uploaded_documents()

    # Cleanup
    if Path(sample_text_file).exists():
        Path(sample_text_file).unlink()
        print(f"\n🧹 Cleaned up sample file: {sample_text_file}")

    print("\n✅ File upload testing completed!")


if __name__ == "__main__":
    main()
