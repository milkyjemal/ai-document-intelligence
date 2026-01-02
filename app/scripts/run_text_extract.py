from app.core.text_extraction import extract_text_from_pdf
from pathlib import Path

if __name__ == "__main__":
    pdf_path = Path("samples/TFF-BOL-Form.pdf")
    result = extract_text_from_pdf(pdf_path)
    print(result)