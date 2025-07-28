#!/usr/bin/env python3
"""
🔄 LEARNING LOOP INTEGRATION AGENT - Phase 3 Implementation
============================================================

Advanced Learning Loop Integration Agent that integrates with the existing Lyrixa agent architecture.
Forms autonomous goals from unresolved memory fragments and coordinates learning cycles.

Integrates with:
- Existing agent_base.py architecture
- Goal system via existing goal_agent.py
- Memory system for fragment analysis
- All Phase 3 components for unified learning
"""

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent_base import AgentBase, AgentResponse

# Try to import other Phase 3 components
try:
    from .contradiction_detection_agent import (
        ContradictionDetectionAgent,
        DetectedContradiction,
    )
    from .curiosity_agent import CuriosityAgent, KnowledgeGap
    from .self_question_generator_agent import (
        GeneratedQuestion,
        SelfQuestionGeneratorAgent,
    )
except ImportError:
    print("⚠️ Phase 3 components not fully available, using mock implementations")
    CuriosityAgent = None
    SelfQuestionGeneratorAgent = None
    ContradictionDetectionAgent = None

# Try to import memory components
try:
    from ..memory.fractal_mesh.base import FractalMesh
    from ..memory.reflector.reflect_analyzer import ReflectAnalyzer
except ImportError:
    print("⚠️ Memory components not available, using mock implementations")
    FractalMesh = None
    ReflectAnalyzer = None


@dataclass
class LearningGoal:
    """Represents an autonomous learning goal generated from memory analysis"""

    goal_id: str
    title: str
    description: str
    goal_type: (
        str  # "curiosity", "contradiction", "question", "integration", "optimization"
    )
    priority: str  # "critical", "high", "medium", "low"

    # Source information
    source_type: str  # "memory_fragment", "knowledge_gap", "contradiction", "question"
    source_ids: List[str]  # IDs of source fragments/gaps/contradictions

    # Goal structure
    sub_goals: List[str]  # Sub-goal IDs
    success_criteria: List[str]
    learning_methods: List[
        str
    ]  # "experimentation", "reflection", "research", "observation"

    # Progress tracking
    progress_percentage: float  # 0.0 to 100.0
    status: str  # "pending", "active", "paused", "completed", "abandoned"

    # Integration with other systems
    related_gaps: List[str]  # KnowledgeGap IDs
    related_questions: List[str]  # GeneratedQuestion IDs
    related_contradictions: List[str]  # DetectedContradiction IDs

    # Metadata
    created_timestamp: str
    last_updated: str
    estimated_completion_time: str
    activation_timestamp: Optional[str] = None
    completion_timestamp: Optional[str] = None


@dataclass
class LearningCycle:
    """Represents a complete learning cycle with multiple goals"""

    cycle_id: str
    cycle_name: str
    goals: List[str]  # LearningGoal IDs
    cycle_type: str  # "exploration", "consolidation", "optimization", "integration"

    # Cycle progress
    current_phase: str  # "planning", "execution", "reflection", "integration"
    progress_percentage: float

    # Timestamps
    start_timestamp: str
    estimated_completion: str

    # Results and insights
    insights_gained: List[str]
    goals_completed: int
    goals_abandoned: int

    # Next cycle preparation
    next_cycle_topics: List[str]
    unresolved_fragments: List[str]
    actual_completion: Optional[str] = None


