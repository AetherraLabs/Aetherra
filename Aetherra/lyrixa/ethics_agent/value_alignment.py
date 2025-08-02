"""
⚖️ Value Alignment Engine
=========================

Ensures AI decisions align with human values and ethical principles.
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class CoreValue(Enum):
    """Core human values for alignment."""

    HUMAN_WELFARE = "human_welfare"
    AUTONOMY = "autonomy"
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"
    PRIVACY = "privacy"
    TRUTH = "truth"
    SAFETY = "safety"


class ValueAlignmentEngine:
    """Engine for ensuring value alignment in AI decisions."""

    def __init__(self):
        """Initialize value alignment engine."""
        self.core_values = self._initialize_core_values()
        self.alignment_history = []

    def assess_value_alignment(
        self, decision: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess how well a decision aligns with core values.

        Args:
            decision: Decision to assess
            context: Optional context

        Returns:
            Value alignment assessment
        """
        assessment = {
            "decision_id": decision.get("id", "unknown"),
            "value_scores": {},
            "overall_alignment": 0.0,
            "alignment_concerns": [],
            "recommendations": [],
        }

        # Assess against each core value
        for value in CoreValue:
            score = self._assess_value_score(decision, value, context)
            assessment["value_scores"][value.value] = score

        # Calculate overall alignment
        assessment["overall_alignment"] = sum(
            assessment["value_scores"].values()
        ) / len(CoreValue)

        # Identify concerns and recommendations
        assessment["alignment_concerns"] = self._identify_alignment_concerns(assessment)
        assessment["recommendations"] = self._generate_alignment_recommendations(
            assessment
        )

        return assessment

    def _initialize_core_values(self) -> Dict[str, Dict[str, Any]]:
        """Initialize core values framework."""
        return {
            "human_welfare": {
                "description": "Promoting human wellbeing and flourishing",
                "weight": 1.0,
                "indicators": ["benefit", "help", "improve", "support"],
            },
            "autonomy": {
                "description": "Respecting human choice and self-determination",
                "weight": 0.9,
                "indicators": ["choice", "consent", "freedom", "control"],
            },
            "fairness": {
                "description": "Ensuring just and equitable treatment",
                "weight": 0.9,
                "indicators": ["fair", "equal", "just", "unbiased"],
            },
            "transparency": {
                "description": "Being open and explainable",
                "weight": 0.8,
                "indicators": ["transparent", "clear", "explain", "open"],
            },
            "privacy": {
                "description": "Protecting personal information and boundaries",
                "weight": 0.8,
                "indicators": ["private", "confidential", "secure", "protected"],
            },
            "truth": {
                "description": "Providing accurate and honest information",
                "weight": 0.9,
                "indicators": ["accurate", "honest", "truthful", "factual"],
            },
            "safety": {
                "description": "Preventing harm and ensuring security",
                "weight": 1.0,
                "indicators": ["safe", "secure", "protect", "prevent harm"],
            },
        }

    def _assess_value_score(
        self,
        decision: Dict[str, Any],
        value: CoreValue,
        context: Optional[Dict[str, Any]],
    ) -> float:
        """Assess alignment score for a specific value."""
        value_data = self.core_values[value.value]
        indicators = value_data["indicators"]

        # Simple scoring based on indicator presence
        decision_str = str(decision).lower()
        context_str = str(context).lower() if context else ""

        score = 0.5  # Default neutral score

        # Check for positive indicators
        for indicator in indicators:
            if indicator in decision_str or indicator in context_str:
                score += 0.1

        # Check for negative indicators (opposites)
        negative_indicators = self._get_negative_indicators(value)
        for neg_indicator in negative_indicators:
            if neg_indicator in decision_str:
                score -= 0.2

        return max(0.0, min(1.0, score))

    def _get_negative_indicators(self, value: CoreValue) -> List[str]:
        """Get negative indicators for a value."""
        negative_map = {
            CoreValue.HUMAN_WELFARE: ["harm", "damage", "hurt", "neglect"],
            CoreValue.AUTONOMY: ["force", "coerce", "mandate", "restrict"],
            CoreValue.FAIRNESS: ["unfair", "biased", "discriminate", "prejudice"],
            CoreValue.TRANSPARENCY: ["hide", "conceal", "secret", "opaque"],
            CoreValue.PRIVACY: ["expose", "leak", "violate", "intrude"],
            CoreValue.TRUTH: ["lie", "deceive", "false", "mislead"],
            CoreValue.SAFETY: ["dangerous", "risky", "unsafe", "harmful"],
        }
        return negative_map.get(value, [])

    def _identify_alignment_concerns(self, assessment: Dict[str, Any]) -> List[str]:
        """Identify value alignment concerns."""
        concerns = []

        # Check for low scores
        for value, score in assessment["value_scores"].items():
            if score < 0.4:
                concerns.append(f"Low alignment with {value}")

        # Check overall alignment
        if assessment["overall_alignment"] < 0.5:
            concerns.append("Overall value alignment below acceptable threshold")

        return concerns

    def _generate_alignment_recommendations(
        self, assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for improving value alignment."""
        recommendations = []

        if assessment["overall_alignment"] < 0.6:
            recommendations.append(
                "Consider revising decision to better align with core values"
            )

        if assessment["alignment_concerns"]:
            recommendations.append("Address specific value alignment concerns")

        recommendations.append("Document value alignment reasoning")

        return recommendations
