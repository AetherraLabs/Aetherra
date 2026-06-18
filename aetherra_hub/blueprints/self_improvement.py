"""Self-Improvement API endpoints.

Provides HTTP API for Aetherra OS self-improvement engine.
Enables external tools to trigger proposal application with optional HMR integration.
"""

from __future__ import annotations

# Standard library imports
import logging
from typing import Any

# Third party imports
from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

# Local imports
from ..services.control_auth import authorize_control_request
from ..services.registry_client import get_service
from ..utils.http import run_coro_blocking

logger = logging.getLogger(__name__)

bp = Blueprint("self_improvement", __name__, url_prefix="/api/selfimprove")


def _get_self_improvement_service() -> Any | None:
    return get_service("self_improvement_engine")


def _service_call(service: Any, message_type: str, payload: dict[str, Any] | None = None) -> Any:
    if hasattr(service, "handle_message"):
        return run_coro_blocking(service.handle_message(message_type, payload or {}))
    if message_type.endswith("status") and hasattr(service, "get_improvement_status"):
        return service.get_improvement_status()
    if message_type.endswith("trends") and hasattr(service, "get_metric_trends"):
        return service.get_metric_trends()
    if message_type.endswith("proposals") and hasattr(service, "list_active_proposals"):
        payload = payload or {}
        summary = (
            service.get_review_summary()
            if hasattr(service, "get_review_summary")
            else {}
        )
        return {
            "status": "ok",
            "summary": summary,
            "proposals": service.list_active_proposals(
                status=payload.get("status"),
                improvement_type=payload.get("improvement_type"),
                readiness_status=payload.get("readiness_status"),
                max_risk=payload.get("max_risk"),
                min_confidence=payload.get("min_confidence"),
                limit=int(payload.get("limit") or 100),
            ),
        }
    if message_type.endswith("dismiss_proposal") and hasattr(service, "dismiss_proposal"):
        return run_coro_blocking(service.dismiss_proposal(**(payload or {})))
    if message_type.endswith("reopen_proposal") and hasattr(service, "reopen_proposal"):
        return run_coro_blocking(service.reopen_proposal(**(payload or {})))
    if message_type.endswith("proposal_history") and hasattr(service, "get_proposal_history"):
        payload = payload or {}
        proposal_id = str(payload.get("proposal_id") or "")
        limit = int(payload.get("limit") or 50)
        return {
            "status": "ok",
            "proposal_id": proposal_id,
            "events": service.get_proposal_history(proposal_id, limit=limit),
        }
    if message_type.endswith("proposal") and hasattr(service, "get_proposal"):
        proposal_id = str((payload or {}).get("proposal_id") or "")
        proposal = service.get_proposal(proposal_id)
        if proposal is None:
            return {"status": "not_found", "proposal": None}
        return {"status": "ok", "proposal": proposal}
    return None


def _authorize_control() -> ResponseReturnValue | None:
    decision = authorize_control_request(request.headers, request.remote_addr)
    if decision.allowed:
        return None
    return jsonify({"ok": False, "error": decision.error}), decision.status_code


def _guardian_decision_for_proposal(data: dict, sender: str | None):
    proposal_id = str(data.get("proposal_id") or "").strip()
    method = str(data.get("method", "auto")).lower()
    hmr_target = data.get("hmr_target")
    hmr_source = data.get("hmr_source")
    rollback_plan = data.get("rollback_plan") or data.get("rollback")
    reversible = bool(data.get("reversible")) or bool(rollback_plan)
    capabilities = ["self:modify"]
    if method in {"auto", "hmr"} and (hmr_target or hmr_source):
        capabilities.append("code:modify")
        capabilities.append("system:reload")
    target = str(hmr_target or hmr_source or proposal_id)
    return evaluate_intent(
        IntentDeclaration(
            requester=str(sender or data.get("sender") or "self_improvement"),
            subsystem="self_improvement",
            action="self.apply_proposal",
            target=target,
            purpose=str(data.get("description") or f"Apply proposal {proposal_id}"),
            capabilities=tuple(capabilities),
            reversible=reversible,
            rollback_plan=str(rollback_plan) if rollback_plan else None,
            evidence=tuple(
                item
                for item in (
                    f"proposal:{proposal_id}" if proposal_id else None,
                    f"hmr_target:{hmr_target}" if hmr_target else None,
                    f"hmr_source:{hmr_source}" if hmr_source else None,
                )
                if item
            ),
            metadata={
                "proposal_id": proposal_id,
                "method": method,
                "type": data.get("type"),
            },
        ),
        approval_id=data.get("guardian_approval_id") or data.get("approval_id"),
    )


