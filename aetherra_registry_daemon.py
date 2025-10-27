#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Aetherra Registry Daemon (MVP): loopback service registry for multi-process deployments

from __future__ import annotations

import argparse
import threading
import time
from dataclasses import asdict, dataclass
from typing import Any

from flask import Flask, jsonify, request

app = Flask(__name__)


@dataclass
class ServiceEntry:
    name: str
    status: str = "unknown"  # unknown|starting|healthy|degraded|stopped
    metadata: dict[str, Any] | None = None
    endpoints: dict[str, str] | None = None
    last_heartbeat: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_SERVICES: dict[str, ServiceEntry] = {}
_LOCK = threading.Lock()


@app.get("/api/registry/status")
def api_status():
    with _LOCK:
        services = {k: v.to_dict() for k, v in _SERVICES.items()}
    total = len(services)
    return jsonify({"total_services": total, "services": services, "ts": time.time()})


@app.post("/api/registry/register")
def api_register():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "missing name"}), 400
    status = (data.get("status") or "starting").strip()
    entry = ServiceEntry(
        name=name,
        status=status,
        metadata=data.get("metadata") or {},
        endpoints=data.get("endpoints") or {},
        last_heartbeat=time.time(),
    )
    with _LOCK:
        _SERVICES[name] = entry
    return jsonify({"ok": True})


@app.post("/api/registry/heartbeat")
def api_heartbeat():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "missing name"}), 400
    with _LOCK:
        entry = _SERVICES.get(name)
        if not entry:
            return jsonify({"ok": False, "error": "unknown service"}), 404
        entry.last_heartbeat = time.time()
    return jsonify({"ok": True})


@app.post("/api/registry/update")
def api_update():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "missing name"}), 400
    with _LOCK:
        entry = _SERVICES.get(name)
        if not entry:
            return jsonify({"ok": False, "error": "unknown service"}), 404
        status = data.get("status")
        if status:
            entry.status = status
        md = data.get("metadata")
        if isinstance(md, dict):
            entry.metadata = (entry.metadata or {}) | md
        eps = data.get("endpoints")
        if isinstance(eps, dict):
            entry.endpoints = (entry.endpoints or {}) | eps
        entry.last_heartbeat = time.time()
    return jsonify({"ok": True})


@app.post("/api/registry/unregister")
def api_unregister():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "missing name"}), 400
    with _LOCK:
        _SERVICES.pop(name, None)
    return jsonify({"ok": True})


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=3030)
    args = p.parse_args()
    app.run(host=args.host, port=args.port, debug=False, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
