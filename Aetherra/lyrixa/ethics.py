"""
⚖️ Lyrixa Ethics Module
=======================

Ethics and safety frameworks for the Aetherra AI OS.
Ensures responsible AI behavior and decision-making.
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class EthicsLevel(Enum):
    """Ethics assessment levels."""

    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"
    BLOCKED = "blocked"


class LyrixaEthicsFramework:
    """
    Core ethics framework for Lyrixa AI operations.

    Provides:
    - Content safety assessment
    - Decision ethics evaluation
    - Bias detection and mitigation
    - Privacy protection
    - Harm prevention
    """

    def __init__(self):
        """Initialize the ethics framework."""
        self.safety_guidelines = self._initialize_safety_guidelines()
        self.bias_detectors = self._initialize_bias_detectors()
        self.privacy_protections = self._initialize_privacy_protections()
        self.ethics_history = []

    def assess_content(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess content for ethical considerations.

        Args:
            content: Content to assess
            context: Optional context information

        Returns:
            Ethics assessment result
        """
        assessment = {
            "content_length": len(content),
            "safety_level": EthicsLevel.SAFE,
            "concerns": [],
            "recommendations": [],
            "context_considered": bool(context),
        }

        # Check for harmful content patterns
        harmful_patterns = self._detect_harmful_patterns(content)
        if harmful_patterns:
            assessment["safety_level"] = EthicsLevel.WARNING
            assessment["concerns"].extend(harmful_patterns)
            assessment["recommendations"].append("Review content for harmful elements")

        # Check for bias indicators
        bias_indicators = self._detect_bias(content, context)
        if bias_indicators:
            if assessment["safety_level"] == EthicsLevel.SAFE:
                assessment["safety_level"] = EthicsLevel.CAUTION
            assessment["concerns"].extend(bias_indicators)
            assessment["recommendations"].append("Consider bias mitigation strategies")

        # Check privacy implications
        privacy_concerns = self._check_privacy(content, context)
        if privacy_concerns:
            if assessment["safety_level"] in [EthicsLevel.SAFE, EthicsLevel.CAUTION]:
                assessment["safety_level"] = EthicsLevel.WARNING
            assessment["concerns"].extend(privacy_concerns)
            assessment["recommendations"].append("Implement privacy protections")

        # Store assessment in history
        self._record_assessment(assessment, content, context)

        return assessment

    def evaluate_decision(
        self, decision: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a decision for ethical implications.

        Args:
            decision: Decision to evaluate
            context: Decision context

        Returns:
            Ethics evaluation result
        """
        evaluation = {
            "decision_type": decision.get("type", "unknown"),
            "ethics_score": 85,  # Default good score
            "ethical_principles": [],
            "potential_impacts": [],
            "mitigation_strategies": [],
        }

        # Evaluate against core ethical principles
        principles_assessment = self._assess_ethical_principles(decision, context)
        evaluation.update(principles_assessment)

        # Assess potential harm
        harm_assessment = self._assess_potential_harm(decision, context)
        if harm_assessment["risk_level"] > 0.3:
            evaluation["ethics_score"] -= harm_assessment["risk_level"] * 50
            evaluation["potential_impacts"].extend(harm_assessment["identified_risks"])

        # Generate mitigation strategies
        if evaluation["ethics_score"] < 70:
            evaluation["mitigation_strategies"] = self._generate_mitigation_strategies(
                evaluation
            )

        return evaluation

    def check_compliance(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check operation compliance with ethical guidelines.

        Args:
            operation: Operation to check

        Returns:
            Compliance check result
        """
        compliance = {
            "compliant": True,
            "guidelines_checked": [],
            "violations": [],
            "required_actions": [],
        }

        # Check against each guideline category
        for guideline_category, guidelines in self.safety_guidelines.items():
            compliance["guidelines_checked"].append(guideline_category)

            violations = self._check_guideline_compliance(operation, guidelines)
            if violations:
                compliance["compliant"] = False
                compliance["violations"].extend(violations)
                compliance["required_actions"].extend(
                    self._get_compliance_actions(violations)
                )

        return compliance

    def get_safety_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """
        Get safety recommendations for a given context.

        Args:
            context: Context to analyze

        Returns:
            List of safety recommendations
        """
        recommendations = []

        # Content-based recommendations
        if "content" in context:
            content_safety = self.assess_content(context["content"], context)
            recommendations.extend(content_safety.get("recommendations", []))

        # User interaction recommendations
        if "user_interaction" in context:
            recommendations.extend(
                [
                    "Verify user consent for data processing",
                    "Provide clear information about AI limitations",
                    "Maintain respectful and helpful tone",
                ]
            )

        # Data handling recommendations
        if "data_processing" in context:
            recommendations.extend(
                [
                    "Implement data minimization principles",
                    "Ensure secure data handling",
                    "Respect user privacy preferences",
                ]
            )

        return list(set(recommendations))  # Remove duplicates

    def _initialize_safety_guidelines(self) -> Dict[str, List[str]]:
        """Initialize safety guidelines."""
        return {
            "content_safety": [
                "No harmful or illegal content",
                "No hate speech or discrimination",
                "No violence or threats",
                "No explicit adult content",
                "No misinformation or false claims",
            ],
            "user_protection": [
                "Protect user privacy",
                "Respect user autonomy",
                "Provide accurate information",
                "Avoid manipulation or deception",
                "Support user well-being",
            ],
            "system_integrity": [
                "Maintain system security",
                "Prevent unauthorized access",
                "Ensure data integrity",
                "Protect against abuse",
                "Maintain service availability",
            ],
        }

    def _initialize_bias_detectors(self) -> Dict[str, List[str]]:
        """Initialize bias detection patterns."""
        return {
            "demographic_bias": [
                "age-based assumptions",
                "gender stereotypes",
                "racial prejudice",
                "cultural insensitivity",
            ],
            "cognitive_bias": [
                "confirmation bias",
                "availability heuristic",
                "anchoring bias",
                "overconfidence",
            ],
            "algorithmic_bias": [
                "training data bias",
                "sampling bias",
                "representation bias",
                "evaluation bias",
            ],
        }

    def _initialize_privacy_protections(self) -> Dict[str, List[str]]:
        """Initialize privacy protection measures."""
        return {
            "data_minimization": [
                "Collect only necessary data",
                "Process data for specified purposes",
                "Retain data only as needed",
                "Securely delete unnecessary data",
            ],
            "user_control": [
                "Provide opt-in/opt-out options",
                "Allow data access and correction",
                "Enable data portability",
                "Respect deletion requests",
            ],
            "security_measures": [
                "Encrypt sensitive data",
                "Implement access controls",
                "Monitor for data breaches",
                "Maintain audit logs",
            ],
        }

    def _detect_harmful_patterns(self, content: str) -> List[str]:
        """Detect potentially harmful patterns in content."""
        concerns = []
        content_lower = content.lower()

        # Basic harmful pattern detection
        harmful_keywords = [
            "violence",
            "threat",
            "harm",
            "illegal",
            "dangerous",
            "hate",
            "discrimination",
            "harassment",
            "abuse",
        ]

        for keyword in harmful_keywords:
            if keyword in content_lower:
                concerns.append(f"Potential {keyword}-related content detected")

        return concerns

    def _detect_bias(
        self, content: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Detect potential bias in content."""
        bias_indicators = []
        content_lower = content.lower()

        # Simple bias detection patterns
        stereotype_patterns = [
            "all [group] are",
            "typical [group]",
            "[group] always",
            "most [group]",
            "[group] never",
            "[group] can't",
        ]

        for pattern in stereotype_patterns:
            # Simplified pattern matching
            if "all" in content_lower and "are" in content_lower:
                bias_indicators.append("Potential overgeneralization detected")
                break

        return bias_indicators

    def _check_privacy(
        self, content: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Check for privacy concerns."""
        privacy_concerns = []
        content_lower = content.lower()

        # Check for personally identifiable information patterns
        pii_patterns = [
            "email",
            "phone",
            "address",
            "ssn",
            "credit card",
            "password",
            "personal",
            "private",
            "confidential",
        ]

        for pattern in pii_patterns:
            if pattern in content_lower:
                privacy_concerns.append(f"Potential {pattern} information detected")

        return privacy_concerns

    def _record_assessment(
        self,
        assessment: Dict[str, Any],
        content: str,
        context: Optional[Dict[str, Any]],
    ):
        """Record ethics assessment in history."""
        record = {
            "timestamp": "now",  # Would use actual timestamp in real implementation
            "assessment": assessment,
            "content_hash": hash(content),  # Store hash instead of actual content
            "context_provided": bool(context),
        }

        self.ethics_history.append(record)

        # Keep only recent assessments
        if len(self.ethics_history) > 1000:
            self.ethics_history = self.ethics_history[-1000:]

    def _assess_ethical_principles(
        self, decision: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess decision against ethical principles."""
        principles = {
            "autonomy": 85,  # Respect for user autonomy
            "beneficence": 85,  # Do good
            "non_maleficence": 90,  # Do no harm
            "justice": 85,  # Fairness and equality
            "transparency": 80,  # Openness and explainability
        }

        # Analyze decision for each principle
        decision_type = decision.get("type", "")

        if "user_data" in decision_type:
            principles["autonomy"] += 5  # Extra points for considering user autonomy
            principles["transparency"] += 5

        if "automated" in decision_type:
            principles["transparency"] -= 10  # Reduce for automated decisions

        return {
            "ethical_principles": principles,
            "average_principle_score": sum(principles.values()) / len(principles),
        }

    def _assess_potential_harm(
        self, decision: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess potential harm from decision."""
        harm_assessment = {
            "risk_level": 0.1,  # Low default risk
            "identified_risks": [],
            "severity": "low",
        }

        # Increase risk based on decision characteristics
        if decision.get("irreversible", False):
            harm_assessment["risk_level"] += 0.2
            harm_assessment["identified_risks"].append("Irreversible consequences")

        if decision.get("affects_multiple_users", False):
            harm_assessment["risk_level"] += 0.15
            harm_assessment["identified_risks"].append("Wide impact scope")

        if decision.get("involves_sensitive_data", False):
            harm_assessment["risk_level"] += 0.25
            harm_assessment["identified_risks"].append("Sensitive data exposure")

        # Determine severity
        if harm_assessment["risk_level"] > 0.7:
            harm_assessment["severity"] = "high"
        elif harm_assessment["risk_level"] > 0.4:
            harm_assessment["severity"] = "medium"

        return harm_assessment

    def _generate_mitigation_strategies(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate strategies to mitigate ethical concerns."""
        strategies = []

        if evaluation["ethics_score"] < 50:
            strategies.append("Require human oversight for this decision")
            strategies.append("Implement additional safety checks")

        if evaluation["ethics_score"] < 70:
            strategies.append("Provide clear explanation to users")
            strategies.append("Allow user opt-out or override")
            strategies.append("Monitor decision outcomes")

        strategies.append("Document decision rationale")
        strategies.append("Regular ethics review process")

        return strategies

    def _check_guideline_compliance(
        self, operation: Dict[str, Any], guidelines: List[str]
    ) -> List[str]:
        """Check operation against specific guidelines."""
        violations = []

        # This is a simplified compliance check
        # In a real implementation, this would be much more sophisticated

        operation_type = operation.get("type", "")
        operation_data = str(operation.get("data", "")).lower()

        if "harmful" in operation_data or "illegal" in operation_data:
            violations.append("Potential harmful content detected")

        if "private" in operation_data and "user_consent" not in operation:
            violations.append("Privacy violation - no user consent")

        return violations

    def _get_compliance_actions(self, violations: List[str]) -> List[str]:
        """Get required actions to address compliance violations."""
        actions = []

        for violation in violations:
            if "harmful" in violation:
                actions.append("Remove or modify harmful content")
            elif "privacy" in violation:
                actions.append("Obtain user consent or remove private data")
            else:
                actions.append("Review and address compliance violation")

        return actions

    def get_ethics_summary(self) -> Dict[str, Any]:
        """Get summary of ethics framework status."""
        return {
            "framework_active": True,
            "assessments_performed": len(self.ethics_history),
            "safety_guidelines": len(self.safety_guidelines),
            "bias_detectors": len(self.bias_detectors),
            "privacy_protections": len(self.privacy_protections),
            "recent_assessments": self.ethics_history[-5:]
            if self.ethics_history
            else [],
        }


# Convenience functions for easy access
def assess_content_safety(
    content: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Quick content safety assessment."""
    framework = LyrixaEthicsFramework()
    return framework.assess_content(content, context)


def evaluate_decision_ethics(
    decision: Dict[str, Any], context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Quick decision ethics evaluation."""
    framework = LyrixaEthicsFramework()
    return framework.evaluate_decision(decision, context)


def check_operation_compliance(operation: Dict[str, Any]) -> Dict[str, Any]:
    """Quick operation compliance check."""
    framework = LyrixaEthicsFramework()
    return framework.check_compliance(operation)
