"""Gemini provider (new `google.genai` SDK)."""
from app.core.config import settings
from app.core.exceptions import LLMError
from app.generation.llm import LLMProvider


class GeminiProvider(LLMProvider):
    name = "gemini"

    def generate(self, prompt: str) -> str:
        if not settings.GEMINI_API_KEY:
            raise LLMError("GEMINI_API_KEY is not configured.")
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            resp = client.models.generate_content(
                model=settings.LLM_MODEL, contents=prompt
            )
            return (resp.text or "").strip()
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Gemini request failed: {e}") from e
