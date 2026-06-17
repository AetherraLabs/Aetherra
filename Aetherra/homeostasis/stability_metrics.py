#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔍 Aetherra Homeostasis Stability Metrics
==========================================

Collects and aggregates system health signals from existing Aetherra components
for use by the homeostasis control system. Provides a unified interface to
monitor all aspects of system stability.

This module interfaces with:
- Service registry for service health and heartbeats
- Memory system for RTT, timeouts, and error counters
- Plugin system for load success rates and timeouts
- Hub for connectivity and WebSocket status
- Self-improvement engine for cognitive metrics
- Exception handling for suppression counters
- GUI systems for responsiveness metrics

Author: Aetherra Labs
"""

# Standard library imports
import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third party imports
import yaml

# Aetherra imports
from aetherra_service_registry import get_service_registry

from aetherra_hub.services.registry_client import (
    get_hmr_audit_counters,
    get_kernel_status,
    get_memory_audit,
    get_memory_quantum_status,
    get_registry_status,
)

logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """Single point-in-time snapshot of all system metrics."""

    timestamp: float

    # Core System Metrics
    task_throughput: float = 0.0
    task_latency: float = 0.0
    queue_depth: float = 0.0
    memory_rtt: float = 0.0
    memory_timeouts: float = 0.0
    exception_suppression: float = 0.0
    plugin_load_success: float = 100.0
    plugin_timeout_rate: float = 0.0
    hub_connection: float = 0.0
    hub_websocket_status: float = 0.0
    gui_heartbeat: float = 1.0
    gui_responsiveness: float = 100.0

    # Cognitive System Metrics
    learning_rate: float = 0.01
    learning_cycle_time: float = 300.0
    confidence_level: float = 0.8
    uncertainty_level: float = 0.1
    model_fallback_rate: float = 0.0
    reflection_stability: float = 0.9

    # Service Availability Metrics
    registry_health: float = 1.0
    service_count: float = 0.0
    kernel_loop_health: float = 1.0
    os_runlevel: str = "UNKNOWN"

    # Raw data for analysis
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricTrend:
    """Trend analysis for a specific metric over time."""

    metric_name: str
    current_value: float
    average: float
    trend_slope: float  # positive = increasing, negative = decreasing
    variance: float
    min_value: float
    max_value: float
    sample_count: int
    time_window: float  # seconds


class StabilityMetrics:
    """
    Collects and aggregates system health signals for homeostasis control.

    Provides continuous monitoring of system metrics with trend analysis,
    threshold detection, and historical tracking capabilities.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the stability metrics collector."""
        self.config_path = config_path or "Aetherra/homeostasis/configs/setpoints.yaml"
        self.setpoints = self._load_setpoints()

        # Metric storage
        self.current_snapshot: Optional[MetricSnapshot] = None
        self.metric_history: deque = deque(maxlen=1000)  # Keep last 1000 snapshots
        self.metric_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # Error tracking
        self.collection_errors: Dict[str, int] = defaultdict(int)
        self.last_successful_collection: Dict[str, float] = {}

        # Timing
        self.last_collection_time: float = 0.0
        self.collection_interval: float = 10.0  # seconds

        # Cache for expensive operations
        self._service_registry_cache: Optional[Any] = None
        self._cache_expire_time: float = 0.0
        self._cache_duration: float = 30.0  # seconds

        logger.info("🔍 Stability metrics collector initialized")

    def _load_setpoints(self) -> Dict[str, Any]:
        """Load setpoints configuration from YAML file."""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return data if isinstance(data, dict) else {}
            else:
                logger.warning(f"Setpoints config not found at {self.config_path}, using defaults")
                return {}
        except Exception as e:
            logger.error(f"Failed to load setpoints config: {e}")
            return {}

    async def collect_snapshot(self) -> MetricSnapshot:
        """Collect a complete snapshot of all system metrics."""
        timestamp = time.time()
        snapshot = MetricSnapshot(timestamp=timestamp)

        # Collect from all sources in parallel for efficiency
        collection_tasks = [
            self._collect_service_registry_metrics(snapshot),
            self._collect_memory_metrics(snapshot),
            self._collect_plugin_metrics(snapshot),
            self._collect_hub_metrics(snapshot),
            self._collect_cognitive_metrics(snapshot),
            self._collect_gui_metrics(snapshot),
            self._collect_kernel_metrics(snapshot),
        ]

        # Execute all collections, but don't fail if one source is unavailable
        results = await asyncio.gather(*collection_tasks, return_exceptions=True)

        # Log any collection errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                source_name = collection_tasks[i].__name__
                self.collection_errors[source_name] += 1
                if self.collection_errors[source_name] % 10 == 1:  # Log every 10th error
                    logger.warning(f"Error collecting from {source_name}: {result}")

        # Store snapshot
        self.current_snapshot = snapshot
        self.metric_history.append(snapshot)
        self.last_collection_time = timestamp

        # Update metric buffers for trend analysis
        self._update_metric_buffers(snapshot)

        logger.debug(f"📊 Collected metrics snapshot at {datetime.fromtimestamp(timestamp)}")
        return snapshot

    async def _get_service_registry(self) -> Optional[Any]:
        """Get service registry with caching."""
        current_time = time.time()
        if self._service_registry_cache and current_time < self._cache_expire_time:
            return self._service_registry_cache

        try:
            registry = await get_service_registry()
            self._service_registry_cache = registry
            self._cache_expire_time = current_time + self._cache_duration
            return registry
        except Exception as e:
            logger.debug(f"Failed to get service registry: {e}")
            return None

    async def _collect_service_registry_metrics(self, snapshot: MetricSnapshot):
        """Collect metrics from the service registry."""
        try:
            registry_status = get_registry_status()
            if registry_status:
                snapshot.registry_health = (
                    1.0 if registry_status.get("status") == "healthy" else 0.0
                )
                snapshot.service_count = len(registry_status.get("services", {}))
                snapshot.raw_data["service_registry"] = registry_status
                self.last_successful_collection["service_registry"] = time.time()
        except Exception as e:
            logger.debug(f"Service registry metrics collection failed: {e}")
            snapshot.registry_health = 0.0

    async def _collect_memory_metrics(self, snapshot: MetricSnapshot):
        """Collect metrics from the memory system."""
        try:
            # Get memory status from multiple sources
            memory_status = get_memory_quantum_status()
            memory_audit = get_memory_audit()

            if memory_status:
                # Extract RTT and timeout information
                quantum_data = memory_status.get("quantum_data", {})
                snapshot.memory_rtt = quantum_data.get("avg_response_time", 50.0)
                snapshot.memory_timeouts = quantum_data.get("timeout_count", 0.0)
                snapshot.raw_data["memory_quantum"] = memory_status

            if memory_audit:
                # Extract additional memory health information
                snapshot.raw_data["memory_audit"] = memory_audit

            # Phase 2D: Collect memory health and STORM metrics
            await self._collect_memory_health_metrics(snapshot)

            self.last_successful_collection["memory"] = time.time()
        except Exception as e:
            logger.debug(f"Memory metrics collection failed: {e}")

    async def _collect_memory_health_metrics(self, snapshot: MetricSnapshot):
        """
        Collect memory health and STORM metrics (Phase 2D).

        Extracts:
        - Recall latency p95
        - Memory pulse health (coherence_score, contradiction_count, orphaned_fragments)
        - STORM metrics (sheaf_inconsistency, coherence_score, ot_cost_avg, tt_rank)
        - Narrative completeness (if available)
        """
        try:
            # Try to get memory engine instance
            registry = await self._get_service_registry()
            if not registry:
                return

            # Look for memory service
            memory_service = registry.get_service_info("memory_system")
            if not memory_service or not memory_service.instance:
                logger.debug("[HOMEOSTASIS] Memory service not available for health metrics")
                return

            memory_engine = memory_service.instance

            # Collect pulse health metrics
            if hasattr(memory_engine, "get_memory_health"):
                health = memory_engine.get_memory_health()
                if health:
                    snapshot.raw_data["memory_health"] = {
                        "coherence_score": health.get("coherence_score", 0.0),
                        "total_fragments": health.get("total_fragments", 0),
                        "active_concepts": health.get("active_concepts", 0),
                        "average_confidence": health.get("average_confidence", 0.0),
                        "contradiction_count": health.get("contradiction_count", 0),
                        "orphaned_fragments": health.get("orphaned_fragments", 0),
                        "health_trend": health.get("health_trend", "unknown"),
                        "status": health.get("status", "unknown"),
                    }
                    logger.debug(
                        f"[HOMEOSTASIS] Memory pulse health: coherence={health.get('coherence_score', 0.0):.2f}, "
                        f"status={health.get('status', 'unknown')}"
                    )

            # Collect STORM metrics if enabled
            if hasattr(memory_engine, "_storm_engine"):
                storm_engine = memory_engine._storm_engine
                if storm_engine and storm_engine.config.enabled:
                    storm_snapshot = storm_engine.metrics.snapshot()
                    snapshot.raw_data["storm_metrics"] = {
                        "sheaf_inconsistency": storm_snapshot.get(
                            "aetherra_storm_sheaf_inconsistency", 0.0
                        ),
                        "ot_cost_avg": storm_snapshot.get("aetherra_storm_ot_cost_avg", 0.0),
                        "tt_rank": storm_snapshot.get("aetherra_storm_tt_rank", 0),
                        "recall_latency_ms_p95": storm_snapshot.get(
                            "aetherra_storm_recall_latency_ms_p95", 0.0
                        ),
                        "approximate_recalls_total": storm_snapshot.get(
                            "aetherra_storm_approximate_recalls_total", 0
                        ),
                        "maintenance_total": storm_snapshot.get(
                            "aetherra_storm_maintenance_total", 0
                        ),
                        "shadow_comparisons_total": storm_snapshot.get(
                            "aetherra_storm_shadow_comparisons_total", 0
                        ),
                        "shadow_agreement_rate": storm_snapshot.get(
                            "aetherra_storm_shadow_agreement_rate", 1.0
                        ),
                    }
                    # Calculate coherence from sheaf inconsistency
                    sheaf_inc = storm_snapshot.get("aetherra_storm_sheaf_inconsistency", 0.0)
                    storm_coherence = 1.0 / (1.0 + sheaf_inc) if sheaf_inc is not None else 1.0
                    snapshot.raw_data["storm_metrics"]["coherence_score"] = storm_coherence

                    logger.debug(
                        f"[HOMEOSTASIS] STORM metrics: inconsistency={sheaf_inc:.4f}, "
                        f"coherence={storm_coherence:.4f}, ot_cost={storm_snapshot.get('aetherra_storm_ot_cost_avg', 0.0):.4f}"
                    )

            # Collect narrative completeness (if available)
            if hasattr(memory_engine, "generate_narrative") and "last_narrative" in getattr(
                memory_engine, "_narrative_cache", {}
            ):
                # Check for recent narrative generation status (optional and non-blocking)
                narrative_data = memory_engine._narrative_cache.get("last_narrative", {})
                completeness = narrative_data.get("completeness", 1.0)
                snapshot.raw_data["narrative_completeness"] = completeness
                logger.debug(f"[HOMEOSTASIS] Narrative completeness: {completeness:.2f}")

        except Exception as e:
            logger.debug(
                f"[HOMEOSTASIS] Memory health metrics collection failed: {e}", exc_info=True
            )

    async def _collect_plugin_metrics(self, snapshot: MetricSnapshot):
        """Collect metrics from the plugin system."""
        try:
            registry = await self._get_service_registry()
            if registry:
                # Get plugin-related services
                plugin_services = []
                for service_name, service_info in registry.list_services().items():
                    if "plugin" in service_name.lower():
                        plugin_services.append(service_info)

                # Calculate plugin success rate
                if plugin_services:
                    healthy_plugins = sum(1 for s in plugin_services if s.status.value == "HEALTHY")
                    snapshot.plugin_load_success = (healthy_plugins / len(plugin_services)) * 100.0
                else:
                    snapshot.plugin_load_success = 100.0  # No plugins to fail

                snapshot.raw_data["plugin_services"] = len(plugin_services)

            self.last_successful_collection["plugins"] = time.time()
        except Exception as e:
            logger.debug(f"Plugin metrics collection failed: {e}")

    async def _collect_hub_metrics(self, snapshot: MetricSnapshot):
        """Collect metrics from the Hub connectivity."""
        try:
            registry = await self._get_service_registry()
            if registry:
                # Look for Hub-related services
                hub_service = registry.get_service_info("aetherra_hub")
                if hub_service and hub_service.status.value == "HEALTHY":
                    snapshot.hub_connection = 1.0
                    snapshot.hub_websocket_status = 1.0
                else:
                    snapshot.hub_connection = 0.0
                    snapshot.hub_websocket_status = 0.0

                snapshot.raw_data["hub_service"] = (
                    hub_service.status.value if hub_service else "NOT_FOUND"
                )

            self.last_successful_collection["hub"] = time.time()
        except Exception as e:
            logger.debug(f"Hub metrics collection failed: {e}")
            snapshot.hub_connection = 0.0

    async def _collect_cognitive_metrics(self, snapshot: MetricSnapshot):
        """Collect metrics from cognitive/learning systems."""
        try:
            registry = await self._get_service_registry()
            if registry:
                # Look for self-improvement engine or similar cognitive services
                engine_service = registry.get_service_info("aetherra_engine")
                if engine_service and hasattr(engine_service.instance, "get_learning_metrics"):
                    metrics = await engine_service.instance.get_learning_metrics()
                    snapshot.learning_rate = metrics.get("learning_rate", 0.01)
                    snapshot.confidence_level = metrics.get("confidence", 0.8)
                    snapshot.uncertainty_level = metrics.get("uncertainty", 0.1)
                    snapshot.reflection_stability = metrics.get("stability", 0.9)
                    snapshot.raw_data["cognitive_metrics"] = metrics

            self.last_successful_collection["cognitive"] = time.time()
        except Exception as e:
            logger.debug(f"Cognitive metrics collection failed: {e}")

    async def _collect_gui_metrics(self, snapshot: MetricSnapshot):
        """Collect metrics from GUI and user interface systems."""
        try:
            registry = await self._get_service_registry()
            if registry:
                # Look for Lyrixa or GUI services
                gui_services = []
                for name, service in registry.list_services().items():
                    if "lyrixa" in name.lower() or "gui" in name.lower():
                        gui_services.append(service)

                if gui_services:
                    # Calculate average responsiveness
                    healthy_guis = sum(1 for s in gui_services if s.status.value == "HEALTHY")
                    snapshot.gui_heartbeat = 1.0 if healthy_guis > 0 else 10.0
                    snapshot.gui_responsiveness = (
                        100.0 if healthy_guis == len(gui_services) else 500.0
                    )

                snapshot.raw_data["gui_services"] = len(gui_services)

            self.last_successful_collection["gui"] = time.time()
        except Exception as e:
            logger.debug(f"GUI metrics collection failed: {e}")

    async def _collect_kernel_metrics(self, snapshot: MetricSnapshot):
        """Collect metrics from the kernel and OS systems."""
        try:
            kernel_status = get_kernel_status()
            hmr_counters = get_hmr_audit_counters()

            if kernel_status:
                snapshot.kernel_loop_health = (
                    1.0 if kernel_status.get("status") == "healthy" else 0.0
                )
                snapshot.os_runlevel = kernel_status.get("runlevel", "UNKNOWN")
                snapshot.raw_data["kernel_status"] = kernel_status

            if hmr_counters:
                # Extract task throughput and latency from HMR counters
                snapshot.task_throughput = hmr_counters.get("tasks_per_second", 0.0)
                snapshot.task_latency = hmr_counters.get("avg_task_latency_ms", 100.0)
                snapshot.queue_depth = hmr_counters.get("queue_depth", 0.0)
                snapshot.raw_data["hmr_counters"] = hmr_counters

            self.last_successful_collection["kernel"] = time.time()
        except Exception as e:
            logger.debug(f"Kernel metrics collection failed: {e}")

    def _update_metric_buffers(self, snapshot: MetricSnapshot):
        """Update rolling buffers for each metric for trend analysis."""
        timestamp = snapshot.timestamp

        # Update buffers for all numeric metrics
        for field_name, field_value in snapshot.__dict__.items():
            if isinstance(field_value, int | float) and field_name != "timestamp":
                self.metric_buffers[field_name].append((timestamp, field_value))

    def get_metric_trend(
        self, metric_name: str, time_window: float = 300.0
    ) -> Optional[MetricTrend]:
        """Get trend analysis for a specific metric over the specified time window."""
        if metric_name not in self.metric_buffers:
            return None

        buffer = self.metric_buffers[metric_name]
        if len(buffer) < 2:
            return None

        # Filter to time window
        current_time = time.time()
        windowed_data = [(t, v) for t, v in buffer if current_time - t <= time_window]

        if len(windowed_data) < 2:
            return None

        # Extract values and timestamps
        times = [t for t, v in windowed_data]
        values = [v for t, v in windowed_data]

        # Calculate trend metrics
        try:
            current_value = values[-1]
            average = statistics.mean(values)
            variance = statistics.variance(values) if len(values) > 1 else 0.0
            min_value = min(values)
            max_value = max(values)

            # Calculate trend slope (linear regression)
            if len(values) >= 2:
                time_deltas = [t - times[0] for t in times]
                n = len(values)
                sum_x = sum(time_deltas)
                sum_y = sum(values)
                sum_xy = sum(x * y for x, y in zip(time_deltas, values, strict=False))
                sum_x2 = sum(x * x for x in time_deltas)

                if n * sum_x2 - sum_x * sum_x != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                else:
                    slope = 0.0
            else:
                slope = 0.0

            return MetricTrend(
                metric_name=metric_name,
                current_value=current_value,
                average=average,
                trend_slope=slope,
                variance=variance,
                min_value=min_value,
                max_value=max_value,
                sample_count=len(values),
                time_window=time_window,
            )

        except Exception as e:
            logger.debug(f"Error calculating trend for {metric_name}: {e}")
            return None

    def get_metric_deviation(self, metric_name: str) -> Optional[float]:
        """Get current deviation from target setpoint for a metric."""
        if not self.current_snapshot:
            return None

        current_value = getattr(self.current_snapshot, metric_name, None)
        if current_value is None:
            return None

        # Find setpoint in configuration
        setpoint_config = self._find_setpoint_config(metric_name)
        if not setpoint_config:
            return None

        target = setpoint_config.get("target")
        if target is None:
            return None

        # Calculate deviation (current - target)
        return float(current_value) - float(target)

    def _find_setpoint_config(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Find setpoint configuration for a specific metric."""
        # Search through different metric categories
        for category in ["core_metrics", "cognitive_metrics", "service_metrics"]:
            category_config = self.setpoints.get(category, {})
            if metric_name in category_config:
                value = category_config[metric_name]
                if isinstance(value, dict):
                    return value
                else:
                    return None
        return None

    def is_metric_in_bounds(self, metric_name: str) -> Optional[bool]:
        """Check if a metric is within acceptable bounds."""
        if not self.current_snapshot:
            return None

        current_value = getattr(self.current_snapshot, metric_name, None)
        if current_value is None:
            return None

        setpoint_config = self._find_setpoint_config(metric_name)
        if not setpoint_config:
            return None

        # Check various bounds
        min_acceptable = setpoint_config.get("min_acceptable")
        max_acceptable = setpoint_config.get("max_acceptable")

        if min_acceptable is not None and current_value < min_acceptable:
            return False
        return not (max_acceptable is not None and current_value > max_acceptable)

    def get_out_of_bounds_metrics(self) -> List[str]:
        """Get list of metrics currently out of acceptable bounds."""
        out_of_bounds: List[str] = []

        if not self.current_snapshot:
            return out_of_bounds

        # Check all metrics
        for field_name in self.current_snapshot.__dict__:
            if field_name in ["timestamp", "raw_data", "os_runlevel"]:
                continue

            if self.is_metric_in_bounds(field_name) is False:
                out_of_bounds.append(field_name)

        return out_of_bounds

    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        if not self.current_snapshot:
            return {"status": "no_data", "message": "No metrics collected yet"}

        out_of_bounds = self.get_out_of_bounds_metrics()

        # Calculate overall health score
        total_metrics = len(
            [
                f
                for f in self.current_snapshot.__dict__
                if f not in ["timestamp", "raw_data", "os_runlevel"]
            ]
        )
        healthy_metrics = total_metrics - len(out_of_bounds)
        health_score = (healthy_metrics / total_metrics) * 100.0 if total_metrics > 0 else 0.0

        # Determine status
        if health_score >= 95.0:
            status = "healthy"
        elif health_score >= 80.0:
            status = "degraded"
        elif health_score >= 60.0:
            status = "unhealthy"
        else:
            status = "critical"

        return {
            "status": status,
            "health_score": health_score,
            "total_metrics": total_metrics,
            "healthy_metrics": healthy_metrics,
            "out_of_bounds_metrics": out_of_bounds,
            "last_collection": datetime.fromtimestamp(self.last_collection_time).isoformat(),
            "collection_errors": dict(self.collection_errors),
        }

    async def start_continuous_collection(self, interval: Optional[float] = None):
        """Start continuous metric collection in the background."""
        if interval:
            self.collection_interval = interval

        logger.info(f"🔄 Starting continuous metrics collection every {self.collection_interval}s")

        while True:
            try:
                await self.collect_snapshot()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                logger.info("📊 Metrics collection stopped")
                break
            except Exception as e:
                logger.error(f"Error in continuous collection: {e}")
                await asyncio.sleep(self.collection_interval)

    def get_current_snapshot(self) -> Optional[MetricSnapshot]:
        """Get the most recent metrics snapshot."""
        return self.current_snapshot

    def get_latest_snapshot(self) -> Optional[MetricSnapshot]:
        """Compatibility alias for integrations using the previous accessor name."""
        return self.get_current_snapshot()

    def get_historical_snapshots(self, count: int = 100) -> List[MetricSnapshot]:
        """Get recent historical snapshots."""
        return list(self.metric_history)[-count:]


# Global instance for easy access
_stability_metrics: Optional[StabilityMetrics] = None


def get_stability_metrics() -> StabilityMetrics:
    """Get the global stability metrics collector instance."""
    global _stability_metrics
    if _stability_metrics is None:
        _stability_metrics = StabilityMetrics()
    return _stability_metrics


if __name__ == "__main__":
    # Test the metrics collection
    import asyncio

    async def test_metrics():
        metrics = StabilityMetrics()
        snapshot = await metrics.collect_snapshot()
        print(f"Collected snapshot: {snapshot}")
        print(f"Health summary: {metrics.get_health_summary()}")

    asyncio.run(test_metrics())
