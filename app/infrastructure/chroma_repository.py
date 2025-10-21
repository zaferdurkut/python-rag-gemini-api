import os

# Set environment variables from config before importing chromadb
from app.core.config import settings

os.environ["CHROMA_TELEMETRY_ANONYMIZED"] = str(
    settings.CHROMA_TELEMETRY_ANONYMIZED
).lower()
os.environ["CHROMA_TELEMETRY"] = str(settings.CHROMA_TELEMETRY).lower()

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import json
import logging
import time
from app.core.config import settings

logger = logging.getLogger(__name__)


class ChromaRepository:
    """ChromaDB repository for vector storage and retrieval."""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "documents",
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """Initialize ChromaDB client and collection."""
        if host:
            # Use remote ChromaDB server with retry
            self.client = self._connect_with_retry(host, port)
            logger.info(f"Connected to remote ChromaDB server: {host}:{port}")
        else:
            # Use local persistent client
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False, allow_reset=True, is_persistent=True
                ),
            )
            logger.info(f"Using local ChromaDB at: {persist_directory}")

        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()

    def _connect_with_retry(
        self,
        host: str,
        port: Optional[int] = None,
        max_retries: int = 10,
        delay: int = 5,
    ):
        """Connect to ChromaDB server with retry mechanism."""
        if port is None:
            port = settings.CHROMA_SERVER_PORT
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Attempting to connect to ChromaDB server (attempt {attempt + 1}/{max_retries})"
                )
                logger.info(f"Host: {host}, Port: {port}")

                # Use HttpClient with proper configuration
                client = chromadb.HttpClient(
                    host=host,
                    port=port,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=False,
                    ),
                )
                # Test connection by getting version
                client.get_version()

                logger.info("Successfully connected to ChromaDB server")
                return client
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                logger.warning(f"Host: {host}, Port: {port}")
                logger.warning(f"Full error: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Failed to connect to ChromaDB server after {max_retries} attempts"
                    )
                    raise Exception(f"Could not connect to ChromaDB server: {e}")

    def _get_or_create_collection(self):
        """Get existing collection or create new one."""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
            return collection
        except Exception:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document embeddings for RAG system"},
            )
            logger.info(f"Created new collection: {self.collection_name}")
            return collection

    async def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to the collection."""
        try:
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]

            if metadatas is None:
                metadatas = [
                    {"timestamp": datetime.now().isoformat()} for _ in documents
                ]

            # Flatten metadata to ensure only primitive types
            flattened_metadatas = []
            for metadata in metadatas:
                flattened = {}
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        flattened[key] = value
                    elif isinstance(value, dict):
                        # Convert dict to string representation
                        flattened[key] = str(value)
                    else:
                        # Convert any other type to string
                        flattened[key] = str(value)
                flattened_metadatas.append(flattened)

            self.collection.add(
                documents=documents, metadatas=flattened_metadatas, ids=ids
            )

            logger.info(f"Added {len(documents)} documents to collection")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    async def search_documents(
        self, query: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            results = self.collection.query(
                query_texts=[query], n_results=n_results, where=where
            )

            documents = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append(
                        {
                            "id": results["ids"][0][i],
                            "document": doc,
                            "metadata": (
                                results["metadatas"][0][i]
                                if results["metadatas"]
                                else {}
                            ),
                            "distance": (
                                results["distances"][0][i]
                                if results["distances"]
                                else 0.0
                            ),
                        }
                    )

            logger.info(f"Found {len(documents)} similar documents")
            return documents
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        try:
            results = self.collection.get(ids=[document_id])

            if results["documents"] and results["documents"][0]:
                return {
                    "id": results["ids"][0],
                    "document": results["documents"][0],
                    "metadata": results["metadatas"][0] if results["metadatas"] else {},
                }
            return None
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            raise

    async def update_document(
        self, document_id: str, document: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a document."""
        try:
            update_data = {"ids": [document_id], "documents": [document]}

            if metadata:
                update_data["metadatas"] = [metadata]

            self.collection.update(**update_data)
            logger.info(f"Updated document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            return False

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"Deleted document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = self.collection.count()
            return {"total_documents": count, "collection_name": self.collection_name}
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"total_documents": 0, "collection_name": self.collection_name}

    async def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents with their IDs and metadata."""
        try:
            # Get all documents from the collection
            results = self.collection.get()

            documents = []
            if results["ids"]:
                for i, doc_id in enumerate(results["ids"]):
                    document_info = {
                        "id": doc_id,
                        "metadata": (
                            results["metadatas"][i]
                            if results["metadatas"] and i < len(results["metadatas"])
                            else {}
                        ),
                    }
                    # Include a preview of the document content (first 100 characters)
                    if results["documents"] and i < len(results["documents"]):
                        content = results["documents"][i]
                        document_info["content_preview"] = (
                            content[:100] + "..." if len(content) > 100 else content
                        )
                        document_info["content_length"] = len(content)

                    documents.append(document_info)

            logger.info(f"Listed {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise

    async def reset_collection(self) -> bool:
        """Reset the collection (delete all documents)."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self._get_or_create_collection()
            logger.info(f"Reset collection {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False
