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


@pytest.mark.asyncio
async def test_proposal_result_records_bounded_learning_outcome(tmp_path):
    eng = SelfImprovementEngine(db_path=str(tmp_path / "self_improvement.db"))
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
    }.issubset(columns)


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(test_analysis_cycle_and_exception_counters_increment())
