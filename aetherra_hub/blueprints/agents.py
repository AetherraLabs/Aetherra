from __future__ import annotations

# Standard library imports
import json
import os
import time
from typing import Any

# Third party imports
from flask import Blueprint, Response, jsonify, request

from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

# Local imports
from ..services import registry_client
from ..services.control_auth import (
    authorize_control_request,
    authorize_token_request,
)

bp = Blueprint("agents", __name__)


def _authz_enabled() -> bool:
    return os.environ.get("AETHERRA_AGENTS_API_ENABLED", "0") == "1"


def _require_token() -> bool:
    return os.environ.get("AETHERRA_AGENTS_API_REQUIRE_TOKEN", "0") == "1"


def _expected_token() -> str:
    return os.environ.get("AETHERRA_AGENTS_API_TOKEN") or os.environ.get(
        "AETHERRA_HUB_CONTROL_TOKEN", ""
    )


def _authorize(*, privileged: bool = False):
    if _require_token():
        decision = authorize_token_request(
            request.headers,
            _expected_token(),
            missing_configuration_error="agents_token_not_configured",
            unauthorized_status=403,
        )
    elif privileged:
        decision = authorize_control_request(request.headers, request.remote_addr)
    else:
        return None
    if decision.allowed:
        return None
    return jsonify({"ok": False, "error": decision.error}), decision.status_code


def _orchestrator_status() -> dict[str, Any]:
    st = registry_client.get_orchestrator_status() or {}
    # Normalize to a stable schema
    if not isinstance(st, dict):
        return {"total_agents": 0, "pending_tasks": 0}
    return {
        "total_agents": int(st.get("total_agents", 0) or 0),
        "pending_tasks": int(st.get("pending_tasks", 0) or 0),
    }


def _disabled_response():
    return jsonify({"ok": False, "error": "disabled"}), 501


def _guardian_decision_for_task(
    *,
    name: str,
    description: str,
    required_capabilities: list[str],
    input_data: dict[str, Any],
    priority: str,
):
    requester = request.headers.get("X-Aetherra-Principal") or "hub:agents_api"
    capabilities = ["agent:execute", *required_capabilities]
    return evaluate_intent(
        IntentDeclaration(
            requester=str(requester),
            subsystem="agent_orchestrator",
            action="agent.execute_task",
            target=f"agent_task:{name}",
            purpose=description or f"Submit agent task {name}",
            capabilities=tuple(capabilities),
            evidence=(f"agent_task:{name}",),
            reversible=True,
            rollback_plan="cancel queued task or stop task before side effects",
            metadata={
                "priority": priority,
                "required_capabilities": tuple(required_capabilities),
                "input_keys": tuple(sorted(str(key) for key in input_data)),
            },
        )
    )


def _guardian_task_block_response(decision) -> tuple[dict[str, Any], int] | None:
    if decision.status in {GuardianStatus.ALLOW, GuardianStatus.ALLOW_LIMITED}:
        return None
    status_code = 202 if decision.status == GuardianStatus.REQUIRE_APPROVAL else 403
    return (
        {
            "ok": False,
            "error": decision.reason,
            "guardian": decision.to_audit_dict(),
        },
        status_code,
    )


@bp.get("/api/agents")
def list_agents():
    # If not enabled, return a benign 200 with enabled flag to avoid noisy 501s
    if not _authz_enabled():
        return _disabled_response()
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    # Fetch registered agents from orchestrator
    agents = registry_client.get_registered_agents()
    # Optional capability filter: ?capability=data-processing
    cap_filter = request.args.get("capability", "").strip().lower()
    if cap_filter and agents:
        agents = [
            a
            for a in agents
            if any(cap_filter in str(c).lower() for c in a.get("capabilities", []))
        ]
    # Optional status filter: ?status=idle
    status_filter = request.args.get("status", "").strip().lower()
    if status_filter and agents:
        agents = [
            a for a in agents if str(a.get("status", "")).lower() == status_filter
        ]
    return jsonify(
        {
            "ok": True,
            "enabled": True,
            "agents": agents,
            "count": len(agents),
            "orchestrator": _orchestrator_status(),
        }
    )


@bp.get("/api/agents/<agent_id>")
def get_agent(agent_id: str):
    """Get details for a specific agent."""
    if not _authz_enabled():
        return _disabled_response()
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    agents = registry_client.get_registered_agents()
    match = next((a for a in agents if str(a.get("agent_id", "")) == agent_id), None)
    if not match:
        return jsonify({"ok": False, "error": "agent_not_found"}), 404
    return jsonify({"ok": True, "agent": match}), 200


@bp.get("/api/agents/<agent_id>/status")
def get_agent_status(agent_id: str):
    """Get health/status for a specific agent."""
    if not _authz_enabled():
        return _disabled_response()
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    agents = registry_client.get_registered_agents()
    match = next((a for a in agents if str(a.get("agent_id", "")) == agent_id), None)
    if not match:
        return jsonify({"ok": False, "error": "agent_not_found"}), 404
    return jsonify(
        {
            "ok": True,
            "agent_id": agent_id,
            "status": match.get("status", "unknown"),
            "capabilities": match.get("capabilities", []),
        }
    ), 200


@bp.get("/api/agents/metrics")
def get_agent_metrics():
    if not _authz_enabled():
        return _disabled_response()
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    return jsonify({"ok": True, "metrics": _orchestrator_status()}), 200


