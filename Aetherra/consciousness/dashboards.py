# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Consciousness Dashboards & Telemetry — Phase 3 & 4
==================================================

Lightweight metrics exporters for consciousness features:
- Self-Trust gauges (per subsystem + global)
- Qualia learning parameters
- Semantic Resonance focus attribution
- Phase 4: Continuity metrics (SNCI, snapshot age, dream cycle stats, consolidation)

Designed for integration with Prometheus, Grafana, or internal telemetry systems.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from .autopilot_manager import AutopilotManager
    from .consolidation import Consolidator
    from .continuity_memory import ContinuityMemory
    from .dream_cycle import DreamCycle
    from .explanation_engine import ExplanationEngine
    from .qualia_learning import QualiaLearner
    from .self_trust import SelfTrust


class ConsciousnessDashboard:
    """Telemetry dashboard for Phase 3 & 4 consciousness metrics.

    Exports structured metrics for self-trust, qualia learning,
    semantic resonance attribution, continuity, and dream cycle.
    """

    def __init__(
        self,
        self_trust: Optional[SelfTrust] = None,
        qualia_learner: Optional[QualiaLearner] = None,
        continuity: Optional[ContinuityMemory] = None,
        dream_cycle: Optional[DreamCycle] = None,
        consolidator: Optional[Consolidator] = None,
        explainer: Optional[ExplanationEngine] = None,
        autopilot: Optional[AutopilotManager] = None,
    ):
        """Initialize dashboard.

        Args:
            self_trust: SelfTrust instance to monitor (optional)
            qualia_learner: QualiaLearner instance to monitor (optional)
            continuity: ContinuityMemory instance to monitor (optional)
            dream_cycle: DreamCycle instance to monitor (optional)
            consolidator: Consolidator instance to monitor (optional)
        """
        self.self_trust = self_trust
        self.qualia_learner = qualia_learner
        self.continuity = continuity
        self.dream_cycle = dream_cycle
        self.consolidator = consolidator
        self.focus_attribution_log: List[
            Tuple[str, float, str]
        ] = []  # (event_type, resonance, reason)
        self.explainer = explainer
        self.autopilot = autopilot

    def log_focus_attribution(self, event_type: str, resonance: float, reason: str) -> None:
        """Record why a focus was selected.

        Args:
            event_type: Event type that gained focus
            resonance: Resonance score
            reason: Human-readable reason
        """
        self.focus_attribution_log.append((event_type, resonance, reason))
        # Keep last 1000 entries
        if len(self.focus_attribution_log) > 1000:
            self.focus_attribution_log = self.focus_attribution_log[-1000:]

    def get_self_trust_metrics(self) -> Dict[str, Any]:
        """Export self-trust metrics.

        Returns:
            Dict with global trust, per-subsystem scores, and metadata
        """
        if not self.self_trust:
            return {"available": False}

        status = self.self_trust.get_status()
        # Back-compat aliases: expose 'global_score' in addition to 'global_trust'
        return {
            "available": True,
            "global_trust": status["global_trust"],
            "global_score": status["global_trust"],
            "subsystems": status["subsystems"],
            "tracked_subsystems": status["tracked_count"],
        }

    def get_qualia_learning_metrics(self) -> Dict[str, Any]:
        """Export qualia learning parameters and statistics.

        Returns:
            Dict with learned params, error/success counts
        """
        if not self.qualia_learner:
            return {"available": False}

        stats = self.qualia_learner.get_stats()
        params = stats["params"]
        # Back-compat flatten: surface key params at top-level
        return {
            "available": True,
            "errors_seen": stats["errors_seen"],
            "successes_seen": stats["successes_seen"],
            "parameters": params,
            # Common params exposed flat for legacy tests
            **{
                k: v
                for k, v in params.items()
                if k in ("curiosity_gain", "success_boost", "error_penalty", "certainty_gain")
            },
        }

    def get_focus_attribution(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent focus attribution events.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of dicts with event_type, resonance, reason
        """
        recent = self.focus_attribution_log[-limit:]
        return [
            {"event_type": et, "resonance": res, "reason": reason} for et, res, reason in recent
        ]

    def get_continuity_metrics(self) -> Dict[str, Any]:
        """Export continuity memory metrics.

        Returns:
            Dict with snapshot count, age, SNCI, utilization
        """
        if not self.continuity:
            return {"available": False}

        stats = self.continuity.get_stats()
        return {
            "available": True,
            "snapshots_total": stats["snapshots_total"],
            "age_seconds": stats["age_seconds"],
            "utilization": stats["utilization"],
            "max_capacity": stats["max_capacity"],
        }

    def get_dream_cycle_metrics(self) -> Dict[str, Any]:
        """Export dream cycle statistics.

        Returns:
            Dict with last run timestamp, avg valence, adjustments count
        """
        if not self.dream_cycle:
            return {"available": False}

        stats = self.dream_cycle.get_stats()
        return {
            "available": True,
            "last_run_ts": stats.get("last_run_ts"),
            "avg_valence": stats.get("avg_valence"),
            "avg_certainty": stats.get("avg_certainty"),
            "snapshots_analyzed": stats.get("snapshots_analyzed", 0),
            "adjustments_count": stats.get("adjustments_count", 0),
        }

    def get_consolidation_metrics(self) -> Dict[str, Any]:
        """Export memory consolidation statistics.

        Returns:
            Dict with total pruned, promoted, last run timestamp
        """
        if not self.consolidator:
            return {"available": False}

        stats = self.consolidator.get_stats()
        return {
            "available": True,
            "total_pruned": stats.get("total_pruned", 0),
            "total_promoted": stats.get("total_promoted", 0),
            "last_run_ts": stats.get("last_run_ts"),
        }

    def get_explain_metrics(self) -> Dict[str, Any]:
        """Export explanation coverage/latency metrics."""
        if not self.explainer:
            return {"available": False}
        m = self.explainer.get_metrics()
        return {"available": True, **m}

    def get_autopilot_metrics(self) -> Dict[str, Any]:
        """Export autopilot readiness metrics."""
        if not self.autopilot:
            return {"available": False}
        try:
            stats = self.autopilot.get_stats()
        except Exception:
            return {"available": False}
        return {"available": True, **stats}

    def get_all_metrics(self) -> Dict[str, Any]:
        """Export all Phase 3 & 4 metrics in one call.

        Returns:
            Comprehensive metrics dict for telemetry export
        """
        return {
            "self_trust": self.get_self_trust_metrics(),
            "qualia_learning": self.get_qualia_learning_metrics(),
            "focus_attribution": self.get_focus_attribution(limit=20),
            "continuity": self.get_continuity_metrics(),
            "dream_cycle": self.get_dream_cycle_metrics(),
            "consolidation": self.get_consolidation_metrics(),
            "explain": self.get_explain_metrics(),
            "autopilot": self.get_autopilot_metrics(),
        }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format.

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []

        # Self-trust metrics
        trust_metrics = self.get_self_trust_metrics()
        if trust_metrics.get("available"):
            lines.append("# HELP aetherra_self_trust_global Global self-trust score (0-100)")
            lines.append("# TYPE aetherra_self_trust_global gauge")
            lines.append(f"aetherra_self_trust_global {trust_metrics['global_trust']:.2f}")

            # Back-compat duplicate metric names for older dashboards/tests
            lines.append("# HELP consciousness_self_trust_global Global self-trust score (0-100)")
            lines.append("# TYPE consciousness_self_trust_global gauge")
            lines.append(f"consciousness_self_trust_global {trust_metrics['global_trust']:.2f}")

            for subsystem, score in trust_metrics.get("subsystems", {}).items():
                lines.append(
                    f'aetherra_self_trust_subsystem{{subsystem="{subsystem}"}} {score:.2f}'
                )
                lines.append(
                    f'consciousness_self_trust_subsystem{{subsystem="{subsystem}"}} {score:.2f}'
                )

        # Qualia learning metrics
        ql_metrics = self.get_qualia_learning_metrics()
        if ql_metrics.get("available"):
            lines.append("# HELP aetherra_qualia_errors Total errors observed")
            lines.append("# TYPE aetherra_qualia_errors counter")
            lines.append(f"aetherra_qualia_errors {ql_metrics['errors_seen']}")

            lines.append("# HELP aetherra_qualia_successes Total successes observed")
            lines.append("# TYPE aetherra_qualia_successes counter")
            lines.append(f"aetherra_qualia_successes {ql_metrics['successes_seen']}")

            for param, value in ql_metrics.get("parameters", {}).items():
                lines.append(f'aetherra_qualia_param{{param="{param}"}} {value:.4f}')
                # Back-compat: Also export old consciousness_qualia_<param> format
                lines.append(f"consciousness_qualia_{param} {value:.4f}")

        # Phase 4: Continuity metrics
        continuity_metrics = self.get_continuity_metrics()
        if continuity_metrics.get("available"):
            lines.append("# HELP aetherra_continuity_snapshots Total snapshots in buffer")
            lines.append("# TYPE aetherra_continuity_snapshots gauge")
            lines.append(f"aetherra_continuity_snapshots {continuity_metrics['snapshots_total']}")

            lines.append("# HELP aetherra_continuity_age_seconds Age of latest snapshot")
            lines.append("# TYPE aetherra_continuity_age_seconds gauge")
            age = continuity_metrics.get("age_seconds", float("inf"))
            age_val = age if age != float("inf") else 0
            lines.append(f"aetherra_continuity_age_seconds {age_val:.1f}")

            lines.append("# HELP aetherra_continuity_utilization Buffer utilization (0.0-1.0)")
            lines.append("# TYPE aetherra_continuity_utilization gauge")
            lines.append(f"aetherra_continuity_utilization {continuity_metrics['utilization']:.2f}")

        # Phase 4: Dream cycle metrics
        dream_metrics = self.get_dream_cycle_metrics()
        if dream_metrics.get("available") and dream_metrics.get("last_run_ts"):
            lines.append("# HELP aetherra_dream_last_run_ts Last dream cycle timestamp")
            lines.append("# TYPE aetherra_dream_last_run_ts gauge")
            lines.append(f"aetherra_dream_last_run_ts {dream_metrics['last_run_ts']}")

            if dream_metrics.get("avg_valence") is not None:
                lines.append(
                    "# HELP aetherra_dream_avg_valence Average valence from dream analysis"
                )
                lines.append("# TYPE aetherra_dream_avg_valence gauge")
                lines.append(f"aetherra_dream_avg_valence {dream_metrics['avg_valence']:.2f}")

            lines.append("# HELP aetherra_dream_adjustments Qualia adjustments made in dream")
            lines.append("# TYPE aetherra_dream_adjustments gauge")
            lines.append(f"aetherra_dream_adjustments {dream_metrics['adjustments_count']}")

        # Phase 4: Consolidation metrics
        cons_metrics = self.get_consolidation_metrics()
        if cons_metrics.get("available"):
            lines.append("# HELP aetherra_memory_pruned_total Total memories pruned")
            lines.append("# TYPE aetherra_memory_pruned_total counter")
            lines.append(f"aetherra_memory_pruned_total {cons_metrics['total_pruned']}")

            lines.append("# HELP aetherra_memory_promoted_total Total memories promoted to LT")
            lines.append("# TYPE aetherra_memory_promoted_total counter")
            lines.append(f"aetherra_memory_promoted_total {cons_metrics['total_promoted']}")

        # Phase 5: Explain metrics
        exp_metrics = self.get_explain_metrics()
        if exp_metrics.get("available"):
            lines.append("# HELP aetherra_explain_coverage_ratio Ratio of events with explanations")
            lines.append("# TYPE aetherra_explain_coverage_ratio gauge")
            lines.append(f"aetherra_explain_coverage_ratio {exp_metrics['coverage_ratio']}")

            lines.append("# HELP aetherra_explain_avg_latency_ms Average explanation latency (ms)")
            lines.append("# TYPE aetherra_explain_avg_latency_ms gauge")
            lines.append(f"aetherra_explain_avg_latency_ms {exp_metrics['avg_latency_ms']}")

        # Phase 5: Autopilot metrics
        ap_metrics = self.get_autopilot_metrics()
        if ap_metrics.get("available"):
            lines.append(
                "# HELP aetherra_autopilot_recent_success_ratio Success ratio of recent actions"
            )
            lines.append("# TYPE aetherra_autopilot_recent_success_ratio gauge")
            lines.append(
                f"aetherra_autopilot_recent_success_ratio {ap_metrics['recent_success_ratio']}"
            )

            lines.append(
                "# HELP aetherra_autopilot_recent_actions Count of recent actions considered"
            )
            lines.append("# TYPE aetherra_autopilot_recent_actions gauge")
            lines.append(f"aetherra_autopilot_recent_actions {ap_metrics['recent_actions']}")

            lines.append("# HELP aetherra_autopilot_eligible Eligibility for autopilot graduation")
            lines.append("# TYPE aetherra_autopilot_eligible gauge")
            eligible_val = 1 if ap_metrics.get("eligible") else 0
            lines.append(f"aetherra_autopilot_eligible {eligible_val}")

        return "\n".join(lines) + "\n"
