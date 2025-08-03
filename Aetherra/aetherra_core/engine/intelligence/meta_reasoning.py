"""
🧠 Meta-Reasoning Engine - Phase I
Advanced decision tracking and explanation system for Lyrixa
Intercepts and analyzes every major decision for transparency and learning
"""

import time
import json
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class DecisionType(Enum):
    """Types of decisions that can be tracked"""
    PLUGIN_SELECTION = "plugin_selection"
    GOAL_PLANNING = "goal_planning"
    ANSWER_GENERATION = "answer_generation"
    MEMORY_RETRIEVAL = "memory_retrieval"
    CONTEXT_ANALYSIS = "context_analysis"
    ERROR_HANDLING = "error_handling"


class ConfidenceLevel(Enum):
    """Confidence levels for decisions"""
    VERY_LOW = (0.0, 0.2, "very_low")
    LOW = (0.2, 0.4, "low")
    MEDIUM = (0.4, 0.6, "medium")
    HIGH = (0.6, 0.8, "high")
    VERY_HIGH = (0.8, 1.0, "very_high")

    def __init__(self, min_val, max_val, label):
        self.min_val = min_val
        self.max_val = max_val
        self.label = label

    @classmethod
    def from_score(cls, score: float):
        """Convert numeric confidence to level"""
        for level in cls:
            if level.min_val <= score <= level.max_val:
                return level
        return cls.MEDIUM


@dataclass
class DecisionTrace:
    """Structured decision trace with metadata"""
    trace_id: str
    decision_type: DecisionType
    timestamp: float
    context: Dict[str, Any]
    decision: str
    alternatives: List[str]
    confidence: float
    confidence_level: ConfidenceLevel
    explanation: str
    metadata: Dict[str, Any]
    outcome: Optional[str] = None
    feedback_score: Optional[float] = None
    learned_from: Optional[str] = None


