"""Evaluator: run dataset items through RAG (+ optional LLM-only baseline)."""
import time
import uuid
from datetime import datetime, timezone

from app.core.config import settings
from app.evaluation import generation_metrics as gm
from app.evaluation import retrieval_metrics as rm
from app.evaluation.dataset import load_dataset
from app.rag.pipeline import get_pipeline


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate(dataset_name: str = "seed", top_k: int = 5, include_baseline: bool = True) -> dict:
    items, _ = load_dataset(dataset_name)
    pipeline = get_pipeline()
    k = top_k or settings.TOP_K

    precisions, recalls, rrs, sims = [], [], [], []
    faiths, rels, ctxrels, halls = [], [], [], []
    base_faiths: list[float] = []
    abstained_correct, abstained_total = 0, 0

    for item in items:
        q = item["question"]
        res = pipeline.ask(q, top_k=k)
        retrieved = res["sources"]

        if item.get("unanswerable"):
            # Correct behavior is abstention; retrieval scores are meaningless here.
            abstained_total += 1
            if res.get("abstained"):
                abstained_correct += 1
                faiths.append(1.0)
            else:
                faiths.append(gm.faithfulness(res["answer"], res.get("context", "")))
            rels.append(0.0)
            ctxrels.append(gm.context_relevance(retrieved))
            continue

        precisions.append(rm.precision_at_k(retrieved, item, k))
        recalls.append(rm.recall_at_k(retrieved, item, k))
        rrs.append(rm.reciprocal_rank(retrieved, item))
        sims.append(rm.average_score(retrieved))

        if res.get("abstained"):
            faiths.append(1.0)  # abstaining instead of inventing is correct
            rels.append(0.0)
        else:
            f = gm.faithfulness(res["answer"], res.get("context", ""))
            faiths.append(f)
            rels.append(gm.answer_relevance(q, res["answer"]))
            if f < 0.3:
                halls.append(1)
        ctxrels.append(gm.context_relevance(retrieved))

        if include_baseline:
            base = pipeline.ask_baseline(q)
            base_faiths.append(gm.faithfulness(base["answer"], res.get("context", "")))

    n = max(1, len(items))
    metrics = {
        "num_questions": len(items),
        "retrieval": {
            f"precision@{k}": round(sum(precisions) / n, 4),
            f"recall@{k}": round(sum(recalls) / n, 4),
            "mrr": round(sum(rrs) / n, 4),
            "avg_similarity": round(sum(sims) / n, 4),
        },
        "generation_rag": {
            "faithfulness": round(sum(faiths) / n, 4),
            "answer_relevance": round(sum(rels) / n, 4),
            "context_relevance": round(sum(ctxrels) / n, 4),
            "hallucination_rate": round(len(halls) / n, 4),
        },
    }
    if include_baseline and base_faiths:
        metrics["generation_baseline_llm_only"] = {
            "faithfulness": round(sum(base_faiths) / n, 4),
        }
    if abstained_total:
        metrics["abstention"] = {
            "unanswerable_questions": abstained_total,
            "correctly_abstained": abstained_correct,
            "abstention_accuracy": round(abstained_correct / abstained_total, 4),
        }
    metrics["evaluated_at"] = _now()
    metrics["run_id"] = f"eval_{uuid.uuid4().hex[:8]}"
    return metrics
