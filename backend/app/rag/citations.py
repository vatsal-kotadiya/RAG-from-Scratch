"""Citation extraction from retrieved chunks (for the Sources UI)."""

PREVIEW_LENGTH = 220


def build_citations(chunks: list[dict]) -> list[dict]:
    sources: list[dict] = []
    for c in chunks:
        text = c.get("text", "")
        sources.append({
            "document_id": c.get("document_id", ""),
            "filename": c.get("filename", ""),
            "page": c.get("page_number"),
            "score": round(float(c.get("score", 0.0)), 4),
            "chunk_id": c.get("chunk_id", ""),
            "text_preview": text[:PREVIEW_LENGTH] + ("..." if len(text) > PREVIEW_LENGTH else ""),
        })
    return sources
