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


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(test_analysis_cycle_and_exception_counters_increment())
