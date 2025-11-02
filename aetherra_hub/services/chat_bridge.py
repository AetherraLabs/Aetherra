"""Lyrixa chat bridge service: registry lookup + instrumentation hooks.

Provides a framework-agnostic function `handle_chat` used by Flask blueprint.
Captures latency + TTFT (placeholder) observations into metrics_accum.ChatMetrics.
"""

from __future__ import annotations

# Standard library imports
import time
from collections.abc import Mapping
from typing import Any

# Local imports
from ..utils.http import run_coro_blocking

# Aetherra imports
try:  # Centralized disclosure policy (optional at import time)
    from Aetherra.core import disclosure_policy as dp  # type: ignore
except Exception:  # pragma: no cover - defensive import fallback
    dp = None  # type: ignore
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


def handle_chat(payload: dict[str, Any]) -> tuple[dict[str, Any], int, dict[str, str]]:
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
            "identity": {"name": "Lyrixa", "title": "Lyrixa AI Assistant"},
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

            # Safely extract name, title, about from identity dict-like object
            try:
                if isinstance(ident, dict):
                    name = str(ident.get("name") or name)
                elif hasattr(ident, "get"):
                    val = ident.get("name")
                    if val:
                        name = str(val)
            except Exception:
                pass

            try:
                if isinstance(ident, dict):
                    title = str(ident.get("title") or title)
                elif hasattr(ident, "get"):
                    val = ident.get("title")
                    if val:
                        title = str(val)
            except Exception:
                pass

            try:
                if isinstance(ident, dict) or hasattr(ident, "get"):
                    about = ident.get("about")
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

    # Apply disclosure controls for Free tier without breaking schema
    # Never fail response due to redaction errors
    from contextlib import suppress

    with suppress(Exception):
        if dp and getattr(dp, "is_free", None) and dp.is_free():
            _apply_free_tier_redaction_inplace(result)

    # Output stats (after potential redaction)
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


def _std_headers(trace_id: str, policy=None) -> dict[str, str]:
    # Standard library imports
    import json

    pol = policy or policy_snapshot()
    return {
        "X-Aetherra-Trace-Id": trace_id,
        "X-Aetherra-Chat-Version": "2",
        "X-Aetherra-Policy": json.dumps(pol),
    }


def _apply_free_tier_redaction_inplace(result: dict[str, Any]) -> None:
    """Redact potentially sensitive content while preserving the expected schema.

    Rules:
    - Keep `text` as a string; strip/replace code fences and diff-like blocks.
    - Truncate excessively long text with a notice.
    - Summarize lists (suggestions, edit_plan, applied_changes) to metadata-safe items,
      preserving counts and basic titles/actions if present.
    - Add disclosure markers.
    """
    # Standard library imports
    import re

    # Redact code/diff blocks in text while keeping a human-readable message
    text = str(result.get("text") or "")
    if text:
        redactions = 0

        # Remove fenced code blocks ```...```
        def _strip_code(m):
            nonlocal redactions
            redactions += 1
            lang = (m.group(1) or "").strip()
            return f"[code block redacted{f' ({lang})' if lang else ''}]"

        text = re.sub(r"```([a-zA-Z0-9_+-]*)\n[\s\S]*?```", _strip_code, text)
        # Remove diff-like hunks
        if re.search(r"^@@ .* @@|^\+\+\+ |^--- ", text, re.M):
            redactions += 1
            text = re.sub(r"^@@ .* @@.*$", "[diff hunk redacted]", text, flags=re.M)
            text = re.sub(
                r"^(\+\+\+|---) .*$", "[diff header redacted]", text, flags=re.M
            )
            text = re.sub(r"^[+-].*$", "[diff line redacted]", text, flags=re.M)
        # Truncate very long text
        max_len = 1200
        if len(text) > max_len:
            text = text[:max_len] + " … [truncated for free tier]"
        if redactions > 0:
            note = "\n[Free tier: some content redacted]"
            if not text.endswith(note):
                text = text + note
        result["text"] = text

    # Summarize list fields
    def _summarize_items(items):
        safe = []
        for it in items[:10]:  # cap length for safety
            if isinstance(it, dict):
                entry = {}
                # Preserve high-level hints if present; drop code/diff details
                for k in ("title", "action", "file", "path"):
                    if k in it:
                        try:
                            entry[k] = str(it[k])
                        except Exception:
                            pass
                entry.setdefault("summary", "details available in higher tiers")
                safe.append(entry)
            else:
                safe.append({"summary": "details available in higher tiers"})
        return safe

    for key in ("suggestions", "edit_plan", "applied_changes"):
        if isinstance(result.get(key), list):
            orig = result.get(key) or []
            result[key] = _summarize_items(orig)

    # Ensure edit_plan mirrors suggestions length-wise for schema expectations
    if isinstance(result.get("suggestions"), list):
        if not isinstance(result.get("edit_plan"), list) or (
            len(result.get("edit_plan") or []) != len(result.get("suggestions") or [])
        ):
            result["edit_plan"] = list(result.get("suggestions") or [])

    # Add disclosure marker
    result.setdefault("disclosure_tier", "free")
    result.setdefault(
        "awareness",
        {"note": "Observation Layer active: code and patches redacted"},
    )
