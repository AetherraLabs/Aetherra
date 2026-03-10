# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .models import ContentType, MemoryRecord


def _cosine_sim(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    if len(a) != len(b):
        # dimension mismatch; safest to return 0
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


@dataclass
class _IndexEntry:
    id: str
    embedding: Optional[List[float]]


class QFACStore:
    """Minimal in-memory store and naive search for QFAC 2.5 scaffolding.

    This is intentionally simple to land the package and enable incremental
    improvements (e.g., IVF-PQ indexing, compression tiers, causal checks).
    """

    def __init__(self) -> None:
        self._by_id: Dict[str, MemoryRecord] = {}
        self._index: List[_IndexEntry] = []

    # --- Core API ---
    def store(
        self,
        content: ContentType,
        *,
        embedding: Optional[Sequence[float]] = None,
        observer_state: Optional[Dict[str, str | int | float]] = None,
    ) -> MemoryRecord:
        rec = MemoryRecord.new(content, embedding=embedding)
        if observer_state:
            if rec.observer_state is None:
                rec.observer_state = {}
            rec.observer_state.update(observer_state)
        self._by_id[rec.id] = rec
        self._index.append(
            _IndexEntry(id=rec.id, embedding=(list(embedding) if embedding else None))
        )
        return rec

    def get(self, rec_id: str) -> Optional[MemoryRecord]:
        return self._by_id.get(rec_id)

    def search(
        self, query: str | Sequence[float], *, top_k: int = 5
    ) -> List[Tuple[MemoryRecord, float]]:
        results: List[Tuple[MemoryRecord, float]] = []
        if isinstance(query, str):
            q = query.strip().lower()
            if not q:
                return []
            for rec in self._by_id.values():
                score = 0.0
                if isinstance(rec.content, str):
                    text = rec.content.lower()
                    # simple containment + length-normalized score
                    if q in text:
                        score = min(1.0, len(q) / (len(text) + 1e-9))
                results.append((rec, score))
        else:
            qv = list(query)
            for ent in self._index:
                rec = self._by_id[ent.id]
                score = _cosine_sim(qv, ent.embedding) if ent.embedding else 0.0
                results.append((rec, score))
        # sort by score desc, then timestamp desc to prefer recent ties
        results.sort(key=lambda t: (t[1], t[0].timestamp), reverse=True)
        return results[:top_k]

    def rewrite_budgeted(self, *, budget_tokens: int = 0) -> int:
        # Baseline: no rewrites yet; returns 0 to indicate no-op
        return 0


# Module-level default store for convenience
_store = QFACStore()


def qfac_store(
    content: ContentType,
    *,
    embedding: Optional[Sequence[float]] = None,
    observer_state: Optional[Dict[str, str | int | float]] = None,
) -> MemoryRecord:
    """Store a new content record in the default QFAC store.

    Returns the created MemoryRecord.
    """
    return _store.store(content, embedding=embedding, observer_state=observer_state)


def qfac_search(
    query: str | Sequence[float], *, top_k: int = 5
) -> List[Tuple[MemoryRecord, float]]:
    """Search the default store with a text or vector query.

    Returns a list of (record, score) pairs.
    """
    return _store.search(query, top_k=top_k)


def qfac_rewrite_budgeted(*, budget_tokens: int = 0) -> int:
    """Run a budgeted rewrite pass over the store (stub).

    Returns the number of rewrites performed.
    """
    return _store.rewrite_budgeted(budget_tokens=budget_tokens)
