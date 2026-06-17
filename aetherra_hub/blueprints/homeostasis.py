"""Homeostasis control and status API.

Exposes live status, metrics, controller mode changes, actuator execution, and rollback.
Base URL: /api/homeostasis
"""

from __future__ import annotations

# Standard library imports
import asyncio
import logging
from typing import Any

# Third party imports
from flask import Blueprint, jsonify, request

from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

# Avoid importing heavy homeostasis core types at module import time to prevent
# circular imports; import lazily within request handlers.
# Aetherra imports
from Aetherra.homeostasis.homeostasis_integration import (  # type: ignore
    get_homeostasis_orchestrator,
)

# Local imports
from ..services.control_auth import authorize_control_request

logger = logging.getLogger(__name__)

bp = Blueprint("homeostasis", __name__, url_prefix="/api/homeostasis")


def _authorize_control():
    decision = authorize_control_request(request.headers, request.remote_addr)
    if decision.allowed:
        return None
    return jsonify({"ok": False, "error": decision.error}), decision.status_code


def _safe_run(coro: Any) -> Any:
    """Run a coroutine safely from sync Flask context.

    Behavior mirrors other blueprints: prefer asyncio.run, otherwise schedule on
    the running loop and return None best‑effort to avoid deadlocks.
    """
    try:
        return asyncio.run(coro)
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(coro)
                return None
            return loop.run_until_complete(coro)
        except Exception:
            return None
    except Exception:
        return None


def _guardian_decision_for_actuator(data: dict[str, Any]):
    action_type = str(data.get("action_type") or "").strip()
    target_service = str(data.get("target_service") or "").strip()
    controller_name = str(data.get("controller_name") or "homeostasis").strip()
    reason = str(data.get("reason") or "ui_trigger").strip()
    priority = str(data.get("priority") or "medium").lower().strip()
    parameters = data.get("parameters") if isinstance(data.get("parameters"), dict) else {}
    target_lower = f"{target_service} {action_type}".lower()
    capabilities = ["homeostasis:actuate"]
    if any(marker in target_lower for marker in ("security", "policy", "capability")):
        capabilities.append("security:modify")

    return evaluate_intent(
        IntentDeclaration(
            requester=str(
                request.headers.get("X-Aetherra-Principal")
                or controller_name
                or "homeostasis"
            ),
            subsystem="homeostasis",
            action="homeostasis.actuate",
            target=f"{target_service or 'system'}:{action_type}",
            purpose=reason or f"Execute homeostasis actuator {action_type}",
            capabilities=tuple(capabilities),
            evidence=(f"homeostasis_action:{action_type}",),
            reversible=True,
            rollback_plan="use homeostasis actuator rollback or restore previous service state",
            metadata={
                "action_type": action_type,
                "target_service": target_service,
                "priority": priority,
                "parameter_keys": tuple(sorted(str(key) for key in parameters)),
            },
        )
    )


def _guardian_requester(default: str = "homeostasis") -> str:
    return str(
        request.headers.get("X-Aetherra-Principal")
        or default
        or "homeostasis"
    ).strip()


def _guardian_decision_for_control(
    *,
    action: str,
    target: str,
    purpose: str,
    capabilities: tuple[str, ...],
    evidence: tuple[str, ...],
    metadata: dict[str, Any],
    rollback_plan: str,
):
    return evaluate_intent(
        IntentDeclaration(
            requester=_guardian_requester(),
            subsystem="homeostasis",
            action=action,
            target=target,
            purpose=purpose,
            capabilities=capabilities,
            evidence=evidence,
            reversible=True,
            rollback_plan=rollback_plan,
            metadata=metadata,
        )
    )


def _guardian_block_response(decision) -> tuple[dict[str, Any], int] | None:
    if decision.status in {GuardianStatus.ALLOW, GuardianStatus.ALLOW_LIMITED}:
        return None
    status_code = 202 if decision.status == GuardianStatus.REQUIRE_APPROVAL else 403
    return (
        {
            "ok": False,
            "executed": False,
            "error": decision.reason,
            "guardian": decision.to_audit_dict(),
        },
        status_code,
    )


