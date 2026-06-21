"""Kernel status, metrics, and privileged control endpoints."""

from __future__ import annotations

# Standard library imports
import asyncio
import os
from datetime import datetime
from typing import Any

# Third party imports
from flask import Blueprint, jsonify, request

from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent
from Aetherra.aetherra_core.os_kernel import build_kernel_readiness_payload

# Local imports
from ..services import registry_client
from ..services.control_auth import authorize_token_request
from ..services.state import hub_state

bp = Blueprint("kernel", __name__, url_prefix="/api/kernel")

_VALID_QUEUES = frozenset({"high_priority", "normal_priority", "background"})


def _kernel_control_authorized():
    if os.environ.get("AETHERRA_HUB_CONTROL_ENABLED", "0") != "1":
        return jsonify({"error": "disabled"}), 501
    if not os.environ.get("AETHERRA_HUB_CONTROL_TOKEN"):
        return jsonify({"error": "forbidden"}), 403
    decision = authorize_token_request(
        request.headers,
        os.environ.get("AETHERRA_HUB_CONTROL_TOKEN"),
        unauthorized_status=403,
    )
    if decision.allowed:
        return None
    return jsonify({"error": decision.error or "forbidden"}), decision.status_code


def _run_async(value: Any) -> Any:
    if not asyncio.iscoroutine(value):
        return value
    try:
        return asyncio.run(value)
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(value)
                return None
            return loop.run_until_complete(value)
        except Exception:
            return None
    except Exception:
        return None


def _kernel_instance() -> Any | None:
    return registry_client.get_service("kernel_loop")


def _guardian_decision_for_control(
    *,
    action: str,
    purpose: str,
    target: str = "kernel:loop",
    metadata: dict[str, Any] | None = None,
) -> Any:
    requester = _kernel_control_requester()
    return evaluate_intent(
        IntentDeclaration(
            requester=str(requester),
            subsystem="kernel",
            action=action,
            target=target,
            purpose=purpose,
            capabilities=("kernel:control",),
            evidence=(f"kernel_control:{action}",),
            reversible=True,
            rollback_plan="restore previous kernel lifecycle or queue state",
            metadata=metadata or {},
        )
    )


def _kernel_control_requester() -> str:
    return str(request.headers.get("X-Aetherra-Principal") or "hub:kernel_control")


def _call_with_requester(method: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        return method(*args, requester=_kernel_control_requester(), **kwargs)
    except TypeError as exc:
        if "requester" not in str(exc):
            raise
        return method(*args, **kwargs)


def _guardian_block_response(decision):
    if decision.status in {GuardianStatus.ALLOW, GuardianStatus.ALLOW_LIMITED}:
        return None
    status_code = 202 if decision.status == GuardianStatus.REQUIRE_APPROVAL else 403
    return (
        jsonify(
            {
                "ok": False,
                "error": decision.reason,
                "guardian": decision.to_audit_dict(),
            }
        ),
        status_code,
    )


def _get_kernel_or_500() -> tuple[Any | None, Any | None]:
    kernel = _kernel_instance()
    if kernel is None:
        return None, (jsonify({"ok": False, "status": "kernel not registered"}), 500)
    return kernel, None


def _json_no_store(payload: dict[str, Any]):
    response = jsonify(payload)
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/status")
def kernel_status():
    hub_state.incr_requests()
    ks = registry_client.get_kernel_status() or {"running": False}
    return _json_no_store(ks)


@bp.get("/readiness")
def kernel_readiness():
    hub_state.incr_requests()
    ks = registry_client.get_kernel_status()
    return _json_no_store(build_kernel_readiness_payload(ks))


@bp.get("/metrics")
def kernel_metrics():
    hub_state.incr_requests()
    ks = registry_client.get_kernel_status() or {"running": False}
    hmr = registry_client.get_hmr_config_metrics() or {}
    payload = {"hub_ts": datetime.now().isoformat(), "kernel": ks}
    if hmr:
        payload["hmr"] = hmr
    return _json_no_store(payload)


@bp.post("/control/pause")
def kernel_control_pause():
    hub_state.incr_requests()
    auth_error = _kernel_control_authorized()
    if auth_error is not None:
        return auth_error
    decision = _guardian_decision_for_control(
        action="kernel.pause",
        purpose="Pause the Aetherra kernel loop",
        metadata={"operation": "pause"},
    )
    block = _guardian_block_response(decision)
    if block is not None:
        return block
    kernel, error = _get_kernel_or_500()
    if error is not None:
        return error
    try:
        _call_with_requester(kernel.pause)
        return jsonify({"ok": True, "status": "paused"})
    except Exception:
        return jsonify({"ok": False, "status": "server"}), 500


@bp.post("/control/resume")
def kernel_control_resume():
    hub_state.incr_requests()
    auth_error = _kernel_control_authorized()
    if auth_error is not None:
        return auth_error
    decision = _guardian_decision_for_control(
        action="kernel.resume",
        purpose="Resume the Aetherra kernel loop",
        metadata={"operation": "resume"},
    )
    block = _guardian_block_response(decision)
    if block is not None:
        return block
    kernel, error = _get_kernel_or_500()
    if error is not None:
        return error
    try:
        _call_with_requester(kernel.resume)
        return jsonify({"ok": True, "status": "resumed"})
    except Exception:
        return jsonify({"ok": False, "status": "server"}), 500


@bp.post("/control/drain")
def kernel_control_drain():
    hub_state.incr_requests()
    auth_error = _kernel_control_authorized()
    if auth_error is not None:
        return auth_error
    body = request.get_json(silent=True) or {}
    queue_name = str(body.get("queue") or "").strip()
    mode = str(body.get("mode") or "dlq").strip()
    if queue_name not in _VALID_QUEUES:
        return jsonify({"error": "invalid queue"}), 400
    decision = _guardian_decision_for_control(
        action="kernel.drain_queue",
        purpose=f"Drain kernel queue {queue_name}",
        target=f"kernel_queue:{queue_name}",
        metadata={"queue": queue_name, "mode": mode},
    )
    block = _guardian_block_response(decision)
    if block is not None:
        return block
    kernel, error = _get_kernel_or_500()
    if error is not None:
        return error
    try:
        _run_async(
            _call_with_requester(kernel.drain_queue, queue_name, mode=mode)
        )
        return jsonify({"ok": True, "status": f"drained:{queue_name}:{mode}"})
    except Exception:
        return jsonify({"ok": False, "status": "server"}), 500


@bp.post("/control/queue_limits")
def kernel_control_queue_limits():
    hub_state.incr_requests()
    auth_error = _kernel_control_authorized()
    if auth_error is not None:
        return auth_error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "invalid_limits"}), 400
    limits = {str(key): value for key, value in payload.items() if str(key) in _VALID_QUEUES}
    decision = _guardian_decision_for_control(
        action="kernel.set_queue_limits",
        purpose="Set Aetherra kernel queue limits",
        target="kernel:queue_limits",
        metadata={"limit_keys": tuple(sorted(limits))},
    )
    block = _guardian_block_response(decision)
    if block is not None:
        return block
    kernel, error = _get_kernel_or_500()
    if error is not None:
        return error
    try:
        _call_with_requester(kernel.set_queue_limits, limits)
        status = {}
        if hasattr(kernel, "get_status"):
            status = {"queue_limits": kernel.get_status().get("queue_limits", {})}
        return jsonify({"ok": True, "status": status})
    except Exception:
        return jsonify({"ok": False, "status": "server"}), 500
