from __future__ import annotations

import os
import uuid
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse

from backend.core.jobs.store import JOB_STORE
from backend.core.llm.factory import get_llm_client
from backend.core.pipeline.bol_extract import extract_bol_sync
from backend.schemas.api_models import ExtractionResponse, APIValidation, APIMeta
from backend.schemas.job_models import JobCreateResponse, JobGetResponse

router = APIRouter(prefix="/v1", tags=["extractions"])

LLM = get_llm_client()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}

MAX_UPLOAD_MB = 10


def _safe_suffix(filename: str | None, content_type: str) -> str:
    suffix = os.path.splitext(filename or "")[1].lower()
    if suffix in {".pdf", ".png", ".jpg", ".jpeg"}:
        return suffix
    return ".pdf" if content_type == "application/pdf" else ".jpg"


def _to_extraction_response(result) -> ExtractionResponse:
    return ExtractionResponse(
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


async def _run_job(job_id: str, schema: str, file_path: str) -> None:
    await JOB_STORE.set_status(job_id, "running")
    try:
        result = extract_bol_sync(schema=schema, file_path=file_path, llm=LLM)
        resp = _to_extraction_response(result)
        await JOB_STORE.set_result(job_id, resp.model_dump())
    except Exception as e:
        await JOB_STORE.set_error(job_id, str(e))
    finally:
        try:
            os.unlink(file_path)
        except OSError:
            pass


@router.post("/extractions", response_model=ExtractionResponse)
async def create_extraction(
    background_tasks: BackgroundTasks,
    async_mode: bool = Query(False, description="If true, returns 202 + job_id and runs extraction in background"),
    schema_name: str = Form("bol_v1"),
    file: UploadFile = File(...),
):
    if schema_name != "bol_v1":
        raise HTTPException(status_code=400, detail="Unsupported schema")

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, PNG, or JPG images are supported")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    tmp_path = None
    try:
        suffix = _safe_suffix(file.filename, file.content_type)
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # ---- ASYNC MODE ----
        if async_mode:
            job_id = uuid.uuid4().hex
            await JOB_STORE.create(job_id)
            background_tasks.add_task(_run_job, job_id, "bol_v1", tmp_path)

            return JSONResponse(
                status_code=202,
                content=JobCreateResponse(job_id=job_id, status="queued").model_dump(),
                headers={"X-Job-Id": job_id},
            )

        # ---- SYNC MODE ----
        result = extract_bol_sync(schema="bol_v1", file_path=tmp_path, llm=LLM)
        resp = _to_extraction_response(result)

        status_code = 200 if result.validation.is_valid else 422
        return JSONResponse(
            status_code=status_code,
            content=resp.model_dump(),
            headers={"X-Request-Id": result.meta.request_id},
        )

    finally:
        # In async mode, _run_job cleans up the file.
        if tmp_path and not async_mode:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


@router.get("/extractions/{job_id}", response_model=JobGetResponse)
async def get_extraction_job(job_id: str):
    rec = await JOB_STORE.get(job_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobGetResponse(
        job_id=rec.job_id,
        status=rec.status,
        result=rec.result,
        error=rec.error,
    )
