"""Generation metrics (transparent heuristics, documented as such).

Faithfulness: fraction of answer content-words also present in the context.
Answer relevance: cosine similarity between question and answer embeddings.
Context relevance: mean retrieval score of the kept chunks.
Hallucination rate: fraction of non-abstained answers with faithfulness < 0.3.
A RAGAS-based judge can replace these without changing callers.
"""
import re

_WORD = re.compile(r"[a-z0-9]+")


def _words(text: str) -> list[str]:
    return _WORD.findall((text or "").lower())


def faithfulness(answer: str, context: str) -> float:
    a, c = set(_words(answer)), set(_words(context))
    if not a:
        return 0.0
    return len(a & c) / len(a)


def answer_relevance(question: str, answer: str) -> float:
    try:
        from app.embeddings.sentence_transformer import get_embedding_service
        svc = get_embedding_service()
        q, a = svc.embed_query(question), svc.embed_query(answer)
        dot = sum(x * y for x, y in zip(q, a))
        return round(max(0.0, min(1.0, dot)), 4)  # embeddings are L2-normalized
    except Exception:
        return 0.0


def context_relevance(results: list[dict]) -> float:
    if not results:
        return 0.0
    return sum(r.get("score", 0.0) for r in results) / len(results)