@bp.get("/status")
def status():
    """Get comprehensive Homeostasis status snapshot.

    Returns orchestrator status, health, controller loops, actuators summary, and supervisor.
    """
    try:
        orch = get_homeostasis_orchestrator()
        # Orchestrator status (sync)
        orchestrator_status = {}
        try:
            orchestrator_status = orch.get_orchestrator_status() or {}
        except Exception:
            orchestrator_status = {}

        # Rich health (async)
        health = {}
        try:
            health = _safe_run(orch.get_system_health_status()) or {}
        except Exception:
            health = {}

        # Controller loops (sync)
        controller = {}
        try:
            if getattr(orch, "controller", None):
                controller = orch.controller.get_controller_status()  # type: ignore[attr-defined]
        except Exception:
            controller = {}

        loops = {}
        try:
            if getattr(orch, "controller", None):
                loops = orch.controller.get_control_loop_status()  # type: ignore[attr-defined]
        except Exception:
            loops = {}

        # Actuators
        actuators = {}
        recent_actions = []
        try:
            if getattr(orch, "actuators", None):
                actuators = orch.actuators.get_actuator_status()  # type: ignore[attr-defined]
                recent_actions = orch.actuators.get_action_history(20)  # type: ignore[attr-defined]
        except Exception:
            actuators = {}

        # Supervisor
        supervisor = {}
        try:
            if getattr(orch, "supervisor", None):
                supervisor = orch.supervisor.get_supervisor_status()  # type: ignore[attr-defined]
        except Exception:
            supervisor = {}

        body = {
            "ok": True,
            "orchestrator": orchestrator_status,
            "health": health,
            "controller": controller,
            "control_loops": loops,
            "actuators": actuators,
            "recent_actions": recent_actions,
            "supervisor": supervisor,
        }
        return jsonify(body)
    except Exception as exc:  # pragma: no cover - best effort
        logger.error("[HOMEOSTASIS] status failed: %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": "status_failed"}), 500


@bp.get("/metrics/snapshot")
def metrics_snapshot():
    """Get current stability metrics snapshot."""
    try:
        orch = get_homeostasis_orchestrator()
        snap = _safe_run(orch.get_metrics_snapshot()) or {}
        return jsonify({"ok": True, "snapshot": snap})
    except Exception as exc:
        logger.debug("[HOMEOSTASIS] metrics snapshot failed: %s", exc)
        return jsonify({"ok": False}), 500


@bp.get("/metrics/summary")
def metrics_summary():
    """Get recent metrics summary (requires observability component)."""
    try:
        minutes = 5
        try:
            q = request.args.get("minutes")
            if q:
                minutes = max(1, int(q))
        except Exception:
            minutes = 5
        orch = get_homeostasis_orchestrator()
        if hasattr(orch, "get_metrics_summary"):
            # get_metrics_summary is sync
            smry = orch.get_metrics_summary(minutes)  # type: ignore[attr-defined]
        else:
            smry = {"error": "observability_not_initialized"}
        return jsonify({"ok": True, "summary": smry})
    except Exception as exc:
        logger.debug("[HOMEOSTASIS] metrics summary failed: %s", exc)
        return jsonify({"ok": False}), 500


