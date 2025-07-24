#!/usr/bin/env python3
"""
📊 SELF-METRICS DASHBOARD - Lyrixa Self-Awareness & Performance Analytics
========================================================================

Real-time monitoring of Lyrixa's cognitive performance, ethical alignment,
and growth trajectory. Provides comprehensive introspection capabilities.

Key Features:
• Memory continuity tracking
• Narrative integrity measurement
• Conflict detection and resolution
• Ethics alignment scoring
• Growth trajectory monitoring
• Real-time performance analytics
"""

import asyncio
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import metrics components
try:
    from .conflict_heatmap import ConflictHeatmapGenerator
    from .ethics_score_tracker import EthicsScoreTracker
    from .growth_trajectory_monitor import GrowthTrajectoryMonitor
    from .memory_continuity_score import MemoryContinuityTracker
    from .narrative_integrity_index import NarrativeIntegrityMonitor
except ImportError:
    print("⚠️ Self-metrics components not yet available - will use placeholder metrics")
    MemoryContinuityTracker = None
    NarrativeIntegrityMonitor = None
    ConflictHeatmapGenerator = None
    EthicsScoreTracker = None
    GrowthTrajectoryMonitor = None


@dataclass
class MetricSnapshot:
    """Snapshot of all metrics at a specific time"""

    timestamp: str
    memory_continuity_score: float
    narrative_integrity_index: float
    ethics_alignment_score: float
    conflict_resolution_efficiency: float
    growth_trajectory_slope: float
    performance_indicators: Dict[str, float]
    system_health_score: float


@dataclass
class PerformanceAlert:
    """Alert for performance issues"""

    alert_id: str
    alert_type: str
    severity: str  # low, medium, high, critical
    metric_name: str
    current_value: float
    threshold_value: float
    description: str
    recommended_actions: List[str]
    timestamp: str


