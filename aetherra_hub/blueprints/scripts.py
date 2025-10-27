"""Minimal scripts runner API for Lyrixa GUI.

Endpoints:
- POST /api/run           -> start a script, return job_id + status
- POST /api/cancel/<id>   -> cancel a script job, return ok

This is a lightweight in-memory shim to make the .aether panel fully
operational in environments where a full workflow runner isn't wired.
"""

from __future__ import annotations

# Standard library imports
import time
import uuid
from typing import Any

# Third party imports
from flask import Blueprint, jsonify, request

bp = Blueprint("scripts", __name__)


# In-memory job store (process local)
_jobs: dict[str, dict[str, Any]] = {}


@bp.post("/api/run")
def run_script():
    data = request.get_json(silent=True) or {}
    script_name = str(data.get("script_name") or data.get("name") or "").strip()
    params = data.get("parameters") or {}
    context = data.get("context") or {}
    if not script_name:
        return jsonify({"error": "missing_script_name"}), 400

    job_id = uuid.uuid4().hex
    # Record basic job info; a real runner would spawn work and stream logs
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
    job = _jobs.get(job_id)
    if not job:
        # Idempotent OK for UI simplicity
        return jsonify({"ok": True, "cancelled": False, "message": "job_not_found"})
    # Mark as cancelled; a real runner would signal the process/task
    job["status"] = "cancelled"
    job["cancelled_at"] = time.time()
    return jsonify({"ok": True, "cancelled": True, "job_id": job_id})
