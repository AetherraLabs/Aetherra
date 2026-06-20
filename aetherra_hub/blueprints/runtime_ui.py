"""Runtime UI API for the Aetherra Cognitive Observatory.

This blueprint exposes a read-only state snapshot for future Observatory
renderers. It must not own privileged actions or bypass Guardian/Security.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, make_response, request
from flask.typing import ResponseReturnValue

from Aetherra.runtime_ui import (
    allowed_observatory_modes,
    build_runtime_ui_activity_payload,
    build_runtime_ui_bootstrap_payload,
    build_runtime_ui_contract_validation_payload,
    build_runtime_ui_manifest,
    build_runtime_ui_observatory_payload,
    build_runtime_ui_scene_payload,
    build_runtime_ui_status_payload,
    build_runtime_ui_subsystem_payload,
    bounded_filter_value,
    bounded_user_name,
    parse_limit,
    parse_observatory_mode,
    runtime_ui_subsystem_names,
)

from ..services.state import hub_state

bp = Blueprint("runtime_ui", __name__, url_prefix="/api/runtime-ui")


@bp.get("/manifest")
def runtime_ui_manifest() -> ResponseReturnValue:
    """Return the Runtime UI contract and safety manifest."""

    hub_state.incr_requests()
    response = make_response(
        jsonify({"ok": True, "manifest": build_runtime_ui_manifest()})
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/status")
def runtime_ui_status() -> ResponseReturnValue:
    """Return compact Runtime UI foundation health."""

    hub_state.incr_requests()
    response = make_response(jsonify(build_runtime_ui_status_payload()))
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/bootstrap")
def runtime_ui_bootstrap() -> ResponseReturnValue:
    """Return the first-load Runtime UI payload for Observatory clients."""

    hub_state.incr_requests()
    mode = parse_observatory_mode(request.args.get("mode"))
    if mode is None:
        return _invalid_mode_response()
    limit_result = parse_limit(request.args.get("limit"), default=25)
    if not limit_result.ok:
        return _invalid_limit_response(limit_result.error)

    payload = build_runtime_ui_bootstrap_payload(
        mode=mode,
        user_name=bounded_user_name(request.args.get("user")),
        limit=limit_result.value,
    )
    response = make_response(jsonify(payload))
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/contract/validate")
def runtime_ui_contract_validate() -> ResponseReturnValue:
    """Validate the current Runtime UI bootstrap contract."""

    hub_state.incr_requests()
    mode = parse_observatory_mode(request.args.get("mode"))
    if mode is None:
        return _invalid_mode_response()
    limit_result = parse_limit(request.args.get("limit"), default=25)
    if not limit_result.ok:
        return _invalid_limit_response(limit_result.error)

    payload = build_runtime_ui_contract_validation_payload(
        mode=mode,
        user_name=bounded_user_name(request.args.get("user")),
        limit=limit_result.value,
    )
    response = make_response(jsonify(payload))
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/observatory")
def observatory_snapshot() -> ResponseReturnValue:
    """Return a read-only Cognitive Observatory state snapshot."""

    hub_state.incr_requests()
    mode = parse_observatory_mode(request.args.get("mode"))
    if mode is None:
        return _invalid_mode_response()

    response = make_response(
        jsonify(
            build_runtime_ui_observatory_payload(
                mode,
                user_name=bounded_user_name(request.args.get("user")),
            )
        )
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/subsystems/<subsystem_name>")
def subsystem_snapshot(subsystem_name: str) -> ResponseReturnValue:
    """Return a focused read-only Observatory snapshot for one subsystem."""

    hub_state.incr_requests()
    payload = build_runtime_ui_subsystem_payload(
        subsystem_name,
        user_name=bounded_user_name(request.args.get("user")),
    )
    if payload is None:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "unknown_subsystem",
                    "valid_subsystems": runtime_ui_subsystem_names(),
                }
            ),
            404,
        )

    response = make_response(jsonify(payload))
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/scene")
def observatory_scene() -> ResponseReturnValue:
    """Return renderer-agnostic Cognitive Observatory scene metadata."""

    hub_state.incr_requests()
    mode = parse_observatory_mode(request.args.get("mode"))
    if mode is None:
        return _invalid_mode_response()

    response = make_response(
        jsonify(
            build_runtime_ui_scene_payload(
                mode,
                user_name=bounded_user_name(request.args.get("user")),
            )
        )
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/activity")
def observatory_activity() -> ResponseReturnValue:
    """Return bounded read-only Observatory activity events."""

    hub_state.incr_requests()
    channel = bounded_filter_value(request.args.get("channel"))
    source = bounded_filter_value(request.args.get("source"))
    limit_result = parse_limit(request.args.get("limit"), default=25)
    if not limit_result.ok:
        return _invalid_limit_response(limit_result.error)

    response = make_response(
        jsonify(
            build_runtime_ui_activity_payload(
                channel=channel,
                source=source,
                limit=limit_result.value,
            )
        )
    )
    response.headers["Cache-Control"] = "no-store"
    return response


def _invalid_mode_response() -> ResponseReturnValue:
    return (
        jsonify(
            {
                "ok": False,
                "error": "invalid_mode",
                "allowed_modes": allowed_observatory_modes(),
            }
        ),
        400,
    )


def _invalid_limit_response(error: str | None) -> ResponseReturnValue:
    return jsonify({"ok": False, "error": error or "invalid_limit"}), 400
