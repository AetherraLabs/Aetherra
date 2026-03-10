# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Dict, List

from .models import MemoryRecord, ObserverState


class ViewMaterializer:
    """Observer-dependent view materializer.

    Simple first cut:
    - Hash priors to set priors_hash
    - Weight records by edge types according to observer priors
    - Return a list of dicts with view_score and record payload
    """

    def __init__(self) -> None:
        # default weights per edge type
        self.default_edge_weights: Dict[str, float] = {
            "supports": 1.0,
            "causes": 0.9,
            "temporal_next": 0.7,
            "related": 0.5,
            "refutes": -0.6,
        }

    def materialize_view(
        self, records: List[MemoryRecord], observer_state: ObserverState
    ) -> List[Dict]:
        os_ = observer_state.materialize()
        priors = os_.priors or {}

        out: List[Dict] = []
        for rec in records:
            # edge salience score
            score = 0.0
            for e in rec.causal_links or []:
                base = self.default_edge_weights.get(e.type, 0.0)
                # observer prior can bias types
                bias = float(priors.get(e.type, 0.0))
                score += (base + bias) * e.weight * e.confidence
            # motifs mild boost if any overlap (baseline heuristic)
            if rec.fractal_sig and rec.fractal_sig.motifs:
                score += 0.05 * len(rec.fractal_sig.motifs)
            out.append(
                {
                    "id": rec.id,
                    "timestamp": rec.timestamp,
                    "view_score": score,
                    "observer": {
                        "agent_id": os_.agent_id,
                        "perspective": os_.perspective,
                        "priors_hash": os_.priors_hash,
                    },
                    "content": rec.content if isinstance(rec.content, str) else str(rec.content),
                }
            )

        out.sort(key=lambda d: d.get("view_score", 0.0), reverse=True)
        return out
