"""Echo provider: honest no-key fallback for dev/tests.

Clearly labeled so it can never be mistaken for a real LLM answer.
"""
from app.generation.llm import LLMProvider


class EchoProvider(LLMProvider):
    name = "echo"

    def generate(self, prompt: str) -> str:
        return (
            "[echo provider — no LLM key configured] "
            "Retrieved context was found, but no LLM provider is configured, "
            "so no grounded answer was generated. Set OPENAI_API_KEY, "
            "GEMINI_API_KEY, or run Ollama to enable generation."
        )
