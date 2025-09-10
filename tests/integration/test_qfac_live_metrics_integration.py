import time

import pytest

from Aetherra.aetherra_core.memory.qfac_integration import QFACMemorySystem


@pytest.mark.asyncio
async def test_qfac_live_metrics_downgrades_in_prod_when_unhealthy(monkeypatch):
    # Simulate prod profile with desired hybrid but poor EMA and recent drift
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_QFAC_MODE", "hybrid")
    # Ensure backend is considered validated to isolate health gating path
    monkeypatch.setenv("AETHERRA_QFAC_VALIDATED", "1")
    # Provide env-fed metrics (live metrics fetch may return None in test)
    monkeypatch.setenv(
        "AETHERRA_QFAC_COHERENCE_EMA", "0.70"
    )  # below hard min default 0.75
    monkeypatch.setenv("AETHERRA_QFAC_LAST_DRIFT_ALERT_EPOCH", str(time.time()))

    # Build system; QFACMemorySystem pulls policy and metrics during __init__
    sys = QFACMemorySystem(data_dir=".test_qfac_sys_live_metrics")

    # Expect enforced downgrade to classical due to health (ema below hard min or recent drift)
    d = sys.qfac_policy_decision
    assert d["mode"] == "classical"
    assert d["allowed"] is False
    assert d["reason"] in ("ema-below-hard-min", "recent-drift-alert")


@pytest.mark.asyncio
async def test_qfac_live_metrics_allows_in_test_profile(monkeypatch):
    # In non-prod with policy default off, desired hybrid should be allowed
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_QFAC_MODE", "hybrid")
    monkeypatch.delenv("AETHERRA_QFAC_VALIDATED", raising=False)
    monkeypatch.setenv(
        "AETHERRA_QFAC_COHERENCE_EMA", "0.60"
    )  # even low should allow in test when policy=off

    sys = QFACMemorySystem(data_dir=".test_qfac_sys_live_metrics2")

    d = sys.qfac_policy_decision
    assert d["mode"] == "hybrid"
    assert d["allowed"] is True
    assert d["policy"] in ("off", "enforce", "shadow")


@pytest.mark.asyncio
async def test_qfac_shadow_mode_reports_but_does_not_downgrade(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_QFAC_POLICY", "shadow")
    monkeypatch.setenv("AETHERRA_QFAC_MODE", "quantum")
    # No validation, no metrics => would deny under enforce
    monkeypatch.delenv("AETHERRA_QFAC_VALIDATED", raising=False)
    monkeypatch.delenv("AETHERRA_QFAC_COHERENCE_EMA", raising=False)
    monkeypatch.delenv("AETHERRA_QFAC_LAST_DRIFT_ALERT_EPOCH", raising=False)

    sys = QFACMemorySystem(data_dir=".test_qfac_sys_live_metrics3")

    d = sys.qfac_policy_decision
    assert d["mode"] == "quantum"
    assert d["allowed"] is True
    assert str(d["reason"]).startswith("shadow-would-deny:")
