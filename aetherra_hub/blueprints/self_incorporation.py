"""Self-Incorporation API endpoints.

Provides HTTP API for Aetherra OS self-incorporation system.
Enables external tools to trigger discovery, classification, security evaluation,
planning, and integration of the OS codebase.
"""

from __future__ import annotations

# Standard library imports
import asyncio
import hashlib
import logging
import threading
from collections.abc import Awaitable
from typing import Any, TypeVar

# Third party imports
from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

# Local imports
from ..services.control_auth import authorize_control_request
from ..services.registry_client import get_service

# Aetherra imports
try:
    from Aetherra.core import disclosure_policy  # type: ignore
except Exception:  # pragma: no cover - defensive import fallback
    disclosure_policy = None  # type: ignore

logger = logging.getLogger(__name__)

bp = Blueprint("self_incorporation", __name__, url_prefix="/api/selfinc")

T = TypeVar("T")


def _run_async(coro: Awaitable[T]) -> T:
    """Run an async service call from Flask's synchronous request handlers."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict[str, T] = {}
    error: dict[str, BaseException] = {}

    def _runner() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except BaseException as exc:  # pragma: no cover - surfaced to caller
            error["value"] = exc

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join()

    if error:
        raise error["value"]
    return result["value"]


def _authorize_control() -> ResponseReturnValue | None:
    decision = authorize_control_request(request.headers, request.remote_addr)
    if decision.allowed:
        return None
    return jsonify({"ok": False, "error": decision.error}), decision.status_code


def _hash_audit_value(value: Any) -> str:
    """Return a bounded hash for values that should not be echoed through Hub."""

    raw = json_safe_repr(value).encode("utf-8", errors="replace")
    return hashlib.sha256(raw).hexdigest()[:16]


def json_safe_repr(value: Any) -> str:
    """Build a deterministic compact representation for audit hashing."""

    try:
        import json

        return json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    except Exception:
        return str(value)


def _safe_key_list(mapping: dict[str, Any], *, limit: int = 20) -> list[str]:
    return sorted(str(key) for key in mapping.keys())[:limit]


def _audit_target_summary(action: str, target: dict[str, Any]) -> dict[str, Any]:
    """Summarize an ethics target without exposing raw private identifiers."""

    summary: dict[str, Any] = {
        "action": str(action or "unknown"),
        "target_keys": _safe_key_list(target),
    }
    for field in ("file_id", "plan_id", "name", "path"):
        if target.get(field):
            summary[f"{field}_hash"] = _hash_audit_value(target.get(field))

    capabilities = target.get("declared_capabilities")
    if isinstance(capabilities, list):
        summary["declared_capability_count"] = len(capabilities)
        summary["declared_capability_hashes"] = [
            _hash_audit_value(capability) for capability in capabilities[:20]
        ]

    if "complexity_score" in target:
        try:
            summary["complexity_score"] = float(target.get("complexity_score") or 0.0)
        except (TypeError, ValueError):
            summary["complexity_score_hash"] = _hash_audit_value(
                target.get("complexity_score")
            )
    return summary


def _audit_result_summary(result: Any) -> dict[str, Any]:
    """Summarize an audit result for Hub readback."""

    if not isinstance(result, dict):
        return {"value_hash": _hash_audit_value(result)}

    summary: dict[str, Any] = {}
    for key, value in result.items():
        key_text = str(key)
        if key_text in {
            "overall_score",
            "utilitarian_score",
            "deontological_score",
            "virtue_score",
            "care_score",
            "confidence",
            "risk_level",
            "rollback_token_count",
        }:
            summary[key_text] = value
        elif isinstance(value, list):
            summary[f"{key_text}_count"] = len(value)
            summary[f"{key_text}_hashes"] = [
                _hash_audit_value(item) for item in value[:20]
            ]
        elif isinstance(value, dict):
            summary[f"{key_text}_keys"] = _safe_key_list(value)
            summary[f"{key_text}_hash"] = _hash_audit_value(value)
        else:
            summary[f"{key_text}_hash"] = _hash_audit_value(value)
    return summary


@bp.get("/status")
def get_status() -> ResponseReturnValue:
    """Get self-incorporation system status."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return (
                jsonify(
                    {
                        "status": "disabled",
                        "running": False,
                        "error": "Self-incorporation service not registered",
                    }
                ),
                503,
            )

        status = _run_async(selfinc_service.get_status())

        if disclosure_policy and disclosure_policy.is_free():
            status = disclosure_policy.redact_payload(status)
        return jsonify(status)
    except Exception as e:
        logger.error(f"[SELFINC] Status error: {e}")
        return (
            jsonify(
                {"status": "error", "running": False, "error": "Internal server error"}
            ),
            500,
        )


