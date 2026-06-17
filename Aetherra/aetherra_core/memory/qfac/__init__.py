"""
QFAC 2.5 — Targeted Upgrades (scaffold)

This package provides a minimal, testable core for the compression-aware
memory subsystem. It avoids heavyweight deps at import time and degrades
gracefully when optional accelerators are missing.

Public API compatibility:
- When called with a MemoryRecord and observer_state, routes to graph-aware API.
- When called with raw content or vectors and top_k, routes to the simple API.
"""

from __future__ import annotations

import hashlib
import os
from typing import Dict, Optional, Sequence, cast

from . import api as _graph_api
from . import qfac_api as _simple_api
from .models import Edge, FractalSignature, MemoryRecord, ObserverState


def _hash_value(value) -> str | None:
    if value is None:
        return None
    raw = str(value)
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "memory:qfac" and capability == "memory:write":
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _guardian_preflight_qfac_store(
    *,
    content: MemoryRecord | str,
    embedding: Optional[Sequence[float]],
    observer_state: Optional[Dict[str, str | int | float]],
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "memory:qfac"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    is_record = isinstance(content, MemoryRecord)
    content_text = content.content if is_record else str(content)
    record_id = content.id if is_record else None
    record_embedding = content.embedding if is_record else embedding

    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="memory",
            action="memory.qfac_store",
            target="memory:qfac",
            purpose="Persist content in QFAC memory structures",
            capabilities=("memory:write",),
            evidence=("qfac_store_request",),
            reversible=True,
            rollback_plan="remove generated QFAC record or restore memory snapshot",
            metadata={
                "content_kind": "memory_record" if is_record else "raw_content",
                "content_length": len(content_text),
                "record_id_hash": _hash_value(record_id),
                "embedding_dimension": len(record_embedding or []),
                "observer_state_keys": sorted((observer_state or {}).keys()),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def _guardian_preflight_qfac_rewrite(*, kwargs: dict):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "memory:qfac"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    mode = "graph" if "budget_ms" in kwargs else "simple"
    budget = kwargs.get("budget_ms") if mode == "graph" else kwargs.get("budget_tokens", 0)

    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="memory",
            action="memory.qfac_rewrite",
            target="memory:qfac",
            purpose="Run budgeted QFAC memory rewrite pass",
            capabilities=("memory:write",),
            evidence=("qfac_rewrite_request",),
            reversible=True,
            rollback_plan="restore QFAC memory structures from snapshot or backup",
            metadata={
                "mode": mode,
                "budget": int(budget or 0),
                "argument_keys": sorted(kwargs.keys()),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def _ensure_guardian_allowed(decision) -> None:
    if not decision.allowed:
        raise PermissionError(f"QFAC memory mutation blocked by Guardian: {decision.reason}")


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
    _ensure_guardian_allowed(
        _guardian_preflight_qfac_store(
            content=content,
            embedding=embedding,
            observer_state=observer_state,
        )
    )
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
    _ensure_guardian_allowed(_guardian_preflight_qfac_rewrite(kwargs=kwargs))
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
