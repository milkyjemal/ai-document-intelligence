from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FIXTURE = Path(__file__).parent / "fixtures" / "test_bol.pdf"


@pytest.mark.integration
def test_extraction_bol_v1_pdf_happy_path():
    with FIXTURE.open("rb") as f:
        files = {"file": ("filled_bol.pdf", f, "application/pdf")}
        data = {"schema_name": "bol_v1"}

        r = client.post("/v1/extractions", data=data, files=files)

    # Accept either 200 or 422 depending on how strict your schema/prompt is,
    # but for a filled fixture we EXPECT 200 in a good system.
    assert r.status_code == 200, r.text

    body = r.json()
    assert body["status"] == "completed"
    assert body["job_id"] is None

    # Validate meta basics
    assert "meta" in body
    assert "request_id" in body["meta"]
    assert body["meta"]["method"] in ("pdf_text", "ocr", "raw_text")

    # Validate extracted data basics
    assert body["data"] is not None
    assert body["data"]["document_type"] == "BOL"
    assert isinstance(body["data"]["bol_number"], str)
    assert len(body["data"]["bol_number"]) > 0

    # Validation object present
    assert body["validation"]["is_valid"] is True
    assert body["validation"]["errors"] == []
