"""CRUD for chat sessions and messages."""
import sqlite3

from app.database import sqlite
from app.models.chat import ChatSession, Message


def create_session(s: ChatSession) -> None:
    sqlite.execute(
        "INSERT INTO chat_sessions (id, title, created_at, updated_at) VALUES (?,?,?,?)",
        (s.id, s.title, s.created_at, s.updated_at),
    )


def get_session(session_id: str) -> ChatSession | None:
    row = sqlite.fetch_one("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
    return ChatSession(**dict(row)) if row else None


def list_sessions() -> list[ChatSession]:
    rows = sqlite.fetch_all("SELECT * FROM chat_sessions ORDER BY updated_at DESC")
    return [ChatSession(**dict(r)) for r in rows]


def delete_session(session_id: str) -> None:
    sqlite.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    sqlite.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))


def add_message(m: Message) -> None:
    sqlite.execute(
        "INSERT INTO messages (id, session_id, role, content, created_at) VALUES (?,?,?,?,?)",
        (m.id, m.session_id, m.role, m.content, m.created_at),
    )


def list_messages(session_id: str) -> list[Message]:
    rows = sqlite.fetch_all(
        "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,)
    )
    return [Message(**dict(r)) for r in rows]


def touch_session(session_id: str, updated_at: str) -> None:
    sqlite.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (updated_at, session_id))
