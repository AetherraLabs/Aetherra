"""Quantum status blueprint.

Provides:
  - GET /api/quantum/status  - minimal status (capability-test compat)
  - GET /api/quantum/snapshot - rich snapshot with coherence metrics, bridge info
"""

from __future__ import annotations

from datetime import datetime, timezone

# Third party imports
from flask import Blueprint, jsonify

bp = Blueprint("quantum", __name__)


@bp.get("/api/quantum/status")
def quantum_status():  # pragma: no cover - exercised via capability tests
    # Minimal fields required by tests: available, backend
    payload = {
        "available": True,
        "backend": "simulated",
    }
    return jsonify(payload), 200


@bp.get("/api/quantum/snapshot")
def quantum_snapshot():
    """Get comprehensive quantum system snapshot with coherence and bridge metrics."""
    from ..services import registry_client

    q_status = registry_client.get_memory_quantum_status()

    payload = {
        "available": True,
        "backend": "simulated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "coherence": {
            "level": float(q_status.get("coherence_level", 1.0)),
            "stable": bool(q_status.get("stable", True)),
            "branch_count": int(q_status.get("branch_count", 0)),
        },
        "bridge_status": {
            "enabled": bool(q_status.get("enabled", False)),
            "ephemeral": bool(q_status.get("ephemeral", True)),
        },
        "memory": {
            "total_memories": int(q_status.get("total_memories", 0)),
        },
    }
    return jsonify(payload), 200