def _guardian_block_response(
    proposal_id: str | None, decision
) -> tuple[dict, int] | None:
    if decision.status in {GuardianStatus.ALLOW, GuardianStatus.ALLOW_LIMITED}:
        return None
    status_code = 202 if decision.status == GuardianStatus.REQUIRE_APPROVAL else 403
    return (
        {
            "ok": False,
            "proposal_id": proposal_id,
            "applied": False,
            "restart_required": False,
            "method": "guardian",
            "guardian": decision.to_audit_dict(),
            "error": decision.reason,
        },
        status_code,
    )


@bp.get("/status")
def get_status() -> ResponseReturnValue:
    """Return read-only self-improvement engine status."""
    try:
        service = _get_self_improvement_service()
        if service is None:
            return (
                jsonify(
                    {
                        "status": "disabled",
                        "running": False,
                        "error": "Self-improvement engine not registered",
                    }
                ),
                503,
            )
        status = _service_call(service, "selfimprovement.status")
        if not isinstance(status, dict):
            return jsonify({"status": "error", "error": "status unavailable"}), 503
        return jsonify(status)
    except Exception as exc:
        logger.error("[SELFIMPROVE] Status error: %s", exc)
        return jsonify({"status": "error", "error": "Internal server error"}), 500


@bp.get("/proposals")
def get_proposals() -> ResponseReturnValue:
    """Return active improvement proposals without applying them."""
    try:
        service = _get_self_improvement_service()
        if service is None:
            return (
                jsonify(
                    {
                        "status": "disabled",
                        "proposals": [],
                        "error": "Self-improvement engine not registered",
                    }
                ),
                503,
            )
        result = _service_call(
            service,
            "selfimprovement.proposals",
            {
                "status": request.args.get("status"),
                "improvement_type": request.args.get("type")
                or request.args.get("improvement_type"),
                "readiness_status": request.args.get("readiness")
                or request.args.get("readiness_status"),
                "max_risk": request.args.get("max_risk", type=float),
                "min_confidence": request.args.get("min_confidence", type=float),
                "limit": request.args.get("limit", 100, type=int),
            },
        )
        if isinstance(result, dict):
            proposals = result.get("proposals", [])
            summary = result.get("summary", {})
        elif isinstance(result, list):
            proposals = result
            summary = {}
        else:
            proposals = []
            summary = {}
        return jsonify({"status": "ok", "summary": summary, "proposals": proposals})
    except Exception as exc:
        logger.error("[SELFIMPROVE] Proposals error: %s", exc)
        return jsonify({"status": "error", "error": "Internal server error"}), 500


@bp.get("/proposals/<proposal_id>")
def get_proposal(proposal_id: str) -> ResponseReturnValue:
    """Return one active improvement proposal without applying it."""
    try:
        service = _get_self_improvement_service()
        if service is None:
            return (
                jsonify(
                    {
                        "status": "disabled",
                        "proposal": None,
                        "error": "Self-improvement engine not registered",
                    }
                ),
                503,
            )
        result = _service_call(
            service,
            "selfimprovement.proposal",
            {"proposal_id": proposal_id},
        )
        if not isinstance(result, dict) or result.get("status") == "not_found":
            return jsonify({"status": "not_found", "proposal": None}), 404
        proposal = result.get("proposal")
        if not isinstance(proposal, dict):
            return jsonify({"status": "not_found", "proposal": None}), 404
        return jsonify({"status": "ok", "proposal": proposal})
    except Exception as exc:
        logger.error("[SELFIMPROVE] Proposal detail error: %s", exc)
        return jsonify({"status": "error", "error": "Internal server error"}), 500


