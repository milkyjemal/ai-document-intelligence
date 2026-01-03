FROM python:3.12-slim

# Prevent Python from writing pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ---- System dependencies (minimal) ----
# PyMuPDF needs some system libs; keep only what we need
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libgl1 \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# ---- Install Python dependencies ----
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    pymupdf \
    pydantic \
    python-dotenv \
    openai \
    pytesseract \
    pdf2image \
    pillow

# ---- Copy application code only ----
COPY app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
