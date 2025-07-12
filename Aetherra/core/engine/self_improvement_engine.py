"""
Aetherra Self-Improvement Engine
Continuous learning and system optimization capabilities.
"""

import asyncio
import json
import logging
import sqlite3
import traceback
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


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

    def get_metric_trend(self, name: str, window_hours: int = 24) -> Tuple[float, str]:
        """Get trend for a metric over specified time window"""
        if name not in self.metrics_history:
            return 0.0, "no_data"

        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent_metrics = [m for m in self.metrics_history[name] if m.timestamp > cutoff]

        if len(recent_metrics) < 2:
            return 0.0, "insufficient_data"

        # Calculate trend using linear regression
        timestamps = [
            (m.timestamp - recent_metrics[0].timestamp).total_seconds()
            for m in recent_metrics
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

    def get_metric_statistics(
        self, name: str, window_hours: int = 24
    ) -> Dict[str, float]:
        """Get statistics for a metric"""
        if name not in self.metrics_history:
            return {}

        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent_metrics = [
            m.value for m in self.metrics_history[name] if m.timestamp > cutoff
        ]

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
            correlation_pattern = self._analyze_correlations(
                metric_name, metric_list, metrics
            )
            if correlation_pattern:
                patterns.append(correlation_pattern)

        return patterns

    def _analyze_temporal_pattern(
        self, name: str, metrics: List[PerformanceMetric]
    ) -> Dict | None:
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
            correlation = np.corrcoef(normalized[:-lag], normalized[lag:])[0, 1]

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

        return np.corrcoef(values1, values2)[0, 1] if len(values1) > 1 else 0.0


class ImprovementGenerator:
    """Generates improvement proposals based on analysis"""

    def __init__(self):
        self.improvement_rules = self._init_improvement_rules()

    def _init_improvement_rules(self) -> Dict[str, callable]:
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
            proposal = ImprovementProposal(
                proposal_id=str(uuid.uuid4()),
                improvement_type=ImprovementType.PERFORMANCE,
                description=f"Address declining performance in {pattern['metric']}",
                expected_benefit=0.3,
                implementation_cost=0.5,
                risk_level=0.2,
                affected_components=[pattern["metric"]],
                success_criteria=[f"Reverse negative trend in {pattern['metric']}"],
                created_at=datetime.now(),
            )
            proposals.append(proposal)

        elif pattern["type"] == "cyclical":
            # Optimize cyclical patterns
            proposal = ImprovementProposal(
                proposal_id=str(uuid.uuid4()),
                improvement_type=ImprovementType.EFFICIENCY,
                description=f"Optimize cyclical pattern in {pattern['metric']}",
                expected_benefit=0.2,
                implementation_cost=0.3,
                risk_level=0.1,
                affected_components=[pattern["metric"]],
                success_criteria=[f"Reduce amplitude of cycles in {pattern['metric']}"],
                created_at=datetime.now(),
            )
            proposals.append(proposal)

        return proposals

    def _generate_from_metrics(
        self, metrics: Dict[str, Any]
    ) -> List[ImprovementProposal]:
        """Generate improvements from metric analysis"""
        proposals = []

        # Example: CPU usage consistently high
        if "cpu_usage" in metrics:
            cpu_stats = metrics["cpu_usage"]
            if cpu_stats.get("mean", 0) > 80:
                proposal = ImprovementProposal(
                    proposal_id=str(uuid.uuid4()),
                    improvement_type=ImprovementType.PERFORMANCE,
                    description="Optimize CPU usage - consistently high utilization detected",
                    expected_benefit=0.4,
                    implementation_cost=0.6,
                    risk_level=0.3,
                    affected_components=["cpu_scheduler", "process_manager"],
                    success_criteria=["Reduce average CPU usage to below 70%"],
                    created_at=datetime.now(),
                )
                proposals.append(proposal)

        return proposals

    def _generate_performance_improvements(
        self, context: Dict
    ) -> List[ImprovementProposal]:
        """Generate performance-focused improvements"""
        # Implementation for performance improvements
        return []

    def _generate_efficiency_improvements(
        self, context: Dict
    ) -> List[ImprovementProposal]:
        """Generate efficiency improvements"""
        # Implementation for efficiency improvements
        return []

    def _generate_reliability_improvements(
        self, context: Dict
    ) -> List[ImprovementProposal]:
        """Generate reliability improvements"""
        # Implementation for reliability improvements
        return []

    def _generate_pattern_improvements(
        self, context: Dict
    ) -> List[ImprovementProposal]:
        """Generate improvements based on pattern analysis"""
        # Implementation for pattern-based improvements
        return []


class SelfImprovementEngine:
    """
    Advanced self-improvement engine that analyzes system performance
    and automatically generates optimization proposals
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
        self._init_database()

    def _init_database(self):
        """Initialize self-improvement database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    context TEXT
                )
            """)

            conn.execute("""
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
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_outcomes (
                    session_id TEXT PRIMARY KEY,
                    method TEXT NOT NULL,
                    target_component TEXT NOT NULL,
                    improvement_achieved REAL NOT NULL,
                    confidence REAL NOT NULL,
                    learning_data TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    change_description TEXT NOT NULL,
                    performance_impact REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)

            conn.commit()
        finally:
            conn.close()

    async def start_improvement_cycle(self):
        """Start the continuous improvement cycle"""
        if self.improvement_active:
            logger.warning("Improvement cycle already active")
            return

        self.improvement_active = True
        self.improvement_task = asyncio.create_task(self._improvement_loop())

        logger.info("Self-improvement cycle started")

    async def stop_improvement_cycle(self):
        """Stop the improvement cycle"""
        if not self.improvement_active:
            return

        self.improvement_active = False

        if self.improvement_task:
            self.improvement_task.cancel()
            try:
                await self.improvement_task
            except asyncio.CancelledError:
                pass

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
            # Analyze patterns
            patterns = self.pattern_analyzer.identify_performance_patterns(
                self.metrics_collector.metrics_history
            )

            # Generate metric statistics
            metric_stats = {}
            for name in self.metrics_collector.metrics_history:
                metric_stats[name] = self.metrics_collector.get_metric_statistics(name)

            # Generate improvement proposals
            proposals = self.improvement_generator.generate_improvements(
                patterns, metric_stats
            )

            # Process proposals
            for proposal in proposals:
                await self._process_proposal(proposal)

            logger.debug(f"Generated {len(proposals)} improvement proposals")

        except Exception as e:
            logger.error(f"Error in analysis and improvement: {e}")

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
            self.active_proposals[proposal.proposal_id] = proposal
            await self._store_proposal(proposal)

            logger.info(
                f"High-confidence proposal: {proposal.description} (score: {score:.2f})"
            )

            # Auto-implement low-risk, high-benefit proposals
            if proposal.risk_level < 0.3 and proposal.expected_benefit > 0.5:
                await self._implement_proposal(proposal)

    def _calculate_proposal_score(self, proposal: ImprovementProposal) -> float:
        """Calculate score for improvement proposal"""
        benefit_score = proposal.expected_benefit
        cost_score = 1.0 - proposal.implementation_cost
        risk_score = 1.0 - proposal.risk_level

        # Weighted combination
        return benefit_score * 0.4 + cost_score * 0.3 + risk_score * 0.3

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

    def record_performance_metric(
        self, name: str, value: float, unit: str, context: Dict[str, Any] | None = None
    ):
        """Record a performance metric for analysis"""
        self.metrics_collector.record_metric(name, value, unit, context)

        # Store in database
        asyncio.create_task(self._store_metric(name, value, unit, context))

    def get_improvement_status(self) -> Dict[str, Any]:
        """Get current improvement system status"""
        active_count = len(
            [p for p in self.active_proposals.values() if p.status == "active"]
        )
        implemented_count = len(
            [p for p in self.active_proposals.values() if p.status == "implemented"]
        )

        return {
            "improvement_active": self.improvement_active,
            "total_proposals": len(self.active_proposals),
            "active_proposals": active_count,
            "implemented_proposals": implemented_count,
            "learning_outcomes": len(self.learning_outcomes),
            "tracked_metrics": len(self.metrics_collector.metrics_history),
            "last_analysis": datetime.now().isoformat(),
        }

    def get_metric_trends(self) -> Dict[str, Dict[str, Any]]:
        """Get trends for all tracked metrics"""
        trends = {}

        for metric_name in self.metrics_collector.metrics_history:
            trend_value, trend_direction = self.metrics_collector.get_metric_trend(
                metric_name
            )
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
                 status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    import random

    for i in range(20):
        engine.record_performance_metric(
            "response_time", 100 + random.uniform(-20, 50), "ms"
        )
        engine.record_performance_metric(
            "cpu_usage", 60 + random.uniform(-10, 30), "percent"
        )
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
