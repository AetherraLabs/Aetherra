"""Plugin metrics accumulation (framework agnostic).

Blueprint updates counters; metrics exporter reads them.
"""

from __future__ import annotations

# Standard library imports
from typing import Dict, List

plugin_metrics: Dict[str, int] = {
    "registrations_total": 0,
    "duplicates_total": 0,
    "validation_errors_total": 0,
    "signature_errors_total": 0,
    "advanced_mode_used_total": 0,
}

# Latency histogram buckets (ms) cumulative counts
_latency_buckets = [5, 10, 25, 50, 100, 250, 500, 1000]
plugin_latency_hist: Dict[int, int] = {b: 0 for b in _latency_buckets}
plugin_latency_inf: int = 0

_METRIC_HELP = {
    "registrations_total": "Total successful plugin registrations",
    "duplicates_total": "Idempotent duplicate registration attempts",
    "validation_errors_total": "Plugin validation failures",
    "signature_errors_total": "Signature / attestation failures",
    "advanced_mode_used_total": "Registrations processed via advanced validation path",
}


def observe_registration_latency(ms: float):  # called by blueprint optionally
    if ms <= 0:
        return
    placed = False
    for b in _latency_buckets:
        if ms <= b:
            plugin_latency_hist[b] = int(plugin_latency_hist.get(b, 0)) + 1
            placed = True
            break
    if not placed:
        global plugin_latency_inf
        plugin_latency_inf += 1


def as_prometheus_lines(prefix: str = "aetherra_plugins") -> List[str]:
    lines: List[str] = []
    for k, v in plugin_metrics.items():
        help_text = _METRIC_HELP.get(k)
        if help_text:
            lines.append(f"# HELP {prefix}_{k} {help_text}")
            lines.append(f"# TYPE {prefix}_{k} counter")
        lines.append(f"{prefix}_{k} {int(v)}")
    # Latency histogram
    cum = 0
    lines.append(
        f"# HELP {prefix}_registration_latency_ms_bucket Plugin registration latency histogram"
    )
    lines.append(f"# TYPE {prefix}_registration_latency_ms_bucket histogram")
    for b in _latency_buckets:
        cum += int(plugin_latency_hist.get(b, 0))
        lines.append(f'{prefix}_registration_latency_ms_bucket{{le="{b}"}} {cum}')
    lines.append(
        f'{prefix}_registration_latency_ms_bucket{{le="+Inf"}} {cum + plugin_latency_inf}'
    )
    return lines


def reset_for_tests():  # pragma: no cover - used in tests optionally
    for k in plugin_metrics:
        plugin_metrics[k] = 0
    for b in _latency_buckets:
        plugin_latency_hist[b] = 0
    global plugin_latency_inf
    plugin_latency_inf = 0
