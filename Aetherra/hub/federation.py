"""
Federation utilities for multi-node hub discovery and plugin catalog sync.

Goals:
- Maintain a peer list (static config + runtime announce).
- Periodically fetch peer /api/plugins and merge a read-only federated view.
- Provide signed-manifest verification hooks (delegated to security.plugin_signing).

This module is optional; callers should handle ImportError gracefully.
"""

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional dep
    requests = None  # type: ignore

try:
    from Aetherra.security.plugin_signing import verify_plugin_signature
except Exception:

    def verify_plugin_signature(manifest: dict) -> bool:  # fallback no-op
        return True


@dataclass
class Peer:
    url: str
    last_seen: Optional[float] = None
    healthy: bool = False


class FederationManager:
    """Simple peer registry and federated catalog cache."""

    def __init__(
        self, self_url: str = "http://localhost:3001", peers: Optional[List[str]] = None
    ):
        self.self_url = self_url.rstrip("/")
        self._peers: Dict[str, Peer] = {
            p.rstrip("/"): Peer(url=p.rstrip("/")) for p in (peers or [])
        }
        self._federated_plugins: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self.interval = int(os.environ.get("AETHERRA_FEDERATION_INTERVAL_SEC", "60"))

    def add_peer(self, url: str):
        url = url.rstrip("/")
        if url == self.self_url:
            return
        with self._lock:
            self._peers.setdefault(url, Peer(url=url))

    def list_peers(self) -> List[dict]:
        with self._lock:
            return [peer.__dict__ for peer in self._peers.values()]

    def get_federated_plugins(self) -> List[dict]:
        with self._lock:
            return list(self._federated_plugins.values())

    def start_background_sync(self):
        if requests is None:
            return  # requests not available
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    def stop(self):
        self._stop.set()

    def _loop(self):
        while not self._stop.is_set():
            try:
                self.sync_once()
            except Exception:
                pass
            self._stop.wait(self.interval)

    def sync_once(self):
        if requests is None:
            return
        merged: Dict[str, dict] = {}
        now = time.time()
        with self._lock:
            peers = list(self._peers.values())
        for peer in peers:
            try:
                resp = requests.get(f"{peer.url}/api/plugins", timeout=5)
                if resp.status_code != 200:
                    raise RuntimeError(f"status {resp.status_code}")
                data = resp.json()
                plugin_list = data.get("plugins", [])
                for p in plugin_list:
                    # verify signature if present; skip unverifiable
                    if not verify_plugin_signature(p):
                        continue
                    key = f"{p.get('name')}@{p.get('version')}#{peer.url}"
                    merged[key] = {**p, "_source": peer.url}
                peer.healthy = True
                peer.last_seen = now
            except Exception:
                peer.healthy = False
        with self._lock:
            self._federated_plugins = merged


# Simple singleton used by hub server
_default_manager: Optional[FederationManager] = None


def get_federation_manager(
    self_url: str = "http://localhost:3001", peers: Optional[List[str]] = None
) -> FederationManager:
    global _default_manager
    if _default_manager is None:
        _default_manager = FederationManager(self_url=self_url, peers=peers)
        _default_manager.start_background_sync()
    return _default_manager
