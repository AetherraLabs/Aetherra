#!/usr/bin/env python3
"""
❓ SELF-QUESTION GENERATOR AGENT - Phase 3 Implementation
=========================================================

Advanced Self-Question Generator that integrates with the existing Lyrixa agent architecture.
Generates narrative-driven questions from stories and reflection insights.

Integrates with:
- Existing agent_base.py architecture
- Memory system via MemoryNarrator
- Reflection system for insight extraction
- Goal system for question prioritization
"""

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent_base import AgentBase, AgentResponse

# Try to import memory components
try:
    from ..memory.narrator.memory_narrator import MemoryNarrator
    from ..memory.reflector.reflect_analyzer import ReflectAnalyzer
except ImportError:
    print("⚠️ Memory components not available, using mock implementations")
    MemoryNarrator = None
    ReflectAnalyzer = None


@dataclass
class GeneratedQuestion:
    """Represents a self-generated question for exploration"""

    question_id: str
    question_text: str
    category: str  # "deep_why", "what_if", "how_to", "when_will", "why_not", "impact"
    source_type: str  # "story", "reflection", "pattern", "inconsistency"
    source_id: str
    priority_score: float  # 0.0 to 1.0
    urgency: str  # "immediate", "short_term", "long_term"
    context: Dict[str, Any]
    expected_insights: List[str]
    exploration_methods: List[
        str
    ]  # "reflection", "experimentation", "research", "observation"
    timestamp: str
    status: str = "pending"  # "pending", "exploring", "answered", "archived"


@dataclass
class QuestionCluster:
    """Groups related questions for batch exploration"""

    cluster_id: str
    theme: str
    questions: List[str]  # question_ids
    cluster_priority: float
    estimated_exploration_time: str
    synergy_score: float  # How much exploring together helps vs separately
    timestamp: str