class SelfMetricsDashboard:
    """
    Comprehensive self-awareness and performance monitoring system
    """

    def __init__(self, data_dir: str = "self_metrics_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize database
        self.db_path = self.data_dir / "self_metrics.db"
        self._init_database()

        # Initialize metric trackers
        self.memory_tracker = (
            MemoryContinuityTracker() if MemoryContinuityTracker else None
        )
        self.narrative_monitor = (
            NarrativeIntegrityMonitor() if NarrativeIntegrityMonitor else None
        )
        self.conflict_generator = (
            ConflictHeatmapGenerator() if ConflictHeatmapGenerator else None
        )
        self.ethics_tracker = EthicsScoreTracker() if EthicsScoreTracker else None
        self.growth_monitor = (
            GrowthTrajectoryMonitor() if GrowthTrajectoryMonitor else None
        )

        # Performance thresholds
        self.performance_thresholds = {
            "memory_continuity_score": {"min": 0.7, "max": 1.0},
            "narrative_integrity_index": {"min": 0.8, "max": 1.0},
            "ethics_alignment_score": {"min": 0.85, "max": 1.0},
            "conflict_resolution_efficiency": {"min": 0.75, "max": 1.0},
            "system_health_score": {"min": 0.8, "max": 1.0},
        }

        # Current metrics cache
        self.current_metrics: Optional[MetricSnapshot] = None
        self.active_alerts: List[PerformanceAlert] = []

        print("📊 SelfMetricsDashboard initialized with comprehensive monitoring")

    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Metrics snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metric_snapshots (
                timestamp TEXT PRIMARY KEY,
                memory_continuity_score REAL,
                narrative_integrity_index REAL,
                ethics_alignment_score REAL,
                conflict_resolution_efficiency REAL,
                growth_trajectory_slope REAL,
                system_health_score REAL,
                performance_indicators TEXT,
                created_at TEXT
            )
        """)

        # Performance alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_alerts (
                alert_id TEXT PRIMARY KEY,
                alert_type TEXT,
                severity TEXT,
                metric_name TEXT,
                current_value REAL,
                threshold_value REAL,
                description TEXT,
                recommended_actions TEXT,
                timestamp TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                resolution_timestamp TEXT
            )
        """)

        # Metric trends table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metric_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                value REAL,
                timestamp TEXT,
                context TEXT
            )
        """)

        conn.commit()
        conn.close()

        print("   📋 Metrics database initialized")

    async def capture_metric_snapshot(self) -> MetricSnapshot:
        """Capture current state of all metrics"""
        print("📸 Capturing comprehensive metric snapshot...")

        # Get current timestamp
        timestamp = datetime.now().isoformat()

        # Collect metrics from all trackers
        memory_score = await self._get_memory_continuity_score()
        narrative_index = await self._get_narrative_integrity_index()
        ethics_score = await self._get_ethics_alignment_score()
        conflict_efficiency = await self._get_conflict_resolution_efficiency()
        growth_slope = await self._get_growth_trajectory_slope()

        # Calculate system health score
        system_health = self._calculate_system_health_score(
            {
                "memory_continuity": memory_score,
                "narrative_integrity": narrative_index,
                "ethics_alignment": ethics_score,
                "conflict_resolution": conflict_efficiency,
            }
        )

        # Collect performance indicators
        performance_indicators = await self._collect_performance_indicators()

        # Create snapshot
        snapshot = MetricSnapshot(
            timestamp=timestamp,
            memory_continuity_score=memory_score,
            narrative_integrity_index=narrative_index,
            ethics_alignment_score=ethics_score,
            conflict_resolution_efficiency=conflict_efficiency,
            growth_trajectory_slope=growth_slope,
            performance_indicators=performance_indicators,
            system_health_score=system_health,
        )

        # Store snapshot
        await self._store_metric_snapshot(snapshot)
        self.current_metrics = snapshot

        # Check for performance alerts
        await self._check_performance_alerts(snapshot)

        print(f"   ✅ Metric snapshot captured (Health: {system_health:.2f})")
        return snapshot

    async def _get_memory_continuity_score(self) -> float:
        """Get current memory continuity score"""
        if self.memory_tracker:
            return await self.memory_tracker.calculate_continuity_score()
        else:
            # Placeholder calculation
            return 0.85  # Simulated good continuity

    async def _get_narrative_integrity_index(self) -> float:
        """Get current narrative integrity index"""
        if self.narrative_monitor:
            return await self.narrative_monitor.calculate_integrity_index()
        else:
            # Placeholder calculation
            return 0.82  # Simulated good integrity

    async def _get_ethics_alignment_score(self) -> float:
        """Get current ethics alignment score"""
        if self.ethics_tracker:
            return await self.ethics_tracker.calculate_alignment_score()
        else:
            # Placeholder calculation
            return 0.91  # Simulated good alignment

    async def _get_conflict_resolution_efficiency(self) -> float:
        """Get current conflict resolution efficiency"""
        if self.conflict_generator:
            return await self.conflict_generator.calculate_resolution_efficiency()
        else:
            # Placeholder calculation
            return 0.78  # Simulated good efficiency

    async def _get_growth_trajectory_slope(self) -> float:
        """Get current growth trajectory slope"""
        if self.growth_monitor:
            return await self.growth_monitor.calculate_trajectory_slope()
        else:
            # Placeholder calculation
            return 0.15  # Simulated positive growth

    def _calculate_system_health_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall system health score"""
        weights = {
            "memory_continuity": 0.25,
            "narrative_integrity": 0.25,
            "ethics_alignment": 0.30,
            "conflict_resolution": 0.20,
        }

        weighted_sum = sum(
            metrics[metric] * weight for metric, weight in weights.items()
        )

        return min(1.0, max(0.0, weighted_sum))

    async def _collect_performance_indicators(self) -> Dict[str, float]:
        """Collect various performance indicators"""
        indicators = {
            "response_time_avg": 0.45,  # seconds
            "memory_usage_mb": 128.5,
            "cpu_utilization": 0.25,
            "error_rate": 0.02,
            "user_satisfaction": 0.88,
            "learning_rate": 0.12,
            "adaptation_speed": 0.75,
            "coherence_score": 0.89,
        }

        return indicators

    async def _store_metric_snapshot(self, snapshot: MetricSnapshot):
        """Store metric snapshot in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO metric_snapshots (
                timestamp, memory_continuity_score, narrative_integrity_index,
                ethics_alignment_score, conflict_resolution_efficiency,
                growth_trajectory_slope, system_health_score,
                performance_indicators, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                snapshot.timestamp,
                snapshot.memory_continuity_score,
                snapshot.narrative_integrity_index,
                snapshot.ethics_alignment_score,
                snapshot.conflict_resolution_efficiency,
                snapshot.growth_trajectory_slope,
                snapshot.system_health_score,
                json.dumps(snapshot.performance_indicators),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    async def _check_performance_alerts(self, snapshot: MetricSnapshot):
        """Check for performance issues and generate alerts"""
        alerts_generated = []

        # Check each metric against thresholds
        metrics_to_check = {
            "memory_continuity_score": snapshot.memory_continuity_score,
            "narrative_integrity_index": snapshot.narrative_integrity_index,
            "ethics_alignment_score": snapshot.ethics_alignment_score,
            "conflict_resolution_efficiency": snapshot.conflict_resolution_efficiency,
            "system_health_score": snapshot.system_health_score,
        }

        for metric_name, value in metrics_to_check.items():
            threshold = self.performance_thresholds.get(metric_name, {})
            min_threshold = threshold.get("min", 0.0)

            if value < min_threshold:
                severity = self._determine_alert_severity(value, min_threshold)
                alert = await self._create_performance_alert(
                    metric_name, value, min_threshold, severity, snapshot.timestamp
                )
                alerts_generated.append(alert)

        if alerts_generated:
            print(f"   ⚠️ Generated {len(alerts_generated)} performance alerts")

    def _determine_alert_severity(self, value: float, threshold: float) -> str:
        """Determine alert severity based on how far below threshold the value is"""
        ratio = value / threshold

        if ratio < 0.5:
            return "critical"
        elif ratio < 0.7:
            return "high"
        elif ratio < 0.9:
            return "medium"
        else:
            return "low"

    async def _create_performance_alert(
        self,
        metric_name: str,
        value: float,
        threshold: float,
        severity: str,
        timestamp: str,
    ) -> PerformanceAlert:
        """Create and store performance alert"""
        alert_id = f"alert_{metric_name}_{timestamp.replace(':', '-')}"

        # Generate recommendations based on metric
        recommendations = self._get_metric_recommendations(
            metric_name, value, threshold
        )

        alert = PerformanceAlert(
            alert_id=alert_id,
            alert_type="threshold_violation",
            severity=severity,
            metric_name=metric_name,
            current_value=value,
            threshold_value=threshold,
            description=f"{metric_name} below threshold: {value:.3f} < {threshold:.3f}",
            recommended_actions=recommendations,
            timestamp=timestamp,
        )

        # Store alert in database
        await self._store_performance_alert(alert)
        self.active_alerts.append(alert)

        return alert

    def _get_metric_recommendations(
        self, metric_name: str, value: float, threshold: float
    ) -> List[str]:
        """Get specific recommendations for metric improvement"""
        recommendations = {
            "memory_continuity_score": [
                "Run memory consolidation process",
                "Check for fragmented memories",
                "Verify temporal coherence in memory links",
                "Increase memory refresh frequency",
            ],
            "narrative_integrity_index": [
                "Review narrative consistency checks",
                "Validate story coherence algorithms",
                "Check for conflicting narratives",
                "Run narrative reconstruction process",
            ],
            "ethics_alignment_score": [
                "Review recent ethical decisions",
                "Run ethics calibration process",
                "Check for value drift",
                "Validate moral reasoning algorithms",
            ],
            "conflict_resolution_efficiency": [
                "Analyze recent conflict patterns",
                "Update conflict resolution strategies",
                "Check decision-making latency",
                "Review consensus mechanisms",
            ],
            "system_health_score": [
                "Run comprehensive system diagnostics",
                "Check individual component health",
                "Verify inter-component communication",
                "Review resource utilization",
            ],
        }

        return recommendations.get(
            metric_name, ["Review metric calculation", "Check system status"]
        )

    async def _store_performance_alert(self, alert: PerformanceAlert):
        """Store performance alert in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO performance_alerts (
                alert_id, alert_type, severity, metric_name,
                current_value, threshold_value, description,
                recommended_actions, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                alert.alert_id,
                alert.alert_type,
                alert.severity,
                alert.metric_name,
                alert.current_value,
                alert.threshold_value,
                alert.description,
                json.dumps(alert.recommended_actions),
                alert.timestamp,
            ),
        )

        conn.commit()
        conn.close()

    async def get_metrics_history(
        self, hours: int = 24, metric_names: Optional[List[str]] = None
    ) -> List[MetricSnapshot]:
        """Get historical metrics data"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        cursor.execute(
            """
            SELECT * FROM metric_snapshots
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC
        """,
            (start_time.isoformat(), end_time.isoformat()),
        )

        rows = cursor.fetchall()
        conn.close()

        snapshots = []
        for row in rows:
            # Reconstruct MetricSnapshot
            snapshot = MetricSnapshot(
                timestamp=row[0],
                memory_continuity_score=row[1],
                narrative_integrity_index=row[2],
                ethics_alignment_score=row[3],
                conflict_resolution_efficiency=row[4],
                growth_trajectory_slope=row[5],
                system_health_score=row[6],
                performance_indicators=json.loads(row[7]) if row[7] else {},
            )
            snapshots.append(snapshot)

        return snapshots

    async def get_metric_trends(
        self, metric_name: str, hours: int = 24
    ) -> Dict[str, Any]:
        """Get trends for specific metric"""
        history = await self.get_metrics_history(hours)

        if not history:
            return {"trend": "no_data", "values": [], "timestamps": []}

        # Extract values and timestamps
        values = []
        timestamps = []

        for snapshot in history:
            if hasattr(snapshot, metric_name):
                values.append(getattr(snapshot, metric_name))
                timestamps.append(snapshot.timestamp)

        if len(values) < 2:
            return {
                "trend": "insufficient_data",
                "values": values,
                "timestamps": timestamps,
            }

        # Calculate trend
        trend_direction = "stable"
        if len(values) >= 2:
            recent_avg = sum(values[-3:]) / min(3, len(values))
            earlier_avg = sum(values[:3]) / min(3, len(values))

            if recent_avg > earlier_avg * 1.05:
                trend_direction = "improving"
            elif recent_avg < earlier_avg * 0.95:
                trend_direction = "declining"

        return {
            "trend": trend_direction,
            "values": values,
            "timestamps": timestamps,
            "current_value": values[-1] if values else 0,
            "average_value": sum(values) / len(values) if values else 0,
            "min_value": min(values) if values else 0,
            "max_value": max(values) if values else 0,
        }

    async def generate_dashboard_report(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard report"""

        if not self.current_metrics:
            await self.capture_metric_snapshot()

        # Get recent trends
        trend_hours = 24
        memory_trends = await self.get_metric_trends(
            "memory_continuity_score", trend_hours
        )
        narrative_trends = await self.get_metric_trends(
            "narrative_integrity_index", trend_hours
        )
        ethics_trends = await self.get_metric_trends(
            "ethics_alignment_score", trend_hours
        )

        # Get active alerts
        active_alerts = [asdict(alert) for alert in self.active_alerts]

        report = {
            "timestamp": datetime.now().isoformat(),
            "current_metrics": asdict(self.current_metrics)
            if self.current_metrics
            else {},
            "metric_trends": {
                "memory_continuity": memory_trends,
                "narrative_integrity": narrative_trends,
                "ethics_alignment": ethics_trends,
            },
            "active_alerts": active_alerts,
            "system_status": self._get_system_status(),
            "recommendations": await self._get_system_recommendations(),
        }

        return report

    def _get_system_status(self) -> str:
        """Get overall system status"""
        if not self.current_metrics:
            return "unknown"

        health_score = self.current_metrics.system_health_score

        if health_score >= 0.9:
            return "excellent"
        elif health_score >= 0.8:
            return "good"
        elif health_score >= 0.7:
            return "fair"
        elif health_score >= 0.6:
            return "poor"
        else:
            return "critical"

    async def _get_system_recommendations(self) -> List[str]:
        """Get system-wide recommendations"""
        recommendations = []

        if not self.current_metrics:
            return ["Capture initial metric snapshot"]

        # Check each metric and provide recommendations
        if self.current_metrics.memory_continuity_score < 0.8:
            recommendations.append("Consider memory optimization and consolidation")

        if self.current_metrics.narrative_integrity_index < 0.8:
            recommendations.append("Review narrative consistency mechanisms")

        if self.current_metrics.ethics_alignment_score < 0.85:
            recommendations.append("Run ethics calibration and review recent decisions")

        if self.current_metrics.conflict_resolution_efficiency < 0.75:
            recommendations.append(
                "Analyze conflict patterns and update resolution strategies"
            )

        if not recommendations:
            recommendations.append(
                "System performing well - continue regular monitoring"
            )

        return recommendations


# Example usage and testing
async def demo_self_metrics_dashboard():
    """Demonstrate self-metrics dashboard capabilities"""
    print("📊 SELF-METRICS DASHBOARD DEMONSTRATION")
    print("=" * 60)

    dashboard = SelfMetricsDashboard()

    # Capture initial metrics
    snapshot = await dashboard.capture_metric_snapshot()
    print(f"\n📸 Current Metrics:")
    print(f"   • Memory Continuity: {snapshot.memory_continuity_score:.3f}")
    print(f"   • Narrative Integrity: {snapshot.narrative_integrity_index:.3f}")
    print(f"   • Ethics Alignment: {snapshot.ethics_alignment_score:.3f}")
    print(f"   • System Health: {snapshot.system_health_score:.3f}")

    # Generate comprehensive report
    report = await dashboard.generate_dashboard_report()
    print(f"\n📋 Dashboard Report:")
    print(f"   • System Status: {report['system_status']}")
    print(f"   • Active Alerts: {len(report['active_alerts'])}")
    print(f"   • Recommendations: {len(report['recommendations'])}")

    for rec in report["recommendations"][:3]:
        print(f"     - {rec}")


if __name__ == "__main__":
    asyncio.run(demo_self_metrics_dashboard())
