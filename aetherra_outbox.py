#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Outbox / Write-Ahead Log (WAL)
--------------------------------------
Append-only queue for deferred, policy-gated writes while running in AAR
headless/safe modes. Entries are JSON objects with an idempotency key.
"""

from __future__ import annotations

# Standard library imports
import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class OutboxEntry:
    key: str
    ts: float
    payload: Dict[str, Any]


class Outbox:
    def __init__(self, root: Optional[str] = None) -> None:
        base = Path(root or os.getcwd()) / "outbox"
        base.mkdir(parents=True, exist_ok=True)
        self._path = base / "outbox.jsonl"
        # Use a lock to serialize appends across threads
        self._lock = threading.Lock()

    def _make_key(self, payload: Dict[str, Any]) -> str:
        # Stable hash over canonical JSON representation
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
        return hashlib.sha256(blob).hexdigest()[:16]

    def enqueue(self, payload: Dict[str, Any]) -> OutboxEntry:
        ts = time.time()
        key = self._make_key(payload | {"ts": ts})
        entry = {"key": key, "ts": ts, "payload": payload}
        with self._lock:
            with self._path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return OutboxEntry(key=key, ts=ts, payload=payload)

    def iter_entries(self):
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    yield obj
                except Exception:
                    continue

    def clear(self) -> None:
        # Rotate by truncating
        with self._lock:
            self._path.write_text("", encoding="utf-8")
