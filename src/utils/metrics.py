"""Prometheus metrics for SCDO"""
import time
import logging
from typing import Optional
from functools import wraps

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client not installed — metrics disabled")


class Metrics:
    def __init__(self):
        if not PROMETHEUS_AVAILABLE:
            return

        self.request_count = Counter(
            "scdo_requests_total",
            "Total requests",
            ["method", "endpoint", "status"]
        )
        self.request_duration = Histogram(
            "scdo_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"]
        )
        self.active_requests = Gauge(
            "scdo_active_requests",
            "Number of active requests"
        )
        self.ai_calls = Counter(
            "scdo_ai_calls_total",
            "Total AI model calls",
            ["model", "status"]
        )
        self.ai_duration = Histogram(
            "scdo_ai_call_duration_seconds",
            "AI call duration in seconds",
            ["model"]
        )
        self.cache_hits = Counter(
            "scdo_cache_hits_total",
            "Total cache hits"
        )
        self.cache_misses = Counter(
            "scdo_cache_misses_total",
            "Total cache misses"
        )

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        if not PROMETHEUS_AVAILABLE:
            return
        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_ai_call(self, model: str, status: str, duration: float):
        if not PROMETHEUS_AVAILABLE:
            return
        self.ai_calls.labels(model=model, status=status).inc()
        self.ai_duration.labels(model=model).observe(duration)

    def record_cache_hit(self):
        if PROMETHEUS_AVAILABLE:
            self.cache_hits.inc()

    def record_cache_miss(self):
        if PROMETHEUS_AVAILABLE:
            self.cache_misses.inc()

    def get_metrics(self) -> tuple:
        if not PROMETHEUS_AVAILABLE:
            return "Metrics not available", "text/plain"
        return generate_latest().decode("utf-8"), CONTENT_TYPE_LATEST


metrics = Metrics()
