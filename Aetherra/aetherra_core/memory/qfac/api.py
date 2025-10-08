# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import time
from typing import Dict, List, Optional, Sequence, Tuple

from .fractal_sig import compute_fractal_signature
from .index_ivf_pq import IVF_PQ_Index
from .materializer import ViewMaterializer
from .models import MemoryRecord, ObserverState, compute_content_hash

# In-memory store (scaffold). Replace with persistent backend later.
_RECORDS: Dict[str, MemoryRecord] = {}
_GRAPH: Dict[str, List[Tuple[str, float, str]]] = {}
_INDEX: Optional[IVF_PQ_Index] = None


def _get_index(dim: int) -> IVF_PQ_Index:
    global _INDEX
    if _INDEX is None:
        _INDEX = IVF_PQ_Index(dim=dim, nlist=64, m=8, nbits=8)
    return _INDEX


def qfac_store(record: MemoryRecord, tier: str = "T0") -> str:
    # Enrich
    record.qfac_meta["tier"] = tier
    record.ensure_ids()
    if record.fractal_sig is None:
        record.fractal_sig = compute_fractal_signature(record)
    if not record.hash:
        record.hash = compute_content_hash(record.content)

    # Index
    if record.embedding is not None:
        idx = _get_index(len(record.embedding))
        idx.add(record.embedding, record.id)

    # Graph
    if record.causal_links:
        _GRAPH[record.id] = [(edge.to, edge.weight, edge.type) for edge in record.causal_links]

    _RECORDS[record.id] = record
    return record.id


def qfac_search(
    query_embedding: Sequence[float],
    observer_state: ObserverState,
    k: int = 20,
) -> List[Dict]:
    if not query_embedding:
        return []
    idx = _get_index(len(query_embedding))
    top = idx.search(query_embedding, k=max(k * 3, 30))
    # Rerank naive by similarity; take top k
    ids = [rid for rid, _ in top[:k]]
    records = [_RECORDS[rid] for rid in ids if rid in _RECORDS]
    vm = ViewMaterializer()
    return vm.materialize_view(records, observer_state)


def qfac_rewrite_budgeted(budget_ms: int = 200) -> Dict[str, int]:
    start = time.time()
    rewrites = 0
    checks = 0
    for rec in list(_RECORDS.values()):
        checks += 1
        # Simple policy: update last_rewrite if older than 1h
        last = float(rec.qfac_meta.get("last_rewrite", 0))
        if time.time() - last > 3600:
            rec.qfac_meta["last_rewrite"] = time.time()
            rewrites += 1
        if (time.time() - start) * 1000.0 >= budget_ms:
            break
    return {"rewrites": rewrites, "checked": checks}


def _reset_qfac_state_for_tests() -> None:  # pragma: no cover
    global _RECORDS, _GRAPH, _INDEX
    _RECORDS = {}
    _GRAPH = {}
    _INDEX = None
