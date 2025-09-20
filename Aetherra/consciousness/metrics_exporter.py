#!/usr/bin/env python3
"""Prometheus Metrics Exporter (Optional)

Exports consciousness-related metrics if AETHERRA_PROMETHEUS=1 is set.
Provides gauges:
  - aetherra_consciousness_narrative_coherence
  - aetherra_consciousness_workspace_queue_size
  - aetherra_consciousness_narrative_chapters_total (counter via gauge increment)

Endpoint listens on port AETHERRA_PROM_PORT (default 9109).
This lightweight module avoids adding the dependency overhead unless enabled.
"""

from __future__ import annotations

# Standard library imports
import os
import threading

try:  # optional dependency
    # Third party imports
    from prometheus_client import (  # type: ignore
        Counter,
        Gauge,
        Histogram,
        start_http_server,
    )
except Exception:  # pragma: no cover
    Gauge = None  # type: ignore
    Counter = None  # type: ignore
    Histogram = None  # type: ignore
    start_http_server = None  # type: ignore

_workspace_queue_gauge = None
_narrative_coherence_gauge = None
_identity_coherence_gauge = None
_narrative_chapters_gauge = None
_workspace_candidate_counter = None
_workspace_broadcast_counter = None
_workspace_latency_hist = None
_narrative_generation_hist = None
_started = False
_lock = threading.Lock()


def initialize_exporter() -> bool:
    """Initialize exporter if enabled; idempotent. Returns True if active."""
    global _started, _workspace_queue_gauge, _narrative_coherence_gauge, _narrative_chapters_gauge, _workspace_candidate_counter, _workspace_broadcast_counter, _workspace_latency_hist, _narrative_generation_hist
    if os.getenv("AETHERRA_PROMETHEUS", "0") != "1":
        return False
    if Gauge is None:
        return False
    with _lock:
        if _started:
            return True
        port = int(os.getenv("AETHERRA_PROM_PORT", "9109"))
        try:
            if start_http_server:
                start_http_server(port)
            else:
                return False
        except Exception:
            return False
        _workspace_queue_gauge = Gauge(
            "aetherra_consciousness_workspace_queue_size",
            "Current workspace candidate queue size",
        )
        _narrative_coherence_gauge = Gauge(
            "aetherra_consciousness_narrative_coherence",
            "Latest narrative coherence index (0-1)",
        )
        _narrative_chapters_gauge = Gauge(
            "aetherra_consciousness_narrative_chapters_total",
            "Total narrative chapters generated (monotonic count)",
        )
        _identity_coherence_gauge = Gauge(
            "aetherra_consciousness_identity_coherence",
            "Proportion of first-person unified identity usage in recent events (0-1)",
        )
        # Counters / Histograms with source label
        if Counter and Histogram:
            try:
                _workspace_candidate_counter = Counter(
                    "aetherra_consciousness_workspace_candidates_total",
                    "Total workspace candidates added",
                    ["source"],
                )
                _workspace_broadcast_counter = Counter(
                    "aetherra_consciousness_workspace_broadcasts_total",
                    "Total workspace broadcasts delivered",
                    ["source"],
                )
                _workspace_latency_hist = Histogram(
                    "aetherra_consciousness_workspace_latency_seconds",
                    "Latency from candidate add to broadcast",
                    buckets=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 1, 2, 5],
                )
                _narrative_generation_hist = Histogram(
                    "aetherra_consciousness_narrative_generation_seconds",
                    "Narrative chapter generation duration",
                    buckets=[0.005, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 1, 2],
                )
            except Exception:
                pass
        _started = True
    return True


def update_workspace_queue(size: int):  # lightweight guard
    if _workspace_queue_gauge is not None:
        try:
            _workspace_queue_gauge.set(size)
        except Exception:
            pass


def update_narrative_coherence(coherence: float):
    if _narrative_coherence_gauge is not None:
        try:
            _narrative_coherence_gauge.set(coherence)
        except Exception:
            pass


def update_identity_coherence(coherence: float):
    if _identity_coherence_gauge is not None:
        try:
            _identity_coherence_gauge.set(coherence)
        except Exception:
            pass


def increment_chapter_count():
    if _narrative_chapters_gauge is not None:
        try:
            # Gauge used as counter (Prom client guarantees thread safety)
            _narrative_chapters_gauge.inc()
        except Exception:
            pass


def inc_workspace_candidate(source: str):
    if _workspace_candidate_counter is not None:
        try:
            _workspace_candidate_counter.labels(source=source or "unknown").inc()
        except Exception:
            pass


def inc_workspace_broadcast(source: str):
    if _workspace_broadcast_counter is not None:
        try:
            _workspace_broadcast_counter.labels(source=source or "unknown").inc()
        except Exception:
            pass


def observe_workspace_latency(seconds: float):
    if _workspace_latency_hist is not None:
        try:
            _workspace_latency_hist.observe(max(0.0, seconds))
        except Exception:
            pass


def observe_narrative_generation(seconds: float):
    if _narrative_generation_hist is not None:
        try:
            _narrative_generation_hist.observe(max(0.0, seconds))
        except Exception:
            pass
