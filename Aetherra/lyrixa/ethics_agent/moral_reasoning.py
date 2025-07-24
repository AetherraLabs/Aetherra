#!/usr/bin/env python3
"""
🧭 MORAL REASONING ENGINE - Ethical Decision Making System
==========================================================

Evaluates goals, actions, and decisions against internalized moral frameworks.
Provides ethical justification for decisions under uncertainty.

Key Features:
• Multi-framework ethical analysis (deontological, consequentialist, virtue ethics)
• Uncertainty-aware moral decision making
• Semantic rationale generation
• Value conflict resolution
• Ethical precedent tracking
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import validation and memory components
try:
    from ..memory.memory_core import LyrixaMemorySystem
    from ..reflection_engine.validation_engine import ChangeCategory, ValidationEngine
except ImportError:
    print("⚠️ Using local import paths for moral reasoning")
    import sys

    sys.path.append(".")


class EthicalFramework(Enum):
    """Ethical reasoning frameworks"""

    DEONTOLOGICAL = "deontological"  # Rule-based ethics (duty, rights)
    CONSEQUENTIALIST = "consequentialist"  # Outcome-based ethics (utility)
    VIRTUE_ETHICS = "virtue_ethics"  # Character-based ethics (virtues)
    CARE_ETHICS = "care_ethics"  # Relationship-based ethics (care, empathy)


class MoralDecision(Enum):
    """Possible moral decisions"""

    ALLOW = "allow"
    REJECT = "reject"
    MODIFY = "modify"
    DEFER = "defer"  # Requires human judgment


class EthicalPrinciple(Enum):
    """Core ethical principles"""

    AUTONOMY = "autonomy"  # Respect for individual freedom
    BENEFICENCE = "beneficence"  # Do good
    NON_MALEFICENCE = "non_maleficence"  # Do no harm
    JUSTICE = "justice"  # Fairness and equality
    TRANSPARENCY = "transparency"  # Openness and honesty
    PRIVACY = "privacy"  # Respect for personal information
    DIGNITY = "dignity"  # Human worth and respect


@dataclass
class EthicalEvaluation:
    """Result of ethical evaluation"""

    decision: MoralDecision
    confidence: float
    explanation: str
    framework_scores: Dict[EthicalFramework, float]
    principle_scores: Dict[EthicalPrinciple, float]
    conflicts_identified: List[str]
    recommendations: List[str]
    precedent_citations: List[str]
    evaluation_timestamp: str


@dataclass
class MoralContext:
    """Context for moral reasoning"""

    action_type: str
    description: str
    stakeholders: List[str]
    potential_outcomes: List[str]
    constraints: Dict[str, Any]
    urgency_level: str = "normal"
    precedent_cases: Optional[List[str]] = None


class MoralReasoningEngine:
    """
    Comprehensive ethical decision making system
    """

    def __init__(self, data_dir: str = "ethics_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Core ethical principles and their weights
        self.core_principles = {
            EthicalPrinciple.NON_MALEFICENCE: 0.95,  # Highest priority - do no harm
            EthicalPrinciple.AUTONOMY: 0.9,  # Respect individual freedom
            EthicalPrinciple.TRANSPARENCY: 0.85,  # Be honest and open
            EthicalPrinciple.PRIVACY: 0.85,  # Protect personal information
            EthicalPrinciple.JUSTICE: 0.8,  # Ensure fairness
            EthicalPrinciple.BENEFICENCE: 0.75,  # Do good when possible
            EthicalPrinciple.DIGNITY: 0.9,  # Respect human worth
        }

        # Ethical framework preferences
        self.framework_weights = {
            EthicalFramework.DEONTOLOGICAL: 0.8,  # Strong rule-based ethics
            EthicalFramework.CONSEQUENTIALIST: 0.7,  # Consider outcomes
            EthicalFramework.VIRTUE_ETHICS: 0.6,  # Character considerations
            EthicalFramework.CARE_ETHICS: 0.65,  # Relationship impact
        }

        # Evaluation history
        self.evaluation_history: List[EthicalEvaluation] = []
        self.precedent_database: Dict[str, List[EthicalEvaluation]] = {}

        # Load existing precedents
        self._load_precedent_database()

        print(
            "🧭 MoralReasoningEngine initialized with comprehensive ethical frameworks"
        )

    def _load_precedent_database(self):
        """Load existing ethical precedents"""
        precedent_file = self.data_dir / "precedent_database.json"
        if precedent_file.exists():
            try:
                with open(precedent_file, "r") as f:
                    precedent_data = json.load(f)
                    # Convert loaded data back to precedent database structure
                    for category, cases in precedent_data.items():
                        self.precedent_database[category] = []
                        for case in cases:
                            # Reconstruct EthicalEvaluation objects from stored data
                            evaluation = EthicalEvaluation(
                                decision=MoralDecision(case["decision"]),
                                confidence=case["confidence"],
                                explanation=case["explanation"],
                                framework_scores={
                                    EthicalFramework(k): v
                                    for k, v in case["framework_scores"].items()
                                },
                                principle_scores={
                                    EthicalPrinciple(k): v
                                    for k, v in case["principle_scores"].items()
                                },
                                conflicts_identified=case["conflicts_identified"],
                                recommendations=case["recommendations"],
                                precedent_citations=case["precedent_citations"],
                                evaluation_timestamp=case["evaluation_timestamp"],
                            )
                            self.precedent_database[category].append(evaluation)
                print(
                    f"   📚 Loaded {len(self.precedent_database)} precedent categories"
                )
            except Exception as e:
                print(f"   ⚠️ Error loading precedents: {e}")

    async def evaluate_moral_decision(
        self, context: MoralContext, category: Optional[str] = None
    ) -> EthicalEvaluation:
        """
        Comprehensive moral evaluation of an action or decision
        """
        print(f"🧭 Evaluating moral decision: {context.action_type}")
        print(f"   • Description: {context.description}")
        print(f"   • Stakeholders: {len(context.stakeholders)}")

        # Analyze under each ethical framework
        framework_scores = {}
        for framework in EthicalFramework:
            score = await self._evaluate_under_framework(context, framework)
            framework_scores[framework] = score

        # Evaluate against core principles
        principle_scores = {}
        for principle in EthicalPrinciple:
            score = await self._evaluate_principle_alignment(context, principle)
            principle_scores[principle] = score

        # Identify ethical conflicts
        conflicts = await self._identify_ethical_conflicts(
            context, framework_scores, principle_scores
        )

        # Find relevant precedents
        precedent_citations = await self._find_relevant_precedents(context, category)

        # Make final moral decision
        decision, confidence = await self._make_moral_decision(
            context, framework_scores, principle_scores, conflicts
        )

        # Generate semantic explanation
        explanation = await self._generate_moral_explanation(
            context, decision, framework_scores, principle_scores, conflicts
        )

        # Generate recommendations
        recommendations = await self._generate_moral_recommendations(
            context, decision, conflicts, principle_scores
        )

        # Create evaluation result
        evaluation = EthicalEvaluation(
            decision=decision,
            confidence=confidence,
            explanation=explanation,
            framework_scores=framework_scores,
            principle_scores=principle_scores,
            conflicts_identified=conflicts,
            recommendations=recommendations,
            precedent_citations=precedent_citations,
            evaluation_timestamp=datetime.now().isoformat(),
        )

        # Store evaluation
        self.evaluation_history.append(evaluation)
        await self._store_precedent(evaluation, category or context.action_type)

        print(
            f"   📊 Decision: {decision.value.upper()} (confidence: {confidence:.2f})"
        )
        print(f"   🧠 Explanation: {explanation[:100]}...")

        return evaluation

    async def _evaluate_under_framework(
        self, context: MoralContext, framework: EthicalFramework
    ) -> float:
        """Evaluate action under specific ethical framework"""

        if framework == EthicalFramework.DEONTOLOGICAL:
            # Rule-based ethics - focus on duties and rights
            return await self._deontological_evaluation(context)

        elif framework == EthicalFramework.CONSEQUENTIALIST:
            # Outcome-based ethics - focus on consequences
            return await self._consequentialist_evaluation(context)

        elif framework == EthicalFramework.VIRTUE_ETHICS:
            # Character-based ethics - focus on virtues
            return await self._virtue_ethics_evaluation(context)

        elif framework == EthicalFramework.CARE_ETHICS:
            # Relationship-based ethics - focus on care and empathy
            return await self._care_ethics_evaluation(context)

        return 0.5  # Neutral if framework not recognized

    async def _deontological_evaluation(self, context: MoralContext) -> float:
        """Evaluate using deontological (rule-based) ethics"""
        score = 0.8  # Base score for rule compliance

        # Check for duty violations
        if any("harm" in outcome.lower() for outcome in context.potential_outcomes):
            score -= 0.3

        # Check for rights violations
        if any(
            "privacy" in constraint.lower() for constraint in context.constraints.keys()
        ):
            if context.constraints.get("privacy_protected", True):
                score += 0.1
            else:
                score -= 0.4

        # Check for autonomy respect
        if "user_consent" in context.constraints:
            if context.constraints["user_consent"]:
                score += 0.2
            else:
                score -= 0.5

        return max(0.0, min(1.0, score))

    async def _consequentialist_evaluation(self, context: MoralContext) -> float:
        """Evaluate using consequentialist (outcome-based) ethics"""
        score = 0.6  # Base score

        # Analyze potential outcomes
        positive_outcomes = len(
            [
                outcome
                for outcome in context.potential_outcomes
                if any(
                    word in outcome.lower()
                    for word in ["benefit", "improve", "help", "good"]
                )
            ]
        )

        negative_outcomes = len(
            [
                outcome
                for outcome in context.potential_outcomes
                if any(
                    word in outcome.lower()
                    for word in ["harm", "damage", "hurt", "bad"]
                )
            ]
        )

        total_outcomes = len(context.potential_outcomes)
        if total_outcomes > 0:
            outcome_ratio = (positive_outcomes - negative_outcomes) / total_outcomes
            score += outcome_ratio * 0.4

        # Consider stakeholder impact
        if len(context.stakeholders) > 0:
            # More stakeholders = need higher benefit threshold
            stakeholder_adjustment = min(0.2, len(context.stakeholders) * 0.05)
            score -= stakeholder_adjustment

        return max(0.0, min(1.0, score))

    async def _virtue_ethics_evaluation(self, context: MoralContext) -> float:
        """Evaluate using virtue ethics (character-based)"""
        score = 0.7  # Base score for virtue alignment

        # Check for virtuous intentions
        virtuous_keywords = ["honest", "fair", "compassionate", "wise", "courageous"]
        if any(keyword in context.description.lower() for keyword in virtuous_keywords):
            score += 0.2

        # Check for vicious tendencies
        vicious_keywords = ["deceptive", "unfair", "cruel", "reckless"]
        if any(keyword in context.description.lower() for keyword in vicious_keywords):
            score -= 0.4

        # Consider character development aspect
        if (
            "learning" in context.description.lower()
            or "growth" in context.description.lower()
        ):
            score += 0.1

        return max(0.0, min(1.0, score))

    async def _care_ethics_evaluation(self, context: MoralContext) -> float:
        """Evaluate using care ethics (relationship-based)"""
        score = 0.6  # Base score

        # Consider relationship impact
        if "user" in context.stakeholders or "human" in context.stakeholders:
            score += 0.2

        # Check for care and empathy
        care_keywords = ["support", "help", "understand", "empathy", "care"]
        if any(keyword in context.description.lower() for keyword in care_keywords):
            score += 0.2

        # Penalize actions that damage relationships
        if any("conflict" in outcome.lower() for outcome in context.potential_outcomes):
            score -= 0.3

        return max(0.0, min(1.0, score))

    async def _evaluate_principle_alignment(
        self, context: MoralContext, principle: EthicalPrinciple
    ) -> float:
        """Evaluate alignment with specific ethical principle"""

        if principle == EthicalPrinciple.NON_MALEFICENCE:
            # Do no harm
            harm_indicators = sum(
                1
                for outcome in context.potential_outcomes
                if "harm" in outcome.lower() or "damage" in outcome.lower()
            )
            return max(0.0, 1.0 - (harm_indicators * 0.3))

        elif principle == EthicalPrinciple.AUTONOMY:
            # Respect individual freedom
            consent = context.constraints.get("user_consent", True)
            return 0.9 if consent else 0.3

        elif principle == EthicalPrinciple.TRANSPARENCY:
            # Openness and honesty
            transparency = context.constraints.get("transparent_process", True)
            return 0.85 if transparency else 0.4

        elif principle == EthicalPrinciple.PRIVACY:
            # Protect personal information
            privacy_protected = context.constraints.get("privacy_protected", True)
            return 0.9 if privacy_protected else 0.2

        elif principle == EthicalPrinciple.JUSTICE:
            # Fairness and equality
            fair_treatment = context.constraints.get("fair_treatment", True)
            return 0.8 if fair_treatment else 0.3

        elif principle == EthicalPrinciple.BENEFICENCE:
            # Do good
            benefit_count = sum(
                1
                for outcome in context.potential_outcomes
                if "benefit" in outcome.lower() or "improve" in outcome.lower()
            )
            return min(1.0, 0.5 + (benefit_count * 0.2))

        elif principle == EthicalPrinciple.DIGNITY:
            # Human worth and respect
            dignity_preserved = context.constraints.get("dignity_preserved", True)
            return 0.9 if dignity_preserved else 0.3

        return 0.7  # Default moderate alignment

    async def _identify_ethical_conflicts(
        self,
        context: MoralContext,
        framework_scores: Dict[EthicalFramework, float],
        principle_scores: Dict[EthicalPrinciple, float],
    ) -> List[str]:
        """Identify conflicts between ethical frameworks or principles"""
        conflicts = []

        # Check for framework conflicts
        max_framework_score = max(framework_scores.values())
        min_framework_score = min(framework_scores.values())

        if max_framework_score - min_framework_score > 0.4:
            conflicts.append(
                f"Framework conflict: {max_framework_score:.2f} vs {min_framework_score:.2f} score difference"
            )

        # Check for principle conflicts
        low_scoring_principles = [
            principle.value
            for principle, score in principle_scores.items()
            if score < 0.5
        ]

        if low_scoring_principles:
            conflicts.append(
                f"Principle violations: {', '.join(low_scoring_principles)}"
            )

        # Check for specific conflicts
        if (
            principle_scores[EthicalPrinciple.TRANSPARENCY] > 0.8
            and principle_scores[EthicalPrinciple.PRIVACY] < 0.3
        ):
            conflicts.append("Transparency vs Privacy conflict")

        if (
            principle_scores[EthicalPrinciple.BENEFICENCE] > 0.8
            and principle_scores[EthicalPrinciple.AUTONOMY] < 0.3
        ):
            conflicts.append("Beneficence vs Autonomy conflict")

        return conflicts

    async def _make_moral_decision(
        self,
        context: MoralContext,
        framework_scores: Dict[EthicalFramework, float],
        principle_scores: Dict[EthicalPrinciple, float],
        conflicts: List[str],
    ) -> Tuple[MoralDecision, float]:
        """Make final moral decision based on all evaluations"""

        # Calculate weighted framework score
        framework_score = sum(
            score * self.framework_weights[framework]
            for framework, score in framework_scores.items()
        ) / sum(self.framework_weights.values())

        # Calculate weighted principle score
        principle_score = sum(
            score * self.core_principles[principle]
            for principle, score in principle_scores.items()
        ) / sum(self.core_principles.values())

        # Combined ethical score
        combined_score = (framework_score + principle_score) / 2

        # Apply conflict penalties
        conflict_penalty = len(conflicts) * 0.1
        final_score = max(0.0, combined_score - conflict_penalty)

        # Decision thresholds
        if final_score >= 0.8:
            return MoralDecision.ALLOW, final_score
        elif final_score >= 0.6:
            return MoralDecision.MODIFY, final_score
        elif final_score >= 0.3:
            return MoralDecision.DEFER, final_score
        else:
            return MoralDecision.REJECT, final_score

    async def _generate_moral_explanation(
        self,
        context: MoralContext,
        decision: MoralDecision,
        framework_scores: Dict[EthicalFramework, float],
        principle_scores: Dict[EthicalPrinciple, float],
        conflicts: List[str],
    ) -> str:
        """Generate semantic explanation for moral decision"""

        explanation_parts = []

        # Decision rationale
        if decision == MoralDecision.ALLOW:
            explanation_parts.append(
                f"The proposed action '{context.action_type}' is ethically permissible."
            )
        elif decision == MoralDecision.MODIFY:
            explanation_parts.append(
                f"The proposed action '{context.action_type}' requires ethical modifications."
            )
        elif decision == MoralDecision.DEFER:
            explanation_parts.append(
                f"The proposed action '{context.action_type}' requires human ethical review."
            )
        else:  # REJECT
            explanation_parts.append(
                f"The proposed action '{context.action_type}' is not ethically acceptable."
            )

        # Framework analysis
        best_framework = max(framework_scores.items(), key=lambda x: x[1])
        worst_framework = min(framework_scores.items(), key=lambda x: x[1])

        explanation_parts.append(
            f"From a {best_framework[0].value} perspective, this action scores {best_framework[1]:.2f}. "
            f"However, {worst_framework[0].value} analysis yields {worst_framework[1]:.2f}."
        )

        # Principle analysis
        strong_principles = [
            principle.value
            for principle, score in principle_scores.items()
            if score > 0.8
        ]
        weak_principles = [
            principle.value
            for principle, score in principle_scores.items()
            if score < 0.5
        ]

        if strong_principles:
            explanation_parts.append(
                f"The action strongly aligns with: {', '.join(strong_principles)}."
            )

        if weak_principles:
            explanation_parts.append(
                f"Concerns exist regarding: {', '.join(weak_principles)}."
            )

        # Conflict explanation
        if conflicts:
            explanation_parts.append(
                f"Ethical tensions identified: {'; '.join(conflicts)}."
            )

        return " ".join(explanation_parts)

    async def _generate_moral_recommendations(
        self,
        context: MoralContext,
        decision: MoralDecision,
        conflicts: List[str],
        principle_scores: Dict[EthicalPrinciple, float],
    ) -> List[str]:
        """Generate actionable moral recommendations"""
        recommendations = []

        if decision == MoralDecision.MODIFY:
            recommendations.append("Implement ethical safeguards before proceeding")

            # Specific principle-based recommendations
            if principle_scores[EthicalPrinciple.TRANSPARENCY] < 0.6:
                recommendations.append("Increase transparency of decision process")

            if principle_scores[EthicalPrinciple.PRIVACY] < 0.6:
                recommendations.append("Strengthen privacy protection measures")

            if principle_scores[EthicalPrinciple.AUTONOMY] < 0.6:
                recommendations.append("Ensure user consent and autonomy preservation")

        elif decision == MoralDecision.DEFER:
            recommendations.append("Seek human ethical review before implementation")
            recommendations.append("Document ethical concerns for review committee")

        elif decision == MoralDecision.REJECT:
            recommendations.append("Redesign approach to address ethical violations")
            recommendations.append(
                "Consider alternative methods that align with moral principles"
            )

        # Conflict-specific recommendations
        if "Transparency vs Privacy conflict" in conflicts:
            recommendations.append(
                "Balance transparency with privacy through selective disclosure"
            )

        if "Beneficence vs Autonomy conflict" in conflicts:
            recommendations.append(
                "Prioritize user choice while providing beneficial guidance"
            )

        return recommendations

    async def _find_relevant_precedents(
        self, context: MoralContext, category: Optional[str] = None
    ) -> List[str]:
        """Find relevant ethical precedents from past decisions"""
        precedents = []

        search_category = category or context.action_type
        if search_category in self.precedent_database:
            # Find similar cases
            for precedent in self.precedent_database[search_category][
                -5:
            ]:  # Last 5 cases
                similarity_score = await self._calculate_precedent_similarity(
                    context, precedent
                )
                if similarity_score > 0.6:
                    precedents.append(
                        f"Similar case ({precedent.evaluation_timestamp[:10]}): "
                        f"{precedent.decision.value} - {precedent.explanation[:100]}..."
                    )

        return precedents

    async def _calculate_precedent_similarity(
        self, current_context: MoralContext, precedent: EthicalEvaluation
    ) -> float:
        """Calculate similarity between current context and precedent"""
        # Simplified similarity calculation
        # In full implementation, would use semantic similarity
        return 0.7  # Placeholder similarity score

    async def _store_precedent(self, evaluation: EthicalEvaluation, category: str):
        """Store evaluation as precedent for future reference"""
        if category not in self.precedent_database:
            self.precedent_database[category] = []

        self.precedent_database[category].append(evaluation)

        # Keep only recent precedents (last 50 per category)
        if len(self.precedent_database[category]) > 50:
            self.precedent_database[category] = self.precedent_database[category][-50:]

        # Save to file
        await self._save_precedent_database()

    async def _save_precedent_database(self):
        """Save precedent database to file"""
        precedent_file = self.data_dir / "precedent_database.json"
        try:
            # Convert precedent database to serializable format
            serializable_db = {}
            for category, evaluations in self.precedent_database.items():
                serializable_db[category] = []
                for eval in evaluations:
                    serializable_db[category].append(
                        {
                            "decision": eval.decision.value,
                            "confidence": eval.confidence,
                            "explanation": eval.explanation,
                            "framework_scores": {
                                k.value: v for k, v in eval.framework_scores.items()
                            },
                            "principle_scores": {
                                k.value: v for k, v in eval.principle_scores.items()
                            },
                            "conflicts_identified": eval.conflicts_identified,
                            "recommendations": eval.recommendations,
                            "precedent_citations": eval.precedent_citations,
                            "evaluation_timestamp": eval.evaluation_timestamp,
                        }
                    )

            with open(precedent_file, "w") as f:
                json.dump(serializable_db, f, indent=2)
        except Exception as e:
            print(f"   ⚠️ Error saving precedents: {e}")

    async def get_ethical_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ethical decision statistics"""
        stats = {
            "total_evaluations": len(self.evaluation_history),
            "decision_distribution": {},
            "average_confidence": 0.0,
            "framework_performance": {},
            "principle_compliance": {},
            "conflict_frequency": 0.0,
        }

        if self.evaluation_history:
            # Decision distribution
            for eval in self.evaluation_history:
                decision = eval.decision.value
                stats["decision_distribution"][decision] = (
                    stats["decision_distribution"].get(decision, 0) + 1
                )

            # Average confidence
            stats["average_confidence"] = sum(
                eval.confidence for eval in self.evaluation_history
            ) / len(self.evaluation_history)

            # Framework performance
            for framework in EthicalFramework:
                scores = [
                    eval.framework_scores.get(framework, 0.0)
                    for eval in self.evaluation_history
                ]
                stats["framework_performance"][framework.value] = sum(scores) / len(
                    scores
                )

            # Principle compliance
            for principle in EthicalPrinciple:
                scores = [
                    eval.principle_scores.get(principle, 0.0)
                    for eval in self.evaluation_history
                ]
                stats["principle_compliance"][principle.value] = sum(scores) / len(
                    scores
                )

            # Conflict frequency
            total_conflicts = sum(
                len(eval.conflicts_identified) for eval in self.evaluation_history
            )
            stats["conflict_frequency"] = total_conflicts / len(self.evaluation_history)

        return stats


