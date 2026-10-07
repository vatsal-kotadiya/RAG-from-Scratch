"""Document metadata model (mirrors SQLite `documents` table)."""
from dataclasses import dataclass


@dataclass
class Document:
    id: str
    filename: str
    file_path: str
    file_type: str
    file_size: int
    page_count: int = 0
    chunk_count: int = 0
    status: str = "UPLOADING"
    error_message: str | None = None
    created_at: str = ""
    updated_at: str = ""


STATUSES = ("UPLOADING", "PROCESSING", "INDEXING", "READY", "FAILED")
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