@bp.post("/scan")
def trigger_scan() -> ResponseReturnValue:
    """Trigger partial or full codebase scan."""
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        # Get optional path filter from request
        data = request.get_json() or {}
        root_filter = data.get("path")

        result = _run_async(selfinc_service.trigger_scan(root_filter))

        if disclosure_policy and disclosure_policy.is_free():
            result = disclosure_policy.redact_payload(result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"[SELFINC] Scan error: {e}")
        return jsonify({"error": "Failed to trigger scan"}), 500


@bp.post("/apply")
def apply_plan() -> ResponseReturnValue:
    """Apply plan actions (subset or all)."""
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        # Get optional filters from request
        data = request.get_json() or {}
        dry_run = data.get("dry_run", False)
        requester = (
            request.headers.get("X-Aetherra-Principal")
            or request.headers.get("X-Principal")
            or "hub:self_incorporation"
        )
        approval_id = data.get("guardian_approval_id")

        # Disclosure policy: block integration in free tier; allow reflective dry-run with redaction
        if disclosure_policy and disclosure_policy.is_free() and not dry_run:
            return jsonify(disclosure_policy.deny_message("apply_plan")), 403

        result = _run_async(
            selfinc_service.trigger_integrate(
                dry_run=dry_run,
                requester=requester,
                approval_id=approval_id,
            )
        )

        if disclosure_policy and disclosure_policy.is_free():
            result = disclosure_policy.redact_payload(result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"[SELFINC] Apply error: {e}")
        return jsonify({"error": "Failed to apply plan"}), 500


@bp.post("/rollback")
def rollback() -> ResponseReturnValue:
    """Rollback integration by rollback token."""
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        data = request.get_json() or {}
        rb_token = data.get("rb_token")

        if not rb_token:
            return jsonify({"error": "rollback token required"}), 400

        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        # Disclosure policy: rollback implies integration capability; block in free tier
        if disclosure_policy and disclosure_policy.is_free():
            return jsonify(disclosure_policy.deny_message("rollback")), 403

        requester = (
            request.headers.get("X-Aetherra-Principal")
            or request.headers.get("X-Principal")
            or "hub:self_incorporation"
        )
        approval_id = data.get("guardian_approval_id")
        result = _run_async(
            selfinc_service.trigger_rollback(
                rb_token,
                requester=requester,
                approval_id=approval_id,
            )
        )

        if result.get("ok"):
            return jsonify(result)

        return jsonify(result), 400

    except Exception as e:
        logger.error(f"[SELFINC] Rollback error: {e}")
        return jsonify({"error": "Rollback operation failed"}), 500


