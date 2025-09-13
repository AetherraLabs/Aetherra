#!/usr/bin/env python3
"""Unified Event Bus (Phase 1)

Lightweight in-process pub/sub bus to connect sensors (producers) and actuators
(consumers) and optionally bridge important events into the global workspace.

API:
  subscribe(event_type, handler) -> handler receives dict event
  publish(event_type, payload_dict, *, to_workspace=False, priority=0, weight=1.0, source="bus")

Env flags:
  AETHERRA_CONSCIOUSNESS_ENABLED=1 required for workspace bridging
  AETHERRA_EVENT_BUS_LOG=1 for console logging

Thread-safety: minimal; assumes single-threaded async / orchestrated usage for Phase 1.
"""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque
from typing import Any, Callable, DefaultDict, Dict, List

try:
    from .workspace_core import get_workspace
except Exception:  # pragma: no cover
    get_workspace = None  # type: ignore

_LOG = os.getenv("AETHERRA_EVENT_BUS_LOG", "0") == "1"


class EventBus:
    def __init__(self):
        self._subs: DefaultDict[str, List[Callable[[dict], None]]] = defaultdict(list)
        self._async_enabled = os.getenv("AETHERRA_EVENT_BUS_ASYNC", "0") == "1"
        self._max_queue = int(os.getenv("AETHERRA_EVENT_BUS_MAX", "1000"))
        self._queue: deque[dict] | None = deque() if self._async_enabled else None
        self._worker: threading.Thread | None = None
        self._stop = False
        if self._async_enabled:
            self._worker = threading.Thread(target=self._loop, daemon=True)
            self._worker.start()

    def subscribe(self, event_type: str, handler: Callable[[dict], None]) -> None:
        self._subs[event_type].append(handler)

    def publish(
        self,
        event_type: str,
        payload: Dict[str, Any],
        *,
        to_workspace: bool = False,
        priority: int = 0,
        weight: float = 1.0,
        source: str = "bus",
    ) -> None:
        evt = {
            "type": event_type,
            "ts": time.time(),
            **payload,
        }
        # If async mode, enqueue and return fast
        if self._async_enabled and self._queue is not None:
            if len(self._queue) < self._max_queue:
                self._queue.append(evt)
            else:
                # Drop oldest (backpressure strategy: drop-oldest)
                try:
                    self._queue.popleft()
                except Exception:
                    pass
                self._queue.append(evt)
        else:
            # Synchronous delivery
            for handler in list(self._subs.get(event_type, [])):
                try:
                    handler(evt)
                except Exception:
                    continue
        # Optionally forward into workspace as candidate
        if (
            to_workspace
            and get_workspace
            and os.getenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0") == "1"
        ):
            try:
                ws = get_workspace()
                if ws.enabled():
                    ws.add_candidate(
                        {"event_type": event_type, **payload},
                        priority=priority,
                        weight=weight,
                        source=source,
                    )
            except Exception:
                pass
        if _LOG:
            print(
                f"[EVENT_BUS] {event_type} (workspace={'Y' if to_workspace else 'N'})"
            )

    def _loop(self):  # async worker
        while not self._stop and self._queue is not None:
            try:
                if not self._queue:
                    time.sleep(0.01)
                    continue
                evt = self._queue.popleft()
                for handler in list(self._subs.get(evt["type"], [])):
                    try:
                        handler(evt)
                    except Exception:
                        continue
                # Workspace forwarding replicated for async path
                if (
                    get_workspace
                    and os.getenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0") == "1"
                    and evt.get("forward_workspace")
                ):
                    try:
                        ws = get_workspace()
                        if ws.enabled():
                            ws.add_candidate(
                                {"event_type": evt["type"], **evt},
                                priority=evt.get("priority", 0),
                                weight=evt.get("weight", 1.0),
                                source=evt.get("source", "bus"),
                            )
                    except Exception:
                        pass
            except Exception:
                time.sleep(0.01)


_EVENT_BUS_SINGLETON: EventBus | None = None


def get_event_bus() -> EventBus:
    global _EVENT_BUS_SINGLETON
    if _EVENT_BUS_SINGLETON is None:
        _EVENT_BUS_SINGLETON = EventBus()
    return _EVENT_BUS_SINGLETON
