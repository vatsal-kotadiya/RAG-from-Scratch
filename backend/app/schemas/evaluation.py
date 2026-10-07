"""Pydantic schemas for evaluation endpoints."""
from pydantic import BaseModel


class EvaluationRunRequest(BaseModel):
    dataset_name: str = "seed"
    top_k: int = 5
    include_baseline: bool = True


class EvaluationRunOut(BaseModel):
    id: str
    dataset_name: str
    model_name: str
    embedding_model: str
    top_k: int
    metrics: dict
    created_at: str = ""
