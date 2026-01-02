from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
import uuid
import time

from pydantic import ValidationError

from app.core.llm.base import LLMClient, LLMExtractRequest
from app.schemas.bol_v1 import BolV1


ExtractMethod = Literal["pdf_text", "ocr", "raw_text"]


@dataclass(frozen=True)
class PipelineMeta:
    request_id: str
    method: ExtractMethod
    page_count: Optional[int]
    timings_ms: Dict[str, int]


@dataclass(frozen=True)
class PipelineValidation:
    is_valid: bool
    errors: List[str]
    warnings: List[str]


@dataclass(frozen=True)
class ExtractBolResult:
    status: Literal["completed"]
    job_id: None
    data: Optional[BolV1]
    validation: PipelineValidation
    meta: PipelineMeta


def extract_bol_sync(
    *,
    schema: Literal["bol_v1"],
    text: str,
    llm: LLMClient,
    method: ExtractMethod = "raw_text",
    page_count: Optional[int] = None,
) -> ExtractBolResult:
    """
    Orchestrates:
    1) LLM extraction -> dict
    2) Pydantic validation -> BolV1
    3) warnings/errors shaping
    """
    request_id = uuid.uuid4().hex
    t0 = time.perf_counter()

    # LLM extraction timing
    t_llm0 = time.perf_counter()
    llm_resp = llm.extract_json(LLMExtractRequest(schema=schema, text=text))
    t_llm1 = time.perf_counter()

    # Validation timing
    t_val0 = time.perf_counter()
    try:
        data = BolV1.model_validate(llm_resp.json)
        errors: list[str] = []
        is_valid = True
    except ValidationError as e:
        data = None
        is_valid = False
        # keep errors readable
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
    t_val1 = time.perf_counter()

    warnings: list[str] = []
    if data is not None:
        if not data.line_items:
            warnings.append("line_items is empty")
        if data.bol_number == "UNKNOWN":
            warnings.append("bol_number is UNKNOWN")

    timings_ms = {
        "llm_extract_ms": int((t_llm1 - t_llm0) * 1000),
        "validation_ms": int((t_val1 - t_val0) * 1000),
        "total_ms": int((time.perf_counter() - t0) * 1000),
    }

    meta = PipelineMeta(
        request_id=request_id,
        method=method,
        page_count=page_count,
        timings_ms=timings_ms,
    )

    validation = PipelineValidation(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
    )

    return ExtractBolResult(status="completed", job_id=None, data=data, validation=validation, meta=meta)