@bp.get("/proposals/<proposal_id>/history")
def get_proposal_history(proposal_id: str) -> ResponseReturnValue:
    """Return lifecycle history for one proposal."""
    try:
        service = _get_self_improvement_service()
        if service is None:
            return (
                jsonify(
                    {
                        "status": "disabled",
                        "events": [],
                        "error": "Self-improvement engine not registered",
                    }
                ),
                503,
            )
        limit = request.args.get("limit", 50, type=int)
        result = _service_call(
            service,
            "selfimprovement.proposal_history",
            {"proposal_id": proposal_id, "limit": limit},
        )
        if not isinstance(result, dict):
            return jsonify({"status": "error", "error": "history unavailable"}), 503
        events = result.get("events")
        if not isinstance(events, list):
            events = []
        return jsonify({"status": "ok", "proposal_id": proposal_id, "events": events})
    except Exception as exc:
        logger.error("[SELFIMPROVE] Proposal history error: %s", exc)
        return jsonify({"status": "error", "error": "Internal server error"}), 500


@bp.get("/trends")
def get_trends() -> ResponseReturnValue:
    """Return read-only metric trends from the self-improvement engine."""
    try:
        service = _get_self_improvement_service()
        if service is None:
            return (
                jsonify(
                    {
                        "status": "disabled",
                        "trends": {},
                        "error": "Self-improvement engine not registered",
                    }
                ),
                503,
            )
        trends = _service_call(service, "selfimprovement.trends")
        if not isinstance(trends, dict):
            trends = {}
        return jsonify({"status": "ok", "trends": trends})
    except Exception as exc:
        logger.error("[SELFIMPROVE] Trends error: %s", exc)
        return jsonify({"status": "error", "error": "Internal server error"}), 500


def _proposal_lifecycle_response(result: Any) -> ResponseReturnValue:
    if not isinstance(result, dict):
        return jsonify({"ok": False, "error": "lifecycle operation failed"}), 500
    status = result.get("status")
    if status == "ok":
        return jsonify({"ok": True, **result})
    if status == "not_found":
        return jsonify({"ok": False, **result}), 404
    if status == "invalid_state":
        return jsonify({"ok": False, **result}), 409
    return jsonify({"ok": False, **result}), 400


@bp.post("/proposals/<proposal_id>/dismiss")
def dismiss_proposal(proposal_id: str) -> ResponseReturnValue:
    """Dismiss a proposal from active review without applying it."""
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        service = _get_self_improvement_service()
        if service is None:
            return (
                jsonify(
                    {
                        "ok": False,
                        "status": "disabled",
                        "error": "Self-improvement engine not registered",
                    }
                ),
                503,
            )
        data = request.get_json(silent=True) or {}
        actor = (
            request.headers.get("X-Aetherra-Principal")
            or data.get("actor")
            or "hub:self_improvement"
        )
        result = _service_call(
            service,
            "selfimprovement.dismiss_proposal",
            {
                "proposal_id": proposal_id,
                "reason": str(data.get("reason") or ""),
                "actor": str(actor),
            },
        )
        return _proposal_lifecycle_response(result)
    except Exception as exc:
        logger.error("[SELFIMPROVE] Dismiss proposal error: %s", exc)
        return jsonify({"ok": False, "error": "Internal server error"}), 500


