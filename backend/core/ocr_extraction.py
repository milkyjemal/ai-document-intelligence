from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, List, Optional

import pytesseract
from PIL import Image

# pdf2image is only used for PDFs
from pdf2image import convert_from_path


IMAGE_EXTS = {".png", ".jpg", ".jpeg"}


def extract_text_from_file_ocr(
    path: str,
    *,
    dpi: int = 300,
    pages: Optional[List[int]] = None,  # 1-based page numbers (PDF only)
) -> Dict[str, object]:
    """
    OCR for either:
      - image files (.png/.jpg/.jpeg) => OCR directly
      - PDFs => convert pages to images then OCR

    pages:
      - Only applies to PDFs (1-based page indices)
      - If None, OCR all pages (not recommended for MVP; use [1] or [1,2])
    """
    t0 = time.perf_counter()
    p = Path(path)
    ext = p.suffix.lower()

    if ext in IMAGE_EXTS:
        # Image OCR
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return {
            "text": text,
            "method": "ocr",
            "page_texts": [text],
            "timings_ms": {"ocr_ms": int((time.perf_counter() - t0) * 1000)},
        }

    # PDF OCR
    first_page = min(pages) if pages else None
    last_page = max(pages) if pages else None

    images = convert_from_path(
        path,
        dpi=dpi,
        first_page=first_page,
        last_page=last_page,
    )

    page_texts: List[str] = []
    for img in images:
        page_texts.append(pytesseract.image_to_string(img))

    full_text = "\n\n".join(page_texts)

    return {
        "text": full_text,
        "method": "ocr",
        "page_texts": page_texts,
        "timings_ms": {"ocr_ms": int((time.perf_counter() - t0) * 1000)},
    }
