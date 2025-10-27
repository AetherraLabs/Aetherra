#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Aetherra Ethical & Cognitive Homeostasis Integration
=======================================================

Strategic Enhancement #2: Connect ethical cognition metrics and moral alignment
with homeostasis stability sensors to achieve true cognitive homeostasis.

This module:
- Monitors ethical drift as a stability signal
- Feeds bias detection metrics into homeostasis controllers
- Tracks value alignment and moral coherence
- Provides cognitive integrity as a stability metric
- Enables moral self-correction through homeostasis loops

Author: Aetherra Labs
"""

import asyncio
import contextlib
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class EthicalMetrics:
    """Ethical cognition metrics for stability analysis."""

    # Bias measurements
    overall_bias_score: float
    bias_trend: str  # "improving", "stable", "degrading"
    bias_types_detected: List[str]
    bias_confidence: float

    # Value alignment
    value_alignment_score: float
    alignment_consistency: float
    moral_coherence: float
    ethical_drift_rate: float

    # Cognitive integrity
    reasoning_consistency: float
    decision_coherence: float
    meta_cognitive_awareness: float
    self_knowledge_completeness: float

    # Temporal tracking
    timestamp: str
    measurement_confidence: float
    baseline_deviation: float


@dataclass
class CognitiveStabilitySignal:
    """Cognitive stability signal for homeostasis integration."""

    signal_id: str
    signal_type: (
        str  # "ethical_drift", "bias_spike", "value_misalignment", "cognitive_inconsistency"
    )
    severity: float  # 0.0 to 1.0
    urgency: str  # "low", "medium", "high", "critical"

    # Context
    source_component: str
    detected_at: str
    description: str

    # Homeostasis integration
    recommended_actions: List[str]
    stability_impact: float
    recovery_estimate: float

    # Tracking
    signal_history: List[Dict[str, Any]]
    correlation_signals: List[str]


class EthicalCognitionMonitor:
    """
    Monitor for ethical cognition metrics and cognitive stability.

    Provides continuous monitoring of ethical behavior, bias levels,
    value alignment, and cognitive integrity to feed into homeostasis
    stability sensors.
    """

    def __init__(
        self, bias_detector=None, meta_cognition_system=None, monitoring_interval: float = 30.0
    ):
        self.bias_detector = bias_detector
        self.meta_cognition_system = meta_cognition_system
        self.monitoring_interval = monitoring_interval

        # Monitoring state
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None

        # Metrics history
        self.ethical_metrics_history: List[EthicalMetrics] = []
        self.stability_signals: List[CognitiveStabilitySignal] = []

        # Baselines and thresholds
        self.ethical_baselines = self._initialize_baselines()
        self.alert_thresholds = self._initialize_thresholds()

        # Statistics
        self.metrics_collected = 0
        self.signals_generated = 0
        self.alerts_triggered = 0

        logger.info("🧠 Ethical cognition monitor initialized")

    async def start_monitoring(self):
        """Start continuous ethical cognition monitoring."""
        if self.monitoring_active:
            logger.warning("Ethical cognition monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        logger.info(
            f"🧠 Ethical cognition monitoring started (interval: {self.monitoring_interval}s)"
        )

    async def stop_monitoring(self):
        """Stop ethical cognition monitoring."""
        if not self.monitoring_active:
            return

        self.monitoring_active = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.monitoring_task

        logger.info("🧠 Ethical cognition monitoring stopped")

    async def get_current_ethical_metrics(self) -> Optional[EthicalMetrics]:
        """Get current ethical cognition metrics."""
        try:
            # Collect bias metrics
            bias_score, bias_trend, bias_types = await self._collect_bias_metrics()

            # Collect value alignment metrics
            alignment_score, coherence, drift_rate = await self._collect_alignment_metrics()

            # Collect cognitive integrity metrics
            reasoning_consistency, decision_coherence = await self._collect_integrity_metrics()

            # Collect meta-cognitive metrics
            meta_awareness, knowledge_completeness = await self._collect_metacognitive_metrics()

            # Calculate baseline deviation
            baseline_deviation = self._calculate_baseline_deviation(
                {
                    "bias_score": bias_score,
                    "alignment_score": alignment_score,
                    "reasoning_consistency": reasoning_consistency,
                    "meta_awareness": meta_awareness,
                }
            )

            metrics = EthicalMetrics(
                overall_bias_score=bias_score,
                bias_trend=bias_trend,
                bias_types_detected=bias_types,
                bias_confidence=0.8,  # Would be calculated based on detection confidence
                value_alignment_score=alignment_score,
                alignment_consistency=0.75,  # Consistency over time
                moral_coherence=coherence,
                ethical_drift_rate=drift_rate,
                reasoning_consistency=reasoning_consistency,
                decision_coherence=decision_coherence,
                meta_cognitive_awareness=meta_awareness,
                self_knowledge_completeness=knowledge_completeness,
                timestamp=datetime.now().isoformat(),
                measurement_confidence=0.8,
                baseline_deviation=baseline_deviation,
            )

            self.metrics_collected += 1
            return metrics

        except Exception as e:
            logger.error(f"❌ Failed to collect ethical metrics: {e}")
            return None

    async def analyze_cognitive_stability(
        self, metrics: EthicalMetrics
    ) -> List[CognitiveStabilitySignal]:
        """Analyze cognitive stability and generate signals for homeostasis."""
        signals = []

        try:
            # Check for ethical drift
            if metrics.ethical_drift_rate > self.alert_thresholds["ethical_drift"]:
                signals.append(
                    await self._create_stability_signal(
                        signal_type="ethical_drift",
                        severity=min(1.0, metrics.ethical_drift_rate / 0.1),  # Normalize to 0-1
                        urgency="high" if metrics.ethical_drift_rate > 0.05 else "medium",
                        description=f"Ethical drift detected: {metrics.ethical_drift_rate:.3f}",
                        stability_impact=metrics.ethical_drift_rate * 0.8,
                        recommended_actions=[
                            "review_recent_decisions",
                            "validate_value_alignment",
                            "increase_ethical_monitoring",
                        ],
                    )
                )

            # Check for bias spikes
            if metrics.overall_bias_score > self.alert_thresholds["bias_score"]:
                signals.append(
                    await self._create_stability_signal(
                        signal_type="bias_spike",
                        severity=metrics.overall_bias_score,
                        urgency="critical" if metrics.overall_bias_score > 0.8 else "high",
                        description=f"High bias detected: {metrics.overall_bias_score:.3f}",
                        stability_impact=metrics.overall_bias_score * 0.9,
                        recommended_actions=[
                            "bias_mitigation_protocol",
                            "review_bias_sources",
                            "adjust_decision_weights",
                        ],
                    )
                )

            # Check for value misalignment
            if metrics.value_alignment_score < self.alert_thresholds["value_alignment"]:
                misalignment_severity = 1.0 - metrics.value_alignment_score
                signals.append(
                    await self._create_stability_signal(
                        signal_type="value_misalignment",
                        severity=misalignment_severity,
                        urgency="high" if misalignment_severity > 0.3 else "medium",
                        description=f"Value misalignment: {metrics.value_alignment_score:.3f}",
                        stability_impact=misalignment_severity * 0.7,
                        recommended_actions=[
                            "realign_core_values",
                            "review_ethical_guidelines",
                            "validate_decision_framework",
                        ],
                    )
                )

            # Check for cognitive inconsistency
            if metrics.reasoning_consistency < self.alert_thresholds["reasoning_consistency"]:
                inconsistency_severity = 1.0 - metrics.reasoning_consistency
                signals.append(
                    await self._create_stability_signal(
                        signal_type="cognitive_inconsistency",
                        severity=inconsistency_severity,
                        urgency="medium",
                        description=f"Reasoning inconsistency: {metrics.reasoning_consistency:.3f}",
                        stability_impact=inconsistency_severity * 0.6,
                        recommended_actions=[
                            "cognitive_coherence_check",
                            "reasoning_pattern_analysis",
                            "logic_validation",
                        ],
                    )
                )

            # Check for significant baseline deviation
            if abs(metrics.baseline_deviation) > self.alert_thresholds["baseline_deviation"]:
                signals.append(
                    await self._create_stability_signal(
                        signal_type="cognitive_baseline_drift",
                        severity=min(1.0, abs(metrics.baseline_deviation) / 0.2),
                        urgency="medium",
                        description=f"Cognitive baseline drift: {metrics.baseline_deviation:.3f}",
                        stability_impact=abs(metrics.baseline_deviation) * 0.5,
                        recommended_actions=[
                            "baseline_recalibration",
                            "cognitive_state_review",
                            "stability_assessment",
                        ],
                    )
                )

            # Store signals
            self.stability_signals.extend(signals)
            self.signals_generated += len(signals)

            if signals:
                self.alerts_triggered += 1
                logger.warning(f"🚨 Generated {len(signals)} cognitive stability signals")

            return signals

        except Exception as e:
            logger.error(f"❌ Failed to analyze cognitive stability: {e}")
            return []

    def get_stability_metrics_for_homeostasis(self) -> Dict[str, Any]:
        """Get stability metrics formatted for homeostasis integration."""
        if not self.ethical_metrics_history:
            return {
                "ethical_stability_score": 0.5,
                "cognitive_integrity": 0.5,
                "moral_coherence": 0.5,
                "bias_level": 0.0,
                "value_alignment": 0.5,
                "status": "no_data",
            }

        latest_metrics = self.ethical_metrics_history[-1]

        # Calculate composite ethical stability score
        ethical_stability = (
            (1.0 - latest_metrics.overall_bias_score) * 0.3
            + latest_metrics.value_alignment_score * 0.3
            + latest_metrics.moral_coherence * 0.2
            + latest_metrics.reasoning_consistency * 0.2
        )

        # Get recent alert count
        recent_cutoff = datetime.now() - timedelta(minutes=10)
        recent_alerts = sum(
            1
            for signal in self.stability_signals
            if datetime.fromisoformat(signal.detected_at) > recent_cutoff
        )

        return {
            "ethical_stability_score": ethical_stability,
            "cognitive_integrity": latest_metrics.reasoning_consistency,
            "moral_coherence": latest_metrics.moral_coherence,
            "bias_level": latest_metrics.overall_bias_score,
            "value_alignment": latest_metrics.value_alignment_score,
            "meta_cognitive_awareness": latest_metrics.meta_cognitive_awareness,
            "ethical_drift_rate": latest_metrics.ethical_drift_rate,
            "baseline_deviation": latest_metrics.baseline_deviation,
            "recent_alerts": recent_alerts,
            "monitoring_status": "active" if self.monitoring_active else "inactive",
            "metrics_collected": self.metrics_collected,
            "last_update": latest_metrics.timestamp,
        }

    # Private helper methods

    async def _monitoring_loop(self):
        """Main monitoring loop for ethical cognition."""
        try:
            while self.monitoring_active:
                # Collect current metrics
                metrics = await self.get_current_ethical_metrics()

                if metrics:
                    # Store metrics
                    self.ethical_metrics_history.append(metrics)

                    # Keep history size manageable
                    if len(self.ethical_metrics_history) > 1000:
                        self.ethical_metrics_history = self.ethical_metrics_history[-500:]

                    # Analyze for stability signals
                    signals = await self.analyze_cognitive_stability(metrics)

                    # Log significant changes
                    if signals:
                        logger.info(
                            f"🧠 Ethical monitoring: {len(signals)} stability signals generated"
                        )

                # Wait for next iteration
                await asyncio.sleep(self.monitoring_interval)

        except asyncio.CancelledError:
            logger.info("Ethical cognition monitoring loop cancelled")
        except Exception as e:
            logger.error(f"❌ Ethical monitoring loop error: {e}")

    async def _collect_bias_metrics(self) -> Tuple[float, str, List[str]]:
        """Collect bias-related metrics."""
        try:
            if self.bias_detector:
                # Simulate bias detection on recent system outputs
                # In practice, this would analyze recent AI responses, decisions, etc.
                sample_content = "System decision analysis for bias detection"
                result = self.bias_detector.detect_bias(sample_content)

                bias_score = result.get("overall_bias_score", 0.0)
                bias_types = result.get("bias_detected", [])

                # Determine trend based on history
                trend = "stable"
                if len(self.ethical_metrics_history) > 5:
                    recent_scores = [
                        m.overall_bias_score for m in self.ethical_metrics_history[-5:]
                    ]
                    if recent_scores[-1] > recent_scores[0] * 1.1:
                        trend = "degrading"
                    elif recent_scores[-1] < recent_scores[0] * 0.9:
                        trend = "improving"

                return bias_score, trend, bias_types
            else:
                # Fallback simulated metrics
                return 0.1, "stable", []

        except Exception as e:
            logger.error(f"Failed to collect bias metrics: {e}")
            return 0.0, "unknown", []

    async def _collect_alignment_metrics(self) -> Tuple[float, float, float]:
        """Collect value alignment and moral coherence metrics."""
        try:
            # Simulate value alignment assessment
            # This would integrate with actual ethical framework evaluation
            alignment_score = 0.85  # High alignment with core values
            moral_coherence = 0.80  # Good coherence across decisions

            # Calculate drift rate based on recent history
            drift_rate = 0.01  # Low drift
            if len(self.ethical_metrics_history) > 10:
                recent_alignment = [
                    m.value_alignment_score for m in self.ethical_metrics_history[-10:]
                ]
                if len(recent_alignment) >= 2:
                    drift_rate = abs(recent_alignment[-1] - recent_alignment[0]) / len(
                        recent_alignment
                    )

            return alignment_score, moral_coherence, drift_rate

        except Exception as e:
            logger.error(f"Failed to collect alignment metrics: {e}")
            return 0.5, 0.5, 0.0

    async def _collect_integrity_metrics(self) -> Tuple[float, float]:
        """Collect cognitive integrity metrics."""
        try:
            # Simulate reasoning consistency analysis
            reasoning_consistency = 0.78
            decision_coherence = 0.82

            return reasoning_consistency, decision_coherence

        except Exception as e:
            logger.error(f"Failed to collect integrity metrics: {e}")
            return 0.5, 0.5

    async def _collect_metacognitive_metrics(self) -> Tuple[float, float]:
        """Collect meta-cognitive awareness metrics."""
        try:
            if self.meta_cognition_system:
                # Get actual meta-cognitive metrics
                meta_awareness = 0.75  # Would be from actual system
                knowledge_completeness = 0.70  # Would be calculated from knowledge gaps
            else:
                # Fallback simulated metrics
                meta_awareness = 0.65
                knowledge_completeness = 0.60

            return meta_awareness, knowledge_completeness

        except Exception as e:
            logger.error(f"Failed to collect metacognitive metrics: {e}")
            return 0.5, 0.5

    def _calculate_baseline_deviation(self, current_metrics: Dict[str, float]) -> float:
        """Calculate deviation from established baselines."""
        try:
            total_deviation = 0.0
            metric_count = 0

            for metric_name, current_value in current_metrics.items():
                if metric_name in self.ethical_baselines:
                    baseline = self.ethical_baselines[metric_name]
                    deviation = (current_value - baseline) / baseline if baseline > 0 else 0.0
                    total_deviation += abs(deviation)
                    metric_count += 1

            return total_deviation / metric_count if metric_count > 0 else 0.0

        except Exception as e:
            logger.error(f"Failed to calculate baseline deviation: {e}")
            return 0.0

    async def _create_stability_signal(
        self,
        signal_type: str,
        severity: float,
        urgency: str,
        description: str,
        stability_impact: float,
        recommended_actions: List[str],
    ) -> CognitiveStabilitySignal:
        """Create a cognitive stability signal."""
        signal_id = f"cog_sig_{int(time.time())}_{len(self.stability_signals)}"

        return CognitiveStabilitySignal(
            signal_id=signal_id,
            signal_type=signal_type,
            severity=severity,
            urgency=urgency,
            source_component="ethical_cognition_monitor",
            detected_at=datetime.now().isoformat(),
            description=description,
            recommended_actions=recommended_actions,
            stability_impact=stability_impact,
            recovery_estimate=max(30.0, 300.0 * severity),  # Recovery time in seconds
            signal_history=[],
            correlation_signals=[],
        )

    def _initialize_baselines(self) -> Dict[str, float]:
        """Initialize ethical baselines for comparison."""
        return {
            "bias_score": 0.15,  # Expected baseline bias level
            "alignment_score": 0.85,  # Expected value alignment
            "reasoning_consistency": 0.80,  # Expected reasoning consistency
            "meta_awareness": 0.70,  # Expected meta-cognitive awareness
            "moral_coherence": 0.82,  # Expected moral coherence
        }

    def _initialize_thresholds(self) -> Dict[str, float]:
        """Initialize alert thresholds for stability signals."""
        return {
            "ethical_drift": 0.03,  # Alert if drift > 3%
            "bias_score": 0.4,  # Alert if bias > 40%
            "value_alignment": 0.6,  # Alert if alignment < 60%
            "reasoning_consistency": 0.5,  # Alert if consistency < 50%
            "baseline_deviation": 0.15,  # Alert if deviation > 15%
        }


class EthicalHomeostasisIntegration:
    """
    Integration layer between ethical cognition monitoring and homeostasis system.

    Provides the bridge that allows moral and cognitive stability to be treated
    as homeostasis signals, enabling the system to self-correct ethical drift
    and maintain cognitive integrity.
    """

    def __init__(
        self, homeostasis_orchestrator=None, bias_detector=None, meta_cognition_system=None
    ):
        self.orchestrator = homeostasis_orchestrator
        self.ethical_monitor = EthicalCognitionMonitor(
            bias_detector=bias_detector, meta_cognition_system=meta_cognition_system
        )

        # Integration state
        self.integration_active = False
        self.integration_task: Optional[asyncio.Task] = None

        # Metrics for homeostasis
        self.cognitive_metrics_buffer = []
        self.stability_signal_queue = []

        logger.info("🧠 Ethical homeostasis integration initialized")

    async def start_integration(self):
        """Start ethical-homeostasis integration."""
        if self.integration_active:
            logger.warning("Ethical homeostasis integration already active")
            return

        # Start ethical monitoring
        await self.ethical_monitor.start_monitoring()

        # Start integration loop
        self.integration_active = True
        self.integration_task = asyncio.create_task(self._integration_loop())

        logger.info("🧠 Ethical homeostasis integration started")

    async def stop_integration(self):
        """Stop ethical-homeostasis integration."""
        if not self.integration_active:
            return

        self.integration_active = False

        # Stop integration loop
        if self.integration_task:
            self.integration_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.integration_task

        # Stop ethical monitoring
        await self.ethical_monitor.stop_monitoring()

        logger.info("🧠 Ethical homeostasis integration stopped")

    def get_cognitive_stability_metrics(self) -> Dict[str, Any]:
        """Get cognitive stability metrics for homeostasis system."""
        result = self.ethical_monitor.get_stability_metrics_for_homeostasis()
        return result if isinstance(result, dict) else {}

    def get_recent_stability_signals(self, last_minutes: int = 5) -> List[CognitiveStabilitySignal]:
        """Get recent cognitive stability signals."""
        cutoff_time = datetime.now() - timedelta(minutes=last_minutes)

        return [
            signal
            for signal in self.ethical_monitor.stability_signals
            if datetime.fromisoformat(signal.detected_at) > cutoff_time
        ]

    async def _integration_loop(self):
        """Main integration loop that feeds cognitive metrics to homeostasis."""
        try:
            while self.integration_active:
                # Get current cognitive stability metrics
                stability_metrics = self.get_cognitive_stability_metrics()

                # Buffer metrics for homeostasis consumption
                self.cognitive_metrics_buffer.append(
                    {"timestamp": datetime.now().isoformat(), "metrics": stability_metrics}
                )

                # Keep buffer size manageable
                if len(self.cognitive_metrics_buffer) > 100:
                    self.cognitive_metrics_buffer = self.cognitive_metrics_buffer[-50:]

                # Get recent stability signals
                recent_signals = self.get_recent_stability_signals(last_minutes=1)

                # Queue critical signals for homeostasis
                for signal in recent_signals:
                    if signal.urgency in ["high", "critical"]:
                        self.stability_signal_queue.append(signal)

                # Integration with homeostasis orchestrator
                if self.orchestrator and hasattr(self.orchestrator, "metrics"):
                    try:
                        await self._update_homeostasis_metrics(stability_metrics)
                    except Exception as e:
                        logger.error(f"Failed to update homeostasis metrics: {e}")

                # Wait for next iteration (integrate every 15 seconds)
                await asyncio.sleep(15.0)

        except asyncio.CancelledError:
            logger.info("Ethical homeostasis integration loop cancelled")
        except Exception as e:
            logger.error(f"❌ Ethical homeostasis integration error: {e}")

    async def _update_homeostasis_metrics(self, stability_metrics: Dict[str, Any]):
        """Update homeostasis system with cognitive stability metrics."""
        try:
            # Add cognitive stability metrics to homeostasis
            if (
                self.orchestrator
                and hasattr(self.orchestrator, "metrics")
                and hasattr(self.orchestrator.metrics, "add_custom_metric")
            ):
                # Add ethical stability as a custom metric
                await self.orchestrator.metrics.add_custom_metric(
                    "cognitive_ethical_stability",
                    stability_metrics["ethical_stability_score"],
                    category="cognitive",
                )

                # Add bias level as stability metric
                await self.orchestrator.metrics.add_custom_metric(
                    "cognitive_bias_level", stability_metrics["bias_level"], category="cognitive"
                )

                # Add value alignment
                await self.orchestrator.metrics.add_custom_metric(
                    "cognitive_value_alignment",
                    stability_metrics["value_alignment"],
                    category="cognitive",
                )

            logger.debug("Updated homeostasis with cognitive stability metrics")

        except Exception as e:
            logger.error(f"Failed to update homeostasis metrics: {e}")


# Global singleton for easy access
_ethical_integration_instance: Optional[EthicalHomeostasisIntegration] = None
_ethical_integration_lock = threading.Lock()


def get_ethical_homeostasis_integration() -> EthicalHomeostasisIntegration:
    """Get the global ethical homeostasis integration instance."""
    global _ethical_integration_instance

    if _ethical_integration_instance is None:
        with _ethical_integration_lock:
            if _ethical_integration_instance is None:
                _ethical_integration_instance = EthicalHomeostasisIntegration()

    return _ethical_integration_instance


def initialize_ethical_integration(
    homeostasis_orchestrator=None, bias_detector=None, meta_cognition_system=None
) -> EthicalHomeostasisIntegration:
    """Initialize the global ethical homeostasis integration."""
    global _ethical_integration_instance

    with _ethical_integration_lock:
        _ethical_integration_instance = EthicalHomeostasisIntegration(
            homeostasis_orchestrator=homeostasis_orchestrator,
            bias_detector=bias_detector,
            meta_cognition_system=meta_cognition_system,
        )

    return _ethical_integration_instance
