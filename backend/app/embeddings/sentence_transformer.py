"""Local sentence-transformers embedding service (all-MiniLM-L6-v2 default)."""
import threading

from app.core.config import settings
from app.core.exceptions import EmbeddingError
from app.core.logging import get_logger
from app.embeddings.base import EmbeddingService

log = get_logger(__name__)
_lock = threading.Lock()
_model = None
_model_name: str | None = None


def _load_model():
    global _model, _model_name
    with _lock:
        if _model is None or _model_name != settings.EMBEDDING_MODEL:
            try:
                from sentence_transformers import SentenceTransformer
                log.info("loading embedding model: %s", settings.EMBEDDING_MODEL)
                _model = SentenceTransformer(settings.EMBEDDING_MODEL)
                _model_name = settings.EMBEDDING_MODEL
            except Exception as e:
                raise EmbeddingError(f"Embedding model failed to load: {e}") from e
        return _model


class SentenceTransformerEmbeddingService(EmbeddingService):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            vectors = _load_model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return [list(map(float, v)) for v in vectors]
        except Exception as e:
            raise EmbeddingError(f"Document embedding failed: {e}") from e

    def embed_query(self, text: str) -> list[float]:
        try:
            vector = _load_model().encode([text], normalize_embeddings=True, show_progress_bar=False)[0]
            return list(map(float, vector))
        except Exception as e:
            raise EmbeddingError(f"Query embedding failed: {e}") from e

    @property
    def dimension(self) -> int:
        return int(_load_model().get_embedding_dimension())


def get_embedding_service() -> EmbeddingService:
    if settings.EMBEDDING_PROVIDER != "sentence_transformers":
        raise EmbeddingError(f"Unknown embedding provider: {settings.EMBEDDING_PROVIDER}")
    return SentenceTransformerEmbeddingService()
