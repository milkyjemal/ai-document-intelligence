# AI Document Intelligence

AI document extraction service that converts logistics documents (Bill of Lading PDFs and images) into validated, structured JSON using LLMs.

Built with FastAPI, Pydantic, OpenAI (optional), and Docker.

This repository also includes a **TypeScript / Next.js frontend** (in `web/`) that provides a polished UI for uploading PDFs/images and inspecting extraction output.

Read more: [`web/README.md`](web/README.md)

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Run Locally](#run-locally)
- [Frontend (Next.js)](#frontend-nextjs)
- [API Usage](#api-usage)
- [Testing](#testing)
- [Docker](#docker)
- [Mock vs Real LLM](#mock-vs-real-llm)
- [Project Structure](#project-structure)
- [Why This Project Matters](#why-this-project-matters)
- [Future Improvements](#future-improvements)
- [Author](#author)

## ✨ Features

- 📄 **PDF Bill of Lading extraction**
- 🖼️ **Image upload support** (PNG/JPG/JPEG)
- 🧠 **LLM-based structured parsing** (OpenAI or mock)
- 🧾 **Form-field + text extraction** (AcroForm-aware)
- 🔎 **OCR extraction** for images and low-text PDFs (fallback)
- ✅ **Strict validation** (Pydantic)
- ⚠️ **Warnings vs errors** (enterprise-style)
- 🔁 **Mock LLM toggle for tests / CI** (no API calls)
- 🐳 **Dockerized** (slim image)
- 🧪 **Pytest integration tests** (comprehensive suite with mock LLM)
- 🤖 **GitHub Actions CI**

## Architecture

```
Client
  |
  v
FastAPI endpoint
  |
  v
Text extraction (PDF text + form fields)
  |
  v
OCR (images or PDF fallback)
  |
  v
Prompt assembly
  |
  v
LLM client (Mock or OpenAI)
  |
  v
Pydantic validation
  |
  v
Structured JSON response
```

Design principle: the LLM is an interchangeable adapter, not the core logic.

## Tech Stack

- **API:** FastAPI
- **Frontend:** Next.js (TypeScript, App Router) + Tailwind CSS
- **Validation:** Pydantic v2
- **PDF parsing:** PyMuPDF
- **OCR:** Tesseract (via `pytesseract`), `pdf2image`, Pillow
- **LLM:** OpenAI (optional) / MockLLM
- **Tests:** pytest
- **CI:** GitHub Actions
- **Container:** Docker (slim image)

## Run Locally

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-multipart pymupdf pydantic python-dotenv openai pillow pytesseract pdf2image
```

OCR dependencies (required for image uploads / OCR fallback):

- **macOS (Homebrew):** `brew install tesseract poppler`
- **Debian/Ubuntu:** `apt-get install tesseract-ocr poppler-utils`

### Configuration

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-...
USE_MOCK_LLM=0
```

### Run the API

```bash
uvicorn backend.main:app --reload
```

- **Swagger UI:** http://127.0.0.1:8000/docs
- **Health check:** http://127.0.0.1:8000/health

## Frontend (Next.js)

The UI lives in the `web/` folder and talks to the FastAPI backend through Next.js API routes (proxy) to avoid browser CORS issues.

### Configure

Create `web/.env.local`:

```bash
BACKEND_URL=http://127.0.0.1:8000
```

You can also copy the example:

```bash
cp web/.env.local.example web/.env.local
```

### Run the frontend

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000

## API Usage

### Synchronous extraction (default)

```bash
curl -X POST "http://127.0.0.1:8000/v1/extractions" \
  -F "schema_name=bol_v1" \
  -F "file=@samples/TFF-BOL-Form.pdf;type=application/pdf"
```

Image uploads are also supported:

```bash
curl -X POST "http://127.0.0.1:8000/v1/extractions" \
  -F "schema_name=bol_v1" \
  -F "file=@samples/sample_bol.jpg;type=image/jpeg"
```

### Asynchronous extraction (returns job id)

Pass `async_mode=true` to return `202 Accepted` and a `job_id`.

```bash
curl -X POST "http://127.0.0.1:8000/v1/extractions?async_mode=true" \
  -F "schema_name=bol_v1" \
  -F "file=@samples/TFF-BOL-Form.pdf;type=application/pdf"
```

Example 202 response:

```json
{
  "job_id": "0f8e7d...",
  "status": "queued"
}
```

### Get async job status

```bash
curl -X GET "http://127.0.0.1:8000/v1/extractions/<job_id>"
```

When the job is complete, the response includes the full extraction result:

```json
{
  "job_id": "0f8e7d...",
  "status": "completed",
  "result": { "status": "completed", "job_id": null, "data": {}, "validation": {}, "meta": {} },
  "error": null
}
```

### Example Response (trimmed)

```json
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
```

Notes:

- `meta.method` may be `pdf_text`, `ocr`, or `pdf_text+ocr` depending on the input and fallback behavior.

## Testing

Tests do not call OpenAI (mock LLM enforced).

```bash
USE_MOCK_LLM=1 python -m pytest -q
```

## Docker

### Build image

```bash
docker build -t ai-document-intelligence .
```

### Run container

```bash
docker run -p 8000:8000 --env-file .env ai-document-intelligence
```

The Docker image includes OCR runtime dependencies (Tesseract + Poppler) to support image uploads and PDF OCR fallback.

## Mock vs Real LLM

Controlled via environment variable:

```bash
USE_MOCK_LLM=1   # tests / CI
USE_MOCK_LLM=0   # real OpenAI
```

This ensures:

- **CI is fast and free**
- **No flaky AI tests**
- **No API cost in tests**
- **Same codebase for prod & CI**

## Project Structure

```text
backend/
  api/            # FastAPI routes
  core/           # pipeline, LLM, extraction logic
  schemas/        # Pydantic models
tests/
  fixtures/       # sample PDFs
web/              # Next.js frontend (TypeScript)
.github/
  workflows/ci.yml
Dockerfile
README.md
```

## Why This Project Matters

This project demonstrates:

- Real-world AI engineering patterns
- Clean separation of concerns
- LLM reliability through validation
- Deterministic testing strategy
- Production-ready API design

This is intentionally not a toy project.

## Future Improvements

- Persistent async job queue (Redis / SQS) + worker pool
- Webhooks
- Multiple document schemas
- Rate limiting & authentication
- Improved OCR fallback heuristics (multi-page OCR, better detection)
- Frontend playground

## Author

Milky Omer
Senior Backend Engineer | AI-focused Systems