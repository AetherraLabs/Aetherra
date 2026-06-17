"""Trainer blueprint exposing job/eval endpoints.

Relies on in-memory trainer service stub. Supports enabled/disabled mode via
AETHERRA_TRAINER_ENABLED env var. Disabled mode returns HTTP 400 for submit
endpoints while still exposing status + metrics.
"""

from __future__ import annotations

# Standard library imports
import os

# Third party imports
from flask import Blueprint, jsonify, request

# Local imports
from ..services import trainer as trainer_service
from ..services.control_auth import authorize_control_request

bp = Blueprint("trainer", __name__)


@bp.get("/api/trainer/status")
def trainer_status():  # pragma: no cover - tested via capabilities
    snap = trainer_service.snapshot_metrics()
    return jsonify(snap), 200


def _enabled() -> bool:
    return os.environ.get("AETHERRA_TRAINER_ENABLED", "0") == "1"


def _authorize():
    decision = authorize_control_request(request.headers, request.remote_addr)
    if decision.allowed:
        return None
    return jsonify({"error": decision.error}), decision.status_code


def _json_object():
    if request.content_length is not None and request.content_length > 262_144:
        return None, (jsonify({"error": "payload_too_large"}), 413)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, (jsonify({"error": "invalid_json_object"}), 400)
    return payload, None


@bp.post("/api/trainer/jobs")
def submit_job():  # pragma: no cover
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    if not _enabled():
        return jsonify({"error": "trainer disabled"}), 400
    payload, payload_error = _json_object()
    if payload_error is not None:
        return payload_error
    try:
        jid = trainer_service.submit_job(payload)  # returns None if disabled mid-flight
    except PermissionError as exc:
        return jsonify({"error": "guardian_denied", "reason": str(exc)}), 403
    if not jid:
        return jsonify({"error": "failed to enqueue job"}), 500
    return jsonify({"job_id": jid}), 200


@bp.get("/api/trainer/jobs")
def list_jobs():  # pragma: no cover
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    jobs = trainer_service.list_jobs()
    return jsonify({"jobs": jobs}), 200


@bp.get("/api/trainer/jobs/<job_id>")
def get_job(job_id: str):  # pragma: no cover
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    job = trainer_service.get_job(job_id)
    if not job:
        return jsonify({"error": "not found"}), 404
    return jsonify({"job": job}), 200


@bp.post("/api/trainer/evals")
def submit_eval():  # pragma: no cover
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    if not _enabled():
        return jsonify({"error": "trainer disabled"}), 400
    payload, payload_error = _json_object()
    if payload_error is not None:
        return payload_error
    try:
        eid = trainer_service.submit_eval(payload)
    except PermissionError as exc:
        return jsonify({"error": "guardian_denied", "reason": str(exc)}), 403
    if not eid:
        return jsonify({"error": "failed to enqueue eval"}), 500
    return jsonify({"eval_id": eid}), 200


@bp.get("/api/trainer/evals")
def list_evals():  # pragma: no cover
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    evals = trainer_service.list_evals()
    return jsonify({"evals": evals}), 200


@bp.get("/api/trainer/evals/<eval_id>")
def get_eval(eval_id: str):  # pragma: no cover
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    ev = trainer_service.get_eval(eval_id)
    if not ev:
        return jsonify({"error": "not found"}), 404
    return jsonify({"eval": ev}), 200
