"""Ollama provider (local models via HTTP, no key needed)."""
import httpx

from app.core.config import settings
from app.core.exceptions import LLMError
from app.generation.llm import LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def generate(self, prompt: str) -> str:
        try:
            with httpx.Client(timeout=120.0) as client:
                r = client.post(
                    f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                    json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False},
                )
                r.raise_for_status()
                return (r.json().get("response") or "").strip()
        except Exception as e:
            raise LLMError(f"Ollama request failed: {e}") from e
