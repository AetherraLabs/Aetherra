"""Authenticated federation peer management endpoints."""

from __future__ import annotations

import os
from urllib.parse import urlparse

from flask import Blueprint, jsonify, request

from Aetherra.hub.federation import get_federation_manager
from Aetherra.security.net_policy import is_domain_allowed

from ..services.control_auth import authorize_control_request

bp = Blueprint("peers", __name__)


def _authorize():
    decision = authorize_control_request(request.headers, request.remote_addr)
    if decision.allowed:
        return None
    return jsonify({"ok": False, "error": decision.error}), decision.status_code


def _federation_enabled() -> bool:
    return os.environ.get("AETHERRA_FEDERATION_ENABLED", "0") == "1"


def _valid_peer_url(value: object) -> str | None:
    if not isinstance(value, str) or len(value) > 2_048:
        return None
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        return None
    normalized = value.strip().rstrip("/")
    if not is_domain_allowed(normalized, "hub:federation:register"):
        return None
    return normalized


@bp.get("/api/peers")
def list_peers():
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    return jsonify({"ok": True, "peers": get_federation_manager().list_peers()}), 200


@bp.post("/api/peers")
def add_peer():
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "invalid_json_object"}), 400
    peer_url = _valid_peer_url(payload.get("url"))
    if peer_url is None:
        return jsonify({"ok": False, "error": "invalid_or_denied_peer_url"}), 400
    manager = get_federation_manager()
    manager.add_peer(peer_url)
    return jsonify({"ok": True, "peer": peer_url}), 200


@bp.post("/api/peers/announce")
def announce():
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    if not _federation_enabled():
        return jsonify({"ok": False, "status": "federation_disabled"}), 501
    get_federation_manager().announce_once()
    return jsonify({"ok": True}), 200


@bp.post("/api/peers/sync")
def sync():
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    if not _federation_enabled():
        return jsonify({"ok": False, "status": "federation_disabled"}), 501
    get_federation_manager().sync_once()
    return jsonify({"ok": True}), 200
