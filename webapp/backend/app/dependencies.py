from fastapi import Request, HTTPException, Depends
from typing import Any
import os
import secrets
import hashlib
import json as json_module
from pathlib import Path
from src.utils.logging_utils import setup_logger

logger = setup_logger("scdo_api", log_file="logs/api.log")

# Settings Configuration
API_KEY = os.getenv("API_KEY", "")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 50 * 1024 * 1024))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Caching Configuration
try:
    import diskcache
    CACHE_DIR = Path(__file__).parent.parent.parent.parent / "cache" / "llm_responses"
    llm_cache = diskcache.Cache(str(CACHE_DIR), size_limit=500 * 1024 * 1024)  # 500 MB
    CACHE_TTL = 24 * 60 * 60  # 24 hours
    logger.info(f"LLM cache initialized at {CACHE_DIR}")
except ImportError:
    llm_cache = None
    CACHE_TTL = 0
    logger.warning("diskcache not installed — LLM caching disabled")

def get_cache_key(prefix: str, data: dict) -> str:
    """Generate a deterministic SHA-256 cache key from input data."""
    serialized = json_module.dumps(data, sort_keys=True, default=str)
    return f"{prefix}:{hashlib.sha256(serialized.encode()).hexdigest()}"

# Global References - These will be populated in main.py lifespan
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

# A global instance to access the components
comps = Components()

# Authentication dependency
async def verify_api_key(request: Request):
    """Verify API key from X-API-Key header or api_key query param.
    Skips auth if API_KEY env var is not set (development mode)."""
    if not API_KEY:
        return  # Auth disabled in dev mode
    
    key = request.headers.get("X-API-Key") or request.query_params.get("api_key") or ""
    if not secrets.compare_digest(key, API_KEY):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Set X-API-Key header or api_key query param."
        )

# Dependency generator to simplify dependency imports in routers
def get_components() -> Components:
    return comps
