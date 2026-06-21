# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Thin Maintenance cycle coordinator.

Maintenance coordinates the operational loop; it does not own observation,
diagnosis, approval, enforcement, execution, or verification authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


AUTHORITY_OWNERSHIP: dict[str, tuple[str, ...]] = {
    "homeostasis": ("observe", "verify"),
    "self_improvement": ("diagnose", "propose"),
    "guardian": ("approve", "deny", "contain"),
    "security": ("enforce",),
    "self_incorporation": ("execute",),
    "maintenance": ("coordinate", "route", "record_outcome"),
}

FAILURE_HANDLING: dict[str, str] = {
    "observation_failed": "continue_degraded_visibility",
    "diagnosis_failed": "no_proposal_generated",
    "proposal_failed": "no_change_occurs",
    "guardian_denied": "terminate_proposal",
    "guardian_contained": "stop_and_apply_containment",
    "security_blocked": "terminate_execution",
    "execution_failed": "activate_rollback_if_available",
    "verification_failed": "escalate_to_homeostasis_and_guardian",
    "learning_failed": "preserve_raw_outcome",
}

MAINTENANCE_LOOP: tuple[dict[str, str], ...] = (
    {
        "phase": "observe",
        "owner": "homeostasis",
        "authority": "observe",
        "description": "collect system and runtime health signals",
    },
    {
        "phase": "diagnose",
        "owner": "self_improvement",
        "authority": "diagnose",
        "description": "identify degradation, bottlenecks, and likely causes",
    },
    {
        "phase": "propose",
        "owner": "self_improvement",
        "authority": "propose",
        "description": "create structured improvement proposals",
    },
    {
        "phase": "review",
        "owner": "guardian",
        "authority": "approve",
        "description": "approve, deny, require approval, or contain",
    },
    {
        "phase": "enforce",
        "owner": "security",
        "authority": "enforce",
        "description": "enforce capabilities, sandboxing, signing, network, and audit",
    },
    {
        "phase": "execute",
        "owner": "self_incorporation",
        "authority": "execute",
        "description": "apply only approved changes through guarded execution paths",
    },
    {
        "phase": "verify",
        "owner": "homeostasis",
        "authority": "verify",
        "description": "compare before and after health and detect regressions",
    },
    {
        "phase": "learn",
        "owner": "maintenance",
        "authority": "record_outcome",
        "description": "record outcome evidence for future confidence and audit trails",
    },
)


class MaintenanceCycleStatus(StrEnum):
    """Lifecycle status for a single Maintenance cycle."""

    CREATED = "created"
    OBSERVED = "observed"
    OBSERVATION_DEGRADED = "observation_degraded"
    DIAGNOSED = "diagnosed"
    PROPOSED = "proposed"
    APPROVED = "approved"
    DENIED = "denied"
    CONTAINED = "contained"
    SECURITY_ENFORCED = "security_enforced"
    SECURITY_BLOCKED = "security_blocked"
    EXECUTED = "executed"
    EXECUTION_FAILED = "execution_failed"
    VERIFIED = "verified"
    VERIFICATION_FAILED = "verification_failed"
    LEARNED = "learned"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass(slots=True)
class MaintenanceEvidence:
    """Observation or diagnostic evidence captured from an owning subsystem."""

    source: str
    summary: str
    severity: str = "info"
    details: dict[str, Any] = field(default_factory=dict)
    observed_at: str = field(default_factory=_utc_now)


@dataclass(slots=True)
class MaintenanceEvent:
    """Append-only event record for a Maintenance cycle."""

    event_type: str
    summary: str
    source: str = "maintenance"
    details: dict[str, Any] = field(default_factory=dict)
    recorded_at: str = field(default_factory=_utc_now)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> MaintenanceEvent:
        return cls(
            event_type=str(record.get("event_type") or "unknown"),
            summary=str(record.get("summary") or ""),
            source=str(record.get("source") or "maintenance"),
            details=dict(record.get("details") or {}),
            recorded_at=str(record.get("recorded_at") or _utc_now()),
        )


