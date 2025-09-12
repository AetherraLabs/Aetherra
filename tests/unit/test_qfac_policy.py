import os

from Aetherra.aetherra_core.memory.qfac_policy import QFACPolicy


def _env(**kwargs):
    prev = {}
    for k, v in kwargs.items():
        prev[k] = os.environ.get(k)
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = str(v)
    try:
        yield
    finally:
        for k, v in prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_prod_defaults_downgrade_without_validation(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.delenv("AETHERRA_QFAC_VALIDATED", raising=False)
    monkeypatch.delenv("AETHERRA_QFAC_BACKEND", raising=False)
    # enforce by default
    policy = QFACPolicy()
    d = policy.resolve_mode(
        profile="prod", desired_mode="hybrid", metrics={"ema": 0.95}
    )
    assert d["mode"] == "classical"
    assert d["allowed"] is False
    assert d["reason"] in (
        "no-validated-backend",
        "missing-coherence-ema",
        "ema-below-gate-min",
        "ema-below-hard-min",
        "recent-drift-alert",
    )


def test_test_profile_allows_hybrid_without_validation(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.delenv("AETHERRA_QFAC_VALIDATED", raising=False)
    policy = QFACPolicy()
    d = policy.resolve_mode(profile="test", desired_mode="hybrid", metrics={"ema": 0.9})
    assert d["mode"] == "hybrid"
    assert d["allowed"] is True


def test_hard_min_blocks(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_QFAC_VALIDATED", "1")
    monkeypatch.setenv("AETHERRA_QFAC_HARD_MIN", "0.8")
    policy = QFACPolicy()
    d = policy.resolve_mode(
        profile="prod", desired_mode="hybrid", metrics={"ema": 0.79}
    )
    assert d["mode"] == "classical"
    assert d["reason"] == "ema-below-hard-min"


def test_shadow_mode_reports(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_QFAC_POLICY", "shadow")
    # No validation and missing metrics would deny under enforce
    policy = QFACPolicy()
    d = policy.resolve_mode(profile="prod", desired_mode="quantum", metrics=None)
    assert d["mode"] == "quantum"
    assert d["allowed"] is True
    assert str(d["reason"]).startswith("shadow-would-deny:")
