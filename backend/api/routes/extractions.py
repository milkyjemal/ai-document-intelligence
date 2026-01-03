from __future__ import annotations

import os
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from backend.core.llm.factory import get_llm_client
from backend.core.pipeline.bol_extract import extract_bol_sync
from backend.schemas.api_models import ExtractionResponse, APIValidation, APIMeta

router = APIRouter(prefix="/v1", tags=["extractions"])

LLM = get_llm_client()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}

MAX_UPLOAD_MB = 10


@router.post("/extractions", response_model=ExtractionResponse)
async def create_extraction(
    schema_name: str = Form("bol_v1"),
    file: UploadFile = File(...),
):
    if schema_name != "bol_v1":
        raise HTTPException(status_code=400, detail="Unsupported schema")

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, PNG, or JPG images are supported")

    tmp_path = None
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")

        if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")

        suffix = os.path.splitext(file.filename or "")[1].lower()
        if suffix not in {".pdf", ".png", ".jpg", ".jpeg"}:
            # Fallback: infer suffix from content-type
            suffix = ".pdf" if file.content_type == "application/pdf" else ".jpg"

        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        result = extract_bol_sync(
            schema="bol_v1",
            file_path=tmp_path,
            llm=LLM,
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
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
