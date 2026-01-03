import fitz  # PyMuPDF
from pathlib import Path

PDF_PATH = Path("samples/TFF-BOL-Form.pdf")

def main() -> None:
    doc = fitz.open(PDF_PATH)
    print("Number of pages:", len(doc))

    first_page_text = doc[0].get_text()
    print("\n--- First page text (first 800 chars) ---\n")
    print(first_page_text[:800])

if __name__ == "__main__":
    main()
