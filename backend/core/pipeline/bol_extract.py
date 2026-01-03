from __future__ import annotations

import time
import uuid
from pathlib import Path

from backend.core.llm.base import LLMClient, LLMExtractRequest
from backend.core.ocr_extraction import extract_text_from_file_ocr
from backend.core.prompting import inject_form_fields
from backend.core.text_extraction import extract_text_from_pdf

from backend.schemas.bol_v1 import BolV1
from backend.core.pipeline.models import PipelineMeta, PipelineValidation, PipelineResult


IMAGE_EXTS = {".png", ".jpg", ".jpeg"}


def _is_image(path: str) -> bool:
    return Path(path).suffix.lower() in IMAGE_EXTS


def extract_bol_sync(
    *,
    schema: str,
    file_path: str,
    llm: LLMClient,
) -> PipelineResult:
    """
    Pipeline owns extraction method decision:
      - Image => OCR only
      - PDF => try pdf_text (+ form fields) first, then OCR fallback if needed
    """
    request_id = uuid.uuid4().hex
    t0_total = time.perf_counter()

    method = "unknown"
    page_count = None
    timings_ms: dict[str, int] = {}

    # 1) Extract text (PDF text first OR OCR)
    if _is_image(file_path):
        # Image => OCR
        ocr = extract_text_from_file_ocr(file_path)
        text = ocr["text"]
        method = "ocr"
        timings_ms.update(ocr.get("timings_ms", {}))

    else:
        # PDF => try text extraction first
        tex = extract_text_from_pdf(file_path)
        page_count = tex.get("page_count")
        timings_ms.update(tex.get("timings_ms", {}))
        method = tex.get("method", "pdf_text")

        text = inject_form_fields(tex.get("text", ""), tex.get("form_fields") or {})

        # OCR fallback heuristic (MVP)
        # If text is too short, OCR the first page and prepend it.
        if len(text.strip()) < 300:
            ocr = extract_text_from_file_ocr(file_path, pages=[1])
            text = ocr["text"] + "\n\n" + text
            method = "pdf_text+ocr"
            timings_ms.update(ocr.get("timings_ms", {}))

    # 2) LLM extract
    t0_llm = time.perf_counter()
    llm_resp = llm.extract_json(LLMExtractRequest(schema=schema, text=text))
    timings_ms["llm_extract_ms"] = int((time.perf_counter() - t0_llm) * 1000)

    # 3) Validate
    t0_val = time.perf_counter()
    validation = PipelineValidation(is_valid=True, errors=[], warnings=[])
    data = None

    try:
        data = BolV1.model_validate(llm_resp.json)
    except Exception as e:
        validation.is_valid = False
        validation.errors.append(str(e))

    timings_ms["validation_ms"] = int((time.perf_counter() - t0_val) * 1000)
    timings_ms["total_ms"] = int((time.perf_counter() - t0_total) * 1000)

    meta = PipelineMeta(
        request_id=request_id,
        method=method,
        page_count=page_count,
        timings_ms=timings_ms,
    )

    return PipelineResult(
        status="completed",
        job_id=None,
        data=data if validation.is_valid else None,
        validation=validation,
        meta=meta,
    )
