"""
Test script for embedding functionality
"""

import asyncio
import sys
import os
import pytest
import tempfile
import shutil

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.infrastructure.embedding_service import embedding_service
from app.infrastructure.chroma_repository import ChromaRepository
from app.core.config import settings


@pytest.mark.asyncio
async def test_embedding_service():
    """Test the embedding service functionality."""
    # Test model info
    model_info = embedding_service.get_model_info()
    assert model_info["loaded"] is True
    assert "embedding_dimension" in model_info

    # Test single embedding
    test_text = (
        "This is a test document about artificial intelligence and machine learning."
    )
    embedding = embedding_service.generate_single_embedding(test_text)
    assert len(embedding) > 0
    assert len(embedding) == model_info["embedding_dimension"]

    # Test multiple embeddings
    test_texts = [
        "Machine learning is a subset of artificial intelligence.",
        "Natural language processing helps computers understand human language.",
        "Deep learning uses neural networks with multiple layers.",
    ]
    embeddings = embedding_service.generate_embeddings(test_texts)
    assert len(embeddings) == len(test_texts)
    assert all(len(emb) == model_info["embedding_dimension"] for emb in embeddings)


@pytest.mark.asyncio
async def test_chroma_with_embeddings():
    """Test ChromaDB with embeddings."""
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    try:
        # Initialize ChromaDB repository
        chroma_repo = ChromaRepository(
            persist_directory=temp_dir,
            collection_name="test_embeddings",
        )

        # Test documents
        test_documents = [
            "Artificial intelligence is transforming the world.",
            "Machine learning algorithms can learn from data.",
            "Natural language processing enables computers to understand text.",
            "Deep learning uses neural networks for complex tasks.",
        ]

        # Add documents with embeddings
        document_ids = await chroma_repo.add_documents(test_documents)
        assert len(document_ids) == len(test_documents)

        # Test search with embeddings
        search_queries = [
            "What is AI?",
            "How do neural networks work?",
            "Tell me about data learning",
        ]

        for query in search_queries:
            results = await chroma_repo.search_documents(query, n_results=2)
            assert len(results) <= 2
            for result in results:
                assert "id" in result
                assert "document" in result
                assert "distance" in result

        # Get collection stats
        stats = await chroma_repo.get_collection_stats()
        assert "total_documents" in stats
        assert stats["total_documents"] == len(test_documents)

        # Clean up test collection
        await chroma_repo.reset_collection()
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_embedding_integration():
    """Test the complete embedding integration workflow."""
    # Test embedding service
    model_info = embedding_service.get_model_info()
    assert model_info["loaded"] is True

    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    try:
        # Test ChromaDB integration
        chroma_repo = ChromaRepository(
            persist_directory=temp_dir,
            collection_name="test_integration",
        )

        # Add a single document
        test_doc = "This is a comprehensive test of the embedding system integration."
        doc_ids = await chroma_repo.add_documents([test_doc])
        assert len(doc_ids) == 1

        # Search for the document
        results = await chroma_repo.search_documents("embedding system", n_results=1)
        assert len(results) == 1
        assert test_doc in results[0]["document"]

        # Clean up
        await chroma_repo.reset_collection()
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


# Standalone test runner for manual execution
async def main():
    """Run all tests manually."""
    print("🚀 Starting Embedding System Tests\n")

    try:
        # Test embedding service
        print("🧪 Testing Embedding Service...")
        model_info = embedding_service.get_model_info()
        print(f"✅ Model Info: {model_info}")

        test_text = "This is a test document about artificial intelligence and machine learning."
        embedding = embedding_service.generate_single_embedding(test_text)
        print(f"✅ Single embedding generated: {len(embedding)} dimensions")

        test_texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Natural language processing helps computers understand human language.",
            "Deep learning uses neural networks with multiple layers.",
        ]
        embeddings = embedding_service.generate_embeddings(test_texts)
        print(
            f"✅ Multiple embeddings generated: {len(embeddings)} embeddings, {len(embeddings[0])} dimensions each"
        )

        # Test ChromaDB with embeddings
        print("\n🧪 Testing ChromaDB with Embeddings...")
        # Use temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        try:
            chroma_repo = ChromaRepository(
                persist_directory=temp_dir,
                collection_name="test_embeddings",
            )

            test_documents = [
                "Artificial intelligence is transforming the world.",
                "Machine learning algorithms can learn from data.",
                "Natural language processing enables computers to understand text.",
                "Deep learning uses neural networks for complex tasks.",
            ]

            print("📝 Adding documents with embeddings...")
            document_ids = await chroma_repo.add_documents(test_documents)
            print(f"✅ Added {len(document_ids)} documents: {document_ids}")

            print("🔍 Testing semantic search...")
            search_queries = [
                "What is AI?",
                "How do neural networks work?",
                "Tell me about data learning",
            ]

            for query in search_queries:
                results = await chroma_repo.search_documents(query, n_results=2)
                print(f"🔍 Query: '{query}'")
                for i, result in enumerate(results):
                    print(
                        f"  {i+1}. {result['document'][:50]}... (distance: {result['distance']:.4f})"
                    )
                print()

            stats = await chroma_repo.get_collection_stats()
            print(f"📊 Collection stats: {stats}")

            await chroma_repo.reset_collection()
            print("🧹 Test collection cleaned up")
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

        print("\n🎉 All tests passed! Embedding system is ready.")
        return 0

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
