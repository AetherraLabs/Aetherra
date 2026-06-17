"""Script control API for Lyrixa GUI.

Endpoints:
- POST /api/run           -> start a script, return job_id + status
- POST /api/cancel/<id>   -> cancel a script job, return ok

This remains an in-memory job coordinator until the workflow runner is wired.
Control-plane authorization is enforced before job state can be mutated.
"""

from __future__ import annotations

# Standard library imports
import time
import uuid
from threading import RLock
from typing import Any

# Third party imports
from flask import Blueprint, jsonify, request

# Local imports
from ..services.control_auth import authorize_control_request

bp = Blueprint("scripts", __name__)


# In-memory job store (process local)
_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = RLock()
_MAX_JOBS = 1_000


def _authorize():
    decision = authorize_control_request(request.headers, request.remote_addr)
    if decision.allowed:
        return None
    return (
        jsonify({"ok": False, "error": decision.error}),
        decision.status_code,
    )


@bp.post("/api/run")
def run_script():
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error

    data = request.get_json(silent=True) or {}
    script_name = str(data.get("script_name") or data.get("name") or "").strip()
    params = data.get("parameters") or {}
    context = data.get("context") or {}
    if not script_name:
        return jsonify({"error": "missing_script_name"}), 400
    if len(script_name) > 255:
        return jsonify({"error": "script_name_too_long"}), 400
    if not isinstance(params, dict) or not isinstance(context, dict):
        return jsonify({"error": "invalid_job_payload"}), 400

    job_id = uuid.uuid4().hex
    with _jobs_lock:
        if len(_jobs) >= _MAX_JOBS:
            terminal_jobs = [
                key
                for key, value in _jobs.items()
                if value.get("status") in {"cancelled", "completed", "failed"}
            ]
            for key in terminal_jobs[: max(1, len(_jobs) - _MAX_JOBS + 1)]:
                _jobs.pop(key, None)
        if len(_jobs) >= _MAX_JOBS:
            return jsonify({"error": "job_capacity_reached"}), 503
        _jobs[job_id] = {
            "id": job_id,
            "script_name": script_name,
            "parameters": params,
            "context": context,
            "status": "running",
            "started_at": time.time(),
        }
    return jsonify({"ok": True, "job_id": job_id, "status": "running"})


@bp.post("/api/cancel/<job_id>")
def cancel_script(job_id: str):
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error

    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            return jsonify({"ok": True, "cancelled": False, "message": "job_not_found"})
        job["status"] = "cancelled"
        job["cancelled_at"] = time.time()
    return jsonify({"ok": True, "cancelled": True, "job_id": job_id})
