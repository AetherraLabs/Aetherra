#!/usr/bin/env python3
"""Global Workspace Core (Phase 1 Skeleton)

Implements a lightweight attention gating and broadcast mechanism for candidate cognitive processes.

Design goals (RFC Phase 1):
- Accept candidate "thought" objects with metadata (priority, source, affect_bias, ethics_score)
- Periodically select a winner (attention) using a pluggable strategy
- Broadcast selected thought to registered subscribers
- Maintain simple metrics (queue depth, selection latency)
- Enforce caps & safeguards (max candidates, max broadcast per interval)

Environment variables (initial):
- AETHERRA_CONSCIOUSNESS_ENABLED=1 -> activate workspace integration
- AETHERRA_WORKSPACE_MAX_CANDIDATES (default 256)
- AETHERRA_WORKSPACE_SELECT_INTERVAL_MS (default 500)
- AETHERRA_WORKSPACE_MAX_BROADCAST_PER_MIN (default 600)

This skeleton intentionally omits advanced scheduling, coherence scoring, and ethics integration.
Future phases will extend with:
- Affect weighting
- Ethics critic veto hooks
- Active inference policy wrapping
- Narrative and coherence updates
"""

from __future__ import annotations

# Standard library imports
import asyncio
import heapq
import os
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, List, Optional

try:  # optional metrics exporter
    # Local imports
    from .metrics_exporter import inc_workspace_broadcast as _metrics_inc_broadcast
    from .metrics_exporter import inc_workspace_candidate as _metrics_inc_candidate
    from .metrics_exporter import initialize_exporter as _metrics_init
    from .metrics_exporter import observe_workspace_latency as _metrics_obs_latency
    from .metrics_exporter import update_workspace_queue as _metrics_update_q
except Exception:  # pragma: no cover
    _metrics_init = None  # type: ignore
    _metrics_update_q = None  # type: ignore
    _metrics_inc_candidate = None  # type: ignore
    _metrics_inc_broadcast = None  # type: ignore
    _metrics_obs_latency = None  # type: ignore

try:  # optional affect engine biasing
    # Local imports
    from .affect_engine import get_affect_engine as _get_affect_engine
except Exception:  # pragma: no cover
    _get_affect_engine = None  # type: ignore


@dataclass(order=True)
class WorkspaceCandidate:
    sort_key: float
    priority: int = field(compare=False)
    created_ts: float = field(compare=False, default_factory=lambda: time.time())
    payload: dict = field(compare=False, default_factory=dict)
    source: str = field(compare=False, default="unknown")
    metadata: dict = field(compare=False, default_factory=dict)


