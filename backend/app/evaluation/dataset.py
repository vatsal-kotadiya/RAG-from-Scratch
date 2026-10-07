"""Evaluation dataset loader (backend/evaluation_dataset/*.json)."""
import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_DIR = BACKEND_DIR / "evaluation_dataset"


def load_dataset(name: str) -> tuple[list[dict], str]:
    """Return (items, source_file). Items: {question, expected_answer,
    relevant_document, relevant_pages}."""
    path = DATASET_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Evaluation dataset '{name}' not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    return items, str(path)


def list_datasets() -> list[str]:
    if not DATASET_DIR.exists():
        return []
    return sorted(p.stem for p in DATASET_DIR.glob("*.json"))
