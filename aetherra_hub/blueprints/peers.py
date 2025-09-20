"""Federation peers blueprint stub.

Exposes /api/peers/announce returning 501 so capability tests that allow
either 200 (implemented) or 501 (not implemented) pass without 404.
"""

from __future__ import annotations

# Third party imports
from flask import Blueprint, jsonify

bp = Blueprint("peers", __name__)


@bp.post("/api/peers/announce")
def announce():  # pragma: no cover - exercised in capability test
    return (
        jsonify(
            {
                "ok": False,
                "status": "federation_disabled",
                "detail": "Peer federation not implemented yet",
            }
        ),
        501,
    )


@bp.post("/api/peers/sync")
def sync():  # pragma: no cover - exercised in capability test
    return (
        jsonify(
            {
                "ok": False,
                "status": "federation_disabled",
                "detail": "Peer sync not implemented yet",
            }
        ),
        501,
    )
