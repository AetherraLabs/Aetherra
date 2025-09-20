#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Agent Runtime (AAR) - HTTP Broker
-----------------------------------------
Minimal HTTP broker exposing Agent Fabric APIs while the full OS is offline.

Endpoints (JSON):
- GET  /status        -> agents.status
- GET  /metrics       -> agents.metrics
- POST /run           -> agent.run      (body: {agent, ...})
- POST /pipeline      -> agent.pipeline (body: {goal, ...})

No external deps; uses wsgiref + a background asyncio loop to drive Fabric.
"""

from __future__ import annotations

# Standard library imports
import asyncio
import json
import threading
from typing import Any, Callable, Dict
from wsgiref.simple_server import make_server


class _AARLoop:
    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self._ready = threading.Event()

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self._bootstrap())
        self._ready.set()
        self.loop.run_forever()

    async def _bootstrap(self):
        # Aetherra imports
        from aetherra_agent_fabric import get_agent_fabric
        from aetherra_service_registry import get_service_registry, register_service

        reg = await get_service_registry()
        fabric = reg.get_service("agent_fabric")
        if not fabric:
            fabric = await get_agent_fabric(reg)
            await fabric.start()
            await register_service(
                "agent_fabric", fabric, metadata={"type": "agents", "aar_broker": True}
            )

    def start(self):
        if not self.thread.is_alive():
            self.thread.start()
            self._ready.wait(timeout=5)

    def submit(self, coro) -> Any:
        fut = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return fut.result(timeout=10)


_aar = _AARLoop()


def _json(start_response: Callable, code: str, obj: Dict[str, Any]):
    body = json.dumps(obj).encode("utf-8")
    start_response(
        code,
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


def application(environ, start_response):  # WSGI entry
    try:
        _aar.start()
        path = environ.get("PATH_INFO", "/")
        method = environ.get("REQUEST_METHOD", "GET").upper()
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
        except Exception:
            length = 0
        body = environ["wsgi.input"].read(length) if length > 0 else b""
        data = {}
        if body:
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception:
                data = {}

        async def call(message_type: str, payload: Dict[str, Any]):
            # Aetherra imports
            from aetherra_service_registry import get_service_registry

            reg = await get_service_registry()
            fabric = reg.get_service("agent_fabric")
            if not fabric:
                return {"ok": False, "error": "fabric_offline"}
            return await fabric.handle_message(message_type, payload)

        if method == "GET" and path == "/status":
            res = _aar.submit(call("agents.status", {}))
            return _json(start_response, "200 OK", res)
        if method == "GET" and path == "/metrics":
            res = _aar.submit(call("agents.metrics", {}))
            return _json(start_response, "200 OK", res)
        if method == "POST" and path == "/run":
            res = _aar.submit(call("agent.run", data or {}))
            return _json(start_response, "200 OK", res)
        if method == "POST" and path == "/pipeline":
            res = _aar.submit(call("agent.pipeline", data or {}))
            return _json(start_response, "200 OK", res)

        return _json(
            start_response, "404 Not Found", {"ok": False, "error": "not_found"}
        )
    except Exception as e:
        return _json(
            start_response, "500 Internal Server Error", {"ok": False, "error": str(e)}
        )


def main(host: str = "127.0.0.1", port: int = 7878):
    httpd = make_server(host, port, application)
    print(f"[AAR] Broker listening on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
