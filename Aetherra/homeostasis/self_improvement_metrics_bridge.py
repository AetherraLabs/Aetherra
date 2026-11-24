#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Forward fresh Homeostasis evidence to the existing Self-Improvement engine.

Only explicitly measured fields enter metric history and the read-only
observation/proposal path. The bridge has no approval or execution authority.
"""

# Standard library imports
import asyncio
import contextlib
import logging
import math
import time
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
        self.observations_forwarded = 0
        self.last_forward_error: str | None = None

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
                self.last_forward_error = "registry_unavailable"
                return

            # Get homeostasis system
            homeostasis = registry.get_service("homeostasis_system")
            if not homeostasis:
                self.last_forward_error = "homeostasis_unavailable"
                return

            # Get self-improvement engine
            sie = registry.get_service("self_improvement_engine")
            if not sie:
                self.last_forward_error = "self_improvement_unavailable"
                return

            # Validate source freshness/presence before any metric is re-timestamped
            # by Self-Improvement intake.
            observation = self._collect_observation(homeostasis)
            if observation is None:
                self.last_forward_error = "observation_unavailable"
                return

            metrics_to_forward = await self._collect_homeostasis_metrics(homeostasis)

            if not metrics_to_forward:
                self.last_forward_error = "metrics_unavailable"
                return

            self.last_forward_error = None
            # Forward each metric to self-improvement engine
            for metric_name, metric_data in metrics_to_forward.items():
                try:
                    delivered = await registry.send_message(
                        "self_improvement_engine",
                        "selfimprovement.record_metric",
                        {
                            "name": metric_name,
                            "value": metric_data["value"],
                            "unit": metric_data["unit"],
                            "context": metric_data.get("context", {}),
                        },
                    )
                    if delivered:
                        self.metrics_forwarded += 1
                    else:
                        self.forward_failures += 1
                        self.last_forward_error = "metric_delivery_failed"
                except Exception as e:
                    logger.debug(f"[BRIDGE] Failed to forward {metric_name}: {e}")
                    self.forward_failures += 1
                    self.last_forward_error = "metric_delivery_failed"

            if await registry.send_message(
                "self_improvement_engine",
                "selfimprovement.observe_homeostasis",
                observation,
            ):
                self.observations_forwarded += 1
            else:
                self.forward_failures += 1
                self.last_forward_error = "observation_delivery_failed"

            logger.debug(
                f"[BRIDGE] Forwarded {len(metrics_to_forward)} metrics to self-improvement"
            )

        except Exception as e:
            self.forward_failures += 1
            self.last_forward_error = "forward_failed"
            logger.error("[BRIDGE] Forward metrics failed: %s", type(e).__name__)

    @staticmethod
    def _measured_snapshot(snapshot: Any) -> dict[str, float]:
        """Project only current finite measurements declared by the collector."""
        # Local imports
        from .observation import _OBSERVED_METRICS

        timestamp = getattr(snapshot, "timestamp", None)
        if (
            isinstance(timestamp, bool)
            or not isinstance(timestamp, (int, float))
            or abs(timestamp) > 1e12
            or not math.isfinite(timestamp)
            or not -30.0 <= time.time() - timestamp <= 180.0
        ):
            return {}
        raw = getattr(snapshot, "raw_data", None)
        measured = raw.get("measured_metrics") if isinstance(raw, dict) else None
        if not isinstance(measured, (list, tuple)):
            return {}
        declared = {name for name in measured[:64] if isinstance(name, str)}
        values = {}
        for name in _OBSERVED_METRICS:
            value = getattr(snapshot, name, None)
            if (
                name in declared
                and not isinstance(value, bool)
                and isinstance(value, (int, float))
                and abs(value) <= 1e12
                and math.isfinite(value)
            ):
                values[name] = float(value)
        return {"timestamp": float(timestamp), **values} if values else {}

    @staticmethod
    def _collect_observation(homeostasis) -> dict[str, Any] | None:
        # Local imports
        from .observation import build_observation_report

        orchestrator = getattr(homeostasis, "instance", homeostasis)
        metrics = getattr(orchestrator, "metrics", None)
        if metrics is None:
            return None
        snapshot = SelfImprovementMetricsBridge._measured_snapshot(
            metrics.get_current_snapshot()
        )
        if not snapshot:
            return None
        controller = getattr(orchestrator, "controller", None)
        supervisor = getattr(orchestrator, "supervisor", None)
        return build_observation_report(
            metrics_snapshot=snapshot,
            controller_status=controller.get_controller_status() if controller else {},
            control_loops=controller.get_control_loop_status() if controller else {},
            supervisor_status=supervisor.get_system_health() if supervisor else {},
            setpoints=getattr(controller, "setpoints", None) or metrics.setpoints,
        )

    async def _collect_homeostasis_metrics(
        self, homeostasis
    ) -> Dict[str, Dict[str, Any]]:
        """Collect only present finite facts from direct or wrapped services."""
        metrics: Dict[str, Dict[str, Any]] = {}
        try:
            orchestrator = getattr(homeostasis, "instance", homeostasis)
            collector = getattr(orchestrator, "metrics", None)
            snapshot = self._measured_snapshot(
                collector.get_current_snapshot() if collector else None
            )
            if snapshot:
                for name, unit in (
                    ("plugin_load_success", "percentage"),
                    ("memory_rtt", "milliseconds"),
                    ("task_latency", "milliseconds"),
                    ("hub_connection", "boolean"),
                ):
                    self._add_metric(
                        metrics,
                        name,
                        snapshot.get(name),
                        unit,
                        {"source": "homeostasis"},
                    )

            controller = getattr(orchestrator, "controller", None)
            if controller:
                status = controller.get_controller_status()
                if isinstance(status, dict):
                    running, mode = status.get("running"), status.get("mode")
                    if running is False or (
                        running is True
                        and isinstance(mode, str)
                        and mode
                        in {
                            "observe_only",
                            "advisory",
                            "disabled",
                            "active",
                            "active_limited",
                            "emergency",
                        }
                    ):
                        self._add_metric(
                            metrics,
                            "controller_active",
                            float(
                                running is True
                                and mode in {"active", "active_limited", "emergency"}
                            ),
                            "boolean",
                            {"source": "homeostasis_controller"},
                        )
                    stats = status.get("stats")
                    if isinstance(stats, dict):
                        self._add_metric(
                            metrics,
                            "actions_executed",
                            stats.get("actions_executed"),
                            "count",
                            {"source": "homeostasis_controller"},
                        )

            supervisor = getattr(orchestrator, "supervisor", None)
            if supervisor:
                health = supervisor.get_system_health()
                runlevel = health.get("runlevel") if isinstance(health, dict) else None
                scores = {
                    "ONLINE": 1.0,
                    "DEGRADED": 0.7,
                    "BOOTING": 0.5,
                    "OFFLINE": 0.3,
                    "FAILED": 0.0,
                }
                if isinstance(runlevel, str) and runlevel in scores:
                    self._add_metric(
                        metrics,
                        "system_health_score",
                        scores[runlevel],
                        "score",
                        {"source": "homeostasis_supervisor", "runlevel": runlevel},
                    )

            # Validator summaries include defaults and derived scores without
            # per-score measurement provenance or freshness. Keep them out
            # of measured metric history.

            corrector = getattr(orchestrator, "error_corrector", None)
            if corrector:
                status = corrector.get_status()
                stats = status.get("statistics", {}) if isinstance(status, dict) else {}
                if isinstance(stats, dict):
                    for name in ("errors_detected", "fixes_successful"):
                        self._add_metric(
                            metrics,
                            name,
                            stats.get(name),
                            "count",
                            {"source": "autonomous_error_corrector"},
                        )
                    attempted, successful = (
                        stats.get("fixes_attempted"),
                        stats.get("fixes_successful"),
                    )
                    if (
                        isinstance(attempted, (int, float))
                        and isinstance(successful, (int, float))
                        and attempted > 0
                        and math.isfinite(attempted)
                        and math.isfinite(successful)
                    ):
                        self._add_metric(
                            metrics,
                            "fix_success_rate",
                            successful / attempted,
                            "percentage",
                            {"source": "autonomous_error_corrector"},
                        )
        except Exception as exc:
            logger.warning("[BRIDGE] Metric collection failed (%s)", type(exc).__name__)
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
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or abs(value) > 1e12
            or not math.isfinite(value)
        ):
            return
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
            "observations_forwarded": self.observations_forwarded,
            "last_forward_error": self.last_forward_error,
            "actions_enabled": False,
            "bridge_interval": self.bridge_interval,
            "success_rate": (
                self.metrics_forwarded
                / (self.metrics_forwarded + self.forward_failures)
                if (self.metrics_forwarded + self.forward_failures) > 0
                else 0.0
            ),
        }