@dataclass(slots=True)
class MaintenanceProposal:
    """Structured proposal produced by Self-Improvement or a diagnostic tool."""

    proposal_id: str
    source: str
    target_subsystem: str
    issue: str
    proposed_action: str
    expected_benefit: str
    risk_level: str
    rollback_plan: str
    approval_required: bool = True
    evidence: tuple[str, ...] = ()
    trace_id: str | None = None


@dataclass(slots=True)
class MaintenanceDecision:
    """Guardian decision summary for a Maintenance proposal."""

    status: str
    reason: str
    audit_id: str | None = None
    containment_actions: tuple[str, ...] = ()
    decided_at: str = field(default_factory=_utc_now)

    @property
    def allowed(self) -> bool:
        return self.status in {"allow", "allow_limited"}

    @property
    def denied(self) -> bool:
        return self.status == "deny"

    @property
    def contained(self) -> bool:
        return self.status == "contain"


@dataclass(slots=True)
class MaintenanceExecution:
    """Execution result from Self-Incorporation or a guarded maintenance tool."""

    executor: str
    status: str
    summary: str
    rollback_token: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    executed_at: str = field(default_factory=_utc_now)

    @property
    def succeeded(self) -> bool:
        return self.status in {"applied", "accepted", "succeeded", "success"}


@dataclass(slots=True)
class MaintenanceVerification:
    """Homeostasis verification of an approved Maintenance outcome."""

    verifier: str
    status: str
    baseline_health: float | None = None
    post_health: float | None = None
    summary: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    verified_at: str = field(default_factory=_utc_now)

    @property
    def passed(self) -> bool:
        return self.status in {"passed", "stable", "improved"}


