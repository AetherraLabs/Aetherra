"""
Aetherra Introspection Controller
Self-awareness and internal state monitoring system.
"""

import asyncio
import gc
import json
import logging
import sqlite3
import threading
import time
import traceback
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List

import psutil

logger = logging.getLogger(__name__)


class IntrospectionLevel(Enum):
    """Levels of introspection depth"""

    SURFACE = "surface"
    MODERATE = "moderate"
    DEEP = "deep"
    CRITICAL = "critical"


class ComponentState(Enum):
    """Component state categories"""

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class SystemState:
    """Current system state snapshot"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_threads: int
    active_tasks: int
    component_states: Dict[str, ComponentState]
    performance_metrics: Dict[str, float]
    error_count: int
    warning_count: int


@dataclass
class IntrospectionReport:
    """Introspection analysis report"""

    report_id: str
    timestamp: datetime
    level: IntrospectionLevel
    system_state: SystemState
    analysis: Dict[str, Any]
    recommendations: List[str]
    anomalies: List[Dict[str, Any]]
    health_score: float


class ComponentMonitor:
    """Monitors individual system components"""

    def __init__(self):
        self.components: Dict[str, Dict] = {}
        self.monitoring_active = False

    def register_component(
        self, name: str, check_function: Callable, threshold: Dict[str, float]
    ):
        """Register a component for monitoring"""
        self.components[name] = {
            "check_function": check_function,
            "threshold": threshold,
            "last_check": None,
            "state": ComponentState.UNKNOWN,
            "metrics": {},
        }

    async def check_component(self, name: str) -> ComponentState:
        """Check the state of a specific component"""
        if name not in self.components:
            return ComponentState.UNKNOWN

        component = self.components[name]

        try:
            # Execute component check
            if asyncio.iscoroutinefunction(component["check_function"]):
                metrics = await component["check_function"]()
            else:
                metrics = component["check_function"]()

            component["metrics"] = metrics
            component["last_check"] = datetime.now()

            # Evaluate state based on thresholds
            state = self._evaluate_component_state(metrics, component["threshold"])
            component["state"] = state

            return state

        except Exception as e:
            logger.error(f"Error checking component {name}: {e}")
            component["state"] = ComponentState.ERROR
            return ComponentState.ERROR

    def _evaluate_component_state(
        self, metrics: Dict[str, float], thresholds: Dict[str, float]
    ) -> ComponentState:
        """Evaluate component state based on metrics and thresholds"""
        critical_violations = 0
        warning_violations = 0

        for metric_name, value in metrics.items():
            threshold_key = f"{metric_name}_threshold"
            critical_key = f"{metric_name}_critical"

            if critical_key in thresholds and value > thresholds[critical_key]:
                critical_violations += 1
            elif threshold_key in thresholds and value > thresholds[threshold_key]:
                warning_violations += 1

        if critical_violations > 0:
            return ComponentState.CRITICAL
        elif warning_violations > 0:
            return ComponentState.WARNING
        else:
            return ComponentState.HEALTHY


class MemoryAnalyzer:
    """Analyzes memory usage and object lifecycle"""

    def __init__(self):
        self.object_tracking = {}
        self.memory_snapshots = []

    def take_memory_snapshot(self) -> Dict[str, Any]:
        """Take a snapshot of current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()

        # Get garbage collection stats
        gc_stats = gc.get_stats()

        # Count objects by type
        object_counts = {}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            object_counts[obj_type] = object_counts.get(obj_type, 0) + 1

        snapshot = {
            "timestamp": datetime.now(),
            "rss_memory": memory_info.rss,
            "vms_memory": memory_info.vms,
            "memory_percent": process.memory_percent(),
            "gc_stats": gc_stats,
            "object_counts": dict(
                sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            ),
            "gc_collected": gc.collect(),
        }

        self.memory_snapshots.append(snapshot)

        # Keep only recent snapshots
        if len(self.memory_snapshots) > 100:
            self.memory_snapshots = self.memory_snapshots[-100:]

        return snapshot

    def analyze_memory_trends(self) -> Dict[str, Any]:
        """Analyze memory usage trends"""
        if len(self.memory_snapshots) < 2:
            return {"status": "insufficient_data"}

        recent_snapshots = self.memory_snapshots[-10:]

        rss_values = [s["rss_memory"] for s in recent_snapshots]
        memory_percent = [s["memory_percent"] for s in recent_snapshots]

        # Calculate trends
        rss_trend = (rss_values[-1] - rss_values[0]) / len(rss_values)
        percent_trend = (memory_percent[-1] - memory_percent[0]) / len(memory_percent)

        # Identify growing object types
        growing_objects = {}
        if len(recent_snapshots) >= 2:
            first_objects = recent_snapshots[0]["object_counts"]
            last_objects = recent_snapshots[-1]["object_counts"]

            for obj_type in last_objects:
                if obj_type in first_objects:
                    growth = last_objects[obj_type] - first_objects[obj_type]
                    if growth > 100:  # Significant growth
                        growing_objects[obj_type] = growth

        return {
            "rss_trend": rss_trend,
            "percent_trend": percent_trend,
            "current_usage": memory_percent[-1],
            "growing_objects": growing_objects,
            "gc_collections": sum(s["gc_collected"] for s in recent_snapshots),
        }


