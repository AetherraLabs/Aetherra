"""Policy endpoints: expose current disclosure tier and notes for UI.

Lightweight, no auth, read-only. Safe to include in free tier builds.
"""

from __future__ import annotations

# Third party imports
from flask import Blueprint, jsonify

# Aetherra imports
try:  # pragma: no cover - optional import resilience
    from Aetherra.core import disclosure_policy as dp  # type: ignore
except Exception:  # pragma: no cover
    dp = None  # type: ignore

bp = Blueprint("policy", __name__)


@bp.get("/api/policy/disclosure")
def get_disclosure_policy():
    tier = "free"
    allow_reflection = False
    allow_integration = False
    if dp is not None:
        try:
            tier = dp.get_tier()
            allow_reflection = dp.allow_reflection()
            allow_integration = dp.allow_integration()
        except Exception:  # pragma: no cover
            pass
    notes = {
        "free": "Observation Layer: metadata-only, no code or patches displayed.",
        "reflect": "Reflection Layer: structured descriptions, still no raw patches.",
        "integrate": "Integration Layer: full capability and disclosure.",
    }
    return jsonify(
        {
            "tier": tier,
            "allow_reflection": allow_reflection,
            "allow_integration": allow_integration,
            "note": notes.get(tier, ""),
        }
    )
