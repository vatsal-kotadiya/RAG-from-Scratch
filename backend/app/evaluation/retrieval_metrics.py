"""Retrieval metrics: Precision@K, Recall@K, MRR, average similarity.

Relevance labels come from the evaluation dataset (relevant_document /
relevant_pages) — never fabricated.
"""


def _is_relevant(result: dict, item: dict) -> bool:
    if result.get("filename") != item.get("relevant_document"):
        return False
    pages = item.get("relevant_pages") or []
    if not pages:
        return True
    return result.get("page_number") in pages


def precision_at_k(results: list[dict], item: dict, k: int) -> float:
    top = results[:k]
    if not top:
        return 0.0
    return sum(1 for r in top if _is_relevant(r, item)) / len(top)


def recall_at_k(results: list[dict], item: dict, k: int, total_relevant: int = 1) -> float:
    if total_relevant <= 0:
        return 0.0
    return sum(1 for r in results[:k] if _is_relevant(r, item)) / total_relevant


def reciprocal_rank(results: list[dict], item: dict) -> float:
    for i, r in enumerate(results, 1):
        if _is_relevant(r, item):
            return 1.0 / i
    return 0.0


def average_score(results: list[dict]) -> float:
    if not results:
        return 0.0
    return sum(r.get("score", 0.0) for r in results) / len(results)
