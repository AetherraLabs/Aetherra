# SPDX-License-Identifier: GPL-3.0-or-later
"""STORM metrics stubs (Prometheus-style naming)

These are placeholder stubs for PR-1. Actual Prometheus integration
will be wired in a subsequent PR with real histogram/counter/gauge exports.
"""

from __future__ import annotations

from typing import Dict


class StormMetrics:
    """Minimal metrics collector for STORM operations.

    Tracks counters and gauges per plan; exports to be wired to
    Prometheus in future PR.
    """

    def __init__(self) -> None:
        # Counters
        self.approximate_recalls_total: int = 0
        self.maintenance_total: int = 0
        self.branch_barycenters_total: int = 0
        self.shadow_comparisons_total: int = 0
        self.shadow_divergences_total: int = 0
        self.shadow_errors_total: int = 0

        # Gauges (last value)
        self.ot_cost_avg: float = 0.0
        self.sheaf_inconsistency: float = 0.0
        self.tt_rank: int = 0
        self.recall_latency_ms_p95: float = 0.0
        self.shadow_agreement_rate: float = 1.0  # % of time STORM agrees with baseline
        self.shadow_latency_ms_avg: float = 0.0  # Shadow recall latency

        # Labeled gauge (action -> timestamp)
        self.maintenance_last: Dict[str, float] = {}

    def record_approximate_recall(self) -> None:
        """Increment approximate_recalls_total counter."""
        self.approximate_recalls_total += 1

    def record_ot_cost(self, cost: float) -> None:
        """Update OT cost gauge (would be avg in real impl)."""
        self.ot_cost_avg = cost

    def record_sheaf_inconsistency(self, inconsistency: float) -> None:
        """Update sheaf inconsistency gauge."""
        self.sheaf_inconsistency = inconsistency

    def record_tt_rank(self, rank: int) -> None:
        """Update TT rank gauge."""
        self.tt_rank = rank

    def record_recall_latency_p95(self, latency_ms: float) -> None:
        """Update p95 recall latency gauge."""
        self.recall_latency_ms_p95 = latency_ms

    def record_maintenance(self, action: str, timestamp: float) -> None:
        """Update maintenance counters and last timestamp."""
        self.maintenance_total += 1
        self.maintenance_last[action] = timestamp

    def record_branch_barycenter(self) -> None:
        """Increment branch barycenters total."""
        self.branch_barycenters_total += 1

    def record_shadow_comparison(self, agreed: bool, latency_ms: float) -> None:
        """Record a shadow mode comparison."""
        self.shadow_comparisons_total += 1
        if not agreed:
            self.shadow_divergences_total += 1
        # Update agreement rate (exponential moving average)
        alpha = 0.1
        current_rate = 1.0 if agreed else 0.0
        self.shadow_agreement_rate = alpha * current_rate + (1 - alpha) * self.shadow_agreement_rate
        # Update latency avg
        if self.shadow_comparisons_total == 1:
            self.shadow_latency_ms_avg = latency_ms
        else:
            self.shadow_latency_ms_avg = (
                alpha * latency_ms + (1 - alpha) * self.shadow_latency_ms_avg
            )

    def record_shadow_error(self) -> None:
        """Increment shadow errors (STORM failed but baseline succeeded)."""
        self.shadow_errors_total += 1

    def snapshot(self) -> Dict[str, float | int | Dict[str, float]]:
        """Return current metrics as a dict for status export."""
        return {
            "aetherra_storm_approximate_recalls_total": self.approximate_recalls_total,
            "aetherra_storm_ot_cost_avg": self.ot_cost_avg,
            "aetherra_storm_sheaf_inconsistency": self.sheaf_inconsistency,
            "aetherra_storm_tt_rank": self.tt_rank,
            "aetherra_storm_branch_barycenters_total": self.branch_barycenters_total,
            "aetherra_storm_maintenance_total": self.maintenance_total,
            "aetherra_storm_maintenance_last": dict(self.maintenance_last),
            "aetherra_storm_recall_latency_ms_p95": self.recall_latency_ms_p95,
            "aetherra_storm_shadow_comparisons_total": self.shadow_comparisons_total,
            "aetherra_storm_shadow_divergences_total": self.shadow_divergences_total,
            "aetherra_storm_shadow_errors_total": self.shadow_errors_total,
            "aetherra_storm_shadow_agreement_rate": self.shadow_agreement_rate,
            "aetherra_storm_shadow_latency_ms_avg": self.shadow_latency_ms_avg,
        }


# Singleton instance for PR-1; later we'll inject this via config/registry
_global_metrics = StormMetrics()


def get_metrics() -> StormMetrics:
    """Return global metrics instance."""
    return _global_metrics
