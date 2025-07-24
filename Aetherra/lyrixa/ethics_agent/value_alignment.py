#!/usr/bin/env python3
"""
🎯 VALUE ALIGNMENT ENGINE - Core Beliefs & Goal Alignment System
==============================================================

Scores actions, decisions, and goals based on alignment with Lyrixa's
internalized core beliefs and values. Ensures consistent value-driven behavior.

Key Features:
• Multi-dimensional value assessment
• Goal-value alignment scoring
• Value conflict detection and resolution
• Dynamic value priority adjustment
• Belief system coherence monitoring
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import ethics components
try:
    from .bias_detector import BiasDetection, BiasType
    from .moral_reasoning import EthicalFramework, EthicalPrinciple
except ImportError:
    print("⚠️ Using local import paths for value alignment")
    import sys

    sys.path.append(".")


class CoreValue(Enum):
    """Core values that guide behavior"""

    HELPFULNESS = "helpfulness"  # Assist and support users effectively
    TRUTHFULNESS = "truthfulness"  # Provide accurate and honest information
    HARMLESSNESS = "harmlessness"  # Avoid causing harm or distress
    FAIRNESS = "fairness"  # Treat all users equitably
    PRIVACY = "privacy"  # Respect and protect personal information
    AUTONOMY = "autonomy"  # Respect user choice and independence
    GROWTH = "growth"  # Facilitate learning and development
    TRANSPARENCY = "transparency"  # Be open about capabilities and limitations
    RELIABILITY = "reliability"  # Provide consistent and dependable service
    RESPECT = "respect"  # Honor dignity and worth of all individuals


class ValuePriority(Enum):
    """Priority levels for value conflicts"""

    CRITICAL = "critical"  # Never compromise
    HIGH = "high"  # Strong preference
    MODERATE = "moderate"  # Balanced consideration
    LOW = "low"  # Can be deprioritized


class AlignmentLevel(Enum):
    """Levels of value alignment"""

    PERFECT = "perfect"  # 0.9-1.0
    STRONG = "strong"  # 0.7-0.9
    MODERATE = "moderate"  # 0.5-0.7
    WEAK = "weak"  # 0.3-0.5
    MISALIGNED = "misaligned"  # 0.0-0.3


@dataclass
class ValueAssessment:
    """Assessment of value alignment for an action/goal"""

    target_item: str
    item_type: str  # action, goal, decision, memory
    value_scores: Dict[CoreValue, float]
    overall_alignment: float
    alignment_level: AlignmentLevel
    value_conflicts: List[str]
    recommendations: List[str]
    assessment_timestamp: str


@dataclass
class ValueProfile:
    """Current value priority profile"""

    value_priorities: Dict[CoreValue, ValuePriority]
    value_weights: Dict[CoreValue, float]
    conflict_resolution_rules: Dict[str, str]
    last_updated: str
    profile_confidence: float


class ValueAlignmentEngine:
    """
    Comprehensive value alignment assessment and management system
    """

    def __init__(self, data_dir: str = "value_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize core value system
        self.value_profile = self._initialize_value_profile()

        # Assessment history
        self.assessment_history: List[ValueAssessment] = []

        # Value conflict patterns
        self.conflict_patterns: Dict[str, List[str]] = {}

        # Load existing assessments
        self._load_assessment_history()

        print("🎯 ValueAlignmentEngine initialized with comprehensive value framework")

    def _initialize_value_profile(self) -> ValueProfile:
        """Initialize the core value profile"""

        # Set value priorities based on ethical principles
        value_priorities = {
            CoreValue.HARMLESSNESS: ValuePriority.CRITICAL,  # Never cause harm
            CoreValue.TRUTHFULNESS: ValuePriority.CRITICAL,  # Always be honest
            CoreValue.PRIVACY: ValuePriority.HIGH,  # Strong privacy protection
            CoreValue.RESPECT: ValuePriority.HIGH,  # Respect all individuals
            CoreValue.FAIRNESS: ValuePriority.HIGH,  # Treat all equitably
            CoreValue.AUTONOMY: ValuePriority.HIGH,  # Respect user choice
            CoreValue.HELPFULNESS: ValuePriority.MODERATE,  # Balance with other values
            CoreValue.TRANSPARENCY: ValuePriority.MODERATE,  # Balance with privacy
            CoreValue.GROWTH: ValuePriority.MODERATE,  # Support development
            CoreValue.RELIABILITY: ValuePriority.MODERATE,  # Consistent service
        }

        # Convert priorities to numerical weights
        priority_weights = {
            ValuePriority.CRITICAL: 1.0,
            ValuePriority.HIGH: 0.8,
            ValuePriority.MODERATE: 0.6,
            ValuePriority.LOW: 0.4,
        }

        value_weights = {
            value: priority_weights[priority]
            for value, priority in value_priorities.items()
        }

        # Define conflict resolution rules
        conflict_resolution_rules = {
            "helpfulness_vs_privacy": "Privacy takes precedence with user consent options",
            "transparency_vs_privacy": "Privacy protected while maintaining transparency about process",
            "autonomy_vs_helpfulness": "User choice respected with helpful guidance offered",
            "truthfulness_vs_harmlessness": "Truth delivered with care to minimize harm",
            "fairness_vs_individual_preference": "Fair treatment with personalization within bounds",
        }

        return ValueProfile(
            value_priorities=value_priorities,
            value_weights=value_weights,
            conflict_resolution_rules=conflict_resolution_rules,
            last_updated=datetime.now().isoformat(),
            profile_confidence=0.95,
        )

    def _load_assessment_history(self):
        """Load existing assessment history"""
        history_file = self.data_dir / "assessment_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    history_data = json.load(f)
                    # Reconstruct ValueAssessment objects
                    for assessment_data in history_data:
                        assessment = ValueAssessment(
                            target_item=assessment_data["target_item"],
                            item_type=assessment_data["item_type"],
                            value_scores={
                                CoreValue(k): v
                                for k, v in assessment_data["value_scores"].items()
                            },
                            overall_alignment=assessment_data["overall_alignment"],
                            alignment_level=AlignmentLevel(
                                assessment_data["alignment_level"]
                            ),
                            value_conflicts=assessment_data["value_conflicts"],
                            recommendations=assessment_data["recommendations"],
                            assessment_timestamp=assessment_data[
                                "assessment_timestamp"
                            ],
                        )
                        self.assessment_history.append(assessment)
                print(f"   📚 Loaded {len(self.assessment_history)} value assessments")
            except Exception as e:
                print(f"   ⚠️ Error loading assessment history: {e}")

    async def assess_value_alignment(
        self,
        item_description: str,
        item_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValueAssessment:
        """
        Comprehensive value alignment assessment
        """
        print(
            f"🎯 Assessing value alignment for {item_type}: {item_description[:50]}..."
        )

        # Assess alignment with each core value
        value_scores = {}
        for value in CoreValue:
            score = await self._assess_individual_value_alignment(
                item_description, item_type, value, context
            )
            value_scores[value] = score

        # Calculate overall alignment score
        overall_alignment = await self._calculate_overall_alignment(value_scores)

        # Determine alignment level
        alignment_level = self._determine_alignment_level(overall_alignment)

        # Identify value conflicts
        value_conflicts = await self._identify_value_conflicts(
            item_description, value_scores, context
        )

        # Generate recommendations
        recommendations = await self._generate_alignment_recommendations(
            item_description, value_scores, value_conflicts, alignment_level
        )

        # Create assessment
        assessment = ValueAssessment(
            target_item=item_description,
            item_type=item_type,
            value_scores=value_scores,
            overall_alignment=overall_alignment,
            alignment_level=alignment_level,
            value_conflicts=value_conflicts,
            recommendations=recommendations,
            assessment_timestamp=datetime.now().isoformat(),
        )

        # Store assessment
        self.assessment_history.append(assessment)
        await self._save_assessment_history()

        print(
            f"   📊 Overall alignment: {overall_alignment:.2f} ({alignment_level.value.upper()})"
        )
        if value_conflicts:
            print(f"   ⚠️ Conflicts detected: {len(value_conflicts)}")

        return assessment

    async def _assess_individual_value_alignment(
        self,
        item_description: str,
        item_type: str,
        value: CoreValue,
        context: Optional[Dict[str, Any]],
    ) -> float:
        """Assess alignment with a specific core value"""

        if value == CoreValue.HELPFULNESS:
            return await self._assess_helpfulness_alignment(item_description, context)
        elif value == CoreValue.TRUTHFULNESS:
            return await self._assess_truthfulness_alignment(item_description, context)
        elif value == CoreValue.HARMLESSNESS:
            return await self._assess_harmlessness_alignment(item_description, context)
        elif value == CoreValue.FAIRNESS:
            return await self._assess_fairness_alignment(item_description, context)
        elif value == CoreValue.PRIVACY:
            return await self._assess_privacy_alignment(item_description, context)
        elif value == CoreValue.AUTONOMY:
            return await self._assess_autonomy_alignment(item_description, context)
        elif value == CoreValue.GROWTH:
            return await self._assess_growth_alignment(item_description, context)
        elif value == CoreValue.TRANSPARENCY:
            return await self._assess_transparency_alignment(item_description, context)
        elif value == CoreValue.RELIABILITY:
            return await self._assess_reliability_alignment(item_description, context)
        elif value == CoreValue.RESPECT:
            return await self._assess_respect_alignment(item_description, context)
        else:
            return 0.7  # Default moderate alignment

    async def _assess_helpfulness_alignment(
        self, item_description: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess alignment with helpfulness value"""
        score = 0.5  # Base score

        # Positive indicators
        helpful_keywords = [
            "assist",
            "help",
            "support",
            "improve",
            "benefit",
            "enhance",
        ]
        if any(keyword in item_description.lower() for keyword in helpful_keywords):
            score += 0.3

        # Context considerations
        if context:
            user_benefit = context.get("user_benefit", False)
            if user_benefit:
                score += 0.2

            service_improvement = context.get("service_improvement", False)
            if service_improvement:
                score += 0.1

        # Negative indicators
        unhelpful_keywords = ["hinder", "obstruct", "complicate", "confuse"]
        if any(keyword in item_description.lower() for keyword in unhelpful_keywords):
            score -= 0.4

        return max(0.0, min(1.0, score))

    async def _assess_truthfulness_alignment(
        self, item_description: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess alignment with truthfulness value"""
        score = 0.8  # High base score for truthfulness

        # Positive indicators
        truthful_keywords = ["accurate", "honest", "factual", "correct", "verify"]
        if any(keyword in item_description.lower() for keyword in truthful_keywords):
            score += 0.2

        # Negative indicators
        deceptive_keywords = ["mislead", "deceive", "false", "fabricate", "lie"]
        if any(keyword in item_description.lower() for keyword in deceptive_keywords):
            score -= 0.8

        # Context considerations
        if context:
            information_accuracy = context.get("information_accuracy", 1.0)
            score *= information_accuracy

        return max(0.0, min(1.0, score))

    async def _assess_harmlessness_alignment(
        self, item_description: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess alignment with harmlessness value"""
        score = 0.9  # Very high base score for harmlessness

        # Check for harm indicators
        harm_keywords = ["harm", "damage", "hurt", "injure", "endanger", "risk"]
        harm_count = sum(
            1 for keyword in harm_keywords if keyword in item_description.lower()
        )

        if harm_count > 0:
            score -= harm_count * 0.3

        # Positive safety indicators
        safety_keywords = ["safe", "protect", "secure", "prevent harm"]
        if any(keyword in item_description.lower() for keyword in safety_keywords):
            score += 0.1

        # Context considerations
        if context:
            risk_level = context.get("risk_level", "low")
            risk_penalties = {"low": 0.0, "medium": 0.2, "high": 0.5, "critical": 0.8}
            score -= risk_penalties.get(risk_level, 0.0)

        return max(0.0, min(1.0, score))

    async def _assess_fairness_alignment(
        self, item_description: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess alignment with fairness value"""
        score = 0.7  # Base score

        # Positive indicators
        fair_keywords = ["fair", "equal", "equitable", "unbiased", "impartial"]
        if any(keyword in item_description.lower() for keyword in fair_keywords):
            score += 0.2

        # Negative indicators
        unfair_keywords = ["discriminate", "bias", "unfair", "prejudice", "favor"]
        if any(keyword in item_description.lower() for keyword in unfair_keywords):
            score -= 0.4

        # Context considerations
        if context:
            equal_treatment = context.get("equal_treatment", True)
            if not equal_treatment:
                score -= 0.3

        return max(0.0, min(1.0, score))

    async def _assess_privacy_alignment(
        self, item_description: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess alignment with privacy value"""
        score = 0.8  # High base score for privacy

        # Privacy protection indicators
        privacy_keywords = ["private", "confidential", "protect data", "anonymous"]
        if any(keyword in item_description.lower() for keyword in privacy_keywords):
            score += 0.2

        # Privacy violation indicators
        violation_keywords = ["share data", "expose", "reveal", "access personal"]
        if any(keyword in item_description.lower() for keyword in violation_keywords):
            score -= 0.5

        # Context considerations
        if context:
            user_consent = context.get("user_consent", True)
            if not user_consent:
                score -= 0.4

            data_protection = context.get("data_protection", True)
            if not data_protection:
                score -= 0.6

        return max(0.0, min(1.0, score))

    async def _assess_autonomy_alignment(
        self, item_description: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess alignment with autonomy value"""
        score = 0.7  # Base score

        # Autonomy support indicators
        autonomy_keywords = ["choice", "option", "decide", "control", "voluntary"]
        if any(keyword in item_description.lower() for keyword in autonomy_keywords):
            score += 0.2

        # Autonomy violation indicators
        violation_keywords = [
            "force",
            "require",
            "mandate",
            "automatic",
            "without consent",
        ]
        if any(keyword in item_description.lower() for keyword in violation_keywords):
            score -= 0.4

        # Context considerations
        if context:
            user_control = context.get("user_control", True)
            if not user_control:
                score -= 0.3

        return max(0.0, min(1.0, score))

    async def _assess_growth_alignment(
        self, item_description: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess alignment with growth value"""
        score = 0.6  # Base score

        # Growth indicators
        growth_keywords = [
            "learn",
            "develop",
            "improve",
            "skill",
            "knowledge",
            "progress",
        ]
        if any(keyword in item_description.lower() for keyword in growth_keywords):
            score += 0.3

        # Context considerations
        if context:
            learning_opportunity = context.get("learning_opportunity", False)
            if learning_opportunity:
                score += 0.2

        return max(0.0, min(1.0, score))

    async def _assess_transparency_alignment(
        self, item_description: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess alignment with transparency value"""
        score = 0.7  # Base score

        # Transparency indicators
        transparent_keywords = ["explain", "clarify", "open", "visible", "clear"]
        if any(keyword in item_description.lower() for keyword in transparent_keywords):
            score += 0.2

        # Opacity indicators
        opaque_keywords = ["hidden", "secret", "unclear", "obscure"]
        if any(keyword in item_description.lower() for keyword in opaque_keywords):
            score -= 0.3

        # Context considerations
        if context:
            process_transparency = context.get("process_transparency", True)
            if not process_transparency:
                score -= 0.3

        return max(0.0, min(1.0, score))

    async def _assess_reliability_alignment(
        self, item_description: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess alignment with reliability value"""
        score = 0.8  # High base score

        # Reliability indicators
        reliable_keywords = ["consistent", "dependable", "stable", "reliable"]
        if any(keyword in item_description.lower() for keyword in reliable_keywords):
            score += 0.2

        # Unreliability indicators
        unreliable_keywords = ["inconsistent", "unreliable", "unstable", "erratic"]
        if any(keyword in item_description.lower() for keyword in unreliable_keywords):
            score -= 0.4

        return max(0.0, min(1.0, score))

    async def _assess_respect_alignment(
        self, item_description: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess alignment with respect value"""
        score = 0.8  # High base score

        # Respect indicators
        respect_keywords = ["respect", "dignity", "courtesy", "polite", "considerate"]
        if any(keyword in item_description.lower() for keyword in respect_keywords):
            score += 0.2

        # Disrespect indicators
        disrespect_keywords = ["disrespect", "rude", "dismissive", "condescending"]
        if any(keyword in item_description.lower() for keyword in disrespect_keywords):
            score -= 0.5

        return max(0.0, min(1.0, score))

    async def _calculate_overall_alignment(
        self, value_scores: Dict[CoreValue, float]
    ) -> float:
        """Calculate weighted overall value alignment score"""

        weighted_sum = 0.0
        total_weight = 0.0

        for value, score in value_scores.items():
            weight = self.value_profile.value_weights.get(value, 0.6)
            weighted_sum += score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def _determine_alignment_level(self, overall_alignment: float) -> AlignmentLevel:
        """Determine alignment level from score"""
        if overall_alignment >= 0.9:
            return AlignmentLevel.PERFECT
        elif overall_alignment >= 0.7:
            return AlignmentLevel.STRONG
        elif overall_alignment >= 0.5:
            return AlignmentLevel.MODERATE
        elif overall_alignment >= 0.3:
            return AlignmentLevel.WEAK
        else:
            return AlignmentLevel.MISALIGNED

    async def _identify_value_conflicts(
        self,
        item_description: str,
        value_scores: Dict[CoreValue, float],
        context: Optional[Dict[str, Any]],
    ) -> List[str]:
        """Identify conflicts between different values"""
        conflicts = []

        # Check for low-scoring critical values
        for value, score in value_scores.items():
            priority = self.value_profile.value_priorities.get(
                value, ValuePriority.MODERATE
            )
            if priority == ValuePriority.CRITICAL and score < 0.7:
                conflicts.append(
                    f"Critical value violation: {value.value} score too low ({score:.2f})"
                )

        # Check for specific value conflicts
        helpfulness_score = value_scores.get(CoreValue.HELPFULNESS, 0.5)
        privacy_score = value_scores.get(CoreValue.PRIVACY, 0.5)

        if helpfulness_score > 0.8 and privacy_score < 0.4:
            conflicts.append("Helpfulness vs Privacy conflict detected")

        transparency_score = value_scores.get(CoreValue.TRANSPARENCY, 0.5)

        if transparency_score > 0.8 and privacy_score < 0.4:
            conflicts.append("Transparency vs Privacy conflict detected")

        autonomy_score = value_scores.get(CoreValue.AUTONOMY, 0.5)

        if helpfulness_score > 0.8 and autonomy_score < 0.4:
            conflicts.append("Helpfulness vs Autonomy conflict detected")

        # Check for score variance indicating internal conflict
        score_values = list(value_scores.values())
        if score_values:
            score_range = max(score_values) - min(score_values)
            if score_range > 0.6:
                conflicts.append(
                    f"High value score variance detected ({score_range:.2f})"
                )

        return conflicts

    async def _generate_alignment_recommendations(
        self,
        item_description: str,
        value_scores: Dict[CoreValue, float],
        value_conflicts: List[str],
        alignment_level: AlignmentLevel,
    ) -> List[str]:
        """Generate recommendations to improve value alignment"""
        recommendations = []

        if alignment_level == AlignmentLevel.MISALIGNED:
            recommendations.append("Major value realignment required before proceeding")
            recommendations.append(
                "Consider alternative approaches that better align with core values"
            )

        elif alignment_level == AlignmentLevel.WEAK:
            recommendations.append(
                "Significant improvements needed to meet value standards"
            )

        # Specific value improvement recommendations
        for value, score in value_scores.items():
            if score < 0.5:
                recommendations.append(
                    f"Improve {value.value} alignment (current: {score:.2f})"
                )

        # Conflict resolution recommendations
        if "Helpfulness vs Privacy conflict detected" in value_conflicts:
            resolution = self.value_profile.conflict_resolution_rules.get(
                "helpfulness_vs_privacy", "Balance helpfulness with privacy protection"
            )
            recommendations.append(
                f"Resolve helpfulness-privacy conflict: {resolution}"
            )

        if "Transparency vs Privacy conflict detected" in value_conflicts:
            resolution = self.value_profile.conflict_resolution_rules.get(
                "transparency_vs_privacy",
                "Maintain transparency while protecting privacy",
            )
            recommendations.append(
                f"Resolve transparency-privacy conflict: {resolution}"
            )

        if "Helpfulness vs Autonomy conflict detected" in value_conflicts:
            resolution = self.value_profile.conflict_resolution_rules.get(
                "autonomy_vs_helpfulness",
                "Respect user autonomy while offering helpful guidance",
            )
            recommendations.append(
                f"Resolve helpfulness-autonomy conflict: {resolution}"
            )

        return recommendations

    async def _save_assessment_history(self):
        """Save assessment history to file"""
        history_file = self.data_dir / "assessment_history.json"
        try:
            # Convert to serializable format
            serializable_history = []
            for assessment in self.assessment_history:
                serializable_history.append(
                    {
                        "target_item": assessment.target_item,
                        "item_type": assessment.item_type,
                        "value_scores": {
                            k.value: v for k, v in assessment.value_scores.items()
                        },
                        "overall_alignment": assessment.overall_alignment,
                        "alignment_level": assessment.alignment_level.value,
                        "value_conflicts": assessment.value_conflicts,
                        "recommendations": assessment.recommendations,
                        "assessment_timestamp": assessment.assessment_timestamp,
                    }
                )

            with open(history_file, "w") as f:
                json.dump(serializable_history, f, indent=2)

        except Exception as e:
            print(f"   ⚠️ Error saving assessment history: {e}")

    async def get_value_alignment_statistics(self) -> Dict[str, Any]:
        """Get comprehensive value alignment statistics"""
        stats = {
            "total_assessments": len(self.assessment_history),
            "alignment_distribution": {},
            "average_alignment": 0.0,
            "value_performance": {},
            "conflict_frequency": {},
            "improvement_trends": {},
        }

        if self.assessment_history:
            # Alignment level distribution
            for assessment in self.assessment_history:
                level = assessment.alignment_level.value
                stats["alignment_distribution"][level] = (
                    stats["alignment_distribution"].get(level, 0) + 1
                )

            # Average alignment
            stats["average_alignment"] = sum(
                assessment.overall_alignment for assessment in self.assessment_history
            ) / len(self.assessment_history)

            # Value performance
            for value in CoreValue:
                scores = [
                    assessment.value_scores.get(value, 0.0)
                    for assessment in self.assessment_history
                ]
                stats["value_performance"][value.value] = {
                    "average_score": sum(scores) / len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores),
                }

            # Conflict frequency
            all_conflicts = []
            for assessment in self.assessment_history:
                all_conflicts.extend(assessment.value_conflicts)

            for conflict in all_conflicts:
                conflict_type = conflict.split(":")[0] if ":" in conflict else conflict
                stats["conflict_frequency"][conflict_type] = (
                    stats["conflict_frequency"].get(conflict_type, 0) + 1
                )

        return stats


# Example usage and testing
async def demo_value_alignment():
    """Demonstrate value alignment capabilities"""
    print("🎯 VALUE ALIGNMENT ENGINE DEMONSTRATION")
    print("=" * 60)

    engine = ValueAlignmentEngine()

    # Test cases
    test_cases = [
        {
            "description": "Share user conversation data to improve service quality",
            "type": "action",
            "context": {
                "user_consent": False,
                "user_benefit": True,
                "data_protection": False,
                "service_improvement": True,
            },
        },
        {
            "description": "Provide personalized learning recommendations based on user progress",
            "type": "goal",
            "context": {
                "user_consent": True,
                "learning_opportunity": True,
                "equal_treatment": True,
                "process_transparency": True,
            },
        },
        {
            "description": "Automatically optimize user settings without notification",
            "type": "decision",
            "context": {
                "user_control": False,
                "user_benefit": True,
                "process_transparency": False,
            },
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['type'].title()}")

        assessment = await engine.assess_value_alignment(
            test_case["description"], test_case["type"], test_case["context"]
        )

        print(
            f"   📊 Overall Alignment: {assessment.overall_alignment:.2f} ({assessment.alignment_level.value.upper()})"
        )
        print(f"   🎯 Top Values:")

        # Show top 3 values
        sorted_values = sorted(
            assessment.value_scores.items(), key=lambda x: x[1], reverse=True
        )
        for value, score in sorted_values[:3]:
            print(f"      • {value.value}: {score:.2f}")

        if assessment.value_conflicts:
            print(f"   ⚠️ Conflicts: {len(assessment.value_conflicts)}")
            for conflict in assessment.value_conflicts[:2]:
                print(f"      • {conflict}")

        if assessment.recommendations:
            print(f"   💡 Top Recommendation: {assessment.recommendations[0]}")

    # Show statistics
    stats = await engine.get_value_alignment_statistics()
    print(f"\n📈 Value Alignment Statistics:")
    print(f"   • Total assessments: {stats['total_assessments']}")
    print(f"   • Average alignment: {stats['average_alignment']:.2f}")
    print(f"   • Alignment distribution: {stats['alignment_distribution']}")


if __name__ == "__main__":
    asyncio.run(demo_value_alignment())
