"""Chat endpoints: ask + session history CRUD."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.exceptions import AppError
from app.database.repositories import chat as chat_repo
from app.models.chat import ChatSession, Message
from app.rag.pipeline import get_pipeline
from app.schemas.chat import ChatRequest, ChatResponse, SessionOut

router = APIRouter()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("", response_model=ChatResponse)
def ask_question(req: ChatRequest):
    try:
        result = get_pipeline().ask(req.question, req.document_ids, req.top_k)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    session_id = req.session_id
    if session_id is None:
        session_id = f"ses_{uuid.uuid4().hex[:12]}"
        chat_repo.create_session(ChatSession(
            id=session_id,
            title=(req.question[:60] + ("..." if len(req.question) > 60 else "")),
            created_at=_now(), updated_at=_now(),
        ))
    elif chat_repo.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    chat_repo.add_message(Message(id=f"msg_{uuid.uuid4().hex[:12]}",
                                 session_id=session_id, role="user",
                                 content=req.question, created_at=_now()))
    chat_repo.add_message(Message(id=f"msg_{uuid.uuid4().hex[:12]}",
                                 session_id=session_id, role="assistant",
                                 content=result["answer"], created_at=_now()))
    chat_repo.touch_session(session_id, _now())

    return ChatResponse(
        answer=result["answer"], sources=result["sources"],
        retrieval_metadata=result["retrieval_metadata"],
        provider=result.get("provider", ""), session_id=session_id,
    )


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions():
    return [SessionOut(**s.__dict__) for s in chat_repo.list_sessions()]


@router.get("/sessions/{session_id}")
def get_session(session_id: str):
    session = chat_repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    return {"session": SessionOut(**session.__dict__),
            "messages": [m.__dict__ for m in chat_repo.list_messages(session_id)]}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    if chat_repo.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    chat_repo.delete_session(session_id)
    return {"deleted": session_id}
