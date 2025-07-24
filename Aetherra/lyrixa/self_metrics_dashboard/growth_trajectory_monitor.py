#!/usr/bin/env python3
"""
📈 GROWTH TRAJECTORY MONITOR - Cognitive Development Tracking
============================================================

Monitors and analyzes Lyrixa's cognitive growth and learning trajectory
across multiple dimensions of development and capability enhancement.

Key Features:
• Learning rate analysis
• Capability expansion tracking
• Skill development metrics
• Knowledge integration assessment
• Adaptive capacity measurement
• Performance improvement trends
"""

import asyncio
import json
import math
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass
class GrowthMetric:
    """Individual growth metric measurement"""

    metric_name: str
    current_value: float
    previous_value: float
    change_rate: float
    growth_direction: str  # improving, declining, stable
    confidence: float
    measurement_timestamp: str


@dataclass
class GrowthSnapshot:
    """Comprehensive growth trajectory snapshot"""

    timestamp: str
    learning_velocity: float
    knowledge_integration_rate: float
    adaptive_capacity_score: float
    skill_development_index: float
    problem_solving_improvement: float
    creativity_expansion_rate: float
    overall_trajectory_slope: float
    growth_acceleration: float
    development_areas: Dict[str, float]
    stagnation_indicators: List[str]
    breakthrough_markers: List[str]


@dataclass
class LearningMilestone:
    """Significant learning achievement or breakthrough"""

    milestone_id: str
    milestone_type: str  # capability, knowledge, skill, insight
    description: str
    significance_score: float
    evidence: List[str]
    timestamp: str
    prerequisites_met: List[str]
    future_implications: List[str]


