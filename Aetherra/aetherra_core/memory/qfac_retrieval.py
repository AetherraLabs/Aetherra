#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
QFAC Retrieval Pipeline (Phase 0/1 stub)

Provides a minimal, dependency-light retrieval over QFACMemorySystem nodes.

Contract:
- class QFACRetrievalPipeline
  - search_over_nodes(nodes: dict[str, Any], query: str, top_k: int = 5) -> list[dict]

Scoring: naive term-frequency on serialized content with light ratio/fidelity boost.
This is intentionally simple and will be replaced in later phases.
"""

from __future__ import annotations

# Standard library imports
import json
from typing import Any, Dict, List


class QFACRetrievalPipeline:
    def __init__(self) -> None:
        self.query_count = 0

    def _content_text(self, obj: Any) -> str:
        try:
            return json.dumps(obj, default=str)
        except Exception:
            try:
                return str(obj)
            except Exception:
                return ""

    def _score(self, content: str, query: str, ratio: float, fidelity: str | None) -> float:
        q = (query or "").strip().lower()
        if not q:
            return 0.0
        text = (content or "").lower()
        base = float(text.count(q))
        # Light boosts
        boost = 1.0
        try:
            if ratio and ratio > 1.0:
                boost *= min(2.0, 0.5 + (ratio / 2.0))  # cap boost
        except Exception:
            pass
        try:
            if fidelity and isinstance(fidelity, str):
                f = fidelity.lower()
                if "high" in f:
                    boost *= 1.1
                elif "degraded" in f:
                    boost *= 0.9
        except Exception:
            pass
        # Normalize by length to avoid dominating by huge blobs
        norm = max(50.0, float(len(text)))
        return (base / norm) * boost

    def search_over_nodes(
        self, nodes: Dict[str, Any], query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        scored: List[Dict[str, Any]] = []
        try:
            for nid, node in (nodes or {}).items():
                try:
                    content = self._content_text(getattr(node, "original_data", None))
                    ratio = 1.0
                    fidelity = None
                    if getattr(node, "compression_metadata", None):
                        try:
                            md = node.compression_metadata
                            osz = int(md.get("original_size", 1))
                            csz = int(md.get("compressed_size", 1))
                            ratio = float(osz) / float(max(1, csz))
                        except Exception:
                            ratio = 1.0
                    if getattr(node, "compression_score", None):
                        try:
                            fidelity = node.compression_score.fidelity_level.value
                        except Exception:
                            fidelity = None
                    s = self._score(content, query, ratio, fidelity)
                    scored.append(
                        {
                            "node_id": nid,
                            "score": float(s),
                            "is_compressed": bool(getattr(node, "is_compressed", False)),
                            "fidelity": fidelity,
                            "ratio": float(ratio),
                        }
                    )
                except Exception:
                    continue
        except Exception:
            return []
        scored.sort(key=lambda d: d.get("score", 0.0), reverse=True)
        k = max(1, int(top_k or 5))
        return scored[:k]

    # --- Phase 1 helpers: parity & thresholds ---
    def compute_scores(self, nodes: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Return list of dicts per node with base and boosted scores.

        base_score: score with boosts disabled (ratio=1.0, fidelity=None)
        boosted_score: score with boosts enabled (ratio/fidelity)
        """
        rows: List[Dict[str, Any]] = []
        try:
            for nid, node in (nodes or {}).items():
                try:
                    content = self._content_text(getattr(node, "original_data", None))
                    # boosted inputs
                    ratio = 1.0
                    fidelity = None
                    if getattr(node, "compression_metadata", None):
                        try:
                            md = node.compression_metadata
                            osz = int(md.get("original_size", 1))
                            csz = int(md.get("compressed_size", 1))
                            ratio = float(osz) / float(max(1, csz))
                        except Exception:
                            ratio = 1.0
                    if getattr(node, "compression_score", None):
                        try:
                            fidelity = node.compression_score.fidelity_level.value
                        except Exception:
                            fidelity = None
                    boosted = float(self._score(content, query, ratio, fidelity))
                    base = float(self._score(content, query, 1.0, None))
                    rows.append(
                        {
                            "node_id": nid,
                            "base": base,
                            "boosted": boosted,
                        }
                    )
                except Exception:
                    continue
        except Exception:
            return []
        return rows

    def parity_compare(
        self, nodes: Dict[str, Any], query: str, top_k: int = 5, threshold: float = 0.0
    ) -> Dict[str, Any]:
        """Compute simple parity stats and threshold drops for a query.

        Returns dict with keys: total, top1_match, any_rank_mismatch, threshold_dropped,
        parity_by_k (sub-dict of k -> 0|1 for prefix/top-k match)
        """
        rows = self.compute_scores(nodes, query)
        if not rows:
            return {
                "total": 1,
                "top1_match": 1,
                "any_rank_mismatch": 0,
                "threshold_dropped": 0,
                "parity_by_k": {1: 1, 3: 1, 5: 1, 10: 1},
            }
        # Rankings
        base_sorted = sorted(rows, key=lambda r: r["base"], reverse=True)
        boosted_sorted = sorted(rows, key=lambda r: r["boosted"], reverse=True)
        k = max(1, int(top_k or 5))
        base_top = [r["node_id"] for r in base_sorted[:k]]
        boosted_top = [r["node_id"] for r in boosted_sorted[:k]]
        top1_match = 1 if (base_top and boosted_top and base_top[0] == boosted_top[0]) else 0
        any_rank_mismatch = 1 if base_top != boosted_top else 0
        # Per-k prefix/top-k parity (k in {1,3,5,10})
        ks = (1, 3, 5, 10)
        pbk: dict[int, int] = {}
        for kk in ks:
            # Compare prefixes up to min(kk, available)
            prefix_len = min(kk, len(base_top), len(boosted_top))
            if prefix_len <= 0:
                pbk[kk] = 1  # degenerate case: treat as match
            else:
                pbk[kk] = 1 if base_top[:prefix_len] == boosted_top[:prefix_len] else 0
        # Threshold drops count across all nodes (how many boosted scores fall below threshold)
        threshold_dropped = 0
        if threshold and threshold > 0.0:
            for r in boosted_sorted:
                try:
                    if float(r["boosted"]) < float(threshold):
                        threshold_dropped += 1
                except Exception:
                    continue
        return {
            "total": 1,
            "top1_match": int(top1_match),
            "any_rank_mismatch": int(any_rank_mismatch),
            "threshold_dropped": int(threshold_dropped),
            "parity_by_k": pbk,
        }
