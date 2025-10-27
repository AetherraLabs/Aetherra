"""Unified Maintenance Status API.

Exposes an aggregated view across Homeostasis, Self-Improvement, and Self-Incorporation.
Endpoint: GET /api/maintenance/status
"""

from __future__ import annotations

# Standard library imports
import asyncio
import logging
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any

# Third party imports
from flask import Blueprint, jsonify

# Local imports
from ..services import registry_client

logger = logging.getLogger(__name__)

bp = Blueprint("maintenance", __name__, url_prefix="/api/maintenance")


def _safe_run(coro: Any) -> Any:
    """Run a coroutine safely from sync context, mirroring registry_client behavior."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Fire-and-forget in active loop; return None best-effort
                loop.create_task(coro)
                return None
            return loop.run_until_complete(coro)
        except Exception:
            return None
    except Exception:
        return None


def _coerce_json_safe(obj: Any) -> Any:
    """Recursively coerce objects into JSON-serializable forms.

    - Enum -> name (str)
    - datetime -> isoformat
    - coroutine -> awaited result via _safe_run
    - dict/list/tuple -> recurse
    - fallback -> original
    """
    try:
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, datetime):
            return obj.isoformat()
        if asyncio.iscoroutine(obj):
            return _safe_run(obj)
        if isinstance(obj, dict):
            return {k: _coerce_json_safe(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            coerced = [_coerce_json_safe(v) for v in obj]
            return coerced if isinstance(obj, list) else tuple(coerced)
        # Dataclass instance -> dict
        if is_dataclass(obj) and not isinstance(obj, type):
            try:
                return _coerce_json_safe(asdict(obj))
            except Exception:
                return str(obj)
        # Plain object with __dict__ -> dict
        if hasattr(obj, "__dict__"):
            try:
                return _coerce_json_safe(dict(vars(obj)))
            except Exception:
                return str(obj)
        return obj
    except Exception:
        # Best-effort: if anything goes wrong, stringify the object
        try:
            return str(obj)
        except Exception:
            return None


@bp.get("/status")
def maintenance_status():
    """Aggregate status across Homeostasis, Self-Improvement, and Self-Incorporation."""
    # Defaults
    now_iso = datetime.now().isoformat()
    homeo: dict[str, Any] = {"available": False}
    sie: dict[str, Any] = {"available": False}
    selfinc: dict[str, Any] = {"available": False}
    overall_runlevel = "UNKNOWN"
    overall_health_pct = None
    critical_health_pct = None

    # Accumulators for cross-cutting KPIs (best-effort)
    kpis: dict[str, Any] = {
        "system_health_score": None,  # 0.0-1.0 if available
        "actions_executed": None,
        "proposals_generated": None,
        "proposals_executed": None,
        "proposals_accepted": None,
        "files_integrated": None,
        "files_quarantined": None,
        "last_rollback_token": None,
    }

    # Homeostasis
    try:
        # Prefer canonical launcher name (homeostasis_system)
        hs = registry_client.get_service(
            "homeostasis_system"
        ) or registry_client.get_service("aetherra_homeostasis")
        if hs:
            # Lightweight orchestrator status (sync)
            orchestrator_status = {}
            try:
                if hasattr(hs, "get_orchestrator_status"):
                    raw_orch = hs.get_orchestrator_status() or {}
                    # Convert objects/dataclasses to mappings and ensure JSON safety
                    if is_dataclass(raw_orch) and not isinstance(raw_orch, type):
                        raw_orch = asdict(raw_orch)
                    elif not isinstance(raw_orch, dict):
                        try:
                            raw_orch = dict(vars(raw_orch))
                        except Exception:
                            raw_orch = {"value": str(raw_orch)}
                    orchestrator_status = _coerce_json_safe(raw_orch)
            except Exception:
                orchestrator_status = {}

            # Rich health (async)
            health_status = {}
            try:
                if hasattr(hs, "get_system_health_status"):
                    raw_health_status = _safe_run(hs.get_system_health_status()) or {}
                    # Ensure nested values are JSON-safe (enums, datetimes, etc.)
                    health_status = _coerce_json_safe(raw_health_status)
            except Exception:
                health_status = {}

            # Try to compute headline fields from supervisor health summary
            try:
                sys_health = (
                    health_status.get("system_health", {})
                    if isinstance(health_status, dict)
                    else {}
                )
                hsum = sys_health.get("health_summary", {})
                overall_health_pct = (
                    float(hsum.get("health_percentage"))
                    if "health_percentage" in hsum
                    else None
                )
                critical_health_pct = (
                    float(hsum.get("critical_health_percentage"))
                    if "critical_health_percentage" in hsum
                    else None
                )
                # KPI: health score as 0.0-1.0 if percentage available
                if overall_health_pct is not None:
                    try:
                        kpis["system_health_score"] = max(
                            0.0, min(1.0, overall_health_pct / 100.0)
                        )
                    except Exception:
                        kpis["system_health_score"] = None
            except Exception as exc:
                logger.debug("[MAINT] compute system_health_score failed: %s", exc)

            try:
                overall_runlevel = str(
                    health_status.get("supervisor", {}).get("runlevel")
                )
            except Exception:
                # Fallback to orchestrator known fields
                overall_runlevel = (
                    "ONLINE" if orchestrator_status.get("running") else "OFFLINE"
                )

            # SI health contribution if metrics bridge is available
            si_health_contrib = None
            try:
                si_bridge = getattr(hs, "si_metrics_bridge", None)
                if si_bridge and hasattr(si_bridge, "get_si_health_contribution"):
                    # Await if coroutine; coerce to JSON-safe
                    si_health_contrib = _coerce_json_safe(
                        si_bridge.get_si_health_contribution()
                    )
            except Exception as exc:
                logger.debug("[MAINT] si_health_contrib failed: %s", exc)

            # KPI: actions executed from actuators if available
            try:
                actions_executed = (
                    (health_status.get("actuators", {}) or {}).get("actions_executed")
                    if isinstance(health_status, dict)
                    else None
                )
                if actions_executed is not None:
                    kpis["actions_executed"] = int(actions_executed)
            except Exception as exc:
                logger.debug("[MAINT] extract actions_executed failed: %s", exc)

            homeo = {
                "available": True,
                "running": bool(orchestrator_status.get("running", False)),
                "orchestrator": orchestrator_status,
                "health": health_status,
                "si_health_contribution": si_health_contrib,
            }
    except Exception as exc:
        logger.debug("[MAINT] homeostasis lookup failed: %s", exc)

    # Self-Improvement Engine
    try:
        sie_service = registry_client.get_service("self_improvement_engine")
        if sie_service:
            status = {}
            try:
                if hasattr(sie_service, "handle_message"):
                    status = (
                        _safe_run(
                            sie_service.handle_message("selfimprovement.status", {})
                        )
                        or {}
                    )
            except Exception as exc:
                logger.debug("[MAINT] sie status fetch failed: %s", exc)
                status = {}
            sie = {
                "available": True,
                "status": status,
            }
            # KPI: proposals generated if reported
            try:
                proposals = (
                    status.get("total_proposals") if isinstance(status, dict) else None
                )
                if proposals is not None:
                    kpis["proposals_generated"] = int(proposals)
            except Exception as exc:
                logger.debug("[MAINT] extract proposals_generated failed: %s", exc)
            # KPI: proposals executed/accepted (best-effort from status or metrics)
            try:
                # direct fields
                pe = (
                    status.get("proposals_executed")
                    if isinstance(status, dict)
                    else None
                )
                pa = (
                    status.get("proposals_accepted")
                    if isinstance(status, dict)
                    else None
                )
                # metrics fallback
                metrics = status.get("metrics", {}) if isinstance(status, dict) else {}
                if pe is None and isinstance(metrics, dict):
                    pe = metrics.get("proposals_executed")
                if pa is None and isinstance(metrics, dict):
                    pa = metrics.get("proposals_accepted")
                if pe is not None:
                    kpis["proposals_executed"] = int(pe)
                if pa is not None:
                    kpis["proposals_accepted"] = int(pa)
            except Exception as exc:
                logger.debug(
                    "[MAINT] extract proposals_executed/accepted failed: %s", exc
                )
    except Exception as exc:
        logger.debug("[MAINT] sie lookup failed: %s", exc)

    # Self-Incorporation
    try:
        si_service = registry_client.get_service("self_incorporation")
        if si_service:
            st = {}
            try:
                if hasattr(si_service, "get_status"):
                    st = _safe_run(si_service.get_status()) or {}
            except Exception as exc:
                logger.debug("[MAINT] selfinc status fetch failed: %s", exc)
                st = {}
            selfinc = {
                "available": True,
                "status": st,
            }
            # KPI: integration/quarantine counters and last rollback token if present
            try:
                metrics = st.get("metrics", {}) if isinstance(st, dict) else {}
                if isinstance(metrics, dict):
                    if metrics.get("files_integrated") is not None:
                        kpis["files_integrated"] = int(
                            metrics.get("files_integrated", 0)
                        )
                    if metrics.get("files_quarantined") is not None:
                        kpis["files_quarantined"] = int(
                            metrics.get("files_quarantined", 0)
                        )
                    # Fallback: some implementations record last rollback token under metrics
                    if not kpis.get("last_rollback_token"):
                        try:
                            m_rb = metrics.get("last_rollback_token")
                            if isinstance(m_rb, str) and m_rb:
                                kpis["last_rollback_token"] = m_rb
                        except Exception as exc:
                            logger.debug(
                                "[MAINT] fallback metrics.last_rollback_token failed: %s",
                                exc,
                            )
                # Some implementations may expose a recent rollback token on status
                last_rb = (
                    st.get("last_rollback_token") if isinstance(st, dict) else None
                )
                if isinstance(last_rb, str) and last_rb:
                    kpis["last_rollback_token"] = last_rb
            except Exception as exc:
                logger.debug("[MAINT] extract selfinc KPIs failed: %s", exc)
    except Exception as exc:
        logger.debug("[MAINT] selfinc lookup failed: %s", exc)

    # Overall view
    overall_running = bool(homeo.get("available") and homeo.get("running"))
    ok = True  # Endpoint succeeds even if some subsystems unavailable

    body = {
        "ok": ok,
        "ts": now_iso,
        "overall": {
            "runlevel": overall_runlevel,
            "health_percent": overall_health_pct,
            "critical_health_percent": critical_health_pct,
            "overall_running": overall_running,
        },
        "kpis": kpis,
        "homeostasis": homeo,
        "self_improvement": sie,
        "self_incorporation": selfinc,
    }

    # Final pass to ensure JSON safety across all nested structures
    body = _coerce_json_safe(body)
    return jsonify(body)