@dataclass(slots=True)
class MaintenanceCycle:
    """Coordinate one Observe -> Learn maintenance loop."""

    cycle_id: str = field(default_factory=lambda: f"maint-{uuid4().hex[:12]}")
    status: MaintenanceCycleStatus = MaintenanceCycleStatus.CREATED
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)
    observations: list[MaintenanceEvidence] = field(default_factory=list)
    diagnosis: MaintenanceEvidence | None = None
    proposal: MaintenanceProposal | None = None
    guardian_decision: MaintenanceDecision | None = None
    security_enforced: bool = False
    security_reason: str | None = None
    execution: MaintenanceExecution | None = None
    verification: MaintenanceVerification | None = None
    learning_record: dict[str, Any] | None = None
    failures: list[dict[str, str]] = field(default_factory=list)
    events: list[MaintenanceEvent] = field(default_factory=list)

    def record_observation(self, evidence: MaintenanceEvidence) -> None:
        self.observations.append(evidence)
        self._event(
            "observation_recorded",
            evidence.summary,
            source=evidence.source,
            details={"severity": evidence.severity},
        )
        self._set_status(MaintenanceCycleStatus.OBSERVED)

    def record_observation_failure(self, reason: str) -> None:
        self._fail("observation_failed", reason)
        self._set_status(MaintenanceCycleStatus.OBSERVATION_DEGRADED)

    def record_diagnosis(self, diagnosis: MaintenanceEvidence) -> None:
        self.diagnosis = diagnosis
        self._event(
            "diagnosis_recorded",
            diagnosis.summary,
            source=diagnosis.source,
            details={"severity": diagnosis.severity},
        )
        self._set_status(MaintenanceCycleStatus.DIAGNOSED)

    def record_diagnosis_failure(self, reason: str) -> None:
        self._fail("diagnosis_failed", reason)

    def record_proposal(self, proposal: MaintenanceProposal) -> None:
        if self.diagnosis is None:
            self._fail("proposal_failed", "missing_diagnosis")
            return
        self.proposal = proposal
        self._event(
            "proposal_recorded",
            proposal.issue,
            source=proposal.source,
            details={
                "proposal_id": proposal.proposal_id,
                "target_subsystem": proposal.target_subsystem,
                "risk_level": proposal.risk_level,
                "approval_required": proposal.approval_required,
            },
        )
        self._set_status(MaintenanceCycleStatus.PROPOSED)

    def record_guardian_decision(self, decision: MaintenanceDecision) -> None:
        self.guardian_decision = decision
        self._event(
            "guardian_decision_recorded",
            decision.reason,
            source="guardian",
            details={
                "status": decision.status,
                "audit_id": decision.audit_id,
                "containment_actions": list(decision.containment_actions),
            },
        )
        if decision.contained:
            self._fail("guardian_contained", decision.reason)
            self._set_status(MaintenanceCycleStatus.CONTAINED)
        elif decision.denied:
            self._fail("guardian_denied", decision.reason)
            self._set_status(MaintenanceCycleStatus.DENIED)
        elif decision.allowed:
            self._set_status(MaintenanceCycleStatus.APPROVED)
        else:
            self._fail("guardian_denied", decision.reason)
            self._set_status(MaintenanceCycleStatus.DENIED)

    def record_security_enforcement(self, *, allowed: bool, reason: str) -> None:
        self.security_enforced = bool(allowed)
        self.security_reason = reason
        self._event(
            "security_enforcement_recorded",
            reason,
            source="security",
            details={"allowed": bool(allowed)},
        )
        if allowed:
            self._set_status(MaintenanceCycleStatus.SECURITY_ENFORCED)
            return
        self._fail("security_blocked", reason)
        self._set_status(MaintenanceCycleStatus.SECURITY_BLOCKED)

    def can_execute(self) -> bool:
        return bool(
            self.proposal
            and self.guardian_decision
            and self.guardian_decision.allowed
            and self.security_enforced
        )

    def record_execution(self, execution: MaintenanceExecution) -> None:
        if not self.can_execute():
            self._fail("execution_failed", "missing_guardian_or_security_authorization")
            self._set_status(MaintenanceCycleStatus.EXECUTION_FAILED)
            return
        self.execution = execution
        self._event(
            "execution_recorded",
            execution.summary,
            source=execution.executor,
            details={
                "status": execution.status,
                "rollback_token": execution.rollback_token,
            },
        )
        if execution.succeeded:
            self._set_status(MaintenanceCycleStatus.EXECUTED)
            return
        self._fail("execution_failed", execution.summary)
        self._set_status(MaintenanceCycleStatus.EXECUTION_FAILED)

    def record_verification(self, verification: MaintenanceVerification) -> None:
        self.verification = verification
        self._event(
            "verification_recorded",
            verification.summary or verification.status,
            source=verification.verifier,
            details={
                "status": verification.status,
                "baseline_health": verification.baseline_health,
                "post_health": verification.post_health,
            },
        )
        if verification.passed:
            self._set_status(MaintenanceCycleStatus.VERIFIED)
            return
        self._fail("verification_failed", verification.summary or verification.status)
        self._set_status(MaintenanceCycleStatus.VERIFICATION_FAILED)

    def record_learning(self, record: dict[str, Any]) -> None:
        if self.verification is None:
            self._fail("learning_failed", "missing_verification")
            return
        self.learning_record = dict(record)
        self._event(
            "learning_recorded",
            str(record.get("outcome") or "learning record stored"),
            source="maintenance",
            details={"keys": sorted(str(key) for key in record.keys())},
        )
        self._set_status(MaintenanceCycleStatus.LEARNED)

    def to_record(self) -> dict[str, Any]:
        """Return a JSON-safe cycle record."""

        return asdict(self)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> MaintenanceCycle:
        """Rehydrate a cycle from a JSON-safe record."""

        cycle = cls(
            cycle_id=str(record.get("cycle_id") or f"maint-{uuid4().hex[:12]}"),
            status=MaintenanceCycleStatus(
                str(record.get("status") or MaintenanceCycleStatus.CREATED.value)
            ),
            created_at=str(record.get("created_at") or _utc_now()),
            updated_at=str(record.get("updated_at") or _utc_now()),
        )
        cycle.observations = [
            MaintenanceEvidence(**item)
            for item in record.get("observations", [])
            if isinstance(item, dict)
        ]
        diagnosis = record.get("diagnosis")
        if isinstance(diagnosis, dict):
            cycle.diagnosis = MaintenanceEvidence(**diagnosis)
        proposal = record.get("proposal")
        if isinstance(proposal, dict):
            proposal = {
                **proposal,
                "evidence": tuple(proposal.get("evidence") or ()),
            }
            cycle.proposal = MaintenanceProposal(**proposal)
        decision = record.get("guardian_decision")
        if isinstance(decision, dict):
            decision = {
                **decision,
                "containment_actions": tuple(decision.get("containment_actions") or ()),
            }
            cycle.guardian_decision = MaintenanceDecision(**decision)
        cycle.security_enforced = bool(record.get("security_enforced", False))
        security_reason = record.get("security_reason")
        cycle.security_reason = str(security_reason) if security_reason is not None else None
        execution = record.get("execution")
        if isinstance(execution, dict):
            cycle.execution = MaintenanceExecution(**execution)
        verification = record.get("verification")
        if isinstance(verification, dict):
            cycle.verification = MaintenanceVerification(**verification)
        learning_record = record.get("learning_record")
        if isinstance(learning_record, dict):
            cycle.learning_record = dict(learning_record)
        cycle.failures = [
            {
                str(key): str(value)
                for key, value in item.items()
            }
            for item in record.get("failures", [])
            if isinstance(item, dict)
        ]
        cycle.events = [
            MaintenanceEvent.from_record(item)
            for item in record.get("events", [])
            if isinstance(item, dict)
        ]
        return cycle

    def summary(self) -> dict[str, Any]:
        """Return a compact status summary for APIs and dashboards."""

        return {
            "cycle_id": self.cycle_id,
            "status": self.status.value,
            "observations": len(self.observations),
            "has_diagnosis": self.diagnosis is not None,
            "has_proposal": self.proposal is not None,
            "guardian_status": (
                self.guardian_decision.status if self.guardian_decision else None
            ),
            "security_enforced": self.security_enforced,
            "can_execute": self.can_execute(),
            "execution_status": self.execution.status if self.execution else None,
            "verification_status": self.verification.status if self.verification else None,
            "event_count": len(self.events),
            "last_event": asdict(self.events[-1]) if self.events else None,
            "failures": list(self.failures),
            "updated_at": self.updated_at,
        }

    def _fail(self, failure_point: str, reason: str) -> None:
        required_behavior = FAILURE_HANDLING.get(failure_point, "record_failure")
        self.failures.append(
            {
                "failure_point": failure_point,
                "required_behavior": required_behavior,
                "reason": reason,
                "recorded_at": _utc_now(),
            }
        )
        self._event(
            "failure_recorded",
            reason,
            source="maintenance",
            details={
                "failure_point": failure_point,
                "required_behavior": required_behavior,
            },
        )
        self.updated_at = _utc_now()

    def _set_status(self, status: MaintenanceCycleStatus) -> None:
        self.status = status
        self.updated_at = _utc_now()

    def _event(
        self,
        event_type: str,
        summary: str,
        *,
        source: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.events.append(
            MaintenanceEvent(
                event_type=event_type,
                summary=summary,
                source=source,
                details=dict(details or {}),
            )
        )
        self.updated_at = _utc_now()


def get_maintenance_contract() -> dict[str, Any]:
    """Return the stable Maintenance authority and failure-handling contract."""

    return {
        "authority_ownership": {
            owner: list(authorities)
            for owner, authorities in AUTHORITY_OWNERSHIP.items()
        },
        "failure_handling": dict(FAILURE_HANDLING),
        "loop": get_maintenance_loop(),
        "mutation_rule": (
            "execution requires proposal, Guardian allow/allow_limited, "
            "and Security enforcement"
        ),
    }


def get_maintenance_loop() -> list[dict[str, str]]:
    """Return the stable Maintenance phase ownership contract."""

    return [dict(phase) for phase in MAINTENANCE_LOOP]


class MaintenanceCoordinator:
    """In-memory coordinator for Maintenance cycle state.

    This class tracks and reports cycles. It intentionally does not observe,
    diagnose, approve, enforce, execute, or verify on behalf of other systems.
    """

    def __init__(self, *, max_recent: int = 50) -> None:
        self.max_recent = max(1, int(max_recent))
        self._cycles: dict[str, MaintenanceCycle] = {}
        self._recent_ids: list[str] = []

    def create_cycle(self, cycle_id: str | None = None) -> MaintenanceCycle:
        cycle = MaintenanceCycle(cycle_id=cycle_id or f"maint-{uuid4().hex[:12]}")
        self._cycles[cycle.cycle_id] = cycle
        self._recent_ids.append(cycle.cycle_id)
        if len(self._recent_ids) > self.max_recent:
            old_id = self._recent_ids.pop(0)
            self._cycles.pop(old_id, None)
        return cycle

    def get_cycle(self, cycle_id: str) -> MaintenanceCycle | None:
        return self._cycles.get(cycle_id)

    def load_cycle(self, record: dict[str, Any]) -> MaintenanceCycle:
        """Load a previously serialized cycle record into the coordinator."""

        cycle = MaintenanceCycle.from_record(record)
        self._cycles[cycle.cycle_id] = cycle
        if cycle.cycle_id in self._recent_ids:
            self._recent_ids.remove(cycle.cycle_id)
        self._recent_ids.append(cycle.cycle_id)
        if len(self._recent_ids) > self.max_recent:
            old_id = self._recent_ids.pop(0)
            self._cycles.pop(old_id, None)
        return cycle

    def route_proposal(
        self,
        proposal: MaintenanceProposal,
        *,
        diagnosis: MaintenanceEvidence,
        observations: list[MaintenanceEvidence] | None = None,
        guardian_decision: MaintenanceDecision | None = None,
        security_allowed: bool | None = None,
        security_reason: str | None = None,
        cycle_id: str | None = None,
    ) -> MaintenanceCycle:
        """Create a cycle and record proposal routing outcomes.

        Guardian and Security decisions are inputs, not decisions made by
        Maintenance. This helper gives callers one consistent record of the
        route without crossing authority boundaries.
        """

        cycle = self.create_cycle(cycle_id)
        for observation in observations or []:
            cycle.record_observation(observation)
        cycle.record_diagnosis(diagnosis)
        cycle.record_proposal(proposal)
        if guardian_decision is not None:
            cycle.record_guardian_decision(guardian_decision)
        if security_allowed is not None:
            cycle.record_security_enforcement(
                allowed=security_allowed,
                reason=security_reason or "security_result_recorded",
            )
        return cycle

    def record_outcome(
        self,
        cycle_id: str,
        *,
        execution: MaintenanceExecution,
        verification: MaintenanceVerification | None = None,
        learning_record: dict[str, Any] | None = None,
    ) -> MaintenanceCycle | None:
        """Record execution, verification, and learning for an existing cycle."""

        cycle = self.get_cycle(cycle_id)
        if cycle is None:
            return None
        cycle.record_execution(execution)
        if verification is not None:
            cycle.record_verification(verification)
        if learning_record is not None:
            cycle.record_learning(learning_record)
        return cycle

    def get_status(self) -> dict[str, Any]:
        recent = [
            self._cycles[cycle_id].summary()
            for cycle_id in reversed(self._recent_ids)
            if cycle_id in self._cycles
        ]
        active = [
            item
            for item in recent
            if item["status"]
            not in {
                MaintenanceCycleStatus.DENIED.value,
                MaintenanceCycleStatus.CONTAINED.value,
                MaintenanceCycleStatus.EXECUTION_FAILED.value,
                MaintenanceCycleStatus.VERIFICATION_FAILED.value,
                MaintenanceCycleStatus.LEARNED.value,
            }
        ]
        return {
            "available": True,
            "coordinator": "maintenance",
            "cycle_count": len(self._cycles),
            "active_cycle_count": len(active),
            "terminal_cycle_count": len(recent) - len(active),
            "failure_count": sum(len(cycle.failures) for cycle in self._cycles.values()),
            "active_cycles": active,
            "recent_cycles": recent[: self.max_recent],
            "contract": get_maintenance_contract(),
        }

    def export_records(self) -> list[dict[str, Any]]:
        """Export recent cycle records for an approved persistence layer."""

        return [
            self._cycles[cycle_id].to_record()
            for cycle_id in self._recent_ids
            if cycle_id in self._cycles
        ]
