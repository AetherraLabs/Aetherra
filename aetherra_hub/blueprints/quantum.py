"""Quantum status blueprint.

Provides /api/quantum/status returning a minimal JSON payload used by capability tests.
The legacy monolith exposed richer quantum / memory coherence information; here we
return a lightweight snapshot and leave TODO hooks for future expansion.
"""

from __future__ import annotations

# Third party imports
from flask import Blueprint, jsonify

bp = Blueprint("quantum", __name__)


@bp.get("/api/quantum/status")
def quantum_status():  # pragma: no cover - exercised via capability tests
    # Minimal fields required by tests: available, backend
    # Future: add coherence metrics, branch counts, etc.
    payload = {
        "available": True,  # always True for now (no real backend wired)
        "backend": "simulated",
    }
    return jsonify(payload), 200
