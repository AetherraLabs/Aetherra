#!/usr/bin/env python3
"""
🔄 Learning Loop Integration - Autonomous Goal Formation from Memory Insights

This module creates a continuous learning loop that forms new goals based on
unresolved memory fragments, contradictions, and knowledge gaps. It integrates
curiosity-driven exploration with goal-directed learning.

Features:
- Goal generation from unresolved memory fragments
- Integration with contradiction detection for resolution goals
- Adaptive learning strategies based on success patterns
- Dynamic goal prioritization and scheduling
- Learning progress tracking and optimization
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to import memory and agent components with fallbacks
try:
    from ..memory.fractal_mesh.base import FractalMesh
    from .contradiction_detection_engine import (
        ContradictionDetectionEngine,
        MemoryContradiction,
    )
    from .curiosity_agent import CuriosityAgent, CuriosityQuestion, KnowledgeGap
    from .self_question_generator import GeneratedQuestion, SelfQuestionGenerator
except ImportError:
    print("⚠️ Memory and agent components not available, using mock implementations")
    CuriosityAgent = None
    KnowledgeGap = None
    CuriosityQuestion = None
    ContradictionDetectionEngine = None
    MemoryContradiction = None
    SelfQuestionGenerator = None
    GeneratedQuestion = None
    FractalMesh = None


class GoalType(Enum):
    """Types of learning goals"""

    KNOWLEDGE_GAP = "knowledge_gap"
    CONTRADICTION_RESOLUTION = "contradiction_resolution"
    PATTERN_EXPLORATION = "pattern_exploration"
    SKILL_IMPROVEMENT = "skill_improvement"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"


class GoalPriority(Enum):
    """Goal priority levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GoalStatus(Enum):
    """Goal execution status"""

    GENERATED = "generated"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass
class LearningGoal:
    """Represents an automatically generated learning goal"""

    goal_id: str
    goal_type: GoalType
    priority: GoalPriority
    title: str
    description: str
    success_criteria: List[str]
    learning_strategies: List[str]
    related_memory_ids: List[str]
    related_contradiction_ids: List[str]
    related_question_ids: List[str]
    estimated_effort: str  # "low", "medium", "high", "very_high"
    estimated_duration: str  # "minutes", "hours", "days", "weeks"
    prerequisite_goals: List[str]
    expected_outcomes: List[str]
    progress_indicators: List[str]
    timestamp: str
    deadline: Optional[str] = None
    status: GoalStatus = GoalStatus.GENERATED
    progress_score: float = 0.0
    completion_evidence: List[str] = None


@dataclass
class LearningStrategy:
    """Represents a learning strategy for achieving goals"""

    strategy_id: str
    strategy_name: str
    description: str
    applicable_goal_types: List[GoalType]
    success_rate: float  # Historical success rate
    typical_duration: str
    resources_required: List[str]
    steps: List[str]
    success_indicators: List[str]
    timestamp: str


@dataclass
class LearningProgress:
    """Tracks progress on learning goals"""

    goal_id: str
    progress_entries: List[Dict[str, Any]]  # Timestamped progress updates
    current_score: float
    obstacles_encountered: List[str]
    strategies_tried: List[str]
    insights_gained: List[str]
    next_steps: List[str]
    timestamp: str


