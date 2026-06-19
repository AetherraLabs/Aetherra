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

from Aetherra.guardian import (
    GuardianStatus,
    IntentDeclaration,
    evaluate_intent,
    record_outcome,
)
from Aetherra.guardian.audit import list_guardian_audit_records

# Avoid importing heavy homeostasis core types at module import time to prevent
# circular imports; import lazily within request handlers.
# Aetherra imports
from Aetherra.homeostasis.homeostasis_integration import (  # type: ignore
    get_homeostasis_orchestrator,
)
from Aetherra.homeostasis.diagnosis import build_diagnosis_report
from Aetherra.homeostasis.learning import build_learning_report
from Aetherra.homeostasis.observation import build_observation_report
from Aetherra.homeostasis.recommendation import build_recommendation_report

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

    approval_id = data.get("guardian_approval_id") or data.get("approval_id")
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
                "controller_name": controller_name,
                "priority": priority,
                "parameter_keys": tuple(sorted(str(key) for key in parameters)),
            },
        ),
        approval_id=str(approval_id).strip() if approval_id else None,
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


def _priority_from_string(priority: str):
    from Aetherra.homeostasis.homeostasis_core import ActionPriority  # type: ignore

    pr_map = {
        "low": ActionPriority.LOW,
        "medium": ActionPriority.MEDIUM,
        "high": ActionPriority.HIGH,
        "critical": ActionPriority.CRITICAL,
        "emergency": ActionPriority.EMERGENCY,
    }
    return pr_map.get(str(priority or "medium").lower(), ActionPriority.MEDIUM)


def _execute_homeostasis_action(data: dict[str, Any]) -> tuple[dict[str, Any], int]:
    from Aetherra.homeostasis.homeostasis_core import ControlAction  # type: ignore

    action_type = str(data.get("action_type") or "").strip()
    target_service = str(data.get("target_service") or "").strip()
    parameters = data.get("parameters") or {}
    controller_name = str(data.get("controller_name") or "homeostasis")
    reason = str(data.get("reason") or "ui_trigger")
    timeout = float(data.get("timeout") or 300.0)
    priority = _priority_from_string(str(data.get("priority") or "medium"))

    if not action_type:
        return {"ok": False, "error": "missing_action_type"}, 400

    guardian_decision = _guardian_decision_for_actuator(data)
    guardian_block = _guardian_block_response(guardian_decision)
    if guardian_block is not None:
        body, status_code = guardian_block
        return body, status_code

    orch = get_homeostasis_orchestrator()
    if not getattr(orch, "actuators", None):
        return {"ok": False, "error": "actuators_unavailable"}, 503

    action = ControlAction(
        action_type=action_type,
        target_service=target_service or "",
        parameters=parameters if isinstance(parameters, dict) else {},
        priority=priority,
        timestamp=0.0,
        controller_name=controller_name,
        reason=reason,
        timeout=timeout,
    )

    exec_method = getattr(orch.actuators, "execute_action_via_kernel", None)  # type: ignore[attr-defined]
    if callable(exec_method):
        res = exec_method(action)
        executed = bool(_safe_run(res) if asyncio.iscoroutine(res) else res)
    else:
        res = orch.actuators.execute_action(action)  # type: ignore[attr-defined]
        executed = bool(_safe_run(res) if asyncio.iscoroutine(res) else res)

    outcome_audit_id = None
    if guardian_decision.audit_id:
        outcome_audit_id = record_outcome(
            guardian_decision.audit_id,
            {
                "status": "completed" if executed else "failed",
                "summary": "Homeostasis actuator execution completed"
                if executed
                else "Homeostasis actuator execution failed",
                "affected_count": 1 if executed else 0,
                "rollback_performed": False,
                "metrics": {
                    "executed": int(executed),
                },
            },
        )

    return {
        "ok": True,
        "executed": executed,
        "audit_id": guardian_decision.audit_id,
        "outcome_audit_id": outcome_audit_id,
    }, 200


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


def _build_homeostasis_observation() -> dict[str, Any]:
    orch = get_homeostasis_orchestrator()

    health = {}
    try:
        health = _safe_run(orch.get_system_health_status()) or {}
    except Exception:
        health = {}

    snapshot = {}
    try:
        snapshot = health.get("current_snapshot") or _safe_run(
            orch.get_metrics_snapshot()
        ) or {}
    except Exception:
        snapshot = {}

    controller = {}
    loops = {}
    setpoints = {}
    try:
        controller_obj = getattr(orch, "controller", None)
        if controller_obj is not None:
            controller = controller_obj.get_controller_status()
            loops = controller_obj.get_control_loop_status()
            setpoints = getattr(controller_obj, "setpoints", {}) or {}
    except Exception:
        controller = {}
        loops = {}
        setpoints = {}

    actuators = {}
    try:
        actuator_obj = getattr(orch, "actuators", None)
        if actuator_obj is not None:
            actuators = actuator_obj.get_actuator_status()
    except Exception:
        actuators = {}

    supervisor = {}
    try:
        supervisor_obj = getattr(orch, "supervisor", None)
        if supervisor_obj is not None:
            supervisor = supervisor_obj.get_supervisor_status()
    except Exception:
        supervisor = {}

    return build_observation_report(
        metrics_snapshot=snapshot,
        health_summary=health.get("metrics") or health.get("health") or {},
        controller_status=controller,
        control_loops=loops,
        actuator_status=actuators,
        supervisor_status=supervisor,
        setpoints=setpoints,
    )


