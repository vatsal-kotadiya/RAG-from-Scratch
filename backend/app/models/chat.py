"""Chat session / message models."""
from dataclasses import dataclass


@dataclass
class ChatSession:
    id: str
    title: str
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Message:
    id: str
    session_id: str
    role: str
    content: str
    created_at: str = ""
