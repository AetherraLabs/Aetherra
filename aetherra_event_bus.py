#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
[KEB] Kernel Event Bus
======================

In-memory pub/sub event bus with minimal durability hooks and burst control.
Provides a simple contract for publish/subscribe/ack and exposes counters for
Prometheus via the Hub.
"""

# Standard library imports
import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Deque, Dict, Optional, Set


@dataclass
class Topic:
    name: str
    backlog: Deque[Dict[str, Any]] = field(default_factory=deque)
    subscribers: Set[str] = field(default_factory=set)  # service names


class EventBus:
    def __init__(self, service_registry):
        self.registry = service_registry
        self._topics: Dict[str, Topic] = {}
        # Simple per-topic token bucket: tokens per interval (sec)
        self._tokens: Dict[str, tuple[float, float]] = defaultdict(lambda: (0.0, 0.0))
        # Metrics counters
        self._metrics = {
            "events_published_total": 0,
            "events_delivered_total": 0,
            "events_dropped_burst": 0,
        }
        self._lock = asyncio.Lock()
        # Config
        self._rate_per_sec = 100.0  # default publish allowance per topic
        self._max_backlog = 1000

    # --------------- Control-plane API ---------------
    async def publish(self, topic: str, event: Dict[str, Any]) -> Dict[str, Any]:
        t = str(topic).strip()
        if not t:
            return {"ok": False, "error": "invalid_topic"}
        async with self._lock:
            top = self._topics.setdefault(t, Topic(name=t))
            # Rate limit (token bucket)
            now = datetime.now().timestamp()
            tokens, last = self._tokens[t]
            tokens = min(self._rate_per_sec, tokens + (now - last) * self._rate_per_sec)
            if tokens < 1.0:
                self._metrics["events_dropped_burst"] += 1
                self._tokens[t] = (tokens, now)
                return {"ok": False, "error": "burst"}
            tokens -= 1.0
            self._tokens[t] = (tokens, now)
            # Enqueue with cap
            if len(top.backlog) >= self._max_backlog:
                # Drop oldest to keep headroom
                try:
                    top.backlog.popleft()
                except Exception:
                    pass
            top.backlog.append({"ts": datetime.now().isoformat(), **(event or {})})
            self._metrics["events_published_total"] += 1
        # Fan-out best-effort without holding the lock
        await self._fanout(t)
        return {"ok": True}

    async def subscribe(self, topic: str, service_name: str) -> Dict[str, Any]:
        t = str(topic).strip()
        s = str(service_name).strip()
        if not t or not s:
            return {"ok": False, "error": "invalid"}
        async with self._lock:
            top = self._topics.setdefault(t, Topic(name=t))
            top.subscribers.add(s)
        return {"ok": True}

    async def ack(self, topic: str, count: int = 1) -> Dict[str, Any]:
        t = str(topic).strip()
        c = max(0, int(count))
        async with self._lock:
            top = self._topics.get(t)
            if not top:
                return {"ok": False, "error": "not_found"}
            for _ in range(min(c, len(top.backlog))):
                try:
                    top.backlog.popleft()
                except Exception:
                    break
        return {"ok": True}

    # --------------- Registry messaging surface ---------------
    async def handle_message(self, message_type: str, data: Any) -> Any:
        mt = (message_type or "").lower()
        payload = data or {}
        if mt.endswith("event.publish"):
            return await self.publish(
                payload.get("topic", ""), payload.get("event") or {}
            )
        if mt.endswith("event.subscribe"):
            return await self.subscribe(
                payload.get("topic", ""), payload.get("service", "")
            )
        if mt.endswith("event.ack"):
            return await self.ack(payload.get("topic", ""), payload.get("count", 1))
        if mt.endswith("event.status"):
            return self.get_status()
        return {"ok": False, "error": "unknown_message"}

    # --------------- Observability ---------------
    def get_metrics(self) -> Dict[str, Any]:
        per_topic_backlog = {n: len(t.backlog) for n, t in self._topics.items()}
        return {**self._metrics.copy(), "topic_backlog": per_topic_backlog}

    def get_status(self) -> Dict[str, Any]:
        return {
            "topics": {
                n: {"subscribers": list(t.subscribers), "backlog": len(t.backlog)}
                for n, t in self._topics.items()
            },
            "metrics": self.get_metrics(),
        }

    async def shutdown(self):
        return True

    # --------------- Internals ---------------
    async def _fanout(self, topic: str):
        top = self._topics.get(topic)
        if not top or not self.registry:
            return
        # Deliver head-of-line event to all subscribers (best-effort broadcast)
        evt = None
        try:
            if top.backlog:
                evt = top.backlog[0]
        except Exception:
            evt = None
        if not evt:
            return
        # Broadcast without popping; consumer acks advance the backlog
        try:
            await self.registry.broadcast_message(f"keb.event.{topic}", evt)
            self._metrics["events_delivered_total"] += len(top.subscribers or [])
        except Exception:
            pass


# Global singleton factory
_event_bus_instance: Optional[EventBus] = None


async def get_event_bus(service_registry) -> EventBus:
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus(service_registry)
    return _event_bus_instance
