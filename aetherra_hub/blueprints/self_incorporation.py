"""Self-Incorporation API endpoints.

Provides HTTP API for Aetherra OS self-incorporation system.
Enables external tools to trigger discovery, classification, security evaluation,
planning, and integration of the OS codebase.
"""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from ..services.registry_client import get_service

logger = logging.getLogger(__name__)

bp = Blueprint("self_incorporation", __name__, url_prefix="/api/selfinc")


@bp.get("/status")
def get_status():
    """Get self-incorporation system status."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify(
                {
                    "status": "disabled",
                    "running": False,
                    "error": "Self-incorporation service not registered",
                }
            ), 503

        # Get status from the service
        import asyncio

        loop = asyncio.get_event_loop()
        status = loop.run_until_complete(selfinc_service.get_status())

        return jsonify(status)
    except Exception as e:
        logger.error(f"[SELFINC] Status error: {e}")
        return jsonify({"status": "error", "running": False, "error": str(e)}), 500


@bp.post("/scan")
def trigger_scan():
    """Trigger partial or full codebase scan."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        # Get optional path filter from request
        data = request.get_json() or {}
        root_filter = data.get("path")

        import asyncio

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(selfinc_service.trigger_scan(root_filter))

        return jsonify(result)
    except Exception as e:
        logger.error(f"[SELFINC] Scan error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.post("/apply")
def apply_plan():
    """Apply plan actions (subset or all)."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        # Get optional filters from request
        data = request.get_json() or {}
        dry_run = data.get("dry_run", False)

        import asyncio

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            selfinc_service.trigger_integrate(dry_run=dry_run)
        )

        return jsonify(result)
    except Exception as e:
        logger.error(f"[SELFINC] Apply error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.post("/rollback")
def rollback():
    """Rollback integration by rollback token."""
    try:
        data = request.get_json() or {}
        rb_token = data.get("rb_token")

        if not rb_token:
            return jsonify({"error": "rollback token required"}), 400

        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        import asyncio

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(selfinc_service.trigger_rollback(rb_token))

        if result.get("ok"):
            return jsonify(result)

        return jsonify(result), 400

    except Exception as e:
        logger.error(f"[SELFINC] Rollback error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.get("/audit")
def get_audit():
    """Get audit records with optional filtering."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        # Get query parameters
        limit = request.args.get("limit", 50, type=int)
        action_filter = request.args.get("action")
        status_filter = request.args.get("status")

        import asyncio

        loop = asyncio.get_event_loop()

        # Get audit summary with filters
        summary = loop.run_until_complete(
            selfinc_service.get_audit_summary(
                action_filter=action_filter, status_filter=status_filter
            )
        )

        return jsonify(
            {
                "audit_summary": summary,
                "filters": {
                    "action": action_filter,
                    "status": status_filter,
                    "limit": limit,
                },
            }
        )
    except Exception as e:
        logger.error(f"[SELFINC] Audit error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.get("/metrics")
def get_metrics():
    """Get self-incorporation metrics for monitoring."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify(
                {
                    "aetherra_selfinc_service_available": 0,
                    "aetherra_selfinc_service_status": "unavailable",
                }
            )

        import asyncio

        loop = asyncio.get_event_loop()
        status = loop.run_until_complete(selfinc_service.get_status())

        # Convert status to Prometheus-style metrics
        metrics = {
            "aetherra_selfinc_service_available": 1 if status.get("running") else 0,
            "aetherra_selfinc_service_status": status.get("status", "unknown"),
            "aetherra_selfinc_files_discovered": status.get("files_by_type", {}).get(
                "total", 0
            ),
            "aetherra_selfinc_last_scan_duration": status.get("last_scan", {}).get(
                "duration", 0
            ),
        }

        # Add file type distribution
        files_by_type = status.get("files_by_type", {})
        for file_type, count in files_by_type.items():
            if file_type != "total":
                metrics[f"aetherra_selfinc_files_{file_type}"] = count

        return jsonify(metrics)
    except Exception as e:
        logger.error(f"[SELFINC] Metrics error: {e}")
        return jsonify(
            {
                "aetherra_selfinc_service_available": 0,
                "aetherra_selfinc_service_error": str(e),
            }
        )


@bp.get("/ethics/overview")
def get_ethics_overview():
    """Get high-level ethics dashboard overview."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        # Get recent audit records with ethics scores
        ethics_threshold = float(request.args.get("threshold", "0.6"))

        # TODO: Add method to audit ledger to get recent records with ethics
        # For now, return basic metrics

        return jsonify(
            {
                "ethics_enabled": hasattr(selfinc_service, "ethics_engine"),
                "ethics_threshold": ethics_threshold,
                "recent_decisions": {
                    "approved": 0,  # TODO: Count from audit ledger
                    "denied": 0,  # TODO: Count from audit ledger
                    "total": 0,  # TODO: Count from audit ledger
                },
                "risk_assessment": {
                    "high_risk_actions": 0,  # TODO: Count high-risk items
                    "medium_risk_actions": 0,  # TODO: Count medium-risk items
                    "low_risk_actions": 0,  # TODO: Count low-risk items
                },
                "framework_weights": selfinc_service.ethics_engine._load_ethics_profile(),
            }
        )

    except Exception as e:
        logger.error(f"[SELFINC] Ethics overview error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.post("/ethics/evaluate")
def evaluate_ethics():
    """Evaluate ethics for a specific action or plan."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        if not hasattr(selfinc_service, "ethics_engine"):
            return jsonify({"error": "Ethics engine not available"}), 503

        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400

        action = data.get("action", "unknown")
        target = data.get("target", {})

        # Get safety decision if file_id provided
        safety_decision = None
        file_id = target.get("file_id")
        if file_id and hasattr(selfinc_service, "safety_index"):
            safety_decision = selfinc_service.safety_index.get_decision(file_id)

        # Evaluate ethics
        ethics_score = selfinc_service.ethics_engine.evaluate_integration(
            action, target, safety_decision
        )

        return jsonify(
            {
                "overall_score": ethics_score.overall_score,
                "utilitarian_score": ethics_score.utilitarian_score,
                "deontological_score": ethics_score.deontological_score,
                "virtue_score": ethics_score.virtue_score,
                "care_score": ethics_score.care_score,
                "confidence": ethics_score.confidence,
                "reasoning": ethics_score.reasoning,
                "risk_factors": ethics_score.risk_factors,
                "ethical_benefits": ethics_score.ethical_benefits,
                "evaluation_timestamp": "2024-01-01T00:00:00Z",  # TODO: Add timestamp
            }
        )

    except Exception as e:
        logger.error(f"[SELFINC] Ethics evaluation error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.get("/ethics/audit/<string:trace_id>")
def get_ethics_audit(trace_id: str):
    """Get detailed ethics audit for a specific integration."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        # TODO: Implement audit record lookup by trace_id in audit ledger
        # For now, return placeholder

        return jsonify(
            {
                "trace_id": trace_id,
                "status": "not_implemented",
                "message": "Audit record lookup not yet implemented",
            }
        )

    except Exception as e:
        logger.error(f"[SELFINC] Ethics audit error: {e}")
        return jsonify({"error": str(e)}), 500
