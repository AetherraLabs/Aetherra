"""Simple header-based idempotency store (independent of principal).

Used specifically for plugin registration to avoid collisions with
chat/message idempotency logic.
"""

from __future__ import annotations

# Standard library imports
import threading
import time
from dataclasses import dataclass

__all__ = ["IdempotencyStore", "IdemResult"]


@dataclass(frozen=True)
class IdemResult:
    already_processed: bool


class IdempotencyStore:
    """Minimal in-memory TTL idempotency store.

    - Thread-safe
    - Simple TTL eviction
    - Suitable for low-volume dev/test usage; replace with Redis for scale.
    """

    def __init__(self, ttl_seconds: int = 600):
        self._ttl = max(1, int(ttl_seconds))
        self._lock = threading.Lock()
        self._hits: dict[str, float] = {}

    def check_and_mark(self, key: str) -> IdemResult:
        if not key:
            return IdemResult(already_processed=False)
        now = time.time()
        with self._lock:
            self._purge_locked(now)
            ts = self._hits.get(key)
            if ts is not None and (now - ts) < self._ttl:
                return IdemResult(already_processed=True)
            self._hits[key] = now
            return IdemResult(already_processed=False)

    def _purge_locked(self, now: float) -> None:
        if not self._hits:
            return
        expired = [k for k, ts in self._hits.items() if (now - ts) >= self._ttl]
        for k in expired[:256]:  # soft cap purges per call
            self._hits.pop(k, None)
