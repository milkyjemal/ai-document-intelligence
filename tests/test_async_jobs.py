from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
FIXTURE = Path(__file__).parent / "fixtures" / "test_bol.pdf"


@pytest.mark.integration
def test_async_job_happy_path(monkeypatch):
    # Avoid real OCR/pdf2image during this test
    def fake_ocr(*args, **kwargs):
        return {"text": "", "timings_ms": {"ocr_ms": 0}}

    monkeypatch.setattr("backend.core.pipeline.bol_extract.extract_text_from_file_ocr", fake_ocr)

    with FIXTURE.open("rb") as f:
        files = {"file": ("test_bol.pdf", f, "application/pdf")}
        data = {"schema_name": "bol_v1"}

        r = client.post("/v1/extractions?async_mode=true", data=data, files=files)

    assert r.status_code == 202, r.text
    body = r.json()
    assert "job_id" in body
    job_id = body["job_id"]
    assert body["status"] in ("queued", "running", "completed")

    # Poll once or twice; BackgroundTasks usually completes quickly in TestClient
    r2 = client.get(f"/v1/extractions/{job_id}")
    assert r2.status_code == 200, r2.text
    body2 = r2.json()
    assert body2["job_id"] == job_id
    assert body2["status"] in ("running", "completed", "failed")

    if body2["status"] == "failed":
        raise AssertionError(f"Job failed: {body2.get('error')}")

    if body2["status"] == "completed":
        assert body2["result"] is not None
        assert body2["result"]["status"] == "completed"