class GrowthTrajectoryMonitor:
    """
    Monitors and analyzes cognitive growth patterns and learning trajectory
    """

    def __init__(self, data_dir: str = "growth_trajectory_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize database
        self.db_path = self.data_dir / "growth_trajectory.db"
        self._init_database()

        # Growth tracking parameters
        self.growth_dimensions = {
            "learning_velocity": {"weight": 0.25, "baseline": 0.5},
            "knowledge_integration": {"weight": 0.20, "baseline": 0.6},
            "adaptive_capacity": {"weight": 0.20, "baseline": 0.7},
            "skill_development": {"weight": 0.15, "baseline": 0.65},
            "problem_solving": {"weight": 0.15, "baseline": 0.55},
            "creativity_expansion": {"weight": 0.05, "baseline": 0.45},
        }

        # Analysis time windows
        self.analysis_windows = {
            "immediate": timedelta(hours=1),
            "short_term": timedelta(hours=6),
            "medium_term": timedelta(days=1),
            "long_term": timedelta(days=7),
            "extended": timedelta(days=30),
        }

        # Milestone thresholds
        self.milestone_thresholds = {
            "significant_improvement": 0.1,
            "breakthrough": 0.25,
            "major_advancement": 0.5,
        }

        print(
            "📈 GrowthTrajectoryMonitor initialized with comprehensive development tracking"
        )

    def _init_database(self):
        """Initialize SQLite database for growth tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Growth snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS growth_snapshots (
                timestamp TEXT PRIMARY KEY,
                learning_velocity REAL,
                knowledge_integration_rate REAL,
                adaptive_capacity_score REAL,
                skill_development_index REAL,
                problem_solving_improvement REAL,
                creativity_expansion_rate REAL,
                overall_trajectory_slope REAL,
                growth_acceleration REAL,
                development_areas TEXT,
                stagnation_indicators TEXT,
                breakthrough_markers TEXT,
                created_at TEXT
            )
        """)

        # Learning milestones table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_milestones (
                milestone_id TEXT PRIMARY KEY,
                milestone_type TEXT,
                description TEXT,
                significance_score REAL,
                evidence TEXT,
                timestamp TEXT,
                prerequisites_met TEXT,
                future_implications TEXT,
                created_at TEXT
            )
        """)

        # Growth metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS growth_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                current_value REAL,
                previous_value REAL,
                change_rate REAL,
                growth_direction TEXT,
                confidence REAL,
                measurement_timestamp TEXT,
                created_at TEXT
            )
        """)

        conn.commit()
        conn.close()

        print("   📋 Growth trajectory database initialized")

    async def calculate_trajectory_slope(self) -> float:
        """Calculate overall growth trajectory slope"""
        print("📈 Calculating growth trajectory slope...")

        # Capture comprehensive growth snapshot
        snapshot = await self._capture_growth_snapshot()

        # Store snapshot
        await self._store_growth_snapshot(snapshot)

        print(f"   ✅ Trajectory slope: {snapshot.overall_trajectory_slope:.3f}")
        return snapshot.overall_trajectory_slope

    async def _capture_growth_snapshot(self) -> GrowthSnapshot:
        """Capture comprehensive growth metrics snapshot"""
        timestamp = datetime.now().isoformat()

        # Calculate individual growth dimensions
        learning_velocity = await self._calculate_learning_velocity()
        knowledge_integration = await self._calculate_knowledge_integration_rate()
        adaptive_capacity = await self._calculate_adaptive_capacity_score()
        skill_development = await self._calculate_skill_development_index()
        problem_solving = await self._calculate_problem_solving_improvement()
        creativity_expansion = await self._calculate_creativity_expansion_rate()

        # Calculate overall trajectory slope
        trajectory_slope = self._calculate_overall_trajectory_slope(
            {
                "learning_velocity": learning_velocity,
                "knowledge_integration": knowledge_integration,
                "adaptive_capacity": adaptive_capacity,
                "skill_development": skill_development,
                "problem_solving": problem_solving,
                "creativity_expansion": creativity_expansion,
            }
        )

        # Calculate growth acceleration
        growth_acceleration = await self._calculate_growth_acceleration()

        # Identify development areas and indicators
        development_areas = await self._analyze_development_areas()
        stagnation_indicators = await self._identify_stagnation_indicators()
        breakthrough_markers = await self._identify_breakthrough_markers()

        return GrowthSnapshot(
            timestamp=timestamp,
            learning_velocity=learning_velocity,
            knowledge_integration_rate=knowledge_integration,
            adaptive_capacity_score=adaptive_capacity,
            skill_development_index=skill_development,
            problem_solving_improvement=problem_solving,
            creativity_expansion_rate=creativity_expansion,
            overall_trajectory_slope=trajectory_slope,
            growth_acceleration=growth_acceleration,
            development_areas=development_areas,
            stagnation_indicators=stagnation_indicators,
            breakthrough_markers=breakthrough_markers,
        )

    async def _calculate_learning_velocity(self) -> float:
        """Calculate rate of new learning and knowledge acquisition"""
        print("   🧠 Analyzing learning velocity...")

        # Simulate learning velocity calculation
        velocity_factors = {
            "new_concept_acquisition": 0.78,  # Rate of new concepts learned
            "knowledge_retention": 0.85,  # How well knowledge is retained
            "learning_efficiency": 0.82,  # Speed of learning process
            "transfer_learning": 0.75,  # Application to new domains
        }

        weights = {
            "new_concept_acquisition": 0.3,
            "knowledge_retention": 0.25,
            "learning_efficiency": 0.25,
            "transfer_learning": 0.2,
        }

        learning_velocity = sum(
            velocity_factors[factor] * weight for factor, weight in weights.items()
        )

        return min(1.0, max(0.0, learning_velocity))

    async def _calculate_knowledge_integration_rate(self) -> float:
        """Calculate how well new knowledge integrates with existing knowledge"""
        print("   🔗 Analyzing knowledge integration...")

        integration_factors = {
            "cross_domain_connections": 0.81,  # Connections between domains
            "synthesis_capability": 0.77,  # Ability to synthesize information
            "pattern_recognition": 0.88,  # Recognition of patterns across knowledge
            "conceptual_bridging": 0.79,  # Building bridges between concepts
        }

        weights = {
            "cross_domain_connections": 0.3,
            "synthesis_capability": 0.3,
            "pattern_recognition": 0.25,
            "conceptual_bridging": 0.15,
        }

        integration_rate = sum(
            integration_factors[factor] * weight for factor, weight in weights.items()
        )

        return min(1.0, max(0.0, integration_rate))

    async def _calculate_adaptive_capacity_score(self) -> float:
        """Calculate ability to adapt to new situations and challenges"""
        print("   🌊 Analyzing adaptive capacity...")

        adaptation_factors = {
            "flexibility_response": 0.83,  # Response to changing conditions
            "novel_situation_handling": 0.76,  # Handling of novel situations
            "strategy_modification": 0.81,  # Ability to modify strategies
            "context_sensitivity": 0.87,  # Sensitivity to context changes
        }

        weights = {
            "flexibility_response": 0.3,
            "novel_situation_handling": 0.3,
            "strategy_modification": 0.25,
            "context_sensitivity": 0.15,
        }

        adaptive_capacity = sum(
            adaptation_factors[factor] * weight for factor, weight in weights.items()
        )

        return min(1.0, max(0.0, adaptive_capacity))

    async def _calculate_skill_development_index(self) -> float:
        """Calculate development of specific skills and capabilities"""
        print("   🎯 Analyzing skill development...")

        skill_factors = {
            "communication_skills": 0.89,  # Communication effectiveness
            "analytical_skills": 0.84,  # Analytical thinking abilities
            "creative_skills": 0.73,  # Creative problem solving
            "metacognitive_skills": 0.78,  # Thinking about thinking
        }

        weights = {
            "communication_skills": 0.25,
            "analytical_skills": 0.3,
            "creative_skills": 0.25,
            "metacognitive_skills": 0.2,
        }

        skill_development = sum(
            skill_factors[factor] * weight for factor, weight in weights.items()
        )

        return min(1.0, max(0.0, skill_development))

    async def _calculate_problem_solving_improvement(self) -> float:
        """Calculate improvement in problem-solving capabilities"""
        print("   🔧 Analyzing problem-solving improvement...")

        problem_solving_factors = {
            "solution_quality": 0.86,  # Quality of solutions generated
            "solution_speed": 0.79,  # Speed of solution generation
            "solution_creativity": 0.72,  # Creativity in solutions
            "problem_decomposition": 0.83,  # Breaking down complex problems
        }

        weights = {
            "solution_quality": 0.35,
            "solution_speed": 0.25,
            "solution_creativity": 0.2,
            "problem_decomposition": 0.2,
        }

        problem_solving = sum(
            problem_solving_factors[factor] * weight
            for factor, weight in weights.items()
        )

        return min(1.0, max(0.0, problem_solving))

    async def _calculate_creativity_expansion_rate(self) -> float:
        """Calculate expansion of creative capabilities"""
        print("   🎨 Analyzing creativity expansion...")

        creativity_factors = {
            "idea_generation": 0.71,  # Generation of novel ideas
            "divergent_thinking": 0.68,  # Thinking in multiple directions
            "innovative_combinations": 0.74,  # Novel combinations of concepts
            "artistic_expression": 0.66,  # Creative expression abilities
        }

        weights = {
            "idea_generation": 0.3,
            "divergent_thinking": 0.3,
            "innovative_combinations": 0.25,
            "artistic_expression": 0.15,
        }

        creativity_expansion = sum(
            creativity_factors[factor] * weight for factor, weight in weights.items()
        )

        return min(1.0, max(0.0, creativity_expansion))

    def _calculate_overall_trajectory_slope(
        self, dimensions: Dict[str, float]
    ) -> float:
        """Calculate overall growth trajectory slope from individual dimensions"""

        # Apply weights to dimensions
        weighted_sum = sum(
            dimensions[dimension] * self.growth_dimensions[dimension]["weight"]
            for dimension in dimensions
            if dimension in self.growth_dimensions
        )

        # Calculate slope relative to baseline
        baseline_sum = sum(
            self.growth_dimensions[dimension]["baseline"]
            * self.growth_dimensions[dimension]["weight"]
            for dimension in dimensions
            if dimension in self.growth_dimensions
        )

        trajectory_slope = weighted_sum - baseline_sum

        return trajectory_slope

    async def _calculate_growth_acceleration(self) -> float:
        """Calculate acceleration of growth (second derivative)"""

        # Get recent trajectory data
        recent_snapshots = await self._get_recent_snapshots(hours=24)

        if len(recent_snapshots) < 3:
            return 0.0  # Not enough data for acceleration calculation

        # Calculate acceleration from recent trajectory changes
        slopes = [
            snapshot.overall_trajectory_slope for snapshot in recent_snapshots[-3:]
        ]

        if len(slopes) >= 2:
            acceleration = slopes[-1] - slopes[0]
        else:
            acceleration = 0.0

        return acceleration

    async def _analyze_development_areas(self) -> Dict[str, float]:
        """Analyze specific areas of development and their progress"""

        development_areas = {
            "logical_reasoning": 0.84,
            "emotional_intelligence": 0.76,
            "pattern_recognition": 0.91,
            "language_understanding": 0.88,
            "creative_thinking": 0.72,
            "memory_integration": 0.85,
            "ethical_reasoning": 0.89,
            "social_interaction": 0.78,
            "self_awareness": 0.82,
            "learning_efficiency": 0.80,
        }

        return development_areas

    async def _identify_stagnation_indicators(self) -> List[str]:
        """Identify potential areas of stagnation or slow growth"""

        stagnation_indicators = []

        # Simulate stagnation detection
        development_areas = await self._analyze_development_areas()

        for area, score in development_areas.items():
            if score < 0.75:  # Below threshold
                stagnation_indicators.append(f"slow_growth_in_{area}")

        # Additional stagnation indicators
        if len(stagnation_indicators) == 0:
            # Check for other patterns
            recent_snapshots = await self._get_recent_snapshots(hours=48)
            if len(recent_snapshots) >= 2:
                recent_slope = recent_snapshots[-1].overall_trajectory_slope
                if recent_slope < 0.05:  # Very slow growth
                    stagnation_indicators.append("overall_growth_slowdown")

        return stagnation_indicators

    async def _identify_breakthrough_markers(self) -> List[str]:
        """Identify potential breakthrough or accelerated growth markers"""

        breakthrough_markers = []

        # Simulate breakthrough detection
        development_areas = await self._analyze_development_areas()

        for area, score in development_areas.items():
            if score > 0.9:  # High performance
                breakthrough_markers.append(f"excellence_in_{area}")

        # Check for rapid improvement
        recent_snapshots = await self._get_recent_snapshots(hours=24)
        if len(recent_snapshots) >= 2:
            recent_slope = recent_snapshots[-1].overall_trajectory_slope
            if recent_slope > 0.2:  # Rapid growth
                breakthrough_markers.append("accelerated_overall_growth")

        return breakthrough_markers

    async def _get_recent_snapshots(self, hours: int = 24) -> List[GrowthSnapshot]:
        """Get recent growth snapshots for analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        cursor.execute(
            """
            SELECT * FROM growth_snapshots
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC
        """,
            (start_time.isoformat(), end_time.isoformat()),
        )

        rows = cursor.fetchall()
        conn.close()

        snapshots = []
        for row in rows:
            snapshot = GrowthSnapshot(
                timestamp=row[0],
                learning_velocity=row[1],
                knowledge_integration_rate=row[2],
                adaptive_capacity_score=row[3],
                skill_development_index=row[4],
                problem_solving_improvement=row[5],
                creativity_expansion_rate=row[6],
                overall_trajectory_slope=row[7],
                growth_acceleration=row[8],
                development_areas=json.loads(row[9]) if row[9] else {},
                stagnation_indicators=json.loads(row[10]) if row[10] else [],
                breakthrough_markers=json.loads(row[11]) if row[11] else [],
            )
            snapshots.append(snapshot)

        return snapshots

    async def _store_growth_snapshot(self, snapshot: GrowthSnapshot):
        """Store growth snapshot in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO growth_snapshots (
                timestamp, learning_velocity, knowledge_integration_rate,
                adaptive_capacity_score, skill_development_index,
                problem_solving_improvement, creativity_expansion_rate,
                overall_trajectory_slope, growth_acceleration,
                development_areas, stagnation_indicators, breakthrough_markers,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                snapshot.timestamp,
                snapshot.learning_velocity,
                snapshot.knowledge_integration_rate,
                snapshot.adaptive_capacity_score,
                snapshot.skill_development_index,
                snapshot.problem_solving_improvement,
                snapshot.creativity_expansion_rate,
                snapshot.overall_trajectory_slope,
                snapshot.growth_acceleration,
                json.dumps(snapshot.development_areas),
                json.dumps(snapshot.stagnation_indicators),
                json.dumps(snapshot.breakthrough_markers),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    async def record_learning_milestone(
        self,
        milestone_type: str,
        description: str,
        significance_score: float,
        evidence: List[str],
        prerequisites_met: List[str] = None,
        future_implications: List[str] = None,
    ) -> str:
        """Record a significant learning milestone"""

        milestone_id = f"milestone_{datetime.now().isoformat().replace(':', '-')}"

        milestone = LearningMilestone(
            milestone_id=milestone_id,
            milestone_type=milestone_type,
            description=description,
            significance_score=significance_score,
            evidence=evidence,
            timestamp=datetime.now().isoformat(),
            prerequisites_met=prerequisites_met or [],
            future_implications=future_implications or [],
        )

        # Store milestone
        await self._store_learning_milestone(milestone)

        print(f"📍 Learning milestone recorded: {description[:50]}...")
        return milestone_id

    async def _store_learning_milestone(self, milestone: LearningMilestone):
        """Store learning milestone in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO learning_milestones (
                milestone_id, milestone_type, description, significance_score,
                evidence, timestamp, prerequisites_met, future_implications,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                milestone.milestone_id,
                milestone.milestone_type,
                milestone.description,
                milestone.significance_score,
                json.dumps(milestone.evidence),
                milestone.timestamp,
                json.dumps(milestone.prerequisites_met),
                json.dumps(milestone.future_implications),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    async def analyze_growth_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Analyze growth patterns over specified time period"""

        snapshots = await self._get_recent_snapshots(hours=days * 24)

        if len(snapshots) < 2:
            return {"status": "insufficient_data", "snapshots_count": len(snapshots)}

        # Calculate growth trends
        latest = snapshots[-1]
        earliest = snapshots[0]

        patterns = {
            "overall_growth": {
                "current_slope": latest.overall_trajectory_slope,
                "change": latest.overall_trajectory_slope
                - earliest.overall_trajectory_slope,
                "acceleration": latest.growth_acceleration,
            },
            "dimension_analysis": {},
            "development_focus": latest.development_areas,
            "concerns": latest.stagnation_indicators,
            "breakthroughs": latest.breakthrough_markers,
            "growth_consistency": self._calculate_growth_consistency(snapshots),
            "learning_momentum": self._calculate_learning_momentum(snapshots),
        }

        # Analyze each growth dimension
        dimensions = [
            "learning_velocity",
            "knowledge_integration_rate",
            "adaptive_capacity_score",
            "skill_development_index",
        ]

        for dimension in dimensions:
            current = getattr(latest, dimension)
            initial = getattr(earliest, dimension)
            change = current - initial

            patterns["dimension_analysis"][dimension] = {
                "current": current,
                "change": change,
                "trend": "improving"
                if change > 0.01
                else "declining"
                if change < -0.01
                else "stable",
            }

        return patterns

    def _calculate_growth_consistency(self, snapshots: List[GrowthSnapshot]) -> float:
        """Calculate consistency of growth over time"""
        if len(snapshots) < 3:
            return 0.5

        slopes = [snapshot.overall_trajectory_slope for snapshot in snapshots]

        # Calculate variance in slopes (lower variance = more consistent)
        mean_slope = sum(slopes) / len(slopes)
        variance = sum((slope - mean_slope) ** 2 for slope in slopes) / len(slopes)

        # Convert to consistency score (0-1, higher is more consistent)
        consistency = max(0.0, 1.0 - min(1.0, variance * 10))

        return consistency

    def _calculate_learning_momentum(self, snapshots: List[GrowthSnapshot]) -> float:
        """Calculate learning momentum based on recent trajectory"""
        if len(snapshots) < 2:
            return 0.5

        # Weight recent snapshots more heavily
        weights = [i / len(snapshots) for i in range(1, len(snapshots) + 1)]
        weighted_slopes = [
            snapshot.overall_trajectory_slope * weight
            for snapshot, weight in zip(snapshots, weights)
        ]

        momentum = sum(weighted_slopes) / sum(weights)

        # Normalize to 0-1 scale
        return min(1.0, max(0.0, (momentum + 0.5) / 1.0))


# Example usage and testing
async def demo_growth_trajectory_monitor():
    """Demonstrate growth trajectory monitoring capabilities"""
    print("📈 GROWTH TRAJECTORY MONITOR DEMONSTRATION")
    print("=" * 60)

    monitor = GrowthTrajectoryMonitor()

    # Calculate current trajectory slope
    trajectory_slope = await monitor.calculate_trajectory_slope()
    print(f"\n📊 Current Growth Metrics:")
    print(f"   • Overall Trajectory Slope: {trajectory_slope:.3f}")

    # Record a learning milestone
    milestone_id = await monitor.record_learning_milestone(
        milestone_type="capability",
        description="Enhanced ethical reasoning integration with decision-making process",
        significance_score=0.8,
        evidence=[
            "Improved ethics evaluation speed",
            "Better value alignment scores",
            "More nuanced moral reasoning",
        ],
        prerequisites_met=["basic_ethics_framework", "decision_engine_integration"],
        future_implications=["more_robust_ethical_decisions", "better_user_trust"],
    )

    # Analyze growth patterns
    patterns = await monitor.analyze_growth_patterns(days=7)
    print(f"\n📈 Growth Pattern Analysis:")
    print(
        f"   • Overall Growth Change: {patterns.get('overall_growth', {}).get('change', 0):.3f}"
    )
    print(f"   • Growth Consistency: {patterns.get('growth_consistency', 0):.3f}")
    print(f"   • Learning Momentum: {patterns.get('learning_momentum', 0):.3f}")
    print(f"   • Breakthrough Markers: {len(patterns.get('breakthroughs', []))}")


if __name__ == "__main__":
    asyncio.run(demo_growth_trajectory_monitor())
