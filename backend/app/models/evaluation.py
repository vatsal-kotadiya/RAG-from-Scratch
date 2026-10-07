"""Evaluation run model."""
from dataclasses import dataclass


@dataclass
class EvaluationRun:
    id: str
    dataset_name: str
    model_name: str
    embedding_model: str
    top_k: int
    metrics_json: str
    created_at: str = ""
