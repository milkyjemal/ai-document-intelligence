# AI Document Intelligence

AI document extraction service that converts logistics documents (Bill of Lading PDFs) into validated, structured JSON using LLMs.

Built with FastAPI, Pydantic, OpenAI (optional), and Docker.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Run Locally](#run-locally)
- [API Usage](#api-usage)
- [Testing](#testing)
- [Docker](#docker)
- [Mock vs Real LLM](#mock-vs-real-llm)
- [Project Structure](#project-structure)
- [Why This Project Matters](#why-this-project-matters)
- [Future Improvements](#future-improvements)
- [Author](#author)

## Features

- **PDF Bill of Lading extraction**
- **LLM-based structured parsing** (OpenAI or mock)
- **Form-field + text extraction** (AcroForm-aware)
- **Strict validation** with Pydantic
- **Warnings vs errors** (enterprise-style)
- **Mock LLM toggle** for tests / CI (no API calls)
- **Dockerized** (slim image)
- **Pytest integration tests**
- **GitHub Actions CI**

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
- **Validation:** Pydantic v2
- **PDF parsing:** PyMuPDF
- **LLM:** OpenAI (optional) / MockLLM
- **Tests:** pytest
- **CI:** GitHub Actions
- **Container:** Docker (slim image)

## Run Locally

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-multipart pymupdf pydantic python-dotenv openai
```

### Configuration

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-...
USE_MOCK_LLM=0
```

### Run the API

```bash
uvicorn app.main:app --reload
```

- **Swagger UI:** http://127.0.0.1:8000/docs
- **Health check:** http://127.0.0.1:8000/health

## API Usage

### Example Request (curl)

```bash
curl -X POST "http://127.0.0.1:8000/v1/extractions" \
  -F "schema_name=bol_v1" \
  -F "file=@samples/TFF-BOL-Form.pdf;type=application/pdf"
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

- Async job queue
- Webhooks
- Multiple document schemas
- Rate limiting & authentication
- OCR fallback pipeline
- Frontend playground

## Author

Milky Omer
Senior Backend Engineer | AI-focused Systems