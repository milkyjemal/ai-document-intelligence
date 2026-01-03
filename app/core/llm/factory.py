from __future__ import annotations

from app.core.config import USE_MOCK_LLM
from app.core.llm.base import LLMClient
from app.core.llm.mock import MockLLMClient
from app.core.llm.openai_client import OpenAILLMClient


def get_llm_client() -> LLMClient:
    """
    Factory that returns the correct LLM implementation.
    - Mock for tests / CI
    - OpenAI for real runs
    """
    if USE_MOCK_LLM:
        return MockLLMClient()

    return OpenAILLMClient()
