# =============================================================================
# SCDO — Multi-stage Dockerfile
# Stage 1: Build frontend  |  Stage 2: Python backend + static assets
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Frontend Build
# ---------------------------------------------------------------------------
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY webapp/frontend/package.json webapp/frontend/package-lock.json ./
RUN npm ci --ignore-scripts

COPY webapp/frontend/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: Backend + Serve
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS production

# System deps for pdf processing (poppler) and OCR (tesseract)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

# Install Python deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY configs/ ./configs/
COPY webapp/backend/ ./webapp/backend/
COPY scripts/ ./scripts/

# Copy built frontend assets
COPY --from=frontend-build /app/frontend/dist ./webapp/frontend/dist

# Create required directories with correct ownership
RUN mkdir -p logs uploads output cache data && chown -R appuser:appuser /app

# Environment defaults
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MAX_UPLOAD_SIZE=52428800

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "webapp.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