@bp.get("/audit")
def get_audit() -> ResponseReturnValue:
    """Get audit records with optional filtering."""
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        # Get query parameters
        limit = request.args.get("limit", 50, type=int)
        action_filter = request.args.get("action")
        status_filter = request.args.get("status")

        summary = _run_async(
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
def get_metrics() -> ResponseReturnValue:
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

        status = _run_async(selfinc_service.get_status())

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
def get_ethics_overview() -> ResponseReturnValue:
    """Get high-level ethics dashboard overview (instrumented)."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503
        ethics_threshold = float(request.args.get("threshold", "0.6"))
        stats = {}
        recent = []
        try:
            stats = selfinc_service.audit_ledger.ethics_stats()
            recent = selfinc_service.audit_ledger.recent(limit=25)
        except Exception as e:  # pragma: no cover
            logger.debug(f"[SELFINC][ETHICS] Stats error: {e}")
            stats = {}
        defaults = {
            "total_decisions": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "avg_score": 0.0,
        }
        for k, v in defaults.items():
            stats.setdefault(k, v)
        approved = sum(
            1
            for r in recent
            if r.get("action") == "integration_plan" and r.get("status") == "applied"
        )
        denied = sum(
            1
            for r in recent
            if r.get("action") == "integration_plan"
            and r.get("status") in {"denied", "ethics_blocked"}
        )
        risk_assessment = {
            "high_risk_actions": stats.get("high_risk", 0),
            "medium_risk_actions": stats.get("medium_risk", 0),
            "low_risk_actions": stats.get("low_risk", 0),
        }
        resp = {
            "_overview_impl_version": 2,
            "ethics_enabled": hasattr(selfinc_service, "ethics_engine"),
            "ethics_threshold": ethics_threshold,
            "recent_decisions": {
                "approved": approved,
                "denied": denied,
                "total": approved + denied,
            },
            "stats": stats,
            "risk_assessment": risk_assessment,
            "framework_weights": selfinc_service.ethics_engine._load_ethics_profile(),
        }
        return jsonify(resp)
    except Exception as e:  # pragma: no cover
        logger.error(f"[SELFINC] Ethics overview error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.post("/ethics/evaluate")
def evaluate_ethics() -> ResponseReturnValue:
    """Evaluate ethics for a specific action or plan (instrumented)."""
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
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
        safety_decision = None
        file_id = target.get("file_id")
        if file_id and hasattr(selfinc_service, "safety_index"):
            safety_decision = selfinc_service.safety_index.get_decision(file_id)
        ethics_score = selfinc_service.ethics_engine.evaluate_integration(
            action, target, safety_decision
        )
        if ethics_score.overall_score < 0.4:
            risk_level = "high"
        elif ethics_score.overall_score < 0.6:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Override risk level based on explicit signals
        caps_str = str(target.get("declared_capabilities", []))
        has_network = "network" in caps_str
        has_exec_like = ("exec" in caps_str) or ("filesystem" in caps_str)
        if has_network and has_exec_like:
            risk_level = "high"
        elif risk_level == "low":
            # Elevate to medium if complexity hints are present
            try:
                complexity_score = float(target.get("complexity_score", 0) or 0)
            except Exception:
                complexity_score = 0.0
            if complexity_score >= 0.6:
                risk_level = "medium"
        import time as _time

        raw = f"{action}:{target.get('file_id')}:{ethics_score.overall_score}:{_time.time()}".encode()
        trace_id = hashlib.sha256(raw).hexdigest()[:16]
        logger.info(
            "[SELFINC][ETHICS] evaluation recorded trace_id=%s audit_db_configured=%s",
            trace_id,
            bool(getattr(selfinc_service.config, "audit_db_path", None)),
        )
        try:
            selfinc_service.audit_ledger.append(
                plan_id=target.get("plan_id", "ad_hoc"),
                action="integration_plan",
                status="applied",
                target=_audit_target_summary(action, target),
                result={
                    "overall_score": ethics_score.overall_score,
                    "risk_factor_count": len(ethics_score.risk_factors),
                    "risk_factor_hashes": [
                        _hash_audit_value(item)
                        for item in ethics_score.risk_factors[:20]
                    ],
                    "benefit_count": len(ethics_score.ethical_benefits),
                    "benefit_hashes": [
                        _hash_audit_value(item)
                        for item in ethics_score.ethical_benefits[:20]
                    ],
                },
                trace_id=trace_id,
                ethics_overall=ethics_score.overall_score,
                risk_level=risk_level,
            )
        except Exception as e:  # pragma: no cover
            logger.debug(f"[SELFINC][ETHICS] Failed to append evaluation audit: {e}")
        resp = {
            "trace_id": trace_id,
            "overall_score": ethics_score.overall_score,
            "utilitarian_score": ethics_score.utilitarian_score,
            "deontological_score": ethics_score.deontological_score,
            "virtue_score": ethics_score.virtue_score,
            "care_score": ethics_score.care_score,
            "confidence": ethics_score.confidence,
            "risk_level": risk_level,
            "reasoning": ethics_score.reasoning,
            "risk_factors": ethics_score.risk_factors,
            "ethical_benefits": ethics_score.ethical_benefits,
        }
        if disclosure_policy and disclosure_policy.is_free():
            # Limit to safe observables in free tier
            resp = {
                "trace_id": trace_id,
                "overall_score": ethics_score.overall_score,
                "confidence": ethics_score.confidence,
                "risk_level": risk_level,
                "disclosure_tier": "free",
                "message": "Detailed ethical reasoning available in higher tiers",
            }
        return jsonify(resp)
    except Exception as e:  # pragma: no cover
        logger.error(f"[SELFINC] Ethics evaluation error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.get("/ethics/audit/<string:trace_id>")
def get_ethics_audit(trace_id: str) -> ResponseReturnValue:
    """Get detailed ethics audit for a specific integration."""
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        audit_db_path = getattr(selfinc_service.config, "audit_db_path", None)
        logger.info(
            "[SELFINC][ETHICS] audit lookup trace_id=%s audit_db_configured=%s",
            trace_id,
            bool(audit_db_path),
        )

        record = None
        if hasattr(selfinc_service, "audit_ledger"):
            try:
                record = selfinc_service.audit_ledger.get_by_trace(trace_id)
            except Exception as e:  # pragma: no cover - defensive
                logger.debug(f"[SELFINC][ETHICS] Trace lookup error: {e}")

        if not record:
            return (
                jsonify(
                    {
                        "trace_id": trace_id,
                        "status": "not_found",
                        "message": "No audit record for trace id",
                    }
                ),
                404,
            )

        resp = {
            "trace_id": trace_id,
            "status": record.get("status"),
            "action": record.get("action"),
            "plan_id": record.get("plan_id"),
            "timestamp": record.get("timestamp"),
            "ethics_overall": record.get("ethics_overall"),
            "risk_level": record.get("risk_level"),
            "result": _audit_result_summary(record.get("result")),
            "target": _audit_result_summary(record.get("target")),
        }

        if disclosure_policy and disclosure_policy.is_free():
            resp = disclosure_policy.redact_payload(resp)
        return jsonify(resp)

    except Exception as e:
        logger.error(f"[SELFINC] Ethics audit error: {e}")
        return jsonify({"error": str(e)}), 500
