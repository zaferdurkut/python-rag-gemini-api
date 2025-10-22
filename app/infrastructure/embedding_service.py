from typing import List, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.exceptions import EmbeddingError
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        batch_size: Optional[int] = None,
    ):
        """Initialize the embedding service."""
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.device = device or settings.EMBEDDING_DEVICE
        self.batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Embedding model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise EmbeddingError(
                message=f"Failed to initialize embedding model '{self.model_name}': {str(e)}",
                details={"model_name": self.model_name, "error": str(e)},
            )

    def generate_embeddings(
        self, texts: Union[str, List[str]], batch_size: Optional[int] = None
    ) -> np.ndarray:
        """Generate embeddings for given texts."""
        if self.model is None:
            raise EmbeddingError(
                message="Embedding model is not initialized",
                details={"error": "model_not_initialized"},
            )

        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.array([])

        # Validate batch size
        effective_batch_size = batch_size or self.batch_size
        if effective_batch_size <= 0:
            raise EmbeddingError(
                message=f"Invalid batch size {effective_batch_size}: must be greater than 0",
                details={"batch_size": effective_batch_size},
            )

        try:
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                batch_size=effective_batch_size,
                show_progress_bar=len(texts) > 10,
                convert_to_numpy=True,
            )

            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise EmbeddingError(
                message=f"Failed to generate embeddings for {len(texts)} texts: {str(e)}",
                details={"text_count": len(texts), "error": str(e)},
            )

    def generate_single_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        return self.generate_embeddings([text])[0]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model."""
        if self.model is None:
            raise EmbeddingError(
                message="Embedding model is not initialized",
                details={"error": "model_not_initialized"},
            )
        return self.model.get_sentence_embedding_dimension()

    def validate_embedding_dimension(self, embeddings: np.ndarray) -> None:
        """Validate that embeddings have the expected dimension."""
        if self.model is None:
            raise EmbeddingError(
                message="Embedding model is not initialized",
                details={"error": "model_not_initialized"},
            )

        expected_dim = self.get_embedding_dimension()
        if embeddings.ndim == 1:
            actual_dim = embeddings.shape[0]
        elif embeddings.ndim == 2:
            actual_dim = embeddings.shape[1]
        else:
            raise EmbeddingError(
                message=f"Invalid embedding shape. Expected 1D or 2D array, got {embeddings.ndim}D",
                details={
                    "expected_dimension": expected_dim,
                    "actual_shape": embeddings.shape,
                },
            )

        if actual_dim != expected_dim:
            raise EmbeddingError(
                message=f"Embedding dimension mismatch. Expected: {expected_dim}, Actual: {actual_dim}",
                details={
                    "expected_dimension": expected_dim,
                    "actual_dimension": actual_dim,
                },
            )

    def get_model_info(self) -> dict:
        """Get information about the current model."""
        if self.model is None:
            return {
                "model_name": self.model_name,
                "device": self.device,
                "loaded": False,
            }

        return {
            "model_name": self.model_name,
            "device": self.device,
            "loaded": True,
            "embedding_dimension": self.get_embedding_dimension(),
            "batch_size": self.batch_size,
        }

    def reload_model(self, model_name: Optional[str] = None):
        """Reload the model with a new model name."""
        try:
            if model_name:
                self.model_name = model_name
            self._initialize_model()
        except Exception as e:
            logger.error(f"Failed to reload model: {e}")
            raise EmbeddingError(
                message=f"Failed to reload model '{model_name or self.model_name}': {str(e)}",
                details={"model_name": model_name or self.model_name, "error": str(e)},
            )

    def change_device(self, device: str):
        """Change the device for the model."""
        try:
            if self.model is not None:
                self.model = self.model.to(device)
            self.device = device
            logger.info(f"Model moved to device: {device}")
        except Exception as e:
            logger.error(f"Failed to change device to {device}: {e}")
            raise EmbeddingError(
                message=f"Failed to change device to '{device}': {str(e)}",
                details={
                    "device": device,
                    "model_name": self.model_name,
                    "error": str(e),
                },
            )


# Global embedding service instance
embedding_service = EmbeddingService()
