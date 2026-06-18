# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Self-Improvement Engine
Continuous learning and system optimization capabilities.
"""

# Standard library imports
import asyncio
import hashlib
import json
import logging
import os
import sqlite3
import traceback
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List

try:
    # Third party imports
    import numpy as np  # type: ignore[assignment]
except ImportError:
    # Fallback numpy-like functions
    class np:
        @staticmethod
        def mean(values):
            return sum(values) / len(values) if values else 0

        @staticmethod
        def std(values):
            if not values:
                return 0
            mean = np.mean(values)
            return (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5

        @staticmethod
        def min(values):
            return min(values) if values else 0

        @staticmethod
        def max(values):
            return max(values) if values else 0

        @staticmethod
        def polyfit(x, y, degree):
            # Simple linear regression for degree 1
            if degree == 1 and len(x) > 1:
                n = len(x)
                sum_x = sum(x)
                sum_y = sum(y)
                sum_xy = sum(x[i] * y[i] for i in range(n))
                sum_x2 = sum(x[i] ** 2 for i in range(n))

                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
                intercept = (sum_y - slope * sum_x) / n
                return [slope, intercept]
            return [0, 0]

        @staticmethod
        def corrcoef(x, y):
            if len(x) != len(y) or len(x) < 2:
                return [[1, 0], [0, 1]]

            mean_x = np.mean(x)
            mean_y = np.mean(y)

            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
            denom_x = sum((x[i] - mean_x) ** 2 for i in range(len(x)))
            denom_y = sum((y[i] - mean_y) ** 2 for i in range(len(y)))

            if denom_x == 0 or denom_y == 0:
                return [[1, 0], [0, 1]]

            correlation = numerator / (denom_x * denom_y) ** 0.5
            return [[1, correlation], [correlation, 1]]


logger = logging.getLogger(__name__)

_VALID_PROPOSAL_RESULT_STATUSES = frozenset(
    {
        "accepted",
        "rejected",
        "failed",
        "error",
        "rolled_back",
        "manual_required",
    }
)


class ImprovementType(Enum):
    """Types of improvements"""

    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    RELIABILITY = "reliability"
    USABILITY = "usability"
    FEATURE = "feature"


class LearningMethod(Enum):
    """Learning methods"""

    REINFORCEMENT = "reinforcement"
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    TRANSFER = "transfer"
    META = "meta"
    EVOLUTIONARY = "evolutionary"


@dataclass
class PerformanceMetric:
    """Performance metric tracking"""

    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] | None = None


@dataclass
class ImprovementProposal:
    """Proposed improvement to the system"""

    proposal_id: str
    improvement_type: ImprovementType
    description: str
    expected_benefit: float
    implementation_cost: float
    risk_level: float
    affected_components: List[str]
    success_criteria: List[str]
    created_at: datetime
    status: str = "proposed"
    issue: str = ""
    potential_cause: str = ""
    proposed_change: str = ""
    evidence: List[str] = field(default_factory=list)
    simulation: Dict[str, Any] = field(default_factory=dict)
    rollback_plan: str = ""
    status_reason: str = ""
    updated_at: datetime | None = None
    proposal_fingerprint: str = ""
    occurrence_count: int = 1
    readiness_status: str = "unknown"
    readiness_reasons: List[str] = field(default_factory=list)


@dataclass
class LearningOutcome:
    """Result of a learning session"""

    session_id: str
    method: LearningMethod
    target_component: str
    improvement_achieved: float
    confidence: float
    learning_data: Dict[str, Any]
    timestamp: datetime


class MetricsCollector:
    """Collects and analyzes system metrics"""

    def __init__(self):
        self.metrics_history: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.collection_active = False

    def record_metric(
        self, name: str, value: float, unit: str, context: Dict[str, Any] | None = None
    ):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name, value=value, unit=unit, timestamp=datetime.now(), context=context
        )
        self.metrics_history[name].append(metric)

        # Keep only recent history (last 1000 entries)
        if len(self.metrics_history[name]) > 1000:
            self.metrics_history[name] = self.metrics_history[name][-1000:]

    def get_metric_trend(self, name: str, window_hours: int = 24) -> tuple[float, str]:
        """Get trend for a metric over specified time window"""
        if name not in self.metrics_history:
            return 0.0, "no_data"

        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent_metrics = [m for m in self.metrics_history[name] if m.timestamp > cutoff]

        if len(recent_metrics) < 2:
            return 0.0, "insufficient_data"

        # Calculate trend using linear regression
        timestamps = [
            (m.timestamp - recent_metrics[0].timestamp).total_seconds() for m in recent_metrics
        ]
        values = [m.value for m in recent_metrics]

        if len(timestamps) > 1:
            slope = np.polyfit(timestamps, values, 1)[0]
            if slope > 0.01:
                return slope, "improving"
            elif slope < -0.01:
                return slope, "degrading"
            else:
                return slope, "stable"

        return 0.0, "stable"

    def get_metric_statistics(self, name: str, window_hours: int = 24) -> Dict[str, float]:
        """Get statistics for a metric"""
        if name not in self.metrics_history:
            return {}

        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent_metrics = [m.value for m in self.metrics_history[name] if m.timestamp > cutoff]

        if not recent_metrics:
            return {}

        return {
            "mean": np.mean(recent_metrics),
            "std": np.std(recent_metrics),
            "min": np.min(recent_metrics),
            "max": np.max(recent_metrics),
            "count": len(recent_metrics),
        }


class PatternAnalyzer:
    """Analyzes patterns in system behavior"""

    def __init__(self):
        self.patterns: Dict[str, Dict] = {}

    def identify_performance_patterns(
        self, metrics: Dict[str, List[PerformanceMetric]]
    ) -> List[Dict]:
        """Identify patterns in performance metrics"""
        patterns = []

        for metric_name, metric_list in metrics.items():
            if len(metric_list) < 10:
                continue

            # Analyze time-based patterns
            pattern = self._analyze_temporal_pattern(metric_name, metric_list)
            if pattern:
                patterns.append(pattern)

            # Analyze correlation patterns
            correlation_pattern = self._analyze_correlations(metric_name, metric_list, metrics)
            if correlation_pattern:
                patterns.append(correlation_pattern)

        return patterns

    def _analyze_temporal_pattern(self, name: str, metrics: List[PerformanceMetric]) -> Dict | None:
        """Analyze temporal patterns in metrics"""
        if len(metrics) < 10:
            return None

        values = [m.value for m in metrics[-50:]]  # Last 50 measurements

        # Check for cyclical patterns
        if self._has_cyclical_pattern(values):
            return {
                "type": "cyclical",
                "metric": name,
                "description": f"Cyclical pattern detected in {name}",
                "confidence": 0.8,
            }

        # Check for trend patterns
        trend_slope = np.polyfit(range(len(values)), values, 1)[0]
        if abs(trend_slope) > 0.1:
            trend_type = "increasing" if trend_slope > 0 else "decreasing"
            return {
                "type": "trend",
                "metric": name,
                "description": f"{trend_type.capitalize()} trend in {name}",
                "slope": trend_slope,
                "confidence": 0.7,
            }

        return None

    def _has_cyclical_pattern(self, values: List[float]) -> bool:
        """Check if values show cyclical pattern"""
        if len(values) < 20:
            return False

        # Simple autocorrelation check
        mean_val = np.mean(values)
        normalized = [v - mean_val for v in values]

        # Check for correlation at different lags
        for lag in range(2, min(10, len(values) // 3)):
            correlation_matrix = np.corrcoef(normalized[:-lag], normalized[lag:])
            correlation = correlation_matrix[0][1]

            if abs(correlation) > 0.6:
                return True

        return False

    def _analyze_correlations(
        self,
        metric_name: str,
        metric_list: List[PerformanceMetric],
        all_metrics: Dict[str, List[PerformanceMetric]],
    ) -> Dict | None:
        """Analyze correlations between metrics"""
        # Find metrics that correlate with the current one
        correlations = []

        for other_name, other_metrics in all_metrics.items():
            if other_name == metric_name or len(other_metrics) < 10:
                continue

            correlation = self._calculate_correlation(metric_list, other_metrics)
            if abs(correlation) > 0.7:
                correlations.append({"metric": other_name, "correlation": correlation})

        if correlations:
            return {
                "type": "correlation",
                "metric": metric_name,
                "correlations": correlations,
                "description": f"{metric_name} correlates with {len(correlations)} other metrics",
            }

        return None

    def _calculate_correlation(
        self, metrics1: List[PerformanceMetric], metrics2: List[PerformanceMetric]
    ) -> float:
        """Calculate correlation between two metric series"""
        # Align timestamps and calculate correlation
        values1, values2 = [], []

        for m1 in metrics1[-50:]:
            # Find closest timestamp in metrics2
            closest = min(
                metrics2[-50:],
                key=lambda m2: abs((m1.timestamp - m2.timestamp).total_seconds()),
            )

            # Only include if timestamps are within 1 minute
            if abs((m1.timestamp - closest.timestamp).total_seconds()) < 60:
                values1.append(m1.value)
                values2.append(closest.value)

        if len(values1) < 5:
            return 0.0

        correlation_matrix = np.corrcoef(values1, values2)
        return correlation_matrix[0][1] if len(values1) > 1 else 0.0


class ImprovementGenerator:
    """Generates improvement proposals based on analysis"""

    def __init__(self):
        self.improvement_rules = self._init_improvement_rules()

    def _init_improvement_rules(self) -> Dict[str, Callable]:
        """Initialize improvement generation rules"""
        return {
            "performance_degradation": self._generate_performance_improvements,
            "resource_inefficiency": self._generate_efficiency_improvements,
            "error_rate_increase": self._generate_reliability_improvements,
            "pattern_anomaly": self._generate_pattern_improvements,
        }

    def generate_improvements(
        self, patterns: List[Dict], metrics: Dict[str, Any]
    ) -> List[ImprovementProposal]:
        """Generate improvement proposals based on patterns and metrics"""
        proposals = []

        for pattern in patterns:
            improvements = self._generate_from_pattern(pattern, metrics)
            proposals.extend(improvements)

        # Generate improvements from direct metric analysis
        metric_improvements = self._generate_from_metrics(metrics)
        proposals.extend(metric_improvements)

        return proposals

    def _generate_from_pattern(
        self, pattern: Dict, metrics: Dict[str, Any]
    ) -> List[ImprovementProposal]:
        """Generate improvements from identified patterns"""
        proposals = []

        if pattern["type"] == "trend" and pattern.get("slope", 0) < -0.1:
            # Degrading performance trend
            issue = f"{pattern['metric']} is trending downward"
            proposed_change = f"Review and tune the subsystem affecting {pattern['metric']}"
            fingerprint = self._fingerprint(
                ImprovementType.PERFORMANCE,
                issue,
                [pattern["metric"]],
                proposed_change,
            )
            proposal = ImprovementProposal(
                proposal_id=self._proposal_id(fingerprint),
                improvement_type=ImprovementType.PERFORMANCE,
                description=f"Address declining performance in {pattern['metric']}",
                expected_benefit=0.3,
                implementation_cost=0.5,
                risk_level=0.2,
                affected_components=[pattern["metric"]],
                success_criteria=[f"Reverse negative trend in {pattern['metric']}"],
                created_at=datetime.now(),
                issue=issue,
                potential_cause="Sustained degradation detected in recent metric history",
                proposed_change=proposed_change,
                evidence=[
                    f"pattern:type={pattern.get('type')}",
                    f"metric:{pattern['metric']}",
                    f"slope:{pattern.get('slope', 0)}",
                ],
                simulation=self._simulate(
                    expected_benefit=0.3,
                    implementation_cost=0.5,
                    risk_level=0.2,
                    rollback_available=True,
                    testable=True,
                ),
                rollback_plan=f"Revert tuning changes for {pattern['metric']} if trend worsens",
                proposal_fingerprint=fingerprint,
            )
            proposals.append(proposal)

        elif pattern["type"] == "cyclical":
            # Optimize cyclical patterns
            issue = f"{pattern['metric']} shows recurring cyclical variance"
            proposed_change = f"Investigate smoothing or scheduling controls for {pattern['metric']}"
            fingerprint = self._fingerprint(
                ImprovementType.EFFICIENCY,
                issue,
                [pattern["metric"]],
                proposed_change,
            )
            proposal = ImprovementProposal(
                proposal_id=self._proposal_id(fingerprint),
                improvement_type=ImprovementType.EFFICIENCY,
                description=f"Optimize cyclical pattern in {pattern['metric']}",
                expected_benefit=0.2,
                implementation_cost=0.3,
                risk_level=0.1,
                affected_components=[pattern["metric"]],
                success_criteria=[f"Reduce amplitude of cycles in {pattern['metric']}"],
                created_at=datetime.now(),
                issue=issue,
                potential_cause="Periodic workload or scheduling behavior may be amplifying variance",
                proposed_change=proposed_change,
                evidence=[
                    f"pattern:type={pattern.get('type')}",
                    f"metric:{pattern['metric']}",
                ],
                simulation=self._simulate(
                    expected_benefit=0.2,
                    implementation_cost=0.3,
                    risk_level=0.1,
                    rollback_available=True,
                    testable=True,
                ),
                rollback_plan=f"Disable smoothing changes for {pattern['metric']} if variance increases",
                proposal_fingerprint=fingerprint,
            )
            proposals.append(proposal)

        return proposals

    def _generate_from_metrics(self, metrics: Dict[str, Any]) -> List[ImprovementProposal]:
        """Generate improvements from metric analysis"""
        proposals = []

        # Example: CPU usage consistently high
        if "cpu_usage" in metrics:
            cpu_stats = metrics["cpu_usage"]
            if self._metric_mean_exceeds(cpu_stats, 80):
                proposals.append(
                    self._build_metric_proposal(
                        improvement_type=ImprovementType.PERFORMANCE,
                        issue="CPU utilization is consistently high",
                        potential_cause=(
                            "Scheduler pressure, process contention, or inefficient "
                            "work batching"
                        ),
                        proposed_change=(
                            "Analyze CPU-heavy paths and propose scheduler or "
                            "batching improvements"
                        ),
                        description=(
                            "Optimize CPU usage - consistently high utilization detected"
                        ),
                        expected_benefit=0.7,
                        implementation_cost=0.3,
                        risk_level=0.2,
                        affected_components=["cpu_scheduler", "process_manager"],
                        success_criteria=["Reduce average CPU usage to below 70%"],
                        evidence=[
                            "metric:cpu_usage",
                            f"mean:{cpu_stats.get('mean', 0)}",
                            f"max:{cpu_stats.get('max', 0)}",
                        ],
                        rollback_plan=(
                            "Restore previous scheduler or process-manager configuration"
                        ),
                    )
                )

        if "response_time" in metrics:
            response_stats = metrics["response_time"]
            if self._metric_mean_exceeds(response_stats, 500):
                proposals.append(
                    self._build_metric_proposal(
                        improvement_type=ImprovementType.PERFORMANCE,
                        issue="Response latency is consistently elevated",
                        potential_cause=(
                            "Request routing, model invocation, or downstream service "
                            "latency may be degrading response time"
                        ),
                        proposed_change=(
                            "Profile high-latency request paths and propose queueing, "
                            "cache, or routing improvements"
                        ),
                        description="Investigate sustained response latency",
                        expected_benefit=0.7,
                        implementation_cost=0.3,
                        risk_level=0.2,
                        affected_components=["request_router", "latency_pipeline"],
                        success_criteria=["Reduce mean response time below 500 ms"],
                        evidence=[
                            "metric:response_time",
                            f"mean:{response_stats.get('mean', 0)}",
                            f"max:{response_stats.get('max', 0)}",
                        ],
                        rollback_plan="Restore previous request routing and cache settings",
                    )
                )

        if "memory_usage" in metrics:
            memory_stats = metrics["memory_usage"]
            if self._metric_mean_exceeds(memory_stats, 85):
                proposals.append(
                    self._build_metric_proposal(
                        improvement_type=ImprovementType.EFFICIENCY,
                        issue="Memory utilization is consistently high",
                        potential_cause=(
                            "Cache growth, retained contexts, or memory-intensive "
                            "workers may be increasing pressure"
                        ),
                        proposed_change=(
                            "Review cache bounds, context retention, and worker memory "
                            "budgets before proposing changes"
                        ),
                        description="Investigate sustained memory pressure",
                        expected_benefit=0.75,
                        implementation_cost=0.3,
                        risk_level=0.25,
                        affected_components=["memory_manager", "cache_layer"],
                        success_criteria=["Reduce average memory usage below 80%"],
                        evidence=[
                            "metric:memory_usage",
                            f"mean:{memory_stats.get('mean', 0)}",
                            f"max:{memory_stats.get('max', 0)}",
                        ],
                        rollback_plan="Restore previous cache and memory budget settings",
                    )
                )

        if "error_rate" in metrics:
            error_stats = metrics["error_rate"]
            if self._metric_mean_exceeds(error_stats, 0.05):
                proposals.append(
                    self._build_metric_proposal(
                        improvement_type=ImprovementType.RELIABILITY,
                        issue="Error rate is above the reliability threshold",
                        potential_cause=(
                            "A service, integration path, or retry policy may be "
                            "producing recurring failures"
                        ),
                        proposed_change=(
                            "Analyze error sources and propose targeted reliability "
                            "or retry policy improvements"
                        ),
                        description="Investigate elevated error rate",
                        expected_benefit=0.8,
                        implementation_cost=0.35,
                        risk_level=0.25,
                        affected_components=["error_handling", "service_health"],
                        success_criteria=["Reduce average error rate below 5%"],
                        evidence=[
                            "metric:error_rate",
                            f"mean:{error_stats.get('mean', 0)}",
                            f"max:{error_stats.get('max', 0)}",
                        ],
                        rollback_plan="Restore previous error-handling or retry policy",
                    )
                )

        return proposals

    @staticmethod
    def _metric_mean_exceeds(
        stats: dict[str, Any],
        threshold: float,
        *,
        minimum_samples: int = 3,
    ) -> bool:
        """Return whether a metric is persistently above threshold."""
        try:
            count = int(stats.get("count", 0))
            mean = float(stats.get("mean", 0.0))
        except (TypeError, ValueError):
            return False
        return count >= minimum_samples and mean > threshold

    def _build_metric_proposal(
        self,
        *,
        improvement_type: ImprovementType,
        issue: str,
        potential_cause: str,
        proposed_change: str,
        description: str,
        expected_benefit: float,
        implementation_cost: float,
        risk_level: float,
        affected_components: list[str],
        success_criteria: list[str],
        evidence: list[str],
        rollback_plan: str,
    ) -> ImprovementProposal:
        fingerprint = self._fingerprint(
            improvement_type,
            issue,
            affected_components,
            proposed_change,
        )
        return ImprovementProposal(
            proposal_id=self._proposal_id(fingerprint),
            improvement_type=improvement_type,
            description=description,
            expected_benefit=expected_benefit,
            implementation_cost=implementation_cost,
            risk_level=risk_level,
            affected_components=affected_components,
            success_criteria=success_criteria,
            created_at=datetime.now(),
            issue=issue,
            potential_cause=potential_cause,
            proposed_change=proposed_change,
            evidence=evidence,
            simulation=self._simulate(
                expected_benefit=expected_benefit,
                implementation_cost=implementation_cost,
                risk_level=risk_level,
                rollback_available=True,
                testable=True,
            ),
            rollback_plan=rollback_plan,
            proposal_fingerprint=fingerprint,
        )

    @staticmethod
    def _fingerprint(
        improvement_type: ImprovementType,
        issue: str,
        affected_components: list[str],
        proposed_change: str,
    ) -> str:
        payload = {
            "type": improvement_type.value,
            "issue": issue.strip().lower(),
            "components": sorted(component.strip().lower() for component in affected_components),
            "proposed_change": proposed_change.strip().lower(),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _proposal_id(fingerprint: str) -> str:
        return f"si-{fingerprint}"

    @staticmethod
    def _simulate(
        *,
        expected_benefit: float,
        implementation_cost: float,
        risk_level: float,
        rollback_available: bool,
        testable: bool,
    ) -> Dict[str, Any]:
        """Create a deterministic, bounded simulation estimate for review."""
        benefit = max(0.0, min(1.0, float(expected_benefit)))
        cost = max(0.0, min(1.0, float(implementation_cost)))
        risk = max(0.0, min(1.0, float(risk_level)))
        confidence = max(0.0, min(1.0, (benefit * 0.5) + ((1.0 - cost) * 0.2) + ((1.0 - risk) * 0.3)))
        return {
            "estimated_impact": benefit,
            "implementation_cost": cost,
            "risk_level": risk,
            "confidence": round(confidence, 3),
            "testable": bool(testable),
            "rollback_available": bool(rollback_available),
            "recommendation": (
                "review"
                if risk >= 0.5 or not rollback_available
                else "candidate"
            ),
        }

    def _generate_performance_improvements(self, context: Dict) -> List[ImprovementProposal]:
        """Generate performance-focused improvements"""
        metrics = context.get("metrics") if isinstance(context, dict) else None
        if isinstance(metrics, dict):
            return [
                proposal
                for proposal in self._generate_from_metrics(metrics)
                if proposal.improvement_type == ImprovementType.PERFORMANCE
            ]
        return []

    def _generate_efficiency_improvements(self, context: Dict) -> List[ImprovementProposal]:
        """Generate efficiency improvements"""
        metrics = context.get("metrics") if isinstance(context, dict) else None
        if isinstance(metrics, dict):
            return [
                proposal
                for proposal in self._generate_from_metrics(metrics)
                if proposal.improvement_type == ImprovementType.EFFICIENCY
            ]
        return []

    def _generate_reliability_improvements(self, context: Dict) -> List[ImprovementProposal]:
        """Generate reliability improvements"""
        metrics = context.get("metrics") if isinstance(context, dict) else None
        if isinstance(metrics, dict):
            return [
                proposal
                for proposal in self._generate_from_metrics(metrics)
                if proposal.improvement_type == ImprovementType.RELIABILITY
            ]
        return []

    def _generate_pattern_improvements(self, context: Dict) -> List[ImprovementProposal]:
        """Generate improvements based on pattern analysis"""
        pattern = context.get("pattern") if isinstance(context, dict) else None
        metrics = context.get("metrics", {}) if isinstance(context, dict) else {}
        if isinstance(pattern, dict) and isinstance(metrics, dict):
            return self._generate_from_pattern(pattern, metrics)
        return []


class SelfImprovementEngine:
    """
    Advanced self-improvement engine that analyzes system performance
    and generates optimization proposals for controlled review.
    """

    def __init__(self, db_path: str = "self_improvement.db"):
        self.db_path = Path(db_path)
        self.metrics_collector = MetricsCollector()
        self.pattern_analyzer = PatternAnalyzer()
        self.improvement_generator = ImprovementGenerator()
        self.active_proposals: Dict[str, ImprovementProposal] = {}
        self.learning_outcomes: List[LearningOutcome] = []
        self.improvement_active = False
        self.improvement_task = None
        self.autonomous_implementation_requested = (
            os.getenv("AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT", "0") == "1"
        )
        self.autonomous_implementation_enabled = False
        # Event loop on which the improvement task was created (for cross-loop shutdown)
        self._task_loop = None  # type: ignore[assignment]
        # Lightweight counters
        self._suppressed_exceptions: int = 0
        self._analysis_cycles: int = 0
        self._init_database()
        self._load_reviewable_proposals()

    def _init_database(self):
        """Initialize self-improvement database"""
        conn = sqlite3.connect(self.db_path)
        try:
            try:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                conn.execute("PRAGMA busy_timeout=3000;")
            except Exception:
                pass
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    context TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS improvement_proposals (
                    proposal_id TEXT PRIMARY KEY,
                    improvement_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    expected_benefit REAL NOT NULL,
                    implementation_cost REAL NOT NULL,
                    risk_level REAL NOT NULL,
                    affected_components TEXT NOT NULL,
                    success_criteria TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    implemented_at TEXT,
                    outcome TEXT
                )
            """
            )
            self._ensure_proposal_columns(conn)

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_outcomes (
                    session_id TEXT PRIMARY KEY,
                    method TEXT NOT NULL,
                    target_component TEXT NOT NULL,
                    improvement_achieved REAL NOT NULL,
                    confidence REAL NOT NULL,
                    learning_data TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS proposal_lifecycle_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposal_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    from_status TEXT,
                    to_status TEXT NOT NULL,
                    actor TEXT,
                    reason TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_proposal_lifecycle_proposal_time
                ON proposal_lifecycle_events(proposal_id, timestamp)
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS system_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    change_description TEXT NOT NULL,
                    performance_impact REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """
            )

            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _ensure_proposal_columns(conn: sqlite3.Connection) -> None:
        """Add proposal metadata columns for existing databases."""
        existing = {
            row[1]
            for row in conn.execute("PRAGMA table_info(improvement_proposals)").fetchall()
        }
        columns = {
            "issue": "TEXT",
            "potential_cause": "TEXT",
            "proposed_change": "TEXT",
            "evidence": "TEXT",
            "simulation": "TEXT",
            "rollback_plan": "TEXT",
            "status_reason": "TEXT",
            "updated_at": "TEXT",
            "proposal_fingerprint": "TEXT",
            "occurrence_count": "INTEGER DEFAULT 1",
            "readiness_status": "TEXT",
            "readiness_reasons": "TEXT",
        }
        for name, column_type in columns.items():
            if name not in existing:
                conn.execute(
                    f"ALTER TABLE improvement_proposals ADD COLUMN {name} {column_type}"
                )

    def _load_reviewable_proposals(self) -> None:
        """Load persisted proposals that are still useful for operator review."""
        reviewable_statuses = {"active", "proposed", "proposed_for_review"}
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT proposal_id, improvement_type, description, expected_benefit,
                       implementation_cost, risk_level, affected_components,
                       success_criteria, status, created_at, issue, potential_cause,
                       proposed_change, evidence, simulation, rollback_plan,
                       status_reason, updated_at, proposal_fingerprint,
                       occurrence_count, readiness_status, readiness_reasons
                FROM improvement_proposals
                WHERE status IN ('active', 'proposed', 'proposed_for_review')
                ORDER BY created_at DESC
                """
            ).fetchall()
        except sqlite3.Error as exc:
            logger.warning("Failed to load persisted self-improvement proposals: %s", exc)
            return
        finally:
            conn.close()

        for row in rows:
            try:
                status = str(row["status"] or "proposed")
                if status not in reviewable_statuses:
                    continue
                improvement_type = ImprovementType(str(row["improvement_type"]))
                created_at = datetime.fromisoformat(str(row["created_at"]))
                proposal = self._proposal_from_row(row, improvement_type, created_at, status)
                self.active_proposals[proposal.proposal_id] = proposal
            except Exception as exc:
                logger.debug(
                    "Skipping malformed self-improvement proposal row: %s", exc
                )

    def _load_proposal_from_db(self, proposal_id: str) -> ImprovementProposal | None:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                """
                SELECT proposal_id, improvement_type, description, expected_benefit,
                       implementation_cost, risk_level, affected_components,
                       success_criteria, status, created_at, issue, potential_cause,
                       proposed_change, evidence, simulation, rollback_plan,
                       status_reason, updated_at, proposal_fingerprint,
                       occurrence_count, readiness_status, readiness_reasons
                FROM improvement_proposals
                WHERE proposal_id = ?
                """,
                (proposal_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return None
        try:
            return self._proposal_from_row(
                row,
                ImprovementType(str(row["improvement_type"])),
                datetime.fromisoformat(str(row["created_at"])),
                str(row["status"] or "proposed"),
            )
        except Exception as exc:
            logger.debug("Failed to load self-improvement proposal %s: %s", proposal_id, exc)
            return None

    def get_proposal_history(
        self,
        proposal_id: str,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return bounded lifecycle history for a proposal."""
        safe_limit = max(1, min(200, int(limit)))
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT proposal_id, event_type, from_status, to_status, actor,
                       reason, timestamp, metadata
                FROM proposal_lifecycle_events
                WHERE proposal_id = ?
                ORDER BY timestamp DESC, id DESC
                LIMIT ?
                """,
                (proposal_id, safe_limit),
            ).fetchall()
        finally:
            conn.close()
        return [
            {
                "proposal_id": str(row["proposal_id"]),
                "event_type": str(row["event_type"]),
                "from_status": row["from_status"],
                "to_status": str(row["to_status"]),
                "actor": row["actor"],
                "reason": row["reason"],
                "timestamp": str(row["timestamp"]),
                "metadata": self._json_dict(row["metadata"]),
            }
            for row in rows
        ]

    def list_learning_outcomes(
        self,
        *,
        proposal_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return bounded, sanitized learning outcomes for review surfaces."""
        safe_limit = max(1, min(200, int(limit)))
        normalized_proposal_id = str(proposal_id or "").strip()
        normalized_status = str(status or "").strip().lower()
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT session_id, method, target_component, improvement_achieved,
                       confidence, learning_data, timestamp
                FROM learning_outcomes
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (max(safe_limit, 1000),),
            ).fetchall()
        finally:
            conn.close()

        outcomes: list[dict[str, Any]] = []
        for row in rows:
            learning_data = self._json_dict(row["learning_data"])
            outcome_proposal_id = str(learning_data.get("proposal_id") or "")
            outcome_status = str(learning_data.get("status") or "").lower()
            if normalized_proposal_id and outcome_proposal_id != normalized_proposal_id:
                continue
            if normalized_status and outcome_status != normalized_status:
                continue
            details_keys = learning_data.get("details_keys")
            if not isinstance(details_keys, list):
                details_keys = []
            outcomes.append(
                {
                    "session_id": str(row["session_id"]),
                    "method": str(row["method"]),
                    "target_component": str(row["target_component"]),
                    "improvement_achieved": float(row["improvement_achieved"]),
                    "confidence": float(row["confidence"]),
                    "timestamp": str(row["timestamp"]),
                    "proposal_id": outcome_proposal_id,
                    "plan_id": str(learning_data.get("plan_id") or ""),
                    "status": outcome_status,
                    "details_keys": sorted(str(key) for key in details_keys),
                }
            )
            if len(outcomes) >= safe_limit:
                break
        return outcomes

    def get_learning_summary(
        self,
        *,
        proposal_id: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Return compact counts for bounded learning outcome review."""
        outcomes = self.list_learning_outcomes(
            proposal_id=proposal_id,
            status=status,
            limit=200,
        )
        by_status: dict[str, int] = {}
        total_improvement = 0.0
        for outcome in outcomes:
            outcome_status = str(outcome.get("status") or "unknown")
            by_status[outcome_status] = by_status.get(outcome_status, 0) + 1
            total_improvement += float(outcome.get("improvement_achieved") or 0.0)
        average = total_improvement / len(outcomes) if outcomes else 0.0
        return {
            "total_outcomes": len(outcomes),
            "by_status": dict(sorted(by_status.items())),
            "average_improvement_achieved": round(average, 4),
        }

    def _count_persisted_learning_outcomes(self) -> int:
        """Return the persisted learning outcome count with an in-memory fallback."""
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute("SELECT COUNT(*) FROM learning_outcomes").fetchone()
            return int(row[0] if row is not None else 0)
        except sqlite3.Error:
            return len(self.learning_outcomes)
        finally:
            conn.close()

    def _proposal_from_row(
        self,
        row: sqlite3.Row,
        improvement_type: ImprovementType,
        created_at: datetime,
        status: str,
    ) -> ImprovementProposal:
        return ImprovementProposal(
            proposal_id=str(row["proposal_id"]),
            improvement_type=improvement_type,
            description=str(row["description"]),
            expected_benefit=float(row["expected_benefit"]),
            implementation_cost=float(row["implementation_cost"]),
            risk_level=float(row["risk_level"]),
            affected_components=self._json_list(row["affected_components"]),
            success_criteria=self._json_list(row["success_criteria"]),
            created_at=created_at,
            status=status,
            issue=str(row["issue"] or ""),
            potential_cause=str(row["potential_cause"] or ""),
            proposed_change=str(row["proposed_change"] or ""),
            evidence=self._json_list(row["evidence"]),
            simulation=self._json_dict(row["simulation"]),
            rollback_plan=str(row["rollback_plan"] or ""),
            status_reason=str(row["status_reason"] or ""),
            updated_at=datetime.fromisoformat(str(row["updated_at"]))
            if row["updated_at"]
            else None,
            proposal_fingerprint=str(row["proposal_fingerprint"] or ""),
            occurrence_count=max(1, int(row["occurrence_count"] or 1)),
            readiness_status=str(row["readiness_status"] or "unknown"),
            readiness_reasons=[
                str(reason) for reason in self._json_list(row["readiness_reasons"])
            ],
        )

    @staticmethod
    def _json_list(value: Any) -> list[Any]:
        if isinstance(value, list):
            return value
        if value is None:
            return []
        try:
            parsed = json.loads(str(value))
        except (TypeError, ValueError, json.JSONDecodeError):
            return []
        return parsed if isinstance(parsed, list) else []

    @staticmethod
    def _json_dict(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if value is None:
            return {}
        try:
            parsed = json.loads(str(value))
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}

    async def start_improvement_cycle(self, loop: asyncio.AbstractEventLoop | None = None):
        """Start the continuous improvement cycle"""
        if self.improvement_active:
            logger.warning("Improvement cycle already active")
            return

        self.improvement_active = True
        # Record the loop this task is created on for correct shutdown
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
        self._task_loop = loop
        if loop is not None:
            self.improvement_task = loop.create_task(self._improvement_loop())
        else:
            # Fallback to current context
            self.improvement_task = asyncio.create_task(self._improvement_loop())

        logger.info("Self-improvement cycle started")

    async def stop_improvement_cycle(self):
        """Stop the improvement cycle"""
        if not self.improvement_active:
            return

        self.improvement_active = False

        if self.improvement_task:
            # Determine the loop that owns the task
            task_loop = None
            try:
                # Python 3.11+ provides get_loop() on Task
                task_loop = self.improvement_task.get_loop()  # type: ignore[attr-defined]
            except Exception:
                task_loop = self._task_loop

            # Cancel the task on its owning loop
            if task_loop is not None:
                try:
                    logger.debug("[SIE] Cancelling improvement task via owning loop")
                    task_loop.call_soon_threadsafe(self.improvement_task.cancel)
                except Exception:
                    logger.debug("[SIE] Owning loop cancel failed; cancelling directly")
                    # Fall back to direct cancel (may not be thread-safe but best-effort)
                    self.improvement_task.cancel()
            else:
                logger.debug("[SIE] Unknown task loop; cancelling directly")
                self.improvement_task.cancel()

            # Await completion when possible to avoid "Task was destroyed" warnings
            try:
                current_loop = None
                try:
                    current_loop = asyncio.get_running_loop()
                except RuntimeError:
                    current_loop = None

                on_current_loop = False
                try:
                    on_current_loop = self.improvement_task in asyncio.all_tasks()
                except Exception:
                    on_current_loop = False

                if on_current_loop or (
                    task_loop is not None and current_loop is not None and task_loop is current_loop
                ):
                    # Same loop: await directly
                    try:
                        logger.debug("[SIE] Awaiting improvement task on same loop")
                        await self.improvement_task
                    except asyncio.CancelledError:
                        pass
                elif task_loop is not None and getattr(task_loop, "is_running", lambda: False)():
                    # Different running loop: wait using a thread-safe done callback
                    # Standard library imports
                    import concurrent.futures as _cf

                    waiter: _cf.Future = _cf.Future()

                    def _mark_done(_):
                        if not waiter.done():
                            waiter.set_result(True)

                    try:
                        logger.debug("[SIE] Waiting for improvement task via thread-safe callback")
                        task_loop.call_soon_threadsafe(
                            self.improvement_task.add_done_callback, _mark_done
                        )  # type: ignore[arg-type]
                        # Also poke the loop in case it's idle
                        task_loop.call_soon_threadsafe(lambda: None)
                        waiter.result(timeout=3)
                    except Exception:
                        pass

                else:
                    # Loop not available/running; best-effort only
                    logger.debug("[SIE] Task loop not running; skipping await")
                    pass
            except Exception:
                pass

        # Clear reference
        self.improvement_task = None

        logger.info("Self-improvement cycle stopped")

    async def _improvement_loop(self):
        """Main improvement loop"""
        try:
            while self.improvement_active:
                await self._analyze_and_improve()
                await asyncio.sleep(300)  # Run every 5 minutes

        except asyncio.CancelledError:
            logger.info("Improvement loop cancelled")
        except Exception as e:
            logger.error(f"Improvement loop error: {e}")
            logger.debug(traceback.format_exc())

    async def _analyze_and_improve(self):
        """Analyze system and generate improvements"""
        try:
            self._analysis_cycles += 1
            # Analyze patterns
            patterns = self.pattern_analyzer.identify_performance_patterns(
                self.metrics_collector.metrics_history
            )

            # Generate metric statistics
            metric_stats = {}
            for name in self.metrics_collector.metrics_history:
                metric_stats[name] = self.metrics_collector.get_metric_statistics(name)

            # Generate improvement proposals
            proposals = self.improvement_generator.generate_improvements(patterns, metric_stats)

            # Process proposals
            for proposal in proposals:
                await self._process_proposal(proposal)

            logger.debug(f"Generated {len(proposals)} improvement proposals")

        except Exception as e:
            logger.error(f"Error in analysis and improvement: {e}")
            self._suppressed_exceptions += 1

    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        # This would integrate with actual system monitoring
        # For now, return sample metrics
        return {
            "response_time": 150.0,
            "cpu_usage": 65.0,
            "memory_usage": 45.0,
            "error_rate": 0.02,
            "throughput": 120.0,
        }

    async def _process_proposal(self, proposal: ImprovementProposal):
        """Process an improvement proposal"""
        # Calculate proposal score
        score = self._calculate_proposal_score(proposal)

        if score > 0.7:  # High-confidence proposals
            self._assess_proposal_readiness(proposal)
            if not proposal.proposal_fingerprint:
                proposal.proposal_fingerprint = self._proposal_fingerprint(proposal)
            if not proposal.proposal_id:
                proposal.proposal_id = f"si-{proposal.proposal_fingerprint}"

            persisted = self._load_proposal_from_db(proposal.proposal_id)
            if persisted is not None and persisted.status not in {
                "active",
                "proposed",
                "proposed_for_review",
            }:
                return

            existing = self.active_proposals.get(proposal.proposal_id)
            if existing is not None:
                existing.expected_benefit = proposal.expected_benefit
                existing.implementation_cost = proposal.implementation_cost
                existing.risk_level = proposal.risk_level
                existing.evidence = proposal.evidence
                existing.simulation = proposal.simulation
                existing.rollback_plan = proposal.rollback_plan
                existing.readiness_status = proposal.readiness_status
                existing.readiness_reasons = proposal.readiness_reasons
                existing.occurrence_count += 1
                existing.updated_at = datetime.now()
                existing.status_reason = "refreshed from repeated analysis"
                await self._store_proposal(existing)
                await self._record_proposal_lifecycle_event(
                    proposal_id=existing.proposal_id,
                    event_type="refreshed",
                    from_status=existing.status,
                    to_status=existing.status,
                    actor="self_improvement_engine",
                    reason=existing.status_reason,
                    metadata={
                        "score": round(score, 3),
                        "occurrence_count": existing.occurrence_count,
                    },
                )
                return

            proposal.status = "active"
            proposal.occurrence_count = max(1, proposal.occurrence_count)
            self.active_proposals[proposal.proposal_id] = proposal
            await self._store_proposal(proposal)
            await self._record_proposal_lifecycle_event(
                proposal_id=proposal.proposal_id,
                event_type="created",
                from_status=None,
                to_status=proposal.status,
                actor="self_improvement_engine",
                reason="proposal generated from analysis",
                metadata={
                    "score": round(score, 3),
                    "improvement_type": proposal.improvement_type.value,
                    "risk_level": proposal.risk_level,
                },
            )

            logger.info(f"High-confidence proposal: {proposal.description} (score: {score:.2f})")

            if self.autonomous_implementation_requested:
                proposal.status_reason = (
                    "autonomous implementation request blocked; Guardian-gated "
                    "controlled execution is required"
                )
                proposal.updated_at = datetime.now()
                await self._store_proposal(proposal)
                await self._record_proposal_lifecycle_event(
                    proposal_id=proposal.proposal_id,
                    event_type="auto_implementation_blocked",
                    from_status=proposal.status,
                    to_status=proposal.status,
                    actor="self_improvement_engine",
                    reason=proposal.status_reason,
                    metadata={"requested_env": "AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT"},
                )

    def _calculate_proposal_score(self, proposal: ImprovementProposal) -> float:
        """Calculate score for improvement proposal"""
        benefit_score = proposal.expected_benefit
        cost_score = 1.0 - proposal.implementation_cost
        risk_score = 1.0 - proposal.risk_level

        # Weighted combination
        return benefit_score * 0.4 + cost_score * 0.3 + risk_score * 0.3

    @staticmethod
    def _assess_proposal_readiness(proposal: ImprovementProposal) -> None:
        """Classify whether a proposal is ready for serious review."""
        reasons: list[str] = []
        simulation = proposal.simulation if isinstance(proposal.simulation, dict) else {}
        rollback_available = bool(simulation.get("rollback_available")) or bool(
            proposal.rollback_plan
        )
        testable = bool(simulation.get("testable"))
        try:
            confidence = float(simulation.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0

        if not rollback_available:
            reasons.append("rollback_missing")
        if not testable:
            reasons.append("not_testable")
        if proposal.risk_level >= 0.67:
            reasons.append("risk_high")
        if len(proposal.evidence) < 2:
            reasons.append("evidence_sparse")
        if confidence < 0.6:
            reasons.append("confidence_low")

        blocking = {"rollback_missing", "not_testable", "risk_high"}
        if blocking.intersection(reasons):
            readiness = "blocked"
        elif reasons:
            readiness = "needs_evidence"
        else:
            readiness = "candidate"

        proposal.readiness_status = readiness
        proposal.readiness_reasons = reasons or ["ready_for_review"]

    @staticmethod
    def _proposal_fingerprint(proposal: ImprovementProposal) -> str:
        payload = {
            "type": proposal.improvement_type.value,
            "issue": proposal.issue.strip().lower(),
            "components": sorted(
                component.strip().lower()
                for component in proposal.affected_components
            ),
            "proposed_change": proposal.proposed_change.strip().lower(),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    async def _implement_proposal(self, proposal: ImprovementProposal):
        """Implement an improvement proposal"""
        logger.info(f"Implementing proposal: {proposal.description}")

        try:
            # Record implementation
            proposal.status = "implementing"

            # Simulate implementation (in real system, this would apply actual changes)
            await asyncio.sleep(1)

            # Create learning outcome
            outcome = LearningOutcome(
                session_id=str(uuid.uuid4()),
                method=LearningMethod.REINFORCEMENT,
                target_component=",".join(proposal.affected_components),
                improvement_achieved=proposal.expected_benefit,
                confidence=0.8,
                learning_data={
                    "proposal_id": proposal.proposal_id,
                    "implementation_method": "automatic",
                    "success_criteria": proposal.success_criteria,
                },
                timestamp=datetime.now(),
            )

            self.learning_outcomes.append(outcome)
            await self._store_learning_outcome(outcome)

            proposal.status = "implemented"
            logger.info(f"Successfully implemented: {proposal.description}")

        except Exception as e:
            proposal.status = "failed"
            logger.error(f"Failed to implement proposal {proposal.proposal_id}: {e}")

    async def record_proposal_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Record a downstream proposal result without executing any changes."""
        proposal_id = str(result.get("proposal_id") or "").strip()
        status = self._normalize_result_status(result.get("status"))
        details = result.get("details") if isinstance(result.get("details"), dict) else {}
        details_keys = self._bounded_detail_keys(details)
        if not proposal_id:
            return {"status": "error", "error": "proposal_id required"}
        if status is None:
            return {
                "status": "error",
                "error": "invalid proposal result status",
                "allowed_statuses": sorted(_VALID_PROPOSAL_RESULT_STATUSES),
            }

        proposal = self.active_proposals.get(proposal_id)
        if proposal is not None:
            previous_status = proposal.status
            proposal.status = status
            proposal.status_reason = str(details.get("reason") or "")[:500]
            proposal.updated_at = datetime.now()
            await self._store_proposal(proposal)
            await self._record_proposal_lifecycle_event(
                proposal_id=proposal_id,
                event_type="result_recorded",
                from_status=previous_status,
                to_status=status,
                actor="controlled_execution",
                reason=proposal.status_reason,
                metadata={
                    "plan_id": str(result.get("plan_id") or ""),
                    "details_keys": details_keys,
                },
            )

        improvement_achieved = details.get("improvement_achieved")
        try:
            achieved = float(improvement_achieved)
        except (TypeError, ValueError):
            achieved = 1.0 if status == "accepted" else 0.0

        target_component = (
            ",".join(proposal.affected_components)
            if proposal is not None
            else str(details.get("type") or "unknown")
        )
        outcome = LearningOutcome(
            session_id=str(uuid.uuid4()),
            method=LearningMethod.REINFORCEMENT,
            target_component=target_component,
            improvement_achieved=max(0.0, min(1.0, achieved)),
            confidence=1.0 if status == "accepted" else 0.5,
            learning_data={
                "proposal_id": proposal_id,
                "plan_id": str(result.get("plan_id") or ""),
                "status": status,
                "details_keys": details_keys,
            },
            timestamp=datetime.now(),
        )
        self.learning_outcomes.append(outcome)
        await self._store_learning_outcome(outcome)
        return {
            "status": "ok",
            "proposal_id": proposal_id,
            "recorded_status": status,
        }

    @staticmethod
    def _normalize_result_status(value: Any) -> str | None:
        status = str(value or "").strip().lower()
        aliases = {
            "applied": "accepted",
            "success": "accepted",
            "succeeded": "accepted",
            "denied": "rejected",
            "blocked": "rejected",
            "failure": "failed",
            "rollback": "rolled_back",
            "manual": "manual_required",
        }
        status = aliases.get(status, status)
        return status if status in _VALID_PROPOSAL_RESULT_STATUSES else None

    @staticmethod
    def _bounded_detail_keys(details: dict[str, Any]) -> list[str]:
        keys = sorted(str(key)[:120] for key in details.keys())
        return keys[:50]

    def record_performance_metric(
        self, name: str, value: float, unit: str, context: Dict[str, Any] | None = None
    ):
        """Record a performance metric for analysis"""
        self.metrics_collector.record_metric(name, value, unit, context)

        # Store in database
        asyncio.create_task(self._store_metric(name, value, unit, context))

    def analyze_interaction(self, interaction_data: Dict[str, Any]):
        """
        Analyzes a single interaction to identify potential immediate improvements
        or gather data for long-term learning.
        """
        # This is a hook for more immediate, per-interaction analysis.
        # For now, we can log the interaction for future offline analysis
        # or trigger a micro-analysis task.
        logger.debug(f"Analyzing interaction: {interaction_data.get('id', 'unknown')}")

        # Example: if response confidence was low, flag for review.
        if interaction_data.get("confidence", 1.0) < 0.6:
            proposal = ImprovementProposal(
                proposal_id=f"review-{interaction_data.get('id', uuid.uuid4())}",
                improvement_type=ImprovementType.ACCURACY,
                description=f"Review low-confidence interaction for query: '{interaction_data.get('query', '...')[:50]}...'",
                expected_benefit=0.1,
                implementation_cost=0.1,
                risk_level=0.0,
                affected_components=[
                    "lyrixa_chat",
                    interaction_data.get("path_used", "unknown"),
                ],
                success_criteria=["Manual review provides insight for tuning."],
                created_at=datetime.now(),
                status="proposed_for_review",
            )
            # Store this special proposal
            asyncio.create_task(self._store_proposal(proposal))

    def get_improvement_status(self) -> Dict[str, Any]:
        """Get current improvement system status"""
        active_count = len([p for p in self.active_proposals.values() if p.status == "active"])
        implemented_count = len(
            [p for p in self.active_proposals.values() if p.status == "implemented"]
        )

        return {
            "improvement_active": self.improvement_active,
            "total_proposals": len(self.active_proposals),
            "active_proposals": active_count,
            "implemented_proposals": implemented_count,
            "learning_outcomes": self._count_persisted_learning_outcomes(),
            "tracked_metrics": len(self.metrics_collector.metrics_history),
            "last_analysis": datetime.now().isoformat(),
            "analysis_cycles": self._analysis_cycles,
            "suppressed_exceptions": self._suppressed_exceptions,
            "autonomous_implementation_enabled": self.autonomous_implementation_enabled,
            "autonomous_implementation_requested": self.autonomous_implementation_requested,
            "implementation_authority": "guardian_controlled_execution",
            "review_summary": self.get_review_summary(),
            "learning_summary": self.get_learning_summary(),
        }

    def list_active_proposals(
        self,
        *,
        status: str | None = None,
        improvement_type: str | None = None,
        readiness_status: str | None = None,
        max_risk: float | None = None,
        min_confidence: float | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return reviewable proposals in a JSON-safe, read-only representation."""
        safe_limit = max(1, min(500, int(limit)))
        proposals = sorted(
            self.active_proposals.values(),
            key=lambda proposal: proposal.created_at,
            reverse=True,
        )
        filtered: list[ImprovementProposal] = []
        for proposal in proposals:
            if status and proposal.status != status:
                continue
            if improvement_type and proposal.improvement_type.value != improvement_type:
                continue
            if readiness_status and proposal.readiness_status != readiness_status:
                continue
            if max_risk is not None and proposal.risk_level > max_risk:
                continue
            confidence = proposal.simulation.get("confidence")
            if min_confidence is not None:
                try:
                    if float(confidence) < min_confidence:
                        continue
                except (TypeError, ValueError):
                    continue
            filtered.append(proposal)
            if len(filtered) >= safe_limit:
                break
        return [self._proposal_to_dict(proposal) for proposal in filtered]

    def get_review_summary(self) -> dict[str, Any]:
        """Return compact review-queue counts for operators."""
        by_status: dict[str, int] = {}
        by_type: dict[str, int] = {}
        by_readiness: dict[str, int] = {}
        risk_bands = {"low": 0, "medium": 0, "high": 0}
        for proposal in self.active_proposals.values():
            by_status[proposal.status] = by_status.get(proposal.status, 0) + 1
            ptype = proposal.improvement_type.value
            by_type[ptype] = by_type.get(ptype, 0) + 1
            readiness = proposal.readiness_status or "unknown"
            by_readiness[readiness] = by_readiness.get(readiness, 0) + 1
            if proposal.risk_level >= 0.67:
                risk_bands["high"] += 1
            elif proposal.risk_level >= 0.34:
                risk_bands["medium"] += 1
            else:
                risk_bands["low"] += 1
        return {
            "total_reviewable": len(self.active_proposals),
            "by_status": dict(sorted(by_status.items())),
            "by_type": dict(sorted(by_type.items())),
            "by_readiness": dict(sorted(by_readiness.items())),
            "risk_bands": risk_bands,
        }

    def get_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        """Return one active proposal by ID, if it is still reviewable."""
        proposal = self.active_proposals.get(proposal_id)
        return self._proposal_to_dict(proposal) if proposal is not None else None

    async def dismiss_proposal(
        self,
        proposal_id: str,
        *,
        reason: str = "",
        actor: str = "",
    ) -> dict[str, Any]:
        """Dismiss a reviewable proposal without applying it."""
        proposal = self.active_proposals.get(proposal_id) or self._load_proposal_from_db(
            proposal_id
        )
        if proposal is None:
            return {"status": "not_found", "proposal_id": proposal_id}
        if proposal.status not in {"active", "proposed", "proposed_for_review"}:
            return {
                "status": "invalid_state",
                "proposal_id": proposal_id,
                "current_status": proposal.status,
            }
        proposal.status = "dismissed"
        proposal.status_reason = reason[:500]
        proposal.updated_at = datetime.now()
        await self._store_proposal(proposal)
        await self._record_proposal_lifecycle_event(
            proposal_id=proposal_id,
            event_type="dismissed",
            from_status="active",
            to_status=proposal.status,
            actor=actor,
            reason=proposal.status_reason,
            metadata={},
        )
        self.active_proposals.pop(proposal_id, None)
        return {
            "status": "ok",
            "proposal_id": proposal_id,
            "proposal_status": proposal.status,
            "actor": actor,
        }

    async def reopen_proposal(
        self,
        proposal_id: str,
        *,
        reason: str = "",
        actor: str = "",
    ) -> dict[str, Any]:
        """Reopen a dismissed proposal for review."""
        proposal = self._load_proposal_from_db(proposal_id)
        if proposal is None:
            return {"status": "not_found", "proposal_id": proposal_id}
        if proposal.status != "dismissed":
            return {
                "status": "invalid_state",
                "proposal_id": proposal_id,
                "current_status": proposal.status,
            }
        proposal.status = "active"
        proposal.status_reason = reason[:500]
        proposal.updated_at = datetime.now()
        await self._store_proposal(proposal)
        await self._record_proposal_lifecycle_event(
            proposal_id=proposal_id,
            event_type="reopened",
            from_status="dismissed",
            to_status=proposal.status,
            actor=actor,
            reason=proposal.status_reason,
            metadata={},
        )
        self.active_proposals[proposal_id] = proposal
        return {
            "status": "ok",
            "proposal_id": proposal_id,
            "proposal_status": proposal.status,
            "actor": actor,
        }

    @staticmethod
    def _proposal_to_dict(proposal: ImprovementProposal) -> dict[str, Any]:
        return {
            "proposal_id": proposal.proposal_id,
            "improvement_type": proposal.improvement_type.value,
            "description": proposal.description,
            "expected_benefit": proposal.expected_benefit,
            "implementation_cost": proposal.implementation_cost,
            "risk_level": proposal.risk_level,
            "affected_components": list(proposal.affected_components),
            "success_criteria": list(proposal.success_criteria),
            "created_at": proposal.created_at.isoformat(),
            "status": proposal.status,
            "issue": proposal.issue,
            "potential_cause": proposal.potential_cause,
            "proposed_change": proposal.proposed_change,
            "evidence": list(proposal.evidence),
            "simulation": dict(proposal.simulation),
            "rollback_plan": proposal.rollback_plan,
            "status_reason": proposal.status_reason,
            "updated_at": proposal.updated_at.isoformat()
            if proposal.updated_at is not None
            else None,
            "proposal_fingerprint": proposal.proposal_fingerprint,
            "occurrence_count": proposal.occurrence_count,
            "readiness_status": proposal.readiness_status,
            "readiness_reasons": list(proposal.readiness_reasons),
        }

    async def _record_proposal_lifecycle_event(
        self,
        *,
        proposal_id: str,
        event_type: str,
        from_status: str | None,
        to_status: str,
        actor: str,
        reason: str,
        metadata: dict[str, Any],
    ) -> None:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO proposal_lifecycle_events
                (proposal_id, event_type, from_status, to_status, actor, reason,
                 timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proposal_id,
                    event_type,
                    from_status,
                    to_status,
                    actor[:200],
                    reason[:500],
                    datetime.now().isoformat(),
                    json.dumps(metadata, sort_keys=True),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def export_internal_metrics(
        self,
    ) -> Dict[str, Any]:  # pragma: no cover - simple accessor
        return {
            "suppressed_exceptions": self._suppressed_exceptions,
            "analysis_cycles": self._analysis_cycles,
            "tracked_metrics": len(self.metrics_collector.metrics_history),
        }

    def get_metric_trends(self) -> Dict[str, Dict[str, Any]]:
        """Get trends for all tracked metrics"""
        trends = {}

        for metric_name in self.metrics_collector.metrics_history:
            trend_value, trend_direction = self.metrics_collector.get_metric_trend(metric_name)
            stats = self.metrics_collector.get_metric_statistics(metric_name)

            trends[metric_name] = {
                "trend_direction": trend_direction,
                "trend_value": trend_value,
                "statistics": stats,
            }

        return trends

    async def _store_metric(
        self, name: str, value: float, unit: str, context: Dict[str, Any] | None
    ):
        """Store metric in database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO performance_metrics (name, value, unit, timestamp, context)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    name,
                    value,
                    unit,
                    datetime.now().isoformat(),
                    json.dumps(context) if context else None,
                ),
            )
            # Helpful indexes for common queries
            try:
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_perf_name_time ON performance_metrics(name, timestamp);"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_proposal_status ON improvement_proposals(status);"
                )
            except Exception:
                pass
            conn.commit()
        finally:
            conn.close()

    async def _store_proposal(self, proposal: ImprovementProposal):
        """Store improvement proposal in database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO improvement_proposals
                (proposal_id, improvement_type, description, expected_benefit,
                 implementation_cost, risk_level, affected_components, success_criteria,
                 status, created_at, issue, potential_cause, proposed_change, evidence,
                 simulation, rollback_plan, status_reason, updated_at,
                 proposal_fingerprint, occurrence_count, readiness_status,
                 readiness_reasons)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    proposal.proposal_id,
                    proposal.improvement_type.value,
                    proposal.description,
                    proposal.expected_benefit,
                    proposal.implementation_cost,
                    proposal.risk_level,
                    json.dumps(proposal.affected_components),
                    json.dumps(proposal.success_criteria),
                    proposal.status,
                    proposal.created_at.isoformat(),
                    proposal.issue,
                    proposal.potential_cause,
                    proposal.proposed_change,
                    json.dumps(proposal.evidence),
                    json.dumps(proposal.simulation),
                    proposal.rollback_plan,
                    proposal.status_reason,
                    proposal.updated_at.isoformat()
                    if proposal.updated_at is not None
                    else None,
                    proposal.proposal_fingerprint,
                    proposal.occurrence_count,
                    proposal.readiness_status,
                    json.dumps(proposal.readiness_reasons),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    async def _store_learning_outcome(self, outcome: LearningOutcome):
        """Store learning outcome in database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO learning_outcomes
                (session_id, method, target_component, improvement_achieved,
                 confidence, learning_data, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    outcome.session_id,
                    outcome.method.value,
                    outcome.target_component,
                    outcome.improvement_achieved,
                    outcome.confidence,
                    json.dumps(outcome.learning_data, default=str),
                    outcome.timestamp.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()


# Testing function
async def test_self_improvement_engine():
    """Test the self-improvement engine"""
    engine = SelfImprovementEngine()

    # Start improvement cycle
    await engine.start_improvement_cycle()

    # Simulate recording metrics
    # Standard library imports
    import random

    for _ in range(20):
        engine.record_performance_metric("response_time", 100 + random.uniform(-20, 50), "ms")
        engine.record_performance_metric("cpu_usage", 60 + random.uniform(-10, 30), "percent")
        await asyncio.sleep(0.1)

    # Wait for analysis
    await asyncio.sleep(2)

    # Get status
    status = engine.get_improvement_status()
    print("Improvement Status:")
    print(json.dumps(status, indent=2))

    # Get metric trends
    trends = engine.get_metric_trends()
    print("\nMetric Trends:")
    print(json.dumps(trends, indent=2, default=str))

    # Stop improvement cycle
    await engine.stop_improvement_cycle()


if __name__ == "__main__":
    asyncio.run(test_self_improvement_engine())
