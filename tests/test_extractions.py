from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

FIXTURE = Path(__file__).parent / "fixtures" / "test_bol.pdf"


@pytest.mark.integration
def test_extraction_bol_v1_pdf_happy_path(monkeypatch):
    # CI-safe: prevent real OCR/pdf2image from running (avoids needing poppler/pdfinfo)
    def fake_ocr(*args, **kwargs):
        return {"text": "", "timings_ms": {"ocr_ms": 0}}

    monkeypatch.setattr(
        "backend.core.pipeline.bol_extract.extract_text_from_file_ocr",
        fake_ocr,
    )

    with FIXTURE.open("rb") as f:
        files = {"file": ("test_bol.pdf", f, "application/pdf")}
        data = {"schema_name": "bol_v1"}

        r = client.post("/v1/extractions", data=data, files=files)

    assert r.status_code == 200, r.text

    body = r.json()
    assert body["status"] == "completed"
    assert body["job_id"] is None

    # Validate meta basics
    assert "meta" in body
    assert "request_id" in body["meta"]
    # Should be pdf_text in this test; allow pdf_text+ocr if your pipeline still marks it
    assert body["meta"]["method"] in ("pdf_text", "pdf_text+ocr")

    # Validate extracted data basics
    assert body["data"] is not None
    assert body["data"]["document_type"] == "BOL"
    assert isinstance(body["data"]["bol_number"], str)
    assert len(body["data"]["bol_number"]) > 0

    # Validation object present
    assert body["validation"]["is_valid"] is True
    assert body["validation"]["errors"] == []
