"""Document endpoints: upload / list / get / delete / re-index."""
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.exceptions import AppError
from app.database.repositories import documents as doc_repo
from app.models.document import SUPPORTED_EXTENSIONS, Document
from app.rag.indexing import delete_document_everywhere, index_document
from app.schemas.document import DocumentOut

router = APIRouter()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_out(doc: Document) -> DocumentOut:
    return DocumentOut(**doc.__dict__)


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(background: BackgroundTasks, file: UploadFile = File(...)):
    filename = Path(file.filename or "").name  # strip any path (traversal protection)
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'.")
    content = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="Maximum file size exceeded.")
    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    safe_name = f"{document_id}_{filename}"
    file_path = settings.upload_dir / safe_name
    file_path.write_bytes(content)

    doc = Document(
        id=document_id, filename=filename, file_path=str(file_path),
        file_type=ext.lstrip("."), file_size=len(content),
        status="UPLOADING", created_at=_now(), updated_at=_now(),
    )
    doc_repo.create(doc)
    background.add_task(index_document, document_id)
    return _to_out(doc_repo.get(document_id))


@router.get("", response_model=list[DocumentOut])
def list_documents():
    return [_to_out(d) for d in doc_repo.list_all()]


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: str):
    doc = doc_repo.get(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return _to_out(doc)


@router.delete("/{document_id}")
def delete_document(document_id: str):
    if not delete_document_everywhere(document_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"deleted": document_id}


@router.post("/{document_id}/reindex", response_model=DocumentOut)
def reindex_document(document_id: str, background: BackgroundTasks):
    doc = doc_repo.get(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    if not Path(doc.file_path).exists():
        raise HTTPException(status_code=404, detail="Source file missing; cannot re-index.")
    doc_repo.update(document_id, status="PROCESSING", error_message=None, updated_at=_now())
    background.add_task(index_document, document_id)
    return _to_out(doc_repo.get(document_id))
