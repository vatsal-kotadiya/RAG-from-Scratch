"""Unit tests: chunk size, overlap, metadata preservation."""
from app.ingestion.chunker import chunk_pages


def _pages(n_words=1000):
    return [(1, " ".join(f"word{i}" for i in range(n_words)))]


def test_chunk_size_respected():
    chunks = chunk_pages(_pages(), "d1", "f.txt", "txt", chunk_size=100, chunk_overlap=10)
    assert chunks
    assert all(len(c["text"].split()) <= 100 for c in chunks)


def test_overlap_present():
    chunks = chunk_pages(_pages(250), "d1", "f.txt", "txt", chunk_size=100, chunk_overlap=20)
    first = set(chunks[0]["text"].split())
    second = set(chunks[1]["text"].split())
    assert len(first & second) > 0


def test_metadata_preserved():
    chunks = chunk_pages([(42, "hello world foo bar")], "doc9", "handbook.pdf", "pdf",
                         chunk_size=500, chunk_overlap=50)
    assert len(chunks) == 1
    c = chunks[0]
    assert c["document_id"] == "doc9"
    assert c["filename"] == "handbook.pdf"
    assert c["page_number"] == 42
    assert c["source_type"] == "pdf"
    assert c["chunk_id"]


def test_none_page_for_txt():
    chunks = chunk_pages([(None, "a b c")], "d2", "n.txt", "txt")
    assert chunks[0]["page_number"] is None


def test_empty_text_no_chunks():
    assert chunk_pages([(1, "   ")], "d3", "e.txt", "txt") == []
