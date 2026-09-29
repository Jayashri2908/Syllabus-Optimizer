from fastapi import Request, HTTPException, Depends
from typing import Any, Optional
import os
import secrets
import hashlib
import json as json_module
import time
from pathlib import Path
from src.utils.logging_utils import setup_logger

logger = setup_logger("scdo_api", log_file="logs/api.log")

PROJECT_ROOT = Path(__file__).resolve().parents[4]

ENV = os.getenv("ENV", "development").lower()
IS_PRODUCTION = ENV == "production"

API_KEY = os.getenv("API_KEY", "")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024)))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8000").split(",")

RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

try:
    import diskcache
    CACHE_DIR = PROJECT_ROOT / "cache" / "llm_responses"
    llm_cache = diskcache.Cache(str(CACHE_DIR), size_limit=500 * 1024 * 1024)
    CACHE_TTL = 24 * 60 * 60
    logger.info(f"LLM cache initialized at {CACHE_DIR}")
except ImportError:
    llm_cache = None
    CACHE_TTL = 0
    logger.warning("diskcache not installed — LLM caching enabled")

_rate_limit_store: dict[str, list[float]] = {}


def get_cache_key(prefix: str, data: dict) -> str:
    serialized = json_module.dumps(data, sort_keys=True, default=str)
    return f"{prefix}:{hashlib.sha256(serialized.encode()).hexdigest()}"


class Components:
    parser: Any = None
    gap_analyzer: Any = None
    outcome_extractor: Any = None
    bloom_mapper: Any = None
    content_optimizer: Any = None
    syllabus_generator: Any = None
    co_po_mapper: Any = None
    pdf_exporter: Any = None
    local_storage: Any = None
    objectives_optimizer: Any = None
    reference_suggester: Any = None


comps = Components()


async def verify_api_key(request: Request):
    if not IS_PRODUCTION and not API_KEY:
        return

    if not API_KEY:
        logger.error("API_KEY not set in production mode")
        raise HTTPException(status_code=500, detail="Server configuration error")

    key = request.headers.get("X-API-Key") or request.query_params.get("api_key") or ""
    if not secrets.compare_digest(key, API_KEY):
        logger.warning(f"Invalid API key attempt from {request.client.host if request.client else 'unknown'}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Set X-API-Key header or api_key query param."
        )


async def rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    if client_ip not in _rate_limit_store:
        _rate_limit_store[client_ip] = []

    _rate_limit_store[client_ip] = [
        t for t in _rate_limit_store[client_ip]
        if now - t < RATE_LIMIT_WINDOW
    ]

    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds."
        )

    _rate_limit_store[client_ip].append(now)


def sanitize_filename(filename: str) -> str:
    import re
    safe = re.sub(r'[^\w\s\-.]', '_', filename)
    safe = safe.strip('.')
    if not safe or safe.startswith('.') or '..' in safe:
        raise HTTPException(status_code=400, detail="Invalid filename")
    return safe


def validate_file_content(content: bytes, max_size: int = MAX_UPLOAD_SIZE) -> None:
    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {max_size // (1024*1024)} MB"
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")


def get_components() -> Components:
    return comps