@bp.post("/mode")
def set_mode():
    """Set controller operating mode."""
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        # Lazy import to avoid circular import during app startup
        from Aetherra.homeostasis.homeostasis_core import ControllerMode  # type: ignore

        data = request.get_json(silent=True) or {}
        mode_str = str(data.get("mode", "")).lower().strip()
        reason = str(data.get("reason") or "UI request")

        mode_map = {
            "observe_only": ControllerMode.OBSERVE_ONLY,
            "advisory": ControllerMode.ADVISORY,
            "active_limited": ControllerMode.ACTIVE_LIMITED,
            "active": ControllerMode.ACTIVE,
            "emergency": ControllerMode.EMERGENCY,
            "disabled": ControllerMode.DISABLED,
        }
        if mode_str not in mode_map:
            return jsonify({"ok": False, "error": "invalid_mode"}), 400

        guardian_decision = _guardian_decision_for_control(
            action="homeostasis.set_mode",
            target="homeostasis:controller_mode",
            purpose=reason or f"Set Homeostasis controller mode to {mode_str}",
            capabilities=("homeostasis:control",),
            evidence=(f"mode:{mode_str}",),
            metadata={"mode": mode_str, "reason_present": bool(reason.strip())},
            rollback_plan="restore the previous Homeostasis controller mode",
        )
        guardian_block = _guardian_block_response(guardian_decision)
        if guardian_block is not None:
            body, status_code = guardian_block
            return jsonify(body), status_code

        orch = get_homeostasis_orchestrator()
        _safe_run(orch.set_controller_mode(mode_map[mode_str], reason))
        return jsonify({"ok": True, "mode": mode_str})
    except Exception as exc:
        logger.error("[HOMEOSTASIS] set_mode failed: %s", exc)
        return jsonify({"ok": False}), 500


@bp.post("/emergency_stop")
def emergency_stop():
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        data = request.get_json(silent=True) or {}
        reason = str(data.get("reason") or "UI emergency stop")
        guardian_decision = _guardian_decision_for_control(
            action="homeostasis.emergency_stop",
            target="homeostasis:emergency_stop",
            purpose=reason or "Trigger Homeostasis emergency stop",
            capabilities=("homeostasis:emergency",),
            evidence=("emergency_stop",),
            metadata={"reason_present": bool(reason.strip())},
            rollback_plan="reset the Homeostasis emergency stop after manual review",
        )
        guardian_block = _guardian_block_response(guardian_decision)
        if guardian_block is not None:
            body, status_code = guardian_block
            return jsonify(body), status_code

        orch = get_homeostasis_orchestrator()
        _safe_run(orch.emergency_stop(reason))
        return jsonify({"ok": True})
    except Exception as exc:
        logger.error("[HOMEOSTASIS] emergency_stop failed: %s", exc)
        return jsonify({"ok": False}), 500


@bp.post("/reset_emergency")
def reset_emergency():
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        guardian_decision = _guardian_decision_for_control(
            action="homeostasis.reset_emergency",
            target="homeostasis:emergency_stop",
            purpose="Reset Homeostasis emergency stop",
            capabilities=("homeostasis:emergency",),
            evidence=("reset_emergency",),
            metadata={},
            rollback_plan="trigger emergency stop again if reset exposes unsafe conditions",
        )
        guardian_block = _guardian_block_response(guardian_decision)
        if guardian_block is not None:
            body, status_code = guardian_block
            return jsonify(body), status_code

        orch = get_homeostasis_orchestrator()
        _safe_run(orch.reset_emergency_stop())
        return jsonify({"ok": True})
    except Exception as exc:
        logger.error("[HOMEOSTASIS] reset_emergency failed: %s", exc)
        return jsonify({"ok": False}), 500


