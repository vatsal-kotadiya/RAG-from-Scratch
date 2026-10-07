"""CRUD for documents metadata."""
import sqlite3

from app.database import sqlite
from app.models.document import Document


def _row_to_doc(row: sqlite3.Row) -> Document:
    return Document(**dict(row))


def create(doc: Document) -> None:
    sqlite.execute(
        """INSERT INTO documents (id, filename, file_path, file_type, file_size,
           page_count, chunk_count, status, error_message, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (doc.id, doc.filename, doc.file_path, doc.file_type, doc.file_size,
         doc.page_count, doc.chunk_count, doc.status, doc.error_message,
         doc.created_at, doc.updated_at),
    )


def get(document_id: str) -> Document | None:
    row = sqlite.fetch_one("SELECT * FROM documents WHERE id = ?", (document_id,))
    return _row_to_doc(row) if row else None


def list_all() -> list[Document]:
    return [_row_to_doc(r) for r in sqlite.fetch_all("SELECT * FROM documents ORDER BY created_at DESC")]


def update(document_id: str, **fields) -> None:
    if not fields:
        return
    sets = ", ".join(f"{k} = ?" for k in fields)
    sqlite.execute(f"UPDATE documents SET {sets} WHERE id = ?", (*fields.values(), document_id))


def delete(document_id: str) -> None:
    sqlite.execute("DELETE FROM documents WHERE id = ?", (document_id,))
