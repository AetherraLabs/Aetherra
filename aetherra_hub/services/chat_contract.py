"""Shared chat admission and response metadata; never persist rejected prompts."""

from __future__ import annotations

# Standard library imports
import json
import logging
import math
import os
import threading
import time
import uuid
from pathlib import Path

# Third party imports
from flask import g, request
from werkzeug.exceptions import HTTPException

# Local imports
from .security import policy_snapshot

_receipt_lock = threading.Lock()
logger = logging.getLogger(__name__)


def normalize_trace_id(value=None) -> str:
    if isinstance(value, str):
        value = "".join(c for c in value if c.isascii() and c.isprintable())[:64]
        if value:
            return value
    return uuid.uuid4().hex


def request_trace_id() -> str:
    if not hasattr(g, "chat_trace_id"):
        try:
            payload = (
                request.args
                if request.method == "GET"
                else request.get_json(silent=True)
            )
        except HTTPException:
            # Error response decoration must not reread an unreadable/oversized body.
            payload = {}
        payload = payload if hasattr(payload, "get") else {}
        g.chat_trace_id = normalize_trace_id(
            request.headers.get("X-Aetherra-Trace-Id")
            or payload.get("trace_id")
            or request.headers.get("X-Aetherra-Trace")
        )
    return g.chat_trace_id


def standard_headers(trace_id: str, policy=None) -> dict[str, str]:
    return {
        "X-Aetherra-Trace-Id": trace_id,
        "X-Aetherra-Chat-Version": "2",
        "X-Aetherra-Policy": json.dumps(
            policy if policy is not None else policy_snapshot()
        ),
    }


def add_response_headers(response):
    if request.path in {"/api/ai/ask", "/api/ai/stream", "/api/lyrixa/chat"}:
        for name, value in standard_headers(request_trace_id()).items():
            response.headers.setdefault(name, value)
    return response


def request_deadline(payload) -> float | None:
    """Resolve absolute deadlines or relative TTLs; ignore malformed optional values."""
    for key in ("deadline_ts", "ttl_sec"):
        try:
            value = float(payload[key])
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        if math.isfinite(value):
            return value if key == "deadline_ts" else time.time() + value
    return None


def is_expired(deadline: float | None) -> bool:
    return deadline is not None and deadline <= time.time()


def expired_error(endpoint: str, trace_id: str) -> dict:
    # This compatibility DLQ is a rejection receipt, never a replayable chat payload.
    # Client trace IDs can contain private text, so omit those along with prompts.
    receipt = {
        "reason": "expired",
        "type": "chat.request",
        "data": {"endpoint": endpoint},
    }
    try:
        path = (
            Path(os.environ.get("AETHERRA_STATE_DIR") or ".aetherra")
            / "hub_chat_dlq.jsonl"
        )
        with _receipt_lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(receipt) + "\n")
    except OSError:
        logger.warning("Could not record expired chat rejection")
    return {
        "ok": False,
        "error": {"code": "invalid_request", "message": "Request expired"},
        "trace_id": trace_id,
    }