@bp.post("/proposals/<proposal_id>/reopen")
def reopen_proposal(proposal_id: str) -> ResponseReturnValue:
    """Reopen a dismissed proposal for active review."""
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        service = _get_self_improvement_service()
        if service is None:
            return (
                jsonify(
                    {
                        "ok": False,
                        "status": "disabled",
                        "error": "Self-improvement engine not registered",
                    }
                ),
                503,
            )
        data = request.get_json(silent=True) or {}
        actor = (
            request.headers.get("X-Aetherra-Principal")
            or data.get("actor")
            or "hub:self_improvement"
        )
        result = _service_call(
            service,
            "selfimprovement.reopen_proposal",
            {
                "proposal_id": proposal_id,
                "reason": str(data.get("reason") or ""),
                "actor": str(actor),
            },
        )
        return _proposal_lifecycle_response(result)
    except Exception as exc:
        logger.error("[SELFIMPROVE] Reopen proposal error: %s", exc)
        return jsonify({"ok": False, "error": "Internal server error"}), 500


@bp.post("/apply")
def apply_proposal() -> ResponseReturnValue:
    """Apply an approved self-improvement proposal.

    Expects JSON body:
    {
        "proposal_id": "SI-101",
        "method": "auto" | "selfinc" | "hmr" (default: "auto"),
        "type": "optimize" | "scale_up" | "degrade" | "change_strategy",  // optional
        "description": "...",  // optional
        "params": { ... },       // optional
        // HMR fields (only if method == "hmr" or fallback to HMR is needed)
        "hmr_target": "memory_adapter",
        "hmr_source": "Aetherra.adapters.memory_adapter"
    }
    """
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        data = request.get_json() or {}
        proposal_id = data.get("proposal_id")

        if not proposal_id:
            return jsonify({"error": "proposal_id required"}), 400

        method = str(data.get("method", "auto")).lower()

        # Build a common payload for Self-Incorporation
        sender = request.headers.get("X-Aetherra-Principal") or data.get("sender")
        guardian_decision = _guardian_decision_for_proposal(data, sender)
        guardian_block = _guardian_block_response(proposal_id, guardian_decision)
        if guardian_block is not None:
            body, status_code = guardian_block
            return jsonify(body), status_code

        proposal_payload = {
            "proposal_id": proposal_id,
            "type": data.get("type"),
            "description": data.get("description"),
            "params": data.get("params") or {},
            "sender": sender,
        }

        # 1) Prefer Self-Incorporation when requested or in auto mode
        if method in ("auto", "selfinc"):
            try:
                selfinc = get_service("self_incorporation")
            except Exception as _e:
                selfinc = None
                logger.debug("[SELFIMPROVE] get self_incorporation failed: %s", _e)

            if selfinc is not None:
                try:
                    si_res = run_coro_blocking(
                        selfinc.handle_message(
                            "selfimprovement.proposal", proposal_payload
                        )
                    )
                except Exception as exc:
                    si_res = {"status": "error", "error": str(exc)}

                if isinstance(si_res, dict) and si_res.get("status") == "accepted":
                    return jsonify(
                        {
                            "ok": True,
                            "proposal_id": proposal_id,
                            "applied": True,
                            "restart_required": False,
                            "method": "selfinc",
                            "selfinc_result": si_res,
                        }
                    )

                # If method explicitly selfinc, do not fallback automatically
                if method == "selfinc":
                    return jsonify(
                        {
                            "ok": False,
                            "proposal_id": proposal_id,
                            "applied": False,
                            "restart_required": False,
                            "method": "selfinc",
                            "error": si_res.get("reason")
                            if isinstance(si_res, dict)
                            else "selfinc_failed",
                            "selfinc_result": si_res,
                        }
                    ), 400

        # 2) Fallback or explicit HMR path
        if method in ("auto", "hmr"):
            hmr_target = data.get("hmr_target")
            hmr_source = data.get("hmr_source")

            if not hmr_target or not hmr_source:
                # No HMR details - approve but mark manual
                logger.info(
                    f"[SELFIMPROVE] Proposal {proposal_id} approved; missing HMR details -> manual"
                )
                return jsonify(
                    {
                        "ok": True,
                        "proposal_id": proposal_id,
                        "applied": False,
                        "restart_required": True,
                        "method": "manual",
                        "message": "Proposal approved, requires manual application or restart",
                    }
                )

            hmr_controller = get_service("hmr_controller")
            if not hmr_controller or not hasattr(hmr_controller, "handle_kernel_task"):
                logger.warning("[SELFIMPROVE] HMR requested but controller unavailable")
                return jsonify(
                    {
                        "ok": True,
                        "proposal_id": proposal_id,
                        "applied": False,
                        "restart_required": True,
                        "warning": "HMR not available",
                    }
                )

            try:
                result = run_coro_blocking(
                    hmr_controller.handle_kernel_task(
                        {
                            "type": "hmr_reload",
                            "data": {
                                "target": hmr_target,
                                "source": hmr_source,
                                "mode": "safe",
                            },
                        }
                    )
                )

                if result and result.get("ok"):
                    logger.info(
                        f"[SELFIMPROVE] Applied proposal {proposal_id} via HMR (target={hmr_target})"
                    )
                    return jsonify(
                        {
                            "ok": True,
                            "proposal_id": proposal_id,
                            "applied": True,
                            "restart_required": False,
                            "method": "hmr",
                            "hmr_result": result,
                        }
                    )

                # HMR returned but not ok
                return jsonify(
                    {
                        "ok": False,
                        "proposal_id": proposal_id,
                        "applied": False,
                        "restart_required": True,
                        "method": "hmr",
                        "error": (result or {}).get("error", "hmr_failed"),
                        "hmr_result": result,
                    }
                ), 400

            except Exception as exc:
                logger.error(f"[SELFIMPROVE] HMR exception for {proposal_id}: {exc}")
                return jsonify(
                    {
                        "ok": False,
                        "proposal_id": proposal_id,
                        "applied": False,
                        "restart_required": True,
                        "method": "hmr",
                        "error": f"HMR exception: {str(exc)}",
                    }
                ), 400

        # 3) Manual apply fallback
        logger.info(f"[SELFIMPROVE] Proposal {proposal_id} marked for manual apply")
        return jsonify(
            {
                "ok": True,
                "proposal_id": proposal_id,
                "applied": False,
                "restart_required": True,
                "method": "manual",
                "message": "Proposal approved, requires manual application or restart",
            }
        )

    except Exception as e:
        logger.error(f"[SELFIMPROVE] Apply error: {e}")
        return jsonify({"error": "Failed to apply proposal"}), 500


