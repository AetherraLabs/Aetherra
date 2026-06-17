#!/usr/bin/env python3
"""Episodic Store

Lightweight append-only JSONL event log with retention policy for Phase 1.
Higher layers (narrative, summarizer) can aggregate older events.
"""

from __future__ import annotations

# Standard library imports
import contextlib
import hashlib
import json
import os
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

# Local imports
from .schemas.episodic_event import EpisodicEvent, EventAttribution

DEFAULT_EVENTS_PATH = os.getenv("AETHERRA_EPISODIC_PATH", ".aetherra/episodic_events.jsonl")
DEFAULT_MAX_EVENTS = 5000
DEFAULT_RETENTION_HOURS = 24
LOCK = threading.RLock()


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _hash_value(value: object) -> str | None:
    raw = str(value) if value is not None else ""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _episodic_capability_checker(requester: str, capability: str) -> bool:
    if requester == "consciousness:episodic" and capability in {
        "consciousness:write",
        "memory:write",
        "fs:write",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _evaluate_episodic_append_guardian(*, path: Path, event: EpisodicEvent):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "consciousness:episodic"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    content = str(event.content or "")
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="consciousness",
            action="consciousness.episodic_event_append",
            target=f"episodic_event:{event.type}",
            purpose="Append a consciousness episodic event to the local continuity log",
            capabilities=("consciousness:write", "memory:write", "fs:write"),
            evidence=("episodic_store.append",),
            reversible=True,
            rollback_plan="remove the appended event from the episodic JSONL log or restore the previous log snapshot",
            metadata={
                "path_hash": _hash_value(path.resolve()),
                "event_type": event.type,
                "event_id_hash": _hash_value(event.id),
                "content_hash": _hash_value(content),
                "content_length": len(content),
                "source_hash": _hash_value(event.attribution.source),
                "importance": event.importance,
                "tag_count": len(event.tags),
                "workspace_priority": event.workspace_priority,
            },
        ),
        approval_id=approval_id,
        capability_checker=_episodic_capability_checker,
    )


class EpisodicStore:
    def __init__(
        self,
        path: str | None = None,
        *,
        max_events: int | None = None,
        retention_hours: int | None = None,
    ):
        path = path or os.getenv("AETHERRA_EPISODIC_PATH", DEFAULT_EVENTS_PATH)
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._max_events = max_events or _env_int(
            "AETHERRA_EPISODIC_MAX_EVENTS", DEFAULT_MAX_EVENTS
        )
        self._retention_hours = retention_hours or _env_int(
            "AETHERRA_EPISODIC_RETENTION_HOURS", DEFAULT_RETENTION_HOURS
        )
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
                with contextlib.suppress(Exception):
                    self._path.rename(corrupt)
        self._loaded = True
        self._enforce_retention()

    def append(self, event: EpisodicEvent) -> None:
        with LOCK:
            self._load()
            guardian_decision = _evaluate_episodic_append_guardian(
                path=self._path,
                event=event,
            )
            if not guardian_decision.allowed:
                raise PermissionError(f"guardian_denied:{guardian_decision.reason}")
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
        if len(self._cache) <= self._max_events:
            return
        # Trim oldest
        overflow = len(self._cache) - self._max_events
        self._cache = self._cache[overflow:]
        # Rewrite file compacted
        tmp = self._path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for e in self._cache:
                f.write(e.model_dump_json() + "\n")
        tmp.replace(self._path)

    def _enforce_retention(self) -> None:
        horizon = datetime.utcnow() - timedelta(hours=self._retention_hours)
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
    current_path = Path(os.getenv("AETHERRA_EPISODIC_PATH", DEFAULT_EVENTS_PATH))
    if EPISODIC_STORE_SINGLETON is None or EPISODIC_STORE_SINGLETON._path != current_path:
        EPISODIC_STORE_SINGLETON = EpisodicStore()
    return EPISODIC_STORE_SINGLETON
