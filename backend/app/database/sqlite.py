"""SQLite application metadata store (documents, sessions, messages, eval runs)."""
import sqlite3
import threading
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)
_lock = threading.RLock()
_conn: sqlite3.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    page_count INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'UPLOADING',
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evaluation_runs (
    id TEXT PRIMARY KEY,
    dataset_name TEXT NOT NULL,
    model_name TEXT NOT NULL,
    embedding_model TEXT NOT NULL,
    top_k INTEGER NOT NULL,
    metrics_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        path: Path = settings.sqlite_path
        path.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(path), check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA foreign_keys = ON")
        with _lock:
            _conn.executescript(SCHEMA)
            _conn.commit()
        log.info("sqlite ready at %s", path)
    return _conn


def execute(query: str, params: tuple = ()) -> sqlite3.Cursor:
    with _lock:
        cur = get_connection().execute(query, params)
        get_connection().commit()
        return cur


def fetch_one(query: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        return get_connection().execute(query, params).fetchone()


def fetch_all(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        return get_connection().execute(query, params).fetchall()
