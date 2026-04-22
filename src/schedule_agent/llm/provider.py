from __future__ import annotations

import os

from schedule_agent.llm.base import LLMClient
from schedule_agent.llm.mock_llm import MockLLM
from schedule_agent.llm.openai_llm import OpenAILLM


def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider == "mock":
        return MockLLM()
    if provider == "openai":
        return OpenAILLM()
    return MockLLM()
