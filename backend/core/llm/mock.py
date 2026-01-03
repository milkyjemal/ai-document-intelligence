# app/core/llm/mock.py
from __future__ import annotations

from typing import Any, Dict

from backend.core.llm.base import LLMClient, LLMExtractRequest, LLMExtractResponse


class MockLLMClient(LLMClient):
    """
    Deterministic mock for local development + tests.

    Strategy:
    - If the text looks like a BOL, return a plausible bol_v1 JSON payload.
    - Otherwise return a low-confidence payload with warnings.

    Notes:
    - This does NOT try to "actually parse" the document.
    - It returns a stable shape that your pipeline can validate with Pydantic.
    """

    def extract_json(self, request: LLMExtractRequest) -> LLMExtractResponse:
        schema = request.schema
        text = request.text or ""

        if schema != "bol_v1":
            raise ValueError(f"MockLLMClient does not support schema: {schema}")

        looks_like_bol = (
            "BILL OF LADING" in text.upper()
            or "STRAIGHT BILL OF LADING" in text.upper()
            or "CONSIGNEE" in text.upper()
        )

        if looks_like_bol:
            payload: Dict[str, Any] = {
                "document_type": "BOL",
                "carrier_name": "TForce Freight",
                "bol_number": "MOCK-BOL-0001",
                "shipment_date": None,
                "shipper": {"name": "Mock Shipper Inc.", "address": None, "phone": None},
                "consignee": {"name": "Mock Consignee LLC", "address": None, "phone": None},
                "origin": {"city": None, "state": None, "postal_code": None, "country": None},
                "destination": {"city": None, "state": None, "postal_code": None, "country": None},
                "line_items": [
                    {
                        "description": "GENERAL FREIGHT",
                        "pieces": 1,
                        "weight_lb": 100.0,
                        "nmfc": None,
                        "freight_class": "100",
                    }
                ],
                "total_pieces": 1,
                "total_weight_lb": 100.0,
                "po_numbers": [],
                "pro_number": None,
                "reference_numbers": [],
                "confidence": 0.75,
                "warnings": [
                    "mock_llm: values are synthetic; plug in a real provider to extract actual fields."
                ],
            }
        else:
            payload = {
                "document_type": "BOL",
                "carrier_name": None,
                "bol_number": "UNKNOWN",
                "shipment_date": None,
                "shipper": None,
                "consignee": None,
                "origin": None,
                "destination": None,
                "line_items": [],
                "total_pieces": None,
                "total_weight_lb": None,
                "po_numbers": [],
                "pro_number": None,
                "reference_numbers": [],
                "confidence": 0.10,
                "warnings": [
                    "mock_llm: input does not resemble a bill of lading.",
                    "mock_llm: returned placeholder values.",
                ],
            }

        return LLMExtractResponse(schema=schema, json=payload, raw=None)