class WorkspaceCore:
    def __init__(self):
        self._enabled = os.getenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0") == "1"
        self._max_candidates = int(os.getenv("AETHERRA_WORKSPACE_MAX_CANDIDATES", "256"))
        self._select_interval_ms = int(os.getenv("AETHERRA_WORKSPACE_SELECT_INTERVAL_MS", "500"))
        self._max_broadcast_per_min = int(
            os.getenv("AETHERRA_WORKSPACE_MAX_BROADCAST_PER_MIN", "600")
        )
        self._queue: List[WorkspaceCandidate] = []  # min-heap by sort_key
        self._subscribers: List[Callable[[dict], Awaitable[None] | None]] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._broadcast_count_window: int = 0
        self._broadcast_window_start: float = time.time()
        # Consciousness stream tap (optional)
        self._stream_enabled = os.getenv("AETHERRA_CONSCIOUSNESS_STREAM", "1") == "1"
        self._stream_path = os.getenv(
            "AETHERRA_CONSCIOUSNESS_STREAM_PATH", ".aetherra/consciousness_stream.log"
        )
        self._stream_hook: Optional[Callable[[dict], None]] = None
        if self._stream_enabled:
            try:
                os.makedirs(os.path.dirname(self._stream_path), exist_ok=True)
            except Exception:
                pass
        # Initialize metrics exporter if requested
        if _metrics_init:
            try:
                _metrics_init()
            except Exception:
                pass

    def enabled(self) -> bool:
        return self._enabled

    def subscribe(self, handler: Callable[[dict], Awaitable[None] | None]) -> None:
        self._subscribers.append(handler)

    def set_stream_hook(self, hook: Callable[[dict], None]):
        """Register a lightweight synchronous hook for UI layers to observe broadcasts."""
        self._stream_hook = hook

    def add_candidate(
        self,
        payload: dict,
        priority: int = 0,
        weight: float = 1.0,
        source: str = "unknown",
        **metadata: Any,
    ) -> bool:
        if not self._enabled:
            return False
        if len(self._queue) >= self._max_candidates:
            # Drop lowest priority (largest sort_key) if this one is better
            try:
                worst = max(self._queue)
                worst_key = worst.sort_key
                new_key = self._compute_sort_key(priority, weight)
                if new_key < worst_key:
                    # Replace worst
                    self._queue.remove(worst)
                    heapq.heapify(self._queue)
                else:
                    return False
            except ValueError:
                return False
        candidate = WorkspaceCandidate(
            sort_key=self._compute_sort_key(priority, weight),
            priority=priority,
            payload=payload,
            source=source,
            metadata=metadata,
        )
        candidate.metadata["enqueue_ts"] = time.time()
        heapq.heappush(self._queue, candidate)
        # metrics
        if _metrics_update_q:
            try:
                _metrics_update_q(len(self._queue))
            except Exception:
                pass
        if _metrics_inc_candidate:
            try:
                _metrics_inc_candidate(source)
            except Exception:
                pass
        return True

    def _compute_sort_key(self, priority: int, weight: float) -> float:
        # Lower sort_key = higher attention; weight can incorporate affect/ethics
        # Apply optional affect multiplier when enabled
        adj_weight = weight
        if _get_affect_engine and os.getenv("AETHERRA_AFFECT_WEIGHT", "1") == "1":
            try:
                adj_weight = max(adj_weight, 0.0001) * _get_affect_engine().affect_weight(priority)
            except Exception:
                pass
        return -(priority) / max(adj_weight, 0.0001)

    async def start(self) -> None:
        if not self._enabled or self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self) -> None:
        interval = max(0.01, self._select_interval_ms / 1000.0)
        while self._running:
            try:
                await asyncio.sleep(interval)
                self._reset_window_if_needed()
                if not self._queue:
                    continue
                if self._broadcast_count_window >= self._max_broadcast_per_min:
                    continue
                candidate = heapq.heappop(self._queue)
                if _metrics_update_q:
                    try:
                        _metrics_update_q(len(self._queue))
                    except Exception:
                        pass
                # Latency observation
                if _metrics_obs_latency:
                    try:
                        enqueue_ts = candidate.metadata.get("enqueue_ts")
                        if enqueue_ts:
                            _metrics_obs_latency(time.time() - enqueue_ts)
                    except Exception:
                        pass
                await self._broadcast(candidate)
            except asyncio.CancelledError:
                break
            except Exception:
                # swallow for resilience; future: metric/log
                pass

    async def _broadcast(self, candidate: WorkspaceCandidate) -> None:
        self._broadcast_count_window += 1
        for handler in list(self._subscribers):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(candidate.payload)
                else:
                    handler(candidate.payload)
            except Exception:
                # future: track handler failure metric
                continue
        # metrics: broadcast counter per source
        try:
            if _metrics_inc_broadcast:
                _metrics_inc_broadcast(candidate.source)
        except Exception:
            pass
        # stream tap
        if self._stream_enabled:
            try:
                line = {
                    "ts": time.time(),
                    "source": candidate.source,
                    "payload": candidate.payload,
                }
                with open(self._stream_path, "a", encoding="utf-8") as f:
                    f.write(f"{line}\n")
                if self._stream_hook:
                    try:
                        self._stream_hook(line)
                    except Exception:
                        pass
            except Exception:
                pass

    def _reset_window_if_needed(self) -> None:
        now = time.time()
        if now - self._broadcast_window_start >= 60:
            self._broadcast_window_start = now
            self._broadcast_count_window = 0

    def queue_size(self) -> int:
        return len(self._queue)


# Convenience singleton pattern (can refine later)
_workspace_singleton: Optional[WorkspaceCore] = None


def get_workspace() -> WorkspaceCore:
    global _workspace_singleton
    if _workspace_singleton is None:
        _workspace_singleton = WorkspaceCore()
    return _workspace_singleton
