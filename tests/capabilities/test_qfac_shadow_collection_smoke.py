import asyncio

import pytest


@pytest.mark.asyncio
async def test_qfac_shadow_mode_parity_increments_on_search_memory():
    # Import locally to avoid heavy imports at module import time
    from Aetherra.aetherra_core.memory.qfac_integration import QFACMemorySystem

    sys = QFACMemorySystem("_qfac_test_smoke")

    # Store a few nodes with simple patterns
    await sys.store_memory({"text": "alpha beta gamma"}, node_id="n1")
    await sys.store_memory({"text": "beta gamma delta"}, node_id="n2")
    await sys.store_memory({"text": "gamma delta epsilon"}, node_id="n3")

    # Give auto-analyze a brief moment (non-critical)
    await asyncio.sleep(0.05)

    before = dict(sys.get_retrieval_parity_metrics_snapshot())
    await sys.search_memory("gamma", top_k=3)
    after = dict(sys.get_retrieval_parity_metrics_snapshot())

    assert after.get("total", 0) >= before.get("total", 0) + 1, (
        f"Expected parity total to increment by at least 1. Before={before}, After={after}"
    )
