from __future__ import annotations

import asyncio
import time
from typing import Optional

from backend.core.jobs.models import JobRecord, JobStatus
from backend.core.config import JOB_TTL_SECONDS


class InMemoryJobStore:
    """
    Simple in-memory job store with TTL cleanup.

    NOTE: In production with multiple workers/instances, this won't be shared.
    """

    def __init__(self, *, ttl_seconds: int) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = asyncio.Lock()
        self._ttl_seconds = ttl_seconds
        self._last_cleanup_at = 0.0

    def _now(self) -> float:
        return time.time()

    def _should_cleanup(self) -> bool:
        # Avoid cleaning too often
        return (self._now() - self._last_cleanup_at) >= 5

    def _cleanup_expired_locked(self) -> None:
        now = self._now()
        cutoff = now - self._ttl_seconds
        expired_ids = [
            job_id
            for job_id, rec in self._jobs.items()
            if rec.updated_at < cutoff
        ]
        for job_id in expired_ids:
            self._jobs.pop(job_id, None)
        self._last_cleanup_at = now

    async def create(self, job_id: str) -> JobRecord:
        async with self._lock:
            if self._should_cleanup():
                self._cleanup_expired_locked()

            now = self._now()
            rec = JobRecord(
                job_id=job_id,
                status="queued",
                created_at=now,
                updated_at=now,
            )
            self._jobs[job_id] = rec
            return rec

    async def get(self, job_id: str) -> Optional[JobRecord]:
        async with self._lock:
            if self._should_cleanup():
                self._cleanup_expired_locked()
            return self._jobs.get(job_id)

    async def set_status(self, job_id: str, status: JobStatus) -> None:
        async with self._lock:
            rec = self._jobs.get(job_id)
            if rec:
                rec.status = status
                rec.updated_at = self._now()

    async def set_result(self, job_id: str, result: dict) -> None:
        async with self._lock:
            rec = self._jobs.get(job_id)
            if rec:
                rec.status = "completed"
                rec.result = result
                rec.error = None
                rec.updated_at = self._now()

    async def set_error(self, job_id: str, error: str) -> None:
        async with self._lock:
            rec = self._jobs.get(job_id)
            if rec:
                rec.status = "failed"
                rec.error = error
                rec.updated_at = self._now()


JOB_STORE = InMemoryJobStore(ttl_seconds=JOB_TTL_SECONDS)
