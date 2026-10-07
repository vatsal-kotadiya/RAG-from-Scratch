"""PDF text extraction with per-page granularity (needed for citations).

Uses PyMuPDF (`import pymupdf` — the `fitz` alias is deprecated).
"""
import pymupdf

from app.core.exceptions import ExtractionError
from app.core.logging import get_logger

log = get_logger(__name__)


def extract_pdf(path: str) -> tuple[list[tuple[int | None, str]], int]:
    """Return ([(page_number, text)], page_count). Page numbers are 1-based."""
    try:
        doc = pymupdf.open(path)
    except Exception as e:
        raise ExtractionError(f"Could not open PDF: {e}") from e
    try:
        pages: list[tuple[int | None, str]] = []
        with doc:
            for i, page in enumerate(doc):
                try:
                    text = page.get_text("text") or ""
                except Exception:
                    text = ""
                pages.append((i + 1, text))
            count = len(doc)
        log.info("extracted PDF: %d pages", count)
        return pages, count
    except ExtractionError:
        raise
    except Exception as e:
        raise ExtractionError(f"PDF extraction failed: {e}") from e
