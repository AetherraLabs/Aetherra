from Aetherra.maintenance import (
    MaintenanceCycle,
    MaintenanceCoordinator,
    MaintenanceCycleStatus,
    MaintenanceDecision,
    MaintenanceEvidence,
    MaintenanceExecution,
    MaintenanceProposal,
    MaintenanceVerification,
    get_maintenance_contract,
)


def _diagnosed_cycle() -> MaintenanceCycle:
    cycle = MaintenanceCycle(cycle_id="maint-test")
    cycle.record_observation(
        MaintenanceEvidence(
            source="homeostasis",
            summary="memory latency elevated",
            severity="warning",
        )
    )
    cycle.record_diagnosis(
        MaintenanceEvidence(
            source="self_improvement",
            summary="memory index pressure likely cause",
            severity="warning",
        )
    )
    return cycle


def _proposal() -> MaintenanceProposal:
    return MaintenanceProposal(
        proposal_id="proposal-1",
        source="self_improvement",
        target_subsystem="memory",
        issue="memory latency elevated",
        proposed_action="optimize memory index",
        expected_benefit="lower recall latency",
        risk_level="medium",
        rollback_plan="restore previous index snapshot",
        evidence=("memory latency p95 > target",),
        trace_id="trace-maint-1",
    )


def test_contract_declares_authority_ownership_and_mutation_rule():
    contract = get_maintenance_contract()

    assert contract["authority_ownership"]["maintenance"] == [
        "coordinate",
        "route",
        "record_outcome",
    ]
    assert contract["authority_ownership"]["guardian"] == [
        "approve",
        "deny",
        "contain",
    ]
    assert "Guardian" in contract["mutation_rule"]
    assert "Security" in contract["mutation_rule"]


def test_cycle_cannot_execute_without_guardian_and_security():
    cycle = _diagnosed_cycle()
    cycle.record_proposal(_proposal())

    cycle.record_execution(
        MaintenanceExecution(
            executor="self_incorporation",
            status="applied",
            summary="should not apply",
        )
    )

    assert cycle.status == MaintenanceCycleStatus.EXECUTION_FAILED
    assert cycle.can_execute() is False
    assert cycle.failures[-1]["failure_point"] == "execution_failed"
    assert "missing_guardian_or_security_authorization" in cycle.failures[-1]["reason"]
    assert cycle.events[-1].event_type == "failure_recorded"
    assert cycle.events[-1].details["required_behavior"] == (
        "activate_rollback_if_available"
    )


def test_guardian_denial_terminates_proposal_path():
    cycle = _diagnosed_cycle()
    cycle.record_proposal(_proposal())

    cycle.record_guardian_decision(
        MaintenanceDecision(status="deny", reason="risk too high")
    )

    assert cycle.status == MaintenanceCycleStatus.DENIED
    assert cycle.can_execute() is False
    assert cycle.failures[-1]["failure_point"] == "guardian_denied"


def test_security_block_prevents_execution_after_guardian_allow():
    cycle = _diagnosed_cycle()
    cycle.record_proposal(_proposal())
    cycle.record_guardian_decision(
        MaintenanceDecision(status="allow_limited", reason="bounded maintenance")
    )
    cycle.record_security_enforcement(allowed=False, reason="missing fs:write")

    assert cycle.status == MaintenanceCycleStatus.SECURITY_BLOCKED
    assert cycle.can_execute() is False
    assert cycle.failures[-1]["failure_point"] == "security_blocked"


