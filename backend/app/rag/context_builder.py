"""Context builder: turn retrieved chunks into a labeled SOURCE block."""


def build_context(chunks: list[dict]) -> str:
    blocks: list[str] = []
    for i, c in enumerate(chunks, 1):
        page = c.get("page_number")
        page_str = f"Page {page}" if page is not None else "Page unknown"
        blocks.append(
            f"SOURCE {i}\n"
            f"Document: {c.get('filename', 'unknown')} | {page_str}\n\n"
            f"{c.get('text', '')}"
        )
    return "\n\n---\n\n".join(blocks)
