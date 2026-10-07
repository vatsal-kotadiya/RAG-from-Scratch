"""Pydantic schemas for document endpoints."""
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    page_count: int = 0
    chunk_count: int = 0
    status: str
    error_message: str | None = None
    created_at: str = ""
    updated_at: str = ""
