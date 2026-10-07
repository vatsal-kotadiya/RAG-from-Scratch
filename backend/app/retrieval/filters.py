"""Result filters: minimum relevance threshold + dedup helpers."""


def apply_min_score(results: list[dict], min_score: float) -> list[dict]:
    return [r for r in results if r.get("score", 0.0) >= min_score]


def dedupe_by_text(results: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for r in results:
        key = (r.get("text") or "").strip()
        if key and key not in seen:
            seen.add(key)
            out.append(r)
    return out
