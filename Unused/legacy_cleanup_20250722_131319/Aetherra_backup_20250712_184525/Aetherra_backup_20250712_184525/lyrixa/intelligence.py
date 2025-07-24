#!/usr/bin/env python3
"""
🧠 LYRIXA INTELLIGENCE MODULE
============================

Core intelligence module for Lyrixa AI Assistant.
Provides advanced cognitive capabilities, pattern recognition, and adaptive learning.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LyrixaIntelligence:
    """
    🧠 Core Intelligence Engine for Lyrixa

    Provides advanced cognitive capabilities including:
    - Pattern recognition and learning
    - Context awareness and memory integration
    - Decision-making support
    - Adaptive behavior modification
    """

    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize the Lyrixa Intelligence system."""
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.intelligence_data_path = self.workspace_path / "lyrixa_intelligence.json"

        # Core intelligence components
        self.memory_patterns = {}
        self.learned_behaviors = {}
        self.decision_history = []
        self.cognitive_metrics = {
            "total_decisions": 0,
            "successful_predictions": 0,
            "pattern_recognitions": 0,
            "adaptive_adjustments": 0,
            "learning_iterations": 0,
        }

        # Intelligence state
        self.current_context = {}
        self.active_patterns = []
        self.confidence_threshold = 0.7

        # Load existing intelligence data
        self._load_intelligence_data()

        logger.info("🧠 Lyrixa Intelligence initialized")

    def _load_intelligence_data(self):
        """Load previously learned intelligence data."""
        try:
            if self.intelligence_data_path.exists():
                with open(self.intelligence_data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.memory_patterns = data.get("memory_patterns", {})
                    self.learned_behaviors = data.get("learned_behaviors", {})
                    self.decision_history = data.get("decision_history", [])
                    self.cognitive_metrics = data.get(
                        "cognitive_metrics", self.cognitive_metrics
                    )
                logger.info(f"📚 Loaded {len(self.memory_patterns)} memory patterns")
        except Exception as e:
            logger.warning(f"⚠️ Could not load intelligence data: {e}")

    def _save_intelligence_data(self):
        """Save current intelligence data to disk."""
        try:
            data = {
                "memory_patterns": self.memory_patterns,
                "learned_behaviors": self.learned_behaviors,
                "decision_history": self.decision_history[
                    -1000:
                ],  # Keep last 1000 decisions
                "cognitive_metrics": self.cognitive_metrics,
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.intelligence_data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Failed to save intelligence data: {e}")

    def analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze current context and extract intelligence insights.

        Args:
            context: Current context information

        Returns:
            Intelligence analysis with insights and recommendations
        """
        self.current_context = context

        analysis = {
            "context_type": self._classify_context(context),
            "complexity_score": self._calculate_complexity(context),
            "similar_patterns": self._find_similar_patterns(context),
            "recommended_actions": [],
            "confidence_level": 0.0,
        }

        # Generate recommendations based on analysis
        analysis["recommended_actions"] = self._generate_recommendations(analysis)
        analysis["confidence_level"] = self._calculate_confidence(analysis)

        # Learn from this analysis
        self._learn_from_context(context, analysis)

        return analysis

    def _classify_context(self, context: Dict[str, Any]) -> str:
        """Classify the type of context we're dealing with."""
        if "code" in context or "programming" in str(context).lower():
            return "programming"
        elif "chat" in context or "conversation" in str(context).lower():
            return "conversational"
        elif "analysis" in context or "data" in str(context).lower():
            return "analytical"
        elif "goal" in context or "task" in str(context).lower():
            return "goal_oriented"
        else:
            return "general"

    def _calculate_complexity(self, context: Dict[str, Any]) -> float:
        """Calculate complexity score for the given context."""
        complexity = 0.0

        # Base complexity from context size
        complexity += min(len(str(context)) / 1000, 1.0)

        # Additional complexity factors
        if isinstance(context, dict):
            complexity += min(len(context) / 10, 0.5)

            # Check for nested structures
            for value in context.values():
                if isinstance(value, (dict, list)):
                    complexity += 0.1

        # Normalize to 0-1 scale
        return min(complexity, 1.0)

    def _find_similar_patterns(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar patterns in memory that match the current context."""
        similar_patterns = []
        context_str = str(context).lower()

        for pattern_id, pattern_data in self.memory_patterns.items():
            similarity = self._calculate_similarity(
                context_str, pattern_data.get("context_signature", "")
            )

            if similarity > 0.3:  # 30% similarity threshold
                similar_patterns.append(
                    {
                        "pattern_id": pattern_id,
                        "similarity": similarity,
                        "success_rate": pattern_data.get("success_rate", 0.0),
                        "usage_count": pattern_data.get("usage_count", 0),
                        "last_used": pattern_data.get("last_used", ""),
                    }
                )

        # Sort by similarity and success rate
        similar_patterns.sort(
            key=lambda x: (x["similarity"], x["success_rate"]), reverse=True
        )
        return similar_patterns[:5]  # Return top 5 patterns

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate intelligent recommendations based on analysis."""
        recommendations = []
        context_type = analysis["context_type"]
        complexity = analysis["complexity_score"]
        similar_patterns = analysis["similar_patterns"]

        # Context-specific recommendations
        if context_type == "programming":
            recommendations.extend(
                [
                    "Consider code analysis and optimization",
                    "Review for best practices and patterns",
                    "Check for potential refactoring opportunities",
                ]
            )
        elif context_type == "conversational":
            recommendations.extend(
                [
                    "Maintain conversational context",
                    "Consider user intent and preferences",
                    "Adapt communication style as needed",
                ]
            )
        elif context_type == "goal_oriented":
            recommendations.extend(
                [
                    "Break down complex goals into smaller tasks",
                    "Consider dependencies and prerequisites",
                    "Plan execution strategy with checkpoints",
                ]
            )

        # Complexity-based recommendations
        if complexity > 0.7:
            recommendations.append(
                "High complexity detected - consider step-by-step approach"
            )
        elif complexity < 0.3:
            recommendations.append("Low complexity - can proceed with direct approach")

        # Pattern-based recommendations
        if similar_patterns:
            best_pattern = similar_patterns[0]
            if best_pattern["success_rate"] > 0.8:
                recommendations.append(
                    f"Similar successful pattern found (success rate: {best_pattern['success_rate']:.1%})"
                )
            else:
                recommendations.append(
                    "Similar patterns exist but with mixed results - proceed cautiously"
                )

        return recommendations

    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence level for the analysis."""
        confidence = 0.5  # Base confidence

        # Adjust based on similar patterns
        similar_patterns = analysis["similar_patterns"]
        if similar_patterns:
            best_pattern = similar_patterns[0]
            confidence += best_pattern["similarity"] * 0.3
            confidence += best_pattern["success_rate"] * 0.2

        # Adjust based on complexity
        complexity = analysis["complexity_score"]
        if complexity < 0.5:
            confidence += 0.1  # More confident with simpler contexts
        else:
            confidence -= 0.1  # Less confident with complex contexts

        return min(max(confidence, 0.0), 1.0)

    def _learn_from_context(self, context: Dict[str, Any], analysis: Dict[str, Any]):
        """Learn from the current context and analysis."""
        # Create a pattern signature
        context_signature = str(context).lower()
        pattern_id = f"pattern_{hash(context_signature) % 100000}"

        # Update or create pattern
        if pattern_id in self.memory_patterns:
            pattern = self.memory_patterns[pattern_id]
            pattern["usage_count"] += 1
            pattern["last_used"] = datetime.now().isoformat()
        else:
            self.memory_patterns[pattern_id] = {
                "context_signature": context_signature,
                "context_type": analysis["context_type"],
                "complexity_score": analysis["complexity_score"],
                "usage_count": 1,
                "success_rate": 0.5,  # Start with neutral success rate
                "created": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
            }

        self.cognitive_metrics["pattern_recognitions"] += 1
        self._save_intelligence_data()

    def record_decision_outcome(
        self,
        decision: str,
        context: Dict[str, Any],
        success: bool,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Record the outcome of a decision for learning purposes.

        Args:
            decision: The decision that was made
            context: The context in which the decision was made
            success: Whether the decision was successful
            details: Additional details about the outcome
        """
        outcome_record = {
            "decision": decision,
            "context_type": self._classify_context(context),
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }

        self.decision_history.append(outcome_record)
        self.cognitive_metrics["total_decisions"] += 1

        if success:
            self.cognitive_metrics["successful_predictions"] += 1

        # Update pattern success rates
        self._update_pattern_success_rates(context, success)

        # Learn from this outcome
        self._adapt_behavior(decision, context, success)

        self._save_intelligence_data()

    def _update_pattern_success_rates(self, context: Dict[str, Any], success: bool):
        """Update success rates for patterns matching this context."""
        context_signature = str(context).lower()

        for pattern_id, pattern_data in self.memory_patterns.items():
            similarity = self._calculate_similarity(
                context_signature, pattern_data["context_signature"]
            )

            if similarity > 0.5:  # High similarity threshold for success rate updates
                current_rate = pattern_data["success_rate"]
                usage_count = pattern_data["usage_count"]

                # Calculate new success rate using weighted average
                new_rate = (
                    current_rate * (usage_count - 1) + (1.0 if success else 0.0)
                ) / usage_count
                pattern_data["success_rate"] = new_rate

    def _adapt_behavior(self, decision: str, context: Dict[str, Any], success: bool):
        """Adapt behavior based on decision outcomes."""
        behavior_key = f"{self._classify_context(context)}_{decision}"

        if behavior_key not in self.learned_behaviors:
            self.learned_behaviors[behavior_key] = {
                "total_attempts": 0,
                "successful_attempts": 0,
                "adaptations": [],
            }

        behavior = self.learned_behaviors[behavior_key]
        behavior["total_attempts"] += 1

        if success:
            behavior["successful_attempts"] += 1
        else:
            # Record adaptation for unsuccessful attempts
            adaptation = {
                "timestamp": datetime.now().isoformat(),
                "context_summary": str(context)[:200],
                "suggested_improvement": self._suggest_improvement(decision, context),
            }
            behavior["adaptations"].append(adaptation)

        self.cognitive_metrics["adaptive_adjustments"] += 1

    def _suggest_improvement(self, decision: str, context: Dict[str, Any]) -> str:
        """Suggest improvements for unsuccessful decisions."""
        context_type = self._classify_context(context)

        improvement_suggestions = {
            "programming": "Consider alternative algorithms or design patterns",
            "conversational": "Adjust communication style or provide more context",
            "analytical": "Gather more data or use different analysis methods",
            "goal_oriented": "Break down into smaller, more manageable tasks",
            "general": "Analyze context more thoroughly before deciding",
        }

        return improvement_suggestions.get(
            context_type, "Review approach and consider alternatives"
        )

    def get_intelligence_status(self) -> Dict[str, Any]:
        """Get current intelligence system status and metrics."""
        success_rate = self.cognitive_metrics["successful_predictions"] / max(
            1, self.cognitive_metrics["total_decisions"]
        )

        return {
            "cognitive_metrics": self.cognitive_metrics,
            "memory_patterns_count": len(self.memory_patterns),
            "learned_behaviors_count": len(self.learned_behaviors),
            "decision_history_length": len(self.decision_history),
            "overall_success_rate": success_rate,
            "intelligence_level": self._assess_intelligence_level(),
            "active_patterns": len(self.active_patterns),
            "current_context_type": self._classify_context(self.current_context)
            if self.current_context
            else "none",
            "last_updated": datetime.now().isoformat(),
        }

    def _assess_intelligence_level(self) -> str:
        """Assess the current intelligence level based on metrics."""
        pattern_count = len(self.memory_patterns)
        decision_count = self.cognitive_metrics["total_decisions"]
        success_rate = self.cognitive_metrics["successful_predictions"] / max(
            1, self.cognitive_metrics["total_decisions"]
        )

        if pattern_count > 100 and decision_count > 50 and success_rate > 0.8:
            return "expert"
        elif pattern_count > 50 and decision_count > 25 and success_rate > 0.7:
            return "advanced"
        elif pattern_count > 20 and decision_count > 10 and success_rate > 0.6:
            return "intermediate"
        elif pattern_count > 5 and decision_count > 5:
            return "developing"
        else:
            return "novice"

    def predict_outcome(
        self, proposed_action: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict the likely outcome of a proposed action in the given context.

        Args:
            proposed_action: The action being considered
            context: The current context

        Returns:
            Prediction with confidence level and reasoning
        """
        analysis = self.analyze_context(context)

        # Find relevant patterns
        relevant_patterns = self._find_similar_patterns(context)

        # Calculate prediction
        if relevant_patterns:
            # Use pattern-based prediction
            weighted_success = sum(
                p["success_rate"] * p["similarity"] for p in relevant_patterns
            ) / sum(p["similarity"] for p in relevant_patterns)

            confidence = sum(p["similarity"] for p in relevant_patterns) / len(
                relevant_patterns
            )
        else:
            # Use base prediction
            complexity = analysis["complexity_score"]
            weighted_success = 0.7 - (
                complexity * 0.2
            )  # Higher complexity = lower success probability
            confidence = 0.3  # Low confidence without patterns

        prediction = {
            "predicted_success_probability": max(0.1, min(0.9, weighted_success)),
            "confidence_level": min(confidence, 1.0),
            "reasoning": self._generate_prediction_reasoning(
                analysis, relevant_patterns
            ),
            "recommendations": analysis["recommended_actions"],
            "risk_factors": self._identify_risk_factors(context, analysis),
            "mitigation_strategies": self._suggest_mitigation_strategies(
                context, analysis
            ),
        }

        return prediction

    def _generate_prediction_reasoning(
        self, analysis: Dict[str, Any], patterns: List[Dict[str, Any]]
    ) -> str:
        """Generate reasoning for the prediction."""
        reasoning_parts = []

        if patterns:
            best_pattern = patterns[0]
            reasoning_parts.append(
                f"Based on {len(patterns)} similar patterns with {best_pattern['success_rate']:.1%} average success rate"
            )
        else:
            reasoning_parts.append(
                "No similar patterns found, using baseline prediction"
            )

        complexity = analysis["complexity_score"]
        if complexity > 0.7:
            reasoning_parts.append(
                "High complexity detected, which may reduce success probability"
            )
        elif complexity < 0.3:
            reasoning_parts.append("Low complexity favors successful outcome")

        return ". ".join(reasoning_parts)

    def _identify_risk_factors(
        self, context: Dict[str, Any], analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify potential risk factors in the current context."""
        risks = []

        if analysis["complexity_score"] > 0.8:
            risks.append("High complexity may lead to unexpected issues")

        if not analysis["similar_patterns"]:
            risks.append("No historical patterns available for guidance")

        context_type = analysis["context_type"]
        if context_type == "programming":
            risks.append(
                "Code changes may introduce bugs or break existing functionality"
            )
        elif context_type == "goal_oriented":
            risks.append("Goal dependencies may not be fully understood")

        return risks

    def _suggest_mitigation_strategies(
        self, context: Dict[str, Any], analysis: Dict[str, Any]
    ) -> List[str]:
        """Suggest strategies to mitigate identified risks."""
        strategies = []

        if analysis["complexity_score"] > 0.7:
            strategies.append("Break down into smaller, manageable steps")
            strategies.append("Implement incremental testing and validation")

        if not analysis["similar_patterns"]:
            strategies.append("Proceed cautiously and gather feedback frequently")
            strategies.append("Create checkpoints for rollback if needed")

        context_type = analysis["context_type"]
        if context_type == "programming":
            strategies.append("Use version control and create backups")
            strategies.append("Implement comprehensive testing")

        return strategies

    def export_intelligence_report(self, output_path: Optional[str] = None) -> str:
        """Export a comprehensive intelligence report."""
        if not output_path:
            output_path = str(
                self.workspace_path
                / f"lyrixa_intelligence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "lyrixa_version": "2.1.0",
                "intelligence_version": "1.0.0",
            },
            "intelligence_status": self.get_intelligence_status(),
            "top_patterns": self._get_top_patterns(10),
            "learned_behaviors_summary": self._summarize_learned_behaviors(),
            "recent_decisions": self.decision_history[-20:],
            "recommendations": self._generate_system_recommendations(),
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"📊 Intelligence report exported to: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"❌ Failed to export intelligence report: {e}")
            return ""

    def _get_top_patterns(self, count: int) -> List[Dict[str, Any]]:
        """Get the top patterns by usage and success rate."""
        patterns = []

        for pattern_id, pattern_data in self.memory_patterns.items():
            score = pattern_data["usage_count"] * pattern_data["success_rate"]
            patterns.append({"pattern_id": pattern_id, "score": score, **pattern_data})

        patterns.sort(key=lambda x: x["score"], reverse=True)
        return patterns[:count]

    def _summarize_learned_behaviors(self) -> Dict[str, Any]:
        """Summarize learned behaviors."""
        summary = {
            "total_behaviors": len(self.learned_behaviors),
            "successful_behaviors": 0,
            "improvement_areas": [],
        }

        for behavior_key, behavior_data in self.learned_behaviors.items():
            success_rate = behavior_data["successful_attempts"] / max(
                1, behavior_data["total_attempts"]
            )

            if success_rate > 0.7:
                summary["successful_behaviors"] += 1
            elif success_rate < 0.5:
                summary["improvement_areas"].append(
                    {
                        "behavior": behavior_key,
                        "success_rate": success_rate,
                        "attempts": behavior_data["total_attempts"],
                    }
                )

        return summary

    def _generate_system_recommendations(self) -> List[str]:
        """Generate recommendations for system improvement."""
        recommendations = []
        status = self.get_intelligence_status()

        if status["memory_patterns_count"] < 20:
            recommendations.append(
                "Increase pattern collection by engaging with diverse contexts"
            )

        if status["overall_success_rate"] < 0.7:
            recommendations.append("Focus on improving decision-making accuracy")

        if status["intelligence_level"] == "novice":
            recommendations.append(
                "Continue learning and pattern recognition to advance intelligence level"
            )

        recommendations.append("Regular intelligence data backups recommended")
        recommendations.append("Consider implementing additional learning algorithms")

        return recommendations


# Global intelligence instance
_intelligence_instance = None


def get_intelligence() -> LyrixaIntelligence:
    """Get the global Lyrixa Intelligence instance."""
    global _intelligence_instance
    if _intelligence_instance is None:
        _intelligence_instance = LyrixaIntelligence()
    return _intelligence_instance


def initialize_intelligence(workspace_path: Optional[str] = None) -> LyrixaIntelligence:
    """Initialize the Lyrixa Intelligence system."""
    global _intelligence_instance
    _intelligence_instance = LyrixaIntelligence(workspace_path)
    return _intelligence_instance


# Convenience functions for common operations
def analyze_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze context using the global intelligence instance."""
    return get_intelligence().analyze_context(context)


def predict_outcome(action: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Predict outcome using the global intelligence instance."""
    return get_intelligence().predict_outcome(action, context)


def record_outcome(
    decision: str,
    context: Dict[str, Any],
    success: bool,
    details: Optional[Dict[str, Any]] = None,
):
    """Record decision outcome using the global intelligence instance."""
    return get_intelligence().record_decision_outcome(
        decision, context, success, details
    )


if __name__ == "__main__":
    # Example usage and testing
    intelligence = LyrixaIntelligence()

    # Example context analysis
    test_context = {
        "type": "code_analysis",
        "language": "python",
        "complexity": "medium",
        "goal": "optimize performance",
    }

    analysis = intelligence.analyze_context(test_context)
    print("🧠 Context Analysis:")
    print(json.dumps(analysis, indent=2))

    # Example prediction
    prediction = intelligence.predict_outcome("refactor_code", test_context)
    print("\n🔮 Outcome Prediction:")
    print(json.dumps(prediction, indent=2))

    # Example outcome recording
    intelligence.record_decision_outcome(
        "refactor_code", test_context, True, {"performance_gain": "15%"}
    )

    # Status check
    status = intelligence.get_intelligence_status()
    print("\n📊 Intelligence Status:")
    print(json.dumps(status, indent=2))
