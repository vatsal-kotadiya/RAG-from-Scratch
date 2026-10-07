"""ChromaDB persistent vector store.

Chroma returns cosine *distance* (with hnsw:space=cosine); we convert it to a
user-friendly similarity score: score = clamp(1 - distance, 0, 1).
"""
import threading

from app.core.config import settings
from app.core.logging import get_logger
from app.vectorstore.base import VectorStore

log = get_logger(__name__)
_client = None
_collection_obj = None
_lock = threading.Lock()
COLLECTION_NAME = "documents"


def _get_collection():
    global _client, _collection_obj
    with _lock:
        if _collection_obj is None:
            import chromadb
            settings.chroma_dir.mkdir(parents=True, exist_ok=True)
            _client = chromadb.PersistentClient(path=str(settings.chroma_dir))
            _collection_obj = _client.get_or_create_collection(
                COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
            )
        return _collection_obj


def _to_score(distance: float) -> float:
    return max(0.0, min(1.0, 1.0 - float(distance)))


class ChromaVectorStore(VectorStore):
    def add_documents(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        col = _get_collection()
        col.add(
            ids=[c["chunk_id"] for c in chunks],
            embeddings=embeddings,
            documents=[c["text"] for c in chunks],
            metadatas=[{
                "document_id": c["document_id"],
                "filename": c["filename"],
                # Chroma metadata must be str/int/float/bool: -1 == unknown page.
                "page_number": c["page_number"] if c["page_number"] is not None else -1,
                "source_type": c.get("source_type", ""),
            } for c in chunks],
        )
        log.info("indexed %d chunks for document %s", len(chunks), chunks[0]["document_id"])

    def similarity_search(
        self, query_embedding: list[float], top_k: int,
        document_ids: list[str] | None = None,
    ) -> list[dict]:
        col = _get_collection()
        where = {"document_id": {"$in": document_ids}} if document_ids else None
        n = max(1, top_k)
        try:
            res = col.query(
                query_embeddings=[query_embedding], n_results=n, where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            return []  # e.g. empty collection
        out: list[dict] = []
        ids = (res.get("ids") or [[]])[0]
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        for i, chunk_id in enumerate(ids):
            meta = metas[i] or {}
            page = meta.get("page_number", -1)
            out.append({
                "chunk_id": chunk_id,
                "text": docs[i] if i < len(docs) else "",
                "score": _to_score(dists[i]) if i < len(dists) else 0.0,
                "document_id": meta.get("document_id", ""),
                "filename": meta.get("filename", ""),
                "page_number": None if page == -1 else page,
            })
        return out

    def delete_document(self, document_id: str) -> None:
        _get_collection().delete(where={"document_id": document_id})
        log.info("deleted vectors for document %s", document_id)

    def count(self, document_id: str | None = None) -> int:
        col = _get_collection()
        if document_id:
            return len(col.get(where={"document_id": document_id}, include=[])["ids"])
        return col.count()


def get_vector_store() -> VectorStore:
    return ChromaVectorStore()
