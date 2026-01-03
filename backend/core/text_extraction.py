from time import perf_counter
from pathlib import Path
from typing import Dict, List

from fitz import open


def extract_text_from_pdf(path: str) -> Dict[str, object]:
    pdf_path = Path(path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    t0 = perf_counter()

    doc = open(pdf_path)
    page_texts: List[str] = []
    form_fields: Dict[str, str] = {}

    for page in doc:
        # Normal text extraction
        page_texts.append(page.get_text())

        # Form fields (AcroForm widgets)
        for w in page.widgets() or []:
            if w.field_name and w.field_value is not None:
                value = str(w.field_value).strip()
                # Keep only meaningful values (avoid empty)
                if value:
                    form_fields[w.field_name] = value

    full_text = "\n\n".join(page_texts)

    return {
        "text": full_text,
        "page_count": len(doc),
        "method": "pdf_text",
        "page_texts": page_texts,
        "form_fields": form_fields,
        "timings_ms": {"text_extraction_ms": int((perf_counter() - t0) * 1000)},
    }
