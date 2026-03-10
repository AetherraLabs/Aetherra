"""Idempotency management service.

Pure in-memory TTL cache for detecting duplicate client_message_id per principal.
Routes build their own HTTP responses; this layer only returns duplication state.
"""

from __future__ import annotations

# Standard library imports
import time
from dataclasses import dataclass, field

# Local imports
from ..config import settings


@dataclass
class IdempotencyManager:
    ttl_sec: int
    enforce: bool
    _cache: dict[str, float] = field(default_factory=dict)

    def _key(self, principal: str, client_id: str) -> str:
        return f"{principal}|{client_id}"

    def check_and_mark(self, principal: str, client_id: str) -> bool:
        """Return True if (principal, client_id) is a duplicate within TTL window.

        Always records the key (refreshing expiration) when not duplicate.
        When enforce is False, still records but never reports duplicate.
        """
        if not client_id:
            return False
        now = time.time()
        # Opportunistic cleanup of expired entries when map grows
        if len(self._cache) > 1024:
            expired = [k for k, exp in list(self._cache.items()) if exp <= now]
            for k in expired[:256]:
                self._cache.pop(k, None)
        k = self._key(principal or "anonymous", client_id)
        exp = self._cache.get(k)
        if self.enforce and exp and exp > now:
            return True
        # (Re)write expiration
        ttl = max(5, int(self.ttl_sec))
        self._cache[k] = now + float(ttl)
        return False


# Default singleton using global settings
manager = IdempotencyManager(
    ttl_sec=settings.idem_ttl_sec, enforce=settings.idem_enforce
)
