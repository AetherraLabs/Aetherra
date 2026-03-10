from __future__ import annotations

# Standard library imports
import os
from typing import Any

# Third party imports
from flask import Blueprint, jsonify, request

# Local imports
from ..services import registry_client

bp = Blueprint("agents", __name__)


def _authz_enabled() -> bool:
    # Enable by default for development (set to "0" to explicitly disable)
    return os.environ.get("AETHERRA_AGENTS_API_ENABLED", "1") == "1"


def _require_token() -> bool:
    return os.environ.get("AETHERRA_AGENTS_API_REQUIRE_TOKEN", "0") == "1"


def _expected_token() -> str:
    return os.environ.get("AETHERRA_AGENTS_API_TOKEN", "")


def _orchestrator_status() -> dict[str, Any]:
    st = registry_client.get_orchestrator_status() or {}
    # Normalize to a stable schema
    if not isinstance(st, dict):
        return {"total_agents": 0, "pending_tasks": 0}
    return {
        "total_agents": int(st.get("total_agents", 0) or 0),
        "pending_tasks": int(st.get("pending_tasks", 0) or 0),
    }


@bp.get("/api/agents")
def list_agents():
    # If not enabled, return a benign 200 with enabled flag to avoid noisy 501s
    if not _authz_enabled():
        return jsonify(
            {
                "ok": True,
                "enabled": False,
                "agents": [],
                "orchestrator": _orchestrator_status(),
            }
        ), 200
    # Optional token check
    if _require_token():
        got = request.headers.get("X-Aetherra-Token", "").strip()
        if not got or got != _expected_token():
            return jsonify({"error": "forbidden"}), 403
    # Fetch registered agents from orchestrator
    agents = registry_client.get_registered_agents()
    # Optional capability filter: ?capability=data-processing
    cap_filter = request.args.get("capability", "").strip().lower()
    if cap_filter and agents:
        agents = [
            a for a in agents
            if any(cap_filter in str(c).lower() for c in a.get("capabilities", []))
        ]
    # Optional status filter: ?status=idle
    status_filter = request.args.get("status", "").strip().lower()
    if status_filter and agents:
        agents = [
            a for a in agents
            if str(a.get("status", "")).lower() == status_filter
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
        return jsonify({"ok": False, "error": "agents_api_disabled"}), 400
    if _require_token():
        got = request.headers.get("X-Aetherra-Token", "").strip()
        if not got or got != _expected_token():
            return jsonify({"error": "forbidden"}), 403
    agents = registry_client.get_registered_agents()
    match = next((a for a in agents if str(a.get("agent_id", "")) == agent_id), None)
    if not match:
        return jsonify({"ok": False, "error": "agent_not_found"}), 404
    return jsonify({"ok": True, "agent": match}), 200


@bp.get("/api/agents/<agent_id>/status")
def get_agent_status(agent_id: str):
    """Get health/status for a specific agent."""
    if not _authz_enabled():
        return jsonify({"ok": False, "error": "agents_api_disabled"}), 400
    if _require_token():
        got = request.headers.get("X-Aetherra-Token", "").strip()
        if not got or got != _expected_token():
            return jsonify({"error": "forbidden"}), 403
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


@bp.post("/api/tasks")
def submit_task():
    """Submit a task to the agent orchestrator."""
    # Check if agents API is enabled
    if not _authz_enabled():
        return jsonify({"ok": False, "error": "agents_api_disabled"}), 400

    # Optional token check
    if _require_token():
        got = request.headers.get("X-Aetherra-Token", "").strip()
        if not got or got != _expected_token():
            return jsonify({"error": "forbidden"}), 403

    # Get task data from request
    payload = request.get_json(silent=True) or {}

    # Validate required fields
    name = payload.get("name", "").strip()
    description = payload.get("description", "").strip()

    if not name:
        return jsonify({"ok": False, "error": "missing_name"}), 400

    # Submit task via registry client
    task_id = registry_client.submit_agent_task(
        name=name,
        description=description,
        required_capabilities=payload.get("required_capabilities", []),
        input_data=payload.get("input_data", {}),
        priority=payload.get("priority", "normal"),
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
        return jsonify({"ok": False, "error": "agents_api_disabled"}), 400

    # Optional token check
    if _require_token():
        got = request.headers.get("X-Aetherra-Token", "").strip()
        if not got or got != _expected_token():
            return jsonify({"error": "forbidden"}), 403

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
        return jsonify({"ok": False, "error": "agents_api_disabled"}), 400

    # Optional token check
    if _require_token():
        got = request.headers.get("X-Aetherra-Token", "").strip()
        if not got or got != _expected_token():
            return jsonify({"error": "forbidden"}), 403

    # Get task status via registry client
    status = registry_client.get_agent_task_status(task_id)

    if not status:
        return jsonify({"ok": False, "error": "task_not_found"}), 404

    return jsonify({"ok": True, "task": status}), 200
