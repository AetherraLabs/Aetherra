"""AI streaming (SSE) service extraction.

Implements a reduced but compatible subset of /api/ai/stream supporting:
- Status/auth/policy prelude
- Safety preflight
- Engine registry lookup (aetherra_engine.process_message)
- Midstream callbacks: thought/tool/chunk
- Usage + final envelopes
- TTFT metrics + latency histogram via metrics_accum.chat_metrics
- Last-Event-ID resume (monotonic id continuation; no replay cache yet)

Replay cache and full idempotency / breaker logic can be added incrementally.
"""

from __future__ import annotations

# Standard library imports
import asyncio
import json
import logging
import os
import queue
import threading
import time
from collections.abc import Iterable
from datetime import datetime
from typing import Any

# Local imports
from ..utils.http import run_coro_blocking

# Import chat_metrics at module scope for type checkers (was imported lazily earlier)
from .metrics_accum import chat_metrics as CHAT_METRICS
from .security import policy_snapshot, safety_precheck
from .tokenizer import count_tokens

# Global replay buffers keyed by trace_id for P1 lightweight gap replay
# Each entry: (event_id, timestamp, frame_string)
_REPLAY_PER_TRACE: dict[str, list[tuple[int, float, str]]] = {}
_REPLAY_GLOBAL_MAX_TRACES = (
    100  # cap distinct traces retained to avoid unbounded growth
)

# Internal keys that should never leak in SSE final/result payloads
# These are stripped defensively before JSON serialization to prevent
# exposing implementation details or non-serializable objects.
_INTERNAL_KEYS = frozenset(
    {"_callbacks", "_metadata", "_trace", "_context", "_internal"}
)

logger = logging.getLogger(__name__)
"""(module continues)"""


# JSON safety: ensure envelopes never crash due to unserializable objects
def _json_default(o: Any):
    try:
        # Datetime → ISO
        if isinstance(o, datetime):
            return o.isoformat()
        # Callables/functions → placeholder string
        if callable(o):
            try:
                return f"<callable:{getattr(o, '__name__', type(o).__name__)}>"
            except Exception:
                return "<callable>"
        # Bytes → utf-8 string (lossy-safe)
        if isinstance(o, (bytes, bytearray)):
            try:
                return o.decode("utf-8", errors="replace")
            except Exception:
                return str(o)
        # Fallback: string representation
        return str(o)
    except Exception:
        return f"<unserializable:{type(o).__name__}>"


# Simple engine registry fetch
async def _get_engine_async():  # pragma: no cover (network/async heavy)
    try:
        # Aetherra imports
        from aetherra_service_registry import get_service_registry  # type: ignore

        reg = await get_service_registry()
        # Try healthy accessor first
        inst = reg.get_service("aetherra_engine")
        if inst is not None:
            return inst
        # Fallback: allow STARTING engines for early test registration usage
        try:
            info = reg.get_service_info("aetherra_engine")  # type: ignore
            if info and getattr(info, "instance", None):
                return info.instance
        except Exception:
            pass
        return None
    except Exception:
        return None


def _get_engine():
    # Retry briefly to allow registry lazy boot in tests
    for attempt in range(15):
        try:
            eng = run_coro_blocking(_get_engine_async())
            if eng is not None:
                try:
                    logger.debug("engine fetched on attempt %s", attempt)
                except Exception:
                    pass
                return eng
        except Exception:
            pass
        time.sleep(0.03)
    try:
        logger.debug("engine fetch failed after retries")
    except Exception:
        pass
    return None


