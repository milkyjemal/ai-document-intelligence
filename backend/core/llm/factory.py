from __future__ import annotations

from backend.core.config import USE_MOCK_LLM
from backend.core.llm.base import LLMClient
from backend.core.llm.mock import MockLLMClient
from backend.core.llm.openai_client import OpenAILLMClient


def get_llm_client() -> LLMClient:
    """
    Factory that returns the correct LLM implementation.
    - Mock for tests / CI
    - OpenAI for real runs
    """

    if USE_MOCK_LLM:
        return MockLLMClient()

    return OpenAILLMClient()
