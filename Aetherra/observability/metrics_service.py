# SPDX-License-Identifier: GPL-3.0-or-later
"""Lightweight in-process metrics exposure service.

Aggregates metrics from:
- BeyondTranscendenceEngine (if available)
- SelfImprovementEngine (if provided)

Usage (illustrative):

    svc = MetricsService()
    svc.register_adapter('transcendence', transcendence_engine.export_metrics)
    svc.register_adapter('self_improvement', self_improvement_engine.export_internal_metrics)
    await svc.start(host='127.0.0.1', port=8765)

HTTP (very small footprint, no external deps):
GET /metrics -> JSON dict { namespace: metrics_dict }

Design goals:
- Zero external dependency (stdlib only)
- Non-blocking (asyncio streams)
- Safe shutdown
- Deterministic-friendly (ordering stable)
"""

from __future__ import annotations

# Standard library imports
import asyncio
import contextlib
import json
import logging
from typing import Callable, Dict

logger = logging.getLogger(__name__)

MetricsProvider = Callable[[], Dict[str, float | int | float]]


class MetricsService:
    def __init__(self):
        self._providers: dict[str, MetricsProvider] = {}
        self._server: asyncio.base_events.Server | None = None
        self._task_loop = None

    def register_adapter(self, name: str, provider: MetricsProvider):
        if not callable(provider):  # pragma: no cover - defensive
            raise TypeError("provider must be callable returning a metrics dict")
        self._providers[name] = provider

    async def start(self, host: str = "127.0.0.1", port: int = 8765):
        if self._server is not None:
            return
        loop = asyncio.get_running_loop()
        self._task_loop = loop
        self._server = await asyncio.start_server(self._handle_client, host, port)
        sockets = self._server.sockets or []
        if sockets:
            logger.info("MetricsService listening on %s:%s", host, port)

    async def stop(self):
        if self._server is None:
            return
        self._server.close()
        with contextlib.suppress(Exception):  # pragma: no cover - rare path
            await self._server.wait_closed()
        self._server = None
        logger.info("MetricsService stopped")

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        try:
            data = await reader.readline()
            request_line = data.decode(errors="ignore").strip()
            if not request_line:
                writer.close()
                await writer.wait_closed()
                return
            # Simple parse; expect GET /metrics HTTP/1.1
            parts = request_line.split()
            path = parts[1] if len(parts) >= 2 else "/"
            if path != "/metrics":
                body = json.dumps({"error": "not found"}).encode()
                writer.write(
                    b"HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\nContent-Length: "
                    + str(len(body)).encode()
                    + b"\r\n\r\n"
                    + body
                )
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return
            # Collect metrics
            payload = {}
            for name in sorted(self._providers.keys()):
                try:
                    payload[name] = self._providers[name]()
                except Exception as e:  # pragma: no cover - isolation path
                    payload[name] = {"error": str(e)}
            body = json.dumps(payload, sort_keys=True).encode()
            writer.write(
                b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: "
                + str(len(body)).encode()
                + b"\r\n\r\n"
                + body
            )
            await writer.drain()
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    def current_snapshot(self) -> dict[str, dict]:  # pragma: no cover - simple accessor
        out: dict[str, dict] = {}
        for name, provider in self._providers.items():
            try:
                out[name] = provider()
            except Exception as e:  # defensive
                out[name] = {"error": str(e)}
        return out


__all__ = ["MetricsService", "MetricsProvider"]
