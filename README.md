AI Document Intelligence – Bill of Lading Extraction API

A production-grade AI document extraction service that converts logistics documents (Bill of Lading PDFs) into validated, structured JSON using LLMs — with a clean pipeline, testability, and CI.

Built with FastAPI, Pydantic, OpenAI (optional), and Docker.

✨ Features

📄 PDF Bill of Lading extraction

🧠 LLM-based structured parsing (OpenAI or mock)

🧾 Form-field + text extraction (AcroForm-aware)

✅ Strict validation with Pydantic

⚠️ Warnings vs errors (enterprise-style)

🔁 Mock LLM toggle for tests / CI (no API calls)

🐳 Dockerized (slim image)

🧪 Pytest integration tests

🤖 GitHub Actions CI

🏗️ Architecture Overview
Client
  │
  ▼
FastAPI Endpoint
  │
  ▼
Text Extraction
(PDF text + form fields)
  │
  ▼
Prompt Assembly
  │
  ▼
LLM Client
(Mock or OpenAI)
  │
  ▼
Pydantic Validation
  │
  ▼
Structured JSON Response


Design principle:
The LLM is an interchangeable adapter, not the core logic.

📦 Tech Stack

API: FastAPI

Validation: Pydantic v2

PDF Parsing: PyMuPDF

LLM: OpenAI (optional) / MockLLM

Tests: pytest

CI: GitHub Actions

Container: Docker (slim image)

🚀 Running Locally
Setup environment
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-multipart pymupdf pydantic python-dotenv openai


Create .env:

OPENAI_API_KEY=sk-...
USE_MOCK_LLM=0

Run the API
uvicorn app.main:app --reload


Swagger UI → http://127.0.0.1:8000/docs

Health check → http://127.0.0.1:8000/health

📤 Example Request (curl)
curl -X POST "http://127.0.0.1:8000/v1/extractions" \
  -F "schema_name=bol_v1" \
  -F "file=@samples/TFF-BOL-Form.pdf;type=application/pdf"

📥 Example Response (trimmed)
{
  "status": "completed",
  "job_id": null,
  "data": {
    "document_type": "BOL",
    "bol_number": "23",
    "shipper": { "name": "ACME Inc." },
    "consignee": { "name": "Receiver LLC" },
    "origin": { "city": "Los Angeles", "state": "CA" },
    "destination": { "city": "Atlanta", "state": "GA" },
    "line_items": [
      {
        "description": "General Freight",
        "pieces": 1,
        "weight_lb": 100,
        "freight_class": "50"
      }
    ],
    "confidence": 0.9
  },
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  },
  "meta": {
    "request_id": "c5a6ce30...",
    "method": "pdf_text",
    "page_count": 2
  }
}

🧪 Running Tests

Tests do not call OpenAI (Mock LLM enforced).

USE_MOCK_LLM=1 python -m pytest -q

🐳 Docker
Build image
docker build -t ai-document-intelligence .

Run container
docker run -p 8000:8000 --env-file .env ai-document-intelligence

🔁 Mock vs Real LLM

Controlled via environment variable:

USE_MOCK_LLM=1   # tests / CI
USE_MOCK_LLM=0   # real OpenAI


This ensures:

CI is fast and free

No flaky AI tests

No API cost in tests

Same codebase for prod & CI

📁 Project Structure
app/
  api/            # FastAPI routes
  core/           # pipeline, LLM, extraction logic
  schemas/        # Pydantic models
tests/
  fixtures/       # sample PDFs
.github/
  workflows/ci.yml
Dockerfile
README.md

🧠 Why This Project Matters

This project demonstrates:

Real-world AI engineering patterns

Clean separation of concerns

LLM reliability through validation

Deterministic testing strategy

Production-ready API design

This is intentionally not a toy project.

🔮 Future Improvements

Async job queue

Webhooks

Multiple document schemas

Rate limiting & authentication

OCR fallback pipeline

Frontend playground

👤 Author

Milky Omer
Senior Backend Engineer | AI-focused Systems