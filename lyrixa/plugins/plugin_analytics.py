"""
Unified Plugin Analytics System
==============================

Comprehensive analytics and performance tracking for Lyrixa plugins.
Tracks execution metrics, usage patterns, performance data, and provides insights
for optimization and plugin management.
"""

import json
import logging
import sqlite3
import statistics
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginMetricsCollector:
    """Collects detailed metrics for plugin execution and usage."""
    # Required plugin metadata
    name = "plugin_analytics"
    description = "PluginMetricsCollector - Auto-generated description"
    input_schema = {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Input data"}
        },
        "required": ["input"]
    }
    output_schema = {
        "type": "object",
        "properties": {
            "result": {"type": "string", "description": "Processing result"},
            "status": {"type": "string", "description": "Operation status"}
        }
    }
    created_by = "Plugin System Auto-Fixer"


    def __init__(self, db_path: str = "plugin_analytics.db"):
        self.db_path = db_path
        self.session_data = {}
        self.lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Initialize the analytics database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    memory_usage REAL,
                    cpu_usage REAL,
                    timestamp TEXT NOT NULL,
                    context_hash TEXT,
                    user_session TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_session TEXT,
                    context_data TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    timestamp TEXT NOT NULL,
                    context_data TEXT
                )
            """)

            # Create indexes for better performance
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_plugin_id ON plugin_executions(plugin_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON plugin_executions(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_plugin_usage ON plugin_usage(plugin_id, timestamp)"
            )

    def record_execution(
        self,
        plugin_id: str,
        execution_time: float,
        success: bool,
        error_message: Optional[str] = None,
        memory_usage: Optional[float] = None,
        cpu_usage: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ):
        """Record a plugin execution event."""
        try:
            with self.lock:
                timestamp = datetime.now().isoformat()
                context_hash = self._hash_context(context or {})

                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO plugin_executions
                        (plugin_id, execution_time, success, error_message,
                         memory_usage, cpu_usage, timestamp, context_hash, user_session)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            plugin_id,
                            execution_time,
                            success,
                            error_message,
                            memory_usage,
                            cpu_usage,
                            timestamp,
                            context_hash,
                            session_id,
                        ),
                    )

                # Update session data
                if session_id not in self.session_data:
                    self.session_data[session_id] = {
                        "executions": 0,
                        "total_time": 0.0,
                        "plugins_used": set(),
                    }

                self.session_data[session_id]["executions"] += 1
                self.session_data[session_id]["total_time"] += execution_time
                self.session_data[session_id]["plugins_used"].add(plugin_id)

        except Exception as e:
            logger.error(f"Failed to record execution: {e}")

    def record_usage(
        self,
        plugin_id: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ):
        """Record a plugin usage event."""
        try:
            with self.lock:
                timestamp = datetime.now().isoformat()
                context_json = json.dumps(context or {})

                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO plugin_usage
                        (plugin_id, action, timestamp, user_session, context_data)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (plugin_id, action, timestamp, session_id, context_json),
                    )

        except Exception as e:
            logger.error(f"Failed to record usage: {e}")

    def record_error(
        self,
        plugin_id: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Record a plugin error event."""
        try:
            with self.lock:
                timestamp = datetime.now().isoformat()
                context_json = json.dumps(context or {})

                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO plugin_errors
                        (plugin_id, error_type, error_message, stack_trace,
                         timestamp, context_data)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            plugin_id,
                            error_type,
                            error_message,
                            stack_trace,
                            timestamp,
                            context_json,
                        ),
                    )

        except Exception as e:
            logger.error(f"Failed to record error: {e}")

    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Create a hash for context data."""
        import hashlib

        context_str = json.dumps(context, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()[:16]

    def get_plugin_metrics(self, plugin_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive metrics for a specific plugin."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            with sqlite3.connect(self.db_path) as conn:
                # Execution metrics
                cursor = conn.execute(
                    """
                    SELECT execution_time, success, memory_usage, cpu_usage, timestamp
                    FROM plugin_executions
                    WHERE plugin_id = ? AND timestamp > ?
                    ORDER BY timestamp DESC
                """,
                    (plugin_id, cutoff_date),
                )

                executions = cursor.fetchall()

                if not executions:
                    return {"plugin_id": plugin_id, "metrics": "No data available"}

                # Calculate metrics
                execution_times = [row[0] for row in executions]
                success_count = sum(1 for row in executions if row[1])
                total_executions = len(executions)

                metrics = {
                    "plugin_id": plugin_id,
                    "total_executions": total_executions,
                    "success_rate": (success_count / total_executions) * 100,
                    "avg_execution_time": statistics.mean(execution_times),
                    "median_execution_time": statistics.median(execution_times),
                    "min_execution_time": min(execution_times),
                    "max_execution_time": max(execution_times),
                    "total_runtime": sum(execution_times),
                }

                # Memory and CPU stats (if available)
                memory_usage = [row[2] for row in executions if row[2] is not None]
                cpu_usage = [row[3] for row in executions if row[3] is not None]

                if memory_usage:
                    metrics["avg_memory_usage"] = statistics.mean(memory_usage)
                    metrics["max_memory_usage"] = max(memory_usage)

                if cpu_usage:
                    metrics["avg_cpu_usage"] = statistics.mean(cpu_usage)
                    metrics["max_cpu_usage"] = max(cpu_usage)

                # Usage patterns
                cursor = conn.execute(
                    """
                    SELECT action, COUNT(*) as count
                    FROM plugin_usage
                    WHERE plugin_id = ? AND timestamp > ?
                    GROUP BY action
                """,
                    (plugin_id, cutoff_date),
                )

                metrics["usage_patterns"] = dict(cursor.fetchall())

                # Error analysis
                cursor = conn.execute(
                    """
                    SELECT error_type, COUNT(*) as count
                    FROM plugin_errors
                    WHERE plugin_id = ? AND timestamp > ?
                    GROUP BY error_type
                """,
                    (plugin_id, cutoff_date),
                )

                metrics["error_patterns"] = dict(cursor.fetchall())

                return metrics

        except Exception as e:
            logger.error(f"Failed to get plugin metrics: {e}")
            return {"plugin_id": plugin_id, "error": str(e)}


class PluginAnalyticsDashboard:
    """Dashboard for visualizing plugin analytics and insights."""

    def __init__(self, metrics_collector: PluginMetricsCollector):
        self.metrics = metrics_collector

    def generate_system_summary(self, days: int = 7) -> Dict[str, Any]:
        """Generate a system-wide analytics summary."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            with sqlite3.connect(self.metrics.db_path) as conn:
                # Total system metrics
                cursor = conn.execute(
                    """
                    SELECT COUNT(*) as total_executions,
                           AVG(execution_time) as avg_time,
                           SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                    FROM plugin_executions
                    WHERE timestamp > ?
                """,
                    (cutoff_date,),
                )

                system_stats = cursor.fetchone()

                # Most used plugins
                cursor = conn.execute(
                    """
                    SELECT plugin_id, COUNT(*) as usage_count
                    FROM plugin_executions
                    WHERE timestamp > ?
                    GROUP BY plugin_id
                    ORDER BY usage_count DESC
                    LIMIT 10
                """,
                    (cutoff_date,),
                )

                most_used = cursor.fetchall()

                # Performance trends
                cursor = conn.execute(
                    """
                    SELECT plugin_id, AVG(execution_time) as avg_time
                    FROM plugin_executions
                    WHERE timestamp > ?
                    GROUP BY plugin_id
                    ORDER BY avg_time DESC
                    LIMIT 5
                """,
                    (cutoff_date,),
                )

                slowest_plugins = cursor.fetchall()

                # Error analysis
                cursor = conn.execute(
                    """
                    SELECT plugin_id, COUNT(*) as error_count
                    FROM plugin_errors
                    WHERE timestamp > ?
                    GROUP BY plugin_id
                    ORDER BY error_count DESC
                    LIMIT 5
                """,
                    (cutoff_date,),
                )

                error_prone = cursor.fetchall()

                return {
                    "system_stats": {
                        "total_executions": system_stats[0] or 0,
                        "avg_execution_time": round(system_stats[1] or 0, 3),
                        "system_success_rate": round(system_stats[2] or 100, 2),
                    },
                    "most_used_plugins": [
                        {"plugin_id": row[0], "usage_count": row[1]}
                        for row in most_used
                    ],
                    "slowest_plugins": [
                        {"plugin_id": row[0], "avg_time": round(row[1], 3)}
                        for row in slowest_plugins
                    ],
                    "error_prone_plugins": [
                        {"plugin_id": row[0], "error_count": row[1]}
                        for row in error_prone
                    ],
                    "period_days": days,
                    "generated_at": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Failed to generate system summary: {e}")
            return {"error": str(e)}

    def generate_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on analytics data."""
        suggestions = []

        try:
            with sqlite3.connect(self.metrics.db_path) as conn:
                # Find slow plugins
                cursor = conn.execute("""
                    SELECT plugin_id, AVG(execution_time) as avg_time, COUNT(*) as usage_count
                    FROM plugin_executions
                    WHERE timestamp > datetime('now', '-7 days')
                    GROUP BY plugin_id
                    HAVING avg_time > 1.0 AND usage_count > 5
                    ORDER BY avg_time DESC
                """)

                for row in cursor.fetchall():
                    suggestions.append(
                        {
                            "type": "performance",
                            "priority": "high",
                            "plugin_id": row[0],
                            "suggestion": f"Plugin '{row[0]}' has slow execution time ({row[1]:.2f}s avg). Consider optimization.",
                            "metric": "execution_time",
                            "value": row[1],
                        }
                    )

                # Find unused plugins
                cursor = conn.execute("""
                    SELECT plugin_id, MAX(timestamp) as last_used
                    FROM plugin_executions
                    GROUP BY plugin_id
                    HAVING last_used < datetime('now', '-14 days')
                """)

                for row in cursor.fetchall():
                    suggestions.append(
                        {
                            "type": "usage",
                            "priority": "medium",
                            "plugin_id": row[0],
                            "suggestion": f"Plugin '{row[0]}' hasn't been used since {row[1][:10]}. Consider unloading.",
                            "metric": "last_used",
                            "value": row[1],
                        }
                    )

                # Find error-prone plugins
                cursor = conn.execute("""
                    SELECT plugin_id, COUNT(*) as error_count
                    FROM plugin_errors
                    WHERE timestamp > datetime('now', '-7 days')
                    GROUP BY plugin_id
                    HAVING error_count > 5
                    ORDER BY error_count DESC
                """)

                for row in cursor.fetchall():
                    suggestions.append(
                        {
                            "type": "reliability",
                            "priority": "high",
                            "plugin_id": row[0],
                            "suggestion": f"Plugin '{row[0]}' has high error rate ({row[1]} errors in 7 days). Check for issues.",
                            "metric": "error_count",
                            "value": row[1],
                        }
                    )

        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            suggestions.append(
                {
                    "type": "system",
                    "priority": "low",
                    "suggestion": f"Analytics system error: {e}",
                    "metric": "system_health",
                    "value": "error",
                }
            )

        return suggestions

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data."""
        return {
            "summary": self.generate_system_summary(),
            "suggestions": self.generate_optimization_suggestions(),
            "timestamp": datetime.now().isoformat(),
        }


class PluginAnalyticsIntegration:
    """Integration layer for easy plugin analytics integration."""

    def __init__(self, db_path: str = "plugin_analytics.db"):
        self.metrics_collector = PluginMetricsCollector(db_path)
        self.dashboard = PluginAnalyticsDashboard(self.metrics_collector)
        self.session_id = f"session_{int(time.time())}"

    def track_plugin_execution(self, plugin_id: str):
        """Context manager for tracking plugin execution."""
        return PluginExecutionTracker(
            self.metrics_collector, plugin_id, self.session_id
        )

    def record_plugin_action(
        self, plugin_id: str, action: str, context: Optional[Dict[str, Any]] = None
    ):
        """Record a plugin action/usage event."""
        self.metrics_collector.record_usage(plugin_id, action, context, self.session_id)

    def record_plugin_error(
        self, plugin_id: str, error: Exception, context: Optional[Dict[str, Any]] = None
    ):
        """Record a plugin error."""
        import traceback

        self.metrics_collector.record_error(
            plugin_id, type(error).__name__, str(error), traceback.format_exc(), context
        )

    def get_plugin_analytics(self, plugin_id: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics for a specific plugin or system overview."""
        if plugin_id:
            return self.metrics_collector.get_plugin_metrics(plugin_id)
        else:
            return self.dashboard.generate_system_summary()

    def get_optimization_insights(self) -> List[Dict[str, Any]]:
        """Get optimization suggestions."""
        return self.dashboard.generate_optimization_suggestions()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data."""
        return self.dashboard.generate_dashboard_data()


class PluginExecutionTracker:
    """Context manager for tracking plugin execution time and outcomes."""

    def __init__(
        self, metrics_collector: PluginMetricsCollector, plugin_id: str, session_id: str
    ):
        self.metrics = metrics_collector
        self.plugin_id = plugin_id
        self.session_id = session_id
        self.start_time = 0.0
        self.context = {}

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None

        self.metrics.record_execution(
            self.plugin_id,
            execution_time,
            success,
            error_message,
            context=self.context,
            session_id=self.session_id,
        )

        if not success:
            import traceback

            self.metrics.record_error(
                self.plugin_id,
                exc_type.__name__ if exc_type else "Unknown",
                error_message or "Unknown error",
                traceback.format_exc() if exc_type else "",
                self.context,
            )

    def set_context(self, context: Dict[str, Any]):
        """Set execution context."""
        self.context = context


# Example usage and testing
if __name__ == "__main__":
    # Initialize analytics system
    analytics = PluginAnalyticsIntegration()

    # Example 1: Track plugin execution
    print("=== Plugin Analytics Demo ===")

    # Simulate plugin executions
    import random
    import time

    plugins = ["data_processor", "ui_enhancer", "file_manager", "api_connector"]

    for i in range(20):
        plugin = random.choice(plugins)

        # Track execution
        with analytics.track_plugin_execution(plugin) as tracker:
            tracker.set_context({"operation": "test", "iteration": i})

            # Simulate work
            time.sleep(random.uniform(0.1, 0.5))

            # Simulate occasional errors
            if random.random() < 0.1:
                raise Exception("Simulated error")

        # Record usage
        analytics.record_plugin_action(plugin, "executed", {"test": True})

    # Get analytics
    dashboard_data = analytics.get_dashboard_data()

    print("\n=== System Summary ===")
    summary = dashboard_data["summary"]
    print(f"Total executions: {summary['system_stats']['total_executions']}")
    print(f"Average execution time: {summary['system_stats']['avg_execution_time']}s")
    print(f"Success rate: {summary['system_stats']['system_success_rate']}%")

    print("\n=== Most Used Plugins ===")
    for plugin in summary["most_used_plugins"]:
        print(f"  {plugin['plugin_id']}: {plugin['usage_count']} uses")

    print("\n=== Optimization Suggestions ===")
    for suggestion in dashboard_data["suggestions"]:
        print(f"  [{suggestion['priority'].upper()}] {suggestion['suggestion']}")

    print("\n=== Individual Plugin Analytics ===")
    for plugin in plugins:
        plugin_metrics = analytics.get_plugin_analytics(plugin)
        if "total_executions" in plugin_metrics:
            print(f"\n{plugin}:")
            print(f"  Executions: {plugin_metrics['total_executions']}")
            print(f"  Success rate: {plugin_metrics['success_rate']:.1f}%")
            print(f"  Avg time: {plugin_metrics['avg_execution_time']:.3f}s")

    print("\n✅ Plugin Analytics Demo Complete")
