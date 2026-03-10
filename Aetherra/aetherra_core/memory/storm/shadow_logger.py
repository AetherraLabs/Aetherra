# SPDX-License-Identifier: GPL-3.0-or-later
"""Shadow mode logging for STORM Phase 0 validation.

Compares STORM results with baseline without affecting production responses.
"""

from __future__ import annotations

import time
from typing import Any

from ..models import MemoryRecallResult


def compare_results(
    baseline: MemoryRecallResult,
    storm: MemoryRecallResult,
    tolerance: float = 0.1,
) -> dict[str, Any]:
    """Compare baseline and STORM results for divergence analysis.

    Returns a comparison dict with:
    - agreed: bool (True if top results match within tolerance)
    - item_overlap: float (Jaccard similarity of item sets)
    - score_delta: float (mean absolute difference in scores)
    - metadata: dict (additional comparison details)
    """

    # Extract item IDs for comparison (handle both dict and object items)
    def get_item_id(item: Any) -> str:
        if isinstance(item, dict):
            return str(item.get("id") or item.get("content", ""))[:50]
        return str(getattr(item, "id", getattr(item, "content", "")))[:50]

    baseline_ids = {get_item_id(item) for item in baseline.items}
    storm_ids = {get_item_id(item) for item in storm.items}

    # Jaccard similarity
    if baseline_ids or storm_ids:
        intersection = len(baseline_ids & storm_ids)
        union = len(baseline_ids | storm_ids)
        item_overlap = intersection / union if union > 0 else 0.0
    else:
        item_overlap = 1.0  # Both empty = perfect agreement

    # Score delta (for overlapping items)
    score_deltas = []
    baseline_id_scores = {
        get_item_id(baseline.items[i]): baseline.scores[i] if i < len(baseline.scores) else 0.0
        for i in range(len(baseline.items))
    }
    storm_id_scores = {
        get_item_id(storm.items[i]): storm.scores[i] if i < len(storm.scores) else 0.0
        for i in range(len(storm.items))
    }

    for item_id in baseline_ids & storm_ids:
        b_score = baseline_id_scores.get(item_id, 0.0)
        s_score = storm_id_scores.get(item_id, 0.0)
        score_deltas.append(abs(b_score - s_score))

    score_delta = float(sum(score_deltas) / len(score_deltas)) if score_deltas else 0.0

    # Agreement: high overlap and low score delta
    agreed = item_overlap >= (1.0 - tolerance) and score_delta <= tolerance

    return {
        "agreed": agreed,
        "item_overlap": item_overlap,
        "score_delta": score_delta,
        "baseline_count": len(baseline.items),
        "storm_count": len(storm.items),
        "metadata": {
            "baseline_source": baseline.source,
            "storm_source": storm.source,
            "baseline_ids_sample": list(baseline_ids)[:3],
            "storm_ids_sample": list(storm_ids)[:3],
        },
    }


async def shadow_recall(
    storm_engine: Any,
    baseline_result: MemoryRecallResult,
    query: str,
    limit: int,
) -> tuple[MemoryRecallResult, dict[str, Any]]:
    """Execute STORM recall in shadow mode and compare with baseline.

    Returns:
        (baseline_result, comparison_dict)

    The baseline content is always returned to ensure zero production impact,
    but successful STORM evidence metadata is merged into the baseline result so
    shadow-mode observability and acceptance checks still see STORM signals.
    """
    start = time.time()
    comparison = {"agreed": True, "latency_ms": 0.0, "error": None}

    try:
        # Run STORM recall with baseline as fallback
        storm_result = await storm_engine.recall(query, limit=limit, base_fallback=baseline_result)
        latency_ms = (time.time() - start) * 1000.0

        # Compare results
        comparison = compare_results(baseline_result, storm_result)
        comparison["latency_ms"] = latency_ms

        # Preserve baseline items/scores but surface STORM evidence metadata.
        baseline_meta = dict(baseline_result.metadata or {})
        storm_meta = dict((storm_result.metadata or {}).get("storm_meta", {}))
        if storm_meta:
            baseline_meta["storm_meta"] = storm_meta
        evidence_tags = dict((storm_result.metadata or {}).get("evidence_tags", {}))
        if evidence_tags:
            baseline_meta["evidence_tags"] = evidence_tags
        baseline_result.metadata = baseline_meta

    except Exception as e:
        # STORM failed but baseline succeeded - record error
        comparison["error"] = str(e)
        comparison["agreed"] = False
        comparison["latency_ms"] = (time.time() - start) * 1000.0

    # Always return baseline content, optionally enriched with STORM metadata.
    return baseline_result, comparison
