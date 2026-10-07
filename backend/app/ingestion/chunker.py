"""Word-based sliding-window chunking.

`chunk_size` / `chunk_overlap` are configured in tokens (see .env); here words
are used as a transparent 1-word ~= 1-token approximation, documented rather
than hidden. Every chunk keeps full metadata for citations.
"""
import uuid


def chunk_pages(
    pages: list[tuple[int | None, str]],
    document_id: str,
    filename: str,
    source_type: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[dict]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    overlap = max(0, min(chunk_overlap, chunk_size - 1))
    step = chunk_size - overlap
    chunks: list[dict] = []
    for page_number, text in pages:
        words = text.split()
        if not words:
            continue
        for start in range(0, len(words), step):
            window = words[start:start + chunk_size]
            if not window:
                break
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "document_id": document_id,
                "filename": filename,
                "page_number": page_number,
                "source_type": source_type,
                "text": " ".join(window),
            })
            if start + chunk_size >= len(words):
                break
    return chunks
