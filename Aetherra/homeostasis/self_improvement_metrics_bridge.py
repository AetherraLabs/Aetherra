#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔄 Self-Improvement Metrics Bridge
===================================

Connects the homeostasis stability metrics system to the self-improvement engine,
ensuring the self-improvement engine has actual data to analyze and act upon.

The Problem:
------------
The self-improvement engine has NO DATA SOURCE. It waits for metrics via
`record_metric()` calls, but nothing in the system actually sends it data.

The Solution:
-------------
This bridge automatically forwards homeostasis metrics to the self-improvement
engine every cycle, giving it real system performance data to analyze.

Author: Aetherra Labs
"""

# Standard library imports
import asyncio
import contextlib
import logging
from typing import Any, Dict, Optional

# Aetherra imports
from aetherra_service_registry import get_service_registry

logger = logging.getLogger(__name__)


class SelfImprovementMetricsBridge:
    """
    Bridges homeostasis metrics to self-improvement engine.

    This ensures the self-improvement engine has actual data to work with
    by automatically forwarding stability metrics from homeostasis.
    """

    def __init__(self):
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.bridge_interval = 60.0  # Forward metrics every minute

        # Statistics
        self.metrics_forwarded = 0
        self.forward_failures = 0

    async def start(self):
        """Start the metrics bridge."""
        if self.running:
            logger.warning("[BRIDGE] Already running")
            return

        self.running = True
        self._task = asyncio.create_task(self._bridge_loop())
        logger.info("🔄 Self-Improvement Metrics Bridge started")

    async def stop(self):
        """Stop the metrics bridge."""
        self.running = False

        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

        logger.info("🔄 Self-Improvement Metrics Bridge stopped")

    async def _bridge_loop(self):
        """Main bridge loop - forwards metrics periodically."""
        try:
            while self.running:
                try:
                    await self._forward_metrics()
                except Exception as e:
                    logger.error(f"[BRIDGE] Metrics forward error: {e}")
                    self.forward_failures += 1

                await asyncio.sleep(self.bridge_interval)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[BRIDGE] Bridge loop error: {e}")

    async def _forward_metrics(self):
        """Forward current metrics from homeostasis to self-improvement."""
        try:
            registry = await get_service_registry()
            if not registry:
                return

            # Get homeostasis system
            homeostasis = registry.get_service("homeostasis_system")
            if not homeostasis:
                logger.debug("[BRIDGE] Homeostasis not available")
                return

            # Get self-improvement engine
            sie = registry.get_service("self_improvement_engine")
            if not sie:
                logger.debug("[BRIDGE] Self-improvement engine not available")
                return

            # Get current homeostasis metrics
            metrics_to_forward = await self._collect_homeostasis_metrics(homeostasis)

            if not metrics_to_forward:
                logger.debug("[BRIDGE] No metrics to forward")
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
                    logger.debug(f"[BRIDGE] Failed to forward {metric_name}: {e}")
                    self.forward_failures += 1

            logger.debug(
                f"[BRIDGE] Forwarded {len(metrics_to_forward)} metrics to self-improvement"
            )

        except Exception as e:
            logger.error(f"[BRIDGE] Forward metrics error: {e}")

    async def _collect_homeostasis_metrics(self, homeostasis) -> Dict[str, Dict[str, Any]]:
        """Collect current metrics from homeostasis system."""
        metrics: Dict[str, Dict[str, Any]] = {}

        try:
            # Get homeostasis orchestrator instance
            if not hasattr(homeostasis, "instance"):
                return metrics

            orchestrator = homeostasis.instance

            # Collect from stability metrics
            if hasattr(orchestrator, "metrics") and orchestrator.metrics:
                snapshot = orchestrator.metrics.get_current_snapshot()
                if snapshot:
                    # Forward key stability metrics
                    self._add_metric(
                        metrics,
                        "plugin_load_success",
                        getattr(snapshot, "plugin_load_success", 0.0),
                        "percentage",
                        {"source": "homeostasis"},
                    )
                    self._add_metric(
                        metrics,
                        "memory_rtt",
                        getattr(snapshot, "memory_rtt", 0.0),
                        "milliseconds",
                        {"source": "homeostasis"},
                    )
                    self._add_metric(
                        metrics,
                        "task_latency",
                        getattr(snapshot, "task_latency", 0.0),
                        "milliseconds",
                        {"source": "homeostasis"},
                    )
                    self._add_metric(
                        metrics,
                        "hub_connection",
                        getattr(snapshot, "hub_connection", 0.0),
                        "boolean",
                        {"source": "homeostasis"},
                    )

            # Collect from controller status
            if hasattr(orchestrator, "controller") and orchestrator.controller:
                controller_status = orchestrator.controller.get_controller_status()
                if controller_status:
                    self._add_metric(
                        metrics,
                        "controller_active",
                        1.0 if controller_status.get("active", False) else 0.0,
                        "boolean",
                        {"source": "homeostasis_controller"},
                    )
                    self._add_metric(
                        metrics,
                        "actions_executed",
                        float(controller_status.get("actions_executed", 0)),
                        "count",
                        {"source": "homeostasis_controller"},
                    )

            # Collect from supervisor
            if hasattr(orchestrator, "supervisor") and orchestrator.supervisor:
                health = orchestrator.supervisor.get_system_health()
                if health:
                    runlevel = health.get("runlevel", "UNKNOWN")
                    # Convert runlevel to numeric score
                    runlevel_scores = {
                        "ONLINE": 1.0,
                        "DEGRADED": 0.7,
                        "BOOTING": 0.5,
                        "OFFLINE": 0.3,
                        "FAILED": 0.0,
                    }
                    self._add_metric(
                        metrics,
                        "system_health_score",
                        runlevel_scores.get(runlevel, 0.5),
                        "score",
                        {"source": "homeostasis_supervisor", "runlevel": runlevel},
                    )

            # Collect from validator (effectiveness metrics)
            if hasattr(orchestrator, "validator") and orchestrator.validator:
                validator_summary = orchestrator.validator.get_validation_summary()
                if validator_summary:
                    effectiveness = validator_summary.get("effectiveness_metrics", {})
                    for metric_name, metric_info in effectiveness.items():
                        if isinstance(metric_info, dict) and "current" in metric_info:
                            self._add_metric(
                                metrics,
                                f"effectiveness_{metric_name}",
                                float(metric_info["current"]),
                                "score",
                                {"source": "homeostasis_validator"},
                            )

            # Collect from error corrector
            if hasattr(orchestrator, "error_corrector") and orchestrator.error_corrector:
                aec_status = orchestrator.error_corrector.get_status()
                if aec_status:
                    stats = aec_status.get("statistics", {})
                    self._add_metric(
                        metrics,
                        "errors_detected",
                        float(stats.get("errors_detected", 0)),
                        "count",
                        {"source": "autonomous_error_corrector"},
                    )
                    self._add_metric(
                        metrics,
                        "fixes_successful",
                        float(stats.get("fixes_successful", 0)),
                        "count",
                        {"source": "autonomous_error_corrector"},
                    )
                    # Calculate fix success rate
                    attempted = stats.get("fixes_attempted", 0)
                    successful = stats.get("fixes_successful", 0)
                    if attempted > 0:
                        success_rate = successful / attempted
                        self._add_metric(
                            metrics,
                            "fix_success_rate",
                            success_rate,
                            "percentage",
                            {"source": "autonomous_error_corrector"},
                        )

        except Exception as e:
            logger.error(f"[BRIDGE] Failed to collect homeostasis metrics: {e}")

        return metrics

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
