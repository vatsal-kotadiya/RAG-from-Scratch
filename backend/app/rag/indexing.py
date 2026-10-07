"""Document indexing orchestrator: extract -> clean -> chunk -> embed -> store."""
import os
from datetime import datetime, timezone

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.database.repositories import documents as doc_repo
from app.embeddings.sentence_transformer import get_embedding_service
from app.ingestion.chunker import chunk_pages
from app.ingestion.cleaner import clean_text
from app.ingestion.loader import extract
from app.vectorstore.chroma_store import get_vector_store

log = get_logger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def index_document(document_id: str) -> None:
    """Full pipeline for one document. Sets READY or FAILED with error message."""
    doc = doc_repo.get(document_id)
    if doc is None:
        log.error("index requested for unknown document %s", document_id)
        return
    try:
        doc_repo.update(document_id, status="PROCESSING", updated_at=_now())
        log.info("extracting %s", doc.filename)
        pages, page_count, source_type = extract(doc.file_path, doc.filename)

        doc_repo.update(document_id, status="INDEXING", page_count=page_count, updated_at=_now())
        cleaned = [(p, clean_text(t)) for p, t in pages]
        chunks = chunk_pages(
            cleaned, document_id, doc.filename, source_type,
            chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP,
        )
        log.info("chunked %s into %d chunks", doc.filename, len(chunks))

        embeddings = get_embedding_service().embed_documents([c["text"] for c in chunks])
        store = get_vector_store()
        store.delete_document(document_id)  # idempotent re-index
        store.add_documents(chunks, embeddings)

        doc_repo.update(
            document_id, status="READY", chunk_count=len(chunks),
            error_message=None, updated_at=_now(),
        )
        log.info("document READY: %s (%d chunks)", doc.filename, len(chunks))
    except AppError as e:
        log.error("indexing failed for %s: %s", doc.filename, e.message)
        doc_repo.update(document_id, status="FAILED", error_message=e.message, updated_at=_now())
    except Exception as e:  # never leave a document stuck in PROCESSING
        log.error("indexing failed for %s: %s", doc.filename, e)
        doc_repo.update(document_id, status="FAILED", error_message=str(e), updated_at=_now())


def delete_document_everywhere(document_id: str) -> bool:
    """Delete file + SQLite row + vectors. Returns True if anything was removed."""
    doc = doc_repo.get(document_id)
    if doc is None:
        return False
    try:
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except OSError as e:
        log.warning("could not delete file %s: %s", doc.file_path, e)
    try:
        get_vector_store().delete_document(document_id)
    except Exception as e:
        log.warning("could not delete vectors for %s: %s", document_id, e)
    doc_repo.delete(document_id)
    return True