def test_approved_enforced_cycle_executes_verifies_and_learns():
    cycle = _diagnosed_cycle()
    cycle.record_proposal(_proposal())
    cycle.record_guardian_decision(
        MaintenanceDecision(status="allow_limited", reason="bounded maintenance")
    )
    cycle.record_security_enforcement(allowed=True, reason="capabilities satisfied")

    assert cycle.can_execute() is True

    cycle.record_execution(
        MaintenanceExecution(
            executor="self_incorporation",
            status="applied",
            summary="index optimized",
            rollback_token="rb-1",
        )
    )
    cycle.record_verification(
        MaintenanceVerification(
            verifier="homeostasis",
            status="improved",
            baseline_health=0.75,
            post_health=0.86,
            summary="latency recovered",
        )
    )
    cycle.record_learning({"proposal_id": "proposal-1", "outcome": "improved"})

    assert cycle.status == MaintenanceCycleStatus.LEARNED
    summary = cycle.summary()
    assert summary["can_execute"] is True
    assert summary["execution_status"] == "applied"
    assert summary["verification_status"] == "improved"
    assert summary["event_count"] == 8
    assert summary["last_event"]["event_type"] == "learning_recorded"
    assert summary["failures"] == []

    assert [event.event_type for event in cycle.events] == [
        "observation_recorded",
        "diagnosis_recorded",
        "proposal_recorded",
        "guardian_decision_recorded",
        "security_enforcement_recorded",
        "execution_recorded",
        "verification_recorded",
        "learning_recorded",
    ]


def test_coordinator_routes_allowed_proposal_without_executing():
    coordinator = MaintenanceCoordinator()
    cycle = coordinator.route_proposal(
        _proposal(),
        observations=[
            MaintenanceEvidence(source="homeostasis", summary="memory pressure")
        ],
        diagnosis=MaintenanceEvidence(
            source="self_improvement",
            summary="memory index pressure likely cause",
        ),
        guardian_decision=MaintenanceDecision(
            status="allow_limited",
            reason="bounded maintenance proposal",
            audit_id="audit-1",
        ),
        security_allowed=True,
        security_reason="capabilities satisfied",
        cycle_id="maint-routed-allow",
    )

    assert cycle.cycle_id == "maint-routed-allow"
    assert cycle.status == MaintenanceCycleStatus.SECURITY_ENFORCED
    assert cycle.can_execute() is True
    assert cycle.execution is None
    assert coordinator.get_status()["active_cycles"][0]["can_execute"] is True


def test_coordinator_routes_guardian_denial_as_terminal():
    coordinator = MaintenanceCoordinator()
    cycle = coordinator.route_proposal(
        _proposal(),
        diagnosis=MaintenanceEvidence(
            source="self_improvement",
            summary="memory index pressure likely cause",
        ),
        guardian_decision=MaintenanceDecision(
            status="deny",
            reason="proposal exceeds maintenance scope",
        ),
    )

    assert cycle.status == MaintenanceCycleStatus.DENIED
    assert cycle.can_execute() is False
    assert cycle.failures[-1]["failure_point"] == "guardian_denied"


def test_coordinator_routes_security_block_after_guardian_allow():
    coordinator = MaintenanceCoordinator()
    cycle = coordinator.route_proposal(
        _proposal(),
        diagnosis=MaintenanceEvidence(
            source="self_improvement",
            summary="memory index pressure likely cause",
        ),
        guardian_decision=MaintenanceDecision(
            status="allow_limited",
            reason="bounded maintenance proposal",
        ),
        security_allowed=False,
        security_reason="missing maintenance:execute",
    )

    assert cycle.status == MaintenanceCycleStatus.SECURITY_BLOCKED
    assert cycle.can_execute() is False
    assert cycle.failures[-1]["failure_point"] == "security_blocked"


def test_coordinator_records_execution_verification_and_learning_outcome():
    coordinator = MaintenanceCoordinator()
    routed = coordinator.route_proposal(
        _proposal(),
        diagnosis=MaintenanceEvidence(
            source="self_improvement",
            summary="memory index pressure likely cause",
        ),
        guardian_decision=MaintenanceDecision(
            status="allow_limited",
            reason="bounded maintenance proposal",
        ),
        security_allowed=True,
        security_reason="capabilities satisfied",
        cycle_id="maint-outcome",
    )

    assert routed.can_execute() is True

    completed = coordinator.record_outcome(
        "maint-outcome",
        execution=MaintenanceExecution(
            executor="self_incorporation",
            status="applied",
            summary="memory index optimized",
            rollback_token="rb-outcome",
        ),
        verification=MaintenanceVerification(
            verifier="homeostasis",
            status="improved",
            baseline_health=0.7,
            post_health=0.82,
            summary="health improved after optimization",
        ),
        learning_record={"outcome": "improved", "proposal_id": "proposal-1"},
    )

    assert completed is routed
    assert completed.status == MaintenanceCycleStatus.LEARNED
    assert completed.execution.rollback_token == "rb-outcome"
    assert completed.verification.post_health == 0.82
    assert completed.learning_record["outcome"] == "improved"


