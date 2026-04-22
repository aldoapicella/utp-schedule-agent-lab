from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GeneratedResponse:
    assistant_message: str
    explanation: list[str]


class LLMClient:
    def compose_response(self, context: dict) -> GeneratedResponse:
        raise NotImplementedError


class LLMProviderError(RuntimeError):
    """Raised when a configured LLM provider cannot complete a request."""
