import asyncio
from pathlib import Path

import pytest

from Aetherra.aetherra_core.engine.self_improvement_engine import SelfImprovementEngine


@pytest.mark.asyncio
async def test_self_improvement_demo_runs(tmp_path: Path):
    db = tmp_path / "demo.db"
    engine = SelfImprovementEngine(db_path=str(db))
    await engine.start_improvement_cycle()

    # Record a couple of metrics and allow loop once
    engine.record_performance_metric("response_time", 120.0, "ms")
    engine.record_performance_metric("cpu_usage", 70.0, "percent")
    await asyncio.sleep(0.2)

    status = engine.get_improvement_status()
    assert isinstance(status, dict)
    assert "tracked_metrics" in status

    trends = engine.get_metric_trends()
    assert isinstance(trends, dict)

    await engine.stop_improvement_cycle()
