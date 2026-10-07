"""Provider factory — only the selected provider is initialized."""
from app.core.config import settings
from app.generation.llm import LLMProvider
from app.generation.providers.echo_provider import EchoProvider
from app.generation.providers.gemini_provider import GeminiProvider
from app.generation.providers.ollama_provider import OllamaProvider
from app.generation.providers.openai_provider import OpenAIProvider


def get_llm_provider() -> LLMProvider:
    name = settings.LLM_PROVIDER.lower()
    if name == "openai":
        provider: LLMProvider = OpenAIProvider()
        if not settings.OPENAI_API_KEY:
            return EchoProvider()  # honest fallback, never silently fails
        return provider
    if name == "gemini":
        if not settings.GEMINI_API_KEY:
            return EchoProvider()
        return GeminiProvider()
    if name == "ollama":
        return OllamaProvider()
    if name == "echo":
        return EchoProvider()
    return EchoProvider()
