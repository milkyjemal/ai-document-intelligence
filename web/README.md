# AI Document Intelligence — Web UI

This folder contains the **TypeScript / Next.js** frontend for the AI Document Intelligence API.

The UI provides a polished workflow to:

- Upload a Bill of Lading (PDF, PNG, JPG, JPEG)
- Submit an extraction request
- Inspect extracted JSON, validation errors/warnings, and request metadata

## Overview

This web interface provides a user-friendly way to interact with the AI Document Intelligence backend. It allows users to upload PDF or image documents, initiate extraction processes, and view the structured JSON output along with any validation feedback.

Image uploads are processed on the backend using OCR before the extraction step.

Supported inputs:

- **PDF** (`.pdf`)
- **Images** (`.png`, `.jpg`, `.jpeg`)

Take a look at the interface screenshot below:

![AI Document Intelligence Web UI](public/assets/ai_doc_intelligence.png)

## Architecture

The frontend talks to the backend through **Next.js API routes** (a server-side proxy). This avoids browser CORS issues and keeps backend details configurable via environment variables.

- **Proxy health:** `GET /api/health` → `${BACKEND_URL}/health`
- **Proxy extraction:** `POST /api/extractions` → `${BACKEND_URL}/v1/extractions` (multipart form upload)

## Prerequisites

- Node.js (recommended: current LTS)
- A running backend API (FastAPI)

Note: OCR dependencies (Tesseract/Poppler) are required on the backend host/container, not in this Next.js app.

## Configuration

Create `web/.env.local`:

```bash
BACKEND_URL=http://127.0.0.1:8000
```

Or copy the example:

```bash
cp .env.local.example .env.local
```

## Run locally

Install dependencies:

```bash
npm install
```

Start the dev server:

```bash
npm run dev
```

Open http://localhost:3000

## Scripts

```bash
npm run dev    # start dev server
npm run build  # production build
npm run start  # run production server
npm run lint   # lint
```

## Project layout

```text
src/
  app/                # Next.js App Router pages + API proxy routes
  components/         # UI components
  lib/                # fetch helpers + shared types
```

## Troubleshooting

- **Backend unreachable**
  - Verify the backend is running and `BACKEND_URL` is correct.
  - If the UI shows “Backend unreachable”, open `http://localhost:3000/api/health` to see the proxy response.

- **Uploads fail / 413 (Payload Too Large)**
  - The backend may enforce a maximum file size.
  - Try a smaller file or adjust backend limits if needed.
