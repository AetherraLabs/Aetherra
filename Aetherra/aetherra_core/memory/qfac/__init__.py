"""
QFAC 2.5 — Targeted Upgrades (scaffold)

This package provides a minimal, testable core for the compression-aware
memory subsystem. It avoids heavyweight deps at import time and degrades
gracefully when optional accelerators are missing.

Public API compatibility:
- When called with a MemoryRecord and observer_state, routes to graph-aware API.
- When called with raw content or vectors and top_k, routes to the simple API.
"""

from typing import Dict, Optional, Sequence, cast

from . import api as _graph_api
from . import qfac_api as _simple_api
from .models import Edge, FractalSignature, MemoryRecord, ObserverState


def qfac_store(
    content: MemoryRecord | str,
    *,
    embedding: Optional[Sequence[float]] = None,
    observer_state: Optional[Dict[str, str | int | float]] = None,
):
    """Store content in QFAC.

    - If a MemoryRecord is provided, uses the graph-aware path and returns the record.
    - If raw content is provided, uses the simple path and returns the MemoryRecord.
    """
    if isinstance(content, MemoryRecord):
        _graph_api.qfac_store(content)
        if observer_state:
            content.qfac_meta.setdefault("observer_state", {}).update(observer_state)
        return content
    # string content path (optionally with embedding)
    return _simple_api.qfac_store(content, embedding=embedding, observer_state=observer_state)


def qfac_search(
    query: str | Sequence[float],
    observer_state: Optional[ObserverState] = None,
    *,
    top_k: Optional[int] = None,
    k: Optional[int] = None,
):
    """Search QFAC with dual-mode behavior.

    - If observer_state is provided: routes to graph-aware search and returns List[Dict].
    - Otherwise: routes to simple search and returns List[Tuple[MemoryRecord, float]].
    """
    if observer_state is not None:
        kk = k if k is not None else (top_k if top_k is not None else 20)
        # In graph mode, query must be an embedding vector
        vec = cast(Sequence[float], query)
        return _graph_api.qfac_search(vec, observer_state, k=kk)
    # simple API path
    kk2 = top_k if top_k is not None else (k if k is not None else 5)
    return _simple_api.qfac_search(query, top_k=kk2)


def qfac_rewrite_budgeted(**kwargs):
    """Run a budgeted rewrite pass.

    - graph mode: use budget_ms (returns a dict with stats)
    - simple mode: use budget_tokens (returns an int count)
    """
    if "budget_ms" in kwargs:
        return _graph_api.qfac_rewrite_budgeted(budget_ms=kwargs["budget_ms"])
    return _simple_api.qfac_rewrite_budgeted(budget_tokens=kwargs.get("budget_tokens", 0))


__all__ = [
    "MemoryRecord",
    "Edge",
    "FractalSignature",
    "ObserverState",
    "qfac_store",
    "qfac_search",
    "qfac_rewrite_budgeted",
]
