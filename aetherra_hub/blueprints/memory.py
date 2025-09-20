"""Memory graph blueprint stub.

Returns 501 so tests that allow 200/501 don't fail with 404.
"""

from __future__ import annotations

# Third party imports
from flask import Blueprint, jsonify

bp = Blueprint("memory", __name__)


@bp.get("/api/memory/graph")
def graph():  # pragma: no cover
    return (
        jsonify(
            {
                "ok": False,
                "status": "memory_graph_disabled",
                "detail": "Memory graph endpoint not implemented yet",
            }
        ),
        501,
    )
