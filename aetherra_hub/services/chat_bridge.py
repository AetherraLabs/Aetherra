"""Lyrixa chat bridge service: registry lookup + instrumentation hooks.

Provides a framework-agnostic function `handle_chat` used by Flask blueprint.
Captures latency + TTFT (placeholder) observations into metrics_accum.ChatMetrics.
"""

from __future__ import annotations

# Standard library imports
import time
from typing import Any, Dict, Mapping, Tuple

# Local imports
from ..utils.http import run_coro_blocking
from .metrics_accum import chat_metrics
from .security import policy_snapshot, safety_precheck
from .tokenizer import count_tokens

OFFLINE_TEXT = "Lyrixa chat service is not online right now. I can still answer identity and Aetherra questions."  # noqa: E501


def _registry_call(
    message: str,
    allow_edits: bool,
    edit_root,
    trace_id: str,
    prio: str,
    deadline_ts,
    ttl_sec,
):
    try:
        # Aetherra imports
        from aetherra_service_registry import get_service_registry  # type: ignore

        async def _call():
            reg = await get_service_registry()
            svc = reg.get_service("lyrixa_chat")
            if not svc:
                return None
            payload2 = {
                "message": message,
                "allow_edits": allow_edits,
                "edit_root": edit_root,
                "trace_id": trace_id,
                "priority": prio,
                "deadline_ts": deadline_ts,
                "ttl_sec": ttl_sec,
            }
            return await svc.handle_message("lyrixa.chat", payload2)

        return run_coro_blocking(_call())
    except Exception:
        return None


def handle_chat(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
    t0 = time.time()
    message = str(payload.get("message") or payload.get("content") or "")
    allow_edits = bool(payload.get("allow_edits", False))
    edit_root = payload.get("edit_root")
    prio = str(payload.get("priority") or "normal").strip().lower()
    ttl_sec = payload.get("ttl_sec")
    try:
        ttl_sec = int(ttl_sec) if ttl_sec is not None else None
    except Exception:
        ttl_sec = None
    deadline_ts = payload.get("deadline_ts")
    try:
        deadline_ts = float(deadline_ts) if deadline_ts is not None else None
    except Exception:
        deadline_ts = None
    if deadline_ts is None and ttl_sec is not None and ttl_sec > 0:
        deadline_ts = time.time() + float(ttl_sec)

    # Input stats
    chat_metrics.inc_request()
    chat_metrics.add_input_stats(message, count_tokens(message))

    trace_id = payload.get("trace_id") or _gen_trace_id()
    # Sanitize trace_id to prevent header injection
    if trace_id and isinstance(trace_id, str):
        # Remove any characters that could cause header injection
        trace_id = "".join(c for c in trace_id if c.isprintable() and c not in "\r\n\0")
        # Limit length to prevent abuse
        trace_id = trace_id[:64] if trace_id else _gen_trace_id()
    else:
        trace_id = _gen_trace_id()

    # Expiry check
    if deadline_ts and deadline_ts < time.time():
        body = {
            "error": "invalid_request",
            "message": "Request expired",
            "trace_id": trace_id,
        }
        headers = _std_headers(trace_id)
        return body, 409, headers

    # Safety
    sc = safety_precheck(message, trace_id, "/api/lyrixa/chat")
    if not sc.get("allow", True):
        body = {
            "error": "policy_violation",
            "reasons": sc.get("reasons", []),
            "trace_id": trace_id,
        }
        headers = _std_headers(trace_id, policy=sc.get("policy"))
        return body, 403, headers

    # Registry call
    result = _registry_call(
        message, allow_edits, edit_root, trace_id, prio, deadline_ts, ttl_sec
    )

    if not result:
        # Offline fallback instrumentation
        chat_metrics.record_mock_fallback()
        # Output stats minimal (no tokens counted for offline message to keep deterministic?)
        body = {
            "text": OFFLINE_TEXT,
            "suggestions": [],
            "applied_changes": [],
            "persona": {"name": "Lyrixa", "title": "Lyrixa AI Assistant"},
            "awareness": {"note": "service offline; awareness limited"},
            "edit_plan": [],
            "confidence": 0.5,
            "trace_id": trace_id,
        }
        _observe_latency(t0)
        headers = _std_headers(trace_id)
        return body, 200, headers

    # Normalize upstream result structure
    if (
        isinstance(result, dict)
        and "result" in result
        and isinstance(result.get("result"), dict)
    ):
        result = result.get("result")  # unwrap common pattern

    if not isinstance(result, dict):  # ensure dict shape
        result = {"text": str(result)}

    # Normalize identity -> persona
    try:
        if (
            "identity" in result
            and "persona" not in result
            and isinstance(result.get("identity"), Mapping)
        ):
            ident = result.get("identity")  # type: ignore[assignment]
            name = "Lyrixa"
            title = "Lyrixa AI Assistant"
            about = None
            try:
                name = str(
                    getattr(
                        ident,
                        "get",
                        lambda k, d=None: ident[k]
                        if isinstance(ident, dict) and k in ident
                        else d,
                    )("name")
                    or name
                )
            except Exception:
                pass
            try:
                title = str(
                    getattr(
                        ident,
                        "get",
                        lambda k, d=None: ident[k]
                        if isinstance(ident, dict) and k in ident
                        else d,
                    )("title")
                    or title
                )
            except Exception:
                pass
            try:
                about = getattr(
                    ident,
                    "get",
                    lambda k, d=None: ident[k]
                    if isinstance(ident, dict) and k in ident
                    else d,
                )("about")
            except Exception:
                about = None
            persona = {"name": name, "title": title}
            if about:
                persona["about"] = about
            result["persona"] = persona  # type: ignore[index]
    except Exception:
        pass
    if "persona" not in result or not isinstance(result.get("persona"), dict):
        result["persona"] = {"name": "Lyrixa", "title": "Lyrixa AI Assistant"}  # type: ignore[index]

    # Awareness structure
    if not isinstance(result.get("awareness"), dict):
        result["awareness"] = {}  # type: ignore[index]
    # Mirror edit_plan when absent
    if "edit_plan" not in result and isinstance(result.get("suggestions"), list):
        try:
            result["edit_plan"] = list(result.get("suggestions") or [])  # type: ignore[index]
        except Exception:
            result["edit_plan"] = []  # type: ignore[index]
    if "confidence" not in result:
        result["confidence"] = 0.5  # type: ignore[index]
    result["trace_id"] = trace_id  # type: ignore[index]

    # Output stats
    out_text = str(result.get("text") or "")
    chat_metrics.add_output_stats(out_text, count_tokens(out_text))

    _observe_latency(t0)
    headers = _std_headers(trace_id)
    return result, 200, headers


def _observe_latency(t0: float):
    try:
        dt_ms = (time.time() - t0) * 1000.0
        chat_metrics.observe_latency_ms(dt_ms)
    except Exception:
        pass


def _gen_trace_id() -> str:
    # Standard library imports
    import uuid

    return uuid.uuid4().hex


def _std_headers(trace_id: str, policy=None) -> Dict[str, str]:
    # Standard library imports
    import json

    pol = policy or policy_snapshot()
    return {
        "X-Aetherra-Trace-Id": trace_id,
        "X-Aetherra-Chat-Version": "2",
        "X-Aetherra-Policy": json.dumps(pol),
    }
