#!/usr/bin/env python3
"""
🧠 CURIOSITY AGENT - Phase 3 Implementation
==========================================

Advanced Curiosity Agent that integrates with the existing Lyrixa agent architecture.
Detects memory gaps, generates targeted questions, and schedules autonomous exploration.

Integrates with:
- Existing agent_base.py architecture
- Memory system via FractalMesh
- Goal system for exploration scheduling
- Reflection system for gap analysis
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    # Try relative imports first (when used as a package)
    from .agent_base import AgentBase, AgentResponse
except ImportError:
    # Fall back to absolute imports (when imported directly)
    try:
        from Aetherra.lyrixa.agents.agent_base import AgentBase, AgentResponse
    except ImportError:
        # If all imports fail, create placeholder classes
        print("⚠️ Agent base not available, using placeholder classes")
        from datetime import datetime

        class AgentBase:
            def __init__(self, *args, **kwargs):
                self.name = kwargs.get("name", "curiosity_agent")

            def log(self, message):
                print(f"[{self.name}] {message}")

            def process(self, input_data, context=None):
                return AgentResponse("Agent not available", "placeholder")

        class AgentResponse:
            def __init__(
                self,
                content="",
                agent_type="placeholder",
                confidence=0.0,
                agent_name="",
                metadata=None,
            ):
                self.content = content
                self.agent_type = agent_type
                self.confidence = confidence
                self.agent_name = agent_name
                self.metadata = metadata or {}
                self.timestamp = datetime.now()


# Try to import memory components
try:
    from ..memory.fractal_mesh.base import FractalMesh
    from ..memory.reflector.reflect_analyzer import ReflectAnalyzer
except ImportError:
    try:
        # Fall back to absolute imports
        from Aetherra.memory.fractal_mesh.base import FractalMesh
        from Aetherra.memory.reflector.reflect_analyzer import ReflectAnalyzer
    except ImportError:
        print("⚠️ Memory components not available, using mock implementations")
        FractalMesh = None
        ReflectAnalyzer = None


@dataclass
class KnowledgeGap:
    """Represents an identified gap in understanding"""

    gap_id: str
    category: str  # "conceptual", "causal", "contextual", "experiential"
    description: str
    confidence_score: float  # How confident we are this is a real gap
    priority: str  # "high", "medium", "low"
    related_memories: List[str]
    exploration_strategies: List[str]
    questions: List[str]
    timestamp: str
    resolution_status: str = "open"  # "open", "exploring", "resolved", "abandoned"


@dataclass
class CuriosityQuestion:
    """Represents a specific question generated for exploration"""

    question_id: str
    question_text: str
    question_type: str  # "why", "how", "what_if", "when", "where", "who"
    related_gap_id: str
    urgency: str  # "immediate", "near_term", "long_term"
    exploration_method: str  # "experiment", "observe", "research", "reflect"
    expected_outcome: str
    timestamp: str
    status: str = "pending"  # "pending", "active", "answered", "abandoned"


class CuriosityAgent(AgentBase):
    """
    Advanced Curiosity Agent for autonomous knowledge gap detection and exploration
    """

    def __init__(self, memory_engine=None, data_dir="curiosity_data"):
        super().__init__(
            "CuriosityAgent",
            "Detects knowledge gaps and generates autonomous exploration questions",
        )

        self.memory_engine = memory_engine
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Agent-specific components
        self.reflector = None
        self.fractal_mesh = None

        if memory_engine:
            self._initialize_memory_components()

        # Storage for curiosity data
        self.knowledge_gaps: Dict[str, KnowledgeGap] = {}
        self.curiosity_questions: Dict[str, CuriosityQuestion] = {}

        # Configuration
        self.max_gaps_tracked = 20
        self.confidence_threshold = 0.7
        self.gap_detection_interval_hours = 6

        # Load existing data
        self._load_persistence_data()

        self.log(
            "🔍 CuriosityAgent initialized with gap detection and question generation"
        )

    def _initialize_memory_components(self):
        """Initialize memory system components"""
        try:
            if ReflectAnalyzer:
                self.reflector = ReflectAnalyzer(self.memory_engine)
            if FractalMesh:
                self.fractal_mesh = FractalMesh()

            self.log("✅ Memory components initialized for curiosity analysis")
        except Exception as e:
            self.log(f"⚠️ Could not initialize memory components: {e}", "WARNING")

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process curiosity-related input and commands"""
        context = context or {}

        try:
            input_lower = input_text.lower()

            # Handle different curiosity commands
            if "detect gaps" in input_lower or "find gaps" in input_lower:
                result = await self._handle_gap_detection(context)
            elif "generate questions" in input_lower:
                result = await self._handle_question_generation(input_text, context)
            elif "schedule exploration" in input_lower:
                result = await self._handle_exploration_scheduling(input_text, context)
            elif "curiosity status" in input_lower or "gap status" in input_lower:
                result = await self._handle_status_request(context)
            elif "resolve gap" in input_lower:
                result = await self._handle_gap_resolution(input_text, context)
            else:
                # General curiosity analysis
                result = await self._handle_general_curiosity(input_text, context)

            self._increment_success()
            return result

        except Exception as e:
            self.log(f"Error processing curiosity input: {e}", "ERROR")
            self._increment_error()

            return AgentResponse(
                content=f"I encountered an error while analyzing curiosity patterns: {str(e)}",
                confidence=0.0,
                agent_name=self.name,
                metadata={"error": str(e)},
            )

    async def _handle_gap_detection(self, context: Dict[str, Any]) -> AgentResponse:
        """Handle knowledge gap detection requests"""
        timeframe_hours = context.get("timeframe_hours", 24)

        self.log(f"🔍 Detecting knowledge gaps in the last {timeframe_hours} hours")

        gaps = await self.detect_knowledge_gaps(timeframe_hours)

        if not gaps:
            return AgentResponse(
                content="I haven't detected any significant knowledge gaps recently. This could mean our knowledge is well-integrated, or we may need to adjust our detection sensitivity.",
                confidence=0.8,
                agent_name=self.name,
                metadata={"gaps_found": 0, "timeframe": timeframe_hours},
            )

        # Format response about detected gaps
        gap_summary = []
        for gap in gaps[:5]:  # Limit to top 5 gaps
            gap_summary.append(
                f"• **{gap.category.title()} Gap**: {gap.description} (Priority: {gap.priority})"
            )

        content = (
            f"🔍 I've identified {len(gaps)} knowledge gaps requiring exploration:\n\n"
            + "\n".join(gap_summary)
        )

        if len(gaps) > 5:
            content += f"\n\n*And {len(gaps) - 5} additional gaps detected.*"

        return AgentResponse(
            content=content,
            confidence=0.9,
            agent_name=self.name,
            metadata={
                "gaps_found": len(gaps),
                "gap_categories": list(set(gap.category for gap in gaps)),
                "high_priority_gaps": len([g for g in gaps if g.priority == "high"]),
            },
        )

    async def _handle_question_generation(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle question generation for curiosity exploration"""
        self.log("❓ Generating curiosity questions from detected gaps")

        # Get recent gaps or specific gap from input
        if "gap_id:" in input_text:
            gap_id = input_text.split("gap_id:")[1].strip().split()[0]
            if gap_id in self.knowledge_gaps:
                gaps = [self.knowledge_gaps[gap_id]]
            else:
                return AgentResponse(
                    content=f"Gap with ID '{gap_id}' not found.",
                    confidence=0.0,
                    agent_name=self.name,
                    metadata={"error": "gap_not_found"},
                )
        else:
            # Generate questions for all open gaps
            gaps = [
                gap
                for gap in self.knowledge_gaps.values()
                if gap.resolution_status == "open"
            ][:3]

        if not gaps:
            return AgentResponse(
                content="No open knowledge gaps found to generate questions for. Run gap detection first.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"gaps_available": 0},
            )

        all_questions = []
        for gap in gaps:
            questions = await self.generate_curiosity_questions(gap)
            all_questions.extend(questions)

        if not all_questions:
            return AgentResponse(
                content="I wasn't able to generate specific questions from the current gaps. This might indicate the gaps need more context or analysis.",
                confidence=0.5,
                agent_name=self.name,
                metadata={"questions_generated": 0},
            )

        # Format response
        question_summary = []
        for i, question in enumerate(all_questions[:5], 1):
            question_summary.append(
                f"{i}. **{question.question_type.title()}**: {question.question_text}"
            )

        content = (
            f"❓ I've generated {len(all_questions)} curiosity questions for exploration:\n\n"
            + "\n".join(question_summary)
        )

        return AgentResponse(
            content=content,
            confidence=0.85,
            agent_name=self.name,
            metadata={
                "questions_generated": len(all_questions),
                "question_types": list(set(q.question_type for q in all_questions)),
                "gaps_processed": len(gaps),
            },
        )

    async def _handle_exploration_scheduling(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle scheduling of exploration activities"""
        self.log("📅 Scheduling curiosity explorations")

        # Get pending questions
        pending_questions = [
            q for q in self.curiosity_questions.values() if q.status == "pending"
        ][:3]

        if not pending_questions:
            return AgentResponse(
                content="No pending curiosity questions found to schedule. Generate questions first.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"scheduled_explorations": 0},
            )

        scheduled_explorations = []
        for question in pending_questions:
            exploration = await self.schedule_exploration(question)
            scheduled_explorations.append(exploration)

        # Format response
        schedule_summary = []
        for i, exploration in enumerate(scheduled_explorations, 1):
            schedule_summary.append(
                f"{i}. **{exploration['exploration_method'].title()}**: {exploration['estimated_duration']}"
            )

        content = (
            f"📅 I've scheduled {len(scheduled_explorations)} curiosity explorations:\n\n"
            + "\n".join(schedule_summary)
        )

        return AgentResponse(
            content=content,
            confidence=0.8,
            agent_name=self.name,
            metadata={
                "scheduled_explorations": len(scheduled_explorations),
                "exploration_methods": [
                    e["exploration_method"] for e in scheduled_explorations
                ],
            },
        )

    async def _handle_status_request(self, context: Dict[str, Any]) -> AgentResponse:
        """Handle curiosity status and summary requests"""
        summary = self.get_curiosity_summary()

        content = f"""🔍 **Curiosity Agent Status**

**Knowledge Gaps**: {summary["knowledge_gaps"]["total"]} total
• Open: {summary["knowledge_gaps"]["open"]}
• Exploring: {summary["knowledge_gaps"]["exploring"]}
• Resolved: {summary["knowledge_gaps"]["resolved"]}

**Questions Generated**: {summary["curiosity_questions"]["total"]} total
• Pending: {summary["curiosity_questions"]["pending"]}
• Active: {summary["curiosity_questions"]["active"]}
• Answered: {summary["curiosity_questions"]["answered"]}

**Exploration Success Rate**: {summary["exploration_success_rate"]:.1%}

**Recent Activity**: {summary["recent_activity"]}
"""

        return AgentResponse(
            content=content, confidence=0.95, agent_name=self.name, metadata=summary
        )

    async def _handle_gap_resolution(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle gap resolution updates"""
        # Extract gap ID from input
        if "gap_id:" in input_text:
            gap_id = input_text.split("gap_id:")[1].strip().split()[0]
            if gap_id in self.knowledge_gaps:
                gap = self.knowledge_gaps[gap_id]
                gap.resolution_status = "resolved"
                gap.timestamp = datetime.now().isoformat()

                # Save changes
                self._save_persistence_data()

                return AgentResponse(
                    content=f"✅ Marked gap '{gap.description[:50]}...' as resolved.",
                    confidence=0.9,
                    agent_name=self.name,
                    metadata={"resolved_gap_id": gap_id},
                )
            else:
                return AgentResponse(
                    content=f"Gap with ID '{gap_id}' not found.",
                    confidence=0.0,
                    agent_name=self.name,
                    metadata={"error": "gap_not_found"},
                )
        else:
            return AgentResponse(
                content="Please specify gap_id: <id> to resolve a specific gap.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"help": "gap_id_required"},
            )

    async def _handle_general_curiosity(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle general curiosity analysis and exploration"""
        self.log("🤔 Performing general curiosity analysis")

        # Analyze the input for curiosity potential
        curiosity_triggers = [
            ("why", "causality"),
            ("how", "mechanism"),
            ("what if", "speculation"),
            ("strange", "anomaly"),
            ("confusing", "uncertainty"),
            ("unexpected", "surprise"),
        ]

        detected_triggers = []
        for trigger, curiosity_type in curiosity_triggers:
            if trigger in input_text.lower():
                detected_triggers.append(curiosity_type)

        if detected_triggers:
            content = f"🤔 I sense curiosity in your question! This touches on {', '.join(detected_triggers)} - areas ripe for exploration. Would you like me to generate specific investigation questions or schedule this for deeper analysis?"
            confidence = 0.8
        else:
            content = "🧠 I'm ready to help with curiosity-driven exploration. I can detect knowledge gaps, generate investigation questions, or schedule autonomous learning activities. What aspect of curiosity would you like to explore?"
            confidence = 0.7

        return AgentResponse(
            content=content,
            confidence=confidence,
            agent_name=self.name,
            metadata={
                "curiosity_triggers": detected_triggers,
                "available_actions": [
                    "detect_gaps",
                    "generate_questions",
                    "schedule_exploration",
                ],
            },
        )

    # Core curiosity methods (simplified versions of our previous implementation)
    async def detect_knowledge_gaps(
        self, timeframe_hours: int = 24
    ) -> List[KnowledgeGap]:
        """Detect knowledge gaps in the memory system"""
        gaps = []

        # Mock implementation - in production this would use the full detection system
        mock_gaps = [
            {
                "category": "causal",
                "description": "Pattern inconsistency: Sometimes async improves performance, sometimes it doesn't",
                "confidence": 0.8,
                "priority": "high",
                "strategies": [
                    "systematic_testing",
                    "controlled_experiments",
                    "pattern_analysis",
                ],
            },
            {
                "category": "contextual",
                "description": "User preference shifts not well understood in recent interactions",
                "confidence": 0.75,
                "priority": "medium",
                "strategies": [
                    "user_pattern_analysis",
                    "preference_tracking",
                    "correlation_study",
                ],
            },
            {
                "category": "experiential",
                "description": "Learning opportunity: Recent plugin optimization was successful but principles not generalized",
                "confidence": 0.9,
                "priority": "high",
                "strategies": [
                    "principle_extraction",
                    "generalization_testing",
                    "pattern_documentation",
                ],
            },
        ]

        for i, mock_gap in enumerate(mock_gaps):
            gap_id = f"gap_{mock_gap['category']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"

            gap = KnowledgeGap(
                gap_id=gap_id,
                category=mock_gap["category"],
                description=mock_gap["description"],
                confidence_score=mock_gap["confidence"],
                priority=mock_gap["priority"],
                related_memories=[f"memory_{i}" for i in range(3)],
                exploration_strategies=mock_gap["strategies"],
                questions=[],
                timestamp=datetime.now().isoformat(),
                resolution_status="open",
            )

            gaps.append(gap)
            self.knowledge_gaps[gap_id] = gap

        # Save to persistence
        self._save_persistence_data()
        self.log(f"🔍 Detected {len(gaps)} knowledge gaps")

        return gaps

    async def generate_curiosity_questions(
        self, gap: KnowledgeGap
    ) -> List[CuriosityQuestion]:
        """Generate specific questions for a knowledge gap"""
        questions = []

        # Generate different types of questions based on gap category
        question_templates = {
            "causal": [
                "Why does {topic} work differently in various contexts?",
                "What causes the inconsistency in {topic}?",
                "How can I identify the key factors that influence {topic}?",
            ],
            "contextual": [
                "What environmental factors affect {topic}?",
                "How does context change the outcomes for {topic}?",
                "When does {topic} behave differently than expected?",
            ],
            "experiential": [
                "What can I learn from this experience with {topic}?",
                "How can I apply this learning to future situations?",
                "What patterns can I extract from this experience?",
            ],
        }

        templates = question_templates.get(gap.category, question_templates["causal"])
        topic = gap.category

        for i, template in enumerate(templates):
            question_id = f"q_{gap.gap_id}_{i}"
            question_text = template.format(topic=topic)

            question = CuriosityQuestion(
                question_id=question_id,
                question_text=question_text,
                question_type="why" if "why" in question_text.lower() else "how",
                related_gap_id=gap.gap_id,
                urgency="near_term",
                exploration_method="research",
                expected_outcome="More effective decision making",
                timestamp=datetime.now().isoformat(),
                status="pending",
            )

            questions.append(question)
            self.curiosity_questions[question_id] = question

        # Update gap with question references
        gap.questions = [q.question_id for q in questions]

        self._save_persistence_data()
        self.log(
            f"🔍 Generated {len(questions)} curiosity questions for gap {gap.gap_id}"
        )

        return questions

    async def schedule_exploration(self, question: CuriosityQuestion) -> Dict[str, Any]:
        """Schedule exploration for a curiosity question"""
        exploration_plan = {
            "question_id": question.question_id,
            "exploration_method": question.exploration_method,
            "scheduled_time": datetime.now().isoformat(),
            "estimated_duration": "30-60 minutes",
            "resources_needed": ["analysis_time", "memory_access"],
            "success_criteria": ["Question answered", "Insights documented"],
            "priority": "medium",
        }

        # Update question status
        question.status = "active"
        self.curiosity_questions[question.question_id] = question

        self.log(f"📅 Scheduled exploration for question: {question.question_text}")
        return exploration_plan

    def get_curiosity_summary(self) -> Dict[str, Any]:
        """Get summary of curiosity agent status"""
        open_gaps = len(
            [g for g in self.knowledge_gaps.values() if g.resolution_status == "open"]
        )
        exploring_gaps = len(
            [
                g
                for g in self.knowledge_gaps.values()
                if g.resolution_status == "exploring"
            ]
        )
        resolved_gaps = len(
            [
                g
                for g in self.knowledge_gaps.values()
                if g.resolution_status == "resolved"
            ]
        )

        pending_questions = len(
            [q for q in self.curiosity_questions.values() if q.status == "pending"]
        )
        active_questions = len(
            [q for q in self.curiosity_questions.values() if q.status == "active"]
        )
        answered_questions = len(
            [q for q in self.curiosity_questions.values() if q.status == "answered"]
        )

        # Calculate success rate
        total_resolved = resolved_gaps + answered_questions
        total_attempted = len(self.knowledge_gaps) + len(self.curiosity_questions)
        success_rate = total_resolved / max(total_attempted, 1)

        return {
            "knowledge_gaps": {
                "total": len(self.knowledge_gaps),
                "open": open_gaps,
                "exploring": exploring_gaps,
                "resolved": resolved_gaps,
            },
            "curiosity_questions": {
                "total": len(self.curiosity_questions),
                "pending": pending_questions,
                "active": active_questions,
                "answered": answered_questions,
            },
            "exploration_success_rate": success_rate,
            "recent_activity": f"Last gap detection: {self.last_activity.strftime('%Y-%m-%d %H:%M')}",
        }

    def _load_persistence_data(self):
        """Load persistent curiosity data"""
        try:
            # Load knowledge gaps
            gaps_file = self.data_dir / "knowledge_gaps.json"
            if gaps_file.exists():
                with open(gaps_file, "r") as f:
                    gaps_data = json.load(f)
                    for gap_id, gap_data in gaps_data.items():
                        self.knowledge_gaps[gap_id] = KnowledgeGap(**gap_data)

            # Load questions
            questions_file = self.data_dir / "curiosity_questions.json"
            if questions_file.exists():
                with open(questions_file, "r") as f:
                    questions_data = json.load(f)
                    for q_id, q_data in questions_data.items():
                        self.curiosity_questions[q_id] = CuriosityQuestion(**q_data)

            self.log(
                f"📂 Loaded {len(self.knowledge_gaps)} gaps and {len(self.curiosity_questions)} questions"
            )

        except Exception as e:
            self.log(f"⚠️ Could not load persistence data: {e}", "WARNING")

    def _save_persistence_data(self):
        """Save persistent curiosity data"""
        try:
            # Save knowledge gaps
            gaps_file = self.data_dir / "knowledge_gaps.json"
            with open(gaps_file, "w") as f:
                gaps_data = {
                    gap_id: asdict(gap) for gap_id, gap in self.knowledge_gaps.items()
                }
                json.dump(gaps_data, f, indent=2)

            # Save questions
            questions_file = self.data_dir / "curiosity_questions.json"
            with open(questions_file, "w") as f:
                questions_data = {
                    q_id: asdict(q) for q_id, q in self.curiosity_questions.items()
                }
                json.dump(questions_data, f, indent=2)

            self.log("💾 Saved curiosity data to persistence")

        except Exception as e:
            self.log(f"❌ Could not save persistence data: {e}", "ERROR")


# Convenience functions for integration with other agents
async def detect_knowledge_gaps(
    memory_engine=None, timeframe_hours: int = 24
) -> List[KnowledgeGap]:
    """Convenience function for gap detection"""
    agent = CuriosityAgent(memory_engine)
    return await agent.detect_knowledge_gaps(timeframe_hours)


async def generate_curiosity_questions(
    gap: KnowledgeGap, memory_engine=None
) -> List[CuriosityQuestion]:
    """Convenience function for question generation"""
    agent = CuriosityAgent(memory_engine)
    return await agent.generate_curiosity_questions(gap)


if __name__ == "__main__":

    async def demo():
        """Demo the CuriosityAgent"""
        print("🧠 CuriosityAgent Demo")
        print("=" * 40)

        agent = CuriosityAgent()
        await agent.initialize()

        # Test different inputs
        test_inputs = [
            "detect gaps",
            "generate questions",
            "schedule exploration",
            "curiosity status",
            "Why does this pattern seem inconsistent?",
        ]

        for input_text in test_inputs:
            print(f"\n🔍 Input: {input_text}")
            response = await agent.process_input(input_text)
            print(f"Response: {response.content[:200]}...")
            print(f"Confidence: {response.confidence}")

        print("\n🎉 Demo completed!")

    # Run demo
    asyncio.run(demo())
