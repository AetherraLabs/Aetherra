"""Metrics accumulation utilities (expanded).

Includes:
 - Chat counters (requests, streams, fallback paths)
 - Rolling kernel cycle time fallback histogram (ms)
 - Rolling orchestrator task latency fallback histogram (ms)
 - Memory + quantum metrics snapshot (queried lazily)
 - Trainer metrics (via trainer service; placeholder until full extraction)

This module focuses on assembling Prometheus plaintext lines without Flask
dependencies. The blueprint invokes ``build_all_metrics_lines`` then wraps the
result in a Response.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from . import registry_client

# (plugin metrics imported lazily in builder)

try:  # trainer service optional (may not yet be fully migrated)
    from . import trainer as trainer_service  # type: ignore
except Exception:  # pragma: no cover - fallback stub
    trainer_service = None  # type: ignore


@dataclass
class ChatMetrics:
    """In-memory accumulation for chat-centric metrics.

    This mirrors the legacy monolith's counters sufficient for Prometheus exports.
    Histograms are stored as cumulative bucket counters updated on observation.
    """

    requests_total: int = 0
    streams_current: int = 0
    streams_by_principal: Dict[str, int] = field(default_factory=dict)
    fallback_mock_total: int = 0  # aggregate counter (stable underlying counter)
    fallback_path_counts: Dict[str, int] = field(
        default_factory=lambda: {"mock": 0, "cached": 0, "engine": 0}
    )
    # Latency histogram + aggregates
    latency_ms_sum: float = 0.0
    latency_count: int = 0
    latency_hist: Dict[int, int] = field(
        default_factory=lambda: {
            50: 0,
            100: 0,
            250: 0,
            500: 0,
            1000: 0,
            2000: 0,
            5000: 0,
        }
    )
    # Time-to-first-token (TTFT) placeholders for future streaming extraction
    ttft_ms_sum: float = 0.0
    ttft_count: int = 0
    ttft_hist: Dict[int, int] = field(
        default_factory=lambda: {50: 0, 100: 0, 250: 0, 500: 0, 1000: 0, 2000: 0}
    )
    # Text + token IO counters
    chars_in_total: int = 0
    chars_out_total: int = 0
    tokens_in_total: int = 0
    tokens_out_total: int = 0
    chunks_total: int = 0
    # Breaker / timeout counter
    breaker_open_total: int = 0
    # Soft timeout counter (SSE enforced timeouts before engine responds)
    soft_timeouts_total: int = 0
    # Security / auth related counters (Phase 0 hardening)
    auth_missing_token_total: int = 0  # AI API call attempted without required token
    auth_invalid_token_total: int = (
        0  # Provided token rejected (placeholder; increment site-wide when implemented)
    )
    hmr_denied_total: int = 0  # Total HMR load/reload requests denied
    hmr_denied_reasons: Dict[str, int] = field(default_factory=dict)  # reason -> count
    # SSE resume gap counter (P1 replay feature)
    resume_gaps_total: int = 0
    # Export deltas
    fallback_mock_delta: float = 0.0  # per-scrape delta integration
    first_scrape: bool = True

    def inc_request(self):
        self.requests_total += 1

    def start_stream(self, principal: str):
        self.streams_current += 1
        if principal:
            self.streams_by_principal[principal] = (
                self.streams_by_principal.get(principal, 0) + 1
            )

    def end_stream(self, principal: str):
        if self.streams_current > 0:
            self.streams_current -= 1
        if principal and principal in self.streams_by_principal:
            self.streams_by_principal[principal] = max(
                0, self.streams_by_principal.get(principal, 1) - 1
            )

    def record_mock_fallback(self):
        self.fallback_mock_total += 1
        self.fallback_path_counts["mock"] = self.fallback_path_counts.get("mock", 0) + 1
        self.fallback_mock_delta += 1

    def observe_latency_ms(self, ms: float):
        if ms <= 0:
            return
        self.latency_ms_sum += ms
        self.latency_count += 1
        placed = False
        for b in (50, 100, 250, 500, 1000, 2000, 5000):
            if ms <= b:
                self.latency_hist[b] = int(self.latency_hist.get(b, 0)) + 1
                placed = True
                break
        if not placed:
            # treat > max bucket as +Inf bucket using sentinel key
            self.latency_hist[5000] = int(self.latency_hist.get(5000, 0)) + 1

    def add_input_stats(self, text: str, tokens: int):
        try:
            self.chars_in_total += len(text or "")
        except Exception:
            pass
        try:
            self.tokens_in_total += int(tokens)
        except Exception:
            pass

    def add_output_stats(self, text: str, tokens: int):
        try:
            self.chars_out_total += len(text or "")
        except Exception:
            pass
        try:
            self.tokens_out_total += int(tokens)
        except Exception:
            pass


chat_metrics = ChatMetrics()


@dataclass
class KernelHist:
    buckets: Dict[int, int] = field(
        default_factory=lambda: {10: 0, 20: 0, 50: 0, 100: 0, 200: 0, 500: 0, 1000: 0}
    )
    inf: int = 0

    def observe_cycle_ms(self, ms_val: float):
        if ms_val <= 0:
            return
        placed = False
        for b in (10, 20, 50, 100, 200, 500, 1000):
            if ms_val <= b:
                self.buckets[b] = int(self.buckets.get(b, 0)) + 1
                placed = True
                break
        if not placed:
            self.inf += 1

    def lines(self) -> List[str]:
        cum = 0
        out: List[str] = []
        for b in (10, 20, 50, 100, 200, 500, 1000):
            cum += int(self.buckets.get(b, 0))
            out.append(f'aetherra_kernel_cycle_time_ms_bucket{{le="{b}"}} {cum}')
        out.append(
            f'aetherra_kernel_cycle_time_ms_bucket{{le="+Inf"}} {cum + int(self.inf)}'
        )
        return out


@dataclass
class OrchestratorHist:
    buckets: Dict[int, int] = field(
        default_factory=lambda: {
            10: 0,
            20: 0,
            50: 0,
            100: 0,
            200: 0,
            500: 0,
            1000: 0,
            2000: 0,
        }
    )
    inf: int = 0

    def observe_latency_ms(self, ms_val: float):
        if ms_val <= 0:
            return
        placed = False
        for b in (10, 20, 50, 100, 200, 500, 1000, 2000):
            if ms_val <= b:
                self.buckets[b] = int(self.buckets.get(b, 0)) + 1
                placed = True
                break
        if not placed:
            self.inf += 1

    def lines(self) -> List[str]:
        cum = 0
        out: List[str] = []
        for b in (10, 20, 50, 100, 200, 500, 1000, 2000):
            cum += int(self.buckets.get(b, 0))
            out.append(
                f'aetherra_orchestrator_task_latency_ms_bucket{{le="{b}"}} {cum}'
            )
        out.append(
            f'aetherra_orchestrator_task_latency_ms_bucket{{le="+Inf"}} {cum + int(self.inf)}'
        )
        return out


kernel_hist = KernelHist()
orchestrator_hist = OrchestratorHist()


# --- Security / HMR metrics helpers (Phase 0) ---
def inc_auth_missing_token():  # pragma: no cover - simple counter
    try:
        chat_metrics.auth_missing_token_total += 1
    except Exception:
        pass


def inc_auth_invalid_token():  # pragma: no cover
    try:
        chat_metrics.auth_invalid_token_total += 1
    except Exception:
        pass


def inc_hmr_denied(reason: str):  # pragma: no cover
    try:
        chat_metrics.hmr_denied_total += 1
        if reason:
            chat_metrics.hmr_denied_reasons[reason] = (
                chat_metrics.hmr_denied_reasons.get(reason, 0) + 1
            )
    except Exception:
        pass


def export_prometheus(lines: List[str]) -> str:
    body = "\n".join(lines) + "\n"
    return body


def baseline_reset_if_first(metrics: ChatMetrics):
    if metrics.first_scrape and metrics.requests_total == 0:
        metrics.fallback_mock_total = 0
        metrics.fallback_path_counts["mock"] = 0
        metrics.first_scrape = False
    elif metrics.first_scrape:
        metrics.first_scrape = False


def chat_metrics_lines(metrics: ChatMetrics) -> List[str]:
    lines: List[str] = []
    # HELP/TYPE preamble (added once per scrape; harmless repetition per Prometheus exposition format)
    lines.extend(
        [
            "# HELP aetherra_chat_requests_total Total chat requests processed",
            "# TYPE aetherra_chat_requests_total counter",
            f"aetherra_chat_requests_total {metrics.requests_total}",
            "# HELP aetherra_chat_streams_current Active streaming connections",
            "# TYPE aetherra_chat_streams_current gauge",
            f"aetherra_chat_streams_current {metrics.streams_current}",
            "# HELP aetherra_chat_streams_current_by_principal Active streaming connections by principal",
            "# TYPE aetherra_chat_streams_current_by_principal gauge",
            "# HELP aetherra_chat_latency_ms_sum Cumulative chat response latency (ms)",
            "# TYPE aetherra_chat_latency_ms_sum counter",
            f"aetherra_chat_latency_ms_sum {metrics.latency_ms_sum}",
            "# HELP aetherra_chat_latency_count Number of latency observations",
            "# TYPE aetherra_chat_latency_count counter",
            f"aetherra_chat_latency_count {metrics.latency_count}",
        ]
    )
    # Per-principal gauges
    try:
        for p, v in metrics.streams_by_principal.items():
            lines.append(
                f'aetherra_chat_streams_current_by_principal{{principal="{p}"}} {v}'
            )
    except Exception:
        pass
    try:
        cum = 0
        order = [50, 100, 250, 500, 1000, 2000, 5000]
        for b in order:
            cnt = int(metrics.latency_hist.get(b, 0))
            cum += max(0, cnt)
            if b == 50:  # first bucket emit HELP/TYPE for histogram once
                lines.append(
                    "# HELP aetherra_chat_latency_ms_bucket Chat latency histogram buckets"
                )
                lines.append("# TYPE aetherra_chat_latency_ms_bucket histogram")
            lines.append(f'aetherra_chat_latency_ms_bucket{{le="{b}"}} {cum}')
        lines.append(f'aetherra_chat_latency_ms_bucket{{le="+Inf"}} {cum}')
    except Exception:
        pass
    # Fallback path counters
    mock_val = metrics.fallback_mock_total + metrics.fallback_mock_delta
    lines.append("# HELP aetherra_chat_fallback_total Fallback path counts by path")
    lines.append("# TYPE aetherra_chat_fallback_total counter")
    lines.append(f'aetherra_chat_fallback_total{{path="mock"}} {mock_val}')
    lines.append(
        f'aetherra_chat_fallback_total{{path="cached"}} {metrics.fallback_path_counts.get("cached", 0)}'
    )
    lines.append(
        f'aetherra_chat_fallback_total{{path="engine"}} {metrics.fallback_path_counts.get("engine", 0)}'
    )
    # IO metrics
    lines.extend(
        [
            "# HELP aetherra_chat_chars_in_total Total input characters",
            "# TYPE aetherra_chat_chars_in_total counter",
            f"aetherra_chat_chars_in_total {metrics.chars_in_total}",
            "# HELP aetherra_chat_chars_out_total Total output characters",
            "# TYPE aetherra_chat_chars_out_total counter",
            f"aetherra_chat_chars_out_total {metrics.chars_out_total}",
            "# HELP aetherra_chat_tokens_in_total Total input tokens (approx/heuristic)",
            "# TYPE aetherra_chat_tokens_in_total counter",
            f"aetherra_chat_tokens_in_total {metrics.tokens_in_total}",
            "# HELP aetherra_chat_tokens_out_total Total output tokens (approx/heuristic)",
            "# TYPE aetherra_chat_tokens_out_total counter",
            f"aetherra_chat_tokens_out_total {metrics.tokens_out_total}",
            "# HELP aetherra_chat_chunks_total Total SSE chunks emitted",
            "# TYPE aetherra_chat_chunks_total counter",
            f"aetherra_chat_chunks_total {metrics.chunks_total}",
            "# HELP aetherra_chat_resume_gaps_total Total SSE resume gap detections (missed events)",
            "# TYPE aetherra_chat_resume_gaps_total counter",
            f"aetherra_chat_resume_gaps_total {getattr(metrics, 'resume_gaps_total', 0)}",
        ]
    )
    # TTFT aggregates + histogram (always export zeros for discoverability)
    lines.append("# HELP aetherra_chat_ttft_ms_sum Time to first token cumulative (ms)")
    lines.append("# TYPE aetherra_chat_ttft_ms_sum counter")
    lines.append(f"aetherra_chat_ttft_ms_sum {metrics.ttft_ms_sum}")
    lines.append("# HELP aetherra_chat_ttft_count Number of TTFT observations")
    lines.append("# TYPE aetherra_chat_ttft_count counter")
    lines.append(f"aetherra_chat_ttft_count {metrics.ttft_count}")
    try:
        cum_t = 0
        order_t = [50, 100, 250, 500, 1000, 2000]
        for b in order_t:
            cnt = int(metrics.ttft_hist.get(b, 0))
            cum_t += max(0, cnt)
            if b == 50:
                lines.append(
                    "# HELP aetherra_chat_ttft_ms_bucket TTFT latency histogram buckets"
                )
                lines.append("# TYPE aetherra_chat_ttft_ms_bucket histogram")
            lines.append(f'aetherra_chat_ttft_ms_bucket{{le="{b}"}} {cum_t}')
        lines.append(f'aetherra_chat_ttft_ms_bucket{{le="+Inf"}} {cum_t}')
    except Exception:
        pass
    # Breaker metric
    lines.append(
        "# HELP aetherra_chat_breaker_open_total Circuit breaker/timeouts opened total"
    )
    lines.append("# TYPE aetherra_chat_breaker_open_total counter")
    lines.append(f"aetherra_chat_breaker_open_total {metrics.breaker_open_total}")
    # Soft timeout counter (export even if zero for discoverability)
    lines.append(
        "# HELP aetherra_chat_soft_timeouts_total Soft timeouts enforced before engine response"
    )
    lines.append("# TYPE aetherra_chat_soft_timeouts_total counter")
    try:
        st_val = int(getattr(metrics, "soft_timeouts_total", 0))
    except Exception:
        st_val = 0
    lines.append(f"aetherra_chat_soft_timeouts_total {st_val}")
    # Security counters
    lines.append(
        "# HELP aetherra_chat_auth_missing_token_total Requests rejected due to missing required auth token"
    )
    lines.append("# TYPE aetherra_chat_auth_missing_token_total counter")
    lines.append(
        f"aetherra_chat_auth_missing_token_total {metrics.auth_missing_token_total}"
    )
    lines.append(
        "# HELP aetherra_chat_auth_invalid_token_total Requests rejected due to invalid/incorrect auth token"
    )
    lines.append("# TYPE aetherra_chat_auth_invalid_token_total counter")
    lines.append(
        f"aetherra_chat_auth_invalid_token_total {metrics.auth_invalid_token_total}"
    )
    lines.append("# HELP aetherra_hmr_denied_total Hot module reload attempts denied")
    lines.append("# TYPE aetherra_hmr_denied_total counter")
    lines.append(f"aetherra_hmr_denied_total {metrics.hmr_denied_total}")
    if metrics.hmr_denied_reasons:
        lines.append(
            "# HELP aetherra_hmr_denied_reasons_total HMR deny counts by reason"
        )
        lines.append("# TYPE aetherra_hmr_denied_reasons_total counter")
        for reason, cnt in metrics.hmr_denied_reasons.items():
            safe_reason = reason.replace('"', '"')
            lines.append(
                f'aetherra_hmr_denied_reasons_total{{reason="{safe_reason}"}} {cnt}'
            )
    # clear delta after scrape
    metrics.fallback_mock_delta = 0
    return lines


def _num(x: Any) -> float:  # safe numeric conversion
    try:
        return float(x)
    except Exception:
        return 0.0


def _trainer_metrics_lines() -> List[str]:
    # Provide HELP/TYPE once (not strictly required each scrape but acceptable)
    preamble = [
        "# HELP aetherra_trainer_enabled Trainer enabled gauge (1=enabled,0=disabled)",
        "# TYPE aetherra_trainer_enabled gauge",
        "# HELP aetherra_trainer_jobs_total Trainer jobs by state",
        "# TYPE aetherra_trainer_jobs_total counter",
        "# HELP aetherra_trainer_jobs_running Currently running trainer jobs",
        "# TYPE aetherra_trainer_jobs_running gauge",
        "# HELP aetherra_trainer_evals_total Trainer evals by state",
        "# TYPE aetherra_trainer_evals_total counter",
        "# HELP aetherra_trainer_eval_runs_total Total evaluation runs",
        "# TYPE aetherra_trainer_eval_runs_total counter",
        "# HELP aetherra_trainer_eval_last_score Last evaluation score",
        "# TYPE aetherra_trainer_eval_last_score gauge",
    ]
    if not trainer_service or not hasattr(trainer_service, "snapshot_metrics"):
        return preamble + [
            "aetherra_trainer_enabled 0",
            'aetherra_trainer_jobs_total{state="queued"} 0',
            'aetherra_trainer_jobs_total{state="running"} 0',
            'aetherra_trainer_jobs_total{state="completed"} 0',
            'aetherra_trainer_jobs_total{state="failed"} 0',
            "aetherra_trainer_jobs_running 0",
            "aetherra_trainer_eval_runs_total 0",
            'aetherra_trainer_evals_total{state="queued"} 0',
            'aetherra_trainer_evals_total{state="running"} 0',
            'aetherra_trainer_evals_total{state="completed"} 0',
            'aetherra_trainer_evals_total{state="failed"} 0',
            "aetherra_trainer_eval_last_score 0",
        ]
    try:
        snap = trainer_service.snapshot_metrics()  # type: ignore[attr-defined]
    except Exception:
        return preamble + [
            "aetherra_trainer_enabled 0",
            "aetherra_trainer_eval_last_score 0",
        ]
    lines: List[str] = []
    lines.append(f"aetherra_trainer_enabled {1 if snap.get('enabled') else 0}")
    for st in ("queued", "running", "completed", "failed"):
        lines.append(
            f'aetherra_trainer_jobs_total{{state="{st}"}} {_num(snap.get("jobs", {}).get(st, 0))}'
        )
    lines.append(f"aetherra_trainer_jobs_running {_num(snap.get('jobs_running', 0))}")
    lines.append(
        f"aetherra_trainer_eval_runs_total {_num(snap.get('eval_runs_total', 0))}"
    )
    for st in ("queued", "running", "completed", "failed"):
        lines.append(
            f'aetherra_trainer_evals_total{{state="{st}"}} {_num(snap.get("evals", {}).get(st, 0))}'
        )
    # Always emit last score (default 0) for discoverability
    last_score = snap.get("eval_last_score")
    if last_score is None:
        last_score = 0
    lines.append(f"aetherra_trainer_eval_last_score {_num(last_score)}")
    return preamble + lines


def build_all_metrics_lines() -> List[str]:  # core builder used by blueprint
    lines: List[str] = []
    # Chat
    baseline_reset_if_first(chat_metrics)
    lines.extend(chat_metrics_lines(chat_metrics))

    # Kernel
    # Kernel status (best-effort). If registry not yet started, skip.
    ks = registry_client.get_kernel_status() or {}
    m = ks.get("metrics", {}) if ks else {}
    try:
        uptime = _num(ks.get("uptime") or (m or {}).get("uptime")) if ks else 0.0
    except Exception:
        uptime = 0.0
    lines.append(f"aetherra_kernel_uptime_seconds {uptime}")
    # Export effective plugin invoke timeout (gauge) if available
    try:
        pit = ks.get("plugin_invoke_timeout_sec") if ks else None
        if pit is not None:
            lines.append(
                "# HELP aetherra_kernel_plugin_invoke_timeout_sec Effective plugin invoke timeout seconds (post-clamp)"
            )
            lines.append("# TYPE aetherra_kernel_plugin_invoke_timeout_sec gauge")
            lines.append(f"aetherra_kernel_plugin_invoke_timeout_sec {_num(pit)}")
        # Night schedule guard status (P1 #10)
        if ks.get("night_schedule_guard_pass") is not None:
            lines.append(
                "# HELP aetherra_kernel_night_schedule_guard_pass 1 if night cycle timezone guard passed, 0 if failing (prod without explicit TZ)"
            )
            lines.append("# TYPE aetherra_kernel_night_schedule_guard_pass gauge")
            lines.append(
                f"aetherra_kernel_night_schedule_guard_pass {1 if ks.get('night_schedule_guard_pass') else 0}"
            )
        # Backpressure guard status
        if ks.get("backpressure_guard_pass") is not None:
            lines.append(
                "# HELP aetherra_kernel_backpressure_guard_pass 1 if kernel backpressure guard passed, 0 if failed"
            )
            lines.append("# TYPE aetherra_kernel_backpressure_guard_pass gauge")
            lines.append(
                f"aetherra_kernel_backpressure_guard_pass {1 if ks.get('backpressure_guard_pass') else 0}"
            )
            viol = ks.get("backpressure_guard_violations") or []
            lines.append(
                "# HELP aetherra_kernel_backpressure_guard_violations Info series listing violation types (value always 1)"
            )
            lines.append("# TYPE aetherra_kernel_backpressure_guard_violations gauge")
            for v in viol:
                try:
                    lines.append(
                        f'aetherra_kernel_backpressure_guard_violations{{violation="{v}"}} 1'
                    )
                except Exception:
                    pass
    except Exception:
        pass
    # Unsafe override detection gauges
    try:
        overrides = {
            "AETHERRA_PROD_UNSAFE_ALLOW": os.getenv("AETHERRA_PROD_UNSAFE_ALLOW"),
            "AETHERRA_ALLOW_UNBOUNDED": os.getenv("AETHERRA_ALLOW_UNBOUNDED"),
        }
        present = 1 if any(v not in (None, "", "0") for v in overrides.values()) else 0
        lines.append(
            "# HELP aetherra_unsafe_override_present 1 if any production unsafe override env var is set"
        )
        lines.append("# TYPE aetherra_unsafe_override_present gauge")
        lines.append(f"aetherra_unsafe_override_present {present}")
        lines.append(
            "# HELP aetherra_unsafe_override_info Individual unsafe override environment variable presence (1=present)"
        )
        lines.append("# TYPE aetherra_unsafe_override_info gauge")
        for k, v in overrides.items():
            val = 1 if v not in (None, "", "0") else 0
            lines.append(f'aetherra_unsafe_override_info{{override="{k}"}} {val}')
    except Exception:
        pass
    # Always export histogram buckets for discoverability (even if zero)
    try:
        raw = float((m or {}).get("last_cycle_time", 0.0))
        ms_val = raw * 1000.0 if raw and raw < 10 else raw
        if ms_val:
            kernel_hist.observe_cycle_ms(ms_val)
    except Exception:
        pass
    lines.extend(kernel_hist.lines())
    if ks:
        qsz = ks.get("queue_sizes", {}) or {}
        lines.append(
            f'aetherra_kernel_queue_size{{queue="high"}} {_num(qsz.get("high_priority", 0))}'
        )
        lines.append(
            f'aetherra_kernel_queue_size{{queue="normal"}} {_num(qsz.get("normal_priority", 0))}'
        )
        lines.append(
            f'aetherra_kernel_queue_size{{queue="background"}} {_num(qsz.get("background", 0))}'
        )

    # Orchestrator
    orch = registry_client.get_orchestrator_status() or {}
    try:
        ms_val = float(orch.get("avg_task_latency_ms", 0.0)) if orch else 0.0
        if ms_val:
            orchestrator_hist.observe_latency_ms(ms_val)
    except Exception:
        pass
    # Always export orchestrator histogram buckets
    lines.extend(orchestrator_hist.lines())
    if orch:
        lines.append(
            f"aetherra_orchestrator_agents_total {_num(orch.get('total_agents', 0))}"
        )
        lines.append(
            f"aetherra_orchestrator_tasks_pending_total {_num(orch.get('pending_tasks', 0))}"
        )

    # Memory quantum + audit
    mq = registry_client.get_memory_quantum_status() or {}
    if mq:
        if "coherence" in mq:
            lines.append(
                f"aetherra_memory_coherence_score {_num(mq.get('coherence', 0.0))}"
            )
        if "branches" in mq:
            lines.append(
                f"aetherra_memory_branches_total {_num(mq.get('branches', 0))}"
            )
        if "fragments" in mq:
            lines.append(
                f"aetherra_memory_fragments_total {_num(mq.get('fragments', 0))}"
            )
    # QFAC policy decision metrics (P1 #9). Best-effort: try optional qfac_memory_system
    try:
        from Aetherra.aetherra_core.memory.qfac_integration import (
            QFACMemorySystem,  # type: ignore
        )

        # Access via service registry for canonical instance
        qfac_status = None
        try:
            qs = registry_client.get_registry_status() or {}
            # Not all registries expose direct instance list; fallback: dynamic import probe below
            _ = qs  # placeholder to avoid linter
        except Exception:
            pass
        # Direct import path: attempt to locate a global instance reference from launcher systems via registry
        try:
            # Indirect retrieval: memory quantum status may include qfac info in future; for now attempt attribute walk
            # This is intentionally best-effort to avoid tight coupling.
            # Heuristic: scan globals for a QFACMemorySystem singleton (lightweight)
            for obj in list(globals().values()):
                if isinstance(
                    obj, QFACMemorySystem
                ):  # pragma: no cover - heuristic path
                    qfac_status = obj.get_policy_decision()
                    break
        except Exception:
            qfac_status = None
        if not qfac_status:
            # Fallback: attempt lazy construction only to introspect policy; this yields a fresh decision
            try:
                _tmp = QFACMemorySystem("_qfac_policy_probe")  # type: ignore
                qfac_status = _tmp.get_policy_decision()
            except Exception:
                qfac_status = None
        if isinstance(qfac_status, dict) and qfac_status:
            mode = qfac_status.get("mode", "classical")
            allowed = 1 if qfac_status.get("allowed") else 0
            reason = str(qfac_status.get("reason", "unknown"))
            policy = str(qfac_status.get("policy", "unknown"))
            lines.append(
                "# HELP aetherra_qfac_policy_mode_current Current effective QFAC mode"
            )
            lines.append("# TYPE aetherra_qfac_policy_mode_current gauge")
            mode_map = {"classical": 0, "hybrid": 1, "quantum": 2}
            lines.append(f"aetherra_qfac_policy_mode_current {mode_map.get(mode, 0)}")
            lines.append(
                "# HELP aetherra_qfac_policy_allowed 1 if desired mode allowed, 0 if downgraded"
            )
            lines.append("# TYPE aetherra_qfac_policy_allowed gauge")
            lines.append(f"aetherra_qfac_policy_allowed {allowed}")
            lines.append(
                "# HELP aetherra_qfac_policy_info Info series for QFAC policy decision (value=1)"
            )
            lines.append("# TYPE aetherra_qfac_policy_info gauge")
            safe_reason = reason.replace('"', '"')
            safe_policy = policy.replace('"', '"')
            lines.append(
                f'aetherra_qfac_policy_info{{key="reason",value="{safe_reason}"}} 1'
            )
            lines.append(
                f'aetherra_qfac_policy_info{{key="policy",value="{safe_policy}"}} 1'
            )
    except Exception:
        pass
    ma = registry_client.get_memory_audit() or {}
    if isinstance(ma.get("audit"), dict):
        audit = ma.get("audit") or {}
        nodes_val = audit.get("nodes")
        if isinstance(nodes_val, (list, tuple)):
            lines.append(f"aetherra_memory_branch_nodes_total {_num(len(nodes_val))}")
        edges_val = audit.get("edges")
        if isinstance(edges_val, (list, tuple)):
            lines.append(f"aetherra_memory_branch_edges_total {_num(len(edges_val))}")

    # Trainer metrics
    lines.extend(_trainer_metrics_lines())

    # Timestamp
    lines.append(
        f"aetherra_hub_export_timestamp_seconds {int(datetime.utcnow().timestamp())}"
    )

    # Plugin metrics appended last
    try:
        from .plugin_metrics import (
            as_prometheus_lines as plugin_metrics_lines,  # type: ignore
        )

        lines.extend(plugin_metrics_lines())
    except Exception:
        pass
    # Key encryption status (security hardening P1) – best-effort
    try:
        keys_path = os.path.expanduser("~/.aetherra/keys.json")
        enc = 0
        if os.path.exists(keys_path):
            import json as _json  # local import to avoid global cost

            try:
                data = _json.loads(open(keys_path, "r", encoding="utf-8").read())
                if isinstance(data, dict) and data.get("__encrypted__") is True:
                    enc = 1
            except Exception:
                pass
        mk_present = (
            1
            if (
                os.getenv("AETHERRA_KEYS_MASTER")
                or os.path.exists(os.path.expanduser("~/.aetherra/keys_master.key"))
            )
            else 0
        )
        lines.append(
            "# HELP aetherra_keys_encrypted 1 if keys.json is in encrypted layout (__encrypted__=true)"
        )
        lines.append("# TYPE aetherra_keys_encrypted gauge")
        lines.append(f"aetherra_keys_encrypted {enc}")
        lines.append(
            "# HELP aetherra_master_key_present 1 if master key (env or file) present"
        )
        lines.append("# TYPE aetherra_master_key_present gauge")
        lines.append(f"aetherra_master_key_present {mk_present}")
    except Exception:
        pass
    return lines
