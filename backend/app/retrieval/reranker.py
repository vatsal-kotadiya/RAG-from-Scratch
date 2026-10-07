"""Reranker (modular). Current strategy: score-threshold + score sort.

A cross-encoder reranker can be plugged in here later without changing callers:
implement `rerank(question, results, final_k)` with the same signature.
"""
from app.retrieval.filters import apply_min_score, dedupe_by_text


def rerank(question: str, results: list[dict], final_k: int, min_score: float = 0.0) -> list[dict]:
    _ = question  # reserved for future cross-encoder rerankers
    ranked = sorted(dedupe_by_text(results), key=lambda r: r.get("score", 0.0), reverse=True)
    if min_score > 0:
        ranked = apply_min_score(ranked, min_score)
    return ranked[: max(1, final_k)]
