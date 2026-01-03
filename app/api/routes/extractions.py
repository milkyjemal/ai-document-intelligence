from __future__ import annotations

import os
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.core.text_extraction import extract_text_from_pdf
from app.core.pipeline.bol_extract import extract_bol_sync
from app.core.llm.factory import get_llm_client
from app.schemas.api_models import ExtractionResponse, APIValidation, APIMeta
from fastapi.responses import JSONResponse
from app.core.prompting import inject_form_fields
import logging

logger = logging.getLogger("ai-document-intelligence")
router = APIRouter(prefix="/v1", tags=["extractions"])

# Create once, reuse across requests
LLM = get_llm_client()

MAX_UPLOAD_BYTES = 10_000_000  # 10 MB


@router.post("/extractions", response_model=ExtractionResponse)
async def create_extraction(
    schema_name: str = Form("bol_v1"),
    file: UploadFile = File(...),
) -> ExtractionResponse:
    if schema_name != "bol_v1":
        raise HTTPException(status_code=400, detail="Unsupported schema")

    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF is supported for now")

    pdf_path = None
    try:
        content = await file.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="File too large")

        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            pdf_path = tmp.name

        tex = extract_text_from_pdf(pdf_path)

        text = inject_form_fields(tex["text"], tex.get("form_fields") or {})

        result = extract_bol_sync(
            schema="bol_v1",
            text=text,
            llm=LLM,
            method="pdf_text",
            page_count=tex.get("page_count"),
        )

        logger.info(
            "extraction_completed request_id=%s valid=%s method=%s pages=%s llm_ms=%s",
            result.meta.request_id,
            result.validation.is_valid,
            result.meta.method,
            result.meta.page_count,
            result.meta.timings_ms.get("llm_extract_ms"),
        )

        resp = ExtractionResponse(
            status=result.status,
            job_id=result.job_id,
            data=result.data,
            validation=APIValidation(
                is_valid=result.validation.is_valid,
                errors=result.validation.errors,
                warnings=result.validation.warnings,
            ),
            meta=APIMeta(
                request_id=result.meta.request_id,
                method=result.meta.method,
                page_count=result.meta.page_count,
                timings_ms=result.meta.timings_ms,
            ),
        )

        status_code = 200 if result.validation.is_valid else 422
        return JSONResponse(
            status_code=status_code,
            content=resp.model_dump(),
            headers={"X-Request-Id": result.meta.request_id},
        )

    finally:
        if pdf_path:
            try:
                os.unlink(pdf_path)
            except OSError:
                pass
