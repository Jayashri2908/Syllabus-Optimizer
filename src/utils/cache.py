"""Unified caching layer for SCDO (Redis + diskcache fallback)"""
import os
import json
import hashlib
import logging
from typing import Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import diskcache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False


class CacheManager:
    def __init__(self):
        self._redis: Optional[Any] = None
        self._disk: Optional[Any] = None
        self._backend = "none"
        self._initialize()

    def _initialize(self):
        redis_url = os.getenv("REDIS_URL", "")
        if redis_url and REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                self._backend = "redis"
                logger.info(f"Redis cache connected: {redis_url}")
                return
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")

        cache_dir = Path(os.getenv("CACHE_DIR", "cache/llm_responses"))
        if DISKCACHE_AVAILABLE:
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                self._disk = diskcache.Cache(str(cache_dir), size_limit=500*1024*1024)
                self._backend = "disk"
                logger.info(f"Disk cache initialized at {cache_dir}")
            except Exception as e:
                logger.warning(f"Disk cache init failed: {e}")

    def get(self, key: str) -> Optional[Any]:
        try:
            if self._backend == "redis" and self._redis:
                value = self._redis.get(key)
                return json.loads(value) if value else None
            elif self._backend == "disk" and self._disk:
                return self._disk.get(key)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        return None

    def set(self, key: str, value: Any, expire: int = 86400) -> bool:
        try:
            if self._backend == "redis" and self._redis:
                self._redis.setex(key, expire, json.dumps(value, default=str))
                return True
            elif self._backend == "disk" and self._disk:
                self._disk.set(key, value, expire=expire)
                return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
        return False

    def delete(self, key: str) -> bool:
        try:
            if self._backend == "redis" and self._redis:
                self._redis.delete(key)
                return True
            elif self._backend == "disk" and self._disk:
                self._disk.delete(key)
                return True
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
        return False

    def clear(self) -> bool:
        try:
            if self._backend == "redis" and self._redis:
                self._redis.flushdb()
                return True
            elif self._backend == "disk" and self._disk:
                self._disk.clear()
                return True
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")
        return False

    @staticmethod
    def make_key(prefix: str, data: Any) -> str:
        serialized = json.dumps(data, sort_keys=True, default=str)
        return f"{prefix}:{hashlib.sha256(serialized.encode()).hexdigest()}"

    @property
    def backend(self) -> str:
        return self._backend


cache_manager = CacheManager()
