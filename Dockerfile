FROM python:3.12-slim

# Prevent Python from writing pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (PyMuPDF sometimes needs these; keep minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY pyproject.toml poetry.lock* requirements.txt* /app/

# If you use requirements.txt:
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# If you don't have requirements.txt yet, do a simple editable install style:
# We'll install runtime deps directly (safe for MVP).
RUN pip install --no-cache-dir fastapi uvicorn python-multipart pymupdf openai python-dotenv

# Copy application code
COPY app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