@bp.post("/actuators/execute")
def actuators_execute():
    """Execute a named actuator action.

    Body: {
      action_type: str, target_service: str, parameters?: dict,
      controller_name?: str, reason?: str, priority?: str, timeout?: number
    }
    """
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        # Lazy import to avoid circular import during app startup
        from Aetherra.homeostasis.homeostasis_core import (  # type: ignore
            ActionPriority,
            ControlAction,
        )

        data = request.get_json(silent=True) or {}
        action_type = str(data.get("action_type") or "").strip()
        target_service = str(data.get("target_service") or "").strip()
        parameters = data.get("parameters") or {}
        controller_name = str(data.get("controller_name") or "homeostasis")
        reason = str(data.get("reason") or "ui_trigger")
        timeout = float(data.get("timeout") or 300.0)
        priority_str = str(data.get("priority") or "medium").lower()

        if not action_type:
            return jsonify({"ok": False, "error": "missing_action_type"}), 400

        guardian_decision = _guardian_decision_for_actuator(data)
        guardian_block = _guardian_block_response(guardian_decision)
        if guardian_block is not None:
            body, status_code = guardian_block
            return jsonify(body), status_code

        pr_map = {
            "low": ActionPriority.LOW,
            "medium": ActionPriority.MEDIUM,
            "high": ActionPriority.HIGH,
            "critical": ActionPriority.CRITICAL,
            "emergency": ActionPriority.EMERGENCY,
        }
        pr = pr_map.get(priority_str, ActionPriority.MEDIUM)

        orch = get_homeostasis_orchestrator()
        if not getattr(orch, "actuators", None):
            return jsonify({"ok": False, "error": "actuators_unavailable"}), 503

        action = ControlAction(
            action_type=action_type,
            target_service=target_service or "",
            parameters=parameters if isinstance(parameters, dict) else {},
            priority=pr,
            timestamp=0.0,
            controller_name=controller_name,
            reason=reason,
            timeout=timeout,
        )

        # Prefer kernel envelope when available
        exec_method = getattr(orch.actuators, "execute_action_via_kernel", None)  # type: ignore[attr-defined]
        ok = False
        if callable(exec_method):
            res = exec_method(action)
            ok = bool(_safe_run(res) if asyncio.iscoroutine(res) else res)
        else:
            res = orch.actuators.execute_action(action)  # type: ignore[attr-defined]
            ok = bool(_safe_run(res) if asyncio.iscoroutine(res) else res)

        return jsonify({"ok": True, "executed": bool(ok)})
    except Exception as exc:  # pragma: no cover - best effort
        logger.error("[HOMEOSTASIS] actuators.execute failed: %s", exc, exc_info=True)
        return jsonify({"ok": False}), 500


@bp.post("/rollback")
def rollback_last():
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        guardian_decision = _guardian_decision_for_control(
            action="homeostasis.rollback",
            target="homeostasis:actuator_history",
            purpose="Rollback the most recent Homeostasis actuator action",
            capabilities=("homeostasis:rollback",),
            evidence=("rollback_last_action",),
            metadata={},
            rollback_plan="inspect action history and re-run the reverted actuator if rollback was unsafe",
        )
        guardian_block = _guardian_block_response(guardian_decision)
        if guardian_block is not None:
            body, status_code = guardian_block
            return jsonify(body), status_code

        orch = get_homeostasis_orchestrator()
        if not getattr(orch, "actuators", None):
            return jsonify({"ok": False, "error": "actuators_unavailable"}), 503
        res = orch.actuators.rollback_last_action()  # type: ignore[attr-defined]
        out = _safe_run(res) if asyncio.iscoroutine(res) else res
        msg = None
        succ = False
        try:
            succ = bool(getattr(out, "success", False))
            msg = getattr(out, "message", None)
        except Exception:
            succ = bool(out)
        return jsonify({"ok": True, "rolled_back": succ, "message": msg})
    except Exception as exc:
        logger.error("[HOMEOSTASIS] rollback failed: %s", exc)
        return jsonify({"ok": False}), 500


@bp.get("/actions")
def actions_history():
    try:
        count = 50
        try:
            q = request.args.get("count")
            if q:
                count = max(1, min(200, int(q)))
        except Exception:
            count = 50
        orch = get_homeostasis_orchestrator()
        if not getattr(orch, "actuators", None):
            return jsonify({"ok": True, "actions": []})
        actions = orch.actuators.get_action_history(count)  # type: ignore[attr-defined]
        return jsonify({"ok": True, "actions": actions})
    except Exception as exc:
        logger.debug("[HOMEOSTASIS] actions history failed: %s", exc)
        return jsonify({"ok": False}), 500
