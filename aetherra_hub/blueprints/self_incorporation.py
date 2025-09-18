"""Self-Incorporation API endpoints.

Provides HTTP API for Aetherra OS self-incorporation system.
Enables external tools to trigger discovery, classification, security evaluation,
planning, and integration of the OS codebase.
"""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from ..services.registry_client import get_service

logger = logging.getLogger(__name__)

bp = Blueprint("self_incorporation", __name__, url_prefix="/api/selfinc")


@bp.get("/status")
def get_status() -> ResponseReturnValue:
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
def trigger_scan() -> ResponseReturnValue:
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
def apply_plan() -> ResponseReturnValue:
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
def rollback() -> ResponseReturnValue:
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
def get_audit() -> ResponseReturnValue:
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
        print(f"OVERVIEW DEBUG resp={resp}", flush=True)
        return jsonify(resp)
    except Exception as e:  # pragma: no cover
        logger.error(f"[SELFINC] Ethics overview error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.post("/ethics/evaluate")
def evaluate_ethics() -> ResponseReturnValue:
    """Evaluate ethics for a specific action or plan (instrumented)."""
    print("EVALUATE ENDPOINT HIT", flush=True)
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
        import hashlib
        import sqlite3
        import time as _time

        raw = f"{action}:{target.get('file_id')}:{ethics_score.overall_score}:{_time.time()}".encode()
        trace_id = hashlib.sha256(raw).hexdigest()[:16]
        audit_db_path = getattr(selfinc_service.config, "audit_db_path", None)
        logger.info(
            f"[SELFINC][DEBUG] evaluate_ethics: trace_id={trace_id} audit_db_path={audit_db_path}"
        )
        try:
            selfinc_service.audit_ledger.append(
                plan_id=target.get("plan_id", "ad_hoc"),
                action="integration_plan",
                status="applied",
                target={"action": action, "target": target},
                result={
                    "overall_score": ethics_score.overall_score,
                    "risk_factors": ethics_score.risk_factors,
                    "benefits": ethics_score.ethical_benefits,
                },
                trace_id=trace_id,
                ethics_overall=ethics_score.overall_score,
                risk_level=risk_level,
            )
            conn = sqlite3.connect(selfinc_service.config.audit_db_path)
            try:
                cur = conn.execute(
                    "SELECT COUNT(*) FROM audit_records WHERE trace_id = ?", (trace_id,)
                )
                row_count = cur.fetchone()[0]
                print(
                    f"EVALUATE DEBUG trace_id={trace_id} row_count_after_insert={row_count}",
                    flush=True,
                )
            finally:
                conn.close()
        except Exception as e:  # pragma: no cover
            logger.debug(f"[SELFINC][ETHICS] Failed to append evaluation audit: {e}")
        return jsonify(
            {
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
        )
    except Exception as e:  # pragma: no cover
        logger.error(f"[SELFINC] Ethics evaluation error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.get("/ethics/audit/<string:trace_id>")
def get_ethics_audit(trace_id: str) -> ResponseReturnValue:
    print(f"AUDIT ENDPOINT HIT: {trace_id}", flush=True)
    """Get detailed ethics audit for a specific integration."""
    try:
        selfinc_service = get_service("self_incorporation")
        if not selfinc_service:
            return jsonify({"error": "Self-incorporation service not available"}), 503

        # Debug: print trace_id and audit DB path (absolute)
        import os

        audit_db_path = getattr(selfinc_service.config, "audit_db_path", None)
        abs_audit_db_path = os.path.abspath(audit_db_path) if audit_db_path else None
        logger.info(
            f"[SELFINC][DEBUG] get_ethics_audit: trace_id={trace_id} audit_db_path={audit_db_path} abs_audit_db_path={abs_audit_db_path}"
        )

        record = None
        if hasattr(selfinc_service, "audit_ledger"):
            try:
                # instrumentation: count rows with trace_id first
                import sqlite3

                conn = sqlite3.connect(selfinc_service.config.audit_db_path)
                try:
                    cur = conn.execute(
                        "SELECT COUNT(*) FROM audit_records WHERE trace_id = ?",
                        (trace_id,),
                    )
                    pre_lookup = cur.fetchone()[0]
                finally:
                    conn.close()
                print(
                    f"AUDIT DEBUG pre_lookup_count={pre_lookup} trace_id={trace_id}",
                    flush=True,
                )
                record = selfinc_service.audit_ledger.get_by_trace(trace_id)
            except Exception as e:  # pragma: no cover - defensive
                logger.debug(f"[SELFINC][ETHICS] Trace lookup error: {e}")

        if not record:
            return jsonify(
                {
                    "trace_id": trace_id,
                    "status": "not_found",
                    "message": "No audit record for trace id",
                }
            ), 404

        return jsonify(
            {
                "trace_id": trace_id,
                "status": record.get("status"),
                "action": record.get("action"),
                "plan_id": record.get("plan_id"),
                "timestamp": record.get("timestamp"),
                "ethics_overall": record.get("ethics_overall"),
                "risk_level": record.get("risk_level"),
                "result": record.get("result"),
                "target": record.get("target"),
            }
        )

    except Exception as e:
        logger.error(f"[SELFINC] Ethics audit error: {e}")
        return jsonify({"error": str(e)}), 500
