from __future__ import annotations

from typing import Literal, Optional, List, Dict

from pydantic import BaseModel

from app.schemas.bol_v1 import BolV1


class APIValidation(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class APIMeta(BaseModel):
    request_id: str
    method: str
    page_count: Optional[int]
    timings_ms: Dict[str, int]


class ExtractionResponse(BaseModel):
    status: Literal["completed", "queued"]
    job_id: Optional[str] = None
    data: Optional[BolV1] = None
    validation: Optional[APIValidation] = None
    meta: APIMeta
