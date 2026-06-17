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

# Standard library imports
import contextlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Local imports
from . import registry_client

# (plugin metrics imported lazily in builder)

try:  # trainer service optional (may not yet be fully migrated)
    # Local imports
    from . import trainer as trainer_service
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
    streams_by_principal: dict[str, int] = field(default_factory=dict)
    fallback_mock_total: int = 0  # aggregate counter (stable underlying counter)
    fallback_path_counts: dict[str, int] = field(
        default_factory=lambda: {"mock": 0, "cached": 0, "engine": 0}
    )
    # Latency histogram + aggregates
    latency_ms_sum: float = 0.0
    latency_count: int = 0
    latency_hist: dict[int, int] = field(
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
    ttft_hist: dict[int, int] = field(
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
    rate_limited_total: int = 0
    # Soft timeout counter (SSE enforced timeouts before engine responds)
    soft_timeouts_total: int = 0
    # Security / auth related counters (Phase 0 hardening)
    auth_missing_token_total: int = 0  # AI API call attempted without required token
    auth_invalid_token_total: int = (
        0  # Provided token rejected (placeholder; increment site-wide when implemented)
    )
    hmr_denied_total: int = 0  # Total HMR load/reload requests denied
    hmr_denied_reasons: dict[str, int] = field(default_factory=dict)  # reason -> count
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
        with contextlib.suppress(Exception):
            self.chars_in_total += len(text or "")
        with contextlib.suppress(Exception):
            self.tokens_in_total += int(tokens)

    def add_output_stats(self, text: str, tokens: int):
        with contextlib.suppress(Exception):
            self.chars_out_total += len(text or "")
        with contextlib.suppress(Exception):
            self.tokens_out_total += int(tokens)


chat_metrics = ChatMetrics()
logger = logging.getLogger(__name__)


@dataclass
class KernelHist:
    buckets: dict[int, int] = field(
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

    def lines(self) -> list[str]:
        cum = 0
        out: list[str] = []
        for b in (10, 20, 50, 100, 200, 500, 1000):
            cum += int(self.buckets.get(b, 0))
            out.append(f'aetherra_kernel_cycle_time_ms_bucket{{le="{b}"}} {cum}')
        out.append(
            f'aetherra_kernel_cycle_time_ms_bucket{{le="+Inf"}} {cum + int(self.inf)}'
        )
        return out


@dataclass
class OrchestratorHist:
    buckets: dict[int, int] = field(
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

    def lines(self) -> list[str]:
        cum = 0
        out: list[str] = []
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
    chat_metrics.auth_missing_token_total += 1


def inc_auth_invalid_token():  # pragma: no cover
    chat_metrics.auth_invalid_token_total += 1


def inc_hmr_denied(reason: str):  # pragma: no cover
    chat_metrics.hmr_denied_total += 1
    if reason:
        chat_metrics.hmr_denied_reasons[reason] = (
            chat_metrics.hmr_denied_reasons.get(reason, 0) + 1
        )


def inc_chat_rate_limited():  # pragma: no cover - simple counter
    chat_metrics.rate_limited_total += 1


def export_prometheus(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def baseline_reset_if_first(metrics: ChatMetrics):
    if metrics.first_scrape and metrics.requests_total == 0:
        metrics.fallback_mock_total = 0
        metrics.fallback_path_counts["mock"] = 0
        metrics.first_scrape = False
    elif metrics.first_scrape:
        metrics.first_scrape = False


def chat_metrics_lines(metrics: ChatMetrics) -> list[str]:
    lines: list[str] = []
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
    with contextlib.suppress(Exception):
        for p, v in metrics.streams_by_principal.items():
            lines.append(
                f'aetherra_chat_streams_current_by_principal{{principal="{p}"}} {v}'
            )
    with contextlib.suppress(Exception):
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
    with contextlib.suppress(Exception):
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
    # Breaker metric
    lines.append(
        "# HELP aetherra_chat_breaker_open_total Circuit breaker/timeouts opened total"
    )
    lines.append("# TYPE aetherra_chat_breaker_open_total counter")
    lines.append(f"aetherra_chat_breaker_open_total {metrics.breaker_open_total}")
    lines.append(
        "# HELP aetherra_chat_rate_limited_total Chat requests rejected by engine rate limiting"
    )
    lines.append("# TYPE aetherra_chat_rate_limited_total counter")
    lines.append(
        f"aetherra_chat_rate_limited_total {getattr(metrics, 'rate_limited_total', 0)}"
    )
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


def _label_value(x: Any) -> str:
    return str(x).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _safe_len(obj: Any) -> int:
    try:
        return int(len(obj))
    except Exception:
        return 0


def _engine_ab_metrics_lines() -> list[str]:
    """Render A/B recall telemetry from the registered engine service."""
    session_metrics = registry_client.get_engine_session_metrics()
    engine_status = registry_client.get_engine_status() or {}
    ab_status = engine_status.get("ab") if isinstance(engine_status, dict) else None
    if not isinstance(ab_status, dict):
        ab_status = {}

    if not session_metrics and not ab_status:
        return []

    lines = [
        "# HELP aetherra_engine_ab_recall_total Total A/B recall operations",
        "# TYPE aetherra_engine_ab_recall_total counter",
        f"aetherra_engine_ab_recall_total {_num(session_metrics.get('ab_recall_total', 0))}",
        "# HELP aetherra_engine_ab_recall_classical_total Total classical A/B recall operations",
        "# TYPE aetherra_engine_ab_recall_classical_total counter",
        f"aetherra_engine_ab_recall_classical_total {_num(session_metrics.get('ab_recall_classical_total', 0))}",
        "# HELP aetherra_engine_ab_recall_quantum_total Total quantum A/B recall operations",
        "# TYPE aetherra_engine_ab_recall_quantum_total counter",
        f"aetherra_engine_ab_recall_quantum_total {_num(session_metrics.get('ab_recall_quantum_total', 0))}",
        "# HELP aetherra_engine_ab_recall_latency_ms_sum Cumulative A/B recall latency by bucket",
        "# TYPE aetherra_engine_ab_recall_latency_ms_sum counter",
    ]

    for bucket in ("classical", "quantum"):
        lines.append(
            f'aetherra_engine_ab_recall_latency_ms_sum{{bucket="{bucket}"}} '
            f"{_num(session_metrics.get(f'ab_recall_latency_ms_sum_{bucket}', 0))}"
        )

    lines.extend(
        [
            "# HELP aetherra_engine_ab_recall_latency_ms_count A/B recall latency observations by bucket",
            "# TYPE aetherra_engine_ab_recall_latency_ms_count counter",
        ]
    )
    for bucket in ("classical", "quantum"):
        lines.append(
            f'aetherra_engine_ab_recall_latency_ms_count{{bucket="{bucket}"}} '
            f"{_num(session_metrics.get(f'ab_recall_latency_ms_count_{bucket}', 0))}"
        )

    mode = ab_status.get("mode")
    if mode:
        lines.extend(
            [
                "# HELP aetherra_engine_ab_mode Active engine A/B recall mode",
                "# TYPE aetherra_engine_ab_mode gauge",
                f'aetherra_engine_ab_mode{{mode="{_label_value(mode)}"}} 1',
            ]
        )

    if "pmem_ready" in ab_status:
        lines.extend(
            [
                "# HELP aetherra_engine_ab_pmem_ready Persistent memory readiness for A/B recall",
                "# TYPE aetherra_engine_ab_pmem_ready gauge",
                f"aetherra_engine_ab_pmem_ready {1 if ab_status.get('pmem_ready') else 0}",
            ]
        )

    return lines


def _trainer_metrics_lines() -> list[str]:
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
        snap = trainer_service.snapshot_metrics()
    except Exception:
        return preamble + [
            "aetherra_trainer_enabled 0",
            "aetherra_trainer_eval_last_score 0",
        ]
    lines: list[str] = []
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


def _registry_metrics_lines() -> list[str]:
    status = registry_client.get_registry_status() or {}
    services = status.get("services") if isinstance(status, dict) else None
    if isinstance(services, dict | list):
        total = len(services)
    elif isinstance(status, dict):
        total = int(_num(status.get("total_services", 0)))
    else:
        total = 0
    return [
        "# HELP aetherra_registry_services_total Registered services visible to the Hub",
        "# TYPE aetherra_registry_services_total gauge",
        f"aetherra_registry_services_total {total}",
    ]


def build_all_metrics_lines() -> list[str]:  # core builder used by blueprint
    lines: list[str] = []
    # Chat
    baseline_reset_if_first(chat_metrics)
    lines.extend(chat_metrics_lines(chat_metrics))
    lines.extend(_registry_metrics_lines())

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
                with contextlib.suppress(Exception):
                    lines.append(
                        f'aetherra_kernel_backpressure_guard_violations{{violation="{v}"}} 1'
                    )
    except Exception:
        logger.exception("metrics: kernel status export failed")
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
        logger.debug("metrics: kernel histogram observe failed", exc_info=True)
    # Always export histogram buckets for discoverability (even if zero)
    try:
        raw = float((m or {}).get("last_cycle_time", 0.0))
        ms_val = raw * 1000.0 if raw and raw < 10 else raw
        if ms_val:
            kernel_hist.observe_cycle_ms(ms_val)
    except Exception:
        logger.debug("metrics: orchestrator latency observe failed", exc_info=True)
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
        inflight = ks.get("inflight") or {}
        if isinstance(inflight, dict):
            for target, count in sorted(inflight.items(), key=lambda item: str(item[0])):
                lines.append(
                    'aetherra_kernel_inflight_current'
                    f'{{target="{_label_value(target)}"}} {_num(count)}'
                )

    # HMR configuration gauges
    hmr_config = registry_client.get_hmr_config_metrics() or {}
    if hmr_config:
        lines.append(
            f"aetherra_hmr_enabled {1 if hmr_config.get('enabled') else 0}"
        )
        lines.append(f"aetherra_hmr_strict {1 if hmr_config.get('strict') else 0}")
        lines.append(
            "aetherra_hmr_allowed_sources_count "
            f"{_num(hmr_config.get('allowed_sources_count', 0))}"
        )
        lines.append(
            f"aetherra_hmr_audit_max_bytes {_num(hmr_config.get('audit_max_bytes', 0))}"
        )
        lines.append(
            "aetherra_hmr_audit_max_backups "
            f"{_num(hmr_config.get('audit_max_backups', 0))}"
        )
    hmr_audit = registry_client.get_hmr_audit_counters() or {}
    if hmr_audit:
        for event, count in sorted(hmr_audit.items(), key=lambda item: str(item[0])):
            lines.append(
                f'aetherra_hmr_audit_total{{event="{_label_value(event)}"}} {_num(count)}'
            )

    # KLM / KEB control-plane metrics
    klm_metrics = registry_client.get_klm_metrics() or {}
    if klm_metrics:
        for name in (
            "loads_total",
            "reloads_total",
            "rollbacks_total",
            "active_modules",
        ):
            if name in klm_metrics:
                lines.append(f"aetherra_klm_{name} {_num(klm_metrics.get(name, 0))}")
        per_module_active = klm_metrics.get("per_module_active") or {}
        if isinstance(per_module_active, dict):
            for module, active in sorted(
                per_module_active.items(), key=lambda item: str(item[0])
            ):
                lines.append(
                    'aetherra_klm_active_module'
                    f'{{module="{_label_value(module)}"}} {_num(active)}'
                )

    keb_metrics = registry_client.get_keb_metrics() or {}
    if keb_metrics:
        for name in (
            "events_published_total",
            "events_delivered_total",
            "events_dropped_burst",
        ):
            if name in keb_metrics:
                lines.append(f"aetherra_keb_{name} {_num(keb_metrics.get(name, 0))}")
        topic_backlog = keb_metrics.get("topic_backlog") or {}
        if isinstance(topic_backlog, dict):
            for topic, backlog in sorted(
                topic_backlog.items(), key=lambda item: str(item[0])
            ):
                lines.append(
                    'aetherra_keb_topic_backlog'
                    f'{{topic="{_label_value(topic)}"}} {_num(backlog)}'
                )

    # Orchestrator
    orch = registry_client.get_orchestrator_status() or {}
    try:
        ms_val = float(orch.get("avg_task_latency_ms", 0.0)) if orch else 0.0
        if ms_val:
            orchestrator_hist.observe_latency_ms(ms_val)
    except Exception:
        logger.debug("metrics: plugin metrics export failed", exc_info=True)
    # Always export orchestrator histogram buckets
    lines.extend(orchestrator_hist.lines())
    if orch:
        lines.append(
            f"aetherra_orchestrator_agents_total {_num(orch.get('total_agents', 0))}"
        )
        lines.append(
            f"aetherra_orchestrator_tasks_pending_total {_num(orch.get('pending_tasks', 0))}"
        )
        pending_by_priority = orch.get("pending_by_priority") or {}
        if isinstance(pending_by_priority, dict):
            for priority, count in sorted(
                pending_by_priority.items(), key=lambda item: str(item[0])
            ):
                lines.append(
                    "aetherra_orchestrator_tasks_pending"
                    f'{{priority="{_label_value(priority)}"}} {_num(count)}'
                )
        task_statuses = orch.get("task_statuses") or {}
        if isinstance(task_statuses, dict):
            for status, count in sorted(
                task_statuses.items(), key=lambda item: str(item[0])
            ):
                lines.append(
                    "aetherra_orchestrator_tasks_total"
                    f'{{status="{_label_value(status)}"}} {_num(count)}'
                )
        counters = orch.get("counters") or {}
        if isinstance(counters, dict):
            for name in (
                "timeouts_total",
                "policy_denied_total",
                "observer_gates_triggered_total",
                "observer_pending_human_total",
                "observer_denied_total",
                "drift_alerts_total",
            ):
                lines.append(
                    f"aetherra_orchestrator_{name} {_num(counters.get(name, 0))}"
                )
        coherence_policy = orch.get("coherence_policy") or {}
        if isinstance(coherence_policy, dict):
            lines.append(
                "aetherra_orchestrator_coherence_gate_min "
                f"{_num(coherence_policy.get('gate_min', 0.0))}"
            )
            lines.append(
                "aetherra_orchestrator_coherence_hard_min "
                f"{_num(coherence_policy.get('hard_min', 0.0))}"
            )
            lines.append(
                "aetherra_orchestrator_coherence_ema "
                f"{_num(coherence_policy.get('ema', 0.0))}"
            )
            lines.append(
                "aetherra_orchestrator_coherence_window_size "
                f"{_num(coherence_policy.get('window_size', 0))}"
            )
            lines.append(
                "aetherra_orchestrator_last_drift_alert_present "
                f"{1 if coherence_policy.get('last_drift_alert') is not None else 0}"
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

    # STORM metrics (STORM PR-5 + Shadow Mode + Day 8 Maintenance)
    storm = registry_client.get_storm_metrics() or {}
    if storm.get("enabled"):
        # HELP and TYPE declarations for STORM metrics
        lines.append(
            "# HELP aetherra_storm_approximate_recalls_total Total approximate recalls executed by STORM"
        )
        lines.append("# TYPE aetherra_storm_approximate_recalls_total counter")
        lines.append(
            "# HELP aetherra_storm_maintenance_total Total STORM maintenance operations (compaction, rebalancing)"
        )
        lines.append("# TYPE aetherra_storm_maintenance_total counter")
        lines.append(
            "# HELP aetherra_storm_branch_barycenters_total Total branch barycenter calculations"
        )
        lines.append("# TYPE aetherra_storm_branch_barycenters_total counter")
        lines.append(
            "# HELP aetherra_storm_shadow_comparisons_total Total shadow mode baseline comparisons"
        )
        lines.append("# TYPE aetherra_storm_shadow_comparisons_total counter")
        lines.append(
            "# HELP aetherra_storm_shadow_divergences_total Total shadow mode result divergences detected"
        )
        lines.append("# TYPE aetherra_storm_shadow_divergences_total counter")
        lines.append(
            "# HELP aetherra_storm_shadow_errors_total Total shadow mode execution errors"
        )
        lines.append("# TYPE aetherra_storm_shadow_errors_total counter")

        # Counters
        for metric in [
            "aetherra_storm_approximate_recalls_total",
            "aetherra_storm_maintenance_total",
            "aetherra_storm_branch_barycenters_total",
            "aetherra_storm_shadow_comparisons_total",
            "aetherra_storm_shadow_divergences_total",
            "aetherra_storm_shadow_errors_total",
        ]:
            if metric in storm:
                lines.append(f"{metric} {_num(storm.get(metric, 0))}")

        # HELP and TYPE declarations for STORM gauges
        lines.append("# HELP aetherra_storm_ot_cost_avg Average optimal transport cost")
        lines.append("# TYPE aetherra_storm_ot_cost_avg gauge")
        lines.append(
            "# HELP aetherra_storm_sheaf_inconsistency Sheaf inconsistency measure"
        )
        lines.append("# TYPE aetherra_storm_sheaf_inconsistency gauge")
        lines.append("# HELP aetherra_storm_tt_rank Current tensor-train rank")
        lines.append("# TYPE aetherra_storm_tt_rank gauge")
        lines.append(
            "# HELP aetherra_storm_recall_latency_ms_p95 95th percentile recall latency in milliseconds"
        )
        lines.append("# TYPE aetherra_storm_recall_latency_ms_p95 gauge")
        lines.append(
            "# HELP aetherra_storm_shadow_agreement_rate Shadow mode agreement rate (0.0-1.0)"
        )
        lines.append("# TYPE aetherra_storm_shadow_agreement_rate gauge")
        lines.append(
            "# HELP aetherra_storm_shadow_latency_ms_avg Average shadow mode comparison latency in milliseconds"
        )
        lines.append("# TYPE aetherra_storm_shadow_latency_ms_avg gauge")

        # Gauges
        for metric in [
            "aetherra_storm_ot_cost_avg",
            "aetherra_storm_sheaf_inconsistency",
            "aetherra_storm_tt_rank",
            "aetherra_storm_recall_latency_ms_p95",
            "aetherra_storm_shadow_agreement_rate",
            "aetherra_storm_shadow_latency_ms_avg",
        ]:
            if metric in storm:
                lines.append(f"{metric} {_num(storm.get(metric, 0.0))}")

        # Labeled gauge: maintenance_last{action=...}
        lines.append(
            "# HELP aetherra_storm_maintenance_last Timestamp of last maintenance operation by action type"
        )
        lines.append("# TYPE aetherra_storm_maintenance_last gauge")
        maint_last = storm.get("aetherra_storm_maintenance_last")
        if isinstance(maint_last, dict):
            for action, timestamp in maint_last.items():
                safe_action = str(action).replace('"', '\\"')
                lines.append(
                    f'aetherra_storm_maintenance_last{{action="{safe_action}"}} {_num(timestamp)}'
                )

    # QFAC validator & shadow logs (Phase 2 scaffolding): best-effort local probes
    def _get_qfac_validator_status() -> dict[str, Any]:
        try:
            # Try to reach a known service if present
            svc = registry_client.get_service("qfac_validator")
            if svc and hasattr(svc, "get_status"):
                st = svc.get_status()
                return st if isinstance(st, dict) else {}
        except Exception:
            logger.debug("metrics: qfac validator status probe failed", exc_info=True)
        return {}

    # Optional test overrides
    try:
        _v_fake = os.getenv("AETHERRA_QFAC_VALIDATOR_FAKE", "0")
        _v_green = int(os.getenv("AETHERRA_QFAC_VALIDATOR_FAKE_GREEN", "0"))
        _v_blocked = int(os.getenv("AETHERRA_QFAC_VALIDATOR_FAKE_BLOCKED", "0"))
    except Exception:
        _v_fake, _v_green, _v_blocked = "0", 0, 0
    qv = _get_qfac_validator_status()
    if _v_fake in ("1", "true", "True"):
        qv = {"green_total": _v_green, "blocked_total": _v_blocked}
    if qv:
        # Gauges: validator green/blocked counts
        lines.append(
            "# HELP aetherra_qfac_validator_green_total Total validations passed (green)"
        )
        lines.append("# TYPE aetherra_qfac_validator_green_total counter")
        lines.append(
            f"aetherra_qfac_validator_green_total {_num(qv.get('green_total', 0))}"
        )
        lines.append(
            "# HELP aetherra_qfac_validator_blocked_total Total validations blocked"
        )
        lines.append("# TYPE aetherra_qfac_validator_blocked_total counter")
        lines.append(
            f"aetherra_qfac_validator_blocked_total {_num(qv.get('blocked_total', 0))}"
        )
    else:
        # Schema defaults
        lines.append(
            "# HELP aetherra_qfac_validator_green_total Total validations passed (green)"
        )
        lines.append("# TYPE aetherra_qfac_validator_green_total counter")
        lines.append("aetherra_qfac_validator_green_total 0")
        lines.append(
            "# HELP aetherra_qfac_validator_blocked_total Total validations blocked"
        )
        lines.append("# TYPE aetherra_qfac_validator_blocked_total counter")
        lines.append("aetherra_qfac_validator_blocked_total 0")

    def _get_qfac_shadow_log_status() -> dict[str, Any]:
        try:
            svc = registry_client.get_service("qfac_shadow_logger")
            if svc and hasattr(svc, "get_status"):
                st = svc.get_status()
                return st if isinstance(st, dict) else {}
        except Exception:
            logger.debug("metrics: qfac shadow log status probe failed", exc_info=True)
        return {}

    try:
        _s_fake = os.getenv("AETHERRA_QFAC_SHADOW_FAKE", "0")
        _s_total = int(os.getenv("AETHERRA_QFAC_SHADOW_FAKE_TOTAL", "0"))
        _s_recent = int(os.getenv("AETHERRA_QFAC_SHADOW_FAKE_RECENT", "0"))
    except Exception:
        _s_fake, _s_total, _s_recent = "0", 0, 0
    ql = _get_qfac_shadow_log_status()
    if _s_fake in ("1", "true", "True"):
        ql = {"logs_total": _s_total, "logs_recent": _s_recent}
    if ql:
        lines.append(
            "# HELP aetherra_qfac_shadow_logs_total Total shadow logs recorded"
        )
        lines.append("# TYPE aetherra_qfac_shadow_logs_total counter")
        lines.append(f"aetherra_qfac_shadow_logs_total {_num(ql.get('logs_total', 0))}")
        lines.append(
            "# HELP aetherra_qfac_shadow_logs_recent Recent shadow logs in window"
        )
        lines.append("# TYPE aetherra_qfac_shadow_logs_recent gauge")
        lines.append(
            f"aetherra_qfac_shadow_logs_recent {_num(ql.get('logs_recent', 0))}"
        )
    else:
        lines.append(
            "# HELP aetherra_qfac_shadow_logs_total Total shadow logs recorded"
        )
        lines.append("# TYPE aetherra_qfac_shadow_logs_total counter")
        lines.append("aetherra_qfac_shadow_logs_total 0")
        lines.append(
            "# HELP aetherra_qfac_shadow_logs_recent Recent shadow logs in window"
        )
        lines.append("# TYPE aetherra_qfac_shadow_logs_recent gauge")
        lines.append("aetherra_qfac_shadow_logs_recent 0")
    # QFAC policy decision metrics (P1 #9). Best-effort: try optional qfac_memory_system
    policy_emitted = False
    snapshot_emitted = False
    parity_emitted = False
    try:
        # Aetherra imports
        from Aetherra.aetherra_core.memory.qfac_integration import (
            QFACMemorySystem,
        )

        # Access via service registry for canonical instance
        qfac_status = None
        try:
            qs = registry_client.get_registry_status() or {}
            # Not all registries expose direct instance list; fallback: dynamic import probe below
            _ = qs  # placeholder to avoid linter
        except Exception:
            logger.debug("metrics: registry status fetch failed", exc_info=True)
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
            logger.debug("metrics: global QFAC scan failed", exc_info=True)
            qfac_status = None
        if not qfac_status:
            # Fallback: attempt lazy construction only to introspect policy; this yields a fresh decision
            try:
                _tmp = QFACMemorySystem("_qfac_policy_probe")
                qfac_status = _tmp.get_policy_decision()
            except Exception:
                logger.debug("metrics: policy probe construct failed", exc_info=True)
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
            policy_emitted = True

        # Always attempt a lightweight QFAC metrics snapshot for observability
        try:
            # Try to discover a live instance (heuristic); otherwise temp-construct
            live_inst = None
            for obj in list(globals().values()):  # pragma: no cover - best-effort
                if isinstance(obj, QFACMemorySystem):
                    live_inst = obj
                    break
            if live_inst is None:
                try:
                    live_inst = QFACMemorySystem("_qfac_metrics_probe")
                except Exception:
                    live_inst = None
            if live_inst is not None and hasattr(live_inst, "get_metrics_snapshot"):
                snap = live_inst.get_metrics_snapshot()
                if isinstance(snap, dict) and snap:
                    lines.append(
                        "# HELP aetherra_qfac_nodes_total Total QFAC nodes tracked"
                    )
                    lines.append("# TYPE aetherra_qfac_nodes_total gauge")
                    lines.append(
                        f"aetherra_qfac_nodes_total {_num(snap.get('nodes_total', 0))}"
                    )
                    lines.append(
                        "# HELP aetherra_qfac_nodes_compressed Total QFAC nodes currently compressed"
                    )
                    lines.append("# TYPE aetherra_qfac_nodes_compressed gauge")
                    lines.append(
                        f"aetherra_qfac_nodes_compressed {_num(snap.get('nodes_compressed', 0))}"
                    )
                    lines.append(
                        "# HELP aetherra_qfac_degraded_nodes_total Nodes flagged degraded by fidelity analysis"
                    )
                    lines.append("# TYPE aetherra_qfac_degraded_nodes_total gauge")
                    lines.append(
                        f"aetherra_qfac_degraded_nodes_total {_num(snap.get('degraded_nodes_total', 0))}"
                    )
                    lines.append(
                        "# HELP aetherra_qfac_compression_ratio Overall compression ratio (original/comp)"
                    )
                    lines.append("# TYPE aetherra_qfac_compression_ratio gauge")
                    lines.append(
                        f"aetherra_qfac_compression_ratio {_num(snap.get('overall_compression_ratio', 1.0))}"
                    )
                    lines.append(
                        "# HELP aetherra_qfac_compression_ratio_avg Average per-node compression ratio"
                    )
                    lines.append("# TYPE aetherra_qfac_compression_ratio_avg gauge")
                    lines.append(
                        f"aetherra_qfac_compression_ratio_avg {_num(snap.get('compression_ratio_avg', 1.0))}"
                    )
                    snapshot_emitted = True

            # Retrieval parity metrics snapshot (Phase 1 planning)
            if live_inst is not None and hasattr(
                live_inst, "get_retrieval_parity_metrics_snapshot"
            ):
                try:
                    p = live_inst.get_retrieval_parity_metrics_snapshot()
                except Exception:
                    p = None
                if isinstance(p, dict):
                    lines.append(
                        "# HELP aetherra_qfac_retrieval_parity_total Total retrieval comparisons performed for parity"
                    )
                    lines.append("# TYPE aetherra_qfac_retrieval_parity_total counter")
                    lines.append(
                        f"aetherra_qfac_retrieval_parity_total {_num(p.get('total', 0))}"
                    )
                    lines.append(
                        "# HELP aetherra_qfac_retrieval_parity_top1_match_total Retrievals where top-1 matched between base and boosted"
                    )
                    lines.append(
                        "# TYPE aetherra_qfac_retrieval_parity_top1_match_total counter"
                    )
                    lines.append(
                        f"aetherra_qfac_retrieval_parity_top1_match_total {_num(p.get('top1_match', 0))}"
                    )
                    lines.append(
                        "# HELP aetherra_qfac_retrieval_parity_any_rank_mismatch_total Retrievals where any rank order differed"
                    )
                    lines.append(
                        "# TYPE aetherra_qfac_retrieval_parity_any_rank_mismatch_total counter"
                    )
                    lines.append(
                        f"aetherra_qfac_retrieval_parity_any_rank_mismatch_total {_num(p.get('any_rank_mismatch', 0))}"
                    )
                    lines.append(
                        "# HELP aetherra_qfac_retrieval_threshold_dropped_results_total Total results dropped due to retrieval threshold"
                    )
                    lines.append(
                        "# TYPE aetherra_qfac_retrieval_threshold_dropped_results_total counter"
                    )
                    lines.append(
                        f"aetherra_qfac_retrieval_threshold_dropped_results_total {_num(p.get('threshold_dropped', 0))}"
                    )
                    # Parity ratio gauge (top1_match / total)
                    try:
                        total = _num(p.get("total", 0))
                        top1 = _num(p.get("top1_match", 0))
                        ratio = (top1 / total) if total > 0 else 0.0
                    except Exception:
                        ratio = 0.0
                    lines.append(
                        "# HELP aetherra_qfac_retrieval_parity_ratio Ratio of top1 matches to total parity comparisons"
                    )
                    lines.append("# TYPE aetherra_qfac_retrieval_parity_ratio gauge")
                    lines.append(f"aetherra_qfac_retrieval_parity_ratio {ratio}")
                    # Per-k parity ratios (topK_match / total) for K in {3,5,10}
                    # Will be computed after we resolve byk in the following block.
                    # Optional: per-k parity counters (e.g., k=1,3,5,10)
                    try:
                        # Prefer dedicated method if present
                        byk_obj: Any = None
                        if hasattr(live_inst, "get_retrieval_parity_by_k_snapshot"):
                            byk_obj = live_inst.get_retrieval_parity_by_k_snapshot()
                        elif isinstance(p, dict):
                            byk_obj = p.get("parity_by_k")
                        # Normalize keys to ints {1,3,5,10}
                        norm: dict[int, float] = {}
                        if isinstance(byk_obj, dict):
                            for k0, v0 in list(byk_obj.items()):
                                try:
                                    kk_int = int(k0) if not isinstance(k0, int) else k0
                                except Exception:
                                    logger.debug(
                                        "metrics: parity_by_k key normalization failed",
                                        exc_info=True,
                                    )
                                    continue
                                try:
                                    norm[int(kk_int)] = float(v0)
                                except Exception:
                                    logger.debug(
                                        "metrics: parity_by_k value normalization failed",
                                        exc_info=True,
                                    )
                            # HELP/TYPE for per-k counters
                            for kk in (1, 3, 5, 10):
                                lines.append(
                                    f"# HELP aetherra_qfac_retrieval_parity_top{kk}_match_total Retrievals where top-{kk} prefix matched between base and boosted"
                                )
                                lines.append(
                                    f"# TYPE aetherra_qfac_retrieval_parity_top{kk}_match_total counter"
                                )
                            for kk in (1, 3, 5, 10):
                                v = norm.get(kk, 0.0)
                                lines.append(
                                    f"aetherra_qfac_retrieval_parity_top{kk}_match_total {_num(int(v))}"
                                )
                            # Per-k ratios (topK/total)
                            try:
                                byk_total = float(total)
                            except Exception:
                                byk_total = 0.0
                            for kk in (3, 5, 10):
                                num = float(norm.get(kk, 0.0))
                                rk = (num / byk_total) if byk_total > 0 else 0.0
                                lines.append(
                                    f"# HELP aetherra_qfac_retrieval_parity_top{kk}_ratio Ratio of top{kk} prefix matches to total parity comparisons"
                                )
                                lines.append(
                                    f"# TYPE aetherra_qfac_retrieval_parity_top{kk}_ratio gauge"
                                )
                                lines.append(
                                    f"aetherra_qfac_retrieval_parity_top{kk}_ratio {rk}"
                                )
                    except Exception:
                        logger.debug(
                            "metrics: parity_by_k export failed", exc_info=True
                        )
                    parity_emitted = True

            # Retrieval policy config gauges (threshold + parity_enabled)
            if live_inst is not None and hasattr(
                live_inst, "get_retrieval_policy_config_snapshot"
            ):
                try:
                    cfg = live_inst.get_retrieval_policy_config_snapshot()
                except Exception:
                    cfg = None
                if isinstance(cfg, dict):
                    lines.append(
                        "# HELP aetherra_qfac_retrieval_threshold Current retrieval score threshold"
                    )
                    lines.append("# TYPE aetherra_qfac_retrieval_threshold gauge")
                    lines.append(
                        f"aetherra_qfac_retrieval_threshold {_num(cfg.get('threshold', 0.0))}"
                    )
                    lines.append(
                        "# HELP aetherra_qfac_retrieval_parity_enabled Parity counting enabled (1) or disabled (0)"
                    )
                    lines.append("# TYPE aetherra_qfac_retrieval_parity_enabled gauge")
                    lines.append(
                        f"aetherra_qfac_retrieval_parity_enabled {_num(cfg.get('parity_enabled', 0))}"
                    )
        except Exception:
            logger.debug("metrics: qfac snapshot probe failed", exc_info=True)
    except Exception:
        logger.debug("metrics: qfac policy block failed", exc_info=True)
    # Emit safe defaults if QFAC is unavailable, to keep schema stable
    if not policy_emitted:
        lines.append(
            "# HELP aetherra_qfac_policy_mode_current Current effective QFAC mode"
        )
        lines.append("# TYPE aetherra_qfac_policy_mode_current gauge")
        lines.append("aetherra_qfac_policy_mode_current 0")
        lines.append(
            "# HELP aetherra_qfac_policy_allowed 1 if desired mode allowed, 0 if downgraded"
        )
        lines.append("# TYPE aetherra_qfac_policy_allowed gauge")
        lines.append("aetherra_qfac_policy_allowed 0")
        lines.append(
            "# HELP aetherra_qfac_policy_info Info series for QFAC policy decision (value=1)"
        )
        lines.append("# TYPE aetherra_qfac_policy_info gauge")
        lines.append('aetherra_qfac_policy_info{key="reason",value="unavailable"} 1')
        lines.append('aetherra_qfac_policy_info{key="policy",value="unknown"} 1')
    if not snapshot_emitted:
        lines.append("# HELP aetherra_qfac_nodes_total Total QFAC nodes tracked")
        lines.append("# TYPE aetherra_qfac_nodes_total gauge")
        lines.append("aetherra_qfac_nodes_total 0")
        lines.append(
            "# HELP aetherra_qfac_nodes_compressed Total QFAC nodes currently compressed"
        )
        lines.append("# TYPE aetherra_qfac_nodes_compressed gauge")
        lines.append("aetherra_qfac_nodes_compressed 0")
        lines.append(
            "# HELP aetherra_qfac_degraded_nodes_total Nodes flagged degraded by fidelity analysis"
        )
        lines.append("# TYPE aetherra_qfac_degraded_nodes_total gauge")
        lines.append("aetherra_qfac_degraded_nodes_total 0")
        lines.append(
            "# HELP aetherra_qfac_compression_ratio Overall compression ratio (original/comp)"
        )
        lines.append("# TYPE aetherra_qfac_compression_ratio gauge")
        lines.append("aetherra_qfac_compression_ratio 1")
        lines.append(
            "# HELP aetherra_qfac_compression_ratio_avg Average per-node compression ratio"
        )
        lines.append("# TYPE aetherra_qfac_compression_ratio_avg gauge")
        lines.append("aetherra_qfac_compression_ratio_avg 1")
    # Retrieval parity/threshold metrics schema (emit zeros for discoverability if not available)
    if not parity_emitted:
        lines.append(
            "# HELP aetherra_qfac_retrieval_parity_total Total retrieval comparisons performed for parity"
        )
        lines.append("# TYPE aetherra_qfac_retrieval_parity_total counter")
        lines.append("aetherra_qfac_retrieval_parity_total 0")
        lines.append(
            "# HELP aetherra_qfac_retrieval_parity_top1_match_total Retrievals where top-1 matched between base and boosted"
        )
        lines.append("# TYPE aetherra_qfac_retrieval_parity_top1_match_total counter")
        lines.append("aetherra_qfac_retrieval_parity_top1_match_total 0")
        lines.append(
            "# HELP aetherra_qfac_retrieval_parity_any_rank_mismatch_total Retrievals where any rank order differed"
        )
        lines.append(
            "# TYPE aetherra_qfac_retrieval_parity_any_rank_mismatch_total counter"
        )
        lines.append("aetherra_qfac_retrieval_parity_any_rank_mismatch_total 0")
        lines.append(
            "# HELP aetherra_qfac_retrieval_threshold_dropped_results_total Total results dropped due to retrieval threshold"
        )
        lines.append(
            "# TYPE aetherra_qfac_retrieval_threshold_dropped_results_total counter"
        )
        lines.append("aetherra_qfac_retrieval_threshold_dropped_results_total 0")
        # Parity ratio gauge schema default
        lines.append(
            "# HELP aetherra_qfac_retrieval_parity_ratio Ratio of top1 matches to total parity comparisons"
        )
        lines.append("# TYPE aetherra_qfac_retrieval_parity_ratio gauge")
        lines.append("aetherra_qfac_retrieval_parity_ratio 0")
        # Per-k counters default (discoverability) with HELP/TYPE
        for kk in (1, 3, 5, 10):
            lines.append(
                f"# HELP aetherra_qfac_retrieval_parity_top{kk}_match_total Retrievals where top-{kk} prefix matched between base and boosted"
            )
            lines.append(
                f"# TYPE aetherra_qfac_retrieval_parity_top{kk}_match_total counter"
            )
        for kk in (1, 3, 5, 10):
            lines.append(f"aetherra_qfac_retrieval_parity_top{kk}_match_total 0")
        # Per-k ratio gauges defaults (discoverability)
        for kk in (3, 5, 10):
            lines.append(
                f"# HELP aetherra_qfac_retrieval_parity_top{kk}_ratio Ratio of top{kk} prefix matches to total parity comparisons"
            )
            lines.append(f"# TYPE aetherra_qfac_retrieval_parity_top{kk}_ratio gauge")
            lines.append(f"aetherra_qfac_retrieval_parity_top{kk}_ratio 0")
    # Retrieval policy gauges (always emit for stable schema)
    lines.append(
        "# HELP aetherra_qfac_retrieval_threshold Current retrieval score threshold"
    )
    lines.append("# TYPE aetherra_qfac_retrieval_threshold gauge")
    try:
        lines.append(
            f"aetherra_qfac_retrieval_threshold {_num(os.getenv('AETHERRA_QFAC_RETRIEVAL_THRESHOLD', 0.0))}"
        )
    except Exception:
        lines.append("aetherra_qfac_retrieval_threshold 0")
    lines.append(
        "# HELP aetherra_qfac_retrieval_parity_enabled Parity counting enabled (1) or disabled (0)"
    )
    lines.append("# TYPE aetherra_qfac_retrieval_parity_enabled gauge")
    lines.append(
        f"aetherra_qfac_retrieval_parity_enabled {1 if (os.getenv('AETHERRA_QFAC_RETRIEVAL_PARITY', '1') not in ('0', 'false', 'False')) else 0}"
    )
    ma = registry_client.get_memory_audit() or {}
    if isinstance(ma.get("audit"), dict):
        audit = ma.get("audit") or {}
        nodes_count = _safe_len(audit.get("nodes"))
        if nodes_count > 0:
            lines.append(f"aetherra_memory_branch_nodes_total {_num(nodes_count)}")
        edges_count = _safe_len(audit.get("edges"))
        if edges_count > 0:
            lines.append(f"aetherra_memory_branch_edges_total {_num(edges_count)}")

    # Trainer metrics
    lines.extend(_trainer_metrics_lines())

    # Engine metrics (message/recall latency, STORM canary)
    try:
        from Aetherra.aetherra_core.engine.aetherra_engine import (
            aetherra_engine,  # type: ignore
        )

        eng_snap = aetherra_engine.get_engine_metrics_snapshot()
        if eng_snap:
            # Message latency histogram + aggregates
            lines.append(
                "# HELP aetherra_engine_message_latency_ms_sum Cumulative message processing latency (ms)"
            )
            lines.append("# TYPE aetherra_engine_message_latency_ms_sum counter")
            lines.append(
                f"aetherra_engine_message_latency_ms_sum {_num(eng_snap.get('message_latency_sum_ms', 0))}"
            )
            lines.append(
                "# HELP aetherra_engine_message_latency_count Number of message latency observations"
            )
            lines.append("# TYPE aetherra_engine_message_latency_count counter")
            lines.append(
                f"aetherra_engine_message_latency_count {_num(eng_snap.get('message_latency_count', 0))}"
            )
            lines.append(
                "# HELP aetherra_engine_message_latency_ms_bucket Message latency histogram buckets"
            )
            lines.append("# TYPE aetherra_engine_message_latency_ms_bucket histogram")
            hist = eng_snap.get("message_latency_hist") or {}
            cum = 0
            for b in (50, 100, 250, 500, 1000, 2000, 5000):
                cum += int(hist.get(b, 0))
                lines.append(
                    f'aetherra_engine_message_latency_ms_bucket{{le="{b}"}} {cum}'
                )
            lines.append(
                f'aetherra_engine_message_latency_ms_bucket{{le="+Inf"}} {cum}'
            )
            # Recall latency histogram + aggregates
            lines.append(
                "# HELP aetherra_engine_recall_latency_ms_sum Cumulative recall latency (ms)"
            )
            lines.append("# TYPE aetherra_engine_recall_latency_ms_sum counter")
            lines.append(
                f"aetherra_engine_recall_latency_ms_sum {_num(eng_snap.get('recall_latency_sum_ms', 0))}"
            )
            lines.append(
                "# HELP aetherra_engine_recall_latency_count Number of recall latency observations"
            )
            lines.append("# TYPE aetherra_engine_recall_latency_count counter")
            lines.append(
                f"aetherra_engine_recall_latency_count {_num(eng_snap.get('recall_latency_count', 0))}"
            )
            lines.append(
                "# HELP aetherra_engine_recall_latency_ms_bucket Recall latency histogram buckets"
            )
            lines.append("# TYPE aetherra_engine_recall_latency_ms_bucket histogram")
            rhist = eng_snap.get("recall_latency_hist") or {}
            rcum = 0
            for b in (10, 20, 50, 100, 200, 500, 1000):
                rcum += int(rhist.get(b, 0))
                lines.append(
                    f'aetherra_engine_recall_latency_ms_bucket{{le="{b}"}} {rcum}'
                )
            lines.append(
                f'aetherra_engine_recall_latency_ms_bucket{{le="+Inf"}} {rcum}'
            )
            # Recall success/failure counters
            lines.append(
                "# HELP aetherra_engine_recall_success_total Total successful recall operations"
            )
            lines.append("# TYPE aetherra_engine_recall_success_total counter")
            lines.append(
                f"aetherra_engine_recall_success_total {_num(eng_snap.get('recall_success_total', 0))}"
            )
            lines.append(
                "# HELP aetherra_engine_recall_failure_total Total failed recall operations"
            )
            lines.append("# TYPE aetherra_engine_recall_failure_total counter")
            lines.append(
                f"aetherra_engine_recall_failure_total {_num(eng_snap.get('recall_failure_total', 0))}"
            )
            # STORM canary metrics
            lines.append(
                "# HELP aetherra_engine_storm_canary_comparisons_total Total shadow recall comparisons"
            )
            lines.append(
                "# TYPE aetherra_engine_storm_canary_comparisons_total counter"
            )
            lines.append(
                f"aetherra_engine_storm_canary_comparisons_total {_num(eng_snap.get('storm_canary_comparisons_total', 0))}"
            )
            lines.append(
                "# HELP aetherra_engine_storm_canary_divergences_total Total divergences detected between recall methods"
            )
            lines.append(
                "# TYPE aetherra_engine_storm_canary_divergences_total counter"
            )
            lines.append(
                f"aetherra_engine_storm_canary_divergences_total {_num(eng_snap.get('storm_canary_divergences_total', 0))}"
            )
            lines.append(
                "# HELP aetherra_engine_storm_canary_shadow_latency_ms_sum Cumulative shadow recall latency (ms)"
            )
            lines.append(
                "# TYPE aetherra_engine_storm_canary_shadow_latency_ms_sum counter"
            )
            lines.append(
                f"aetherra_engine_storm_canary_shadow_latency_ms_sum {_num(eng_snap.get('storm_canary_shadow_latency_sum_ms', 0))}"
            )
            lines.append(
                "# HELP aetherra_engine_storm_canary_shadow_latency_count Number of shadow recall latency observations"
            )
            lines.append(
                "# TYPE aetherra_engine_storm_canary_shadow_latency_count counter"
            )
            lines.append(
                f"aetherra_engine_storm_canary_shadow_latency_count {_num(eng_snap.get('storm_canary_shadow_latency_count', 0))}"
            )
    except Exception:
        logger.debug("metrics: engine metrics export failed", exc_info=True)

    lines.extend(_engine_ab_metrics_lines())

    # Timestamp
    lines.append(
        f"aetherra_hub_export_timestamp_seconds {int(datetime.utcnow().timestamp())}"
    )

    # Plugin metrics appended last
    try:
        # Local imports
        from .plugin_metrics import (
            as_prometheus_lines as plugin_metrics_lines,
        )

        lines.extend(plugin_metrics_lines())
    except Exception:
        logger.debug("metrics: plugin metrics import failed", exc_info=True)
    # Key encryption status (security hardening P1) – best-effort
    try:
        keys_path = os.path.expanduser("~/.aetherra/keys.json")
        enc = 0
        if os.path.exists(keys_path):
            # Standard library imports
            import json as _json  # local import to avoid global cost

            try:
                with open(keys_path, encoding="utf-8") as f:
                    data = _json.load(f)
                if isinstance(data, dict) and data.get("__encrypted__") is True:
                    enc = 1
            except Exception:
                logger.debug("metrics: keys.json read failed", exc_info=True)
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
        logger.debug("metrics: key encryption status export failed", exc_info=True)
    return lines
