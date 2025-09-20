"""
Smoke test for policy_bootstrap.py
"""


def test_import_policy_bootstrap() -> None:
    import Aetherra.cli.policy_bootstrap as _policy_bootstrap

    # Ensure module is loaded and referenced to avoid unused import diagnostics
    assert _policy_bootstrap is not None
