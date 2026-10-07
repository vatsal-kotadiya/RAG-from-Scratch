"""Unit tests: context/prompt construction, no-context behavior, citations."""
from app.generation.prompts import SYSTEM_PROMPT, build_prompt
from app.rag.citations import build_citations
from app.rag.context_builder import build_context
from app.rag.pipeline import NO_CONTEXT_MESSAGE, RAGPipeline


def _chunks():
    return [
        {"chunk_id": "c1", "document_id": "d1", "filename": "handbook.pdf",
         "page_number": 42, "score": 0.91, "text": "Attendance must be 75 percent."},
        {"chunk_id": "c2", "document_id": "d1", "filename": "handbook.pdf",
         "page_number": 43, "score": 0.86, "text": "Below 75 percent triggers a warning."},
    ]


def test_context_construction():
    ctx = build_context(_chunks())
    assert "SOURCE 1" in ctx and "SOURCE 2" in ctx
    assert "handbook.pdf" in ctx and "Page 42" in ctx
    assert "75 percent" in ctx


def test_prompt_contains_context_and_question():
    prompt = build_prompt("How much?", "CTX")
    assert "How much?" in prompt and "CTX" in prompt
    assert "only the" in SYSTEM_PROMPT and "provided context" in SYSTEM_PROMPT


def test_citation_generation():
    cites = build_citations(_chunks())
    assert cites[0]["page"] == 42
    assert cites[0]["score"] == 0.91
    assert cites[0]["chunk_id"] == "c1"
    assert cites[0]["text_preview"]


def test_no_context_abstains_without_llm_calls(monkeypatch):
    pipe = RAGPipeline()
    monkeypatch.setattr(
        "app.rag.pipeline.get_retriever",
        lambda: type("R", (), {"retrieve": lambda self, *a, **k: []})(),
    )
    called = []
    monkeypatch.setattr(
        "app.rag.pipeline.get_llm_provider",
        lambda: type("P", (), {"name": "echo",
                              "generate": lambda self, p: called.append(p) or "x"})(),
    )
    import app.core.config as cfg
    monkeypatch.setattr(cfg.settings, "MIN_RETRIEVAL_SCORE", 0.99)
    res = pipe.ask("anything", top_k=3)
    assert res["abstained"] is True
    assert res["answer"] == NO_CONTEXT_MESSAGE
    assert called == []
