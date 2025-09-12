"""Trace id extraction and propagation helpers."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

__all__ = ["extract_trace_id"]


def extract_trace_id(
    req: Any = None,
    body: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
) -> str:
    try:
        hdr = (getattr(req, "headers", {}) or {}).get("X-Aetherra-Trace-Id")
        if hdr and str(hdr).strip():
            return str(hdr).strip()
    except Exception:
        pass
    try:
        if body and isinstance(body, dict):
            b = body.get("trace_id") or body.get("traceId")
            if b and str(b).strip():
                return str(b).strip()
    except Exception:
        pass
    try:
        if query and isinstance(query, dict):
            q = query.get("trace_id") or query.get("traceId")
            if q and str(q).strip():
                return str(q).strip()
    except Exception:
        pass
    return str(uuid.uuid4())
