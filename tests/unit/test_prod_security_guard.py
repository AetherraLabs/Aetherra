# Standard library imports
import importlib

# Third party imports
import pytest

# We import via a helper to force module reload with modified env each test


def _attempt_create_app():
    # Aetherra imports
    import aetherra_hub.app as app_mod

    importlib.reload(app_mod)
    return app_mod.create_app()


@pytest.mark.parametrize(
    "missing_vars",
    [
        ["AETHERRA_SCRIPT_VERIFY_STRICT"],
        ["AETHERRA_SIGNING_STRICT"],
        ["AETHERRA_REQUIRE_CAPABILITIES"],
        ["AETHERRA_AI_API_REQUIRE_TOKEN"],  # only relevant if AI API enabled
    ],
)
def test_prod_guard_aborts_on_missing(missing_vars, monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    # Baseline secure posture
    monkeypatch.setenv("AETHERRA_SCRIPT_VERIFY_STRICT", "1")
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("AETHERRA_AI_API_TOKEN", "dummy")
    for mv in missing_vars:
        # remove each set for this parametrization
        for var in missing_vars:
            monkeypatch.delenv(var, raising=False)
        with pytest.raises(RuntimeError):
            _attempt_create_app()
        # restore for next iteration inside param group
        for var in missing_vars:
            # re-add secure baseline except ones not under test
            if var == "AETHERRA_AI_API_REQUIRE_TOKEN":
                monkeypatch.setenv(var, "1")
            elif var == "AETHERRA_AI_API_ENABLED":
                monkeypatch.setenv(var, "1")
            else:
                monkeypatch.setenv(var, "1")


def test_prod_guard_override(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_PROD_UNSAFE_ALLOW", "1")
    # Intentionally insecure
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    # Should not raise due to override
    _attempt_create_app()


def test_prod_guard_secure_pass(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_SCRIPT_VERIFY_STRICT", "1")
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("AETHERRA_AI_API_TOKEN", "token123")
    _attempt_create_app()
