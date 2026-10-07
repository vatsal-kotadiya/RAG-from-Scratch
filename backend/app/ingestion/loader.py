"""Dispatcher: pick the right extractor from the file extension."""
from pathlib import Path

from app.core.exceptions import UnsupportedFileTypeError
from app.ingestion.docx_loader import extract_docx
from app.ingestion.pdf_loader import extract_pdf
from app.ingestion.text_loader import extract_text
from app.models.document import SUPPORTED_EXTENSIONS


def extract(path: str, filename: str) -> tuple[list[tuple[int | None, str]], int, str]:
    """Return (pages, page_count, source_type). Raises on unsupported/empty content."""
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file format '{ext}'. Supported: PDF, DOCX, TXT, MD."
        )
    if ext == ".pdf":
        pages, count = extract_pdf(path)
        source = "pdf"
    elif ext == ".docx":
        pages, count = extract_docx(path)
        source = "docx"
    else:
        pages, count = extract_text(path)
        source = "md" if ext == ".md" else "txt"
    if not pages or not any(t.strip() for _, t in pages):
        from app.core.exceptions import ExtractionError
        raise ExtractionError("Document contains no extractable text.")
    return pages, count, source
