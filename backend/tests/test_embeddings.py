"""Unit tests: embedding generation, query embedding, dimension consistency."""
from app.embeddings.sentence_transformer import get_embedding_service


def test_embed_documents_shape():
    svc = get_embedding_service()
    vecs = svc.embed_documents(["hello world", "second sentence"])
    assert len(vecs) == 2
    assert all(len(v) == svc.dimension for v in vecs)


def test_embed_query_matches_doc_dimension():
    svc = get_embedding_service()
    q = svc.embed_query("what is attendance?")
    d = svc.embed_documents(["attendance is 75 percent"])[0]
    assert len(q) == len(d) == svc.dimension
    assert svc.dimension > 0


def test_empty_documents():
    assert get_embedding_service().embed_documents([]) == []
