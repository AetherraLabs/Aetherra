"""Tests for SelfImprovementEngine internal metrics counters.

Focus:
- analysis_cycles increments after an analysis run
- suppressed_exceptions increments when an exception occurs inside _analyze_and_improve
- export_internal_metrics returns expected keys
- MetricsService can register and snapshot both engines (smoke)
"""

from __future__ import annotations

# Standard library imports
import asyncio
import sqlite3
from datetime import datetime

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.engine.self_improvement_engine import (
    ImprovementProposal,
    ImprovementType,
    SelfImprovementEngine,
)
from Aetherra.observability.metrics_service import MetricsService


@pytest.mark.asyncio
async def test_analysis_cycle_and_exception_counters_increment():
    eng = SelfImprovementEngine(db_path=":memory:")

    # Force an exception in analysis by monkeypatching pattern analyzer
    def boom(*a, **k):  # noqa: D401 - simple test hook
        raise RuntimeError("inject failure")

    eng.pattern_analyzer.identify_performance_patterns = boom  # type: ignore[assignment]
    before_cycles = eng._analysis_cycles
    before_suppressed = eng._suppressed_exceptions
    await eng._analyze_and_improve()
    assert eng._analysis_cycles == before_cycles + 1
    assert eng._suppressed_exceptions == before_suppressed + 1
    metrics = eng.export_internal_metrics()
    assert {"suppressed_exceptions", "analysis_cycles", "tracked_metrics"}.issubset(
        metrics.keys()
    )


@pytest.mark.asyncio
async def test_metrics_service_snapshot_smoke():
    eng = SelfImprovementEngine(db_path=":memory:")
    svc = MetricsService()
    svc.register_adapter("self_improvement", eng.export_internal_metrics)
    # Use snapshot API (avoid opening port for speed)
    snap = svc.current_snapshot()
    assert "self_improvement" in snap
    assert "analysis_cycles" in snap["self_improvement"]


@pytest.mark.asyncio
async def test_high_confidence_proposals_remain_recommendations_by_default(
    monkeypatch, tmp_path
):
    monkeypatch.delenv("AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT", raising=False)
    eng = SelfImprovementEngine(db_path=str(tmp_path / "self_improvement.db"))
    proposal = ImprovementProposal(
        proposal_id="safe-recommendation",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Recommend a low-risk performance improvement",
        expected_benefit=0.9,
        implementation_cost=0.1,
        risk_level=0.1,
        affected_components=["scheduler"],
        success_criteria=["Latency improves"],
        created_at=datetime.now(),
    )

    await eng._process_proposal(proposal)

    proposals = eng.list_active_proposals()
    assert proposal.status == "active"
    assert proposals[0]["proposal_id"] == "safe-recommendation"
    assert eng.get_improvement_status()["implemented_proposals"] == 0
    assert eng.get_improvement_status()["autonomous_implementation_enabled"] is False