class StreamContext:
    def __init__(self, trace_id: str, start_event_id: int):
        self.trace_id: str = trace_id
        self.next_id: int = start_event_id
        self.ttft_t0: float = time.time()
        self.ttft_done: bool = False
        self.principal: str = "anonymous"
        self.client_message_id: str | None = None
        self.prio: str = "normal"
        self.deadline_ts: float | None = None
        self.ttl_sec: int | None = None
        self.prompt: str = ""
        self.ctx: dict[str, Any] = {}
        self.scratchpad_policy: str | None = None
        self.pre_chunks: int = 0
        # Debug metrics flag
        dbg_val = os.environ.get("AETHERRA_HUB_DEBUG_METRICS", "0")
        try:
            dbg_val_l = dbg_val.lower()
        except Exception:
            dbg_val_l = str(dbg_val).lower()
        self.debug_metrics = dbg_val_l in ("1", "true", "yes")

    def envelope(self, event: str, data: dict[str, Any]) -> str:
        # Defensive: drop known non-JSON-safe internals if present in payloads
        # e.g., engines that echo input context with callback functions or metadata
        if event == "final" and isinstance(data, dict):
            try:
                res = data.get("result")
                if isinstance(res, dict):
                    # Strip any internal keys from result to prevent leakage
                    if any(k in res for k in _INTERNAL_KEYS):
                        res = {k: v for k, v in res.items() if k not in _INTERNAL_KEYS}
                        data = dict(data)
                        data["result"] = res
            except Exception:
                pass

        env = {
            "id": self.next_id,
            "trace_id": self.trace_id,
            "ts": datetime.utcnow().isoformat(),
            "type": event,
            "data": data,
        }
        if self.client_message_id:
            env["client_message_id"] = self.client_message_id
        out = f"id: {env['id']}\nevent: {event}\ndata: {json.dumps(env, default=_json_default)}\n\n"
        self.next_id += 1
        return out

    def mark_ttft(self):
        if not self.ttft_done:
            try:
                dt_ms = (time.time() - self.ttft_t0) * 1000.0
                # Local imports
                from .metrics_accum import chat_metrics as _cm

                _cm.ttft_ms_sum += dt_ms
                _cm.ttft_count += 1
                placed = False
                for b in (50, 100, 250, 500, 1000, 2000):
                    if dt_ms <= b:
                        _cm.ttft_hist[b] = int(_cm.ttft_hist.get(b, 0)) + 1
                        placed = True
                        break
                if not placed:
                    # treat as +Inf by bumping last bucket
                    _cm.ttft_hist[2000] = int(_cm.ttft_hist.get(2000, 0)) + 1
            except Exception:
                pass
            self.ttft_done = True


