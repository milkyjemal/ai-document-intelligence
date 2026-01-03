from pathlib import Path

import pytest

from backend.core.llm.mock import MockLLMClient
from backend.core.pipeline.bol_extract import extract_bol_sync


@pytest.mark.integration
def test_image_goes_directly_to_ocr(monkeypatch):
    # Fake OCR result (so CI doesn't need tesseract/poppler)
    def fake_ocr(path: str, *args, **kwargs):
        return {"text": "BILL OF LADING\nBOL NUMBER: 23", "timings_ms": {"ocr_ms": 5}}

    monkeypatch.setattr("backend.core.pipeline.bol_extract.extract_text_from_file_ocr", fake_ocr)

    img_path = Path("tests/fixtures/sample_image.png")
    assert img_path.exists(), "Add tests/fixtures/sample_image.png (any small jpg)"

    result = extract_bol_sync(schema="bol_v1", file_path=str(img_path), llm=MockLLMClient())
    
    assert result.meta.method == "ocr"
    assert result.validation.is_valid


@pytest.mark.integration
def test_pdf_falls_back_to_ocr(monkeypatch, tmp_path):
    # Force PDF text extraction to be "too short"
    def fake_pdf_text(path: str):
        return {"text": " ", "page_count": 1, "method": "pdf_text", "timings_ms": {"pdf_text_ms": 2}}

    def fake_ocr(path: str, *args, **kwargs):
        return {"text": "BILL OF LADING\nBOL NUMBER: 23", "timings_ms": {"ocr_ms": 5}}

    monkeypatch.setattr("backend.core.pipeline.bol_extract.extract_text_from_pdf", fake_pdf_text)
    monkeypatch.setattr("backend.core.pipeline.bol_extract.extract_text_from_file_ocr", fake_ocr)

    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    result = extract_bol_sync(schema="bol_v1", file_path=str(pdf_path), llm=MockLLMClient())
    assert result.meta.method == "pdf_text+ocr"
    assert result.validation.is_valid