# Example usage and testing
async def demo_moral_reasoning():
    """Demonstrate moral reasoning capabilities"""
    print("🧭 MORAL REASONING ENGINE DEMONSTRATION")
    print("=" * 60)

    engine = MoralReasoningEngine()

    # Test case 1: Memory sharing decision
    context1 = MoralContext(
        action_type="memory_sharing",
        description="Share user conversation patterns to improve service quality",
        stakeholders=["user", "service_improvement", "privacy_advocates"],
        potential_outcomes=[
            "Improved personalized responses",
            "Better user experience",
            "Potential privacy concerns",
            "Possible data misuse",
        ],
        constraints={
            "user_consent": False,
            "privacy_protected": False,
            "transparent_process": True,
            "fair_treatment": True,
        },
    )

    evaluation1 = await engine.evaluate_moral_decision(context1, "data_handling")
    print(f"\n📊 Memory Sharing Evaluation:")
    print(f"   • Decision: {evaluation1.decision.value.upper()}")
    print(f"   • Confidence: {evaluation1.confidence:.2f}")
    print(f"   • Explanation: {evaluation1.explanation}")

    # Test case 2: Learning optimization decision
    context2 = MoralContext(
        action_type="learning_optimization",
        description="Modify learning algorithm to accelerate skill acquisition",
        stakeholders=["user", "learning_effectiveness"],
        potential_outcomes=[
            "Faster learning progress",
            "Improved skill development",
            "Reduced cognitive load",
        ],
        constraints={
            "user_consent": True,
            "privacy_protected": True,
            "transparent_process": True,
            "dignity_preserved": True,
        },
    )

    evaluation2 = await engine.evaluate_moral_decision(context2, "system_optimization")
    print(f"\n📊 Learning Optimization Evaluation:")
    print(f"   • Decision: {evaluation2.decision.value.upper()}")
    print(f"   • Confidence: {evaluation2.confidence:.2f}")
    print(f"   • Recommendations: {len(evaluation2.recommendations)}")

    # Show statistics
    stats = await engine.get_ethical_statistics()
    print(f"\n📈 Ethical Decision Statistics:")
    print(f"   • Total evaluations: {stats['total_evaluations']}")
    print(f"   • Average confidence: {stats['average_confidence']:.2f}")
    print(f"   • Decision distribution: {stats['decision_distribution']}")


if __name__ == "__main__":
    asyncio.run(demo_moral_reasoning())
