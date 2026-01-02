from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional


SchemaName = Literal["bol_v1"]


@dataclass(frozen=True)
class LLMExtractRequest:
    schema: SchemaName
    text: str
    document_hint: Optional[str] = None  # e.g., filename, carrier name, etc.


@dataclass(frozen=True)
class LLMExtractResponse:
    schema: SchemaName
    json: Dict[str, Any]
    raw: Optional[str] = None  # provider raw response if you want to store it later


class LLMClient(ABC):
    """
    Provider-agnostic interface. Later you can add OpenAI/Anthropic clients
    implementing this exact contract.
    """

    @abstractmethod
    def extract_json(self, request: LLMExtractRequest) -> LLMExtractResponse:
        """
        Return a JSON-serializable dict that matches the requested schema.
        Must be deterministic for a given input when possible (helps testing).
        """
        raise NotImplementedError
