import json
from typing import Any, Dict

from openai import OpenAI
from backend.core.config import OPENAI_API_KEY

from backend.core.llm.base import (
    LLMClient,
    LLMExtractRequest,
    LLMExtractResponse,
)


class OpenAILLMClient(LLMClient):
    """
    OpenAI implementation of LLMClient.
    Uses strict JSON output and schema-guided extraction.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self._client = OpenAI(api_key=OPENAI_API_KEY)
        self._model = model

    def extract_json(self, request: LLMExtractRequest) -> LLMExtractResponse:
        if request.schema != "bol_v1":
            raise ValueError(f"Unsupported schema: {request.schema}")

        system_prompt = (
            "You are an expert logistics document parser.\n"
            "Extract structured data from a Bill of Lading.\n"
            "Return ONLY valid JSON. Do not include explanations."
        )

        schema_prompt = """
        Extract a Bill of Lading into the following JSON structure:

        {
        "document_type": "BOL",
        "carrier_name": string | null,
        "bol_number": string,
        "shipment_date": "YYYY-MM-DD" | null,
        "shipper": { "name": string, "address": string | null, "phone": string | null } | null,
        "consignee": { "name": string, "address": string | null, "phone": string | null } | null,
        "origin": { "city": string | null, "state": string | null, "postal_code": string | null, "country": string | null } | null,
        "destination": { "city": string | null, "state": string | null, "postal_code": string | null, "country": string | null } | null,
        "line_items": [
            {
            "description": string,
            "pieces": number | null,
            "weight_lb": number | null,
            "nmfc": string | null,
            "freight_class": string | null
            }
        ],
        "total_pieces": number | null,
        "total_weight_lb": number | null,
        "po_numbers": string[],
        "pro_number": string | null,
        "reference_numbers": string[],
        "confidence": number,
        "warnings": string[]
        }

        Rules:
        - Return ONLY valid JSON
        - Use null when unknown
        - confidence must be between 0 and 1
        - If uncertain, lower confidence and add a warning
        """

        user_prompt = (
            schema_prompt
            + "\n\nDOCUMENT TEXT:\n----------------\n"
            + request.text
        )

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )

        raw_content = response.choices[0].message.content

        try:
            parsed: Dict[str, Any] = json.loads(raw_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"OpenAI did not return valid JSON: {raw_content}") from e

        return LLMExtractResponse(
            schema=request.schema,
            json=parsed,
            raw=raw_content,
        )