@bp.get("/observation")
def observation():
    """Return a read-only Homeostasis awareness report."""

    try:
        return jsonify({"ok": True, "observation": _build_homeostasis_observation()})
    except Exception as exc:  # pragma: no cover - best effort
        logger.error("[HOMEOSTASIS] observation failed: %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": "observation_failed"}), 500


@bp.get("/diagnosis")
def diagnosis():
    """Return a read-only Homeostasis diagnosis report."""

    try:
        observation_report = _build_homeostasis_observation()
        return jsonify(
            {
                "ok": True,
                "observation": observation_report,
                "diagnosis": build_diagnosis_report(observation_report),
            }
        )
    except Exception as exc:  # pragma: no cover - best effort
        logger.error("[HOMEOSTASIS] diagnosis failed: %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": "diagnosis_failed"}), 500


@bp.get("/recommendations")
def recommendations():
    """Return read-only Homeostasis recommendations."""

    try:
        observation_report = _build_homeostasis_observation()
        diagnosis_report = build_diagnosis_report(observation_report)
        return jsonify(
            {
                "ok": True,
                "observation": observation_report,
                "diagnosis": diagnosis_report,
                "recommendations": build_recommendation_report(
                    observation_report,
                    diagnosis_report,
                ),
            }
        )
    except Exception as exc:  # pragma: no cover - best effort
        logger.error("[HOMEOSTASIS] recommendations failed: %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": "recommendations_failed"}), 500


@bp.get("/learning")
def learning():
    """Return read-only Homeostasis action outcome learning summary."""

    try:
        try:
            limit = int(request.args.get("limit", "100"))
        except ValueError:
            return jsonify({"ok": False, "error": "limit must be an integer"}), 400
        records = list_guardian_audit_records(limit=max(1, min(limit, 200)))
        return jsonify({"ok": True, "learning": build_learning_report(records)})
    except Exception as exc:  # pragma: no cover - best effort
        logger.error("[HOMEOSTASIS] learning report failed: %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": "learning_failed"}), 500


@bp.post("/recommendations/execute")
def execute_recommendation():
    """Execute a current actuator recommendation after explicit confirmation."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error

    payload = request.get_json(silent=True) or {}
    if payload.get("confirm_execution") is not True:
        return jsonify({"ok": False, "error": "confirm_execution required"}), 400

    requested_action = str(payload.get("action_type") or "").strip()
    requested_target = str(payload.get("target_service") or "").strip()
    if not requested_action or not requested_target:
        return jsonify({"ok": False, "error": "action_type and target_service required"}), 400

    try:
        observation_report = _build_homeostasis_observation()
        diagnosis_report = build_diagnosis_report(observation_report)
        recommendation_report = build_recommendation_report(
            observation_report,
            diagnosis_report,
        )
        current = next(
            (
                item
                for item in recommendation_report.get("recommendations", [])
                if item.get("action_type") == requested_action
                and item.get("target_service") == requested_target
            ),
            None,
        )
        if current is None:
            return jsonify({"ok": False, "error": "recommendation_not_current"}), 409

        capabilities = set(current.get("required_capabilities") or [])
        if "homeostasis:actuate" not in capabilities:
            return jsonify({"ok": False, "error": "recommendation_not_executable"}), 409

        action_payload = {
            "action_type": current["action_type"],
            "target_service": current["target_service"],
            "parameters": current.get("parameters") or {},
            "guardian_approval_id": payload.get("guardian_approval_id")
            or payload.get("approval_id"),
            "priority": payload.get("priority") or "medium",
            "controller_name": "homeostasis_recommendation",
            "reason": payload.get("reason")
            or f"Execute Homeostasis recommendation for {current['cause_category']}",
            "timeout": payload.get("timeout") or 300.0,
        }
        result, status_code = _execute_homeostasis_action(action_payload)
        result["recommendation"] = current
        result["controlled_action"] = {
            "source": "current_recommendation",
            "guardian_reviewed": status_code == 200,
            "executed": bool(result.get("executed")),
        }
        return jsonify(result), status_code
    except Exception as exc:  # pragma: no cover - best effort
        logger.error("[HOMEOSTASIS] recommendation execution failed: %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": "recommendation_execution_failed"}), 500


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
        data = request.get_json(silent=True) or {}
        result, status_code = _execute_homeostasis_action(data)
        return jsonify(result), status_code
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
