import pytest

from aetherra_self_incorporation import SelfIncorporationService


@pytest.mark.asyncio
async def test_strict_mode_unknown_sender_rejected(monkeypatch):
    # Enable strict mode (production profile)
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    # Make guard permissive to not interfere with this test
    monkeypatch.setenv("AETHERRA_GUARD_INTEGRATION_PER_HOUR", "1000")

    svc = SelfIncorporationService()
    await svc.start()

    # No sender provided -> should be rejected in strict mode
    res = await svc.handle_improvement_proposal(
        {"type": "scale_up", "params": {"delta": 0.1}}
    )

    assert res.get("status") == "rejected"
    assert res.get("reason") == "unknown_sender_in_strict_mode"

    await svc.stop()


@pytest.mark.asyncio
async def test_proposal_rate_limiting_enforced(monkeypatch):
    # Non-strict mode to avoid capability checks
    monkeypatch.delenv("AETHERRA_PROFILE", raising=False)
    monkeypatch.delenv("AETHERRA_NET_STRICT", raising=False)
    # Make guard permissive to avoid guard rejections in this test
    monkeypatch.setenv("AETHERRA_GUARD_INTEGRATION_PER_HOUR", "1000")

    svc = SelfIncorporationService()
    await svc.start()

    # Send 12 proposals rapidly from same sender -> last 2 should hit rate limit
    results = []
    for _ in range(12):
        res = await svc.handle_improvement_proposal(
            {"type": "scale_up", "params": {"delta": 0.01}, "sender": "loadtester"}
        )
        results.append(res)

    exceeded = sum(1 for r in results if r.get("reason") == "rate_limit_exceeded")
    assert exceeded >= 2, f"expected at least 2 rate-limit rejections, got {exceeded}"

    await svc.stop()
