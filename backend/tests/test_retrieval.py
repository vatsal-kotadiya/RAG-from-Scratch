"""Unit tests: retrieval returns relevant chunk, honors top-k and doc filter."""
import uuid

from app.embeddings.sentence_transformer import get_embedding_service
from app.vectorstore.chroma_store import ChromaVectorStore

_store = ChromaVectorStore()
_svc = get_embedding_service()


def _make_chunks(doc_id: str, texts: list[str]) -> list[dict]:
    return [{
        "chunk_id": f"{doc_id}-c{i}", "document_id": doc_id,
        "filename": f"{doc_id}.txt", "page_number": None,
        "source_type": "txt", "text": t,
    } for i, t in enumerate(texts)]


def test_relevant_chunk_returned():
    doc_id = f"t1-{uuid.uuid4().hex[:6]}"
    chunks = _make_chunks(doc_id, [
        "The minimum attendance requirement is 75 percent each semester.",
        "The cafeteria serves lunch between noon and two pm daily.",
    ])
    _store.add_documents(chunks, _svc.embed_documents([c["text"] for c in chunks]))
    try:
        results = _store.similarity_search(
            _svc.embed_query("What is the attendance requirement?"),
            top_k=2, document_ids=[doc_id])
        assert len(results) == 2
        assert "attendance" in results[0]["text"].lower()
        assert results[0]["score"] >= results[1]["score"]
    finally:
        _store.delete_document(doc_id)


def test_top_k_and_filtering():
    d1, d2 = f"a-{uuid.uuid4().hex[:6]}", f"b-{uuid.uuid4().hex[:6]}"
    c1 = _make_chunks(d1, ["attendance policy seventy five percent"])
    c2 = _make_chunks(d2, ["attendance policy seventy five percent"])
    for chunks in (c1, c2):
        _store.add_documents(chunks, _svc.embed_documents([c["text"] for c in chunks]))
    try:
        q = _svc.embed_query("attendance policy")
        only_d2 = _store.similarity_search(q, top_k=5, document_ids=[d2])
        assert only_d2 and all(r["document_id"] == d2 for r in only_d2)
        one = _store.similarity_search(q, top_k=1)
        assert len(one) == 1
    finally:
        _store.delete_document(d1)
        _store.delete_document(d2)
