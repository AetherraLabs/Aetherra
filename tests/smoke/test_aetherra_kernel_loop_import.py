"""
Smoke test for aetherra_kernel_loop.py
"""


def test_import_aetherra_kernel_loop() -> None:
    import aetherra_kernel_loop as _kernel_loop

    # Ensure module is loaded and referenced to avoid unused import diagnostics
    assert _kernel_loop is not None
