"""Background task queue for SCDO"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logger.warning("celery not installed — background tasks disabled")

celery_app: Optional[Celery] = None

if CELERY_AVAILABLE:
    broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    celery_app = Celery(
        "scdo_tasks",
        broker=broker_url,
        backend=result_backend,
    )

    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=3600,
        worker_prefetch_multiplier=1,
    )
