"""CRUD for evaluation runs."""
import sqlite3

from app.database import sqlite
from app.models.evaluation import EvaluationRun


def create(run: EvaluationRun) -> None:
    sqlite.execute(
        """INSERT INTO evaluation_runs
           (id, dataset_name, model_name, embedding_model, top_k, metrics_json, created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (run.id, run.dataset_name, run.model_name, run.embedding_model,
         run.top_k, run.metrics_json, run.created_at),
    )


def get(run_id: str) -> EvaluationRun | None:
    row = sqlite.fetch_one("SELECT * FROM evaluation_runs WHERE id = ?", (run_id,))
    return EvaluationRun(**dict(row)) if row else None


def list_all() -> list[EvaluationRun]:
    rows = sqlite.fetch_all("SELECT * FROM evaluation_runs ORDER BY created_at DESC")
    return [EvaluationRun(**dict(r)) for r in rows]