class PerformanceProfiler:
    """Profiles system performance"""

    def __init__(self):
        self.profiles = {}
        self.active_profiles = {}

    def start_profiling(self, operation_name: str) -> str:
        """Start profiling an operation"""
        profile_id = str(uuid.uuid4())

        self.active_profiles[profile_id] = {
            "operation": operation_name,
            "start_time": time.time(),
            "start_memory": psutil.Process().memory_info().rss,
            "start_cpu": psutil.Process().cpu_percent(),
        }

        return profile_id

    def end_profiling(self, profile_id: str) -> Dict[str, Any]:
        """End profiling and return results"""
        if profile_id not in self.active_profiles:
            return {}

        profile = self.active_profiles[profile_id]
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss

        result = {
            "operation": profile["operation"],
            "duration": end_time - profile["start_time"],
            "memory_delta": end_memory - profile["start_memory"],
            "peak_cpu": psutil.Process().cpu_percent(),
            "timestamp": datetime.now(),
        }

        # Store result
        operation = profile["operation"]
        if operation not in self.profiles:
            self.profiles[operation] = []
        self.profiles[operation].append(result)

        # Clean up
        del self.active_profiles[profile_id]

        return result

    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for an operation"""
        if operation_name not in self.profiles:
            return {}

        profiles = self.profiles[operation_name]
        durations = [p["duration"] for p in profiles]
        memory_deltas = [p["memory_delta"] for p in profiles]

        return {
            "count": len(profiles),
            "avg_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "avg_memory_delta": sum(memory_deltas) / len(memory_deltas),
            "last_run": profiles[-1]["timestamp"],
        }


class AnomalyDetector:
    """Detects anomalies in system behavior"""

    def __init__(self):
        self.baseline_metrics = {}
        self.anomaly_threshold = 2.0  # Standard deviations

    def update_baseline(self, metrics: Dict[str, float]):
        """Update baseline metrics for anomaly detection"""
        for metric, value in metrics.items():
            if metric not in self.baseline_metrics:
                self.baseline_metrics[metric] = {"values": [], "mean": 0, "std": 0}

            baseline = self.baseline_metrics[metric]
            baseline["values"].append(value)

            # Keep only recent values
            if len(baseline["values"]) > 100:
                baseline["values"] = baseline["values"][-100:]

            # Update statistics
            if len(baseline["values"]) > 1:
                baseline["mean"] = sum(baseline["values"]) / len(baseline["values"])
                variance = sum(
                    (x - baseline["mean"]) ** 2 for x in baseline["values"]
                ) / len(baseline["values"])
                baseline["std"] = variance**0.5

    def detect_anomalies(
        self, current_metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in current metrics"""
        anomalies = []

        for metric, value in current_metrics.items():
            if metric in self.baseline_metrics:
                baseline = self.baseline_metrics[metric]

                if baseline["std"] > 0:
                    z_score = abs(value - baseline["mean"]) / baseline["std"]

                    if z_score > self.anomaly_threshold:
                        anomalies.append(
                            {
                                "metric": metric,
                                "current_value": value,
                                "expected_range": [
                                    baseline["mean"] - baseline["std"],
                                    baseline["mean"] + baseline["std"],
                                ],
                                "z_score": z_score,
                                "severity": "high" if z_score > 3.0 else "medium",
                            }
                        )

        return anomalies


