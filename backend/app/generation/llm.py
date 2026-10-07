"""LLM provider abstraction — one interface, swappable backends."""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...
