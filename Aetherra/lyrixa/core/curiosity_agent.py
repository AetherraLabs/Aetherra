#!/usr/bin/env python3
"""
🔍 CuriosityAgent - Autonomous Knowledge Gap Detection & Exploration

This agent identifies gaps in Lyrixa's understanding and generates specific
questions for knowledge acquisition. It builds on the reflector system to
create curiosity-driven learning opportunities.

Features:
- Gap-driven exploration using memory analysis
- Question generation for knowledge acquisition
- Exploration scheduling integration
- Success tracking for curiosity-driven learning
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Try to import memory components with fallbacks
try:
    from ..memory.fractal_mesh.base import FractalMesh
    from ..memory.fractal_mesh.concepts.concept_clusters import ConceptClusterManager
    from ..memory.fractal_mesh.timelines.reflective_timeline_engine import (
        ReflectiveTimelineEngine,
    )
    from ..memory.reflector.reflect_analyzer import ReflectAnalyzer
except ImportError:
    print("⚠️ Memory components not available, using mock implementations")
    FractalMesh = None
    ConceptClusterManager = None
    ReflectiveTimelineEngine = None
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
    questions: List[str]
    exploration_strategies: List[str]
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


class CuriosityAgent:
    """
    Autonomous agent for detecting knowledge gaps and generating exploration questions
    """

    def __init__(self, memory_engine=None, data_dir="curiosity_data"):
        self.memory_engine = memory_engine
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize components
        self.fractal_mesh = None
        self.concept_clusters = None
        self.timeline_engine = None
        self.reflector = None

        if memory_engine:
            self._initialize_memory_components()

        # Storage
        self.knowledge_gaps: Dict[str, KnowledgeGap] = {}
        self.curiosity_questions: Dict[str, CuriosityQuestion] = {}

        # Configuration
        self.gap_detection_threshold = 0.6
        self.question_generation_limit = 5
        self.exploration_success_threshold = 0.7

        # Load existing data
        self._load_persistence_data()

        logging.info(
            "🔍 CuriosityAgent initialized with gap detection and question generation"
        )

    def _initialize_memory_components(self):
        """Initialize memory system components"""
        try:
            if FractalMesh:
                self.fractal_mesh = FractalMesh()
            if ConceptClusterManager:
                self.concept_clusters = ConceptClusterManager()
            if ReflectiveTimelineEngine:
                self.timeline_engine = ReflectiveTimelineEngine()
            if ReflectAnalyzer:
                self.reflector = ReflectAnalyzer()
            logging.info("✅ Memory components initialized for curiosity analysis")
        except Exception as e:
            logging.warning(f"⚠️ Could not initialize memory components: {e}")

    async def detect_knowledge_gaps(
        self, timeframe_hours: int = 24
    ) -> List[KnowledgeGap]:
        """
        Identify knowledge gaps using multiple analysis methods

        Args:
            timeframe_hours: How far back to analyze for gaps

        Returns:
            List of identified knowledge gaps
        """
        gaps = []

        try:
            # 1. Confidence-based gap detection
            confidence_gaps = await self._detect_confidence_gaps(timeframe_hours)
            gaps.extend(confidence_gaps)

            # 2. Pattern inconsistency detection
            pattern_gaps = await self._detect_pattern_inconsistencies()
            gaps.extend(pattern_gaps)

            # 3. Causal chain incomplete detection
            causal_gaps = await self._detect_incomplete_causal_chains()
            gaps.extend(causal_gaps)

            # 4. Context mismatch detection
            context_gaps = await self._detect_context_mismatches()
            gaps.extend(context_gaps)

            # 5. Learning opportunity detection
            learning_gaps = await self._detect_learning_opportunities()
            gaps.extend(learning_gaps)

            # Deduplicate and prioritize
            unique_gaps = self._deduplicate_gaps(gaps)
            prioritized_gaps = self._prioritize_gaps(unique_gaps)

            # Store new gaps
            for gap in prioritized_gaps:
                self.knowledge_gaps[gap.gap_id] = gap

            # Save to persistence
            self._save_persistence_data()

            logging.info(f"🔍 Detected {len(prioritized_gaps)} knowledge gaps")
            return prioritized_gaps

        except Exception as e:
            logging.error(f"❌ Error detecting knowledge gaps: {e}")
            return []

    async def _detect_confidence_gaps(self, timeframe_hours: int) -> List[KnowledgeGap]:
        """Detect gaps based on low confidence memory fragments"""
        gaps = []

        if not self.memory_engine:
            return gaps

        try:
            # Get recent memories with low confidence
            since = datetime.now() - timedelta(hours=timeframe_hours)

            # Mock query - in real implementation, this would query the memory engine
            low_confidence_memories = [
                {
                    "id": "mem_1",
                    "content": "Plugin X fails in context Y",
                    "confidence": 0.3,
                    "topic": "plugin_behavior",
                },
                {
                    "id": "mem_2",
                    "content": "Users seem happier after topic A",
                    "confidence": 0.4,
                    "topic": "user_satisfaction",
                },
                {
                    "id": "mem_3",
                    "content": "Performance drops with feature B",
                    "confidence": 0.2,
                    "topic": "system_performance",
                },
            ]

            for memory in low_confidence_memories:
                if memory["confidence"] < self.gap_detection_threshold:
                    gap = KnowledgeGap(
                        gap_id=f"conf_gap_{memory['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        category="conceptual",
                        description=f"Low confidence understanding: {memory['content']}",
                        confidence_score=1.0
                        - memory["confidence"],  # Inverse of memory confidence
                        priority="high" if memory["confidence"] < 0.3 else "medium",
                        related_memories=[memory["id"]],
                        questions=[
                            f"Why does {memory['content'].lower()}?",
                            f"What conditions cause {memory['content'].lower()}?",
                            f"How can I better understand {memory['topic']}?",
                        ],
                        exploration_strategies=[
                            "observe_patterns",
                            "test_hypotheses",
                            "gather_more_data",
                        ],
                        timestamp=datetime.now().isoformat(),
                    )
                    gaps.append(gap)

            logging.info(f"🔍 Found {len(gaps)} confidence-based gaps")

        except Exception as e:
            logging.error(f"❌ Error in confidence gap detection: {e}")

        return gaps

    async def _detect_pattern_inconsistencies(self) -> List[KnowledgeGap]:
        """Detect gaps from inconsistent patterns in memory"""
        gaps = []

        try:
            # Mock pattern analysis - in real implementation, this would use concept clusters
            inconsistent_patterns = [
                {
                    "pattern": "async_performance",
                    "contradiction": "Sometimes async improves performance, sometimes it doesn't",
                    "confidence": 0.8,
                    "memories": ["async_mem_1", "async_mem_2", "async_mem_3"],
                }
            ]

            for pattern in inconsistent_patterns:
                gap = KnowledgeGap(
                    gap_id=f"pattern_gap_{pattern['pattern']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category="causal",
                    description=f"Pattern inconsistency: {pattern['contradiction']}",
                    confidence_score=pattern["confidence"],
                    priority="high",
                    related_memories=pattern["memories"],
                    questions=[
                        f"What determines when {pattern['pattern']} works well?",
                        f"What are the key variables affecting {pattern['pattern']}?",
                        f"Can I identify the conditions that predict success?",
                    ],
                    exploration_strategies=[
                        "controlled_testing",
                        "variable_isolation",
                        "correlation_analysis",
                    ],
                    timestamp=datetime.now().isoformat(),
                )
                gaps.append(gap)

            logging.info(f"🔍 Found {len(gaps)} pattern inconsistency gaps")

        except Exception as e:
            logging.error(f"❌ Error in pattern inconsistency detection: {e}")

        return gaps

    async def _detect_incomplete_causal_chains(self) -> List[KnowledgeGap]:
        """Detect gaps in causal understanding"""
        gaps = []

        try:
            # Mock causal chain analysis
            incomplete_chains = [
                {
                    "chain_id": "performance_improvement",
                    "missing_links": ["optimization_method", "measurement_criteria"],
                    "confidence": 0.7,
                    "description": "Performance improved but mechanism unclear",
                }
            ]

            for chain in incomplete_chains:
                gap = KnowledgeGap(
                    gap_id=f"causal_gap_{chain['chain_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category="causal",
                    description=f"Incomplete causal understanding: {chain['description']}",
                    confidence_score=chain["confidence"],
                    priority="medium",
                    related_memories=[chain["chain_id"]],
                    questions=[
                        f"What was the actual mechanism behind {chain['description']}?",
                        f"What steps were involved in {chain['chain_id']}?",
                        f"How can I track the causal pathway more clearly?",
                    ],
                    exploration_strategies=[
                        "step_by_step_analysis",
                        "mechanism_tracing",
                        "hypothesis_testing",
                    ],
                    timestamp=datetime.now().isoformat(),
                )
                gaps.append(gap)

            logging.info(f"🔍 Found {len(gaps)} causal chain gaps")

        except Exception as e:
            logging.error(f"❌ Error in causal chain detection: {e}")

        return gaps

    async def _detect_context_mismatches(self) -> List[KnowledgeGap]:
        """Detect gaps from context-dependent behavior variations"""
        gaps = []

        try:
            # Mock context analysis
            context_mismatches = [
                {
                    "behavior": "user_response_quality",
                    "contexts": ["morning", "evening", "weekend"],
                    "variations": "Response quality varies by time",
                    "confidence": 0.6,
                }
            ]

            for mismatch in context_mismatches:
                gap = KnowledgeGap(
                    gap_id=f"context_gap_{mismatch['behavior']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category="contextual",
                    description=f"Context-dependent variation: {mismatch['variations']}",
                    confidence_score=mismatch["confidence"],
                    priority="medium",
                    related_memories=[mismatch["behavior"]],
                    questions=[
                        f"Why does {mismatch['behavior']} vary across {', '.join(mismatch['contexts'])}?",
                        f"What contextual factors influence {mismatch['behavior']}?",
                        f"Can I predict {mismatch['behavior']} based on context?",
                    ],
                    exploration_strategies=[
                        "contextual_observation",
                        "factor_analysis",
                        "controlled_context_testing",
                    ],
                    timestamp=datetime.now().isoformat(),
                )
                gaps.append(gap)

            logging.info(f"🔍 Found {len(gaps)} context mismatch gaps")

        except Exception as e:
            logging.error(f"❌ Error in context mismatch detection: {e}")

        return gaps

    async def _detect_learning_opportunities(self) -> List[KnowledgeGap]:
        """Detect potential learning opportunities from successful patterns"""
        gaps = []

        try:
            # Mock learning opportunity analysis
            opportunities = [
                {
                    "opportunity": "plugin_optimization_success",
                    "description": "Recent plugin optimization was successful but principles not generalized",
                    "confidence": 0.9,
                    "potential": "high",
                }
            ]

            for opp in opportunities:
                gap = KnowledgeGap(
                    gap_id=f"learning_gap_{opp['opportunity']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category="experiential",
                    description=f"Learning opportunity: {opp['description']}",
                    confidence_score=opp["confidence"],
                    priority="high" if opp["potential"] == "high" else "medium",
                    related_memories=[opp["opportunity"]],
                    questions=[
                        f"What principles can I extract from {opp['opportunity']}?",
                        f"How can I apply this learning to other situations?",
                        f"What made {opp['opportunity']} successful?",
                    ],
                    exploration_strategies=[
                        "principle_extraction",
                        "pattern_generalization",
                        "transfer_testing",
                    ],
                    timestamp=datetime.now().isoformat(),
                )
                gaps.append(gap)

            logging.info(f"🔍 Found {len(gaps)} learning opportunity gaps")

        except Exception as e:
            logging.error(f"❌ Error in learning opportunity detection: {e}")

        return gaps

    def _deduplicate_gaps(self, gaps: List[KnowledgeGap]) -> List[KnowledgeGap]:
        """Remove duplicate or very similar gaps"""
        unique_gaps = []
        seen_descriptions = set()

        for gap in gaps:
            # Simple deduplication by description similarity
            similar_found = False
            for seen_desc in seen_descriptions:
                if self._similarity_score(gap.description, seen_desc) > 0.8:
                    similar_found = True
                    break

            if not similar_found:
                unique_gaps.append(gap)
                seen_descriptions.add(gap.description)

        logging.info(
            f"🔍 Deduplicated {len(gaps)} gaps to {len(unique_gaps)} unique gaps"
        )
        return unique_gaps

    def _prioritize_gaps(self, gaps: List[KnowledgeGap]) -> List[KnowledgeGap]:
        """Prioritize gaps based on confidence, category, and potential impact"""

        def priority_score(gap: KnowledgeGap) -> float:
            base_score = gap.confidence_score

            # Category weights
            category_weights = {
                "conceptual": 1.0,
                "causal": 1.2,  # Higher priority for causal understanding
                "contextual": 0.9,
                "experiential": 1.1,
            }

            # Priority weights
            priority_weights = {"high": 1.5, "medium": 1.0, "low": 0.7}

            return (
                base_score
                * category_weights.get(gap.category, 1.0)
                * priority_weights.get(gap.priority, 1.0)
            )

        sorted_gaps = sorted(gaps, key=priority_score, reverse=True)
        logging.info(f"🔍 Prioritized {len(gaps)} gaps")
        return sorted_gaps

    async def generate_curiosity_questions(
        self, gap: KnowledgeGap
    ) -> List[CuriosityQuestion]:
        """
        Generate specific, actionable questions for a knowledge gap

        Args:
            gap: The knowledge gap to generate questions for

        Returns:
            List of curiosity questions
        """
        questions = []

        try:
            # Generate different types of questions based on gap category
            question_generators = {
                "conceptual": self._generate_conceptual_questions,
                "causal": self._generate_causal_questions,
                "contextual": self._generate_contextual_questions,
                "experiential": self._generate_experiential_questions,
            }

            generator = question_generators.get(
                gap.category, self._generate_generic_questions
            )
            base_questions = await generator(gap)

            # Convert to CuriosityQuestion objects
            for i, q_text in enumerate(
                base_questions[: self.question_generation_limit]
            ):
                question = CuriosityQuestion(
                    question_id=f"{gap.gap_id}_q{i + 1}",
                    question_text=q_text,
                    question_type=self._classify_question_type(q_text),
                    related_gap_id=gap.gap_id,
                    urgency=self._determine_urgency(gap, q_text),
                    exploration_method=self._suggest_exploration_method(gap, q_text),
                    expected_outcome=self._predict_outcome(gap, q_text),
                    timestamp=datetime.now().isoformat(),
                )
                questions.append(question)
                self.curiosity_questions[question.question_id] = question

            # Save to persistence
            self._save_persistence_data()

            logging.info(
                f"🔍 Generated {len(questions)} curiosity questions for gap {gap.gap_id}"
            )

        except Exception as e:
            logging.error(f"❌ Error generating curiosity questions: {e}")

        return questions

    async def _generate_conceptual_questions(self, gap: KnowledgeGap) -> List[str]:
        """Generate questions for conceptual gaps"""
        return [
            f"What is the fundamental nature of {self._extract_key_concept(gap.description)}?",
            f"How does {self._extract_key_concept(gap.description)} relate to other concepts I understand?",
            f"What are the essential characteristics that define {self._extract_key_concept(gap.description)}?",
            f"Under what conditions does {self._extract_key_concept(gap.description)} apply?",
            f"What exceptions or edge cases exist for {self._extract_key_concept(gap.description)}?",
        ]

    async def _generate_causal_questions(self, gap: KnowledgeGap) -> List[str]:
        """Generate questions for causal gaps"""
        return [
            f"What causes {self._extract_key_concept(gap.description)}?",
            f"What are the intermediate steps between cause and effect in {self._extract_key_concept(gap.description)}?",
            f"What variables influence the strength of this causal relationship?",
            f"Are there alternative causal pathways that could explain this?",
            f"What would happen if I modified the conditions?",
        ]

    async def _generate_contextual_questions(self, gap: KnowledgeGap) -> List[str]:
        """Generate questions for contextual gaps"""
        return [
            f"In which contexts does {self._extract_key_concept(gap.description)} behave differently?",
            f"What contextual factors are most influential?",
            f"How can I predict behavior based on context?",
            f"What contexts have I not yet observed?",
            f"Are there hidden contextual variables I'm missing?",
        ]

    async def _generate_experiential_questions(self, gap: KnowledgeGap) -> List[str]:
        """Generate questions for experiential gaps"""
        return [
            f"What can I learn from this experience with {self._extract_key_concept(gap.description)}?",
            f"How can I apply this learning to future situations?",
            f"What patterns can I extract from this experience?",
            f"What would I do differently next time?",
            f"How does this experience change my understanding?",
        ]

    async def _generate_generic_questions(self, gap: KnowledgeGap) -> List[str]:
        """Generate generic questions for unknown gap types"""
        return [
            f"What don't I understand about {self._extract_key_concept(gap.description)}?",
            f"How can I learn more about this?",
            f"What experiments could help me understand this better?",
            f"Who or what could provide more information?",
            f"What related areas should I explore?",
        ]

    def _extract_key_concept(self, description: str) -> str:
        """Extract the key concept from a gap description"""
        # Simple extraction - in production, this could use NLP
        words = description.lower().split()

        # Remove common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]

        if filtered_words:
            return filtered_words[0]
        return "this concept"

    def _classify_question_type(self, question: str) -> str:
        """Classify the type of question"""
        question_lower = question.lower()
        if question_lower.startswith("what"):
            return "what"
        elif question_lower.startswith("why"):
            return "why"
        elif question_lower.startswith("how"):
            return "how"
        elif question_lower.startswith("when"):
            return "when"
        elif question_lower.startswith("where"):
            return "where"
        elif question_lower.startswith("who"):
            return "who"
        elif "what if" in question_lower:
            return "what_if"
        else:
            return "other"

    def _determine_urgency(self, gap: KnowledgeGap, question: str) -> str:
        """Determine the urgency of exploring a question"""
        if gap.priority == "high":
            return "immediate"
        elif gap.priority == "medium":
            return "near_term"
        else:
            return "long_term"

    def _suggest_exploration_method(self, gap: KnowledgeGap, question: str) -> str:
        """Suggest the best method for exploring a question"""
        question_lower = question.lower()

        if "experiment" in question_lower or "test" in question_lower:
            return "experiment"
        elif "observe" in question_lower or "watch" in question_lower:
            return "observe"
        elif "research" in question_lower or "learn" in question_lower:
            return "research"
        else:
            return "reflect"

    def _predict_outcome(self, gap: KnowledgeGap, question: str) -> str:
        """Predict the expected outcome of exploring a question"""
        outcomes = [
            "Better understanding of underlying mechanisms",
            "Improved prediction accuracy",
            "Enhanced pattern recognition",
            "More effective decision making",
            "Reduced uncertainty in related areas",
        ]

        # Simple mapping based on gap category
        category_outcomes = {
            "conceptual": "Better understanding of underlying mechanisms",
            "causal": "Improved prediction accuracy",
            "contextual": "Enhanced pattern recognition",
            "experiential": "More effective decision making",
        }

        return category_outcomes.get(
            gap.category, "Reduced uncertainty in related areas"
        )

    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        # Simple Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1 & words2
        union = words1 | words2

        if not union:
            return 0.0

        return len(intersection) / len(union)

    async def schedule_exploration(self, question: CuriosityQuestion) -> Dict[str, Any]:
        """
        Schedule exploration for a curiosity question

        Args:
            question: The question to explore

        Returns:
            Exploration plan
        """
        plan = {
            "question_id": question.question_id,
            "exploration_method": question.exploration_method,
            "scheduled_time": datetime.now().isoformat(),
            "estimated_duration": self._estimate_exploration_duration(question),
            "resources_needed": self._identify_resources_needed(question),
            "success_criteria": self._define_success_criteria(question),
            "fallback_strategies": self._suggest_fallback_strategies(question),
        }

        # Update question status
        question.status = "active"
        self.curiosity_questions[question.question_id] = question

        logging.info(f"📅 Scheduled exploration for question: {question.question_text}")
        return plan

    def _estimate_exploration_duration(self, question: CuriosityQuestion) -> str:
        """Estimate how long exploration might take"""
        method_durations = {
            "experiment": "1-3 hours",
            "observe": "ongoing",
            "research": "30-60 minutes",
            "reflect": "15-30 minutes",
        }
        return method_durations.get(question.exploration_method, "variable")

    def _identify_resources_needed(self, question: CuriosityQuestion) -> List[str]:
        """Identify resources needed for exploration"""
        method_resources = {
            "experiment": [
                "test environment",
                "measurement tools",
                "controlled conditions",
            ],
            "observe": ["monitoring systems", "data collection", "pattern detection"],
            "research": [
                "information sources",
                "search capabilities",
                "analysis tools",
            ],
            "reflect": ["quiet time", "memory access", "reasoning framework"],
        }
        return method_resources.get(question.exploration_method, ["basic resources"])

    def _define_success_criteria(self, question: CuriosityQuestion) -> List[str]:
        """Define what success looks like for this exploration"""
        return [
            "Question answered with confidence > 0.7",
            "Related knowledge gap reduced",
            "New insights generated",
            "Improved prediction capability",
            "Enhanced understanding documented",
        ]

    def _suggest_fallback_strategies(self, question: CuriosityQuestion) -> List[str]:
        """Suggest alternative approaches if primary exploration fails"""
        return [
            "Break question into smaller sub-questions",
            "Try alternative exploration method",
            "Seek external information sources",
            "Defer to future learning opportunity",
            "Document partial insights gained",
        ]

    async def track_exploration_success(
        self, question_id: str, outcome: Dict[str, Any]
    ) -> float:
        """
        Track the success of an exploration attempt

        Args:
            question_id: The question that was explored
            outcome: Results of the exploration

        Returns:
            Success score (0.0 to 1.0)
        """
        if question_id not in self.curiosity_questions:
            logging.warning(f"⚠️ Question {question_id} not found for success tracking")
            return 0.0

        question = self.curiosity_questions[question_id]

        # Calculate success score based on multiple factors
        success_factors = {
            "answer_confidence": outcome.get("confidence", 0.0),
            "insight_generation": 1.0
            if outcome.get("insights_generated", 0) > 0
            else 0.0,
            "gap_reduction": outcome.get("gap_reduction", 0.0),
            "knowledge_transfer": outcome.get("transferability", 0.0),
            "completeness": outcome.get("completeness", 0.0),
        }

        # Weighted average
        weights = {
            "answer_confidence": 0.3,
            "insight_generation": 0.2,
            "gap_reduction": 0.2,
            "knowledge_transfer": 0.15,
            "completeness": 0.15,
        }

        success_score = sum(
            success_factors[factor] * weights[factor] for factor in success_factors
        )

        # Update question status
        if success_score >= self.exploration_success_threshold:
            question.status = "answered"
        else:
            question.status = "partial"

        self.curiosity_questions[question_id] = question

        # Update related gap
        gap_id = question.related_gap_id
        if gap_id in self.knowledge_gaps:
            gap = self.knowledge_gaps[gap_id]
            if success_score >= self.exploration_success_threshold:
                gap.resolution_status = "resolved"
            else:
                gap.resolution_status = "exploring"
            self.knowledge_gaps[gap_id] = gap

        # Save to persistence
        self._save_persistence_data()

        logging.info(f"📊 Exploration success for {question_id}: {success_score:.2f}")
        return success_score

    def get_curiosity_summary(self) -> Dict[str, Any]:
        """Get a summary of current curiosity state"""
        total_gaps = len(self.knowledge_gaps)
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

        total_questions = len(self.curiosity_questions)
        pending_questions = len(
            [q for q in self.curiosity_questions.values() if q.status == "pending"]
        )
        active_questions = len(
            [q for q in self.curiosity_questions.values() if q.status == "active"]
        )
        answered_questions = len(
            [q for q in self.curiosity_questions.values() if q.status == "answered"]
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "knowledge_gaps": {
                "total": total_gaps,
                "open": open_gaps,
                "exploring": exploring_gaps,
                "resolved": resolved_gaps,
            },
            "curiosity_questions": {
                "total": total_questions,
                "pending": pending_questions,
                "active": active_questions,
                "answered": answered_questions,
            },
            "exploration_success_rate": answered_questions / max(total_questions, 1),
            "most_curious_categories": self._get_top_categories(),
            "recent_discoveries": self._get_recent_discoveries(),
        }

    def _get_top_categories(self) -> List[str]:
        """Get the categories with the most knowledge gaps"""
        category_counts = {}
        for gap in self.knowledge_gaps.values():
            category_counts[gap.category] = category_counts.get(gap.category, 0) + 1

        return sorted(
            category_counts.keys(), key=lambda c: category_counts[c], reverse=True
        )[:3]

    def _get_recent_discoveries(self) -> List[str]:
        """Get recently resolved gaps as discoveries"""
        recent_resolved = [
            gap
            for gap in self.knowledge_gaps.values()
            if gap.resolution_status == "resolved"
        ]

        # Sort by timestamp and take most recent
        recent_resolved.sort(key=lambda g: g.timestamp, reverse=True)

        return [gap.description for gap in recent_resolved[:3]]

    def _load_persistence_data(self):
        """Load persistent data from files"""
        try:
            # Load knowledge gaps
            gaps_file = self.data_dir / "knowledge_gaps.json"
            if gaps_file.exists():
                with open(gaps_file, "r") as f:
                    gaps_data = json.load(f)
                    self.knowledge_gaps = {
                        gap_id: KnowledgeGap(**gap_data)
                        for gap_id, gap_data in gaps_data.items()
                    }

            # Load curiosity questions
            questions_file = self.data_dir / "curiosity_questions.json"
            if questions_file.exists():
                with open(questions_file, "r") as f:
                    questions_data = json.load(f)
                    self.curiosity_questions = {
                        q_id: CuriosityQuestion(**q_data)
                        for q_id, q_data in questions_data.items()
                    }

            logging.info(
                f"📂 Loaded {len(self.knowledge_gaps)} gaps and {len(self.curiosity_questions)} questions"
            )

        except Exception as e:
            logging.warning(f"⚠️ Could not load persistence data: {e}")

    def _save_persistence_data(self):
        """Save persistent data to files"""
        try:
            # Save knowledge gaps
            gaps_file = self.data_dir / "knowledge_gaps.json"
            with open(gaps_file, "w") as f:
                gaps_data = {
                    gap_id: asdict(gap) for gap_id, gap in self.knowledge_gaps.items()
                }
                json.dump(gaps_data, f, indent=2)

            # Save curiosity questions
            questions_file = self.data_dir / "curiosity_questions.json"
            with open(questions_file, "w") as f:
                questions_data = {
                    q_id: asdict(question)
                    for q_id, question in self.curiosity_questions.items()
                }
                json.dump(questions_data, f, indent=2)

            logging.info("💾 Saved curiosity data to persistence")

        except Exception as e:
            logging.error(f"❌ Could not save persistence data: {e}")


# Convenience functions for integration
async def detect_knowledge_gaps(
    memory_engine=None, timeframe_hours: int = 24
) -> List[KnowledgeGap]:
    """Convenience function to detect knowledge gaps"""
    agent = CuriosityAgent(memory_engine)
    return await agent.detect_knowledge_gaps(timeframe_hours)


async def generate_curiosity_questions(
    gap: KnowledgeGap, memory_engine=None
) -> List[CuriosityQuestion]:
    """Convenience function to generate questions for a gap"""
    agent = CuriosityAgent(memory_engine)
    return await agent.generate_curiosity_questions(gap)


if __name__ == "__main__":

    async def demo():
        """Demo the CuriosityAgent"""
        print("🔍 Curiosity Agent Demo")
        print("=" * 50)

        # Initialize agent
        agent = CuriosityAgent()

        # Detect knowledge gaps
        print("\n🔍 Detecting knowledge gaps...")
        gaps = await agent.detect_knowledge_gaps(timeframe_hours=48)

        for gap in gaps[:3]:  # Show first 3 gaps
            print(f"\n📍 Gap: {gap.description}")
            print(f"   Category: {gap.category}")
            print(f"   Priority: {gap.priority}")
            print(f"   Confidence: {gap.confidence_score:.2f}")

            # Generate questions for this gap
            questions = await agent.generate_curiosity_questions(gap)
            print(f"   Questions generated: {len(questions)}")

            for i, q in enumerate(questions[:2], 1):  # Show first 2 questions
                print(f"     {i}. {q.question_text}")
                print(f"        Method: {q.exploration_method}")
                print(f"        Urgency: {q.urgency}")

        # Show summary
        print("\n📊 Curiosity Summary:")
        summary = agent.get_curiosity_summary()
        print(f"   Total gaps: {summary['knowledge_gaps']['total']}")
        print(f"   Total questions: {summary['curiosity_questions']['total']}")
        print(f"   Success rate: {summary['exploration_success_rate']:.2f}")

        print("\n🎉 Demo completed!")

    # Run demo
    asyncio.run(demo())
