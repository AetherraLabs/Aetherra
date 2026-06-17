# Standard library imports
import asyncio

# Aetherra imports
from aetherra_self_incorporation import (
    SelfIncorporationConfig,
    SelfIncorporationService,
)


async def _start_selfinc():
    cfg = SelfIncorporationConfig()
    svc = SelfIncorporationService(cfg)
    await svc.start()
    return svc


async def _exercise_optimize_proposal():
    svc = await _start_selfinc()

    # Baseline counters
    base_exec = int(svc.metrics.get("proposals_executed", 0))
    base_acc = int(svc.metrics.get("proposals_accepted", 0))

    # Send an "optimize" proposal via message handler (public contract)
    proposal = {
        "proposal_id": "p-123",
        "type": "optimize",
        "params": {"hint": "indexing", "value": True},
    }
    res = await svc.handle_message("selfimprovement.proposal", proposal)

    return svc, res, base_exec, base_acc


def test_proposal_consumer_optimize_adjusts_knobs_and_metrics(monkeypatch):
    # Ensure test profile for permissive behavior
    monkeypatch.delenv("AETHERRA_PROFILE", raising=False)
    monkeypatch.delenv("AETHERRA_NET_STRICT", raising=False)
    monkeypatch.delenv("AETHERRA_SELFINC_STRICT", raising=False)
    monkeypatch.setenv("AETHERRA_SELFINC_TRUST_MODE", "standard")

    svc, res, base_exec, base_acc = asyncio.run(_exercise_optimize_proposal())

    assert isinstance(res, dict)
    assert res.get("status") in ("accepted", "rejected")
    # For optimize knob change, we expect acceptance in default config
    assert res.get("status") == "accepted"

    # Metrics should have incremented
    assert int(svc.metrics.get("proposals_executed", 0)) == base_exec + 1
    assert int(svc.metrics.get("proposals_accepted", 0)) == base_acc + 1

    # Optimization hint should be recorded
    assert svc._optimization_hints.get("indexing") is True
