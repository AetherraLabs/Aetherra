"""Read-only Runtime UI snapshot collection."""

from __future__ import annotations

from typing import Any


def collect_runtime_ui_system_status() -> dict[str, dict[str, Any]]:
    """Collect conservative subsystem status without activating systems."""

    status: dict[str, dict[str, Any]] = {
        "security": {
            "status": "active",
            "health": 1.0,
            "activity": 0.35,
            "summary": "Security enforcement and audit foundations are available.",
            "metrics": {"authority": "enforce"},
        },
        "homeostasis": {
            "status": "stable",
            "health": 0.9,
            "activity": 0.2,
            "summary": "Homeostasis observation, diagnosis, recommendation, and verification foundations are available.",
            "metrics": {"authority": "observe_verify"},
        },
        "memory": {
            "status": "stable",
            "health": 0.85,
            "activity": 0.15,
            "summary": "Memory is exposed as safe summary metadata for the Observatory foundation.",
            "metrics": {"view": "summary_only"},
        },
        "consciousness": {
            "status": "stable",
            "health": 0.8,
            "activity": 0.2,
            "summary": "Consciousness traces are represented as read-only runtime state.",
            "metrics": {"view": "trace_summary"},
        },
        "agents": {
            "status": "stable",
            "health": 0.8,
            "activity": 0.2,
            "summary": "Agent activity is observable without direct UI execution authority.",
            "metrics": {"authority": "observe"},
        },
        "self_improvement": {
            "status": "stable",
            "health": 0.85,
            "activity": 0.18,
            "summary": "Self-Improvement proposes only; it does not apply changes.",
            "metrics": {"authority": "diagnose_propose"},
        },
        "self_incorporation": {
            "status": "stable",
            "health": 0.85,
            "activity": 0.12,
            "summary": "Self-Incorporation execution remains staged, governed, and rollback-aware.",
            "metrics": {"authority": "execute_after_approval"},
        },
        "maintenance": {
            "status": "stable",
            "health": 0.85,
            "activity": 0.22,
            "summary": "Maintenance coordinates observe, propose, approve, apply, verify, and learn cycles.",
            "metrics": {"authority": "coordinate"},
        },
        "aether_script": {
            "status": "stable",
            "health": 0.85,
            "activity": 0.15,
            "summary": "Aether Script state is presented as validation and execution-gate metadata.",
            "metrics": {"view": "validation_summary"},
        },
        "kernel": {
            "status": "stable",
            "health": 0.85,
            "activity": 0.2,
            "summary": "Kernel readiness is observable through bounded runtime metadata.",
            "metrics": {"authority": "runtime_core"},
        },
        "integration_validation": {
            "status": "stable",
            "health": 0.9,
            "activity": 0.1,
            "summary": "Integration Validation is available as a readiness signal; checks are not run per request.",
            "metrics": {"view": "readiness_signal"},
        },
    }
    status["guardian"] = _guardian_status()
    return status


def collect_runtime_ui_events() -> list[dict[str, Any]]:
    """Return bounded synthetic activity events for the foundation snapshot."""

    return [
        {
            "source": "runtime_ui",
            "event_type": "observatory_snapshot",
            "summary": "Read-only Cognitive Observatory snapshot generated.",
            "severity": "info",
            "details": {"authority": "observe_only"},
        },
        {
            "source": "guardian",
            "event_type": "decision",
            "summary": "Guardian status included in Observatory snapshot.",
            "severity": "notice",
            "details": {"view": "summary_only"},
        },
        {
            "source": "homeostasis",
            "event_type": "health",
            "summary": "Homeostasis health is available as read-only status metadata.",
            "severity": "info",
            "details": {"view": "health_summary"},
        },
    ]


def _guardian_status() -> dict[str, Any]:
    try:
        from Aetherra.guardian import (  # pylint: disable=import-outside-toplevel
            guardian_audit_integrity_ok,
            guardian_enabled,
            guardian_mode,
            guardian_mode_status,
        )

        enabled = guardian_enabled()
        audit_ok = guardian_audit_integrity_ok()
        mode = guardian_mode().value
        mode_state = guardian_mode_status().get("state")
    except Exception:
        return {
            "status": "unknown",
            "health": None,
            "activity": 0.0,
            "summary": "Guardian status could not be collected for this read-only snapshot.",
            "metrics": {"available": False},
        }

    return {
        "status": "active" if enabled else "offline",
        "health": 1.0 if enabled and audit_ok else 0.55,
        "activity": 0.4 if enabled else 0.0,
        "summary": "Guardian is the decision layer above Security and governed execution.",
        "metrics": {
            "available": True,
            "enabled": enabled,
            "mode": mode,
            "mode_state": mode_state,
            "audit_integrity_ok": audit_ok,
        },
    }
