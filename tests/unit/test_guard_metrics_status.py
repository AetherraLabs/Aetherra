import pytest

from aetherra_self_incorporation import SelfIncorporationService


@pytest.mark.asyncio
async def test_guard_metrics_exposed_and_rejections_count_increment(monkeypatch):
    # Force guard to reject any integration by setting threshold to 0
    monkeypatch.setenv("AETHERRA_GUARD_INTEGRATION_PER_HOUR", "0")
    # Ensure non-strict mode for simpler auth
    monkeypatch.delenv("AETHERRA_PROFILE", raising=False)
    monkeypatch.delenv("AETHERRA_NET_STRICT", raising=False)

    svc = SelfIncorporationService()
    await svc.start()

    # Submit a simple proposal which should be rejected by guard
    res = await svc.handle_improvement_proposal(
        {"type": "scale_up", "params": {"delta": 0.1}, "sender": "tester"}
    )

    assert res.get("status") == "rejected"
    assert str(res.get("reason", "")).startswith("guard_violation:"), res

    # Status should include guard metrics with at least 1 rejection
    st = await svc.get_status()
    guards = st.get("guards", {})
    assert isinstance(guards, dict)
    assert bool(guards), "guards block should be present in status"
    rej = guards.get("rejections", {})
    assert int(rej.get("total", 0)) >= 1
    by_pol = rej.get("by_policy", {})
    assert any(v >= 1 for v in by_pol.values())

    await svc.stop()