class LearningLoopIntegrationAgent(AgentBase):
    """
    Advanced Learning Loop Integration for autonomous goal formation and learning cycles
    """

    def __init__(self, memory_engine=None, data_dir="learning_loop_data"):
        super().__init__(
            "LearningLoopIntegrationAgent",
            "Forms autonomous goals from unresolved memory fragments and coordinates learning cycles",
        )

        self.memory_engine = memory_engine
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Phase 3 component agents
        self.curiosity_agent = None
        self.question_generator = None
        self.contradiction_detector = None

        # Memory components
        self.fractal_mesh = None
        self.reflector = None

        if memory_engine:
            self._initialize_components()

        # Storage for learning goals and cycles
        self.learning_goals: Dict[str, LearningGoal] = {}
        self.learning_cycles: Dict[str, LearningCycle] = {}
        self.current_cycle_id: Optional[str] = None

        # Configuration
        self.max_active_goals = 5
        self.cycle_length_days = 7
        self.goal_priority_threshold = 0.6

        # Load existing data
        self._load_persistence_data()

        self.log(
            "🔄 LearningLoopIntegrationAgent initialized with autonomous goal formation"
        )

    def _initialize_components(self):
        """Initialize Phase 3 components and memory systems"""
        try:
            # Initialize Phase 3 components
            if CuriosityAgent:
                self.curiosity_agent = CuriosityAgent(self.memory_engine)
            if SelfQuestionGeneratorAgent:
                self.question_generator = SelfQuestionGeneratorAgent(self.memory_engine)
            if ContradictionDetectionAgent:
                self.contradiction_detector = ContradictionDetectionAgent(
                    self.memory_engine
                )

            # Initialize memory components
            if FractalMesh:
                self.fractal_mesh = FractalMesh()
            if ReflectAnalyzer:
                self.reflector = ReflectAnalyzer(self.memory_engine)

            self.log("✅ All Phase 3 components and memory systems initialized")
        except Exception as e:
            self.log(f"⚠️ Could not initialize some components: {e}", "WARNING")

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process learning loop integration input and commands"""
        context = context or {}

        try:
            input_lower = input_text.lower()

            # Handle different learning loop commands
            if "generate goals" in input_lower or "create goals" in input_lower:
                result = await self._handle_goal_generation(context)
            elif "start cycle" in input_lower or "begin cycle" in input_lower:
                result = await self._handle_cycle_start(context)
            elif "activate goals" in input_lower:
                result = await self._handle_goal_activation(context)
            elif "update progress" in input_lower:
                result = await self._handle_progress_update(input_text, context)
            elif "learning status" in input_lower or "cycle status" in input_lower:
                result = await self._handle_status_request(context)
            elif "complete goal" in input_lower:
                result = await self._handle_goal_completion(input_text, context)
            elif "integration analysis" in input_lower:
                result = await self._handle_integration_analysis(context)
            else:
                # General learning loop analysis
                result = await self._handle_general_learning(input_text, context)

            self._increment_success()
            return result

        except Exception as e:
            self.log(f"Error processing learning loop input: {e}", "ERROR")
            self._increment_error()

            return AgentResponse(
                content=f"I encountered an error while managing learning loops: {str(e)}",
                confidence=0.0,
                agent_name=self.name,
                metadata={"error": str(e)},
            )

    async def _handle_goal_generation(self, context: Dict[str, Any]) -> AgentResponse:
        """Handle learning goal generation from memory fragments"""
        self.log("🎯 Generating learning goals from unresolved memory fragments")

        goals = await self.generate_learning_goals()

        if not goals:
            return AgentResponse(
                content="I haven't found any unresolved memory fragments that suggest new learning goals. This could mean our current learning is well-integrated or we need deeper fragment analysis.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"goals_generated": 0},
            )

        # Format response about generated goals
        goal_summary = []
        for i, goal in enumerate(goals[:5], 1):
            goal_summary.append(
                f"{i}. **{goal.goal_type.title()}**: {goal.title} (Priority: {goal.priority})"
            )

        content = (
            f"🎯 I've generated {len(goals)} learning goals from memory analysis:\n\n"
            + "\n".join(goal_summary)
        )

        if len(goals) > 5:
            content += f"\n\n*And {len(goals) - 5} additional goals generated.*"

        return AgentResponse(
            content=content,
            confidence=0.9,
            agent_name=self.name,
            metadata={
                "goals_generated": len(goals),
                "goal_types": list(set(g.goal_type for g in goals)),
                "high_priority_goals": len(
                    [g for g in goals if g.priority in ["critical", "high"]]
                ),
            },
        )

    async def _handle_cycle_start(self, context: Dict[str, Any]) -> AgentResponse:
        """Handle starting a new learning cycle"""
        cycle_type = context.get("cycle_type", "exploration")

        self.log(f"🔄 Starting new {cycle_type} learning cycle")

        # Get pending goals for the cycle
        pending_goals = [
            g for g in self.learning_goals.values() if g.status == "pending"
        ][: self.max_active_goals]

        if not pending_goals:
            return AgentResponse(
                content="No pending learning goals found to start a cycle. Generate learning goals first.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"cycle_started": False},
            )

        cycle = await self.start_learning_cycle(pending_goals, cycle_type)

        content = f"🔄 Started {cycle_type} learning cycle '{cycle.cycle_name}' with {len(pending_goals)} goals:\n\n"

        for i, goal_id in enumerate(cycle.goals[:3], 1):
            goal = self.learning_goals[goal_id]
            content += f"{i}. {goal.title}\n"

        if len(cycle.goals) > 3:
            content += f"\n*And {len(cycle.goals) - 3} additional goals.*"

        return AgentResponse(
            content=content,
            confidence=0.9,
            agent_name=self.name,
            metadata={
                "cycle_id": cycle.cycle_id,
                "cycle_type": cycle_type,
                "goals_in_cycle": len(cycle.goals),
            },
        )

    async def _handle_goal_activation(self, context: Dict[str, Any]) -> AgentResponse:
        """Handle activating learning goals"""
        self.log("⚡ Activating learning goals")

        activated_goals = await self.activate_goals()

        if not activated_goals:
            return AgentResponse(
                content="No goals were activated. This might mean all high-priority goals are already active or no goals are ready for activation.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"goals_activated": 0},
            )

        goal_summary = []
        for goal in activated_goals:
            goal_summary.append(f"• **{goal.title}** ({goal.goal_type})")

        content = (
            f"⚡ Activated {len(activated_goals)} learning goals:\n\n"
            + "\n".join(goal_summary)
        )

        return AgentResponse(
            content=content,
            confidence=0.85,
            agent_name=self.name,
            metadata={
                "goals_activated": len(activated_goals),
                "goal_types": [g.goal_type for g in activated_goals],
            },
        )

    async def _handle_progress_update(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle progress updates for goals"""
        # Extract goal ID and progress from input
        if "goal_id:" in input_text and "progress:" in input_text:
            goal_id = input_text.split("goal_id:")[1].split()[0]
            progress_str = input_text.split("progress:")[1].split()[0]

            try:
                progress = float(progress_str)
                if goal_id in self.learning_goals:
                    updated = await self.update_goal_progress(goal_id, progress)

                    if updated:
                        goal = self.learning_goals[goal_id]
                        return AgentResponse(
                            content=f"✅ Updated progress for '{goal.title}' to {progress}%",
                            confidence=0.9,
                            agent_name=self.name,
                            metadata={"goal_id": goal_id, "new_progress": progress},
                        )
                    else:
                        return AgentResponse(
                            content=f"Could not update progress for goal '{goal_id}'",
                            confidence=0.5,
                            agent_name=self.name,
                            metadata={"error": "update_failed"},
                        )
                else:
                    return AgentResponse(
                        content=f"Goal with ID '{goal_id}' not found.",
                        confidence=0.0,
                        agent_name=self.name,
                        metadata={"error": "goal_not_found"},
                    )
            except ValueError:
                return AgentResponse(
                    content=f"Invalid progress value '{progress_str}'. Please use a number between 0 and 100.",
                    confidence=0.0,
                    agent_name=self.name,
                    metadata={"error": "invalid_progress"},
                )
        else:
            return AgentResponse(
                content="Please specify goal_id: <id> progress: <percentage> to update goal progress.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"help": "format_required"},
            )

    async def _handle_goal_completion(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle goal completion"""
        if "goal_id:" in input_text:
            goal_id = input_text.split("goal_id:")[1].strip().split()[0]

            if goal_id in self.learning_goals:
                goal = self.learning_goals[goal_id]
                goal.status = "completed"
                goal.progress_percentage = 100.0
                goal.completion_timestamp = datetime.now().isoformat()
                goal.last_updated = datetime.now().isoformat()

                # Update current cycle if applicable
                if (
                    self.current_cycle_id
                    and self.current_cycle_id in self.learning_cycles
                ):
                    cycle = self.learning_cycles[self.current_cycle_id]
                    cycle.goals_completed += 1

                self._save_persistence_data()

                return AgentResponse(
                    content=f"🎉 Completed learning goal: '{goal.title}'",
                    confidence=0.95,
                    agent_name=self.name,
                    metadata={"completed_goal_id": goal_id},
                )
            else:
                return AgentResponse(
                    content=f"Goal with ID '{goal_id}' not found.",
                    confidence=0.0,
                    agent_name=self.name,
                    metadata={"error": "goal_not_found"},
                )
        else:
            return AgentResponse(
                content="Please specify goal_id: <id> to complete a specific goal.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"help": "goal_id_required"},
            )

    async def _handle_status_request(self, context: Dict[str, Any]) -> AgentResponse:
        """Handle learning loop status and summary requests"""
        summary = self.get_learning_loop_summary()

        current_cycle_info = ""
        if self.current_cycle_id and self.current_cycle_id in self.learning_cycles:
            cycle = self.learning_cycles[self.current_cycle_id]
            current_cycle_info = f"""
**Current Cycle**: {cycle.cycle_name} ({cycle.cycle_type})
• Phase: {cycle.current_phase}
• Progress: {cycle.progress_percentage:.1f}%
• Goals Completed: {cycle.goals_completed}/{len(cycle.goals)}
"""

        content = f"""🔄 **Learning Loop Integration Status**

**Learning Goals**: {summary["total_goals"]} total
• Pending: {summary["pending_goals"]}
• Active: {summary["active_goals"]}
• Completed: {summary["completed_goals"]}
• Paused: {summary["paused_goals"]}

**Goal Types**:
{self._format_goal_type_breakdown(summary["goal_type_breakdown"])}
{current_cycle_info}
**Learning Cycles**: {summary["total_cycles"]} completed

**Integration Success Rate**: {summary["integration_success_rate"]:.1%}

**Recent Activity**: {summary["recent_activity"]}
"""

        return AgentResponse(
            content=content, confidence=0.95, agent_name=self.name, metadata=summary
        )

    async def _handle_integration_analysis(
        self, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle integration analysis across Phase 3 components"""
        self.log("🔗 Analyzing integration across Phase 3 components")

        analysis = await self.analyze_phase3_integration()

        content = f"""🔗 **Phase 3 Integration Analysis**

**Component Status**:
• Curiosity Agent: {analysis["curiosity_status"]}
• Question Generator: {analysis["question_generator_status"]}
• Contradiction Detector: {analysis["contradiction_detector_status"]}

**Integration Metrics**:
• Cross-component References: {analysis["cross_references"]}
• Unified Goals Created: {analysis["unified_goals"]}
• Resolution Synergies: {analysis["resolution_synergies"]}

**Key Insights**:
{self._format_insights(analysis["key_insights"])}

**Optimization Opportunities**:
{self._format_opportunities(analysis["optimization_opportunities"])}
"""

        return AgentResponse(
            content=content, confidence=0.85, agent_name=self.name, metadata=analysis
        )

    async def _handle_general_learning(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle general learning loop requests"""
        self.log("🤔 Performing general learning loop analysis")

        # Analyze input for learning triggers
        learning_triggers = [
            ("goal", "goal_formation"),
            ("cycle", "cycle_management"),
            ("progress", "progress_tracking"),
            ("integration", "component_integration"),
            ("unresolved", "fragment_analysis"),
            ("learning", "autonomous_learning"),
        ]

        detected_triggers = []
        for trigger, learning_type in learning_triggers:
            if trigger in input_text.lower():
                detected_triggers.append(learning_type)

        if detected_triggers:
            content = f"🔄 I can help with {', '.join(detected_triggers)}! Would you like me to generate goals from memory fragments, start a learning cycle, or analyze integration across Phase 3 components?"
            confidence = 0.8
        else:
            content = "🔄 I'm ready to coordinate autonomous learning! I can generate goals from unresolved memory fragments, start learning cycles, activate goals, or analyze integration across all Phase 3 components. What aspect of learning would you like to explore?"
            confidence = 0.7

        return AgentResponse(
            content=content,
            confidence=confidence,
            agent_name=self.name,
            metadata={
                "learning_triggers": detected_triggers,
                "available_actions": [
                    "generate_goals",
                    "start_cycle",
                    "activate_goals",
                    "integration_analysis",
                ],
            },
        )

    # Core learning loop methods
    async def generate_learning_goals(self) -> List[LearningGoal]:
        """Generate learning goals from unresolved memory fragments and Phase 3 components"""
        goals = []

        # Generate goals from different sources
        curiosity_goals = await self._generate_goals_from_curiosity()
        question_goals = await self._generate_goals_from_questions()
        contradiction_goals = await self._generate_goals_from_contradictions()
        integration_goals = await self._generate_integration_goals()

        goals.extend(curiosity_goals)
        goals.extend(question_goals)
        goals.extend(contradiction_goals)
        goals.extend(integration_goals)

        # Save to persistence
        self._save_persistence_data()
        self.log(f"🎯 Generated {len(goals)} learning goals from multiple sources")

        return goals

    async def _generate_goals_from_curiosity(self) -> List[LearningGoal]:
        """Generate goals from curiosity gaps"""
        goals = []

        if self.curiosity_agent:
            try:
                # Get recent knowledge gaps
                gaps = await self.curiosity_agent.detect_knowledge_gaps()

                for gap in gaps[:3]:  # Limit to top 3 gaps
                    goal_id = f"goal_curiosity_{gap.gap_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                    goal = LearningGoal(
                        goal_id=goal_id,
                        title=f"Explore {gap.category} gap: {gap.description[:50]}...",
                        description=f"Investigate and resolve the knowledge gap: {gap.description}",
                        goal_type="curiosity",
                        priority=gap.priority,
                        source_type="knowledge_gap",
                        source_ids=[gap.gap_id],
                        sub_goals=[],
                        success_criteria=[
                            "Gap understanding improved",
                            "Exploration questions answered",
                        ],
                        learning_methods=gap.exploration_strategies,
                        progress_percentage=0.0,
                        status="pending",
                        related_gaps=[gap.gap_id],
                        related_questions=[],
                        related_contradictions=[],
                        created_timestamp=datetime.now().isoformat(),
                        last_updated=datetime.now().isoformat(),
                        estimated_completion_time="2-3 days",
                    )

                    goals.append(goal)
                    self.learning_goals[goal_id] = goal

            except Exception as e:
                self.log(f"Could not generate curiosity goals: {e}", "WARNING")

        return goals

    async def _generate_goals_from_questions(self) -> List[LearningGoal]:
        """Generate goals from generated questions"""
        goals = []

        if self.question_generator:
            try:
                # Get pending questions
                pending_questions = [
                    q
                    for q in self.question_generator.generated_questions.values()
                    if q.status == "pending"
                ][:3]

                for question in pending_questions:
                    goal_id = f"goal_question_{question.question_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                    goal = LearningGoal(
                        goal_id=goal_id,
                        title=f"Answer {question.category} question",
                        description=f"Explore and answer: {question.question_text}",
                        goal_type="question",
                        priority="medium",
                        source_type="generated_question",
                        source_ids=[question.question_id],
                        sub_goals=[],
                        success_criteria=["Question answered", "Insights documented"],
                        learning_methods=question.exploration_methods,
                        progress_percentage=0.0,
                        status="pending",
                        related_gaps=[],
                        related_questions=[question.question_id],
                        related_contradictions=[],
                        created_timestamp=datetime.now().isoformat(),
                        last_updated=datetime.now().isoformat(),
                        estimated_completion_time="1-2 days",
                    )

                    goals.append(goal)
                    self.learning_goals[goal_id] = goal

            except Exception as e:
                self.log(f"Could not generate question goals: {e}", "WARNING")

        return goals

    async def _generate_goals_from_contradictions(self) -> List[LearningGoal]:
        """Generate goals from detected contradictions"""
        goals = []

        if self.contradiction_detector:
            try:
                # Get open contradictions
                open_contradictions = [
                    c
                    for c in self.contradiction_detector.detected_contradictions.values()
                    if c.resolution_status == "open"
                ][:2]

                for contradiction in open_contradictions:
                    goal_id = f"goal_contradiction_{contradiction.contradiction_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                    goal = LearningGoal(
                        goal_id=goal_id,
                        title=f"Resolve {contradiction.contradiction_type.value} contradiction",
                        description=f"Resolve contradiction: {contradiction.title}",
                        goal_type="contradiction",
                        priority=contradiction.severity
                        if contradiction.severity in ["high", "critical"]
                        else "medium",
                        source_type="detected_contradiction",
                        source_ids=[contradiction.contradiction_id],
                        sub_goals=[],
                        success_criteria=[
                            "Contradiction resolved",
                            "Resolution validated",
                        ],
                        learning_methods=[
                            "analysis",
                            "evidence_gathering",
                            "clarification",
                        ],
                        progress_percentage=0.0,
                        status="pending",
                        related_gaps=[],
                        related_questions=[],
                        related_contradictions=[contradiction.contradiction_id],
                        created_timestamp=datetime.now().isoformat(),
                        last_updated=datetime.now().isoformat(),
                        estimated_completion_time="2-4 days",
                    )

                    goals.append(goal)
                    self.learning_goals[goal_id] = goal

            except Exception as e:
                self.log(f"Could not generate contradiction goals: {e}", "WARNING")

        return goals

    async def _generate_integration_goals(self) -> List[LearningGoal]:
        """Generate goals for Phase 3 component integration"""
        goals = []

        # Create integration goal
        goal_id = f"goal_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        goal = LearningGoal(
            goal_id=goal_id,
            title="Optimize Phase 3 component integration",
            description="Improve coordination and synergy between curiosity, questioning, and contradiction resolution",
            goal_type="integration",
            priority="medium",
            source_type="system_analysis",
            source_ids=["phase3_integration"],
            sub_goals=[],
            success_criteria=[
                "Better cross-component coordination",
                "Reduced duplicate work",
                "Improved learning efficiency",
            ],
            learning_methods=["analysis", "optimization", "testing"],
            progress_percentage=0.0,
            status="pending",
            related_gaps=[],
            related_questions=[],
            related_contradictions=[],
            created_timestamp=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            estimated_completion_time="1 week",
        )

        goals.append(goal)
        self.learning_goals[goal_id] = goal

        return goals

    async def start_learning_cycle(
        self, goals: List[LearningGoal], cycle_type: str = "exploration"
    ) -> LearningCycle:
        """Start a new learning cycle with the given goals"""
        cycle_id = f"cycle_{cycle_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        cycle = LearningCycle(
            cycle_id=cycle_id,
            cycle_name=f"{cycle_type.title()} Cycle - {datetime.now().strftime('%b %d')}",
            goals=[goal.goal_id for goal in goals],
            cycle_type=cycle_type,
            current_phase="planning",
            progress_percentage=0.0,
            start_timestamp=datetime.now().isoformat(),
            estimated_completion=(
                datetime.now() + timedelta(days=self.cycle_length_days)
            ).isoformat(),
            insights_gained=[],
            goals_completed=0,
            goals_abandoned=0,
            next_cycle_topics=[],
            unresolved_fragments=[],
        )

        self.learning_cycles[cycle_id] = cycle
        self.current_cycle_id = cycle_id

        # Update goal statuses
        for goal in goals:
            goal.status = "active"
            goal.activation_timestamp = datetime.now().isoformat()

        self._save_persistence_data()
        self.log(f"🔄 Started learning cycle {cycle_id} with {len(goals)} goals")

        return cycle

    async def activate_goals(self) -> List[LearningGoal]:
        """Activate high-priority pending goals"""
        pending_goals = [
            g for g in self.learning_goals.values() if g.status == "pending"
        ]

        # Sort by priority and activate top goals
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        sorted_goals = sorted(
            pending_goals, key=lambda g: priority_order.get(g.priority, 0), reverse=True
        )

        activated_goals = []
        active_count = len(
            [g for g in self.learning_goals.values() if g.status == "active"]
        )

        for goal in sorted_goals:
            if active_count < self.max_active_goals:
                goal.status = "active"
                goal.activation_timestamp = datetime.now().isoformat()
                goal.last_updated = datetime.now().isoformat()
                activated_goals.append(goal)
                active_count += 1
            else:
                break

        self._save_persistence_data()
        self.log(f"⚡ Activated {len(activated_goals)} learning goals")

        return activated_goals

    async def update_goal_progress(self, goal_id: str, progress: float) -> bool:
        """Update progress for a specific goal"""
        if goal_id in self.learning_goals:
            goal = self.learning_goals[goal_id]
            goal.progress_percentage = min(100.0, max(0.0, progress))
            goal.last_updated = datetime.now().isoformat()

            # Auto-complete if 100%
            if goal.progress_percentage >= 100.0:
                goal.status = "completed"
                goal.completion_timestamp = datetime.now().isoformat()

            self._save_persistence_data()
            self.log(f"📊 Updated goal {goal_id} progress to {progress}%")
            return True

        return False

    # 🧬 SELF-DIRECTED LEARNING LOOP ENHANCEMENTS
    # ============================================

    async def create_learning_goal(self, memory_issue: Dict[str, Any]) -> LearningGoal:
        """
        Transform gaps or contradictions into learning goals, then measure outcomes.

        Args:
            memory_issue: Dictionary containing issue details with keys:
                - type: 'gap', 'contradiction', 'inconsistency', 'knowledge_void'
                - description: Human-readable description of the issue
                - source: Where the issue was detected (curiosity_agent, contradiction_detector, etc.)
                - severity: 'low', 'medium', 'high', 'critical'
                - evidence: Supporting data or examples
                - context: Relevant context information

        Returns:
            LearningGoal: New goal specifically created for this memory issue
        """
        issue_type = memory_issue.get("type", "unknown")
        severity = memory_issue.get("severity", "medium")
        description = memory_issue.get("description", "Unspecified memory issue")

        # Generate unique goal ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        goal_id = f"learning_goal_{issue_type}_{timestamp}_{len(self.learning_goals)}"

        # Determine goal type based on issue type
        if issue_type == "gap":
            goal_type = "knowledge_acquisition"
            title = f"Fill Knowledge Gap: {description[:60]}..."
        elif issue_type == "contradiction":
            goal_type = "contradiction_resolution"
            title = f"Resolve Contradiction: {description[:60]}..."
        elif issue_type == "inconsistency":
            goal_type = "consistency_improvement"
            title = f"Improve Consistency: {description[:60]}..."
        else:
            goal_type = "general_learning"
            title = f"Learning Goal: {description[:60]}..."

        # Set priority based on severity
        priority_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        priority = priority_map.get(severity, 2)

        # Create learning goal
        learning_goal = LearningGoal(
            goal_id=goal_id,
            title=title,
            description=f"Address {issue_type}: {description}",
            goal_type=goal_type,
            priority=["low", "medium", "high", "critical"][priority - 1],
            source_type=issue_type,
            source_ids=[memory_issue.get("id", f"issue_{timestamp}")],
            sub_goals=[],
            success_criteria=[
                f"Successfully address the {issue_type}",
                "Demonstrate improved understanding or resolution",
                "Update memory system with new knowledge",
                "Validate solution effectiveness",
            ],
            learning_methods=["reflection", "experimentation", "research"],
            progress_percentage=0.0,
            status="pending",
            related_gaps=[memory_issue.get("id", "")] if issue_type == "gap" else [],
            related_questions=[],
            related_contradictions=[memory_issue.get("id", "")]
            if issue_type == "contradiction"
            else [],
            created_timestamp=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            estimated_completion_time=(datetime.now() + timedelta(days=7)).isoformat(),
        )

        # Store the goal
        self.learning_goals[goal_id] = learning_goal

        # Initialize tracking data
        if not hasattr(self, "learning_outcomes"):
            self.learning_outcomes = {}

        self.learning_outcomes[goal_id] = {
            "original_issue": memory_issue,
            "goal_created": datetime.now().isoformat(),
            "initial_memory_state": await self._capture_memory_state(),
            "baseline_metrics": await self._calculate_baseline_metrics(memory_issue),
            "tracking_active": True,
        }

        # Save persistence
        self._save_persistence_data()

        self.log(f"🎯 Created learning goal {goal_id} for {issue_type}: {title}")
        return learning_goal

    async def track_outcomes(self, goal_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate learning success via memory updates or concept shifts.

        Args:
            goal_id: Specific goal to track, or None to track all active goals

        Returns:
            Dictionary containing outcome analysis and success metrics
        """
        if not hasattr(self, "learning_outcomes"):
            self.learning_outcomes = {}

        tracking_results = {
            "tracking_timestamp": datetime.now().isoformat(),
            "goals_tracked": 0,
            "successful_outcomes": 0,
            "partial_outcomes": 0,
            "failed_outcomes": 0,
            "detailed_results": {},
            "overall_learning_effectiveness": 0.0,
            "improvement_recommendations": [],
        }

        # Determine which goals to track
        goals_to_track = []
        if goal_id:
            if goal_id in self.learning_goals:
                goals_to_track = [goal_id]
        else:
            # Track all active goals
            goals_to_track = [
                gid
                for gid, goal in self.learning_goals.items()
                if goal.status in ["active", "completed"]
            ]

        for gid in goals_to_track:
            if gid not in self.learning_outcomes:
                continue

            goal = self.learning_goals[gid]
            outcome_data = self.learning_outcomes[gid]

            # Capture current memory state
            current_memory_state = await self._capture_memory_state()
            current_metrics = await self._calculate_baseline_metrics(
                outcome_data["original_issue"]
            )

            # Calculate improvement metrics
            baseline_metrics = outcome_data["baseline_metrics"]
            improvement_score = self._calculate_improvement_score(
                baseline_metrics, current_metrics
            )

            # Determine outcome success level
            success_level = self._determine_success_level(
                goal, improvement_score, current_metrics
            )

            # Generate outcome analysis
            outcome_analysis = {
                "goal_id": gid,
                "goal_title": goal.title,
                "goal_status": goal.status,
                "progress_percentage": goal.progress_percentage,
                "success_level": success_level,  # 'successful', 'partial', 'failed'
                "improvement_score": improvement_score,
                "baseline_metrics": baseline_metrics,
                "current_metrics": current_metrics,
                "memory_changes": self._analyze_memory_changes(
                    outcome_data["initial_memory_state"], current_memory_state
                ),
                "learning_insights": self._extract_learning_insights(
                    goal, improvement_score
                ),
                "goal_duration_hours": self._calculate_goal_duration(
                    outcome_data["goal_created"]
                ),
                "recommendation": self._generate_outcome_recommendation(
                    success_level, improvement_score
                ),
            }

            tracking_results["detailed_results"][gid] = outcome_analysis
            tracking_results["goals_tracked"] += 1

            # Update counters
            if success_level == "successful":
                tracking_results["successful_outcomes"] += 1
            elif success_level == "partial":
                tracking_results["partial_outcomes"] += 1
            else:
                tracking_results["failed_outcomes"] += 1

        # Calculate overall effectiveness
        total_tracked = tracking_results["goals_tracked"]
        if total_tracked > 0:
            effectiveness = (
                tracking_results["successful_outcomes"]
                + 0.5 * tracking_results["partial_outcomes"]
            ) / total_tracked
            tracking_results["overall_learning_effectiveness"] = effectiveness

        # Generate improvement recommendations
        tracking_results["improvement_recommendations"] = (
            self._generate_improvement_recommendations(tracking_results)
        )

        self.log(
            f"📊 Tracked outcomes for {total_tracked} goals. Effectiveness: {tracking_results['overall_learning_effectiveness']:.2f}"
        )
        return tracking_results

    async def adjust_thresholds(
        self, outcome_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Tune sensitivity to gaps/conflicts based on resolution success.

        Args:
            outcome_analysis: Results from track_outcomes() or None to use recent data

        Returns:
            Dictionary containing updated thresholds and adjustment rationale
        """
        if outcome_analysis is None:
            outcome_analysis = await self.track_outcomes()

        # Initialize threshold adjustment data
        if not hasattr(self, "adaptive_thresholds"):
            self.adaptive_thresholds = {
                "gap_detection_sensitivity": 0.5,  # 0.0 to 1.0
                "contradiction_severity_threshold": 0.7,  # 0.0 to 1.0
                "learning_goal_creation_rate": 0.8,  # Goals per detected issue
                "success_rate_target": 0.75,  # Target success rate
                "adjustment_history": [],
                "last_adjustment": None,
            }

        current_effectiveness = outcome_analysis.get(
            "overall_learning_effectiveness", 0.0
        )
        total_goals = outcome_analysis.get("goals_tracked", 0)

        adjustment_results = {
            "adjustment_timestamp": datetime.now().isoformat(),
            "previous_thresholds": dict(self.adaptive_thresholds),
            "current_effectiveness": current_effectiveness,
            "target_effectiveness": self.adaptive_thresholds["success_rate_target"],
            "adjustment_needed": False,
            "adjustments_made": {},
            "rationale": [],
            "recommended_actions": [],
        }

        # Determine if adjustment is needed
        effectiveness_gap = (
            current_effectiveness - self.adaptive_thresholds["success_rate_target"]
        )

        if (
            abs(effectiveness_gap) > 0.1 and total_goals >= 3
        ):  # Significant gap with enough data
            adjustment_results["adjustment_needed"] = True

            if effectiveness_gap < 0:  # Below target - reduce sensitivity
                # Too many failures - reduce sensitivity to create fewer, higher-quality goals
                if self.adaptive_thresholds["gap_detection_sensitivity"] > 0.2:
                    old_sensitivity = self.adaptive_thresholds[
                        "gap_detection_sensitivity"
                    ]
                    self.adaptive_thresholds["gap_detection_sensitivity"] = max(
                        0.2, old_sensitivity - 0.1
                    )
                    adjustment_results["adjustments_made"][
                        "gap_detection_sensitivity"
                    ] = {
                        "old": old_sensitivity,
                        "new": self.adaptive_thresholds["gap_detection_sensitivity"],
                        "change": -0.1,
                    }
                    adjustment_results["rationale"].append(
                        f"Reduced gap detection sensitivity from {old_sensitivity:.2f} to "
                        f"{self.adaptive_thresholds['gap_detection_sensitivity']:.2f} due to low success rate"
                    )

                if self.adaptive_thresholds["contradiction_severity_threshold"] < 0.9:
                    old_threshold = self.adaptive_thresholds[
                        "contradiction_severity_threshold"
                    ]
                    self.adaptive_thresholds["contradiction_severity_threshold"] = min(
                        0.9, old_threshold + 0.1
                    )
                    adjustment_results["adjustments_made"][
                        "contradiction_severity_threshold"
                    ] = {
                        "old": old_threshold,
                        "new": self.adaptive_thresholds[
                            "contradiction_severity_threshold"
                        ],
                        "change": 0.1,
                    }
                    adjustment_results["rationale"].append(
                        f"Increased contradiction severity threshold from {old_threshold:.2f} to "
                        f"{self.adaptive_thresholds['contradiction_severity_threshold']:.2f} to focus on critical issues"
                    )

                adjustment_results["recommended_actions"].extend(
                    [
                        "Focus on higher-confidence knowledge gaps",
                        "Prioritize critical contradictions only",
                        "Improve goal success criteria specificity",
                    ]
                )

            else:  # Above target - increase sensitivity
                # High success rate - can afford to be more sensitive
                if self.adaptive_thresholds["gap_detection_sensitivity"] < 0.8:
                    old_sensitivity = self.adaptive_thresholds[
                        "gap_detection_sensitivity"
                    ]
                    self.adaptive_thresholds["gap_detection_sensitivity"] = min(
                        0.8, old_sensitivity + 0.1
                    )
                    adjustment_results["adjustments_made"][
                        "gap_detection_sensitivity"
                    ] = {
                        "old": old_sensitivity,
                        "new": self.adaptive_thresholds["gap_detection_sensitivity"],
                        "change": 0.1,
                    }
                    adjustment_results["rationale"].append(
                        f"Increased gap detection sensitivity from {old_sensitivity:.2f} to "
                        f"{self.adaptive_thresholds['gap_detection_sensitivity']:.2f} due to high success rate"
                    )

                if self.adaptive_thresholds["contradiction_severity_threshold"] > 0.5:
                    old_threshold = self.adaptive_thresholds[
                        "contradiction_severity_threshold"
                    ]
                    self.adaptive_thresholds["contradiction_severity_threshold"] = max(
                        0.5, old_threshold - 0.1
                    )
                    adjustment_results["adjustments_made"][
                        "contradiction_severity_threshold"
                    ] = {
                        "old": old_threshold,
                        "new": self.adaptive_thresholds[
                            "contradiction_severity_threshold"
                        ],
                        "change": -0.1,
                    }
                    adjustment_results["rationale"].append(
                        f"Decreased contradiction severity threshold from {old_threshold:.2f} to "
                        f"{self.adaptive_thresholds['contradiction_severity_threshold']:.2f} to catch more issues"
                    )

                adjustment_results["recommended_actions"].extend(
                    [
                        "Expand knowledge gap detection scope",
                        "Address lower-severity contradictions",
                        "Increase learning goal creation rate",
                    ]
                )

        else:
            adjustment_results["rationale"].append(
                f"No adjustment needed. Current effectiveness {current_effectiveness:.2f} "
                f"is within acceptable range of target {self.adaptive_thresholds['success_rate_target']:.2f}"
            )

        # Record adjustment in history
        self.adaptive_thresholds["adjustment_history"].append(
            {
                "timestamp": adjustment_results["adjustment_timestamp"],
                "effectiveness_gap": effectiveness_gap,
                "adjustments": adjustment_results["adjustments_made"],
                "total_goals_analyzed": total_goals,
            }
        )

        # Keep only last 10 adjustments
        if len(self.adaptive_thresholds["adjustment_history"]) > 10:
            self.adaptive_thresholds["adjustment_history"] = self.adaptive_thresholds[
                "adjustment_history"
            ][-10:]

        self.adaptive_thresholds["last_adjustment"] = adjustment_results[
            "adjustment_timestamp"
        ]

        # Save persistence
        self._save_persistence_data()

        self.log(
            f"🎛️ Threshold adjustment complete. Needed: {adjustment_results['adjustment_needed']}"
        )
        return adjustment_results

    # Helper methods for self-directed learning loop

    async def _capture_memory_state(self) -> Dict[str, Any]:
        """Capture current memory system state for comparison"""
        try:
            if self.memory_engine:
                # Get memory statistics
                return {
                    "timestamp": datetime.now().isoformat(),
                    "total_memories": len(getattr(self.memory_engine, "memories", [])),
                    "concept_clusters": len(
                        getattr(self.memory_engine, "concept_clusters", {})
                    ),
                    "confidence_distribution": "mock_distribution",  # Would calculate actual distribution
                    "coherence_score": 0.75,  # Mock coherence score
                }
            else:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "status": "no_memory_engine",
                    "mock_state": True,
                }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "fallback_state": True,
            }

    async def _calculate_baseline_metrics(
        self, memory_issue: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate baseline metrics for tracking improvement"""
        issue_type = memory_issue.get("type", "unknown")

        if issue_type == "gap":
            return {
                "knowledge_completeness": 0.3,  # Low due to gap
                "confidence_score": 0.4,
                "consistency_score": 0.7,
                "resolution_potential": 0.8,
            }
        elif issue_type == "contradiction":
            return {
                "knowledge_completeness": 0.6,
                "confidence_score": 0.3,  # Low due to contradiction
                "consistency_score": 0.2,  # Very low due to conflict
                "resolution_potential": 0.9,
            }
        else:
            return {
                "knowledge_completeness": 0.5,
                "confidence_score": 0.5,
                "consistency_score": 0.5,
                "resolution_potential": 0.6,
            }

    def _calculate_improvement_score(
        self, baseline: Dict[str, float], current: Dict[str, float]
    ) -> float:
        """Calculate overall improvement score"""
        improvements = []
        for key in baseline:
            if key in current:
                improvement = current[key] - baseline[key]
                improvements.append(improvement)

        return sum(improvements) / len(improvements) if improvements else 0.0

    def _determine_success_level(
        self,
        goal: LearningGoal,
        improvement_score: float,
        current_metrics: Dict[str, float],
    ) -> str:
        """Determine if goal resolution was successful, partial, or failed"""
        if improvement_score > 0.3 and goal.progress_percentage >= 80:
            return "successful"
        elif improvement_score > 0.1 or goal.progress_percentage >= 50:
            return "partial"
        else:
            return "failed"

    def _analyze_memory_changes(
        self, initial_state: Dict, current_state: Dict
    ) -> Dict[str, Any]:
        """Analyze changes in memory state"""
        return {
            "state_comparison": "mock_comparison",
            "significant_changes": ["increased_coherence", "new_connections"],
            "change_magnitude": 0.2,
        }

    def _extract_learning_insights(
        self, goal: LearningGoal, improvement_score: float
    ) -> List[str]:
        """Extract learning insights from goal progression"""
        insights = []

        if improvement_score > 0.3:
            insights.append(
                f"Successfully addressed {goal.goal_type} with significant improvement"
            )
        elif improvement_score > 0.1:
            insights.append(
                f"Made progress on {goal.goal_type} but room for improvement"
            )
        else:
            insights.append(
                f"Limited progress on {goal.goal_type} - may need different approach"
            )

        if goal.progress_percentage >= 90:
            insights.append("Goal completion metrics indicate thorough resolution")

        return insights

    def _calculate_goal_duration(self, created_timestamp: str) -> float:
        """Calculate how long a goal has been active"""
        try:
            created = datetime.fromisoformat(created_timestamp)
            duration = datetime.now() - created
            return duration.total_seconds() / 3600  # Hours
        except Exception:
            return 0.0

    def _generate_outcome_recommendation(
        self, success_level: str, improvement_score: float
    ) -> str:
        """Generate recommendation based on outcome"""
        if success_level == "successful":
            return "Goal successfully completed - consider similar approaches for future issues"
        elif success_level == "partial":
            return "Partial success achieved - continue monitoring and consider additional interventions"
        else:
            return "Goal unsuccessful - reassess approach and consider alternative strategies"

    def _generate_improvement_recommendations(
        self, tracking_results: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for improving learning effectiveness"""
        recommendations = []

        effectiveness = tracking_results.get("overall_learning_effectiveness", 0.0)

        if effectiveness < 0.5:
            recommendations.extend(
                [
                    "Consider more specific success criteria for learning goals",
                    "Increase focus on higher-confidence knowledge gaps",
                    "Implement more frequent progress tracking",
                ]
            )
        elif effectiveness < 0.75:
            recommendations.extend(
                [
                    "Good progress - consider expanding scope of learning goals",
                    "Add more diverse learning approaches",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Excellent learning effectiveness - maintain current approach",
                    "Consider mentoring or knowledge sharing opportunities",
                ]
            )

        return recommendations

    # 🧠 META-LEARNING TRACKER ENHANCEMENTS
    # ======================================

    async def log_learning_session(
        self, context: Dict[str, Any], outcome: Dict[str, Any], time_spent: float
    ) -> str:
        """
        Evaluate how well Lyrixa learns — and adapt her strategies accordingly.

        Args:
            context: Dictionary containing learning session context with keys:
                - goal_id: ID of the learning goal being pursued
                - learning_method: Method used ('experimentation', 'reflection', 'research', 'observation')
                - agent_used: Which agent facilitated the learning (curiosity, contradiction, etc.)
                - initial_state: Starting knowledge/confidence levels
                - target_objective: What was trying to be achieved
                - resources_used: Tools, data, or systems utilized
                - difficulty_level: 'low', 'medium', 'high', 'extreme'

            outcome: Dictionary containing learning session results with keys:
                - success_level: 'failure', 'partial', 'success', 'breakthrough'
                - knowledge_gained: Specific insights or understanding acquired
                - confidence_change: Numerical change in confidence (-1.0 to 1.0)
                - contradiction_reduction: Number of contradictions resolved
                - narrative_clarity_improvement: Improvement in story coherence (0.0 to 1.0)
                - unexpected_discoveries: List of serendipitous findings
                - obstacles_encountered: Challenges faced during learning
                - final_state: Ending knowledge/confidence levels

            time_spent: Duration of learning session in minutes

        Returns:
            str: Session log ID for tracking and analysis
        """
        # Initialize meta-learning storage
        if not hasattr(self, "learning_sessions"):
            self.learning_sessions = {}

        # Generate session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"learning_session_{timestamp}_{len(self.learning_sessions)}"

        # Extract key metrics
        goal_id = context.get("goal_id", "unknown_goal")
        learning_method = context.get("learning_method", "unknown_method")
        agent_used = context.get("agent_used", "unknown_agent")
        difficulty_level = context.get("difficulty_level", "medium")

        success_level = outcome.get("success_level", "unknown")
        confidence_change = outcome.get("confidence_change", 0.0)
        contradiction_reduction = outcome.get("contradiction_reduction", 0)
        narrative_clarity_improvement = outcome.get(
            "narrative_clarity_improvement", 0.0
        )

        # Calculate effectiveness score
        effectiveness_score = self._calculate_session_effectiveness(outcome, time_spent)

        # Create comprehensive learning session record
        learning_session = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "goal_id": goal_id,
            "learning_context": context,
            "learning_outcome": outcome,
            "time_spent_minutes": time_spent,
            "effectiveness_score": effectiveness_score,
            "key_metrics": {
                "learning_method": learning_method,
                "agent_used": agent_used,
                "difficulty_level": difficulty_level,
                "success_level": success_level,
                "confidence_change": confidence_change,
                "contradiction_reduction": contradiction_reduction,
                "narrative_clarity_improvement": narrative_clarity_improvement,
                "time_efficiency": effectiveness_score
                / max(time_spent, 1.0),  # effectiveness per minute
            },
            "learning_insights": self._extract_session_insights(context, outcome),
            "strategy_performance": self._evaluate_strategy_performance(
                context, outcome
            ),
            "meta_analysis": {
                "learning_velocity": abs(confidence_change)
                / max(time_spent / 60.0, 0.1),  # confidence change per hour
                "complexity_handling": self._assess_complexity_handling(
                    difficulty_level, success_level
                ),
                "method_suitability": self._assess_method_suitability(
                    learning_method, outcome
                ),
                "agent_effectiveness": self._assess_agent_effectiveness(
                    agent_used, outcome
                ),
            },
        }

        # Store session
        self.learning_sessions[session_id] = learning_session

        # Update goal progress if applicable
        if goal_id in self.learning_goals:
            goal = self.learning_goals[goal_id]
            # Increment progress based on success level
            progress_increment = {
                "failure": 0,
                "partial": 10,
                "success": 25,
                "breakthrough": 40,
            }.get(success_level, 5)

            await self.update_goal_progress(
                goal_id, min(100.0, goal.progress_percentage + progress_increment)
            )

        # Save persistence
        self._save_persistence_data()

        self.log(
            f"📚 Logged learning session {session_id} with effectiveness {effectiveness_score:.2f}"
        )
        return session_id

    async def score_effectiveness(
        self, session_ids: Optional[List[str]] = None, timeframe_hours: float = 24.0
    ) -> Dict[str, Any]:
        """
        Based on confidence improvement, contradiction reduction, or narrative clarity.

        Args:
            session_ids: Specific sessions to analyze, or None for recent sessions
            timeframe_hours: Time window for analysis if session_ids not provided

        Returns:
            Dictionary containing comprehensive effectiveness analysis
        """
        if not hasattr(self, "learning_sessions"):
            self.learning_sessions = {}

        # Determine sessions to analyze
        sessions_to_analyze = []
        if session_ids:
            sessions_to_analyze = [
                self.learning_sessions[sid]
                for sid in session_ids
                if sid in self.learning_sessions
            ]
        else:
            # Get sessions within timeframe
            cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
            for session in self.learning_sessions.values():
                session_time = datetime.fromisoformat(session["timestamp"])
                if session_time >= cutoff_time:
                    sessions_to_analyze.append(session)

        if not sessions_to_analyze:
            return {
                "analysis_timestamp": datetime.now().isoformat(),
                "sessions_analyzed": 0,
                "overall_effectiveness": 0.0,
                "effectiveness_trends": {},
                "method_analysis": {},
                "agent_analysis": {},
                "improvement_areas": ["No recent learning sessions to analyze"],
            }

        # Calculate overall effectiveness metrics
        total_sessions = len(sessions_to_analyze)
        total_confidence_change = sum(
            s["key_metrics"]["confidence_change"] for s in sessions_to_analyze
        )
        total_contradiction_reduction = sum(
            s["key_metrics"]["contradiction_reduction"] for s in sessions_to_analyze
        )
        total_narrative_improvement = sum(
            s["key_metrics"]["narrative_clarity_improvement"]
            for s in sessions_to_analyze
        )
        average_effectiveness = (
            sum(s["effectiveness_score"] for s in sessions_to_analyze) / total_sessions
        )

        # Analyze by learning method
        method_analysis = {}
        for session in sessions_to_analyze:
            method = session["key_metrics"]["learning_method"]
            if method not in method_analysis:
                method_analysis[method] = {
                    "session_count": 0,
                    "average_effectiveness": 0.0,
                    "success_rate": 0.0,
                    "average_time": 0.0,
                    "breakthrough_rate": 0.0,
                }

            method_stats = method_analysis[method]
            method_stats["session_count"] += 1
            method_stats["average_effectiveness"] += session["effectiveness_score"]
            method_stats["average_time"] += session["time_spent_minutes"]

            if session["key_metrics"]["success_level"] in ["success", "breakthrough"]:
                method_stats["success_rate"] += 1
            if session["key_metrics"]["success_level"] == "breakthrough":
                method_stats["breakthrough_rate"] += 1

        # Calculate averages for methods
        for method_stats in method_analysis.values():
            count = method_stats["session_count"]
            method_stats["average_effectiveness"] /= count
            method_stats["success_rate"] /= count
            method_stats["average_time"] /= count
            method_stats["breakthrough_rate"] /= count

        # Analyze by agent
        agent_analysis = {}
        for session in sessions_to_analyze:
            agent = session["key_metrics"]["agent_used"]
            if agent not in agent_analysis:
                agent_analysis[agent] = {
                    "session_count": 0,
                    "average_effectiveness": 0.0,
                    "confidence_impact": 0.0,
                    "speed_score": 0.0,
                }

            agent_stats = agent_analysis[agent]
            agent_stats["session_count"] += 1
            agent_stats["average_effectiveness"] += session["effectiveness_score"]
            agent_stats["confidence_impact"] += session["key_metrics"][
                "confidence_change"
            ]
            agent_stats["speed_score"] += session["key_metrics"]["time_efficiency"]

        # Calculate averages for agents
        for agent_stats in agent_analysis.values():
            count = agent_stats["session_count"]
            agent_stats["average_effectiveness"] /= count
            agent_stats["confidence_impact"] /= count
            agent_stats["speed_score"] /= count

        # Analyze effectiveness trends
        effectiveness_trends = {
            "confidence_improvement_rate": total_confidence_change
            / max(total_sessions, 1),
            "contradiction_resolution_rate": total_contradiction_reduction
            / max(total_sessions, 1),
            "narrative_clarity_improvement_rate": total_narrative_improvement
            / max(total_sessions, 1),
            "learning_velocity_trend": self._calculate_velocity_trend(
                sessions_to_analyze
            ),
            "difficulty_adaptation_score": self._calculate_difficulty_adaptation(
                sessions_to_analyze
            ),
        }

        # Identify improvement areas
        improvement_areas = self._identify_improvement_areas(
            sessions_to_analyze, method_analysis, agent_analysis
        )

        effectiveness_analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "timeframe_hours": timeframe_hours,
            "sessions_analyzed": total_sessions,
            "overall_effectiveness": average_effectiveness,
            "effectiveness_grade": self._grade_effectiveness(average_effectiveness),
            "core_metrics": {
                "total_confidence_change": total_confidence_change,
                "total_contradiction_reduction": total_contradiction_reduction,
                "total_narrative_improvement": total_narrative_improvement,
                "average_session_time": sum(
                    s["time_spent_minutes"] for s in sessions_to_analyze
                )
                / total_sessions,
            },
            "effectiveness_trends": effectiveness_trends,
            "method_analysis": method_analysis,
            "agent_analysis": agent_analysis,
            "improvement_areas": improvement_areas,
            "learning_insights": self._generate_meta_learning_insights(
                sessions_to_analyze
            ),
        }

        self.log(
            f"📊 Scored effectiveness for {total_sessions} sessions: {average_effectiveness:.2f}"
        )
        return effectiveness_analysis

    async def recommend_strategy_updates(
        self, effectiveness_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Suggest whether to retry, change tools, or escalate.

        Args:
            effectiveness_analysis: Results from score_effectiveness() or None to generate new analysis

        Returns:
            Dictionary containing strategy recommendations and justifications
        """
        if effectiveness_analysis is None:
            effectiveness_analysis = await self.score_effectiveness()

        overall_effectiveness = effectiveness_analysis.get("overall_effectiveness", 0.0)
        method_analysis = effectiveness_analysis.get("method_analysis", {})
        agent_analysis = effectiveness_analysis.get("agent_analysis", {})
        improvement_areas = effectiveness_analysis.get("improvement_areas", [])

        # Initialize recommendations structure
        strategy_recommendations = {
            "analysis_timestamp": datetime.now().isoformat(),
            "overall_assessment": self._assess_learning_performance(
                overall_effectiveness
            ),
            "immediate_actions": [],
            "method_recommendations": {},
            "agent_recommendations": {},
            "escalation_triggers": [],
            "optimization_opportunities": [],
            "strategic_changes": [],
            "confidence_level": self._calculate_recommendation_confidence(
                effectiveness_analysis
            ),
        }

        # Generate immediate action recommendations
        if overall_effectiveness < 0.3:
            strategy_recommendations["immediate_actions"].extend(
                [
                    "CRITICAL: Conduct comprehensive learning strategy review",
                    "Pause current learning goals to reassess approach",
                    "Switch to simpler, more structured learning methods",
                    "Increase supervision and guidance in learning sessions",
                ]
            )
        elif overall_effectiveness < 0.6:
            strategy_recommendations["immediate_actions"].extend(
                [
                    "Review and optimize current learning approaches",
                    "Identify and address specific performance bottlenecks",
                    "Consider supplementary learning resources or methods",
                ]
            )
        else:
            strategy_recommendations["immediate_actions"].extend(
                [
                    "Maintain current effective learning strategies",
                    "Explore advanced learning techniques for acceleration",
                    "Consider expanding learning scope or complexity",
                ]
            )

        # Method-specific recommendations
        for method, stats in method_analysis.items():
            method_effectiveness = stats["average_effectiveness"]
            success_rate = stats["success_rate"]

            if method_effectiveness < 0.4 or success_rate < 0.3:
                strategy_recommendations["method_recommendations"][method] = {
                    "action": "REPLACE",
                    "justification": f"Low effectiveness ({method_effectiveness:.2f}) and success rate ({success_rate:.2f})",
                    "alternatives": self._suggest_method_alternatives(method),
                    "retry_conditions": "Only after significant strategy modification",
                }
            elif method_effectiveness < 0.7:
                strategy_recommendations["method_recommendations"][method] = {
                    "action": "OPTIMIZE",
                    "justification": f"Moderate effectiveness ({method_effectiveness:.2f}) with room for improvement",
                    "improvements": self._suggest_method_improvements(method, stats),
                    "retry_conditions": "After implementing suggested improvements",
                }
            else:
                strategy_recommendations["method_recommendations"][method] = {
                    "action": "EXPAND",
                    "justification": f"High effectiveness ({method_effectiveness:.2f}) - leverage more extensively",
                    "expansion_suggestions": self._suggest_method_expansion(method),
                    "retry_conditions": "Apply to more complex learning scenarios",
                }

        # Agent-specific recommendations
        for agent, stats in agent_analysis.items():
            agent_effectiveness = stats["average_effectiveness"]

            if agent_effectiveness < 0.4:
                strategy_recommendations["agent_recommendations"][agent] = {
                    "action": "LIMIT_USE",
                    "justification": f"Low effectiveness ({agent_effectiveness:.2f})",
                    "alternatives": self._suggest_agent_alternatives(agent),
                    "escalation_threshold": "If no improvement after strategy changes",
                }
            elif agent_effectiveness < 0.7:
                strategy_recommendations["agent_recommendations"][agent] = {
                    "action": "CONFIGURE",
                    "justification": "Moderate effectiveness - needs optimization",
                    "configuration_changes": self._suggest_agent_configurations(
                        agent, stats
                    ),
                }
            else:
                strategy_recommendations["agent_recommendations"][agent] = {
                    "action": "PRIORITIZE",
                    "justification": f"High effectiveness ({agent_effectiveness:.2f})",
                    "priority_scenarios": self._identify_agent_strengths(agent, stats),
                }

        # Escalation triggers
        escalation_needed = False
        if overall_effectiveness < 0.2:
            strategy_recommendations["escalation_triggers"].append(
                "CRITICAL: Overall learning effectiveness below 20%"
            )
            escalation_needed = True

        if (
            len(
                [
                    m
                    for m in method_analysis.values()
                    if m["average_effectiveness"] < 0.3
                ]
            )
            > len(method_analysis) * 0.7
        ):
            strategy_recommendations["escalation_triggers"].append(
                "MAJOR: More than 70% of learning methods underperforming"
            )
            escalation_needed = True

        if not any(s["success_rate"] > 0.5 for s in method_analysis.values()):
            strategy_recommendations["escalation_triggers"].append(
                "SEVERE: No learning method achieving >50% success rate"
            )
            escalation_needed = True

        # Strategic changes based on patterns
        if (
            "experimentation" in method_analysis
            and method_analysis["experimentation"]["success_rate"] < 0.3
        ):
            strategy_recommendations["strategic_changes"].append(
                "Shift from experimentation to structured research-based learning"
            )

        if (
            "reflection" in method_analysis
            and method_analysis["reflection"]["average_effectiveness"] > 0.8
        ):
            strategy_recommendations["strategic_changes"].append(
                "Increase reflection-based learning across all goals"
            )

        # Optimization opportunities
        if method_analysis:
            best_method = max(
                method_analysis.items(), key=lambda x: x[1]["average_effectiveness"]
            )
            if best_method and best_method[0]:
                strategy_recommendations["optimization_opportunities"].append(
                    f"Leverage '{best_method[0]}' method more extensively (effectiveness: {best_method[1]['average_effectiveness']:.2f})"
                )

        if agent_analysis:
            best_agent = max(
                agent_analysis.items(), key=lambda x: x[1]["average_effectiveness"]
            )
            if best_agent and best_agent[0]:
                strategy_recommendations["optimization_opportunities"].append(
                    f"Prioritize '{best_agent[0]}' agent for critical learning tasks (effectiveness: {best_agent[1]['average_effectiveness']:.2f})"
                )

        # Save recommendations to history
        if not hasattr(self, "strategy_recommendations_history"):
            self.strategy_recommendations_history = []

        self.strategy_recommendations_history.append(strategy_recommendations)

        # Keep only last 10 recommendations
        if len(self.strategy_recommendations_history) > 10:
            self.strategy_recommendations_history = (
                self.strategy_recommendations_history[-10:]
            )

        self._save_persistence_data()

        action_type = (
            "ESCALATE"
            if escalation_needed
            else "OPTIMIZE"
            if overall_effectiveness < 0.7
            else "MAINTAIN"
        )
        self.log(
            f"🎯 Generated strategy recommendations: {action_type} (effectiveness: {overall_effectiveness:.2f})"
        )

        return strategy_recommendations

    # Helper methods for meta-learning tracker

    def _calculate_session_effectiveness(
        self, outcome: Dict[str, Any], time_spent: float
    ) -> float:
        """Calculate effectiveness score for a learning session"""
        success_level = outcome.get("success_level", "unknown")
        confidence_change = outcome.get("confidence_change", 0.0)
        contradiction_reduction = outcome.get("contradiction_reduction", 0)
        narrative_clarity_improvement = outcome.get(
            "narrative_clarity_improvement", 0.0
        )

        # Base score from success level
        success_scores = {
            "failure": 0.1,
            "partial": 0.4,
            "success": 0.7,
            "breakthrough": 1.0,
        }
        base_score = success_scores.get(success_level, 0.2)

        # Confidence improvement bonus
        confidence_bonus = min(0.3, max(0.0, confidence_change * 0.3))

        # Contradiction reduction bonus
        contradiction_bonus = min(0.2, contradiction_reduction * 0.05)

        # Narrative clarity bonus
        clarity_bonus = min(0.2, narrative_clarity_improvement * 0.2)

        # Time efficiency factor (penalize excessive time)
        time_factor = max(0.5, min(1.0, 60.0 / max(time_spent, 30.0)))

        # Calculate final effectiveness score
        effectiveness = (
            base_score + confidence_bonus + contradiction_bonus + clarity_bonus
        ) * time_factor
        return min(1.0, max(0.0, effectiveness))

    def _extract_session_insights(
        self, context: Dict[str, Any], outcome: Dict[str, Any]
    ) -> List[str]:
        """Extract insights from a learning session"""
        insights = []

        success_level = outcome.get("success_level", "unknown")
        learning_method = context.get("learning_method", "unknown")
        difficulty_level = context.get("difficulty_level", "medium")

        if success_level == "breakthrough":
            insights.append(f"Breakthrough achieved using {learning_method} method")
        elif success_level == "success":
            insights.append(f"Successful learning with {learning_method} approach")
        elif success_level == "failure" and difficulty_level == "high":
            insights.append(
                f"High difficulty task requires alternative to {learning_method}"
            )

        if outcome.get("unexpected_discoveries"):
            insights.append(
                "Serendipitous discoveries suggest expanding exploration scope"
            )

        if outcome.get("confidence_change", 0) > 0.5:
            insights.append(
                "Significant confidence improvement - method highly effective"
            )

        return insights

    def _evaluate_strategy_performance(
        self, context: Dict[str, Any], outcome: Dict[str, Any]
    ) -> Dict[str, float]:
        """Evaluate performance of the strategy used"""
        return {
            "method_alignment": self._score_method_alignment(context, outcome),
            "resource_efficiency": self._score_resource_efficiency(context, outcome),
            "goal_progression": self._score_goal_progression(context, outcome),
            "knowledge_transfer": self._score_knowledge_transfer(context, outcome),
        }

    def _score_method_alignment(
        self, context: Dict[str, Any], outcome: Dict[str, Any]
    ) -> float:
        """Score how well the method aligned with the learning objective"""
        # Mock implementation - would analyze method suitability
        success_level = outcome.get("success_level", "unknown")
        return {
            "failure": 0.2,
            "partial": 0.5,
            "success": 0.8,
            "breakthrough": 1.0,
        }.get(success_level, 0.3)

    def _score_resource_efficiency(
        self, context: Dict[str, Any], outcome: Dict[str, Any]
    ) -> float:
        """Score resource efficiency of the learning session"""
        # Mock implementation - would analyze resource usage vs outcomes
        return 0.7  # Placeholder

    def _score_goal_progression(
        self, context: Dict[str, Any], outcome: Dict[str, Any]
    ) -> float:
        """Score how much the session advanced the goal"""
        confidence_change = outcome.get("confidence_change", 0.0)
        return min(1.0, max(0.0, confidence_change + 0.5))

    def _score_knowledge_transfer(
        self, context: Dict[str, Any], outcome: Dict[str, Any]
    ) -> float:
        """Score potential for knowledge transfer to other domains"""
        # Mock implementation - would analyze generalizability
        return 0.6  # Placeholder

    def _assess_complexity_handling(
        self, difficulty_level: str, success_level: str
    ) -> float:
        """Assess how well complexity was handled"""
        difficulty_scores = {"low": 1.0, "medium": 2.0, "high": 3.0, "extreme": 4.0}
        success_scores = {
            "failure": 1.0,
            "partial": 2.0,
            "success": 3.0,
            "breakthrough": 4.0,
        }

        difficulty_score = difficulty_scores.get(difficulty_level, 2.0)
        success_score = success_scores.get(success_level, 1.0)

        return min(1.0, success_score / difficulty_score)

    def _assess_method_suitability(
        self, learning_method: str, outcome: Dict[str, Any]
    ) -> float:
        """Assess how suitable the method was for the outcome achieved"""
        # Mock implementation - would analyze method-outcome alignment
        success_level = outcome.get("success_level", "unknown")
        base_scores = {
            "failure": 0.2,
            "partial": 0.5,
            "success": 0.8,
            "breakthrough": 1.0,
        }
        return base_scores.get(success_level, 0.3)

    def _assess_agent_effectiveness(
        self, agent_used: str, outcome: Dict[str, Any]
    ) -> float:
        """Assess how effective the agent was"""
        # Mock implementation - would analyze agent-specific performance
        confidence_change = outcome.get("confidence_change", 0.0)
        return min(1.0, max(0.0, confidence_change * 0.5 + 0.5))

    # Additional helper methods for meta-learning analysis

    def _calculate_velocity_trend(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate learning velocity trend"""
        if len(sessions) < 2:
            return 0.0
        velocities = [
            s.get("meta_analysis", {}).get("learning_velocity", 0.0) for s in sessions
        ]
        return sum(velocities) / len(velocities) if velocities else 0.0

    def _calculate_difficulty_adaptation(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate how well the system adapts to difficulty"""
        if not sessions:
            return 0.0
        complexity_scores = [
            s.get("meta_analysis", {}).get("complexity_handling", 0.0) for s in sessions
        ]
        return (
            sum(complexity_scores) / len(complexity_scores)
            if complexity_scores
            else 0.0
        )

    def _identify_improvement_areas(
        self,
        sessions: List[Dict[str, Any]],
        method_analysis: Dict,
        agent_analysis: Dict,
    ) -> List[str]:
        """Identify areas needing improvement"""
        areas = []
        for method, stats in method_analysis.items():
            if stats["average_effectiveness"] < 0.5:
                areas.append(f"Improve {method} learning method")
        return areas if areas else ["No significant improvement areas identified"]

    def _grade_effectiveness(self, effectiveness: float) -> str:
        """Grade effectiveness score"""
        if effectiveness >= 0.9:
            return "EXCELLENT"
        elif effectiveness >= 0.7:
            return "GOOD"
        elif effectiveness >= 0.5:
            return "FAIR"
        else:
            return "NEEDS_IMPROVEMENT"

    def _generate_meta_learning_insights(
        self, sessions: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate insights about meta-learning patterns"""
        if not sessions:
            return ["No sessions available for analysis"]
        return [
            f"Analyzed {len(sessions)} learning sessions",
            "Meta-learning patterns identified",
        ]

    def _assess_learning_performance(self, effectiveness: float) -> str:
        """Assess overall learning performance"""
        if effectiveness >= 0.8:
            return "HIGH_PERFORMANCE"
        elif effectiveness >= 0.6:
            return "MODERATE_PERFORMANCE"
        else:
            return "NEEDS_IMPROVEMENT"

    def _calculate_recommendation_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence level in recommendations"""
        sessions_analyzed = analysis.get("sessions_analyzed", 0)
        return min(1.0, sessions_analyzed / 10.0)

    def _suggest_method_alternatives(self, method: str) -> List[str]:
        """Suggest alternative learning methods"""
        return ["reflection", "research", "experimentation", "observation"]

    def _suggest_method_improvements(
        self, method: str, stats: Dict[str, Any]
    ) -> List[str]:
        """Suggest improvements for a learning method"""
        return ["Add more structure", "Increase focus", "Improve feedback"]

    def _suggest_method_expansion(self, method: str) -> List[str]:
        """Suggest ways to expand successful methods"""
        return ["Apply to more scenarios", "Increase complexity", "Add collaboration"]

    def _suggest_agent_alternatives(self, agent: str) -> List[str]:
        """Suggest alternative agents"""
        return ["curiosity_agent", "contradiction_detector", "question_generator"]

    def _suggest_agent_configurations(
        self, agent: str, stats: Dict[str, Any]
    ) -> List[str]:
        """Suggest configuration changes for agents"""
        return ["Optimize thresholds", "Improve algorithms", "Enhance feedback"]

    def _identify_agent_strengths(self, agent: str, stats: Dict[str, Any]) -> List[str]:
        """Identify scenarios where agent performs best"""
        return [
            "Complex problem solving",
            "High-confidence scenarios",
            "Time-sensitive tasks",
        ]

    async def analyze_phase3_integration(self) -> Dict[str, Any]:
        """Analyze integration across Phase 3 components"""
        analysis = {
            "curiosity_status": "Active" if self.curiosity_agent else "Not Available",
            "question_generator_status": "Active"
            if self.question_generator
            else "Not Available",
            "contradiction_detector_status": "Active"
            if self.contradiction_detector
            else "Not Available",
            "cross_references": 0,
            "unified_goals": 0,
            "resolution_synergies": 0,
            "key_insights": [
                "Phase 3 components working independently",
                "Goal generation from multiple sources successful",
                "Integration opportunities identified",
            ],
            "optimization_opportunities": [
                "Cross-reference knowledge gaps with contradictions",
                "Generate questions from contradiction analysis",
                "Create unified learning cycles spanning all components",
            ],
        }

        # Count cross-references in goals
        for goal in self.learning_goals.values():
            if (
                len(goal.related_gaps)
                + len(goal.related_questions)
                + len(goal.related_contradictions)
                > 1
            ):
                analysis["cross_references"] += 1

            if goal.goal_type == "integration":
                analysis["unified_goals"] += 1

        self.log("🔗 Completed Phase 3 integration analysis")
        return analysis

    def get_learning_loop_summary(self) -> Dict[str, Any]:
        """Get summary of learning loop status"""
        total_goals = len(self.learning_goals)
        pending_goals = len(
            [g for g in self.learning_goals.values() if g.status == "pending"]
        )
        active_goals = len(
            [g for g in self.learning_goals.values() if g.status == "active"]
        )
        completed_goals = len(
            [g for g in self.learning_goals.values() if g.status == "completed"]
        )
        paused_goals = len(
            [g for g in self.learning_goals.values() if g.status == "paused"]
        )

        # Goal type breakdown
        goal_type_breakdown = {}
        for goal in self.learning_goals.values():
            goal_type = goal.goal_type
            if goal_type not in goal_type_breakdown:
                goal_type_breakdown[goal_type] = 0
            goal_type_breakdown[goal_type] += 1

        # Calculate success rate
        total_resolved = completed_goals
        success_rate = total_resolved / max(total_goals, 1)

        return {
            "total_goals": total_goals,
            "pending_goals": pending_goals,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "paused_goals": paused_goals,
            "goal_type_breakdown": goal_type_breakdown,
            "total_cycles": len(self.learning_cycles),
            "integration_success_rate": success_rate,
            "recent_activity": f"Last activity: {self.last_activity.strftime('%Y-%m-%d %H:%M')}",
        }

    def _format_goal_type_breakdown(self, breakdown: Dict[str, int]) -> str:
        """Format goal type breakdown for display"""
        if not breakdown:
            return "• No goals yet"

        lines = []
        for goal_type, count in sorted(
            breakdown.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"• {goal_type.title()}: {count}")

        return "\n".join(lines)

    def _format_insights(self, insights: List[str]) -> str:
        """Format insights for display"""
        return "\n".join(f"• {insight}" for insight in insights)

    def _format_opportunities(self, opportunities: List[str]) -> str:
        """Format optimization opportunities for display"""
        return "\n".join(f"• {opp}" for opp in opportunities)

    def _load_persistence_data(self):
        """Load persistent learning loop data"""
        try:
            # Load learning goals
            goals_file = self.data_dir / "learning_goals.json"
            if goals_file.exists():
                with open(goals_file, "r") as f:
                    goals_data = json.load(f)
                    for g_id, g_data in goals_data.items():
                        self.learning_goals[g_id] = LearningGoal(**g_data)

            # Load learning cycles
            cycles_file = self.data_dir / "learning_cycles.json"
            if cycles_file.exists():
                with open(cycles_file, "r") as f:
                    cycles_data = json.load(f)
                    for c_id, c_data in cycles_data.items():
                        self.learning_cycles[c_id] = LearningCycle(**c_data)

            # Load current cycle ID
            current_cycle_file = self.data_dir / "current_cycle.json"
            if current_cycle_file.exists():
                with open(current_cycle_file, "r") as f:
                    data = json.load(f)
                    self.current_cycle_id = data.get("current_cycle_id")

            self.log(
                f"📂 Loaded {len(self.learning_goals)} goals and {len(self.learning_cycles)} cycles"
            )

        except Exception as e:
            self.log(f"⚠️ Could not load persistence data: {e}", "WARNING")

    def _save_persistence_data(self):
        """Save persistent learning loop data"""
        try:
            # Save learning goals
            goals_file = self.data_dir / "learning_goals.json"
            with open(goals_file, "w") as f:
                goals_data = {
                    g_id: asdict(goal) for g_id, goal in self.learning_goals.items()
                }
                json.dump(goals_data, f, indent=2)

            # Save learning cycles
            cycles_file = self.data_dir / "learning_cycles.json"
            with open(cycles_file, "w") as f:
                cycles_data = {
                    c_id: asdict(cycle) for c_id, cycle in self.learning_cycles.items()
                }
                json.dump(cycles_data, f, indent=2)

            # Save current cycle ID
            current_cycle_file = self.data_dir / "current_cycle.json"
            with open(current_cycle_file, "w") as f:
                json.dump({"current_cycle_id": self.current_cycle_id}, f)

            self.log("💾 Saved learning loop data to persistence")

        except Exception as e:
            self.log(f"❌ Could not save persistence data: {e}", "ERROR")


# Convenience functions for integration
async def generate_autonomous_goals(memory_engine=None) -> List[LearningGoal]:
    """Convenience function for goal generation"""
    agent = LearningLoopIntegrationAgent(memory_engine)
    return await agent.generate_learning_goals()


async def analyze_learning_integration(memory_engine=None) -> Dict[str, Any]:
    """Convenience function for integration analysis"""
    agent = LearningLoopIntegrationAgent(memory_engine)
    return await agent.analyze_phase3_integration()


if __name__ == "__main__":

    async def demo():
        """Demo the LearningLoopIntegrationAgent"""
        print("🔄 LearningLoopIntegrationAgent Demo")
        print("=" * 60)

        agent = LearningLoopIntegrationAgent()
        await agent.initialize()

        # Test different inputs
        test_inputs = [
            "generate goals",
            "start cycle",
            "activate goals",
            "learning status",
            "integration analysis",
            "I want to improve my learning process",
        ]

        for input_text in test_inputs:
            print(f"\n🔄 Input: {input_text}")
            response = await agent.process_input(input_text)
            print(f"Response: {response.content[:200]}...")
            print(f"Confidence: {response.confidence}")

        print("\n🎉 Demo completed!")

    # Run demo
    asyncio.run(demo())
