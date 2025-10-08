import asyncio
import os
import re
import types

import pytest

from Aetherra.aetherra_core.memory.qfac_integration import QFACMemorySystem


@pytest.mark.asyncio
async def test_retrieval_threshold_filters_and_parity_counters_increment(monkeypatch):
    # Set a small threshold so only strong matches pass
    monkeypatch.setenv("AETHERRA_QFAC_RETRIEVAL_THRESHOLD", "0.02")

    sys = QFACMemorySystem("_test_qfac_threshold")

    # Store a couple of nodes with distinct content to produce different scores
    await sys.store_memory({"text": "alpha beta gamma"}, node_id="n1")
    await sys.store_memory({"text": "alpha alpha alpha"}, node_id="n2")
    await sys.store_memory({"text": "unrelated content"}, node_id="n3")

    # Allow any background auto-compress tasks to tick (best-effort, non-critical)
    await asyncio.sleep(0.05)

    # Query that should strongly match n2, weakly match others
    results = await sys.search_memory("alpha", top_k=5)

    # All results should be >= threshold
    assert all(
        float(r.get("score", 0.0)) >= float(sys.retrieval_threshold or 0.0)
        for r in results
    )

    # Parity counters should have incremented
    snap = sys.get_retrieval_parity_metrics_snapshot()
    assert snap.get("total", 0) >= 1
    # Either top1 matches or rank mismatch gets counted deterministically
    assert snap.get("top1_match", 0) in (0, 1)
    assert snap.get("any_rank_mismatch", 0) in (0, 1)
    assert snap.get("threshold_dropped", 0) >= 0

    # Sanity: exporter schema still contains parity lines
    from aetherra_hub.services.metrics_accum import build_all_metrics_lines

    text = "\n".join(build_all_metrics_lines())
    for pattern in [
        r"^aetherra_qfac_retrieval_parity_total ",
        r"^aetherra_qfac_retrieval_parity_top1_match_total ",
        r"^aetherra_qfac_retrieval_parity_any_rank_mismatch_total ",
        r"^aetherra_qfac_retrieval_threshold_dropped_results_total ",
    ]:
        assert re.search(pattern, text, flags=re.MULTILINE), (
            f"missing {pattern} in exporter"
        )
