"""Interactive Lyrixa API - emotions, expressions, and interactivity status.

Endpoints:
- GET /api/interactive/status - Get current emotion, expression, and system status
- GET /api/interactive/emotion - Get current emotion state
- GET /api/interactive/expression - Get current expression
- POST /api/interactive/trigger - Manually trigger an emotion/expression (admin)
"""

from __future__ import annotations

import logging
import os

from flask import Blueprint, Response, jsonify, request

# Local imports
from ..services.control_auth import authorize_control_request

logger = logging.getLogger(__name__)

bp = Blueprint("interactive", __name__, url_prefix="/api/interactive")


def _get_interactive_system():
    """Get the Interactive Lyrixa system instance."""
    try:
        from Aetherra.lyrixa.interactive import get_interactive_system

        from ..utils.http import run_coro_blocking

        return run_coro_blocking(get_interactive_system())
    except Exception as e:
        logger.warning(f"Failed to get interactive system: {e}")
        return None


@bp.route("/status", methods=["GET"])
def get_status() -> tuple[Response, int]:
    """Get comprehensive Interactive Lyrixa status."""
    interactive_sys = _get_interactive_system()

    if not interactive_sys:
        return jsonify(
            {
                "error": "interactive_system_unavailable",
                "message": "Interactive Lyrixa system is not available",
                "enabled": False,
            }
        ), 503

    try:
        status = interactive_sys.get_status()
        return jsonify(
            {
                "status": "ok",
                "data": status,
            }
        ), 200

    except Exception as e:
        logger.error(f"Error getting interactive status: {e}", exc_info=True)
        return jsonify(
            {
                "error": "status_error",
                "message": str(e),
            }
        ), 500


@bp.route("/emotion", methods=["GET"])
def get_emotion() -> tuple[Response, int]:
    """Get current emotion state."""
    interactive_sys = _get_interactive_system()

    if not interactive_sys:
        return jsonify(
            {
                "error": "interactive_system_unavailable",
                "emotion": None,
            }
        ), 503

    try:
        if not interactive_sys.interactive_loop:
            return jsonify(
                {
                    "emotion": None,
                    "message": "Interactive loop not initialized",
                }
            ), 200

        emotion = interactive_sys.interactive_loop.get_current_emotion()
        return jsonify(
            {
                "emotion": emotion,
            }
        ), 200

    except Exception as e:
        logger.error(f"Error getting emotion: {e}", exc_info=True)
        return jsonify(
            {
                "error": "emotion_error",
                "message": str(e),
            }
        ), 500


@bp.route("/expression", methods=["GET"])
def get_expression() -> tuple[Response, int]:
    """Get current expression state."""
    interactive_sys = _get_interactive_system()

    if not interactive_sys:
        return jsonify(
            {
                "error": "interactive_system_unavailable",
                "expression": None,
            }
        ), 503

    try:
        if not interactive_sys.expression_manager:
            return jsonify(
                {
                    "expression": None,
                    "message": "Expression manager not initialized",
                }
            ), 200

        expression = interactive_sys.expression_manager.get_current_expression()
        return jsonify(
            {
                "expression": expression,
            }
        ), 200

    except Exception as e:
        logger.error(f"Error getting expression: {e}", exc_info=True)
        return jsonify(
            {
                "error": "expression_error",
                "message": str(e),
            }
        ), 500


@bp.route("/metrics", methods=["GET"])
def get_metrics() -> tuple[Response, int]:
    """Get metrics for Prometheus export."""
    interactive_sys = _get_interactive_system()

    if not interactive_sys:
        return jsonify(
            {
                "error": "interactive_system_unavailable",
                "metrics": {},
            }
        ), 503

    try:
        metrics = interactive_sys.get_metrics()
        return jsonify(
            {
                "metrics": metrics,
            }
        ), 200

    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        return jsonify(
            {
                "error": "metrics_error",
                "message": str(e),
            }
        ), 500


def _check_admin_auth() -> tuple[Response, int] | None:
    """Check admin API key. Returns error response if denied, None if allowed.

    Set AETHERRA_ADMIN_KEY env var to require authentication. If not set,
    the endpoint is unrestricted (dev/local mode).
    """
    admin_key = os.environ.get("AETHERRA_ADMIN_KEY", "").strip()
    if not admin_key:
        # No key configured – dev mode, allow all
        return None
    provided = request.headers.get("X-Aetherra-Admin-Key", "").strip()
    if not provided or provided != admin_key:
        return jsonify(
            {"error": "forbidden", "message": "Admin authentication required"}
        ), 403
    return None


def _check_control_auth() -> tuple[Response, int] | None:
    """Authorize interactive mutations using the Hub control-plane policy."""
    decision = authorize_control_request(request.headers, request.remote_addr)
    if decision.allowed:
        return None
    return jsonify({"error": decision.error}), decision.status_code


@bp.route("/trigger", methods=["POST"])
def trigger_emotion() -> tuple[Response, int]:
    """
    Manually trigger an emotion/expression (admin only).

    Body:
    {
        "emotion": "excited",  # or "calm", "curious", "focused", etc.
        "intensity": 0.8,      # 0.0 - 1.0
        "duration": 5.0        # seconds (optional)
    }
    """
    auth_err = _check_control_auth()
    if auth_err is not None:
        return auth_err

    interactive_sys = _get_interactive_system()

    if not interactive_sys:
        return jsonify(
            {
                "error": "interactive_system_unavailable",
            }
        ), 503

    try:
        data = request.get_json() or {}
        emotion = data.get("emotion")
        intensity = data.get("intensity", 0.5)
        duration = data.get("duration", 5.0)

        if not emotion:
            return jsonify(
                {
                    "error": "invalid_request",
                    "message": "emotion is required",
                }
            ), 400

        # Validate intensity
        try:
            intensity = float(intensity)
            if not 0.0 <= intensity <= 1.0:
                raise ValueError("Intensity must be between 0.0 and 1.0")
        except ValueError as e:
            return jsonify(
                {
                    "error": "invalid_intensity",
                    "message": str(e),
                }
            ), 400

        # Publish the emotion via event bus if available
        if interactive_sys.event_bus:
            from ..utils.http import run_coro_blocking

            async def _publish():
                await interactive_sys.event_bus.publish(
                    "lyrixa.emotion.triggered",
                    {
                        "emotion": emotion,
                        "intensity": intensity,
                        "duration": duration,
                        "source": "api_trigger",
                    },
                )

            run_coro_blocking(_publish())

            return jsonify(
                {
                    "status": "ok",
                    "message": f"Triggered {emotion} emotion",
                    "emotion": emotion,
                    "intensity": intensity,
                    "duration": duration,
                }
            ), 200

        return jsonify(
            {
                "error": "event_bus_unavailable",
                "message": "Cannot trigger emotion without event bus",
            }
        ), 503

    except Exception as e:
        logger.error(f"Error triggering emotion: {e}", exc_info=True)
        return jsonify(
            {
                "error": "trigger_error",
                "message": str(e),
            }
        ), 500
