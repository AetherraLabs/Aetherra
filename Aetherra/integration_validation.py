"""Cross-system integration validation for Aetherra foundations.

The validator is intentionally non-destructive. It checks that the current
foundation systems can cooperate through their public contracts without running
real maintenance mutations, external tools, network calls, or file-changing
self-incorporation actions.
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator


@dataclass(slots=True)
class IntegrationValidationCheck:
    """One validation check result."""

    name: str
    passed: bool
    summary: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IntegrationValidationReport:
    """Cross-system validation report."""

    profile: str
    workspace_root: str
    checks: list[IntegrationValidationCheck]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "workspace_root": self.workspace_root,
            "passed": self.passed,
            "check_count": len(self.checks),
            "checks": [asdict(check) for check in self.checks],
        }


def run_integration_validation(
    *,
    workspace_root: str | Path | None = None,
    profile: str = "test",
) -> IntegrationValidationReport:
    """Run the non-destructive cross-system validation foundation."""

    if workspace_root is None:
        with tempfile.TemporaryDirectory(prefix="aetherra-integration-") as tmp_dir:
            return _run_validation(Path(tmp_dir), profile=profile)
    return _run_validation(Path(workspace_root), profile=profile)


def _run_validation(workspace_root: Path, *, profile: str) -> IntegrationValidationReport:
    workspace_root = workspace_root.expanduser().resolve()
    workspace_root.mkdir(parents=True, exist_ok=True)
    checks: list[IntegrationValidationCheck] = []

    with _validation_environment(workspace_root, profile=profile):
        checks.append(_check_guardian_security_chain())
        checks.append(_check_homeostasis_observation_diagnosis())
        checks.append(_check_maintenance_coordination_chain())
        checks.append(_check_self_incorporation_scope_and_rollback())
        checks.append(_check_aether_script_runtime_gate())

    return IntegrationValidationReport(
        profile=profile,
        workspace_root=str(workspace_root),
        checks=checks,
    )


def _check_guardian_security_chain() -> IntegrationValidationCheck:
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    allowed = evaluate_intent(
        IntentDeclaration(
            requester="aether_script:runtime",
            subsystem="integration_validation",
            action="script.execute",
            target="integration_validation:script_allow",
            purpose="Validate Guardian and Security capability bridge for script execution",
            capabilities=("script:run",),
            reversible=False,
            evidence=("integration_validation:guardian_security_allow",),
            metadata={"validation": True},
        ),
        capability_checker=_integration_capability_checker,
    )

    with _temporary_env({"AETHERRA_REQUIRE_CAPABILITIES": "1"}):
        denied = evaluate_intent(
            IntentDeclaration(
                requester="external-integration-runner",
                subsystem="integration_validation",
                action="script.execute",
                target="integration_validation:script_deny",
                purpose="Validate strict capability denial for unauthorized callers",
                capabilities=("script:run",),
                reversible=False,
                evidence=("integration_validation:guardian_security_deny",),
                metadata={"validation": True},
            )
        )

    passed = bool(allowed.allowed and not denied.allowed and denied.reason == "missing_capability")
    return IntegrationValidationCheck(
        name="guardian_security_chain",
        passed=passed,
        summary="Guardian allows an internal script runtime and denies an external strict-mode caller",
        details={
            "allow_status": allowed.status.value,
            "allow_reason": allowed.reason,
            "deny_status": denied.status.value,
            "deny_reason": denied.reason,
            "deny_missing_capability": "script:run"
            in tuple(denied.details.get("missing_capabilities") or ()),
        },
    )


def _check_homeostasis_observation_diagnosis() -> IntegrationValidationCheck:
    from Aetherra.homeostasis.diagnosis import build_diagnosis_report
    from Aetherra.homeostasis.observation import build_observation_report

    observation = build_observation_report(
        metrics_snapshot={
            "memory_rtt": 180.0,
            "queue_depth": 120.0,
            "plugin_load_success": 60.0,
        },
        health_summary={"status": "degraded"},
        controller_status={"mode": "advisory", "pending_actions": 2},
        supervisor_status={"runlevel": "DEGRADED"},
        setpoints={
            "core_metrics": {
                "memory_rtt": {
                    "target": 50.0,
                    "max_acceptable": 120.0,
                    "critical_threshold": 500.0,
                },
                "queue_depth": {
                    "target": 5.0,
                    "max_acceptable": 50.0,
                    "critical_threshold": 100.0,
                },
                "plugin_load_success": {
                    "target": 95.0,
                    "min_acceptable": 85.0,
                    "critical_threshold": 70.0,
                },
            }
        },
    )
    diagnosis = build_diagnosis_report(observation)
    causes = {cause.get("category") for cause in diagnosis.get("causes", [])}
    passed = bool(
        observation.get("actions_enabled") is False
        and diagnosis.get("actions_enabled") is False
        and diagnosis.get("summary", {}).get("status") == "causes_identified"
        and {"memory_pressure", "agent_or_kernel_overload", "service_degradation"}
        <= causes
    )
    return IntegrationValidationCheck(
        name="homeostasis_observation_diagnosis",
        passed=passed,
        summary="Homeostasis observes and diagnoses pressure without enabling actions",
        details={
            "observation_phase": observation.get("phase"),
            "diagnosis_phase": diagnosis.get("phase"),
            "risk_level": observation.get("risk", {}).get("level"),
            "cause_count": diagnosis.get("summary", {}).get("cause_count"),
            "causes": sorted(str(cause) for cause in causes if cause),
        },
    )


def _check_maintenance_coordination_chain() -> IntegrationValidationCheck:
    from Aetherra.guardian import IntentDeclaration, evaluate_intent
    from Aetherra.maintenance import (
        MaintenanceDecision,
        MaintenanceEvidence,
        MaintenanceExecution,
        MaintenanceProposal,
        MaintenanceService,
        MaintenanceVerification,
    )

    decision = evaluate_intent(
        IntentDeclaration(
            requester="integration_validation:maintenance",
            subsystem="maintenance",
            action="maintenance.route_proposal",
            target="maintenance:integration_validation",
            purpose="Validate Maintenance routes a proposal only after Guardian and Security",
            capabilities=("maintenance:coordinate",),
            reversible=True,
            rollback_plan="discard the dry-run validation cycle",
            evidence=("integration_validation:maintenance_route",),
            metadata={
                "proposal_id_hash": "integration-validation-proposal",
                "dry_run": True,
            },
        ),
        capability_checker=_integration_capability_checker,
    )

    service = MaintenanceService(autosave=False)
    cycle = service.route_proposal(
        MaintenanceProposal(
            proposal_id="integration-validation-proposal",
            source="self_improvement",
            target_subsystem="memory",
            issue="validation memory pressure",
            proposed_action="dry-run no-op maintenance validation",
            expected_benefit="prove routing contract",
            risk_level="low",
            rollback_plan="no mutation performed",
            approval_required=False,
            evidence=("validation",),
        ),
        observations=[
            MaintenanceEvidence(
                source="homeostasis",
                summary="validation pressure observed",
                severity="warning",
            )
        ],
        diagnosis=MaintenanceEvidence(
            source="self_improvement",
            summary="validation diagnosis produced",
            severity="warning",
        ),
        guardian_decision=MaintenanceDecision(
            status=decision.status.value,
            reason=decision.reason,
            audit_id=decision.audit_id,
        ),
        security_allowed=decision.allowed,
        security_reason="guardian_capability_bridge_satisfied",
        cycle_id="integration-validation-cycle",
    )
    completed = service.record_outcome(
        cycle.cycle_id,
        execution=MaintenanceExecution(
            executor="self_incorporation",
            status="applied",
            summary="dry-run validation action recorded",
            details={"dry_run": True},
        ),
        verification=MaintenanceVerification(
            verifier="homeostasis",
            status="stable",
            baseline_health=0.8,
            post_health=0.8,
            summary="validation health unchanged",
        ),
        learning_record={"outcome": "stable", "dry_run": True},
    )

    passed = bool(
        decision.allowed
        and cycle.can_execute()
        and completed is not None
        and completed.summary()["execution_status"] == "applied"
        and completed.summary()["verification_status"] == "stable"
        and completed.summary()["failures"] == []
    )
    return IntegrationValidationCheck(
        name="maintenance_coordination_chain",
        passed=passed,
        summary="Maintenance coordinates proposal routing and records a dry-run outcome",
        details={
            "guardian_status": decision.status.value,
            "cycle_status": completed.status.value if completed else None,
            "can_execute": cycle.can_execute(),
            "event_count": completed.summary()["event_count"] if completed else 0,
        },
    )


def _check_self_incorporation_scope_and_rollback() -> IntegrationValidationCheck:
    from aetherra_self_incorporation import (
        SelfIncorporationConfig,
        SelfIncorporationService,
    )

    async def _run() -> tuple[dict[str, Any], dict[str, Any]]:
        with tempfile.TemporaryDirectory(prefix="aetherra-selfinc-validation-") as tmp_dir:
            temp_path = Path(tmp_dir)
            config = SelfIncorporationConfig()
            config.hmr_enabled = True
            config.index_db_path = temp_path / "selfinc_index.db"
            config.index_jsonl_path = temp_path / "selfinc_index.jsonl"
            config.audit_db_path = temp_path / "selfinc_audit.db"
            service = SelfIncorporationService(config)

            scope_plan = {
                "plan_id": "integration-validation-scope-lock",
                "status": "ready",
                "actions": [
                    {
                        "action": "register_workflow",
                        "target": {"file_id": "approved-workflow"},
                        "deps": [],
                    }
                ],
            }

            async def scope_plan_runner(include_experimental: bool = False):
                return scope_plan

            async def mutate_after_approval(approved_plan: dict[str, Any]):
                approved_plan["actions"].append(
                    {
                        "action": "register_workflow",
                        "target": {"file_id": "scope-expansion"},
                        "deps": [],
                    }
                )
                return {
                    "overall_score": 0.95,
                    "risk_factors": [],
                    "reasoning": ["validation mutation after approval"],
                }

            service._run_integration_planning = scope_plan_runner  # type: ignore[method-assign]
            service._evaluate_plan_ethics = mutate_after_approval  # type: ignore[method-assign]
            scope_result = await service.trigger_integrate(dry_run=True)

            rollback_plan = {
                "plan_id": "integration-validation-rollback-required",
                "status": "ready",
                "actions": [
                    {
                        "action": "register_plugin",
                        "target": {"file_id": "plugin-needs-hmr-rollback"},
                        "deps": [],
                    }
                ],
            }

            async def rollback_plan_runner(include_experimental: bool = False):
                return rollback_plan

            service._run_integration_planning = rollback_plan_runner  # type: ignore[method-assign]
            service.service_registry = None
            rollback_result = await service.trigger_integrate(dry_run=False)

            return scope_result, rollback_result

    scope_result, rollback_result = asyncio.run(_run())
    passed = bool(
        scope_result.get("ok") is False
        and scope_result.get("status") == "scope_mismatch"
        and scope_result.get("applied") == 0
        and rollback_result.get("ok") is False
        and rollback_result.get("status") == "rollback_unavailable"
        and rollback_result.get("reason")
        == "rollback_unavailable:register_plugin:hmr_controller_unavailable"
    )
    return IntegrationValidationCheck(
        name="self_incorporation_scope_and_rollback",
        passed=passed,
        summary="Self-Incorporation rejects post-approval scope drift and rollback-less mutation",
        details={
            "scope_status": scope_result.get("status"),
            "scope_reason": scope_result.get("reason"),
            "scope_applied": scope_result.get("applied"),
            "rollback_status": rollback_result.get("status"),
            "rollback_reason": rollback_result.get("reason"),
        },
    )


def _check_aether_script_runtime_gate() -> IntegrationValidationCheck:
    from aetherra_script_service import AetherScriptService

    async def _run() -> tuple[dict[str, Any], dict[str, Any], bool]:
        service = AetherScriptService()
        await service.initialize()
        allowed = await service.execute_script_content(
            'goal "integration validation"\nvalidation_value = 1',
            filename="integration_validation.aether",
        )
        with _temporary_env({"AETHERRA_REQUIRE_CAPABILITIES": "1"}):
            denied = await service.execute_script_content(
                'blocked_value = "should-not-execute"',
                filename="blocked_validation.aether",
                context={"_requester": "external-integration-runner"},
            )
        return allowed, denied, "blocked_value" in service._last_ctx

    allowed, denied, blocked_mutated = asyncio.run(_run())
    passed = bool(
        allowed.get("success") is True
        and denied.get("success") is False
        and denied.get("error") == "guardian_denied"
        and not blocked_mutated
    )
    return IntegrationValidationCheck(
        name="aether_script_runtime_gate",
        passed=passed,
        summary="Aether Script allows an internal validation script and blocks strict external execution",
        details={
            "allow_success": allowed.get("success"),
            "deny_error": denied.get("error"),
            "blocked_mutated": blocked_mutated,
        },
    )


def _integration_capability_checker(requester: str, capability: str) -> bool:
    internal_allow = {
        "aether_script:runtime": {"script:run"},
        "integration_validation:maintenance": {"maintenance:coordinate"},
    }
    if capability in internal_allow.get(requester, set()):
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


@contextmanager
def _validation_environment(workspace_root: Path, *, profile: str) -> Iterator[None]:
    updates = {
        "AETHERRA_PROFILE": profile,
        "AETHERRA_GUARDIAN_MODE": "enforcing",
        "AETHERRA_WORKSPACE_ROOT": str(workspace_root),
        "AETHERRA_POLICY_HOME": str(workspace_root / "policy"),
        "AETHERRA_AUDIT": "0",
    }
    with _temporary_env(updates, clear=("AETHERRA_REQUIRE_CAPABILITIES",)):
        yield


@contextmanager
def _temporary_env(
    updates: dict[str, str],
    *,
    clear: tuple[str, ...] = (),
) -> Iterator[None]:
    changed = set(updates) | set(clear)
    previous = {key: os.environ.get(key) for key in changed}
    try:
        for key in clear:
            os.environ.pop(key, None)
        for key, value in updates.items():
            os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main() -> int:
    report = run_integration_validation()
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
