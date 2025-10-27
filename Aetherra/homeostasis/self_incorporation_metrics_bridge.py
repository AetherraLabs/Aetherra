#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔄 Self-Incorporation Metrics Bridge (Phase 9)
==============================================

Connects the Self-Incorporation service metrics to the self-improvement engine,
completing the autonomous maintenance triangle:

    Homeostasis (Stability) → Self-Improvement (Intelligence) → Self-Incorporation (Evolution)
                                        ↑___________________________________|

The Problem:
------------
Self-Incorporation generates valuable metrics (files discovered, classified,
integrated, quarantined, night cycles completed, insights) but the self-improvement
engine has no visibility into this data. The autonomous loop is incomplete.

The Solution:
-------------
This Phase 9 bridge automatically forwards Self-Incorporation metrics to the
self-improvement engine every cycle, enabling:
- Learning from integration patterns
- Optimizing discovery and classification strategies
- Adjusting integration velocity based on success rates
- Including Self-Incorporation health in overall system health score

Integration Point:
------------------
This bridge is loaded as Phase 9 in the homeostasis integration orchestrator,
parallel to Phase 8 (Self-Improvement Metrics Bridge).

Author: Aetherra Labs
Created: 2025-10-23
"""

# Standard library imports
import asyncio
import contextlib
import logging
from typing import Any, Dict, Optional

# Aetherra imports
from aetherra_service_registry import get_service_registry

logger = logging.getLogger(__name__)


class SelfIncorporationMetricsBridge:
    """
    Bridges Self-Incorporation metrics to self-improvement engine.

    This completes the autonomous maintenance triangle by giving the
    self-improvement engine visibility into code evolution patterns.

    Metrics Forwarded:
    ------------------
    - files_discovered: Total files found during discovery
    - files_classified: Total files classified by type and intent
    - files_integrated: Total files successfully integrated
    - files_quarantined: Total files quarantined due to trust/security issues
    - night_cycles_completed: Total night learning cycles completed
    - night_cycle_insights: Total insights generated during night cycles
    - discovery_rate: Files discovered per hour
    - integration_success_rate: Successful integrations / total attempts
    - quarantine_rate: Quarantined files / total files processed
    - self_incorporation_health: Overall health score (0.0-1.0)
    """

    def __init__(self):
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.bridge_interval = 60.0  # Forward metrics every minute

        # Statistics
        self.metrics_forwarded = 0
        self.forward_failures = 0

        # Track previous values for rate calculations
        self._prev_metrics: Dict[str, float] = {}
        self._prev_timestamp: Optional[float] = None

    async def start(self):
        """Start the metrics bridge."""
        if self.running:
            logger.warning("[SI-BRIDGE] Already running")
            return

        self.running = True
        self._task = asyncio.create_task(self._bridge_loop())
        logger.info("🔄 Self-Incorporation Metrics Bridge (Phase 9) started")

    async def stop(self):
        """Stop the metrics bridge."""
        self.running = False

        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

        logger.info("🔄 Self-Incorporation Metrics Bridge (Phase 9) stopped")

    async def _bridge_loop(self):
        """Main bridge loop - forwards metrics periodically."""
        try:
            while self.running:
                try:
                    await self._forward_metrics()
                except Exception as e:
                    logger.error(f"[SI-BRIDGE] Metrics forward error: {e}")
                    self.forward_failures += 1

                await asyncio.sleep(self.bridge_interval)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[SI-BRIDGE] Bridge loop error: {e}")

    async def _forward_metrics(self):
        """Forward current metrics from Self-Incorporation to self-improvement."""
        try:
            import time

            registry = await get_service_registry()
            if not registry:
                return

            # Get Self-Incorporation service
            si_service = registry.get_service("self_incorporation")
            if not si_service:
                logger.debug("[SI-BRIDGE] Self-Incorporation not available")
                return

            # Get self-improvement engine
            sie = registry.get_service("self_improvement_engine")
            if not sie:
                logger.debug("[SI-BRIDGE] Self-improvement engine not available")
                return

            # Get current Self-Incorporation metrics
            metrics_to_forward = await self._collect_si_metrics(si_service)

            if not metrics_to_forward:
                logger.debug("[SI-BRIDGE] No metrics to forward")
                return

            # Forward each metric to self-improvement engine
            for metric_name, metric_data in metrics_to_forward.items():
                try:
                    await registry.send_message(
                        "self_improvement_engine",
                        "selfimprovement.record_metric",
                        {
                            "name": metric_name,
                            "value": metric_data["value"],
                            "unit": metric_data["unit"],
                            "context": metric_data.get("context", {}),
                        },
                    )
                    self.metrics_forwarded += 1
                except Exception as e:
                    logger.debug(f"[SI-BRIDGE] Failed to forward {metric_name}: {e}")
                    self.forward_failures += 1

            logger.debug(
                f"[SI-BRIDGE] Forwarded {len(metrics_to_forward)} Self-Incorporation metrics"
            )

            # Update timestamp for rate calculations
            self._prev_timestamp = time.time()

        except Exception as e:
            logger.error(f"[SI-BRIDGE] Forward metrics error: {e}")

    async def _collect_si_metrics(self, si_service) -> Dict[str, Dict[str, Any]]:
        """Collect current metrics from Self-Incorporation service."""
        import time

        metrics: Dict[str, Dict[str, Any]] = {}

        try:
            # Get health/status from Self-Incorporation
            if not hasattr(si_service, "health_check"):
                return metrics

            health = await si_service.health_check()
            if not health:
                return metrics

            # Extract core metrics
            si_metrics = health.get("metrics", {})

            # Core counters
            self._add_metric(
                metrics,
                "si_files_discovered",
                float(si_metrics.get("files_discovered", 0)),
                "count",
                {"source": "self_incorporation"},
            )

            self._add_metric(
                metrics,
                "si_files_classified",
                float(si_metrics.get("files_classified", 0)),
                "count",
                {"source": "self_incorporation"},
            )

            self._add_metric(
                metrics,
                "si_files_integrated",
                float(si_metrics.get("files_integrated", 0)),
                "count",
                {"source": "self_incorporation"},
            )

            self._add_metric(
                metrics,
                "si_files_quarantined",
                float(si_metrics.get("files_quarantined", 0)),
                "count",
                {"source": "self_incorporation"},
            )

            self._add_metric(
                metrics,
                "si_night_cycles_completed",
                float(si_metrics.get("night_cycles_completed", 0)),
                "count",
                {"source": "self_incorporation"},
            )

            self._add_metric(
                metrics,
                "si_night_cycle_insights",
                float(si_metrics.get("night_cycle_insights", 0)),
                "count",
                {"source": "self_incorporation"},
            )

            # Calculate rates (requires previous values)
            current_time = time.time()
            if self._prev_timestamp and self._prev_metrics:
                time_delta = current_time - self._prev_timestamp
                if time_delta > 0:
                    # Discovery rate (files/hour)
                    prev_discovered = self._prev_metrics.get("files_discovered", 0)
                    current_discovered = float(si_metrics.get("files_discovered", 0))
                    discovery_rate = (current_discovered - prev_discovered) / time_delta * 3600
                    self._add_metric(
                        metrics,
                        "si_discovery_rate",
                        discovery_rate,
                        "files_per_hour",
                        {"source": "self_incorporation"},
                    )

            # Integration success rate
            integrated = float(si_metrics.get("files_integrated", 0))
            classified = float(si_metrics.get("files_classified", 0))
            quarantined = float(si_metrics.get("files_quarantined", 0))

            total_processed = integrated + quarantined
            if total_processed > 0:
                integration_success_rate = integrated / total_processed
                self._add_metric(
                    metrics,
                    "si_integration_success_rate",
                    integration_success_rate,
                    "percentage",
                    {"source": "self_incorporation"},
                )

                # Quarantine rate
                quarantine_rate = quarantined / total_processed
                self._add_metric(
                    metrics,
                    "si_quarantine_rate",
                    quarantine_rate,
                    "percentage",
                    {"source": "self_incorporation"},
                )

            # Overall Self-Incorporation health score
            health_score = self._calculate_si_health_score(health, si_metrics)
            self._add_metric(
                metrics,
                "si_health_score",
                health_score,
                "score",
                {
                    "source": "self_incorporation",
                    "status": health.get("status", "unknown"),
                },
            )

            # Store current metrics for next rate calculation
            self._prev_metrics = {
                "files_discovered": float(si_metrics.get("files_discovered", 0)),
                "files_classified": float(si_metrics.get("files_classified", 0)),
                "files_integrated": float(si_metrics.get("files_integrated", 0)),
            }

        except Exception as e:
            logger.error(f"[SI-BRIDGE] Failed to collect SI metrics: {e}")

        return metrics

    def _calculate_si_health_score(
        self, health: Dict[str, Any], si_metrics: Dict[str, Any]
    ) -> float:
        """
        Calculate Self-Incorporation health score (0.0-1.0).

        Factors:
        - Service status (running, enabled)
        - Integration success rate
        - Quarantine rate (lower is better)
        - Active processing (discovery/classification/integration)
        """
        score = 0.0

        # Base: Service running and enabled (40%)
        if health.get("running", False) and health.get("config_enabled", False):
            score += 0.4

        # Integration success rate (30%)
        integrated = float(si_metrics.get("files_integrated", 0))
        quarantined = float(si_metrics.get("files_quarantined", 0))
        total_processed = integrated + quarantined

        if total_processed > 0:
            success_rate = integrated / total_processed
            score += 0.3 * success_rate

        # Active processing (20%)
        # If we're discovering and classifying files, we're healthy
        discovered = float(si_metrics.get("files_discovered", 0))

        if discovered > 0:
            score += 0.1
        if float(si_metrics.get("files_classified", 0)) > 0:
            score += 0.1

        # Night cycle activity (10%)
        night_cycles = float(si_metrics.get("night_cycles_completed", 0))
        if night_cycles > 0:
            score += 0.1

        return min(1.0, score)

    def _add_metric(
        self,
        metrics: Dict[str, Dict[str, Any]],
        name: str,
        value: float,
        unit: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Helper to add a metric to the collection."""
        metrics[name] = {
            "value": value,
            "unit": unit,
            "context": context or {},
        }

    def get_status(self) -> Dict[str, Any]:
        """Get bridge status."""
        return {
            "running": self.running,
            "metrics_forwarded": self.metrics_forwarded,
            "forward_failures": self.forward_failures,
            "bridge_interval": self.bridge_interval,
            "success_rate": (
                self.metrics_forwarded / (self.metrics_forwarded + self.forward_failures)
                if (self.metrics_forwarded + self.forward_failures) > 0
                else 0.0
            ),
        }

    async def get_si_health_contribution(self) -> float:
        """
        Get Self-Incorporation's contribution to overall system health.

        This is called by the homeostasis supervisor to include
        Self-Incorporation health in the overall system health score.

        Returns:
            float: Health score from 0.0 (unhealthy) to 1.0 (healthy)
        """
        try:
            registry = await get_service_registry()
            if not registry:
                return 0.5  # Neutral if no registry

            si_service = registry.get_service("self_incorporation")
            if not si_service:
                return 0.5  # Neutral if SI not available

            health = await si_service.health_check()
            if not health:
                return 0.5

            si_metrics = health.get("metrics", {})
            return self._calculate_si_health_score(health, si_metrics)

        except Exception as e:
            logger.error(f"[SI-BRIDGE] Failed to get SI health contribution: {e}")
            return 0.5  # Neutral on error
