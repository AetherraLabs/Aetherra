#!/usr/bin/env python3
"""Episodic Store

Lightweight append-only JSONL event log with retention policy for Phase 1.
Higher layers (narrative, summarizer) can aggregate older events.
"""

from __future__ import annotations

# Standard library imports
import json
import os
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

# Local imports
from .schemas.episodic_event import EpisodicEvent, EventAttribution

DEFAULT_EVENTS_PATH = os.getenv(
    "AETHERRA_EPISODIC_PATH", ".aetherra/episodic_events.jsonl"
)
MAX_EVENTS = int(os.getenv("AETHERRA_EPISODIC_MAX_EVENTS", "5000"))
RETENTION_HOURS = int(os.getenv("AETHERRA_EPISODIC_RETENTION_HOURS", "24"))
LOCK = threading.Lock()


class EpisodicStore:
    def __init__(self, path: str = DEFAULT_EVENTS_PATH):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: List[EpisodicEvent] = []
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        if self._path.exists():
            try:
                for line in self._path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    self._cache.append(EpisodicEvent(**data))
            except Exception:
                # Corruption fallback: rename file and start fresh
                corrupt = self._path.with_suffix(".corrupt")
                try:
                    self._path.rename(corrupt)
                except Exception:
                    pass
        self._loaded = True
        self._enforce_retention()

    def append(self, event: EpisodicEvent) -> None:
        with LOCK:
            self._load()
            self._cache.append(event)
            with self._path.open("a", encoding="utf-8") as f:
                f.write(event.model_dump_json() + "\n")
            self._enforce_limits()
            self._enforce_retention()

    def new_event(
        self, type: str, content: str, source: str, importance: float = 0.5, **kw
    ) -> EpisodicEvent:
        evt = EpisodicEvent(
            id=str(uuid.uuid4()),
            type=type,
            content=content,
            importance=importance,
            attribution=EventAttribution(
                source=source, agent=None, confidence=kw.pop("confidence", 1.0)
            ),
            **kw,
        )
        self.append(evt)
        return evt

    def list_recent(self, limit: int = 100) -> List[EpisodicEvent]:
        with LOCK:
            self._load()
            return list(self._cache[-limit:])

    def _enforce_limits(self) -> None:
        if len(self._cache) <= MAX_EVENTS:
            return
        # Trim oldest
        overflow = len(self._cache) - MAX_EVENTS
        self._cache = self._cache[overflow:]
        # Rewrite file compacted
        tmp = self._path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for e in self._cache:
                f.write(e.model_dump_json() + "\n")
        tmp.replace(self._path)

    def _enforce_retention(self) -> None:
        horizon = datetime.utcnow() - timedelta(hours=RETENTION_HOURS)
        original_len = len(self._cache)
        self._cache = [e for e in self._cache if e.ts >= horizon or e.importance >= 0.8]
        if len(self._cache) != original_len:
            tmp = self._path.with_suffix(".tmp")
            with tmp.open("w", encoding="utf-8") as f:
                for e in self._cache:
                    f.write(e.model_dump_json() + "\n")
            tmp.replace(self._path)


EPISODIC_STORE_SINGLETON: Optional[EpisodicStore] = None


def get_episodic_store() -> EpisodicStore:
    global EPISODIC_STORE_SINGLETON
    if EPISODIC_STORE_SINGLETON is None:
        EPISODIC_STORE_SINGLETON = EpisodicStore()
    return EPISODIC_STORE_SINGLETON
