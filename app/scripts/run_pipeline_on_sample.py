from __future__ import annotations

from pathlib import Path

# from app.core.llm.mock import MockLLMClient
from app.core.llm.openai_client import OpenAILLMClient
from app.core.pipeline.bol_extract import extract_bol_sync
from app.core.text_extraction import extract_text_from_pdf


PDF_PATH = Path("samples/TFF-BOL-Form.pdf")


def main() -> None:
    # 1) Extract text from PDF
    tex = extract_text_from_pdf(str(PDF_PATH))
    form_fields = tex.get("form_fields") or {}
    text = tex.get("text")
    page_count = tex.get("page_count")
    if form_fields:
        # Only include fields that are not "Off" to reduce noise
        interesting = {k: v for k, v in form_fields.items() if v != "Off"}

        if interesting:
            fields_block = "\n".join([f"- {k}: {v}" for k, v in sorted(interesting.items())])
            text = "FORM FIELDS:\n" + fields_block + "\n\n" + text

    # 2) Mock LLM
    # llm = MockLLMClient()
    llm = OpenAILLMClient()
    # 3) Run pipeline
    result = extract_bol_sync(
        schema="bol_v1",
        text=text,
        llm=llm,
        method="pdf_text",
        page_count=page_count,
    )

    # 4) Print results
    print("\n=== PIPELINE RESULT ===")
    print("status:", result.status)
    print("job_id:", result.job_id)
    print("\nvalidation:", result.validation)
    print("\nmeta:", result.meta)

    if result.data is None:
        print("\ndata: None")
    else:
        print("\n=== EXTRACTED DATA ===")
        print(result.data.model_dump())


if __name__ == "__main__":
    main()
