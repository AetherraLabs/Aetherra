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
import traceback
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List

try:
    import psutil
except ImportError:
    # Fallback system monitoring
    class psutil:
        class Process:
            def memory_info(self):
                return type("obj", (object,), {"rss": 0, "vms": 0})()

            def memory_percent(self):
                return 0.0

            def cpu_percent(self):
                return 0.0


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
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
        except Exception:
            memory_info = type("obj", (object,), {"rss": 0, "vms": 0})()

        # Get garbage collection stats
        gc_stats = gc.get_stats() if hasattr(gc, "get_stats") else []

        # Count objects by type
        object_counts = {}
        try:
            for obj in gc.get_objects():
                obj_type = type(obj).__name__
                object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
        except Exception:
            pass

        snapshot = {
            "timestamp": datetime.now(),
            "rss_memory": getattr(memory_info, "rss", 0),
            "vms_memory": getattr(memory_info, "vms", 0),
            "memory_percent": 0.0,
            "gc_stats": gc_stats,
            "object_counts": dict(
                sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            )
            if object_counts
            else {},
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
        rss_trend = (
            (rss_values[-1] - rss_values[0]) / len(rss_values)
            if len(rss_values) > 1
            else 0
        )
        percent_trend = (
            (memory_percent[-1] - memory_percent[0]) / len(memory_percent)
            if len(memory_percent) > 1
            else 0
        )

        return {
            "rss_trend": rss_trend,
            "percent_trend": percent_trend,
            "current_rss": rss_values[-1] if rss_values else 0,
            "current_percent": memory_percent[-1] if memory_percent else 0,
        }


class IntrospectionController:
    """
    Advanced introspection system for self-monitoring and analysis
    """

    def __init__(self, db_path: str = "introspection.db"):
        self.db_path = Path(db_path)
        self.component_monitor = ComponentMonitor()
        self.memory_analyzer = MemoryAnalyzer()
        self.introspection_active = False
        self.introspection_task = None
        self.reports: List[IntrospectionReport] = []
        self.analysis_callbacks: List[Callable] = []
        self._init_database()

    def _init_database(self):
        """Initialize introspection database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_usage REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    active_threads INTEGER NOT NULL,
                    active_tasks INTEGER NOT NULL,
                    error_count INTEGER NOT NULL,
                    warning_count INTEGER NOT NULL,
                    health_score REAL NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS introspection_reports (
                    report_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    analysis TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    anomalies TEXT NOT NULL,
                    health_score REAL NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS component_health (
                    component_name TEXT NOT NULL,
                    state TEXT NOT NULL,
                    metrics TEXT,
                    timestamp TEXT NOT NULL,
                    PRIMARY KEY (component_name, timestamp)
                )
            """)

            conn.commit()
        finally:
            conn.close()

    async def start_introspection(self, interval: int = 60):
        """Start continuous introspection monitoring"""
        if self.introspection_active:
            logger.warning("Introspection already active")
            return

        self.introspection_active = True
        self.introspection_task = asyncio.create_task(
            self._introspection_loop(interval)
        )

        logger.info(f"Introspection monitoring started (interval: {interval}s)")

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

        logger.info("Introspection monitoring stopped")

    async def _introspection_loop(self, interval: int):
        """Main introspection monitoring loop"""
        try:
            while self.introspection_active:
                await self._perform_introspection()
                await asyncio.sleep(interval)

        except asyncio.CancelledError:
            logger.info("Introspection loop cancelled")
        except Exception as e:
            logger.error(f"Introspection loop error: {e}")
            logger.debug(traceback.format_exc())

    async def _perform_introspection(self):
        """Perform introspection analysis"""
        try:
            # Collect system state
            system_state = await self._collect_system_state()

            # Generate introspection report
            report = await self._generate_report(
                system_state, IntrospectionLevel.MODERATE
            )

            # Store report
            self.reports.append(report)
            await self._store_report(report)

            # Trigger callbacks
            for callback in self.analysis_callbacks:
                try:
                    await callback(report)
                except Exception as e:
                    logger.error(f"Callback error: {e}")

            logger.debug(
                f"Introspection completed: health_score={report.health_score:.2f}"
            )

        except Exception as e:
            logger.error(f"Introspection error: {e}")

    async def _collect_system_state(self) -> SystemState:
        """Collect current system state"""
        try:
            process = psutil.Process()
            cpu_usage = process.cpu_percent()
            memory_usage = process.memory_percent()
        except Exception:
            cpu_usage = 0.0
            memory_usage = 0.0

        # Get thread count
        active_threads = threading.active_count()

        # Get active tasks (approximation)
        try:
            active_tasks = len([t for t in asyncio.all_tasks() if not t.done()])
        except Exception:
            active_tasks = 0

        # Check component states
        component_states = {}
        for name in self.component_monitor.components:
            state = await self.component_monitor.check_component(name)
            component_states[name] = state

        # Basic performance metrics
        performance_metrics = {
            "response_time": 0.0,  # Would be collected from actual system
            "throughput": 0.0,  # Would be collected from actual system
        }

        # Count errors and warnings
        error_count = sum(
            1 for state in component_states.values() if state == ComponentState.ERROR
        )
        warning_count = sum(
            1 for state in component_states.values() if state == ComponentState.WARNING
        )

        return SystemState(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_threads=active_threads,
            active_tasks=active_tasks,
            component_states=component_states,
            performance_metrics=performance_metrics,
            error_count=error_count,
            warning_count=warning_count,
        )

    async def _generate_report(
        self, system_state: SystemState, level: IntrospectionLevel
    ) -> IntrospectionReport:
        """Generate introspection report"""
        analysis = {}
        recommendations = []
        anomalies = []

        # Analyze CPU usage
        if system_state.cpu_usage > 80:
            analysis["cpu_status"] = "high"
            recommendations.append("Consider optimizing CPU-intensive operations")
            anomalies.append(
                {
                    "type": "high_cpu",
                    "value": system_state.cpu_usage,
                    "threshold": 80,
                }
            )
        else:
            analysis["cpu_status"] = "normal"

        # Analyze memory usage
        if system_state.memory_usage > 85:
            analysis["memory_status"] = "high"
            recommendations.append("Memory usage is high - consider cleanup")
            anomalies.append(
                {
                    "type": "high_memory",
                    "value": system_state.memory_usage,
                    "threshold": 85,
                }
            )
        else:
            analysis["memory_status"] = "normal"

        # Analyze component health
        unhealthy_components = [
            name
            for name, state in system_state.component_states.items()
            if state in [ComponentState.ERROR, ComponentState.CRITICAL]
        ]

        if unhealthy_components:
            analysis["component_health"] = "degraded"
            recommendations.append(
                f"Address issues in components: {', '.join(unhealthy_components)}"
            )

        # Calculate health score
        health_score = self._calculate_health_score(system_state)

        return IntrospectionReport(
            report_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            level=level,
            system_state=system_state,
            analysis=analysis,
            recommendations=recommendations,
            anomalies=anomalies,
            health_score=health_score,
        )

    def _calculate_health_score(self, system_state: SystemState) -> float:
        """Calculate overall system health score"""
        score = 1.0

        # CPU penalty
        if system_state.cpu_usage > 80:
            score -= 0.3
        elif system_state.cpu_usage > 60:
            score -= 0.1

        # Memory penalty
        if system_state.memory_usage > 85:
            score -= 0.3
        elif system_state.memory_usage > 70:
            score -= 0.1

        # Component health penalty
        total_components = len(system_state.component_states)
        if total_components > 0:
            unhealthy_ratio = system_state.error_count / total_components
            score -= unhealthy_ratio * 0.4

        return max(0.0, score)

    async def _store_report(self, report: IntrospectionReport):
        """Store introspection report in database"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Store system state
            conn.execute(
                """
                INSERT INTO system_states
                (timestamp, cpu_usage, memory_usage, active_threads, active_tasks,
                 error_count, warning_count, health_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    report.system_state.timestamp.isoformat(),
                    report.system_state.cpu_usage,
                    report.system_state.memory_usage,
                    report.system_state.active_threads,
                    report.system_state.active_tasks,
                    report.system_state.error_count,
                    report.system_state.warning_count,
                    report.health_score,
                ),
            )

            # Store introspection report
            conn.execute(
                """
                INSERT INTO introspection_reports
                (report_id, timestamp, level, analysis, recommendations, anomalies, health_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    report.report_id,
                    report.timestamp.isoformat(),
                    report.level.value,
                    json.dumps(report.analysis),
                    json.dumps(report.recommendations),
                    json.dumps(report.anomalies, default=str),
                    report.health_score,
                ),
            )

            conn.commit()
        finally:
            conn.close()

    def register_analysis_callback(self, callback: Callable):
        """Register callback for introspection analysis"""
        self.analysis_callbacks.append(callback)

    def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status"""
        if not self.reports:
            return {"status": "no_data"}

        latest_report = self.reports[-1]
        return {
            "health_score": latest_report.health_score,
            "timestamp": latest_report.timestamp.isoformat(),
            "cpu_usage": latest_report.system_state.cpu_usage,
            "memory_usage": latest_report.system_state.memory_usage,
            "active_threads": latest_report.system_state.active_threads,
            "component_count": len(latest_report.system_state.component_states),
            "error_count": latest_report.system_state.error_count,
            "warning_count": latest_report.system_state.warning_count,
            "recommendations": latest_report.recommendations,
        }


# Testing function
async def test_introspection_controller():
    """Test the introspection controller"""
    controller = IntrospectionController()

    # Register a test component
    def check_test_component():
        return {"response_time": 150.0, "error_rate": 0.02}

    controller.component_monitor.register_component(
        "test_component",
        check_test_component,
        {"response_time_threshold": 200.0, "error_rate_critical": 0.1},
    )

    # Start introspection
    await controller.start_introspection(interval=5)

    # Let it run for a bit
    await asyncio.sleep(10)

    # Get health status
    status = controller.get_health_status()
    print("Health Status:")
    print(json.dumps(status, indent=2, default=str))

    # Stop introspection
    await controller.stop_introspection()


if __name__ == "__main__":
    asyncio.run(test_introspection_controller())
