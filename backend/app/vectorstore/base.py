"""Vector store abstraction — ChromaDB today, FAISS later, same interface."""
from abc import ABC, abstractmethod


class VectorStore(ABC):
    @abstractmethod
    def add_documents(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        ...

    @abstractmethod
    def similarity_search(
        self, query_embedding: list[float], top_k: int,
        document_ids: list[str] | None = None,
    ) -> list[dict]:
        """Return [{chunk_id, text, score, document_id, filename, page_number}]."""

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        ...

    @abstractmethod
    def count(self, document_id: str | None = None) -> int:
        ...