def test_coordinator_record_outcome_returns_none_for_unknown_cycle():
    coordinator = MaintenanceCoordinator()

    result = coordinator.record_outcome(
        "missing-cycle",
        execution=MaintenanceExecution(
            executor="self_incorporation",
            status="applied",
            summary="should not be recorded",
        ),
    )

    assert result is None


def test_coordinator_record_outcome_refuses_unapproved_execution():
    coordinator = MaintenanceCoordinator()
    cycle = coordinator.route_proposal(
        _proposal(),
        diagnosis=MaintenanceEvidence(
            source="self_improvement",
            summary="memory index pressure likely cause",
        ),
        cycle_id="maint-unapproved",
    )

    result = coordinator.record_outcome(
        "maint-unapproved",
        execution=MaintenanceExecution(
            executor="self_incorporation",
            status="applied",
            summary="should not apply",
        ),
    )

    assert result is cycle
    assert cycle.status == MaintenanceCycleStatus.EXECUTION_FAILED
    assert cycle.execution is None
    assert cycle.failures[-1]["reason"] == "missing_guardian_or_security_authorization"


def test_cycle_record_round_trip_preserves_events_and_state():
    cycle = _diagnosed_cycle()
    cycle.record_proposal(_proposal())
    cycle.record_guardian_decision(
        MaintenanceDecision(status="allow_limited", reason="bounded maintenance")
    )
    cycle.record_security_enforcement(allowed=True, reason="capabilities satisfied")

    restored = MaintenanceCycle.from_record(cycle.to_record())

    assert restored.cycle_id == cycle.cycle_id
    assert restored.status == MaintenanceCycleStatus.SECURITY_ENFORCED
    assert restored.can_execute() is True
    assert restored.proposal.proposal_id == "proposal-1"
    assert restored.guardian_decision.allowed is True
    assert [event.event_type for event in restored.events] == [
        event.event_type for event in cycle.events
    ]


def test_coordinator_exports_and_loads_cycle_records_with_counts():
    coordinator = MaintenanceCoordinator(max_recent=5)
    allowed = coordinator.route_proposal(
        _proposal(),
        diagnosis=MaintenanceEvidence(
            source="self_improvement",
            summary="memory index pressure likely cause",
        ),
        guardian_decision=MaintenanceDecision(
            status="allow_limited",
            reason="bounded maintenance proposal",
        ),
        security_allowed=True,
        security_reason="capabilities satisfied",
        cycle_id="maint-export-allowed",
    )
    coordinator.record_outcome(
        allowed.cycle_id,
        execution=MaintenanceExecution(
            executor="self_incorporation",
            status="applied",
            summary="memory index optimized",
        ),
        verification=MaintenanceVerification(
            verifier="homeostasis",
            status="improved",
            summary="health improved",
        ),
        learning_record={"outcome": "improved"},
    )
    coordinator.route_proposal(
        _proposal(),
        diagnosis=MaintenanceEvidence(
            source="self_improvement",
            summary="memory index pressure likely cause",
        ),
        guardian_decision=MaintenanceDecision(
            status="deny",
            reason="proposal exceeds maintenance scope",
        ),
        cycle_id="maint-export-denied",
    )

    records = coordinator.export_records()
    restored = MaintenanceCoordinator()
    for record in records:
        restored.load_cycle(record)

    status = restored.get_status()
    assert status["cycle_count"] == 2
    assert status["active_cycle_count"] == 0
    assert status["terminal_cycle_count"] == 2
    assert status["failure_count"] == 1
    assert restored.get_cycle("maint-export-allowed").status == (
        MaintenanceCycleStatus.LEARNED
    )
    assert restored.get_cycle("maint-export-denied").status == (
        MaintenanceCycleStatus.DENIED
    )
