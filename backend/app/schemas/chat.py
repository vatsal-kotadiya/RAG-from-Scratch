"""Pydantic schemas for chat endpoints (matches IMP.md response schema)."""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    document_ids: list[str] = Field(default_factory=list)
    top_k: int = 5
    session_id: str | None = None


class SourceOut(BaseModel):
    document_id: str
    filename: str
    page: int | None = None
    score: float
    chunk_id: str
    text_preview: str = ""


class RetrievalMetadataOut(BaseModel):
    top_k: int
    retrieved_count: int
    average_score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceOut]
    retrieval_metadata: RetrievalMetadataOut
    provider: str = ""
    session_id: str | None = None


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: str = ""
    updated_at: str = ""
