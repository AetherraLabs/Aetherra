"""Self-Improvement API endpoints.

Provides HTTP API for Aetherra OS self-improvement engine.
Enables external tools to trigger proposal application with optional HMR integration.
"""

from __future__ import annotations

# Standard library imports
import asyncio
import logging

# Third party imports
from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

# Local imports
from ..services.control_auth import authorize_control_request
from ..services.registry_client import get_service

logger = logging.getLogger(__name__)

bp = Blueprint("self_improvement", __name__, url_prefix="/api/selfimprove")


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
                    loop = asyncio.get_event_loop()
                    si_res = loop.run_until_complete(
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
            if not hmr_controller:
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

            loop = asyncio.get_event_loop()
            try:
                result = loop.run_until_complete(
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
        proposals = data.get("proposals", [])
        method = str(data.get("method", "auto")).lower()

        if not proposals:
            return jsonify({"error": "proposals array required"}), 400

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
                loop = asyncio.get_event_loop()
                si_res = loop.run_until_complete(
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
        if not hmr_controller:
            return {
                "proposal_id": proposal_id,
                "ok": True,
                "applied": False,
                "restart_required": True,
                "warning": "HMR not available",
            }

        loop = asyncio.get_event_loop()
        try:
            result = loop.run_until_complete(
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