@bp.post("/batch-apply")
def batch_apply_proposals() -> ResponseReturnValue:
    """Apply multiple approved proposals.

    Expects JSON body:
    {
        "proposals": [
            {"proposal_id": "SI-101", "hmr_target": "...", "hmr_source": "..."},
            {"proposal_id": "SI-102", "hmr_target": "...", "hmr_source": "..."}
        ],
        "use_hmr": true  // optional, default true
    }
    """
    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        data = request.get_json() or {}
        proposals = data.get("proposals")
        proposal_ids = data.get("proposal_ids")
        method = str(data.get("method", "auto")).lower()

        if proposals is None and isinstance(proposal_ids, list):
            proposals = [{"proposal_id": proposal_id} for proposal_id in proposal_ids]

        if not proposals:
            return jsonify({"error": "proposals or proposal_ids array required"}), 400

        sender = request.headers.get("X-Aetherra-Principal") or data.get("sender")

        results = []
        for proposal in proposals:
            proposal_id = proposal.get("proposal_id")
            if not proposal_id:
                results.append(
                    {"proposal_id": None, "ok": False, "error": "missing proposal_id"}
                )
                continue

            # Build request for single apply
            apply_data = {
                "proposal_id": proposal_id,
                "method": str(proposal.get("method", method)).lower(),
                "type": proposal.get("type"),
                "description": proposal.get("description"),
                "params": proposal.get("params"),
                "hmr_target": proposal.get("hmr_target"),
                "hmr_source": proposal.get("hmr_source"),
                "reversible": proposal.get("reversible", data.get("reversible")),
                "rollback_plan": proposal.get(
                    "rollback_plan",
                    proposal.get("rollback", data.get("rollback_plan") or data.get("rollback")),
                ),
                "sender": sender or proposal.get("sender"),
            }

            # Reuse internal helper
            result = _apply_single_proposal(apply_data)
            results.append(result)

        success_count = sum(1 for r in results if r.get("ok") and r.get("applied"))

        return jsonify(
            {
                "ok": True,
                "total": len(proposals),
                "applied": success_count,
                "results": results,
            }
        )

    except Exception as e:
        logger.error(f"[SELFIMPROVE] Batch apply error: {e}")
        return jsonify({"error": "Failed to batch apply proposals"}), 500


