import asyncio
import os

import pytest

from Aetherra.aetherra_core.memory.qfac_integration import QFACMemorySystem


@pytest.mark.asyncio
async def test_parity_toggle_disables_counter_increment(monkeypatch):
    # Disable parity
    monkeypatch.setenv("AETHERRA_QFAC_RETRIEVAL_PARITY", "0")

    sys = QFACMemorySystem("_test_qfac_parity_toggle")

    # Seed content
    await sys.store_memory({"text": "alpha"}, node_id="n1")
    await sys.store_memory({"text": "alpha alpha"}, node_id="n2")

    await asyncio.sleep(0.01)

    before = dict(sys.get_retrieval_parity_metrics_snapshot())
    await sys.search_memory("alpha", top_k=3)
    after = dict(sys.get_retrieval_parity_metrics_snapshot())

    # No counter should increase when disabled
    for key in ("total", "top1_match", "any_rank_mismatch", "threshold_dropped"):
        assert after.get(key, -1) == before.get(key, -1), (
            f"counter {key} changed despite parity disabled"
        )