class LearningLoopIntegration:
    """
    Integrates curiosity, contradictions, and questions into autonomous learning goals
    """

    def __init__(self, memory_engine=None, data_dir="learning_loop_data"):
        self.memory_engine = memory_engine
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize components
        self.curiosity_agent = None
        self.contradiction_engine = None
        self.question_generator = None
        self.fractal_mesh = None

        if memory_engine:
            self._initialize_components()

        # Storage
        self.learning_goals: Dict[str, LearningGoal] = {}
        self.learning_strategies: Dict[str, LearningStrategy] = {}
        self.learning_progress: Dict[str, LearningProgress] = {}

        # Configuration
        self.max_active_goals = 5
        self.max_total_goals = 50
        self.goal_generation_interval_hours = 24
        self.progress_check_interval_hours = 6
        self.goal_timeout_days = 30

        # Initialize default strategies
        self._initialize_default_strategies()

        # Load existing data
        self._load_persistence_data()

        logging.info("🔄 Learning Loop Integration initialized")

    def _initialize_components(self):
        """Initialize learning system components"""
        try:
            if CuriosityAgent:
                self.curiosity_agent = CuriosityAgent(self.memory_engine)
            if ContradictionDetectionEngine:
                self.contradiction_engine = ContradictionDetectionEngine(
                    self.memory_engine
                )
            if SelfQuestionGenerator:
                self.question_generator = SelfQuestionGenerator(self.memory_engine)
            if FractalMesh:
                self.fractal_mesh = FractalMesh()

            logging.info("✅ Learning loop components initialized")
        except Exception as e:
            logging.warning(f"⚠️ Could not initialize components: {e}")

    def _initialize_default_strategies(self):
        """Initialize default learning strategies"""
        default_strategies = [
            LearningStrategy(
                strategy_id="systematic_exploration",
                strategy_name="Systematic Exploration",
                description="Break down complex topics into smaller, explorable components",
                applicable_goal_types=[
                    GoalType.KNOWLEDGE_GAP,
                    GoalType.PATTERN_EXPLORATION,
                ],
                success_rate=0.75,
                typical_duration="hours",
                resources_required=["time", "focus", "analysis_tools"],
                steps=[
                    "Identify the scope of exploration",
                    "Break into smaller sub-components",
                    "Explore each component systematically",
                    "Synthesize findings across components",
                    "Validate understanding through application",
                ],
                success_indicators=[
                    "Clear understanding achieved",
                    "Can explain to others",
                    "Can apply knowledge",
                ],
                timestamp=datetime.now().isoformat(),
            ),
            LearningStrategy(
                strategy_id="contradiction_resolution",
                strategy_name="Contradiction Resolution",
                description="Resolve contradictions through evidence gathering and analysis",
                applicable_goal_types=[
                    GoalType.CONTRADICTION_RESOLUTION,
                    GoalType.VALIDATION,
                ],
                success_rate=0.68,
                typical_duration="hours",
                resources_required=[
                    "evidence_sources",
                    "analysis_time",
                    "critical_thinking",
                ],
                steps=[
                    "Clearly define the contradiction",
                    "Gather additional evidence for both sides",
                    "Identify contextual factors",
                    "Analyze evidence quality and reliability",
                    "Form resolution or refined understanding",
                ],
                success_indicators=[
                    "Contradiction resolved",
                    "Evidence-based conclusion",
                    "Improved confidence",
                ],
                timestamp=datetime.now().isoformat(),
            ),
            LearningStrategy(
                strategy_id="experimental_validation",
                strategy_name="Experimental Validation",
                description="Test hypotheses through controlled experiments or observations",
                applicable_goal_types=[GoalType.VALIDATION, GoalType.SKILL_IMPROVEMENT],
                success_rate=0.82,
                typical_duration="days",
                resources_required=[
                    "experimentation_environment",
                    "measurement_tools",
                    "analysis_capability",
                ],
                steps=[
                    "Form testable hypothesis",
                    "Design experiment or observation protocol",
                    "Execute experiment with careful measurement",
                    "Analyze results objectively",
                    "Draw conclusions and refine understanding",
                ],
                success_indicators=[
                    "Hypothesis tested",
                    "Clear results obtained",
                    "Learning documented",
                ],
                timestamp=datetime.now().isoformat(),
            ),
            LearningStrategy(
                strategy_id="iterative_improvement",
                strategy_name="Iterative Improvement",
                description="Gradually improve through repeated practice and refinement",
                applicable_goal_types=[
                    GoalType.SKILL_IMPROVEMENT,
                    GoalType.OPTIMIZATION,
                ],
                success_rate=0.88,
                typical_duration="weeks",
                resources_required=[
                    "practice_opportunities",
                    "feedback_mechanisms",
                    "patience",
                ],
                steps=[
                    "Establish baseline performance",
                    "Identify specific improvement targets",
                    "Practice with focus on targets",
                    "Gather feedback and adjust approach",
                    "Measure progress and continue iteration",
                ],
                success_indicators=[
                    "Measurable improvement",
                    "Consistent performance",
                    "Skill transfer",
                ],
                timestamp=datetime.now().isoformat(),
            ),
        ]

        for strategy in default_strategies:
            self.learning_strategies[strategy.strategy_id] = strategy

    async def generate_learning_goals(
        self, timeframe_hours: int = 24
    ) -> List[LearningGoal]:
        """
        Generate new learning goals based on memory analysis

        Args:
            timeframe_hours: How far back to analyze for goal generation

        Returns:
            List of generated learning goals
        """
        goals = []

        try:
            # Generate goals from different sources
            gap_goals = await self._generate_goals_from_knowledge_gaps(timeframe_hours)
            goals.extend(gap_goals)

            contradiction_goals = await self._generate_goals_from_contradictions(
                timeframe_hours
            )
            goals.extend(contradiction_goals)

            question_goals = await self._generate_goals_from_questions(timeframe_hours)
            goals.extend(question_goals)

            pattern_goals = await self._generate_goals_from_patterns(timeframe_hours)
            goals.extend(pattern_goals)

            # Filter and prioritize goals
            filtered_goals = self._filter_goals(goals)
            prioritized_goals = self._prioritize_goals(filtered_goals)

            # Limit total goals
            limited_goals = prioritized_goals[
                : self.max_total_goals - len(self.learning_goals)
            ]

            # Store new goals
            for goal in limited_goals:
                self.learning_goals[goal.goal_id] = goal

            # Save to persistence
            self._save_persistence_data()

            logging.info(f"🔄 Generated {len(limited_goals)} learning goals")
            return limited_goals

        except Exception as e:
            logging.error(f"❌ Error generating learning goals: {e}")
            return []

    async def _generate_goals_from_knowledge_gaps(
        self, timeframe_hours: int
    ) -> List[LearningGoal]:
        """Generate goals from identified knowledge gaps"""
        goals = []

        if not self.curiosity_agent:
            return goals

        try:
            # Get recent knowledge gaps
            knowledge_gaps = await self.curiosity_agent.detect_knowledge_gaps(
                timeframe_hours
            )

            for gap in knowledge_gaps[:5]:  # Limit to top 5 gaps
                goal = await self._create_knowledge_gap_goal(gap)
                if goal:
                    goals.append(goal)

            logging.info(f"🔄 Generated {len(goals)} goals from knowledge gaps")

        except Exception as e:
            logging.error(f"❌ Error generating goals from knowledge gaps: {e}")

        return goals

    async def _generate_goals_from_contradictions(
        self, timeframe_hours: int
    ) -> List[LearningGoal]:
        """Generate goals from detected contradictions"""
        goals = []

        if not self.contradiction_engine:
            return goals

        try:
            # Get recent contradictions
            contradictions = await self.contradiction_engine.detect_contradictions(
                timeframe_hours
            )

            for contradiction in contradictions[:3]:  # Limit to top 3 contradictions
                goal = await self._create_contradiction_resolution_goal(contradiction)
                if goal:
                    goals.append(goal)

            logging.info(f"🔄 Generated {len(goals)} goals from contradictions")

        except Exception as e:
            logging.error(f"❌ Error generating goals from contradictions: {e}")

        return goals

    async def _generate_goals_from_questions(
        self, timeframe_hours: int
    ) -> List[LearningGoal]:
        """Generate goals from generated questions"""
        goals = []

        if not self.question_generator:
            return goals

        try:
            # Generate questions from recent insights
            questions = await self.question_generator.generate_questions_from_stories(
                timeframe_hours
            )
            questions.extend(
                await self.question_generator.generate_questions_from_reflections(
                    timeframe_hours
                )
            )

            # Group questions by complexity and create goals
            high_priority_questions = [q for q in questions if q.priority_score > 0.8]

            for question in high_priority_questions[:4]:  # Limit to top 4 questions
                goal = await self._create_question_exploration_goal(question)
                if goal:
                    goals.append(goal)

            logging.info(f"🔄 Generated {len(goals)} goals from questions")

        except Exception as e:
            logging.error(f"❌ Error generating goals from questions: {e}")

        return goals

    async def _generate_goals_from_patterns(
        self, timeframe_hours: int
    ) -> List[LearningGoal]:
        """Generate goals from memory patterns and insights"""
        goals = []

        try:
            # Mock pattern analysis - in production, this would analyze memory patterns
            patterns = [
                {
                    "pattern_id": "performance_optimization",
                    "description": "Performance optimization patterns show inconsistent results",
                    "insight": "Need systematic approach to understand optimization factors",
                    "priority": "high",
                },
                {
                    "pattern_id": "learning_acceleration",
                    "description": "Learning accelerates with systematic debugging approaches",
                    "insight": "Should formalize and generalize debugging methodology",
                    "priority": "medium",
                },
            ]

            for pattern in patterns[:2]:  # Limit to top 2 patterns
                goal = await self._create_pattern_exploration_goal(pattern)
                if goal:
                    goals.append(goal)

            logging.info(f"🔄 Generated {len(goals)} goals from patterns")

        except Exception as e:
            logging.error(f"❌ Error generating goals from patterns: {e}")

        return goals

    async def _create_knowledge_gap_goal(
        self, gap: KnowledgeGap
    ) -> Optional[LearningGoal]:
        """Create a learning goal from a knowledge gap"""
        if not KnowledgeGap:
            return None

        try:
            # Determine priority based on gap characteristics
            priority_mapping = {
                "high": GoalPriority.HIGH,
                "medium": GoalPriority.MEDIUM,
                "low": GoalPriority.LOW,
            }
            priority = priority_mapping.get(gap.priority, GoalPriority.MEDIUM)

            # Create goal
            goal = LearningGoal(
                goal_id=f"gap_goal_{gap.gap_id}",
                goal_type=GoalType.KNOWLEDGE_GAP,
                priority=priority,
                title=f"Resolve Knowledge Gap: {gap.category}",
                description=f"Address knowledge gap: {gap.description}",
                success_criteria=[
                    "Gap understanding improved significantly",
                    "Can explain the concept clearly",
                    "Confidence level > 0.8 on related topics",
                    "Can apply knowledge in relevant contexts",
                ],
                learning_strategies=gap.exploration_strategies,
                related_memory_ids=gap.related_memories,
                related_contradiction_ids=[],
                related_question_ids=gap.questions,
                estimated_effort=self._estimate_effort_from_gap(gap),
                estimated_duration=self._estimate_duration_from_gap(gap),
                prerequisite_goals=[],
                expected_outcomes=[
                    "Improved understanding of " + gap.category,
                    "Reduced uncertainty in related areas",
                    "Better decision-making capability",
                ],
                progress_indicators=[
                    "Questions answered satisfactorily",
                    "Exploration strategies executed",
                    "Related memories updated with higher confidence",
                ],
                timestamp=datetime.now().isoformat(),
            )

            return goal

        except Exception as e:
            logging.error(f"❌ Error creating knowledge gap goal: {e}")
            return None

    async def _create_contradiction_resolution_goal(
        self, contradiction: MemoryContradiction
    ) -> Optional[LearningGoal]:
        """Create a learning goal from a contradiction"""
        if not MemoryContradiction:
            return None

        try:
            # Determine priority based on contradiction severity
            priority_mapping = {
                "critical": GoalPriority.CRITICAL,
                "major": GoalPriority.HIGH,
                "minor": GoalPriority.MEDIUM,
                "potential": GoalPriority.LOW,
            }
            priority = priority_mapping.get(contradiction.severity, GoalPriority.MEDIUM)

            goal = LearningGoal(
                goal_id=f"contradiction_goal_{contradiction.contradiction_id}",
                goal_type=GoalType.CONTRADICTION_RESOLUTION,
                priority=priority,
                title=f"Resolve {contradiction.contradiction_type.title()} Contradiction",
                description=f"Resolve contradiction between conflicting memories with {contradiction.conflict_score:.2f} conflict score",
                success_criteria=[
                    "Contradiction resolved with clear explanation",
                    "Evidence-based conclusion reached",
                    "Related memories updated consistently",
                    "No remaining logical conflicts",
                ],
                learning_strategies=contradiction.resolution_strategies,
                related_memory_ids=[
                    contradiction.memory_a_id,
                    contradiction.memory_b_id,
                ]
                + contradiction.related_memories,
                related_contradiction_ids=[contradiction.contradiction_id],
                related_question_ids=[],
                estimated_effort=self._estimate_effort_from_contradiction(
                    contradiction
                ),
                estimated_duration=self._estimate_duration_from_contradiction(
                    contradiction
                ),
                prerequisite_goals=[],
                expected_outcomes=[
                    "Consistent understanding of conflicting topics",
                    "Improved memory reliability",
                    "Better reasoning capabilities",
                ],
                progress_indicators=[
                    "Additional evidence gathered",
                    "Resolution strategies attempted",
                    "Contradiction status updated",
                ],
                timestamp=datetime.now().isoformat(),
            )

            return goal

        except Exception as e:
            logging.error(f"❌ Error creating contradiction resolution goal: {e}")
            return None

    async def _create_question_exploration_goal(
        self, question: GeneratedQuestion
    ) -> Optional[LearningGoal]:
        """Create a learning goal from a generated question"""
        if not GeneratedQuestion:
            return None

        try:
            # Map question urgency to goal priority
            priority_mapping = {
                "immediate": GoalPriority.HIGH,
                "near_term": GoalPriority.MEDIUM,
                "long_term": GoalPriority.LOW,
            }
            priority = priority_mapping.get(question.urgency, GoalPriority.MEDIUM)

            goal = LearningGoal(
                goal_id=f"question_goal_{question.question_id}",
                goal_type=self._map_question_category_to_goal_type(
                    question.question_category
                ),
                priority=priority,
                title=f"Explore Question: {question.question_category.title()}",
                description=f"Answer the question: {question.question_text}",
                success_criteria=question.success_criteria,
                learning_strategies=[question.exploration_method],
                related_memory_ids=question.insight_source.related_memories
                if question.insight_source
                else [],
                related_contradiction_ids=[],
                related_question_ids=[question.question_id],
                estimated_effort=self._estimate_effort_from_question(question),
                estimated_duration=question.estimated_exploration_time,
                prerequisite_goals=[],
                expected_outcomes=[question.expected_outcome]
                + question.follow_up_questions,
                progress_indicators=[
                    "Question exploration initiated",
                    "Evidence or insights gathered",
                    "Answer formulated and validated",
                ],
                timestamp=datetime.now().isoformat(),
            )

            return goal

        except Exception as e:
            logging.error(f"❌ Error creating question exploration goal: {e}")
            return None

    async def _create_pattern_exploration_goal(
        self, pattern: Dict[str, Any]
    ) -> Optional[LearningGoal]:
        """Create a learning goal from a memory pattern"""
        try:
            priority_mapping = {
                "high": GoalPriority.HIGH,
                "medium": GoalPriority.MEDIUM,
                "low": GoalPriority.LOW,
            }
            priority = priority_mapping.get(
                pattern.get("priority", "medium"), GoalPriority.MEDIUM
            )

            goal = LearningGoal(
                goal_id=f"pattern_goal_{pattern['pattern_id']}",
                goal_type=GoalType.PATTERN_EXPLORATION,
                priority=priority,
                title=f"Explore Pattern: {pattern['pattern_id'].title()}",
                description=f"Investigate pattern: {pattern['description']}",
                success_criteria=[
                    "Pattern mechanism understood",
                    "Key variables identified",
                    "Predictive model developed",
                    "Application opportunities identified",
                ],
                learning_strategies=[
                    "systematic_exploration",
                    "experimental_validation",
                ],
                related_memory_ids=[],
                related_contradiction_ids=[],
                related_question_ids=[],
                estimated_effort="medium",
                estimated_duration="days",
                prerequisite_goals=[],
                expected_outcomes=[
                    pattern.get("insight", "Better understanding of pattern"),
                    "Improved pattern recognition",
                    "Enhanced decision-making",
                ],
                progress_indicators=[
                    "Pattern analysis initiated",
                    "Key variables identified",
                    "Pattern model validated",
                ],
                timestamp=datetime.now().isoformat(),
            )

            return goal

        except Exception as e:
            logging.error(f"❌ Error creating pattern exploration goal: {e}")
            return None

    def _map_question_category_to_goal_type(self, question_category: str) -> GoalType:
        """Map question category to goal type"""
        mapping = {
            "understanding": GoalType.KNOWLEDGE_GAP,
            "prediction": GoalType.PATTERN_EXPLORATION,
            "optimization": GoalType.OPTIMIZATION,
            "exploration": GoalType.PATTERN_EXPLORATION,
            "validation": GoalType.VALIDATION,
            "meta": GoalType.SKILL_IMPROVEMENT,
        }
        return mapping.get(question_category, GoalType.KNOWLEDGE_GAP)

    def _estimate_effort_from_gap(self, gap: KnowledgeGap) -> str:
        """Estimate effort required for a knowledge gap"""
        if not KnowledgeGap:
            return "medium"

        if gap.confidence_score > 0.8:
            return "high"
        elif gap.confidence_score > 0.6:
            return "medium"
        else:
            return "low"

    def _estimate_duration_from_gap(self, gap: KnowledgeGap) -> str:
        """Estimate duration for addressing a knowledge gap"""
        if not KnowledgeGap:
            return "hours"

        category_durations = {
            "conceptual": "hours",
            "causal": "days",
            "contextual": "hours",
            "experiential": "weeks",
        }
        return category_durations.get(gap.category, "hours")

    def _estimate_effort_from_contradiction(
        self, contradiction: MemoryContradiction
    ) -> str:
        """Estimate effort required for resolving a contradiction"""
        if not MemoryContradiction:
            return "medium"

        if contradiction.conflict_score > 0.8:
            return "high"
        elif contradiction.evidence_strength > 0.7:
            return "medium"
        else:
            return "low"

    def _estimate_duration_from_contradiction(
        self, contradiction: MemoryContradiction
    ) -> str:
        """Estimate duration for resolving a contradiction"""
        if not MemoryContradiction:
            return "hours"

        type_durations = {
            "semantic": "hours",
            "confidence": "hours",
            "temporal": "days",
            "logical": "days",
            "value": "hours",
        }
        return type_durations.get(contradiction.contradiction_type, "hours")

    def _estimate_effort_from_question(self, question: GeneratedQuestion) -> str:
        """Estimate effort required for exploring a question"""
        if not GeneratedQuestion:
            return "medium"

        complexity_efforts = {
            "basic": "low",
            "intermediate": "medium",
            "advanced": "high",
            "meta": "high",
        }
        return complexity_efforts.get(question.complexity_level, "medium")

    def _filter_goals(self, goals: List[LearningGoal]) -> List[LearningGoal]:
        """Filter out duplicate or low-value goals"""
        filtered = []
        seen_descriptions = set()

        for goal in goals:
            # Check for duplicates
            if goal.description not in seen_descriptions:
                filtered.append(goal)
                seen_descriptions.add(goal.description)

        return filtered

    def _prioritize_goals(self, goals: List[LearningGoal]) -> List[LearningGoal]:
        """Prioritize goals based on multiple factors"""

        def priority_score(goal: LearningGoal) -> float:
            # Base score from priority level
            priority_scores = {
                GoalPriority.CRITICAL: 4.0,
                GoalPriority.HIGH: 3.0,
                GoalPriority.MEDIUM: 2.0,
                GoalPriority.LOW: 1.0,
            }

            base_score = priority_scores.get(goal.priority, 2.0)

            # Boost for certain goal types
            type_boosts = {
                GoalType.CONTRADICTION_RESOLUTION: 0.5,
                GoalType.VALIDATION: 0.3,
                GoalType.KNOWLEDGE_GAP: 0.2,
                GoalType.SKILL_IMPROVEMENT: 0.1,
            }

            type_boost = type_boosts.get(goal.goal_type, 0.0)

            # Penalty for high effort goals if we have many active goals
            effort_penalty = 0.0
            active_goals = len(
                [
                    g
                    for g in self.learning_goals.values()
                    if g.status == GoalStatus.ACTIVE
                ]
            )
            if active_goals > 3 and goal.estimated_effort in ["high", "very_high"]:
                effort_penalty = 0.5

            return base_score + type_boost - effort_penalty

        return sorted(goals, key=priority_score, reverse=True)

    async def activate_goals(self, max_active: int = None) -> List[LearningGoal]:
        """Activate the highest priority goals for execution"""
        if max_active is None:
            max_active = self.max_active_goals

        # Get currently active goals
        active_goals = [
            g for g in self.learning_goals.values() if g.status == GoalStatus.ACTIVE
        ]
        available_slots = max_active - len(active_goals)

        if available_slots <= 0:
            logging.info("🔄 No available slots for new active goals")
            return active_goals

        # Get scheduled goals ready for activation
        scheduled_goals = [
            g for g in self.learning_goals.values() if g.status == GoalStatus.SCHEDULED
        ]
        generated_goals = [
            g for g in self.learning_goals.values() if g.status == GoalStatus.GENERATED
        ]

        # Prioritize and activate goals
        available_goals = scheduled_goals + generated_goals
        prioritized_goals = self._prioritize_goals(available_goals)

        newly_activated = []
        for goal in prioritized_goals[:available_slots]:
            goal.status = GoalStatus.ACTIVE
            self.learning_goals[goal.goal_id] = goal
            newly_activated.append(goal)

            # Initialize progress tracking
            progress = LearningProgress(
                goal_id=goal.goal_id,
                progress_entries=[],
                current_score=0.0,
                obstacles_encountered=[],
                strategies_tried=[],
                insights_gained=[],
                next_steps=goal.learning_strategies[:3],
                timestamp=datetime.now().isoformat(),
            )
            self.learning_progress[goal.goal_id] = progress

        # Save changes
        self._save_persistence_data()

        logging.info(f"🔄 Activated {len(newly_activated)} new goals")
        return active_goals + newly_activated

    async def update_goal_progress(
        self, goal_id: str, progress_update: Dict[str, Any]
    ) -> bool:
        """Update progress on a learning goal"""
        if goal_id not in self.learning_goals:
            logging.warning(f"⚠️ Goal {goal_id} not found for progress update")
            return False

        try:
            goal = self.learning_goals[goal_id]

            # Get or create progress tracking
            if goal_id not in self.learning_progress:
                progress = LearningProgress(
                    goal_id=goal_id,
                    progress_entries=[],
                    current_score=0.0,
                    obstacles_encountered=[],
                    strategies_tried=[],
                    insights_gained=[],
                    next_steps=[],
                    timestamp=datetime.now().isoformat(),
                )
                self.learning_progress[goal_id] = progress
            else:
                progress = self.learning_progress[goal_id]

            # Update progress
            progress_entry = {
                "timestamp": datetime.now().isoformat(),
                "progress_delta": progress_update.get("progress_delta", 0.0),
                "description": progress_update.get("description", ""),
                "evidence": progress_update.get("evidence", []),
                "challenges": progress_update.get("challenges", []),
                "insights": progress_update.get("insights", []),
            }

            progress.progress_entries.append(progress_entry)
            progress.current_score += progress_update.get("progress_delta", 0.0)
            progress.current_score = max(0.0, min(1.0, progress.current_score))

            # Update obstacles and insights
            if progress_update.get("challenges"):
                progress.obstacles_encountered.extend(progress_update["challenges"])
            if progress_update.get("insights"):
                progress.insights_gained.extend(progress_update["insights"])

            # Update goal progress score
            goal.progress_score = progress.current_score

            # Check for completion
            if progress.current_score >= 1.0:
                goal.status = GoalStatus.COMPLETED
                goal.completion_evidence = progress_update.get("evidence", [])
                logging.info(f"🎉 Goal {goal_id} completed!")

            # Update storage
            self.learning_goals[goal_id] = goal
            self.learning_progress[goal_id] = progress

            # Save changes
            self._save_persistence_data()

            logging.info(
                f"🔄 Updated progress for goal {goal_id}: {progress.current_score:.2f}"
            )
            return True

        except Exception as e:
            logging.error(f"❌ Error updating goal progress: {e}")
            return False

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning loop status"""
        total_goals = len(self.learning_goals)

        # Count by status
        status_counts = {}
        for goal in self.learning_goals.values():
            status_counts[goal.status.value] = (
                status_counts.get(goal.status.value, 0) + 1
            )

        # Count by type
        type_counts = {}
        for goal in self.learning_goals.values():
            type_counts[goal.goal_type.value] = (
                type_counts.get(goal.goal_type.value, 0) + 1
            )

        # Calculate completion rate
        completed = status_counts.get("completed", 0)
        completion_rate = completed / max(total_goals, 1)

        # Get active goals
        active_goals = [
            g for g in self.learning_goals.values() if g.status == GoalStatus.ACTIVE
        ]

        # Calculate average progress
        if active_goals:
            avg_progress = sum(g.progress_score for g in active_goals) / len(
                active_goals
            )
        else:
            avg_progress = 0.0

        return {
            "timestamp": datetime.now().isoformat(),
            "total_goals": total_goals,
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "completion_rate": completion_rate,
            "active_goals_count": len(active_goals),
            "average_active_progress": avg_progress,
            "learning_strategies_available": len(self.learning_strategies),
            "recent_completions": [
                {
                    "title": g.title,
                    "type": g.goal_type.value,
                    "completion_time": g.timestamp,
                }
                for g in sorted(
                    self.learning_goals.values(),
                    key=lambda x: x.timestamp,
                    reverse=True,
                )
                if g.status == GoalStatus.COMPLETED
            ][:3],
        }

    def _load_persistence_data(self):
        """Load persistent data from files"""
        try:
            # Load learning goals
            goals_file = self.data_dir / "learning_goals.json"
            if goals_file.exists():
                with open(goals_file, "r") as f:
                    goals_data = json.load(f)
                    for goal_id, goal_data in goals_data.items():
                        # Convert enum values back
                        goal_data["goal_type"] = GoalType(goal_data["goal_type"])
                        goal_data["priority"] = GoalPriority(goal_data["priority"])
                        goal_data["status"] = GoalStatus(goal_data["status"])
                        self.learning_goals[goal_id] = LearningGoal(**goal_data)

            # Load learning strategies
            strategies_file = self.data_dir / "learning_strategies.json"
            if strategies_file.exists():
                with open(strategies_file, "r") as f:
                    strategies_data = json.load(f)
                    for strategy_id, strategy_data in strategies_data.items():
                        # Convert enum values back
                        strategy_data["applicable_goal_types"] = [
                            GoalType(gt)
                            for gt in strategy_data["applicable_goal_types"]
                        ]
                        self.learning_strategies[strategy_id] = LearningStrategy(
                            **strategy_data
                        )

            # Load learning progress
            progress_file = self.data_dir / "learning_progress.json"
            if progress_file.exists():
                with open(progress_file, "r") as f:
                    progress_data = json.load(f)
                    self.learning_progress = {
                        p_id: LearningProgress(**p_data)
                        for p_id, p_data in progress_data.items()
                    }

            logging.info(
                f"📂 Loaded {len(self.learning_goals)} goals, {len(self.learning_strategies)} strategies, {len(self.learning_progress)} progress records"
            )

        except Exception as e:
            logging.warning(f"⚠️ Could not load persistence data: {e}")

    def _save_persistence_data(self):
        """Save persistent data to files"""
        try:
            # Save learning goals
            goals_file = self.data_dir / "learning_goals.json"
            with open(goals_file, "w") as f:
                goals_data = {}
                for goal_id, goal in self.learning_goals.items():
                    goal_dict = asdict(goal)
                    # Convert enums to strings
                    goal_dict["goal_type"] = goal.goal_type.value
                    goal_dict["priority"] = goal.priority.value
                    goal_dict["status"] = goal.status.value
                    goals_data[goal_id] = goal_dict
                json.dump(goals_data, f, indent=2)

            # Save learning strategies
            strategies_file = self.data_dir / "learning_strategies.json"
            with open(strategies_file, "w") as f:
                strategies_data = {}
                for strategy_id, strategy in self.learning_strategies.items():
                    strategy_dict = asdict(strategy)
                    # Convert enums to strings
                    strategy_dict["applicable_goal_types"] = [
                        gt.value for gt in strategy.applicable_goal_types
                    ]
                    strategies_data[strategy_id] = strategy_dict
                json.dump(strategies_data, f, indent=2)

            # Save learning progress
            progress_file = self.data_dir / "learning_progress.json"
            with open(progress_file, "w") as f:
                progress_data = {
                    p_id: asdict(progress)
                    for p_id, progress in self.learning_progress.items()
                }
                json.dump(progress_data, f, indent=2)

            logging.info("💾 Saved learning loop data to persistence")

        except Exception as e:
            logging.error(f"❌ Could not save persistence data: {e}")


# Convenience functions for integration
async def generate_autonomous_learning_goals(
    memory_engine=None, timeframe_hours: int = 24
) -> List[LearningGoal]:
    """Convenience function to generate learning goals"""
    loop = LearningLoopIntegration(memory_engine)
    return await loop.generate_learning_goals(timeframe_hours)


async def activate_learning_goals(
    memory_engine=None, max_active: int = 5
) -> List[LearningGoal]:
    """Convenience function to activate learning goals"""
    loop = LearningLoopIntegration(memory_engine)
    return await loop.activate_goals(max_active)


if __name__ == "__main__":

    async def demo():
        """Demo the Learning Loop Integration"""
        print("🔄 Learning Loop Integration Demo")
        print("=" * 50)

        # Initialize learning loop
        loop = LearningLoopIntegration()

        # Generate learning goals
        print("\n🎯 Generating learning goals...")
        goals = await loop.generate_learning_goals(timeframe_hours=48)

        print(f"\n📊 Goal Generation Results:")
        print(f"   Total goals generated: {len(goals)}")

        for i, goal in enumerate(goals[:3], 1):
            print(f"\n   {i}. [{goal.goal_type.value}] {goal.title}")
            print(f"      Priority: {goal.priority.value}")
            print(f"      Description: {goal.description[:80]}...")
            print(f"      Estimated effort: {goal.estimated_effort}")
            print(f"      Expected duration: {goal.estimated_duration}")
            print(f"      Success criteria: {len(goal.success_criteria)} defined")

        # Activate goals
        print(f"\n🚀 Activating goals...")
        active_goals = await loop.activate_goals(max_active=3)

        print(f"\n📈 Active Goals:")
        for i, goal in enumerate(active_goals[:3], 1):
            print(f"   {i}. {goal.title} (Progress: {goal.progress_score:.1%})")

        # Simulate progress update
        if active_goals:
            goal_id = active_goals[0].goal_id
            print(f"\n📊 Simulating progress update for: {active_goals[0].title}")

            await loop.update_goal_progress(
                goal_id,
                {
                    "progress_delta": 0.3,
                    "description": "Made significant progress on understanding key concepts",
                    "evidence": ["Concept analysis completed", "Questions answered"],
                    "insights": [
                        "Key relationships identified",
                        "Pattern beginning to emerge",
                    ],
                },
            )

        # Show summary
        summary = loop.get_learning_summary()
        print(f"\n📊 Learning Loop Summary:")
        print(f"   Total goals: {summary['total_goals']}")
        print(f"   Active goals: {summary['active_goals_count']}")
        print(f"   Completion rate: {summary['completion_rate']:.1%}")
        print(f"   Average progress: {summary['average_active_progress']:.1%}")
        print(f"   Goal types: {list(summary['type_breakdown'].keys())}")

        print("\n🎉 Demo completed!")

    # Run demo
    asyncio.run(demo())
