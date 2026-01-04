from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional

JobStatus = Literal["queued", "running", "completed", "failed"]


@dataclass
class JobRecord:
    job_id: str
    status: JobStatus
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = 0.0
    updated_at: float = 0.0