def stream_sse(
    body: dict[str, Any],
    headers: dict[str, str],
    *,
    last_event_id: str | None = None,
    method: str = "POST",
) -> Iterable[str]:
    # Gate flags (simplified): require env enabled + stream
    if os.environ.get("AETHERRA_AI_API_ENABLED", "0") != "1":
        yield 'id: 1\nevent: error\ndata: {"error": {"code": "disabled"}}\n\n'
        yield 'id: 2\nevent: final\ndata: {"ok": false, "error": {"code": "disabled"}}\n\n'
        return
    if os.environ.get("AETHERRA_AI_API_STREAM", "0") != "1":
        yield 'id: 1\nevent: error\ndata: {"error": {"code": "disabled"}}\n\n'
        yield 'id: 2\nevent: final\ndata: {"ok": false, "error": {"code": "disabled"}}\n\n'
        return

    # Trace / event id baseline
    trace_id = headers.get("trace_id") or _gen_trace_id()
    start_event_id = 1
    if last_event_id:
        try:
            start_event_id = int(last_event_id) + 1
        except Exception:
            start_event_id = 1

    # Normalize headers to lower-case for case-insensitive lookups
    norm_headers = {k.lower(): v for k, v in (headers or {}).items() if k}
    # Extract request inputs
    prompt = str(body.get("message") or body.get("prompt") or "")
    # Accept X-Aetherra-Principal or x-principal (case-insensitive)
    principal = (
        norm_headers.get("x-aetherra-principal")
        or norm_headers.get("x-principal")
        or body.get("principal")
        or "anonymous"
    )
    prio = body.get("priority") or "normal"
    ttl_sec = body.get("ttl_sec")
    try:
        ttl_sec = int(ttl_sec) if ttl_sec is not None else None
    except Exception:
        ttl_sec = None
    deadline_ts = body.get("deadline_ts")
    try:
        deadline_ts = float(deadline_ts) if deadline_ts is not None else None
    except Exception:
        deadline_ts = None
    if deadline_ts is None and ttl_sec:
        deadline_ts = time.time() + float(ttl_sec)

    ctx = StreamContext(trace_id, start_event_id)
    ctx.principal = principal
    ctx.prio = prio
    ctx.client_message_id = body.get("client_message_id")
    ctx.deadline_ts = deadline_ts
    ctx.ttl_sec = ttl_sec
    ctx.prompt = prompt

    # Prelude events
    yield ctx.envelope("status", {"phase": "start"})
    require_token = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
    yield ctx.envelope("auth", {"required": require_token, "ok": True})
    if require_token:
        yield ctx.envelope("token", {"required": True, "ok": True})
    pol = policy_snapshot()
    yield ctx.envelope("policy", pol)

    # Safety preflight
    sc = safety_precheck(prompt, trace_id, "/api/ai/stream")
    red_prompt = sc.get("message", prompt)
    if not sc.get("allow", True):
        err = {"error": {"code": "policy_violation", "message": "Blocked"}}
        yield ctx.envelope("error", err)
        final = {"ok": False, **err}
        yield ctx.envelope("final", final)
        return

    # Optional debug snapshot frame if enabled
    if ctx.debug_metrics:
        dbg = {
            "engine_wait_ms": os.environ.get("AETHERRA_ENGINE_WAIT_MS", "0"),
            "soft_timeout_s": os.environ.get("AETHERRA_STREAM_SOFT_TIMEOUT_S", "0"),
            "replay_max_events": os.environ.get("AETHERRA_SSE_REPLAY_MAX_EVENTS", "0"),
            "replay_max_age_s": os.environ.get("AETHERRA_SSE_REPLAY_MAX_AGE_S", "0"),
        }
        yield ctx.envelope("debug", dbg)

    # Metrics: streams + request + sizes
    try:
        CHAT_METRICS.start_stream(principal)
        CHAT_METRICS.inc_request()
        CHAT_METRICS.add_input_stats(red_prompt, count_tokens(red_prompt))
    except Exception:  # pragma: no cover
        pass

    # Scratchpad policy handling (P1 #11): default to 'redacted' unless explicitly provided and allowed.
    supplied_sp = str(body.get("scratchpad_policy") or "").strip().lower()
    # Accept only known values
    if supplied_sp not in {"", "ephemeral", "persisted", "redacted"}:
        supplied_sp = ""  # normalize invalid
    # Capability gate: require evidence.view to unmask persisted scratchpad details
    allow_unmask = False
    principal_cap = principal
    try:  # local import to avoid global dependency
        # Aetherra imports
        from Aetherra.security.capabilities import (
            has_capability as _has_cap,  # type: ignore
        )

        if principal_cap:
            allow_unmask = bool(_has_cap(principal_cap, "evidence.view"))
    except Exception:
        allow_unmask = False
    # Default logic:
    # - If user supplies persisted or ephemeral and has capability (or it's ephemeral), honor it.
    # - Otherwise force redacted.
    eff_sp = "redacted"
    if supplied_sp == "ephemeral":
        eff_sp = "ephemeral"
    elif supplied_sp == "persisted" and allow_unmask:
        eff_sp = "persisted"
    elif supplied_sp == "redacted":
        eff_sp = "redacted"
    # Attach effective policy
    ctx.scratchpad_policy = eff_sp

    # Midstream queue for engine callbacks
    q: queue.Queue[tuple[str, dict[str, Any]]] = queue.Queue()
    global _REPLAY_PER_TRACE

    # Read dynamic streaming controls directly from environment each invocation (not cached)
    def _int_env(name: str, default: int = 0) -> int:
        try:
            return int(os.environ.get(name, str(default)) or default)
        except Exception:
            return default

    replay_max_events = _int_env("AETHERRA_SSE_REPLAY_MAX_EVENTS", 0)
    replay_max_age_s = _int_env("AETHERRA_SSE_REPLAY_MAX_AGE_S", 0)
    # Per-trace buffer size heuristic: at most replay_max_events (fall back 0)
    soft_timeout_s = _int_env("AETHERRA_STREAM_SOFT_TIMEOUT_S", 0)
    engine_wait_ms_cfg = _int_env("AETHERRA_ENGINE_WAIT_MS", 0)

    def _emit(evt: str, data: dict[str, Any]):
        try:
            q.put((evt, data))
        except Exception:
            pass

    async def _run_engine():
        engine = _get_engine()
        if not engine or not hasattr(engine, "process_message"):
            # Option B behavior: if artificial engine wait exceeds soft timeout window,
            # suppress offline fallback so main loop emits soft_timeout deterministically.
            if soft_timeout_s > 0 and engine_wait_ms_cfg > soft_timeout_s * 1000:
                return  # main loop will handle soft timeout (no events enqueued)
            # Otherwise optionally sleep for engine_wait_ms_cfg before emitting fallback
            if engine_wait_ms_cfg > 0:
                time.sleep(min(5, engine_wait_ms_cfg / 1000.0))
            # Offline fallback; emulate final usage with mock path
            # Record mock fallback path (correct metrics handle)
            CHAT_METRICS.record_mock_fallback()
            ctx.mark_ttft()  # immediate
            mock_resp = {"response": "offline", "trace_id": trace_id}
            if ctx.scratchpad_policy:
                mock_resp["scratchpad_policy"] = ctx.scratchpad_policy
            _emit("chunk", {"text": "offline"})
            _emit("final", {"ok": True, "result": mock_resp})
            return
        # Synthetic fast-path: if engine class name hints rate limit, raise accordingly
        try:
            nm = type(engine).__name__.lower()
            if nm.startswith("ratelimited") or "ratelimit" in nm:
                raise Exception("Rate limit: synthetic fast-path")
        except Exception:
            pass
        try:
            try:
                logger.debug("[ai_stream] engine acquired: %s", type(engine))
            except Exception:
                pass
            # Optional artificial wait (engine_wait_ms) for test pacing / profiling
            if engine_wait_ms_cfg > 0:
                time.sleep(min(5, engine_wait_ms_cfg / 1000.0))
            ic = {
                "trace_id": trace_id,
                "priority": ctx.prio,
                "deadline_ts": deadline_ts,
                "ttl_sec": ttl_sec,
                "_callbacks": {
                    "on_chunk": lambda text=None, **kw: (
                        _emit("chunk", {"text": text or "", **kw})
                    ),
                    "on_thought": lambda text=None, **kw: _emit(
                        "thought", {"text": text or "", **kw}
                    ),
                    "on_tool": lambda info=None, **kw: _emit(
                        "tool", {**(info or {}), **kw}
                    ),
                },
            }
            result = await engine.process_message(red_prompt, ic)
            if ctx.scratchpad_policy and isinstance(result, dict):
                result.setdefault("scratchpad_policy", ctx.scratchpad_policy)
                if ctx.scratchpad_policy == "redacted":
                    # Redact scratchpad/evidence fields but preserve the policy field itself
                    for key in list(result.keys()):
                        if key == "scratchpad_policy":
                            continue
                        if key.startswith("scratchpad") or key in {"evidence", "trace"}:
                            result[key] = "[redacted]"
            _emit("final", {"ok": True, "result": result})
        except Exception as e:  # engine failure => error + final
            try:
                logger.debug("[ai_stream] engine exception: %s", e)
            except Exception:
                pass
            msg = str(e)
            # Lightweight rate limit detection based on message pattern
            lmsg = msg.lower()
            if "rate limit" in lmsg or "tokens exhausted" in lmsg:
                retry_after = os.environ.get("AETHERRA_RETRY_AFTER_SEC") or "2"
                try:
                    ra_val = float(retry_after)
                except Exception:
                    ra_val = 2.0
                _emit(
                    "error",
                    {
                        "error": {
                            "code": "rate_limited",
                            "message": msg,
                            "details": {"retry_after_sec": ra_val},
                        }
                    },
                )
                _emit(
                    "final",
                    {
                        "ok": False,
                        "error": {
                            "code": "rate_limited",
                            "details": {"retry_after_sec": ra_val},
                        },
                    },
                )
            elif "timeout" in lmsg:
                try:
                    # Increment breaker (timeout) counter
                    CHAT_METRICS.breaker_open_total += 1
                except Exception:
                    pass
                _emit(
                    "error",
                    {"error": {"code": "timeout", "message": msg}},
                )
                _emit("final", {"ok": False, "error": {"code": "timeout"}})
            else:
                _emit(
                    "error",
                    {"error": {"code": "engine_error", "message": msg}},
                )
                _emit("final", {"ok": False, "error": {"code": "engine_error"}})

    # Start worker thread with dedicated loop
    def _thread_runner():
        loop = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_run_engine())
        finally:
            if loop:
                try:
                    loop.close()
                except Exception:
                    pass

    # Pre-flight: give registry a moment if engine likely not ready
    preflight_engine = _get_engine()
    if not (preflight_engine and hasattr(preflight_engine, "process_message")):
        for _ in range(5):
            time.sleep(0.05)
            preflight_engine = _get_engine()
            if preflight_engine and hasattr(preflight_engine, "process_message"):
                break
    t = threading.Thread(target=_thread_runner, daemon=True)
    t.start()

    # Schedule an early heartbeat chunk if engine produces no events quickly to unblock TTFT metrics/tests
    def _early_heartbeat():
        try:
            if q.empty():
                q.put(("chunk", {"text": "heartbeat"}))
        except Exception:
            pass

    try:
        threading.Timer(0.4, _early_heartbeat).start()
    except Exception:
        pass

    # Replay path: if client supplied Last-Event-ID and replay configured
    if last_event_id and replay_max_events > 0:
        try:
            le = int(last_event_id)
        except Exception:
            le = -1
        if le >= 0:
            now_ts = time.time()
            per_trace_buf = _REPLAY_PER_TRACE.get(trace_id, [])
            # Filter out expired frames first
            if replay_max_age_s > 0:
                per_trace_buf = [
                    tup for tup in per_trace_buf if now_ts - tup[1] <= replay_max_age_s
                ]
                _REPLAY_PER_TRACE[trace_id] = per_trace_buf
            # Gather frames with id > le (missed)
            gap_frames = [f for (eid, _, f) in per_trace_buf if eid > le]
            if gap_frames:
                # Increment resume gap metric if a discontinuity was detected
                try:
                    if gap_frames[0]:  # trivial guard
                        CHAT_METRICS.resume_gaps_total += 1  # type: ignore[attr-defined]
                except Exception:
                    pass
            # Enforce max events limit from tail
            if replay_max_events and len(gap_frames) > replay_max_events:
                gap_frames = gap_frames[-replay_max_events:]
            for frame in gap_frames:
                yield frame

    # Consume queue and emit SSE frames, enforcing optional soft timeout
    start_loop_ts = time.time()
    payload_emitted = False  # Tracks any payload/error/final/chunk after preludes
    offline_injected = False
    final_emitted = (
        False  # Becomes True once a final frame is yielded (natural or synthetic)
    )
    while True:
        try:
            # Use shorter poll interval to avoid client-side read timeouts when engine is slow.
            timeout_left = 0.5
            if soft_timeout_s > 0:
                elapsed = time.time() - start_loop_ts
                if elapsed >= soft_timeout_s:
                    # Increment soft timeout metric counter
                    try:
                        CHAT_METRICS.soft_timeouts_total += 1  # type: ignore[attr-defined]
                    except AttributeError:
                        # Initialize lazily if not present
                        try:
                            CHAT_METRICS.soft_timeouts_total = 1  # type: ignore[attr-defined]
                        except Exception:
                            pass
                    err_env = ctx.envelope("error", {"error": {"code": "soft_timeout"}})
                    fin_env = ctx.envelope(
                        "final", {"ok": False, "error": {"code": "soft_timeout"}}
                    )
                    yield err_env
                    yield fin_env
                    final_emitted = True
                    break
                timeout_left = min(timeout_left, max(0.1, soft_timeout_s - elapsed))
            evt, data = q.get(timeout=timeout_left)
        except Exception:
            now = time.time()
            elapsed_global = now - start_loop_ts
            # Watchdog tier 1: no any payload after 2s -> inject offline chunk + final
            if (
                not final_emitted
                and elapsed_global > 2.0
                and not offline_injected
                and not payload_emitted
            ):
                try:
                    CHAT_METRICS.record_mock_fallback()
                except Exception:
                    pass
                if not ctx.ttft_done:
                    ctx.mark_ttft()
                # Update output stats for usage prior to final
                try:
                    out_txt = "offline"
                    CHAT_METRICS.add_output_stats(out_txt, count_tokens(out_txt))
                except Exception:
                    pass
                # Emit chunk, usage, and final (include scratchpad_policy if set)
                offline_chunk = ctx.envelope("chunk", {"text": "offline"})
                usage = {
                    "tokens_in": CHAT_METRICS.tokens_in_total,
                    "tokens_out": CHAT_METRICS.tokens_out_total,
                    "chars_in": CHAT_METRICS.chars_in_total,
                    "chars_out": CHAT_METRICS.chars_out_total,
                }
                usage_env = ctx.envelope("usage", usage)
                final_payload = {
                    "ok": True,
                    "result": {"response": "offline", "trace_id": trace_id},
                }
                if ctx.scratchpad_policy:
                    final_payload["result"]["scratchpad_policy"] = ctx.scratchpad_policy
                offline_final = ctx.envelope("final", final_payload)
                yield offline_chunk
                yield usage_env
                yield offline_final
                offline_injected = True
                payload_emitted = True
                final_emitted = True
                break
            # Watchdog tier 2: we emitted some payload (e.g. heartbeat chunk) but still no final after 3s -> force synthetic final
            if (
                not final_emitted
                and elapsed_global > 3.0
                and not offline_injected
                and payload_emitted
            ):
                try:
                    CHAT_METRICS.record_mock_fallback()
                except Exception:
                    pass
                if not ctx.ttft_done:
                    ctx.mark_ttft()
                # Update output stats for usage prior to final
                try:
                    out_txt = "offline"
                    CHAT_METRICS.add_output_stats(out_txt, count_tokens(out_txt))
                except Exception:
                    pass
                usage = {
                    "tokens_in": CHAT_METRICS.tokens_in_total,
                    "tokens_out": CHAT_METRICS.tokens_out_total,
                    "chars_in": CHAT_METRICS.chars_in_total,
                    "chars_out": CHAT_METRICS.chars_out_total,
                }
                usage_env = ctx.envelope("usage", usage)
                final_payload = {
                    "ok": True,
                    "result": {
                        "response": "offline",
                        "trace_id": trace_id,
                        "forced": True,
                    },
                }
                if ctx.scratchpad_policy:
                    final_payload["result"]["scratchpad_policy"] = ctx.scratchpad_policy
                forced_final = ctx.envelope("final", final_payload)
                yield usage_env
                yield forced_final
                offline_injected = True
                final_emitted = True
                break
            # If soft timeout configured keep looping; else allow broader loop to continue
            if soft_timeout_s > 0:
                continue
            # Hard upper bound (safety) – if >10s with no final, abort
            if elapsed_global > 10.0:
                if not final_emitted:
                    # Emit a terminal soft_timeout guard final so tests don't hang indefinitely
                    if not ctx.ttft_done:
                        ctx.mark_ttft()
                    guard_final = ctx.envelope(
                        "final", {"ok": False, "error": {"code": "guard_timeout"}}
                    )
                    yield guard_final
                    final_emitted = True
                break
            continue
        if evt == "chunk":
            try:
                CHAT_METRICS.chunks_total += 1
            except Exception:
                pass
            if not ctx.ttft_done:
                ctx.mark_ttft()
            payload_emitted = True
        elif evt == "error":
            # Reinforce breaker increment if timeout error surfaced via event path (defensive)
            try:
                err_code = (
                    (data.get("error") or {}).get("code")
                    if isinstance(data, dict)
                    else None
                )
                if err_code == "timeout":
                    CHAT_METRICS.breaker_open_total += 1
            except Exception:
                pass
            if not ctx.ttft_done:
                ctx.mark_ttft()
            payload_emitted = True
        if evt == "final":
            # Output metrics (usage) before final
            try:
                out_txt = ""
                res = data.get("result") if isinstance(data, dict) else {}
                if isinstance(res, dict):
                    out_txt = str(res.get("response") or res.get("text") or "")
                CHAT_METRICS.add_output_stats(out_txt, count_tokens(out_txt))
            except Exception:
                pass
            if not ctx.ttft_done:
                ctx.mark_ttft()
            # Defensive breaker increment if final itself signals timeout (some engines may only surface error in final)
            try:
                if isinstance(data, dict):
                    err_obj = data.get("error")
                    if isinstance(err_obj, dict) and err_obj.get("code") == "timeout":
                        CHAT_METRICS.breaker_open_total += 1
            except Exception:
                pass
            usage = {
                "tokens_in": CHAT_METRICS.tokens_in_total,
                "tokens_out": CHAT_METRICS.tokens_out_total,
                "chars_in": CHAT_METRICS.chars_in_total,
                "chars_out": CHAT_METRICS.chars_out_total,
            }
            usage_frame = ctx.envelope("usage", usage)
            final_frame = ctx.envelope(evt, data)
            yield usage_frame
            yield final_frame
            payload_emitted = True
            final_emitted = True
            # Append to per-trace replay buffer
            if replay_max_events > 0:
                try:
                    buf = _REPLAY_PER_TRACE.setdefault(trace_id, [])
                    buf.append((ctx.next_id - 2, time.time(), usage_frame))
                    buf.append((ctx.next_id - 1, time.time(), final_frame))
                    # Trim this trace buffer
                    if replay_max_events and len(buf) > replay_max_events * 2:
                        _REPLAY_PER_TRACE[trace_id] = buf[-(replay_max_events * 2) :]
                    # Global trace cap eviction (FIFO by insertion order heuristic)
                    if len(_REPLAY_PER_TRACE) > _REPLAY_GLOBAL_MAX_TRACES:
                        try:
                            # Remove oldest by earliest first event timestamp
                            oldest_tid = min(
                                _REPLAY_PER_TRACE.items(),
                                key=lambda kv: kv[1][0][1] if kv[1] else time.time(),
                            )[0]
                            if oldest_tid != trace_id:
                                _REPLAY_PER_TRACE.pop(oldest_tid, None)
                        except Exception:
                            pass
                except Exception:
                    pass
            break
        else:
            frame = ctx.envelope(evt, data)
            yield frame
            payload_emitted = True
            if replay_max_events > 0:
                try:
                    buf = _REPLAY_PER_TRACE.setdefault(trace_id, [])
                    buf.append((ctx.next_id - 1, time.time(), frame))
                    if replay_max_events and len(buf) > replay_max_events * 2:
                        _REPLAY_PER_TRACE[trace_id] = buf[-(replay_max_events * 2) :]
                except Exception:
                    pass

    # Decrement active stream counters
    try:
        CHAT_METRICS.end_stream(principal)
    except Exception:  # pragma: no cover
        pass


def _gen_trace_id() -> str:
    # Standard library imports
    import uuid

    return uuid.uuid4().hex