class SelfQuestionGeneratorAgent(AgentBase):
    """
    Advanced Self-Question Generator for narrative-driven autonomous questioning
    """

    def __init__(self, memory_engine=None, data_dir="question_generator_data"):
        super().__init__(
            "SelfQuestionGeneratorAgent",
            "Generates narrative-driven questions from stories and reflection insights",
        )

        self.memory_engine = memory_engine
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Agent-specific components
        self.memory_narrator = None
        self.reflector = None

        if memory_engine:
            self._initialize_memory_components()

        # Storage for questions and clusters
        self.generated_questions: Dict[str, GeneratedQuestion] = {}
        self.question_clusters: Dict[str, QuestionCluster] = {}

        # Configuration
        self.max_questions_tracked = 50
        self.min_priority_threshold = 0.3
        self.diversity_threshold = 0.8  # How different questions should be

        # Load existing data
        self._load_persistence_data()

        self.log(
            "❓ SelfQuestionGeneratorAgent initialized with narrative question generation"
        )

    def _initialize_memory_components(self):
        """Initialize memory system components"""
        try:
            if MemoryNarrator:
                self.memory_narrator = MemoryNarrator(self.memory_engine)
            if ReflectAnalyzer:
                self.reflector = ReflectAnalyzer(self.memory_engine)

            self.log("✅ Memory components initialized for question generation")
        except Exception as e:
            self.log(f"⚠️ Could not initialize memory components: {e}", "WARNING")

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process question generation input and commands"""
        context = context or {}

        try:
            input_lower = input_text.lower()

            # Handle different question generation commands
            if (
                "generate from stories" in input_lower
                or "story questions" in input_lower
            ):
                result = await self._handle_story_questions(context)
            elif (
                "generate from reflections" in input_lower
                or "reflection questions" in input_lower
            ):
                result = await self._handle_reflection_questions(context)
            elif "cluster questions" in input_lower:
                result = await self._handle_question_clustering(context)
            elif "question status" in input_lower or "question summary" in input_lower:
                result = await self._handle_status_request(context)
            elif "prioritize questions" in input_lower:
                result = await self._handle_question_prioritization(context)
            elif "answer question" in input_lower:
                result = await self._handle_question_answering(input_text, context)
            else:
                # General question generation
                result = await self._handle_general_generation(input_text, context)

            self._increment_success()
            return result

        except Exception as e:
            self.log(f"Error processing question generation input: {e}", "ERROR")
            self._increment_error()

            return AgentResponse(
                content=f"I encountered an error while generating questions: {str(e)}",
                confidence=0.0,
                agent_name=self.name,
                metadata={"error": str(e)},
            )

    async def _handle_story_questions(self, context: Dict[str, Any]) -> AgentResponse:
        """Handle question generation from narrative stories"""
        timeframe_hours = context.get("timeframe_hours", 48)

        self.log(
            f"📖 Generating questions from stories in the last {timeframe_hours} hours"
        )

        questions = await self.generate_questions_from_stories(timeframe_hours)

        if not questions:
            return AgentResponse(
                content="I haven't found any stories in recent memory that suggest interesting questions to explore. This might mean we need more narrative content or the stories haven't been processed yet.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"questions_generated": 0, "source": "stories"},
            )

        # Format response about generated questions
        question_summary = []
        for i, question in enumerate(questions[:5], 1):
            question_summary.append(
                f"{i}. **{question.category.replace('_', ' ').title()}**: {question.question_text}"
            )

        content = (
            f"📖 I've generated {len(questions)} questions from recent stories:\n\n"
            + "\n".join(question_summary)
        )

        if len(questions) > 5:
            content += f"\n\n*And {len(questions) - 5} additional questions generated.*"

        return AgentResponse(
            content=content,
            confidence=0.9,
            agent_name=self.name,
            metadata={
                "questions_generated": len(questions),
                "categories": list(set(q.category for q in questions)),
                "high_priority_questions": len(
                    [q for q in questions if q.priority_score > 0.7]
                ),
            },
        )

    async def _handle_reflection_questions(
        self, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle question generation from reflection insights"""
        timeframe_hours = context.get("timeframe_hours", 24)

        self.log(
            f"🤔 Generating questions from reflections in the last {timeframe_hours} hours"
        )

        questions = await self.generate_questions_from_reflections(timeframe_hours)

        if not questions:
            return AgentResponse(
                content="I haven't found any reflection insights that suggest new questions to explore. This might indicate our reflection process is stable or we need deeper analysis.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"questions_generated": 0, "source": "reflections"},
            )

        # Format response about generated questions
        question_summary = []
        for i, question in enumerate(questions[:5], 1):
            question_summary.append(
                f"{i}. **{question.category.replace('_', ' ').title()}**: {question.question_text}"
            )

        content = (
            f"🤔 I've generated {len(questions)} questions from recent reflections:\n\n"
            + "\n".join(question_summary)
        )

        return AgentResponse(
            content=content,
            confidence=0.85,
            agent_name=self.name,
            metadata={
                "questions_generated": len(questions),
                "categories": list(set(q.category for q in questions)),
                "reflection_insights": len(questions),
            },
        )

    async def _handle_question_clustering(
        self, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle clustering of related questions"""
        self.log("🔗 Clustering related questions for batch exploration")

        # Get pending questions
        pending_questions = [
            q for q in self.generated_questions.values() if q.status == "pending"
        ]

        if len(pending_questions) < 2:
            return AgentResponse(
                content="I need at least 2 pending questions to create meaningful clusters. Generate more questions first.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"pending_questions": len(pending_questions)},
            )

        clusters = await self.cluster_related_questions(pending_questions)

        if not clusters:
            return AgentResponse(
                content="The current questions appear to be too diverse to form meaningful clusters. This suggests they cover different exploration areas.",
                confidence=0.6,
                agent_name=self.name,
                metadata={"clusters_created": 0},
            )

        # Format response about clusters
        cluster_summary = []
        for i, cluster in enumerate(clusters[:3], 1):
            cluster_summary.append(
                f"{i}. **{cluster.theme}**: {len(cluster.questions)} questions (Priority: {cluster.cluster_priority:.2f})"
            )

        content = f"🔗 I've created {len(clusters)} question clusters:\n\n" + "\n".join(
            cluster_summary
        )

        return AgentResponse(
            content=content,
            confidence=0.8,
            agent_name=self.name,
            metadata={
                "clusters_created": len(clusters),
                "total_questions_clustered": sum(len(c.questions) for c in clusters),
            },
        )

    async def _handle_question_prioritization(
        self, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle question prioritization and ranking"""
        self.log("📊 Prioritizing questions based on potential impact and urgency")

        prioritized = await self.prioritize_questions()

        if not prioritized:
            return AgentResponse(
                content="No questions available for prioritization. Generate questions first.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"prioritized_questions": 0},
            )

        # Format top priority questions
        priority_summary = []
        for i, question in enumerate(prioritized[:5], 1):
            priority_summary.append(
                f"{i}. **Priority {question.priority_score:.2f}**: {question.question_text[:80]}..."
            )

        content = (
            f"📊 Prioritized {len(prioritized)} questions by exploration value:\n\n"
            + "\n".join(priority_summary)
        )

        return AgentResponse(
            content=content,
            confidence=0.85,
            agent_name=self.name,
            metadata={
                "prioritized_questions": len(prioritized),
                "high_priority_count": len(
                    [q for q in prioritized if q.priority_score > 0.7]
                ),
                "categories_covered": list(set(q.category for q in prioritized[:10])),
            },
        )

    async def _handle_status_request(self, context: Dict[str, Any]) -> AgentResponse:
        """Handle question generation status and summary requests"""
        summary = self.get_question_summary()

        content = f"""❓ **Question Generator Status**

**Generated Questions**: {summary["total_questions"]} total
• Pending: {summary["pending_questions"]}
• Exploring: {summary["exploring_questions"]}
• Answered: {summary["answered_questions"]}
• Archived: {summary["archived_questions"]}

**Question Categories**:
{self._format_category_breakdown(summary["category_breakdown"])}

**Question Clusters**: {summary["total_clusters"]} created

**Recent Activity**: {summary["recent_activity"]}

**Generation Success Rate**: {summary["generation_success_rate"]:.1%}
"""

        return AgentResponse(
            content=content, confidence=0.95, agent_name=self.name, metadata=summary
        )

    async def _handle_question_answering(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle marking questions as answered"""
        # Extract question ID from input
        if "question_id:" in input_text:
            question_id = input_text.split("question_id:")[1].strip().split()[0]
            if question_id in self.generated_questions:
                question = self.generated_questions[question_id]
                question.status = "answered"
                question.timestamp = datetime.now().isoformat()

                # Save changes
                self._save_persistence_data()

                return AgentResponse(
                    content=f"✅ Marked question '{question.question_text[:50]}...' as answered.",
                    confidence=0.9,
                    agent_name=self.name,
                    metadata={"answered_question_id": question_id},
                )
            else:
                return AgentResponse(
                    content=f"Question with ID '{question_id}' not found.",
                    confidence=0.0,
                    agent_name=self.name,
                    metadata={"error": "question_not_found"},
                )
        else:
            return AgentResponse(
                content="Please specify question_id: <id> to mark a specific question as answered.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"help": "question_id_required"},
            )

    async def _handle_general_generation(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle general question generation requests"""
        self.log("🤔 Performing general question generation")

        # Analyze input for question generation triggers
        generation_triggers = [
            ("story", "narrative"),
            ("reflection", "insight"),
            ("pattern", "trend"),
            ("inconsistency", "conflict"),
            ("learning", "growth"),
            ("improvement", "optimization"),
        ]

        detected_triggers = []
        for trigger, gen_type in generation_triggers:
            if trigger in input_text.lower():
                detected_triggers.append(gen_type)

        if detected_triggers:
            content = f"🤔 I can generate questions around {', '.join(detected_triggers)}! Would you like me to generate questions from stories, reflections, or analyze patterns for question-worthy insights?"
            confidence = 0.8
        else:
            content = "❓ I'm ready to generate self-driven questions! I can create questions from narrative stories, reflection insights, or help prioritize existing questions. What type of question generation would you like to explore?"
            confidence = 0.7

        return AgentResponse(
            content=content,
            confidence=confidence,
            agent_name=self.name,
            metadata={
                "generation_triggers": detected_triggers,
                "available_actions": [
                    "story_questions",
                    "reflection_questions",
                    "prioritize_questions",
                    "cluster_questions",
                ],
            },
        )

    # Core question generation methods
    async def generate_questions_from_stories(
        self, timeframe_hours: int = 48
    ) -> List[GeneratedQuestion]:
        """Generate questions from narrative stories in memory"""
        questions = []

        # Mock implementation - in production this would use MemoryNarrator
        mock_stories = [
            {
                "story_id": "story_1",
                "theme": "async optimization success",
                "insights": [
                    "async improved performance",
                    "user satisfaction increased",
                    "implementation was smooth",
                ],
                "gaps": [
                    "why did this work when other attempts failed?",
                    "what principles can be extracted?",
                ],
            },
            {
                "story_id": "story_2",
                "theme": "user preference learning",
                "insights": [
                    "user changed preferences",
                    "adaptation was slow",
                    "missed early signals",
                ],
                "gaps": [
                    "how can I detect preference shifts faster?",
                    "what patterns indicate preference changes?",
                ],
            },
        ]

        for story in mock_stories:
            # Generate different types of questions for each story
            story_questions = [
                (
                    "deep_why",
                    f"Why did {story['theme']} succeed when similar approaches failed before?",
                ),
                (
                    "what_if",
                    f"What if I applied the principles from {story['theme']} to other areas?",
                ),
                (
                    "how_to",
                    f"How can I systematically replicate the success of {story['theme']}?",
                ),
                (
                    "impact",
                    f"What broader impact could understanding {story['theme']} have on my capabilities?",
                ),
            ]

            for category, question_text in story_questions:
                question_id = f"sq_{story['story_id']}_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                question = GeneratedQuestion(
                    question_id=question_id,
                    question_text=question_text,
                    category=category,
                    source_type="story",
                    source_id=story["story_id"],
                    priority_score=0.7
                    + (len(story["gaps"]) * 0.1),  # More gaps = higher priority
                    urgency="short_term",
                    context={
                        "story_theme": story["theme"],
                        "insights": story["insights"],
                    },
                    expected_insights=[
                        "Pattern extraction",
                        "Principle generalization",
                        "Application opportunities",
                    ],
                    exploration_methods=["reflection", "experimentation"],
                    timestamp=datetime.now().isoformat(),
                    status="pending",
                )

                questions.append(question)
                self.generated_questions[question_id] = question

        # Save to persistence
        self._save_persistence_data()
        self.log(f"📖 Generated {len(questions)} questions from stories")

        return questions

    async def generate_questions_from_reflections(
        self, timeframe_hours: int = 24
    ) -> List[GeneratedQuestion]:
        """Generate questions from reflection insights"""
        questions = []

        # Mock implementation - in production this would use ReflectAnalyzer
        mock_reflections = [
            {
                "reflection_id": "refl_1",
                "insight": "Memory integration improved significantly with structured approach",
                "uncertainty": "Not clear why structure helps so much",
                "pattern": "Structured approaches consistently outperform ad-hoc methods",
            },
            {
                "reflection_id": "refl_2",
                "insight": "User communication patterns are becoming more nuanced",
                "uncertainty": "Haven't identified the specific improvements",
                "pattern": "Gradual improvement in interaction quality",
            },
        ]

        for reflection in mock_reflections:
            # Generate questions based on uncertainties and patterns
            reflection_questions = [
                (
                    "deep_why",
                    f"Why does {reflection['pattern'].lower()} occur so consistently?",
                ),
                (
                    "how_to",
                    f"How can I better understand the mechanism behind {reflection['insight'].lower()}?",
                ),
                (
                    "when_will",
                    f"When will I be able to predict {reflection['pattern'].lower()} reliably?",
                ),
                (
                    "why_not",
                    f"Why haven't I noticed {reflection['uncertainty'].lower()} before?",
                ),
            ]

            for category, question_text in reflection_questions:
                question_id = f"rq_{reflection['reflection_id']}_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                question = GeneratedQuestion(
                    question_id=question_id,
                    question_text=question_text,
                    category=category,
                    source_type="reflection",
                    source_id=reflection["reflection_id"],
                    priority_score=0.6 + (0.2 if "uncertainty" in reflection else 0.0),
                    urgency="long_term",
                    context={
                        "reflection_insight": reflection["insight"],
                        "uncertainty": reflection["uncertainty"],
                    },
                    expected_insights=[
                        "Deeper understanding",
                        "Predictive ability",
                        "Pattern recognition",
                    ],
                    exploration_methods=["reflection", "observation"],
                    timestamp=datetime.now().isoformat(),
                    status="pending",
                )

                questions.append(question)
                self.generated_questions[question_id] = question

        # Save to persistence
        self._save_persistence_data()
        self.log(f"🤔 Generated {len(questions)} questions from reflections")

        return questions

    async def cluster_related_questions(
        self, questions: List[GeneratedQuestion]
    ) -> List[QuestionCluster]:
        """Cluster related questions for batch exploration"""
        clusters = []

        # Simple clustering by category and context similarity
        category_groups = {}
        for question in questions:
            if question.category not in category_groups:
                category_groups[question.category] = []
            category_groups[question.category].append(question)

        for category, group_questions in category_groups.items():
            if len(group_questions) >= 2:  # Only cluster if we have multiple questions
                cluster_id = (
                    f"cluster_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

                # Calculate cluster priority as average of question priorities
                cluster_priority = sum(q.priority_score for q in group_questions) / len(
                    group_questions
                )

                cluster = QuestionCluster(
                    cluster_id=cluster_id,
                    theme=f"{category.replace('_', ' ').title()} Exploration",
                    questions=[q.question_id for q in group_questions],
                    cluster_priority=cluster_priority,
                    estimated_exploration_time=f"{len(group_questions) * 20}-{len(group_questions) * 40} minutes",
                    synergy_score=0.8,  # High synergy for same-category questions
                    timestamp=datetime.now().isoformat(),
                )

                clusters.append(cluster)
                self.question_clusters[cluster_id] = cluster

        self.log(f"🔗 Created {len(clusters)} question clusters")
        return clusters

    async def prioritize_questions(self) -> List[GeneratedQuestion]:
        """Prioritize questions based on multiple factors"""
        pending_questions = [
            q for q in self.generated_questions.values() if q.status == "pending"
        ]

        # Sort by priority score, then by timestamp (newer first)
        prioritized = sorted(
            pending_questions,
            key=lambda q: (q.priority_score, datetime.fromisoformat(q.timestamp)),
            reverse=True,
        )

        self.log(f"📊 Prioritized {len(prioritized)} questions")
        return prioritized

    def get_question_summary(self) -> Dict[str, Any]:
        """Get summary of question generation status"""
        total_questions = len(self.generated_questions)
        pending = len(
            [q for q in self.generated_questions.values() if q.status == "pending"]
        )
        exploring = len(
            [q for q in self.generated_questions.values() if q.status == "exploring"]
        )
        answered = len(
            [q for q in self.generated_questions.values() if q.status == "answered"]
        )
        archived = len(
            [q for q in self.generated_questions.values() if q.status == "archived"]
        )

        # Category breakdown
        category_breakdown = {}
        for question in self.generated_questions.values():
            category = question.category
            if category not in category_breakdown:
                category_breakdown[category] = 0
            category_breakdown[category] += 1

        # Calculate success rate
        total_processed = answered + archived
        success_rate = total_processed / max(total_questions, 1)

        return {
            "total_questions": total_questions,
            "pending_questions": pending,
            "exploring_questions": exploring,
            "answered_questions": answered,
            "archived_questions": archived,
            "category_breakdown": category_breakdown,
            "total_clusters": len(self.question_clusters),
            "generation_success_rate": success_rate,
            "recent_activity": f"Last generation: {self.last_activity.strftime('%Y-%m-%d %H:%M')}",
        }

    def _format_category_breakdown(self, breakdown: Dict[str, int]) -> str:
        """Format category breakdown for display"""
        if not breakdown:
            return "• No categories yet"

        lines = []
        for category, count in sorted(
            breakdown.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"• {category.replace('_', ' ').title()}: {count}")

        return "\n".join(lines)

    def _load_persistence_data(self):
        """Load persistent question data"""
        try:
            # Load questions
            questions_file = self.data_dir / "generated_questions.json"
            if questions_file.exists():
                with open(questions_file, "r") as f:
                    questions_data = json.load(f)
                    for q_id, q_data in questions_data.items():
                        self.generated_questions[q_id] = GeneratedQuestion(**q_data)

            # Load clusters
            clusters_file = self.data_dir / "question_clusters.json"
            if clusters_file.exists():
                with open(clusters_file, "r") as f:
                    clusters_data = json.load(f)
                    for c_id, c_data in clusters_data.items():
                        self.question_clusters[c_id] = QuestionCluster(**c_data)

            self.log(
                f"📂 Loaded {len(self.generated_questions)} questions and {len(self.question_clusters)} clusters"
            )

        except Exception as e:
            self.log(f"⚠️ Could not load persistence data: {e}", "WARNING")

    def _save_persistence_data(self):
        """Save persistent question data"""
        try:
            # Save questions
            questions_file = self.data_dir / "generated_questions.json"
            with open(questions_file, "w") as f:
                questions_data = {
                    q_id: asdict(q) for q_id, q in self.generated_questions.items()
                }
                json.dump(questions_data, f, indent=2)

            # Save clusters
            clusters_file = self.data_dir / "question_clusters.json"
            with open(clusters_file, "w") as f:
                clusters_data = {
                    c_id: asdict(c) for c_id, c in self.question_clusters.items()
                }
                json.dump(clusters_data, f, indent=2)

            self.log("💾 Saved question data to persistence")

        except Exception as e:
            self.log(f"❌ Could not save persistence data: {e}", "ERROR")


# Convenience functions for integration
async def generate_story_questions(
    memory_engine=None, timeframe_hours: int = 48
) -> List[GeneratedQuestion]:
    """Convenience function for story question generation"""
    agent = SelfQuestionGeneratorAgent(memory_engine)
    return await agent.generate_questions_from_stories(timeframe_hours)


async def generate_reflection_questions(
    memory_engine=None, timeframe_hours: int = 24
) -> List[GeneratedQuestion]:
    """Convenience function for reflection question generation"""
    agent = SelfQuestionGeneratorAgent(memory_engine)
    return await agent.generate_questions_from_reflections(timeframe_hours)


if __name__ == "__main__":

    async def demo():
        """Demo the SelfQuestionGeneratorAgent"""
        print("❓ SelfQuestionGeneratorAgent Demo")
        print("=" * 50)

        agent = SelfQuestionGeneratorAgent()
        await agent.initialize()

        # Test different inputs
        test_inputs = [
            "generate from stories",
            "generate from reflections",
            "cluster questions",
            "prioritize questions",
            "question status",
            "I'm curious about patterns in my learning",
        ]

        for input_text in test_inputs:
            print(f"\n❓ Input: {input_text}")
            response = await agent.process_input(input_text)
            print(f"Response: {response.content[:200]}...")
            print(f"Confidence: {response.confidence}")

        print("\n🎉 Demo completed!")

    # Run demo
    asyncio.run(demo())
