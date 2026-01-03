from dataclasses import dataclass
from typing import Dict, List, Optional, Literal

from backend.schemas.bol_v1 import BolV1
ExtractMethod = Literal["pdf_text", "ocr", "pdf_text+ocr"]

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
class PipelineResult:
    status: Literal["completed"]
    job_id: None
    data: Optional[BolV1]
    validation: PipelineValidation
    meta: PipelineMeta