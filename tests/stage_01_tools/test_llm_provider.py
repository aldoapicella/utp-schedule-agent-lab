from __future__ import annotations

from schedule_agent.llm.mock_llm import MockLLM
from schedule_agent.llm.openai_llm import OpenAILLM
from schedule_agent.llm.provider import get_llm_client


def test_provider_returns_mock_by_default(monkeypatch) -> None:
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    client = get_llm_client()
    assert isinstance(client, MockLLM)


def test_provider_returns_openai_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = get_llm_client()
    assert isinstance(client, OpenAILLM)