@bp.post("/api/agents/evaluate")
def evaluate_agents():
    if not _authz_enabled():
        return _disabled_response()
    auth_error = _authorize(privileged=True)
    if auth_error is not None:
        return auth_error
    plan = request.get_json(silent=True)
    if not isinstance(plan, dict):
        return jsonify({"ok": False, "error": "invalid_json_object"}), 400
    report = registry_client.run_agent_evaluation(plan)
    if report is None:
        return jsonify({"ok": False, "error": "evaluation_unavailable"}), 503
    return jsonify({"ok": True, "report": report}), 200


@bp.get("/api/agents/evaluation")
def get_agent_evaluation():
    if not _authz_enabled():
        return _disabled_response()
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    return jsonify(
        {"ok": True, "report": registry_client.get_last_agent_evaluation()}
    ), 200


@bp.post("/api/tasks")
def submit_task():
    """Submit a task to the agent orchestrator."""
    # Check if agents API is enabled
    if not _authz_enabled():
        return _disabled_response()

    auth_error = _authorize(privileged=True)
    if auth_error is not None:
        return auth_error

    # Get task data from request
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "invalid_json_object"}), 400

    # Validate required fields
    name = str(payload.get("name") or "").strip()
    description = str(payload.get("description") or "").strip()

    if not name:
        return jsonify({"ok": False, "error": "missing_name"}), 400
    if len(name) > 128 or len(description) > 4096:
        return jsonify({"ok": False, "error": "task_metadata_too_large"}), 413
    required_capabilities = payload.get("required_capabilities", [])
    input_data = payload.get("input_data", {})
    if not isinstance(required_capabilities, list) or not all(
        isinstance(item, str) for item in required_capabilities
    ):
        return jsonify({"ok": False, "error": "invalid_required_capabilities"}), 400
    if len(required_capabilities) > 64 or not isinstance(input_data, dict):
        return jsonify({"ok": False, "error": "invalid_task_input"}), 400

    # Submit task via registry client
    priority = str(payload.get("priority") or "normal").lower()
    if priority not in {"low", "normal", "high", "critical"}:
        return jsonify({"ok": False, "error": "invalid_priority"}), 400

    guardian_decision = _guardian_decision_for_task(
        name=name,
        description=description,
        required_capabilities=required_capabilities,
        input_data=input_data,
        priority=priority,
    )
    guardian_block = _guardian_task_block_response(guardian_decision)
    if guardian_block is not None:
        body, status_code = guardian_block
        return jsonify(body), status_code

    engine_data = (
        payload.get("data") if isinstance(payload.get("data"), dict) else input_data
    )
    task_id = registry_client.execute_agent_task(name, engine_data, priority)
    if task_id is None:
        task_id = registry_client.submit_agent_task(
            name=name,
            description=description,
            required_capabilities=required_capabilities,
            input_data=input_data,
            priority=priority,
            max_execution_time=payload.get("max_execution_time", 300),
        )

    if not task_id:
        return jsonify({"ok": False, "error": "task_submission_failed"}), 500

    return jsonify({"ok": True, "task_id": task_id}), 200


@bp.get("/api/tasks")
def list_tasks():
    """Get a list of recent tasks."""
    # Check if agents API is enabled
    if not _authz_enabled():
        return _disabled_response()

    # Optional token check
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error

    # Get query parameters
    limit = request.args.get("limit", 50, type=int)
    include_completed = request.args.get("include_completed", "true").lower() == "true"

    # Clamp limit to reasonable range
    limit = max(1, min(limit, 200))

    # Get task list via registry client
    tasks = registry_client.get_agent_task_list(
        limit=limit, include_completed=include_completed
    )

    return jsonify({"ok": True, "tasks": tasks, "count": len(tasks)}), 200


@bp.get("/api/tasks/<task_id>")
def get_task_status(task_id: str):
    """Get the status of a specific task."""
    # Check if agents API is enabled
    if not _authz_enabled():
        return _disabled_response()

    # Optional token check
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error

    # Get task status via registry client
    status = registry_client.get_agent_task_status(task_id)

    if not status:
        return jsonify({"ok": False, "error": "task_not_found"}), 404

    return jsonify({"ok": True, "status": status}), 200


def _sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'))}\n\n"


@bp.post("/api/tasks/<task_id>/stream")
def stream_task_status(task_id: str):
    if (
        not _authz_enabled()
        or os.environ.get("AETHERRA_AGENTS_API_STREAM", "0") != "1"
    ):
        return _disabled_response()
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    try:
        poll_seconds = max(
            0.05,
            min(
                float(os.environ.get("AETHERRA_AGENTS_STREAM_POLL_MS", "200")) / 1000,
                2.0,
            ),
        )
    except ValueError:
        poll_seconds = 0.2

    def generate():
        yield _sse("status", {"phase": "start", "task_id": task_id})
        yield _sse("token", {"required": _require_token(), "ok": True})
        last_status: dict[str, Any] | None = None
        for _ in range(20):
            status = registry_client.get_agent_task_status(task_id)
            if status and status != last_status:
                yield _sse("update", {"task_id": task_id, "status": status})
                last_status = status
            state = str((status or {}).get("state", "")).lower()
            progress = float((status or {}).get("progress", 0) or 0)
            if (
                state in {"done", "complete", "completed", "failed", "cancelled"}
                or progress >= 100
            ):
                break
            time.sleep(poll_seconds)
        final_status = (
            registry_client.get_agent_task_status(task_id) or last_status or {}
        )
        yield _sse("final", {"ok": True, "task_id": task_id, "status": final_status})

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
