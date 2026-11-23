"""Idempotency management service.

Pure in-memory TTL cache for detecting duplicate client_message_id per principal.
Routes build their own HTTP responses; this layer only returns duplication state.
"""

from __future__ import annotations

# Standard library imports
import os
import threading
import time
import uuid
from dataclasses import dataclass, field

# Local imports
from ..config import settings


@dataclass
class IdempotencyManager:
    ttl_sec: int
    enforce: bool
    _cache: dict[str, float] = field(default_factory=dict)
    _owners: dict[str, str] = field(default_factory=dict, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def _key(self, principal: str, client_id: str) -> str:
        return f"{principal}|{client_id}"

    def check_and_mark(self, principal: str, client_id: str) -> bool:
        """Return True if (principal, client_id) is a duplicate within TTL window.

        Always records the key (refreshing expiration) when not duplicate.
        When enforce is False, still records but never reports duplicate.
        """
        return bool(client_id) and self.reserve(principal, client_id) is None

    def reserve(self, principal: str, client_id: str) -> str | None:
        """Return an ownership token, or None for a duplicate or empty ID."""
        if not client_id:
            return None
        with self._lock:
            now = time.time()
            if len(self._cache) > 1024:
                expired = [k for k, exp in list(self._cache.items()) if exp <= now]
                for k in expired[:256]:
                    self._cache.pop(k, None)
                    self._owners.pop(k, None)
            k = self._key(principal or "anonymous", client_id)
            exp = self._cache.get(k)
            enforce = (
                self.enforce or os.environ.get("AETHERRA_IDEMPOTENCY_ENFORCE") == "1"
            )
            if enforce and exp and exp > now:
                return None
            ttl_env = os.environ.get("AETHERRA_IDEMPOTENCY_TTL_SEC")
            ttl = max(5, int(ttl_env or self.ttl_sec))
            token = uuid.uuid4().hex
            self._cache[k] = now + float(ttl)
            self._owners[k] = token
            return token

    def release(self, principal: str, client_id: str, token: str) -> None:
        """Release only this request's reservation after rejected admission."""
        with self._lock:
            k = self._key(principal or "anonymous", client_id)
            if self._owners.get(k) == token:
                self._cache.pop(k, None)
                self._owners.pop(k, None)


# Default singleton using global settings
manager = IdempotencyManager(
    ttl_sec=settings.idem_ttl_sec, enforce=settings.idem_enforce
)
