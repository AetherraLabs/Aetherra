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
import logging
from collections import defaultdict, deque
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Topic:
    name: str
    backlog: deque[dict[str, Any]] = field(default_factory=deque)
    subscribers: set[str] = field(default_factory=set)  # service names


class EventBus:
    def __init__(self, service_registry):
        self.registry = service_registry
        self._topics: dict[str, Topic] = {}
        # Simple per-topic token bucket: tokens per interval (sec)
        self._tokens: dict[str, tuple[float, float]] = defaultdict(lambda: (0.0, 0.0))
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

    def _guardian_requester(self, value: Any, fallback: str = "event_bus") -> str:
        requester = str(value or fallback).strip()
        return requester or fallback

    def _guardian_capability_checker(self, requester: str, capability: str) -> bool:
        if requester == "event_bus" and capability in {
            "event:publish",
            "event:subscribe",
            "event:ack",
            "event:command",
        }:
            return True
        from Aetherra.security.capabilities import has_capability

        return has_capability(requester, capability)

    def _publish_capabilities(
        self, topic: str, event_payload: dict[str, Any]
    ) -> tuple[str, ...]:
        capabilities = ["event:publish"]
        event_type = str(event_payload.get("type") or "").strip().lower()
        topic_parts = {
            part
            for part in topic.replace("-", ".").replace("_", ".").lower().split(".")
            if part
        }
        event_parts = {
            part
            for part in event_type.replace("-", ".").replace("_", ".").split(".")
            if part
        }
        privileged_markers = {
            "admin",
            "command",
            "control",
            "execute",
            "reload",
            "restart",
            "shutdown",
        }
        if topic_parts & privileged_markers or event_parts & privileged_markers:
            capabilities.append("event:command")
        return tuple(capabilities)

    def _guardian_preflight(
        self,
        *,
        requester: str,
        action: str,
        topic: str,
        purpose: str,
        capabilities: tuple[str, ...],
        metadata: dict[str, Any],
    ) -> None:
        from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

        decision = evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="event_bus",
                action=action,
                target="event_bus:topic",
                purpose=purpose,
                capabilities=capabilities,
                evidence=(f"topic:{topic}",),
                reversible=True,
                rollback_plan="ack, unsubscribe, or ignore queued event depending on operation",
                metadata=metadata,
            ),
            capability_checker=self._guardian_capability_checker,
        )
        if decision.status not in {
            GuardianStatus.ALLOW,
            GuardianStatus.ALLOW_LIMITED,
        }:
            raise PermissionError(
                f"Guardian denied event bus action {action}: {decision.reason}"
            )

    # --------------- Control-plane API ---------------
    async def publish(self, topic: str, event: dict[str, Any]) -> dict[str, Any]:
        t = str(topic).strip()
        if not t:
            return {"ok": False, "error": "invalid_topic"}
        event_payload = event if isinstance(event, dict) else {}
        source = self._guardian_requester(event_payload.get("source"))
        capabilities = self._publish_capabilities(t, event_payload)
        self._guardian_preflight(
            requester=source,
            action=(
                "event_bus.publish_command"
                if "event:command" in capabilities
                else "event_bus.publish"
            ),
            topic=t,
            purpose=f"Publish event to topic {t}",
            capabilities=capabilities,
            metadata={
                "topic": t,
                "event_keys": tuple(sorted(str(key) for key in event_payload)),
                "event_type": str(event_payload.get("type") or ""),
                "source": source,
                "privileged": "event:command" in capabilities,
            },
        )
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
                with suppress(Exception):
                    top.backlog.popleft()
            top.backlog.append({"ts": datetime.now().isoformat(), **event_payload})
            self._metrics["events_published_total"] += 1
        # Fan-out best-effort without holding the lock
        await self._fanout(t)
        return {"ok": True}

    async def subscribe(self, topic: str, service_name: str) -> dict[str, Any]:
        t = str(topic).strip()
        s = str(service_name).strip()
        if not t or not s:
            return {"ok": False, "error": "invalid"}
        self._guardian_preflight(
            requester=self._guardian_requester(s),
            action="event_bus.subscribe",
            topic=t,
            purpose=f"Subscribe service {s} to topic {t}",
            capabilities=("event:subscribe",),
            metadata={"topic": t, "service_name": s},
        )
        async with self._lock:
            top = self._topics.setdefault(t, Topic(name=t))
            top.subscribers.add(s)
        return {"ok": True}

    async def ack(self, topic: str, count: int = 1) -> dict[str, Any]:
        t = str(topic).strip()
        c = max(0, int(count))
        if not t:
            return {"ok": False, "error": "invalid_topic"}
        self._guardian_preflight(
            requester="event_bus",
            action="event_bus.ack",
            topic=t,
            purpose=f"Acknowledge {c} event(s) on topic {t}",
            capabilities=("event:ack",),
            metadata={"topic": t, "count": c},
        )
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
    def get_metrics(self) -> dict[str, Any]:
        per_topic_backlog = {n: len(t.backlog) for n, t in self._topics.items()}
        return {**self._metrics.copy(), "topic_backlog": per_topic_backlog}

    def get_status(self) -> dict[str, Any]:
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
        except Exception as exc:
            logger.debug("KEB fanout failed for topic %s: %s", topic, exc)


# Global singleton factory
_event_bus_instance: EventBus | None = None


async def get_event_bus(service_registry) -> EventBus:
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus(service_registry)
    return _event_bus_instance
