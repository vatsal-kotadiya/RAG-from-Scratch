"""DOCX text extraction via python-docx (paragraphs + tables, in order)."""
from docx import Document as DocxDocument

from app.core.exceptions import ExtractionError
from app.core.logging import get_logger

log = get_logger(__name__)


def extract_docx(path: str) -> tuple[list[tuple[int | None, str]], int]:
    try:
        doc = DocxDocument(path)
    except Exception as e:
        raise ExtractionError(f"Could not open DOCX: {e}") from e
    try:
        parts: list[str] = []
        for para in doc.paragraphs:
            if para.text and para.text.strip():
                parts.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells if c.text and c.text.strip()]
                if cells:
                    parts.append(" | ".join(cells))
        # DOCX has no reliable page numbers -> page is None.
        return ([(None, "\n".join(parts))] if parts else []), 0
    except Exception as e:
        raise ExtractionError(f"DOCX extraction failed: {e}") from e