class MetaReasoningEngine:
    """
    🧠 Meta-Reasoning Engine

    Intercepts every major decision Lyrixa makes and stores:
    - What was decided
    - Why it was chosen (context, memory links, intent)
    - How confident she was
    - What alternatives were rejected
    - What she learned from the interaction
    """

    def __init__(self, memory, plugin_manager):
        self.memory = memory
        self.plugin_manager = plugin_manager
        self.decision_history = []
        self.learning_patterns = {}

    def trace_decision(
        self,
        context: Dict[str, Any],
        decision: str,
        options: List[str],
        confidence: float,
        explanation: str,
        decision_type: DecisionType = DecisionType.PLUGIN_SELECTION,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DecisionTrace:
        """
        🔍 Core decision tracing method
        Records every major decision with full context and reasoning
        """
        trace = DecisionTrace(
            trace_id=str(uuid.uuid4()),
            decision_type=decision_type,
            timestamp=time.time(),
            context=context,
            decision=decision,
            alternatives=options,
            confidence=confidence,
            confidence_level=ConfidenceLevel.from_score(confidence),
            explanation=explanation,
            metadata=metadata or {}
        )

        # Store in memory system
        trace_data = {
            "type": "meta_trace",
            **asdict(trace)
        }
        self.memory.store(trace_data)

        # Keep local history for quick access
        self.decision_history.append(trace)

        # Analyze patterns for learning
        self._analyze_decision_pattern(trace)

        return trace

    def explain_plugin_choice(
        self,
        goal: str,
        context_summary: str,
        plugin_chosen: str,
        reason: str,
        confidence: float,
        memory_links: Optional[List[str]] = None,
        intent: Optional[str] = None
    ) -> DecisionTrace:
        """
        🧩 Explain why a specific plugin was chosen
        Enhanced version with memory links and intent tracking
        """
        available_plugins = self.plugin_manager.list_plugin_names() if self.plugin_manager else []

        context = {
            "goal": goal,
            "context": context_summary,
            "intent": intent,
            "memory_links": memory_links or [],
            "available_plugins_count": len(available_plugins)
        }

        metadata = {
            "plugin_success_rate": self._get_plugin_success_rate(plugin_chosen),
            "previous_usage_count": self._get_plugin_usage_count(plugin_chosen),
            "context_similarity": self._calculate_context_similarity(context_summary)
        }

        return self.trace_decision(
            context=context,
            decision=plugin_chosen,
            options=available_plugins,
            confidence=confidence,
            explanation=reason,
            decision_type=DecisionType.PLUGIN_SELECTION,
            metadata=metadata
        )

    def explain_goal_planning(
        self,
        user_request: str,
        planned_steps: List[str],
        confidence: float,
        reasoning: str
    ) -> DecisionTrace:
        """
        🎯 Explain goal planning and step breakdown decisions
        """
        context = {
            "user_request": user_request,
            "steps_count": len(planned_steps),
            "complexity_estimate": self._estimate_complexity(planned_steps)
        }

        alternatives = ["single_step", "alternative_breakdown", "direct_response"]

        return self.trace_decision(
            context=context,
            decision=f"multi_step_plan_{len(planned_steps)}",
            options=alternatives,
            confidence=confidence,
            explanation=reasoning,
            decision_type=DecisionType.GOAL_PLANNING,
            metadata={"planned_steps": planned_steps}
        )

    def explain_answer_generation(
        self,
        question: str,
        answer_approach: str,
        confidence: float,
        sources_used: List[str],
        reasoning: str
    ) -> DecisionTrace:
        """
        💬 Explain how an answer was generated
        """
        context = {
            "question": question,
            "question_type": self._classify_question_type(question),
            "sources_count": len(sources_used),
            "sources": sources_used
        }

        alternatives = ["direct_answer", "researched_answer", "plugin_assisted", "memory_based"]

        return self.trace_decision(
            context=context,
            decision=answer_approach,
            options=alternatives,
            confidence=confidence,
            explanation=reasoning,
            decision_type=DecisionType.ANSWER_GENERATION,
            metadata={"sources_used": sources_used}
        )

    def reflect_on_decision(self, trace_id: str, outcome: str, learned: str) -> bool:
        """
        🔁 Reflect on a past decision and learn from it
        Update the trace with outcome and learning
        """
        # Find the trace
        trace = self._find_trace_by_id(trace_id)
        if not trace:
            return False

        # Update with reflection
        trace.outcome = outcome
        trace.learned_from = learned

        # Store the learning pattern
        self._store_learning_pattern(trace)

        # Update in memory
        self._update_trace_in_memory(trace)

        return True

    def get_reasoning_history(self, limit: int = 10) -> List[DecisionTrace]:
        """
        📚 Get recent reasoning history for transparency
        """
        return self.decision_history[-limit:]

    def get_confidence_trends(self) -> Dict[str, float]:
        """
        📊 Analyze confidence trends across decision types
        """
        trends = {}
        for decision_type in DecisionType:
            relevant_traces = [t for t in self.decision_history if t.decision_type == decision_type]
            if relevant_traces:
                avg_confidence = sum(t.confidence for t in relevant_traces) / len(relevant_traces)
                trends[decision_type.value] = avg_confidence
        return trends

    def explain_reasoning_chain(self, goal: str) -> List[DecisionTrace]:
        """
        🔗 Show the complete reasoning chain for a goal
        """
        relevant_traces = [
            t for t in self.decision_history
            if goal.lower() in str(t.context).lower()
        ]
        return sorted(relevant_traces, key=lambda x: x.timestamp)

    def add_feedback(self, trace_id: str, feedback_score: float, feedback_text: str = "") -> bool:
        """
        👍 Add user feedback to a decision for learning
        """
        trace = self._find_trace_by_id(trace_id)
        if not trace:
            return False

        trace.feedback_score = feedback_score
        if feedback_text:
            trace.metadata["user_feedback"] = feedback_text

        # Learn from feedback
        self._learn_from_feedback(trace)

        return True

    def trace_ui_action(
        self,
        action_type: str,
        context: Dict[str, Any],
        target: str,
        confidence: float,
        explanation: str,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DecisionTrace:
        """
        🎯 Trace UI actions and their execution
        Track when Lyrixa triggers actual UI changes vs just talking about them
        """
        trace = DecisionTrace(
            trace_id=str(uuid.uuid4()),
            decision_type=DecisionType.CONTEXT_ANALYSIS,  # UI actions are context-driven
            timestamp=time.time(),
            context={
                **context,
                "action_type": action_type,
                "ui_target": target,
                "execution_success": success
            },
            decision=f"{action_type}_{target}",
            alternatives=["describe_only", "execute_action", "defer_action"],
            confidence=confidence,
            confidence_level=ConfidenceLevel.from_score(confidence),
            explanation=explanation,
            metadata={
                **(metadata or {}),
                "ui_action": True,
                "success": success,
                "timestamp": time.time()
            }
        )

        # Store in memory system
        trace_data = {
            "type": "ui_action_trace",
            **asdict(trace)
        }
        self.memory.store(trace_data)

        # Keep local history
        self.decision_history.append(trace)

        return trace

    def explain_intent_routing(
        self,
        user_input: str,
        detected_intent: str,
        confidence: float,
        routing_decision: str,
        available_routes: List[str],
        reasoning: str
    ) -> DecisionTrace:
        """
        🧠 Explain intent classification and routing decisions
        Track how user input gets routed to specific handlers
        """
        context = {
            "user_input": user_input,
            "input_length": len(user_input),
            "intent_keywords": self._extract_intent_keywords(user_input),
            "routing_target": routing_decision
        }

        metadata = {
            "detected_intent": detected_intent,
            "intent_confidence": confidence,
            "input_analysis": {
                "has_plugin_keyword": "plugin" in user_input.lower(),
                "has_load_keyword": "load" in user_input.lower(),
                "has_editor_keyword": "editor" in user_input.lower(),
                "has_code_keyword": "code" in user_input.lower()
            }
        }

        return self.trace_decision(
            context=context,
            decision=routing_decision,
            options=available_routes,
            confidence=confidence,
            explanation=reasoning,
            decision_type=DecisionType.CONTEXT_ANALYSIS,
            metadata=metadata
        )

    def _extract_intent_keywords(self, text: str) -> List[str]:
        """Extract key intent words from user input"""
        intent_words = ["plugin", "load", "editor", "create", "generate", "code", "file", "open", "inject", "populate"]
        return [word for word in intent_words if word in text.lower()]

    # [TOOL] Helper methods

    def _get_plugin_success_rate(self, plugin_name: str) -> float:
        """Calculate success rate for a plugin based on history"""
        plugin_traces = [t for t in self.decision_history if t.decision == plugin_name]
        if not plugin_traces:
            return 0.5  # Default neutral

        successful = [t for t in plugin_traces if t.feedback_score and t.feedback_score > 0.6]
        return len(successful) / len(plugin_traces)

    def _get_plugin_usage_count(self, plugin_name: str) -> int:
        """Count how many times a plugin has been used"""
        return len([t for t in self.decision_history if t.decision == plugin_name])

    def _calculate_context_similarity(self, context: str) -> float:
        """Calculate similarity to previous contexts (simplified)"""
        # Simplified implementation - could use embeddings in future
        similar_contexts = [
            t for t in self.decision_history[-10:]  # Last 10 decisions
            if any(word in str(t.context).lower() for word in context.lower().split()[:3])
        ]
        return min(len(similar_contexts) / 10.0, 1.0)

    def _estimate_complexity(self, steps: List[str]) -> str:
        """Estimate complexity of planned steps"""
        if len(steps) <= 2:
            return "simple"
        elif len(steps) <= 5:
            return "moderate"
        else:
            return "complex"

    def _classify_question_type(self, question: str) -> str:
        """Classify the type of question being asked"""
        question_lower = question.lower()
        if any(word in question_lower for word in ["what", "who", "where", "when"]):
            return "factual"
        elif any(word in question_lower for word in ["how", "why"]):
            return "explanatory"
        elif "?" in question:
            return "inquiry"
        else:
            return "statement"

    def _find_trace_by_id(self, trace_id: str) -> Optional[DecisionTrace]:
        """Find a trace by its ID"""
        for trace in self.decision_history:
            if trace.trace_id == trace_id:
                return trace
        return None

    def _analyze_decision_pattern(self, trace: DecisionTrace):
        """Analyze patterns in decision making for learning"""
        pattern_key = f"{trace.decision_type.value}_{trace.confidence_level.label}"
        if pattern_key not in self.learning_patterns:
            self.learning_patterns[pattern_key] = []
        self.learning_patterns[pattern_key].append(trace.trace_id)

    def _store_learning_pattern(self, trace: DecisionTrace):
        """Store a learning pattern from reflection"""
        learning_data = {
            "type": "learning_pattern",
            "decision_type": trace.decision_type.value,
            "outcome": trace.outcome,
            "learned": trace.learned_from,
            "timestamp": time.time()
        }
        self.memory.store(learning_data)

    def _update_trace_in_memory(self, trace: DecisionTrace):
        """Update an existing trace in memory with new information"""
        # This would need to be implemented based on your memory system
        updated_data = {
            "type": "meta_trace_update",
            "trace_id": trace.trace_id,
            **asdict(trace)
        }
        self.memory.store(updated_data)

    def _learn_from_feedback(self, trace: DecisionTrace):
        """Learn from user feedback on decisions"""
        if trace.feedback_score:
            # Adjust confidence in similar future decisions
            pattern = f"{trace.decision_type.value}_{trace.decision}"
            feedback_data = {
                "type": "feedback_learning",
                "pattern": pattern,
                "feedback_score": trace.feedback_score,
                "timestamp": time.time()
            }
            self.memory.store(feedback_data)

    # 📊 Analytics and reporting methods

    def generate_reasoning_report(self) -> Dict[str, Any]:
        """Generate a comprehensive reasoning analysis report"""
        return {
            "total_decisions": len(self.decision_history),
            "confidence_trends": self.get_confidence_trends(),
            "decision_type_distribution": self._get_decision_type_distribution(),
            "learning_patterns_count": len(self.learning_patterns),
            "average_confidence": self._get_average_confidence(),
            "recent_decisions": [asdict(t) for t in self.get_reasoning_history(5)]
        }

    def _get_decision_type_distribution(self) -> Dict[str, int]:
        """Get distribution of decision types"""
        distribution = {}
        for trace in self.decision_history:
            decision_type = trace.decision_type.value
            distribution[decision_type] = distribution.get(decision_type, 0) + 1
        return distribution

    def _get_average_confidence(self) -> float:
        """Calculate average confidence across all decisions"""
        if not self.decision_history:
            return 0.0
        return sum(t.confidence for t in self.decision_history) / len(self.decision_history)
