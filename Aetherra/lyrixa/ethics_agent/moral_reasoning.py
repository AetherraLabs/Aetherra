"""
🧠 Moral Reasoning Engine
=========================

Advanced moral reasoning capabilities for ethical decision-making
in the Aetherra AI OS.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class MoralFramework(Enum):
    """Different moral reasoning frameworks."""

    UTILITARIAN = "utilitarian"
    DEONTOLOGICAL = "deontological"
    VIRTUE_ETHICS = "virtue_ethics"
    CARE_ETHICS = "care_ethics"
    PRINCIPLISM = "principlism"


@dataclass
class MoralDilemma:
    """Represents a moral dilemma for analysis."""

    id: str
    description: str
    stakeholders: List[str]
    potential_actions: List[str]
    consequences: Dict[str, List[str]]
    context: Dict[str, Any]
    timestamp: datetime


class MoralReasoningEngine:
    """
    Engine for moral reasoning and ethical decision-making.

    Provides:
    - Multi-framework moral analysis
    - Stakeholder impact assessment
    - Ethical decision recommendations
    - Moral conflict resolution
    """

    def __init__(self):
        """Initialize the moral reasoning engine."""
        self.moral_principles = self._initialize_moral_principles()
        self.ethical_frameworks = self._initialize_frameworks()
        self.moral_history = []
        self.stakeholder_weights = {}

    def analyze_moral_dilemma(self, dilemma: MoralDilemma) -> Dict[str, Any]:
        """
        Analyze a moral dilemma using multiple ethical frameworks.

        Args:
            dilemma: The moral dilemma to analyze

        Returns:
            Comprehensive moral analysis
        """
        analysis = {
            "dilemma_id": dilemma.id,
            "framework_analyses": {},
            "stakeholder_impact": {},
            "recommended_action": None,
            "confidence": 0.0,
            "moral_reasoning": [],
        }

        # Analyze using each framework
        for framework in MoralFramework:
            framework_result = self._apply_framework(dilemma, framework)
            analysis["framework_analyses"][framework.value] = framework_result

        # Assess stakeholder impacts
        analysis["stakeholder_impact"] = self._assess_stakeholder_impact(dilemma)

        # Generate recommendation
        recommendation = self._generate_recommendation(analysis, dilemma)
        analysis.update(recommendation)

        # Store in history
        self._record_moral_analysis(dilemma, analysis)

        return analysis

    def evaluate_action_ethics(
        self, action: str, context: Dict[str, Any], affected_parties: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the ethics of a proposed action.

        Args:
            action: Action to evaluate
            context: Situational context
            affected_parties: List of affected stakeholders

        Returns:
            Ethical evaluation result
        """
        evaluation = {
            "action": action,
            "ethical_score": 0.0,
            "framework_scores": {},
            "ethical_concerns": [],
            "positive_aspects": [],
            "recommendations": [],
        }

        # Create a simple dilemma for analysis
        dilemma = MoralDilemma(
            id=f"eval_{hash(action)}",
            description=f"Evaluation of action: {action}",
            stakeholders=affected_parties or ["user", "system"],
            potential_actions=[action, "no_action"],
            consequences={action: ["unknown"], "no_action": ["status_quo"]},
            context=context,
            timestamp=datetime.now(),
        )

        # Analyze using frameworks
        for framework in MoralFramework:
            score = self._score_action_by_framework(action, context, framework)
            evaluation["framework_scores"][framework.value] = score

        # Calculate overall ethical score
        evaluation["ethical_score"] = sum(
            evaluation["framework_scores"].values()
        ) / len(MoralFramework)

        # Generate concerns and recommendations
        evaluation["ethical_concerns"] = self._identify_ethical_concerns(
            action, context
        )
        evaluation["positive_aspects"] = self._identify_positive_aspects(
            action, context
        )
        evaluation["recommendations"] = self._generate_ethical_recommendations(
            evaluation
        )

        return evaluation

    def resolve_moral_conflict(
        self, conflicting_values: List[str], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve conflicts between moral values.

        Args:
            conflicting_values: List of conflicting moral values
            context: Situational context

        Returns:
            Conflict resolution strategy
        """
        resolution = {
            "conflict_type": "value_conflict",
            "conflicting_values": conflicting_values,
            "resolution_strategy": None,
            "compromise_solution": None,
            "priority_ranking": [],
            "justification": "",
        }

        # Analyze value conflicts
        value_analysis = self._analyze_value_conflicts(conflicting_values, context)

        # Determine resolution strategy
        if len(conflicting_values) == 2:
            resolution["resolution_strategy"] = "binary_choice"
            resolution["compromise_solution"] = self._find_compromise(
                conflicting_values, context
            )
        else:
            resolution["resolution_strategy"] = "multi_value_balancing"
            resolution["priority_ranking"] = self._rank_values_by_importance(
                conflicting_values, context
            )

        resolution["justification"] = self._generate_resolution_justification(
            resolution, context
        )

        return resolution

    def get_moral_guidance(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide moral guidance for a given situation.

        Args:
            situation: Description of the situation

        Returns:
            Moral guidance and recommendations
        """
        guidance = {
            "situation_type": self._classify_situation(situation),
            "applicable_principles": [],
            "moral_considerations": [],
            "recommended_approach": "",
            "potential_pitfalls": [],
            "ethical_best_practices": [],
        }

        # Identify applicable moral principles
        guidance["applicable_principles"] = self._identify_applicable_principles(
            situation
        )

        # Generate moral considerations
        guidance["moral_considerations"] = self._generate_moral_considerations(
            situation
        )

        # Recommend approach
        guidance["recommended_approach"] = self._recommend_moral_approach(
            situation, guidance
        )

        # Identify potential pitfalls
        guidance["potential_pitfalls"] = self._identify_moral_pitfalls(situation)

        # Provide best practices
        guidance["ethical_best_practices"] = self._get_ethical_best_practices(situation)

        return guidance

    def _initialize_moral_principles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize core moral principles."""
        return {
            "autonomy": {
                "description": "Respect for individual autonomy and self-determination",
                "weight": 0.9,
                "applications": ["consent", "choice", "freedom"],
            },
            "beneficence": {
                "description": "Acting in ways that benefit others",
                "weight": 0.8,
                "applications": ["helping", "promoting_welfare", "positive_outcomes"],
            },
            "non_maleficence": {
                "description": "Do no harm",
                "weight": 0.95,
                "applications": ["avoiding_harm", "preventing_damage", "safety"],
            },
            "justice": {
                "description": "Fair treatment and distribution of benefits/burdens",
                "weight": 0.85,
                "applications": ["fairness", "equality", "rights"],
            },
            "veracity": {
                "description": "Truth-telling and honesty",
                "weight": 0.8,
                "applications": ["honesty", "transparency", "accuracy"],
            },
            "fidelity": {
                "description": "Keeping promises and commitments",
                "weight": 0.75,
                "applications": ["promise_keeping", "loyalty", "reliability"],
            },
        }

    def _initialize_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize ethical reasoning frameworks."""
        return {
            "utilitarian": {
                "focus": "consequences",
                "principle": "greatest good for greatest number",
                "decision_criteria": "maximize overall utility",
            },
            "deontological": {
                "focus": "duties and rules",
                "principle": "categorical imperatives",
                "decision_criteria": "follow moral rules regardless of consequences",
            },
            "virtue_ethics": {
                "focus": "character traits",
                "principle": "act according to virtues",
                "decision_criteria": "what would a virtuous person do",
            },
            "care_ethics": {
                "focus": "relationships and care",
                "principle": "maintain caring relationships",
                "decision_criteria": "preserve relationships and care for others",
            },
            "principlism": {
                "focus": "moral principles",
                "principle": "balance competing principles",
                "decision_criteria": "weigh and balance moral principles",
            },
        }

    def _apply_framework(
        self, dilemma: MoralDilemma, framework: MoralFramework
    ) -> Dict[str, Any]:
        """Apply a specific ethical framework to analyze a dilemma."""
        framework_analysis = {
            "framework": framework.value,
            "recommended_action": None,
            "reasoning": "",
            "strength": 0.0,
        }

        if framework == MoralFramework.UTILITARIAN:
            framework_analysis = self._utilitarian_analysis(dilemma)
        elif framework == MoralFramework.DEONTOLOGICAL:
            framework_analysis = self._deontological_analysis(dilemma)
        elif framework == MoralFramework.VIRTUE_ETHICS:
            framework_analysis = self._virtue_ethics_analysis(dilemma)
        elif framework == MoralFramework.CARE_ETHICS:
            framework_analysis = self._care_ethics_analysis(dilemma)
        elif framework == MoralFramework.PRINCIPLISM:
            framework_analysis = self._principlism_analysis(dilemma)

        return framework_analysis

    def _utilitarian_analysis(self, dilemma: MoralDilemma) -> Dict[str, Any]:
        """Perform utilitarian analysis."""
        action_utilities = {}

        for action in dilemma.potential_actions:
            total_utility = 0
            consequences = dilemma.consequences.get(action, [])

            for consequence in consequences:
                # Simple utility calculation (would be more sophisticated in practice)
                if "benefit" in consequence.lower():
                    total_utility += 1
                elif "harm" in consequence.lower():
                    total_utility -= 1

            action_utilities[action] = total_utility

        best_action = max(action_utilities, key=action_utilities.get)

        return {
            "framework": "utilitarian",
            "recommended_action": best_action,
            "reasoning": f"Action {best_action} maximizes overall utility",
            "strength": 0.8,
            "utility_scores": action_utilities,
        }

    def _deontological_analysis(self, dilemma: MoralDilemma) -> Dict[str, Any]:
        """Perform deontological analysis."""
        # Check actions against moral rules
        rule_violations = {}

        for action in dilemma.potential_actions:
            violations = 0

            # Check against basic moral rules
            if "lie" in action.lower() or "deceive" in action.lower():
                violations += 1
            if "harm" in action.lower():
                violations += 1
            if "break" in action.lower() and "promise" in action.lower():
                violations += 1

            rule_violations[action] = violations

        best_action = min(rule_violations, key=rule_violations.get)

        return {
            "framework": "deontological",
            "recommended_action": best_action,
            "reasoning": f"Action {best_action} violates fewest moral rules",
            "strength": 0.7,
            "rule_violations": rule_violations,
        }

    def _virtue_ethics_analysis(self, dilemma: MoralDilemma) -> Dict[str, Any]:
        """Perform virtue ethics analysis."""
        virtue_scores = {}
        virtues = ["courage", "honesty", "compassion", "justice", "temperance"]

        for action in dilemma.potential_actions:
            score = 0

            # Simple virtue scoring
            for virtue in virtues:
                if (
                    virtue in action.lower()
                    or virtue in str(dilemma.consequences.get(action, [])).lower()
                ):
                    score += 1

            virtue_scores[action] = score

        best_action = max(virtue_scores, key=virtue_scores.get)

        return {
            "framework": "virtue_ethics",
            "recommended_action": best_action,
            "reasoning": f"Action {best_action} best exemplifies virtuous character",
            "strength": 0.6,
            "virtue_scores": virtue_scores,
        }

    def _care_ethics_analysis(self, dilemma: MoralDilemma) -> Dict[str, Any]:
        """Perform care ethics analysis."""
        care_scores = {}

        for action in dilemma.potential_actions:
            score = 0

            # Score based on care and relationship preservation
            if "care" in action.lower() or "help" in action.lower():
                score += 2
            if "relationship" in action.lower() or "connect" in action.lower():
                score += 1
            if "harm" in action.lower() or "damage" in action.lower():
                score -= 2

            care_scores[action] = score

        best_action = max(care_scores, key=care_scores.get)

        return {
            "framework": "care_ethics",
            "recommended_action": best_action,
            "reasoning": f"Action {best_action} best preserves caring relationships",
            "strength": 0.7,
            "care_scores": care_scores,
        }

    def _principlism_analysis(self, dilemma: MoralDilemma) -> Dict[str, Any]:
        """Perform principlism analysis."""
        principle_scores = {}

        for action in dilemma.potential_actions:
            total_score = 0

            # Score against each principle
            for principle, data in self.moral_principles.items():
                principle_score = 0

                # Simple principle matching
                for application in data["applications"]:
                    if application in action.lower():
                        principle_score += data["weight"]

                total_score += principle_score

            principle_scores[action] = total_score

        best_action = max(principle_scores, key=principle_scores.get)

        return {
            "framework": "principlism",
            "recommended_action": best_action,
            "reasoning": f"Action {best_action} best balances moral principles",
            "strength": 0.8,
            "principle_scores": principle_scores,
        }

    def _assess_stakeholder_impact(
        self, dilemma: MoralDilemma
    ) -> Dict[str, Dict[str, Any]]:
        """Assess impact on each stakeholder."""
        stakeholder_analysis = {}

        for stakeholder in dilemma.stakeholders:
            stakeholder_analysis[stakeholder] = {
                "potential_benefits": [],
                "potential_harms": [],
                "rights_affected": [],
                "interests_impact": "neutral",
            }

            # Analyze each potential action's impact on this stakeholder
            for action in dilemma.potential_actions:
                consequences = dilemma.consequences.get(action, [])

                for consequence in consequences:
                    if "benefit" in consequence.lower():
                        stakeholder_analysis[stakeholder]["potential_benefits"].append(
                            consequence
                        )
                    elif "harm" in consequence.lower():
                        stakeholder_analysis[stakeholder]["potential_harms"].append(
                            consequence
                        )

        return stakeholder_analysis

    def _generate_recommendation(
        self, analysis: Dict[str, Any], dilemma: MoralDilemma
    ) -> Dict[str, Any]:
        """Generate final recommendation based on analysis."""
        framework_votes = {}

        # Count votes from each framework
        for framework_name, framework_analysis in analysis[
            "framework_analyses"
        ].items():
            recommended_action = framework_analysis.get("recommended_action")
            if recommended_action:
                if recommended_action not in framework_votes:
                    framework_votes[recommended_action] = 0
                framework_votes[recommended_action] += framework_analysis.get(
                    "strength", 0.5
                )

        # Determine consensus
        if framework_votes:
            best_action = max(framework_votes, key=framework_votes.get)
            max_score = framework_votes[best_action]
            total_possible = len(analysis["framework_analyses"])
            confidence = max_score / total_possible if total_possible > 0 else 0
        else:
            best_action = (
                dilemma.potential_actions[0]
                if dilemma.potential_actions
                else "no_action"
            )
            confidence = 0.0

        return {
            "recommended_action": best_action,
            "confidence": confidence,
            "framework_consensus": framework_votes,
            "moral_reasoning": [
                f"Analysis across {len(analysis['framework_analyses'])} ethical frameworks",
                f"Consensus recommendation: {best_action}",
                f"Confidence level: {confidence:.2f}",
            ],
        }

    def _record_moral_analysis(self, dilemma: MoralDilemma, analysis: Dict[str, Any]):
        """Record moral analysis in history."""
        record = {"timestamp": datetime.now(), "dilemma": dilemma, "analysis": analysis}

        self.moral_history.append(record)

        # Keep only recent analyses
        if len(self.moral_history) > 1000:
            self.moral_history = self.moral_history[-1000:]

    def _score_action_by_framework(
        self, action: str, context: Dict[str, Any], framework: MoralFramework
    ) -> float:
        """Score an action using a specific framework."""
        # Simplified scoring system
        score = 0.5  # Default neutral score

        action_lower = action.lower()

        if framework == MoralFramework.UTILITARIAN:
            if "benefit" in action_lower or "help" in action_lower:
                score += 0.3
            if "harm" in action_lower:
                score -= 0.4

        elif framework == MoralFramework.DEONTOLOGICAL:
            if "honest" in action_lower or "truth" in action_lower:
                score += 0.3
            if "lie" in action_lower or "deceive" in action_lower:
                score -= 0.5

        # Add more framework-specific scoring logic here

        return max(0.0, min(1.0, score))

    def _identify_ethical_concerns(
        self, action: str, context: Dict[str, Any]
    ) -> List[str]:
        """Identify potential ethical concerns with an action."""
        concerns = []
        action_lower = action.lower()

        if "harm" in action_lower:
            concerns.append("Potential harm to stakeholders")
        if "privacy" in action_lower and "violate" in action_lower:
            concerns.append("Privacy violation concerns")
        if "deceive" in action_lower or "lie" in action_lower:
            concerns.append("Truthfulness and honesty issues")
        if "force" in action_lower or "coerce" in action_lower:
            concerns.append("Autonomy and consent concerns")

        return concerns

    def _identify_positive_aspects(
        self, action: str, context: Dict[str, Any]
    ) -> List[str]:
        """Identify positive ethical aspects of an action."""
        positives = []
        action_lower = action.lower()

        if "help" in action_lower or "benefit" in action_lower:
            positives.append("Promotes welfare and benefits")
        if "honest" in action_lower or "transparent" in action_lower:
            positives.append("Promotes honesty and transparency")
        if "fair" in action_lower or "just" in action_lower:
            positives.append("Supports fairness and justice")
        if "respect" in action_lower:
            positives.append("Respects dignity and autonomy")

        return positives

    def _generate_ethical_recommendations(
        self, evaluation: Dict[str, Any]
    ) -> List[str]:
        """Generate ethical recommendations based on evaluation."""
        recommendations = []

        if evaluation["ethical_score"] < 0.5:
            recommendations.append(
                "Consider alternative actions with better ethical outcomes"
            )
            recommendations.append("Seek additional ethical review before proceeding")

        if evaluation["ethical_concerns"]:
            recommendations.append(
                "Address identified ethical concerns before implementation"
            )

        recommendations.append("Document ethical reasoning for transparency")
        recommendations.append("Monitor outcomes and be prepared to adjust approach")

        return recommendations

    def get_moral_statistics(self) -> Dict[str, Any]:
        """Get moral reasoning engine statistics."""
        return {
            "total_analyses_performed": len(self.moral_history),
            "frameworks_available": len(MoralFramework),
            "moral_principles": len(self.moral_principles),
            "recent_dilemmas": len(
                [
                    r
                    for r in self.moral_history
                    if (datetime.now() - r["timestamp"]).days < 7
                ]
            ),
        }