class IntrospectionController:
    """
    Advanced introspection controller for system self-awareness
    """

    def __init__(self, db_path: str = "introspection.db"):
        self.db_path = Path(db_path)
        self.component_monitor = ComponentMonitor()
        self.memory_analyzer = MemoryAnalyzer()
        self.performance_profiler = PerformanceProfiler()
        self.anomaly_detector = AnomalyDetector()
        self.introspection_active = False
        self.introspection_task = None
        self.reports: List[IntrospectionReport] = []
        self._init_database()
        self._register_core_components()

    def _init_database(self):
        """Initialize introspection database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS introspection_reports (
                    report_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    system_state TEXT NOT NULL,
                    analysis TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    anomalies TEXT NOT NULL,
                    health_score REAL NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS component_states (
                    component_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    state TEXT NOT NULL,
                    metrics TEXT,
                    PRIMARY KEY (component_name, timestamp)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_profiles (
                    profile_id TEXT PRIMARY KEY,
                    operation_name TEXT NOT NULL,
                    duration REAL NOT NULL,
                    memory_delta INTEGER NOT NULL,
                    peak_cpu REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)

            conn.commit()
        finally:
            conn.close()

    def _register_core_components(self):
        """Register core system components for monitoring"""
        self.component_monitor.register_component(
            "memory",
            self._check_memory_component,
            {
                "usage_threshold": 80.0,
                "usage_critical": 95.0,
                "growth_threshold": 10.0,
                "growth_critical": 25.0,
            },
        )

        self.component_monitor.register_component(
            "cpu",
            self._check_cpu_component,
            {"usage_threshold": 80.0, "usage_critical": 95.0},
        )

        self.component_monitor.register_component(
            "threads",
            self._check_thread_component,
            {"count_threshold": 50, "count_critical": 100},
        )

    async def _check_memory_component(self) -> Dict[str, float]:
        """Check memory component health"""
        snapshot = self.memory_analyzer.take_memory_snapshot()
        trends = self.memory_analyzer.analyze_memory_trends()

        return {
            "usage": snapshot["memory_percent"],
            "rss_mb": snapshot["rss_memory"] / (1024 * 1024),
            "growth_trend": trends.get("percent_trend", 0),
        }

    async def _check_cpu_component(self) -> Dict[str, float]:
        """Check CPU component health"""
        process = psutil.Process()

        # Get CPU usage over short interval
        cpu_percent = process.cpu_percent(interval=0.1)

        return {"usage": cpu_percent, "threads": process.num_threads()}

    async def _check_thread_component(self) -> Dict[str, float]:
        """Check thread component health"""
        thread_count = threading.active_count()

        return {
            "count": float(thread_count),
            "main_thread_alive": float(threading.main_thread().is_alive()),
        }

    async def start_introspection(
        self, level: IntrospectionLevel = IntrospectionLevel.MODERATE
    ):
        """Start introspection monitoring"""
        if self.introspection_active:
            logger.warning("Introspection already active")
            return

        self.introspection_active = True
        self.introspection_task = asyncio.create_task(self._introspection_loop(level))

        logger.info(f"Introspection started at {level.value} level")

    async def stop_introspection(self):
        """Stop introspection monitoring"""
        if not self.introspection_active:
            return

        self.introspection_active = False

        if self.introspection_task:
            self.introspection_task.cancel()
            try:
                await self.introspection_task
            except asyncio.CancelledError:
                pass

        logger.info("Introspection stopped")

    async def _introspection_loop(self, level: IntrospectionLevel):
        """Main introspection loop"""
        try:
            interval = self._get_introspection_interval(level)

            while self.introspection_active:
                await self._perform_introspection(level)
                await asyncio.sleep(interval)

        except asyncio.CancelledError:
            logger.info("Introspection loop cancelled")
        except Exception as e:
            logger.error(f"Introspection loop error: {e}")
            logger.debug(traceback.format_exc())

    def _get_introspection_interval(self, level: IntrospectionLevel) -> int:
        """Get introspection interval based on level"""
        intervals = {
            IntrospectionLevel.SURFACE: 60,  # 1 minute
            IntrospectionLevel.MODERATE: 30,  # 30 seconds
            IntrospectionLevel.DEEP: 15,  # 15 seconds
            IntrospectionLevel.CRITICAL: 5,  # 5 seconds
        }
        return intervals.get(level, 30)

    async def _perform_introspection(self, level: IntrospectionLevel):
        """Perform introspection analysis"""
        try:
            # Collect system state
            system_state = await self._collect_system_state()

            # Perform analysis based on level
            analysis = await self._analyze_system_state(system_state, level)

            # Detect anomalies
            anomalies = self._detect_system_anomalies(system_state)

            # Generate recommendations
            recommendations = self._generate_recommendations(system_state, anomalies)

            # Calculate health score
            health_score = self._calculate_health_score(system_state, anomalies)

            # Create report
            report = IntrospectionReport(
                report_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                level=level,
                system_state=system_state,
                analysis=analysis,
                recommendations=recommendations,
                anomalies=anomalies,
                health_score=health_score,
            )

            self.reports.append(report)

            # Keep only recent reports
            if len(self.reports) > 1000:
                self.reports = self.reports[-1000:]

            # Store report
            await self._store_report(report)

            # Update anomaly detection baseline
            metrics = {
                "cpu_usage": system_state.cpu_usage,
                "memory_usage": system_state.memory_usage,
                "active_threads": float(system_state.active_threads),
                "error_count": float(system_state.error_count),
            }
            self.anomaly_detector.update_baseline(metrics)

            logger.debug(f"Introspection completed - Health: {health_score:.2f}")

        except Exception as e:
            logger.error(f"Error during introspection: {e}")

    async def _collect_system_state(self) -> SystemState:
        """Collect current system state"""
        # Check all components
        component_states = {}
        for component_name in self.component_monitor.components:
            state = await self.component_monitor.check_component(component_name)
            component_states[component_name] = state

        # Get system metrics
        process = psutil.Process()

        # Count errors and warnings from component states
        error_count = len(
            [s for s in component_states.values() if s == ComponentState.ERROR]
        )
        warning_count = len(
            [s for s in component_states.values() if s == ComponentState.WARNING]
        )

        return SystemState(
            timestamp=datetime.now(),
            cpu_usage=process.cpu_percent(),
            memory_usage=process.memory_percent(),
            active_threads=process.num_threads(),
            active_tasks=len(asyncio.all_tasks()),
            component_states=component_states,
            performance_metrics={},
            error_count=error_count,
            warning_count=warning_count,
        )

    async def _analyze_system_state(
        self, state: SystemState, level: IntrospectionLevel
    ) -> Dict[str, Any]:
        """Analyze system state based on introspection level"""
        analysis = {
            "timestamp": state.timestamp.isoformat(),
            "level": level.value,
            "summary": {},
        }

        # Basic analysis for all levels
        analysis["summary"]["overall_health"] = "healthy"
        if state.error_count > 0:
            analysis["summary"]["overall_health"] = "error"
        elif state.warning_count > 0:
            analysis["summary"]["overall_health"] = "warning"

        analysis["summary"]["resource_utilization"] = {
            "cpu": "normal" if state.cpu_usage < 80 else "high",
            "memory": "normal" if state.memory_usage < 80 else "high",
        }

        # Deeper analysis for higher levels
        if level in [IntrospectionLevel.DEEP, IntrospectionLevel.CRITICAL]:
            analysis["memory_analysis"] = self.memory_analyzer.analyze_memory_trends()

        if level == IntrospectionLevel.CRITICAL:
            analysis["performance_profiles"] = {
                op: self.performance_profiler.get_operation_stats(op)
                for op in self.performance_profiler.profiles
            }

        return analysis

    def _detect_system_anomalies(self, state: SystemState) -> List[Dict[str, Any]]:
        """Detect anomalies in system state"""
        metrics = {
            "cpu_usage": state.cpu_usage,
            "memory_usage": state.memory_usage,
            "active_threads": float(state.active_threads),
            "error_count": float(state.error_count),
        }

        return self.anomaly_detector.detect_anomalies(metrics)

    def _generate_recommendations(
        self, state: SystemState, anomalies: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on system state"""
        recommendations = []

        # High resource usage recommendations
        if state.cpu_usage > 90:
            recommendations.append(
                "CPU usage is critically high - consider reducing workload"
            )
        elif state.cpu_usage > 80:
            recommendations.append("CPU usage is high - monitor for performance impact")

        if state.memory_usage > 90:
            recommendations.append(
                "Memory usage is critically high - check for memory leaks"
            )
        elif state.memory_usage > 80:
            recommendations.append("Memory usage is high - consider garbage collection")

        # Thread count recommendations
        if state.active_threads > 100:
            recommendations.append(
                "High thread count detected - review thread management"
            )

        # Error state recommendations
        if state.error_count > 0:
            recommendations.append(
                f"System has {state.error_count} components in error state"
            )

        # Anomaly-based recommendations
        for anomaly in anomalies:
            recommendations.append(
                f"Anomaly detected in {anomaly['metric']}: value {anomaly['current_value']:.2f} "
                f"is outside normal range"
            )

        return recommendations

    def _calculate_health_score(
        self, state: SystemState, anomalies: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall system health score (0-1)"""
        score = 1.0

        # Penalize high resource usage
        if state.cpu_usage > 80:
            score -= (state.cpu_usage - 80) / 100
        if state.memory_usage > 80:
            score -= (state.memory_usage - 80) / 100

        # Penalize errors and warnings
        score -= state.error_count * 0.2
        score -= state.warning_count * 0.1

        # Penalize anomalies
        score -= len(anomalies) * 0.1

        return max(0.0, min(1.0, score))

    def get_current_health(self) -> Dict[str, Any]:
        """Get current system health summary"""
        if not self.reports:
            return {"status": "no_data"}

        latest_report = self.reports[-1]

        return {
            "health_score": latest_report.health_score,
            "timestamp": latest_report.timestamp.isoformat(),
            "anomaly_count": len(latest_report.anomalies),
            "recommendation_count": len(latest_report.recommendations),
            "component_states": {
                name: state.value
                for name, state in latest_report.system_state.component_states.items()
            },
            "resource_usage": {
                "cpu": latest_report.system_state.cpu_usage,
                "memory": latest_report.system_state.memory_usage,
                "threads": latest_report.system_state.active_threads,
            },
        }

    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health score history"""
        cutoff = datetime.now() - timedelta(hours=hours)

        recent_reports = [r for r in self.reports if r.timestamp > cutoff]

        return [
            {
                "timestamp": r.timestamp.isoformat(),
                "health_score": r.health_score,
                "anomaly_count": len(r.anomalies),
                "cpu_usage": r.system_state.cpu_usage,
                "memory_usage": r.system_state.memory_usage,
            }
            for r in recent_reports
        ]

    async def _store_report(self, report: IntrospectionReport):
        """Store introspection report in database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO introspection_reports
                (report_id, timestamp, level, system_state, analysis, recommendations, anomalies, health_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    report.report_id,
                    report.timestamp.isoformat(),
                    report.level.value,
                    json.dumps(
                        {
                            "cpu_usage": report.system_state.cpu_usage,
                            "memory_usage": report.system_state.memory_usage,
                            "active_threads": report.system_state.active_threads,
                            "component_states": {
                                k: v.value
                                for k, v in report.system_state.component_states.items()
                            },
                        }
                    ),
                    json.dumps(report.analysis, default=str),
                    json.dumps(report.recommendations),
                    json.dumps(report.anomalies, default=str),
                    report.health_score,
                ),
            )
            conn.commit()
        finally:
            conn.close()


# Testing function
async def test_introspection_controller():
    """Test the introspection controller"""
    controller = IntrospectionController()

    # Start introspection
    await controller.start_introspection(IntrospectionLevel.MODERATE)

    # Let it run for a bit
    await asyncio.sleep(5)

    # Get current health
    health = controller.get_current_health()
    print("Current Health:")
    print(json.dumps(health, indent=2))

    # Get health history
    history = controller.get_health_history(1)  # Last hour
    print(f"\nHealth History ({len(history)} reports):")
    for h in history[-3:]:  # Show last 3
        print(
            f"  {h['timestamp']}: Health={h['health_score']:.2f}, CPU={h['cpu_usage']:.1f}%"
        )

    # Stop introspection
    await controller.stop_introspection()


if __name__ == "__main__":
    asyncio.run(test_introspection_controller())
