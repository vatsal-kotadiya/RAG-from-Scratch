"""Evaluation endpoints: run eval, list runs, get run."""
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.database.repositories import evaluation as eval_repo
from app.evaluation.evaluator import evaluate
from app.models.evaluation import EvaluationRun
from app.schemas.evaluation import EvaluationRunOut, EvaluationRunRequest

router = APIRouter()


def _to_out(run: EvaluationRun) -> EvaluationRunOut:
    return EvaluationRunOut(
        id=run.id, dataset_name=run.dataset_name, model_name=run.model_name,
        embedding_model=run.embedding_model, top_k=run.top_k,
        metrics=json.loads(run.metrics_json), created_at=run.created_at,
    )


@router.post("/run", response_model=EvaluationRunOut)
def run_evaluation(req: EvaluationRunRequest):
    try:
        metrics = evaluate(req.dataset_name, req.top_k, req.include_baseline)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    run = EvaluationRun(
        id=metrics.pop("run_id"), dataset_name=req.dataset_name,
        model_name=f"{settings.LLM_PROVIDER}:{settings.LLM_MODEL}",
        embedding_model=f"{settings.EMBEDDING_PROVIDER}:{settings.EMBEDDING_MODEL}",
        top_k=req.top_k, metrics_json=json.dumps(metrics),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    eval_repo.create(run)
    return _to_out(run)


@router.get("/runs", response_model=list[EvaluationRunOut])
def list_runs():
    return [_to_out(r) for r in eval_repo.list_all()]


@router.get("/runs/{run_id}", response_model=EvaluationRunOut)
def get_run(run_id: str):
    run = eval_repo.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Evaluation run not found.")
    return _to_out(run)
