from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel

JobStatus = Literal["queued", "running", "completed", "failed"]


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobGetResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
