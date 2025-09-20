"""
Smoke test for run_hub_ai_api.py
"""


def test_import_run_hub_ai_api() -> None:
    import tools.run_hub_ai_api as _run_hub

    # Ensure module is loaded and referenced to avoid unused import diagnostics
    assert _run_hub is not None