@pytest.mark.asyncio
async def test_auto_implementation_env_is_blocked_without_guardian_path(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT", "1")
    eng = SelfImprovementEngine(db_path=str(tmp_path / "self_improvement.db"))
    proposal = ImprovementProposal(
        proposal_id="legacy-auto-blocked",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Do not auto-implement even with legacy env enabled",
        expected_benefit=0.9,
        implementation_cost=0.1,
        risk_level=0.1,
        affected_components=["scheduler"],
        success_criteria=["Proposal remains reviewable"],
        created_at=datetime.now(),
    )

    await eng._process_proposal(proposal)

    status = eng.get_improvement_status()
    active = eng.get_proposal("legacy-auto-blocked")
    history = eng.get_proposal_history("legacy-auto-blocked")
    assert status["autonomous_implementation_requested"] is True
    assert status["autonomous_implementation_enabled"] is False
    assert status["implementation_authority"] == "guardian_controlled_execution"
    assert status["implemented_proposals"] == 0
    assert active["status"] == "active"
    assert "Guardian-gated" in active["status_reason"]
    assert history[0]["event_type"] == "auto_implementation_blocked"


@pytest.mark.asyncio
async def test_generated_proposals_include_hypothesis_and_simulation(tmp_path):
    eng = SelfImprovementEngine(db_path=str(tmp_path / "self_improvement.db"))

    for value in (85.0, 86.0, 87.5):
        eng.record_performance_metric("cpu_usage", value, "percent")

    await eng._analyze_and_improve()

    proposals = eng.list_active_proposals()
    assert proposals
    proposal = proposals[0]
    assert proposal["issue"] == "CPU utilization is consistently high"
    assert "Scheduler pressure" in proposal["potential_cause"]
    assert proposal["simulation"]["testable"] is True
    assert proposal["simulation"]["rollback_available"] is True
    assert proposal["rollback_plan"]
    assert proposal["readiness_status"] == "candidate"
    assert proposal["readiness_reasons"] == ["ready_for_review"]


@pytest.mark.asyncio
async def test_repeated_analysis_refreshes_existing_proposal(tmp_path):
    eng = SelfImprovementEngine(db_path=str(tmp_path / "self_improvement.db"))

    for value in (85.0, 86.0, 87.5):
        eng.record_performance_metric("cpu_usage", value, "percent")

    await eng._analyze_and_improve()
    await eng._analyze_and_improve()

    proposals = eng.list_active_proposals()
    history = eng.get_proposal_history(proposals[0]["proposal_id"])

    assert len(proposals) == 1
    assert proposals[0]["proposal_id"].startswith("si-")
    assert proposals[0]["occurrence_count"] == 2
    assert proposals[0]["proposal_fingerprint"]
    assert history[0]["event_type"] == "refreshed"
    assert history[1]["event_type"] == "created"


@pytest.mark.asyncio
async def test_dismissed_duplicate_proposal_is_not_reactivated(tmp_path):
    eng = SelfImprovementEngine(db_path=str(tmp_path / "self_improvement.db"))

    for value in (85.0, 86.0, 87.5):
        eng.record_performance_metric("cpu_usage", value, "percent")

    await eng._analyze_and_improve()
    proposal_id = eng.list_active_proposals()[0]["proposal_id"]
    await eng.dismiss_proposal(proposal_id, reason="not now", actor="operator")
    await eng._analyze_and_improve()

    assert eng.list_active_proposals() == []
    assert eng._load_proposal_from_db(proposal_id).status == "dismissed"


@pytest.mark.asyncio
async def test_proposal_result_records_bounded_learning_outcome(tmp_path):
    db_path = tmp_path / "self_improvement.db"
    eng = SelfImprovementEngine(db_path=str(db_path))
    proposal = ImprovementProposal(
        proposal_id="learn-from-result",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Learn from a controlled proposal result",
        expected_benefit=0.8,
        implementation_cost=0.2,
        risk_level=0.1,
        affected_components=["memory"],
        success_criteria=["Outcome is recorded"],
        created_at=datetime.now(),
    )
    await eng._process_proposal(proposal)

    result = await eng.record_proposal_result(
        {
            "proposal_id": "learn-from-result",
            "plan_id": "plan-123",
            "status": "accepted",
            "details": {
                "improvement_achieved": 0.4,
                "raw_payload": "do-not-store-this-value",
            },
        }
    )

    status = eng.get_improvement_status()
    outcome = eng.learning_outcomes[-1]
    assert result["status"] == "ok"
    assert eng.active_proposals["learn-from-result"].status == "accepted"
    assert status["learning_outcomes"] == 1
    assert outcome.improvement_achieved == 0.4
    assert outcome.learning_data["details_keys"] == [
        "improvement_achieved",
        "raw_payload",
    ]
    assert "do-not-store-this-value" not in str(outcome.learning_data)
    outcomes = eng.list_learning_outcomes(
        proposal_id="learn-from-result",
        status="accepted",
    )
    summary = eng.get_learning_summary(
        proposal_id="learn-from-result",
        status="accepted",
    )
    assert outcomes == [
        {
            "session_id": outcome.session_id,
            "method": "reinforcement",
            "target_component": "memory",
            "improvement_achieved": 0.4,
            "confidence": 1.0,
            "timestamp": outcome.timestamp.isoformat(),
            "proposal_id": "learn-from-result",
            "plan_id": "plan-123",
            "status": "accepted",
            "details_keys": ["improvement_achieved", "raw_payload"],
        }
    ]
    assert summary["total_outcomes"] == 1
    assert summary["by_status"] == {"accepted": 1}
    assert "do-not-store-this-value" not in str(outcomes)
    reloaded = SelfImprovementEngine(db_path=str(db_path))
    assert reloaded.get_improvement_status()["learning_outcomes"] == 1
    assert reloaded.list_learning_outcomes(proposal_id="learn-from-result") == outcomes


@pytest.mark.asyncio
async def test_proposal_result_rejects_invalid_status_without_mutation(tmp_path):
    eng = SelfImprovementEngine(db_path=str(tmp_path / "self_improvement.db"))
    proposal = ImprovementProposal(
        proposal_id="invalid-result-status",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Reject malformed result status",
        expected_benefit=0.8,
        implementation_cost=0.2,
        risk_level=0.1,
        affected_components=["memory"],
        success_criteria=["Invalid results do not mutate state"],
        created_at=datetime.now(),
    )
    await eng._process_proposal(proposal)

    result = await eng.record_proposal_result(
        {
            "proposal_id": "invalid-result-status",
            "status": "active",
            "details": {"reason": "status injection attempt"},
        }
    )

    assert result["status"] == "error"
    assert result["error"] == "invalid proposal result status"
    assert eng.get_proposal("invalid-result-status")["status"] == "active"
    assert eng.get_improvement_status()["learning_outcomes"] == 0
    assert [
        event["event_type"]
        for event in eng.get_proposal_history("invalid-result-status")
    ] == ["created"]


@pytest.mark.asyncio
async def test_proposal_result_normalizes_status_and_bounds_detail_keys(tmp_path):
    eng = SelfImprovementEngine(db_path=str(tmp_path / "self_improvement.db"))
    proposal = ImprovementProposal(
        proposal_id="bounded-result-keys",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Bound result detail keys",
        expected_benefit=0.8,
        implementation_cost=0.2,
        risk_level=0.1,
        affected_components=["memory"],
        success_criteria=["Details are bounded"],
        created_at=datetime.now(),
    )
    await eng._process_proposal(proposal)
    details = {f"key-{index:03d}-{'x' * 160}": index for index in range(75)}
    details["improvement_achieved"] = 0.6

    result = await eng.record_proposal_result(
        {
            "proposal_id": "bounded-result-keys",
            "plan_id": "plan-bounded",
            "status": "success",
            "details": details,
        }
    )

    outcome = eng.list_learning_outcomes(proposal_id="bounded-result-keys")[0]
    assert result["recorded_status"] == "accepted"
    assert len(outcome["details_keys"]) == 50
    assert all(len(key) <= 120 for key in outcome["details_keys"])
    assert "improvement_achieved" in outcome["details_keys"]
    assert outcome["status"] == "accepted"


@pytest.mark.asyncio
async def test_reviewable_proposals_reload_from_database(tmp_path):
    db_path = tmp_path / "self_improvement.db"
    eng = SelfImprovementEngine(db_path=str(db_path))
    proposal = ImprovementProposal(
        proposal_id="reload-reviewable",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Persist active proposal for review",
        expected_benefit=0.8,
        implementation_cost=0.2,
        risk_level=0.1,
        affected_components=["kernel"],
        success_criteria=["Proposal remains reviewable after restart"],
        created_at=datetime.now(),
        issue="Kernel latency is elevated",
        potential_cause="Queue contention",
        proposed_change="Review queue scheduling",
        evidence=["metric:queue_depth"],
        simulation={"confidence": 0.8, "testable": True},
        rollback_plan="Restore prior scheduler settings",
    )
    await eng._process_proposal(proposal)

    reloaded = SelfImprovementEngine(db_path=str(db_path))
    proposals = reloaded.list_active_proposals()

    assert proposals[0]["proposal_id"] == "reload-reviewable"
    assert proposals[0]["issue"] == "Kernel latency is elevated"
    assert proposals[0]["simulation"]["confidence"] == 0.8
    assert reloaded.get_proposal("reload-reviewable")["proposal_id"] == (
        "reload-reviewable"
    )
    assert reloaded.get_proposal("missing") is None


@pytest.mark.asyncio
async def test_proposal_review_filters_and_summary(tmp_path):
    eng = SelfImprovementEngine(db_path=str(tmp_path / "self_improvement.db"))
    proposals = [
        ImprovementProposal(
            proposal_id="review-low",
            improvement_type=ImprovementType.PERFORMANCE,
            description="Low-risk performance proposal",
            expected_benefit=0.8,
            implementation_cost=0.2,
            risk_level=0.1,
            affected_components=["kernel"],
            success_criteria=["Review low risk"],
            created_at=datetime.now(),
            evidence=["metric:kernel", "trend:degrading"],
            simulation={"confidence": 0.9, "testable": True, "rollback_available": True},
            rollback_plan="Restore prior settings",
        ),
        ImprovementProposal(
            proposal_id="review-medium",
            improvement_type=ImprovementType.RELIABILITY,
            description="Medium-risk reliability proposal",
            expected_benefit=0.8,
            implementation_cost=0.2,
            risk_level=0.5,
            affected_components=["memory"],
            success_criteria=["Review medium risk"],
            created_at=datetime.now(),
            evidence=["metric:memory", "trend:degrading"],
            simulation={"confidence": 0.7, "testable": False},
        ),
    ]
    for proposal in proposals:
        await eng._process_proposal(proposal)

    low_risk = eng.list_active_proposals(max_risk=0.2)
    confident = eng.list_active_proposals(min_confidence=0.8)
    reliability = eng.list_active_proposals(improvement_type="reliability")
    candidates = eng.list_active_proposals(readiness_status="candidate")
    summary = eng.get_review_summary()

    assert [proposal["proposal_id"] for proposal in low_risk] == ["review-low"]
    assert [proposal["proposal_id"] for proposal in confident] == ["review-low"]
    assert [proposal["proposal_id"] for proposal in reliability] == ["review-medium"]
    assert [proposal["proposal_id"] for proposal in candidates] == ["review-low"]
    assert summary["total_reviewable"] == 2
    assert summary["by_type"]["performance"] == 1
    assert summary["by_type"]["reliability"] == 1
    assert summary["by_readiness"]["candidate"] == 1
    assert summary["by_readiness"]["blocked"] == 1
    assert summary["risk_bands"] == {"low": 1, "medium": 1, "high": 0}


@pytest.mark.asyncio
async def test_proposal_readiness_classification(tmp_path):
    eng = SelfImprovementEngine(db_path=str(tmp_path / "self_improvement.db"))
    candidate = ImprovementProposal(
        proposal_id="readiness-candidate",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Ready candidate",
        expected_benefit=0.8,
        implementation_cost=0.2,
        risk_level=0.1,
        affected_components=["kernel"],
        success_criteria=["Ready"],
        created_at=datetime.now(),
        evidence=["metric:latency", "trend:degrading"],
        simulation={"confidence": 0.8, "testable": True, "rollback_available": True},
        rollback_plan="Restore prior state",
    )
    needs_evidence = ImprovementProposal(
        proposal_id="readiness-evidence",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Needs more evidence",
        expected_benefit=0.8,
        implementation_cost=0.2,
        risk_level=0.1,
        affected_components=["memory"],
        success_criteria=["More evidence"],
        created_at=datetime.now(),
        evidence=["metric:memory"],
        simulation={"confidence": 0.7, "testable": True, "rollback_available": True},
        rollback_plan="Restore memory setting",
    )
    blocked = ImprovementProposal(
        proposal_id="readiness-blocked",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Blocked proposal",
        expected_benefit=0.8,
        implementation_cost=0.2,
        risk_level=0.1,
        affected_components=["agent"],
        success_criteria=["Blocked"],
        created_at=datetime.now(),
        evidence=["metric:agent", "trend:degrading"],
        simulation={"confidence": 0.8, "testable": False},
    )

    for proposal in (candidate, needs_evidence, blocked):
        await eng._process_proposal(proposal)

    by_id = {proposal["proposal_id"]: proposal for proposal in eng.list_active_proposals()}
    assert by_id["readiness-candidate"]["readiness_status"] == "candidate"
    assert by_id["readiness-evidence"]["readiness_status"] == "needs_evidence"
    assert by_id["readiness-evidence"]["readiness_reasons"] == ["evidence_sparse"]
    assert by_id["readiness-blocked"]["readiness_status"] == "blocked"
    assert "not_testable" in by_id["readiness-blocked"]["readiness_reasons"]


@pytest.mark.asyncio
async def test_terminal_proposals_do_not_reload_for_review(tmp_path):
    db_path = tmp_path / "self_improvement.db"
    eng = SelfImprovementEngine(db_path=str(db_path))
    proposal = ImprovementProposal(
        proposal_id="reload-terminal",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Terminal proposal should not reload",
        expected_benefit=0.8,
        implementation_cost=0.2,
        risk_level=0.1,
        affected_components=["memory"],
        success_criteria=["Terminal status is hidden from active review"],
        created_at=datetime.now(),
    )
    await eng._process_proposal(proposal)
    await eng.record_proposal_result(
        {
            "proposal_id": "reload-terminal",
            "plan_id": "plan-terminal",
            "status": "accepted",
            "details": {"improvement_achieved": 0.2},
        }
    )

    reloaded = SelfImprovementEngine(db_path=str(db_path))

    assert reloaded.list_active_proposals() == []


@pytest.mark.asyncio
async def test_proposal_lifecycle_dismiss_and_reopen(tmp_path):
    db_path = tmp_path / "self_improvement.db"
    eng = SelfImprovementEngine(db_path=str(db_path))
    proposal = ImprovementProposal(
        proposal_id="review-lifecycle",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Manage proposal review lifecycle",
        expected_benefit=0.8,
        implementation_cost=0.2,
        risk_level=0.1,
        affected_components=["scheduler"],
        success_criteria=["Proposal can be dismissed and reopened"],
        created_at=datetime.now(),
    )
    await eng._process_proposal(proposal)

    dismissed = await eng.dismiss_proposal(
        "review-lifecycle",
        reason="not needed now",
        actor="operator",
    )
    after_dismiss_reload = SelfImprovementEngine(db_path=str(db_path))
    assert after_dismiss_reload.list_active_proposals() == []

    assert dismissed["status"] == "ok"
    assert eng.list_active_proposals() == []
    dismiss_history = eng.get_proposal_history("review-lifecycle")
    assert dismiss_history[0]["event_type"] == "dismissed"
    assert dismiss_history[0]["actor"] == "operator"
    assert dismiss_history[0]["reason"] == "not needed now"

    reopened = await after_dismiss_reload.reopen_proposal(
        "review-lifecycle",
        reason="review again",
        actor="operator",
    )

    assert reopened["status"] == "ok"
    assert after_dismiss_reload.get_proposal("review-lifecycle")["status"] == "active"
    assert after_dismiss_reload.get_proposal("review-lifecycle")["status_reason"] == (
        "review again"
    )
    reopen_history = after_dismiss_reload.get_proposal_history("review-lifecycle")
    assert [event["event_type"] for event in reopen_history[:2]] == [
        "reopened",
        "dismissed",
    ]


@pytest.mark.asyncio
async def test_proposal_lifecycle_rejects_terminal_state_reopen(tmp_path):
    db_path = tmp_path / "self_improvement.db"
    eng = SelfImprovementEngine(db_path=str(db_path))
    proposal = ImprovementProposal(
        proposal_id="terminal-lifecycle",
        improvement_type=ImprovementType.PERFORMANCE,
        description="Do not reopen accepted proposal",
        expected_benefit=0.8,
        implementation_cost=0.2,
        risk_level=0.1,
        affected_components=["memory"],
        success_criteria=["Terminal proposal stays terminal"],
        created_at=datetime.now(),
    )
    await eng._process_proposal(proposal)
    await eng.record_proposal_result(
        {
            "proposal_id": "terminal-lifecycle",
            "plan_id": "plan-terminal",
            "status": "accepted",
            "details": {},
        }
    )

    result = await eng.reopen_proposal("terminal-lifecycle", reason="try reopen")

    assert result["status"] == "invalid_state"
    assert result["current_status"] == "accepted"


def test_existing_proposal_database_schema_is_migrated(tmp_path):
    db_path = tmp_path / "legacy_self_improvement.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE improvement_proposals (
                proposal_id TEXT PRIMARY KEY,
                improvement_type TEXT NOT NULL,
                description TEXT NOT NULL,
                expected_benefit REAL NOT NULL,
                implementation_cost REAL NOT NULL,
                risk_level REAL NOT NULL,
                affected_components TEXT NOT NULL,
                success_criteria TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                implemented_at TEXT,
                outcome TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

    SelfImprovementEngine(db_path=str(db_path))
    migrated = sqlite3.connect(db_path)
    try:
        columns = {
            row[1]
            for row in migrated.execute(
                "PRAGMA table_info(improvement_proposals)"
            ).fetchall()
        }
    finally:
        migrated.close()

    assert {
        "issue",
        "potential_cause",
        "proposed_change",
        "evidence",
        "simulation",
        "rollback_plan",
        "status_reason",
        "updated_at",
        "proposal_fingerprint",
        "occurrence_count",
        "readiness_status",
        "readiness_reasons",
    }.issubset(columns)


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(test_analysis_cycle_and_exception_counters_increment())
