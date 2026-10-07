"""API tests: upload validation, list, chat abstention, eval runs."""
import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_upload_rejects_bad_extension():
    r = client.post("/api/documents/upload",
                    files={"file": ("evil.exe", io.BytesIO(b"data"), "application/octet-stream")})
    assert r.status_code == 400


def test_upload_rejects_empty_file():
    r = client.post("/api/documents/upload",
                    files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")})
    assert r.status_code == 400


def test_list_documents_shape():
    r = client.get("/api/documents")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_chat_unknown_question_abstains_or_answers():
    r = client.post("/api/chat", json={
        "question": "xqz definitely not in any document ever",
        "document_ids": [], "top_k": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] and "sources" in body and "retrieval_metadata" in body


def test_chat_empty_question_rejected():
    r = client.post("/api/chat", json={"question": "", "document_ids": []})
    assert r.status_code == 422
