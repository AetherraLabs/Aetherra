# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Federation utilities for multi-node hub discovery and plugin catalog sync.

Goals:
- Maintain a peer list (static config + runtime announce).
- Periodically fetch peer /api/plugins and merge a read-only federated view.
- Provide signed-manifest verification hooks (delegated to security.plugin_signing).

This module is optional; callers should handle ImportError gracefully.
"""

from __future__ import annotations

# Standard library imports
import json
import os
import threading
import time
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    # Aetherra imports
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

    def __init__(self, self_url: str = "http://localhost:3001", peers: Optional[List[str]] = None):
        self.self_url = self_url.rstrip("/")
        self._peers: Dict[str, Peer] = {
            p.rstrip("/"): Peer(url=p.rstrip("/")) for p in (peers or [])
        }
        self._federated_plugins: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self.interval = int(os.environ.get("AETHERRA_FEDERATION_INTERVAL_SEC", "60"))
        # Optional persistence
        self._persist = os.environ.get("AETHERRA_FEDERATION_STATE", "0") == "1"
        self._state_dir = Path(
            os.environ.get("AETHERRA_STATE_DIR", os.path.expanduser("~/.aetherra"))
        ).resolve()
        self._state_file = self._state_dir / "hub_state.json"
        if self._persist:
            self._load_state()

    def add_peer(self, url: str):
        url = url.rstrip("/")
        if url == self.self_url:
            return
        with self._lock:
            self._peers.setdefault(url, Peer(url=url))
            if self._persist:
                self._save_state()

    def list_peers(self) -> List[dict]:
        with self._lock:
            return [peer.__dict__ for peer in self._peers.values()]

    def get_federated_plugins(self) -> List[dict]:
        with self._lock:
            return list(self._federated_plugins.values())

    def start_background_sync(self):
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    def stop(self):
        self._stop.set()

    def _loop(self):
        while not self._stop.is_set():
            with suppress(Exception):
                self.sync_once()
            self._stop.wait(self.interval)

    def sync_once(self):
        from Aetherra.security.net_policy import http_get

        merged: Dict[str, dict] = {}
        now = time.time()
        with self._lock:
            peers = list(self._peers.values())
        for peer in peers:
            try:
                resp = http_get(
                    f"{peer.url}/api/plugins",
                    timeout=5,
                    requester="hub:federation:sync",
                    headers=self._auth_headers(),
                )
                if resp is None or resp.status_code != 200:
                    status = resp.status_code if resp is not None else "denied"
                    raise RuntimeError(f"status {status}")
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
            if self._persist:
                self._save_state()

    def announce_once(self):
        """Announce this hub to all known peers (best-effort)."""
        from Aetherra.security.net_policy import http_post

        now = time.time()
        with self._lock:
            peers = list(self._peers.values())
        for peer in peers:
            try:
                resp = http_post(
                    f"{peer.url}/api/peers",
                    {"url": self.self_url},
                    timeout=5,
                    requester="hub:federation:announce",
                    headers=self._auth_headers(),
                )
                if resp is not None and resp.status_code in (200, 201, 202):
                    peer.healthy = True
                    peer.last_seen = now
                else:
                    peer.healthy = False
            except Exception:
                peer.healthy = False

    @staticmethod
    def _auth_headers() -> dict[str, str] | None:
        token = (
            os.environ.get("AETHERRA_FEDERATION_TOKEN")
            or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
            or ""
        ).strip()
        return {"Authorization": f"Bearer {token}"} if token else None

    # Persistence helpers (best-effort, never fatal)
    def _load_state(self):
        try:
            self._state_dir.mkdir(parents=True, exist_ok=True)
            if self._state_file.exists():
                data = json.loads(self._state_file.read_text(encoding="utf-8"))
                peers = data.get("peers", [])
                for p in peers:
                    if isinstance(p, str):
                        self._peers.setdefault(p.rstrip("/"), Peer(url=p.rstrip("/")))
        except Exception:
            pass

    def _save_state(self):
        try:
            self._state_dir.mkdir(parents=True, exist_ok=True)
            data = {
                "peers": list(self._peers.keys()),
                # Store only counts to avoid bloat
                "federated_count": len(self._federated_plugins),
            }
            self._state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass


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
