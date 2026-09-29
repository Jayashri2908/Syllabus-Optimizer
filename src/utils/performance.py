"""Performance optimization utilities for SCDO"""
import time
import logging
import functools
from typing import Callable, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def timed(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} completed in {duration:.3f}s")
        return result
    return wrapper


@contextmanager
def timer(name: str):
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(f"{name} took {duration:.3f}s")


class QueryOptimizer:
    @staticmethod
    def optimize_chroma_query(query_text: str, n_results: int = 3) -> dict:
        return {
            "query_texts": [query_text],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }

    @staticmethod
    def batch_query(queries: list, n_results: int = 3) -> list:
        results = []
        for query in queries:
            results.append(
                QueryOptimizer.optimize_chroma_query(query, n_results)
            )
        return results


class MemoryOptimizer:
    @staticmethod
    def clear_matplotlib():
        try:
            import matplotlib.pyplot as plt
            plt.close("all")
        except ImportError:
            pass

    @staticmethod
    def cleanup_large_objects(*objects):
        for obj in objects:
            del obj


class ConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self._pool = []
        self._in_use = set()

    def acquire(self):
        if self._pool:
            conn = self._pool.pop()
            self._in_use.add(id(conn))
            return conn
        return None

    def release(self, conn):
        conn_id = id(conn)
        if conn_id in self._in_use:
            self._in_use.remove(conn_id)
            if len(self._pool) < self.max_connections:
                self._pool.append(conn)

    def close_all(self):
        self._pool.clear()
        self._in_use.clear()
