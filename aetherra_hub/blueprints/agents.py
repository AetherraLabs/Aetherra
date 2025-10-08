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
    return os.environ.get("AETHERRA_AGENTS_API_ENABLED", "0") == "1"


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
    # Disabled path mirrors other endpoints (501)
    if not _authz_enabled():
        return jsonify({"error": "disabled"}), 501
    # Optional token check
    if _require_token():
        got = request.headers.get("X-Aetherra-Token", "").strip()
        if not got or got != _expected_token():
            return jsonify({"error": "forbidden"}), 403
    # Happy path: surface orchestrator status basics
    return jsonify({"ok": True, "orchestrator": _orchestrator_status()})
