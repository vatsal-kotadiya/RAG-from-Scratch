"""OpenAI provider (lazy client, key from env)."""
from app.core.config import settings
from app.core.exceptions import LLMError
from app.generation.llm import LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def generate(self, prompt: str) -> str:
        if not settings.OPENAI_API_KEY:
            raise LLMError("OPENAI_API_KEY is not configured.")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return (resp.choices[0].message.content or "").strip()
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"OpenAI request failed: {e}") from e