def _apply_single_proposal(data: dict) -> dict:
    """Internal helper to apply a single proposal (reused by batch endpoint)."""
    proposal_id = data.get("proposal_id")
    method = str(data.get("method", "auto")).lower()
    guardian_decision = _guardian_decision_for_proposal(data, data.get("sender"))
    guardian_block = _guardian_block_response(proposal_id, guardian_decision)
    if guardian_block is not None:
        body, status_code = guardian_block
        body["status_code"] = status_code
        return body

    # Try Self-Incorporation first if requested/auto
    if method in ("auto", "selfinc"):
        try:
            selfinc = get_service("self_incorporation")
        except Exception as _e:
            selfinc = None
            logger.debug("[SELFIMPROVE] get self_incorporation failed: %s", _e)

        if selfinc is not None:
            payload = {
                "proposal_id": proposal_id,
                "type": data.get("type"),
                "description": data.get("description"),
                "params": data.get("params") or {},
                "sender": data.get("sender"),
            }
            try:
                si_res = run_coro_blocking(
                    selfinc.handle_message("selfimprovement.proposal", payload)
                )
            except Exception as exc:
                si_res = {"status": "error", "error": str(exc)}

            if isinstance(si_res, dict) and si_res.get("status") == "accepted":
                return {
                    "proposal_id": proposal_id,
                    "ok": True,
                    "applied": True,
                    "restart_required": False,
                    "method": "selfinc",
                    "selfinc_result": si_res,
                }

            if method == "selfinc":
                return {
                    "proposal_id": proposal_id,
                    "ok": False,
                    "applied": False,
                    "restart_required": False,
                    "method": "selfinc",
                    "error": si_res.get("reason")
                    if isinstance(si_res, dict)
                    else "selfinc_failed",
                    "selfinc_result": si_res,
                }

    # HMR explicit or fallback
    if method in ("auto", "hmr"):
        hmr_target = data.get("hmr_target")
        hmr_source = data.get("hmr_source")
        if not hmr_target or not hmr_source:
            return {
                "proposal_id": proposal_id,
                "ok": True,
                "applied": False,
                "restart_required": True,
                "method": "manual",
                "message": "Proposal approved, requires manual application or restart",
            }

        hmr_controller = get_service("hmr_controller")
        if not hmr_controller or not hasattr(hmr_controller, "handle_kernel_task"):
            return {
                "proposal_id": proposal_id,
                "ok": True,
                "applied": False,
                "restart_required": True,
                "warning": "HMR not available",
            }

        try:
            result = run_coro_blocking(
                hmr_controller.handle_kernel_task(
                    {
                        "type": "hmr_reload",
                        "data": {
                            "target": hmr_target,
                            "source": hmr_source,
                            "mode": "safe",
                        },
                    }
                )
            )
            if result and result.get("ok"):
                return {
                    "proposal_id": proposal_id,
                    "ok": True,
                    "applied": True,
                    "restart_required": False,
                    "method": "hmr",
                    "hmr_result": result,
                }
            return {
                "proposal_id": proposal_id,
                "ok": False,
                "applied": False,
                "restart_required": True,
                "method": "hmr",
                "error": (result or {}).get("error", "hmr_failed"),
                "hmr_result": result,
            }
        except Exception as exc:
            return {
                "proposal_id": proposal_id,
                "ok": False,
                "applied": False,
                "restart_required": True,
                "method": "hmr",
                "error": f"HMR exception: {str(exc)}",
            }

    # Manual fallback
    return {
        "proposal_id": proposal_id,
        "ok": True,
        "applied": False,
        "restart_required": True,
        "method": "manual",
    }
