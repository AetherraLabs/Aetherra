"""Security endpoints for Lyrixa GUI.

Endpoints:
- GET /api/security/policy -> current policy snapshot (caps, network, dp, flags)
"""

from __future__ import annotations

# Third party imports
from flask import Blueprint, jsonify

# Local imports
from ..services.security import policy_snapshot

bp = Blueprint("security", __name__, url_prefix="/api/security")


@bp.get("/policy")
def get_policy():
    pol = policy_snapshot()
    return jsonify(pol)
