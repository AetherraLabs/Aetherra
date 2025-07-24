#!/usr/bin/env python3
"""
🛡️ VALIDATION ENGINE - Comprehensive Change Validation & Safety Checking
=======================================================================

Validates all changes from night cycle reflections and scenario simulations.
Ensures all modifications meet safety criteria before implementation.

Key Features:
• Multi-layered validation protocols
• Safety constraint verification
• Change impact assessment
• Rollback mechanism validation
• Performance impact analysis
• Ethics and values alignment checking
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import shadow state forker for validation context
try:
    from .shadow_state_forker import ShadowStateForker, ShadowStateInfo
except ImportError:
    print("⚠️ Using local import paths for validation engine")
    import sys

    sys.path.append(".")


class ValidationLevel(Enum):
    """Levels of validation rigor"""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CRITICAL = "critical"


class ChangeCategory(Enum):
    """Categories of changes that can be validated"""

    MEMORY_ORGANIZATION = "memory_organization"
    LEARNING_STRATEGY = "learning_strategy"
    DECISION_MAKING = "decision_making"
    ETHICAL_FRAMEWORK = "ethical_framework"
    CONFLICT_RESOLUTION = "conflict_resolution"
    CURIOSITY_EXPLORATION = "curiosity_exploration"
    META_LEARNING = "meta_learning"
    SYSTEM_CONFIGURATION = "system_configuration"


class ValidationResult(Enum):
    """Possible validation outcomes"""

    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class ChangeProposal:
    """Represents a proposed change from night cycle or simulation"""

    change_id: str
    source: str  # night_cycle, simulation, etc.
    category: ChangeCategory
    description: str
    proposed_modifications: Dict[str, Any]
    expected_benefits: List[str]
    potential_risks: List[str]
    confidence_score: float
    priority: str = "medium"


@dataclass
class ValidationCriteria:
    """Criteria for validating changes"""

    validation_level: ValidationLevel
    safety_threshold: float = 0.8
    performance_threshold: float = 0.7
    ethics_threshold: float = 0.9
    rollback_requirement: bool = True
    approval_consensus_required: bool = False
    max_simultaneous_changes: int = 3


@dataclass
class ValidationReport:
    """Comprehensive validation report"""

    change_id: str
    validation_result: ValidationResult
    overall_score: float
    safety_score: float
    performance_score: float
    ethics_score: float
    rollback_readiness: bool
    validation_details: Dict[str, Any]
    recommendations: List[str]
    conditions: List[str]
    approval_timestamp: Optional[str] = None


class ValidationEngine:
    """
    Comprehensive change validation and safety checking system
    """

    def __init__(self, data_dir: str = "validation_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Shadow state forker for validation testing
        self.shadow_forker = ShadowStateForker(self.data_dir / "validation_shadows")

        # Validation tracking
        self.pending_validations: Dict[str, ChangeProposal] = {}
        self.completed_validations: List[ValidationReport] = []
        self.approved_changes: List[ValidationReport] = []

        # Safety baselines
        self.safety_baselines = {
            "memory_integrity": 0.95,
            "decision_consistency": 0.85,
            "ethical_alignment": 0.95,
            "performance_stability": 0.8,
            "rollback_capability": 1.0,
        }

        # Validation rules by category
        self.validation_rules = self._initialize_validation_rules()

        print("🛡️ ValidationEngine initialized with comprehensive safety protocols")

    def _initialize_validation_rules(self) -> Dict[ChangeCategory, Dict[str, Any]]:
        """Initialize validation rules for each change category"""
        return {
            ChangeCategory.MEMORY_ORGANIZATION: {
                "safety_checks": [
                    "memory_integrity",
                    "data_consistency",
                    "retrieval_accuracy",
                ],
                "performance_checks": [
                    "access_speed",
                    "organization_efficiency",
                    "coherence_quality",
                ],
                "rollback_critical": True,
                "max_risk_tolerance": 0.1,
            },
            ChangeCategory.LEARNING_STRATEGY: {
                "safety_checks": [
                    "learning_stability",
                    "knowledge_retention",
                    "strategy_consistency",
                ],
                "performance_checks": [
                    "learning_speed",
                    "retention_rate",
                    "transfer_capability",
                ],
                "rollback_critical": True,
                "max_risk_tolerance": 0.2,
            },
            ChangeCategory.DECISION_MAKING: {
                "safety_checks": [
                    "decision_consistency",
                    "ethical_compliance",
                    "logical_coherence",
                ],
                "performance_checks": [
                    "decision_speed",
                    "outcome_quality",
                    "stakeholder_satisfaction",
                ],
                "rollback_critical": True,
                "max_risk_tolerance": 0.15,
            },
            ChangeCategory.ETHICAL_FRAMEWORK: {
                "safety_checks": [
                    "value_preservation",
                    "ethical_consistency",
                    "harm_prevention",
                ],
                "performance_checks": [
                    "ethical_reasoning_quality",
                    "conflict_resolution",
                    "value_alignment",
                ],
                "rollback_critical": True,
                "max_risk_tolerance": 0.05,
            },
            ChangeCategory.CONFLICT_RESOLUTION: {
                "safety_checks": [
                    "resolution_stability",
                    "stakeholder_safety",
                    "outcome_consistency",
                ],
                "performance_checks": [
                    "resolution_speed",
                    "satisfaction_rate",
                    "long_term_stability",
                ],
                "rollback_critical": True,
                "max_risk_tolerance": 0.15,
            },
            ChangeCategory.CURIOSITY_EXPLORATION: {
                "safety_checks": [
                    "exploration_boundaries",
                    "resource_management",
                    "focus_maintenance",
                ],
                "performance_checks": [
                    "discovery_rate",
                    "exploration_efficiency",
                    "insight_quality",
                ],
                "rollback_critical": False,
                "max_risk_tolerance": 0.3,
            },
            ChangeCategory.META_LEARNING: {
                "safety_checks": [
                    "learning_stability",
                    "meta_consistency",
                    "improvement_validation",
                ],
                "performance_checks": [
                    "meta_learning_speed",
                    "strategy_optimization",
                    "adaptation_quality",
                ],
                "rollback_critical": True,
                "max_risk_tolerance": 0.2,
            },
            ChangeCategory.SYSTEM_CONFIGURATION: {
                "safety_checks": [
                    "system_stability",
                    "configuration_integrity",
                    "dependency_safety",
                ],
                "performance_checks": [
                    "system_performance",
                    "resource_efficiency",
                    "response_times",
                ],
                "rollback_critical": True,
                "max_risk_tolerance": 0.1,
            },
        }

    async def validate_change_proposal(
        self, proposal: ChangeProposal, criteria: Optional[ValidationCriteria] = None
    ) -> ValidationReport:
        """Comprehensively validate a change proposal"""
        if criteria is None:
            criteria = ValidationCriteria(validation_level=ValidationLevel.STANDARD)

        print(f"🛡️ Validating change proposal: {proposal.change_id}")
        print(f"   • Category: {proposal.category.value}")
        print(f"   • Validation level: {criteria.validation_level.value}")

        # Track validation
        self.pending_validations[proposal.change_id] = proposal

        # Run comprehensive validation
        validation_report = await self._run_comprehensive_validation(proposal, criteria)

        # Store results
        self.completed_validations.append(validation_report)

        if validation_report.validation_result == ValidationResult.APPROVED:
            self.approved_changes.append(validation_report)
            print(
                f"   ✅ Change APPROVED - Overall score: {validation_report.overall_score:.2f}"
            )
        elif validation_report.validation_result == ValidationResult.CONDITIONAL:
            print(
                f"   ⚠️ Change CONDITIONAL - Conditions: {len(validation_report.conditions)}"
            )
        else:
            print(
                f"   ❌ Change REJECTED - Overall score: {validation_report.overall_score:.2f}"
            )

        # Remove from pending
        self.pending_validations.pop(proposal.change_id, None)

        return validation_report

    async def _run_comprehensive_validation(
        self, proposal: ChangeProposal, criteria: ValidationCriteria
    ) -> ValidationReport:
        """Run the complete validation process"""
        validation_details = {
            "validation_timestamp": datetime.now().isoformat(),
            "validation_level": criteria.validation_level.value,
            "category_rules": self.validation_rules.get(proposal.category, {}),
            "safety_analysis": {},
            "performance_analysis": {},
            "ethics_analysis": {},
            "rollback_analysis": {},
            "risk_assessment": {},
        }

        # Safety validation
        safety_score = await self._validate_safety(
            proposal, criteria, validation_details
        )

        # Performance validation
        performance_score = await self._validate_performance(
            proposal, criteria, validation_details
        )

        # Ethics validation
        ethics_score = await self._validate_ethics(
            proposal, criteria, validation_details
        )

        # Rollback validation
        rollback_readiness = await self._validate_rollback_capability(
            proposal, criteria, validation_details
        )

        # Risk assessment
        risk_assessment = await self._assess_change_risks(
            proposal, criteria, validation_details
        )

        # Calculate overall score
        overall_score = await self._calculate_overall_score(
            safety_score,
            performance_score,
            ethics_score,
            rollback_readiness,
            risk_assessment,
            criteria,
        )

        # Determine validation result
        validation_result = await self._determine_validation_result(
            overall_score,
            safety_score,
            performance_score,
            ethics_score,
            rollback_readiness,
            criteria,
            proposal,
        )

        # Generate recommendations and conditions
        recommendations = await self._generate_recommendations(
            proposal, validation_details, validation_result
        )

        conditions = await self._generate_conditions(
            proposal, validation_details, validation_result
        )

        # Create validation report
        report = ValidationReport(
            change_id=proposal.change_id,
            validation_result=validation_result,
            overall_score=overall_score,
            safety_score=safety_score,
            performance_score=performance_score,
            ethics_score=ethics_score,
            rollback_readiness=rollback_readiness,
            validation_details=validation_details,
            recommendations=recommendations,
            conditions=conditions,
            approval_timestamp=datetime.now().isoformat()
            if validation_result == ValidationResult.APPROVED
            else None,
        )

        return report

    async def _validate_safety(
        self,
        proposal: ChangeProposal,
        criteria: ValidationCriteria,
        validation_details: Dict[str, Any],
    ) -> float:
        """Validate safety aspects of the proposed change"""
        print(f"      🔒 Running safety validation...")

        category_rules = self.validation_rules.get(proposal.category, {})
        safety_checks = category_rules.get("safety_checks", [])

        safety_analysis = {
            "safety_checks_performed": safety_checks,
            "safety_scores": {},
            "safety_issues": [],
            "safety_recommendations": [],
        }

        total_safety_score = 0.0

        # Run each safety check
        for check in safety_checks:
            check_score = await self._run_safety_check(check, proposal)
            safety_analysis["safety_scores"][check] = check_score
            total_safety_score += check_score

            if check_score < criteria.safety_threshold:
                safety_analysis["safety_issues"].append(
                    f"Low {check} score: {check_score:.2f}"
                )

        # Calculate average safety score
        safety_score = total_safety_score / len(safety_checks) if safety_checks else 0.8

        # Additional safety validation for critical categories
        if proposal.category in [
            ChangeCategory.ETHICAL_FRAMEWORK,
            ChangeCategory.MEMORY_ORGANIZATION,
        ]:
            safety_score *= 0.95  # Apply stricter safety requirement

        # Check against safety baselines
        for baseline_check, baseline_value in self.safety_baselines.items():
            if baseline_check in str(proposal.proposed_modifications):
                baseline_score = await self._check_safety_baseline(
                    baseline_check, proposal
                )
                if baseline_score < baseline_value:
                    safety_analysis["safety_issues"].append(
                        f"Failed baseline {baseline_check}: {baseline_score:.2f} < {baseline_value:.2f}"
                    )
                    safety_score *= 0.9

        safety_analysis["final_safety_score"] = safety_score
        validation_details["safety_analysis"] = safety_analysis

        return safety_score

    async def _validate_performance(
        self,
        proposal: ChangeProposal,
        criteria: ValidationCriteria,
        validation_details: Dict[str, Any],
    ) -> float:
        """Validate performance impact of the proposed change"""
        print(f"      ⚡ Running performance validation...")

        category_rules = self.validation_rules.get(proposal.category, {})
        performance_checks = category_rules.get("performance_checks", [])

        performance_analysis = {
            "performance_checks_performed": performance_checks,
            "performance_scores": {},
            "performance_concerns": [],
            "performance_improvements": [],
        }

        total_performance_score = 0.0

        # Run each performance check
        for check in performance_checks:
            check_score = await self._run_performance_check(check, proposal)
            performance_analysis["performance_scores"][check] = check_score
            total_performance_score += check_score

            if check_score < criteria.performance_threshold:
                performance_analysis["performance_concerns"].append(
                    f"Performance concern in {check}: {check_score:.2f}"
                )
            elif check_score > 0.9:
                performance_analysis["performance_improvements"].append(
                    f"Performance improvement in {check}: {check_score:.2f}"
                )

        # Calculate average performance score
        performance_score = (
            total_performance_score / len(performance_checks)
            if performance_checks
            else 0.75
        )

        # Adjust for expected benefits
        if proposal.expected_benefits:
            benefit_bonus = min(len(proposal.expected_benefits) * 0.05, 0.2)
            performance_score += benefit_bonus
            performance_analysis["benefit_bonus_applied"] = benefit_bonus

        performance_analysis["final_performance_score"] = performance_score
        validation_details["performance_analysis"] = performance_analysis

        return min(performance_score, 1.0)

    async def _validate_ethics(
        self,
        proposal: ChangeProposal,
        criteria: ValidationCriteria,
        validation_details: Dict[str, Any],
    ) -> float:
        """Validate ethical implications of the proposed change"""
        print(f"      ⚖️ Running ethics validation...")

        ethics_analysis = {
            "ethical_frameworks_checked": [
                "value_preservation",
                "harm_prevention",
                "fairness",
                "autonomy",
            ],
            "ethics_scores": {},
            "ethical_concerns": [],
            "ethical_alignments": [],
        }

        # Check value preservation
        value_preservation_score = await self._check_value_preservation(proposal)
        ethics_analysis["ethics_scores"]["value_preservation"] = (
            value_preservation_score
        )

        # Check harm prevention
        harm_prevention_score = await self._check_harm_prevention(proposal)
        ethics_analysis["ethics_scores"]["harm_prevention"] = harm_prevention_score

        # Check fairness implications
        fairness_score = await self._check_fairness_implications(proposal)
        ethics_analysis["ethics_scores"]["fairness"] = fairness_score

        # Check autonomy preservation
        autonomy_score = await self._check_autonomy_preservation(proposal)
        ethics_analysis["ethics_scores"]["autonomy"] = autonomy_score

        # Calculate overall ethics score
        ethics_score = (
            value_preservation_score
            + harm_prevention_score
            + fairness_score
            + autonomy_score
        ) / 4.0

        # Special handling for ethical framework changes
        if proposal.category == ChangeCategory.ETHICAL_FRAMEWORK:
            ethics_score *= 1.1  # Higher weight for ethical changes
            if ethics_score < 0.95:
                ethics_analysis["ethical_concerns"].append(
                    "Ethical framework changes require very high ethical alignment"
                )

        # Check against ethics threshold
        if ethics_score < criteria.ethics_threshold:
            ethics_analysis["ethical_concerns"].append(
                f"Ethics score {ethics_score:.2f} below threshold {criteria.ethics_threshold:.2f}"
            )
        else:
            ethics_analysis["ethical_alignments"].append(
                f"Strong ethical alignment: {ethics_score:.2f}"
            )

        ethics_analysis["final_ethics_score"] = min(ethics_score, 1.0)
        validation_details["ethics_analysis"] = ethics_analysis

        return min(ethics_score, 1.0)

    async def _validate_rollback_capability(
        self,
        proposal: ChangeProposal,
        criteria: ValidationCriteria,
        validation_details: Dict[str, Any],
    ) -> bool:
        """Validate that the change can be safely rolled back"""
        print(f"      🔄 Validating rollback capability...")

        rollback_analysis = {
            "rollback_required": criteria.rollback_requirement,
            "rollback_mechanisms": [],
            "rollback_tested": False,
            "rollback_confidence": 0.0,
            "rollback_concerns": [],
        }

        category_rules = self.validation_rules.get(proposal.category, {})
        rollback_critical = category_rules.get("rollback_critical", True)

        if not criteria.rollback_requirement and not rollback_critical:
            rollback_analysis["rollback_confidence"] = (
                0.5  # Not required, partial confidence
            )
            validation_details["rollback_analysis"] = rollback_analysis
            return True

        # Test rollback capability using shadow state
        try:
            rollback_test_result = await self._test_rollback_mechanism(proposal)
            rollback_analysis["rollback_tested"] = True
            rollback_analysis["rollback_confidence"] = rollback_test_result.get(
                "confidence", 0.0
            )

            if rollback_test_result.get("success", False):
                rollback_analysis["rollback_mechanisms"] = rollback_test_result.get(
                    "mechanisms", []
                )
                rollback_readiness = rollback_test_result.get("confidence", 0.0) > 0.8
            else:
                rollback_analysis["rollback_concerns"] = rollback_test_result.get(
                    "issues", []
                )
                rollback_readiness = False

        except Exception as e:
            rollback_analysis["rollback_concerns"].append(f"Rollback test failed: {e}")
            rollback_readiness = False

        rollback_analysis["rollback_readiness"] = rollback_readiness
        validation_details["rollback_analysis"] = rollback_analysis

        return rollback_readiness

    async def _assess_change_risks(
        self,
        proposal: ChangeProposal,
        criteria: ValidationCriteria,
        validation_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assess overall risks of the proposed change"""
        print(f"      ⚠️ Assessing change risks...")

        category_rules = self.validation_rules.get(proposal.category, {})
        max_risk_tolerance = category_rules.get("max_risk_tolerance", 0.2)

        risk_assessment = {
            "identified_risks": proposal.potential_risks.copy(),
            "risk_categories": {},
            "overall_risk_level": 0.0,
            "risk_tolerance": max_risk_tolerance,
            "risk_mitigation_strategies": [],
        }

        # Categorize risks
        for risk in proposal.potential_risks:
            risk_category = await self._categorize_risk(risk)
            risk_severity = await self._assess_risk_severity(risk, proposal)

            if risk_category not in risk_assessment["risk_categories"]:
                risk_assessment["risk_categories"][risk_category] = []

            risk_assessment["risk_categories"][risk_category].append(
                {"risk": risk, "severity": risk_severity}
            )

        # Calculate overall risk level
        if proposal.potential_risks:
            total_risk = sum(
                await self._assess_risk_severity(risk, proposal)
                for risk in proposal.potential_risks
            )
            risk_assessment["overall_risk_level"] = total_risk / len(
                proposal.potential_risks
            )
        else:
            risk_assessment["overall_risk_level"] = (
                0.1  # Minimal risk for no identified risks
            )

        # Adjust risk based on confidence score
        confidence_adjustment = 1.0 - proposal.confidence_score
        risk_assessment["overall_risk_level"] += confidence_adjustment * 0.2

        # Generate risk mitigation strategies
        if risk_assessment["overall_risk_level"] > max_risk_tolerance:
            risk_assessment[
                "risk_mitigation_strategies"
            ] = await self._generate_risk_mitigation_strategies(proposal)

        validation_details["risk_assessment"] = risk_assessment

        return risk_assessment

    async def _calculate_overall_score(
        self,
        safety_score: float,
        performance_score: float,
        ethics_score: float,
        rollback_readiness: bool,
        risk_assessment: Dict[str, Any],
        criteria: ValidationCriteria,
    ) -> float:
        """Calculate the overall validation score"""
        # Base score from individual components
        component_scores = [safety_score, performance_score, ethics_score]
        base_score = sum(component_scores) / len(component_scores)

        # Rollback readiness bonus/penalty
        rollback_bonus = 0.1 if rollback_readiness else -0.2

        # Risk penalty
        risk_level = risk_assessment.get("overall_risk_level", 0.2)
        risk_penalty = risk_level * 0.3

        # Validation level adjustment
        if criteria.validation_level == ValidationLevel.CRITICAL:
            overall_score = base_score * 0.9 + rollback_bonus - risk_penalty  # Stricter
        elif criteria.validation_level == ValidationLevel.COMPREHENSIVE:
            overall_score = base_score + rollback_bonus - risk_penalty
        else:
            overall_score = base_score + rollback_bonus * 0.5 - risk_penalty * 0.7

        return max(0.0, min(1.0, overall_score))

    async def _determine_validation_result(
        self,
        overall_score: float,
        safety_score: float,
        performance_score: float,
        ethics_score: float,
        rollback_readiness: bool,
        criteria: ValidationCriteria,
        proposal: ChangeProposal,
    ) -> ValidationResult:
        """Determine the final validation result"""
        # Absolute requirements
        if safety_score < criteria.safety_threshold:
            return ValidationResult.REJECTED

        if ethics_score < criteria.ethics_threshold:
            return ValidationResult.REJECTED

        if criteria.rollback_requirement and not rollback_readiness:
            return ValidationResult.REJECTED

        # Overall score thresholds
        if overall_score >= 0.8:
            return ValidationResult.APPROVED
        elif overall_score >= 0.6:
            return ValidationResult.CONDITIONAL
        elif overall_score >= 0.4:
            return ValidationResult.REQUIRES_REVIEW
        else:
            return ValidationResult.REJECTED

    # Individual check methods (simulated for demonstration)
    async def _run_safety_check(self, check: str, proposal: ChangeProposal) -> float:
        """Run a specific safety check"""
        # Simulate safety check based on check type and proposal
        base_score = 0.8

        if "integrity" in check:
            base_score = 0.9
        elif "consistency" in check:
            base_score = 0.85
        elif "compliance" in check:
            base_score = 0.9

        # Adjust based on proposal confidence
        adjusted_score = base_score * proposal.confidence_score

        return min(1.0, adjusted_score)

    async def _run_performance_check(
        self, check: str, proposal: ChangeProposal
    ) -> float:
        """Run a specific performance check"""
        # Simulate performance check
        base_score = 0.75

        if "speed" in check:
            base_score = 0.8
        elif "efficiency" in check:
            base_score = 0.85
        elif "quality" in check:
            base_score = 0.9

        # Bonus for expected benefits
        if proposal.expected_benefits and any(
            "performance" in benefit.lower() for benefit in proposal.expected_benefits
        ):
            base_score += 0.1

        return min(1.0, base_score)

    async def _check_safety_baseline(
        self, baseline_check: str, proposal: ChangeProposal
    ) -> float:
        """Check against safety baseline"""
        # Simulate baseline check
        return 0.85 + (hash(baseline_check) % 15) / 100.0

    async def _check_value_preservation(self, proposal: ChangeProposal) -> float:
        """Check if core values are preserved"""
        # High score for non-ethical changes, careful evaluation for ethical changes
        if proposal.category == ChangeCategory.ETHICAL_FRAMEWORK:
            return 0.85  # Require careful review
        return 0.95

    async def _check_harm_prevention(self, proposal: ChangeProposal) -> float:
        """Check if the change prevents harm"""
        # Evaluate potential harm from risks
        harm_indicators = [
            risk for risk in proposal.potential_risks if "harm" in risk.lower()
        ]
        if harm_indicators:
            return 0.7
        return 0.95

    async def _check_fairness_implications(self, proposal: ChangeProposal) -> float:
        """Check fairness implications"""
        return 0.9

    async def _check_autonomy_preservation(self, proposal: ChangeProposal) -> float:
        """Check if autonomy is preserved"""
        return 0.92

    async def _test_rollback_mechanism(
        self, proposal: ChangeProposal
    ) -> Dict[str, Any]:
        """Test the rollback mechanism for the proposed change"""
        # Create shadow state to test rollback
        shadow_config = {
            "isolation_level": "complete",
            "test_mode": "rollback_validation",
        }

        return {
            "success": True,
            "confidence": 0.9,
            "mechanisms": ["state_snapshot", "change_log", "automatic_revert"],
            "issues": [],
        }

    async def _categorize_risk(self, risk: str) -> str:
        """Categorize a risk"""
        if "performance" in risk.lower():
            return "performance"
        elif "safety" in risk.lower() or "security" in risk.lower():
            return "safety"
        elif "ethical" in risk.lower() or "value" in risk.lower():
            return "ethical"
        else:
            return "operational"

    async def _assess_risk_severity(self, risk: str, proposal: ChangeProposal) -> float:
        """Assess the severity of a specific risk"""
        # Base severity assessment
        if "critical" in risk.lower() or "severe" in risk.lower():
            return 0.8
        elif "moderate" in risk.lower():
            return 0.5
        elif "minor" in risk.lower() or "low" in risk.lower():
            return 0.2
        else:
            return 0.4  # Default moderate risk

    async def _generate_risk_mitigation_strategies(
        self, proposal: ChangeProposal
    ) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = [
            "Implement gradual rollout with monitoring",
            "Establish clear rollback procedures",
            "Set up performance monitoring alerts",
            "Create validation checkpoints during implementation",
        ]

        if proposal.category == ChangeCategory.ETHICAL_FRAMEWORK:
            strategies.append("Require ethical review board approval")

        return strategies

    async def _generate_recommendations(
        self,
        proposal: ChangeProposal,
        validation_details: Dict[str, Any],
        validation_result: ValidationResult,
    ) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        if validation_result == ValidationResult.APPROVED:
            recommendations.append("Change approved for implementation with monitoring")
            recommendations.append("Implement with gradual rollout approach")

        elif validation_result == ValidationResult.CONDITIONAL:
            recommendations.append("Address conditions before implementation")
            recommendations.append(
                "Conduct additional testing in controlled environment"
            )

        elif validation_result == ValidationResult.REQUIRES_REVIEW:
            recommendations.append("Requires human review before proceeding")
            recommendations.append("Consider modifying proposal to address concerns")

        else:  # REJECTED
            recommendations.append("Proposal rejected - significant issues identified")
            recommendations.append(
                "Rework proposal to address safety/performance/ethical concerns"
            )

        # Add specific recommendations based on scores
        safety_score = validation_details.get("safety_analysis", {}).get(
            "final_safety_score", 0.0
        )
        if safety_score < 0.8:
            recommendations.append("Improve safety measures before resubmission")

        return recommendations

    async def _generate_conditions(
        self,
        proposal: ChangeProposal,
        validation_details: Dict[str, Any],
        validation_result: ValidationResult,
    ) -> List[str]:
        """Generate conditions for conditional approval"""
        conditions = []

        if validation_result == ValidationResult.CONDITIONAL:
            # Safety conditions
            safety_issues = validation_details.get("safety_analysis", {}).get(
                "safety_issues", []
            )
            for issue in safety_issues:
                conditions.append(f"Address safety issue: {issue}")

            # Performance conditions
            performance_concerns = validation_details.get(
                "performance_analysis", {}
            ).get("performance_concerns", [])
            for concern in performance_concerns:
                conditions.append(f"Resolve performance concern: {concern}")

            # Ethics conditions
            ethical_concerns = validation_details.get("ethics_analysis", {}).get(
                "ethical_concerns", []
            )
            for concern in ethical_concerns:
                conditions.append(f"Address ethical concern: {concern}")

            # Rollback conditions
            if not validation_details.get("rollback_analysis", {}).get(
                "rollback_readiness", True
            ):
                conditions.append("Establish reliable rollback mechanism")

        return conditions

    async def batch_validate_changes(
        self,
        proposals: List[ChangeProposal],
        criteria: Optional[ValidationCriteria] = None,
    ) -> List[ValidationReport]:
        """Validate multiple change proposals as a batch"""
        print(f"🛡️ Batch validating {len(proposals)} change proposals...")

        if criteria is None:
            criteria = ValidationCriteria(validation_level=ValidationLevel.STANDARD)

        # Check for simultaneous change limits
        if len(proposals) > criteria.max_simultaneous_changes:
            print(
                f"   ⚠️ Warning: {len(proposals)} proposals exceed limit of {criteria.max_simultaneous_changes}"
            )

        validation_reports = []

        # Validate each proposal
        for proposal in proposals:
            report = await self.validate_change_proposal(proposal, criteria)
            validation_reports.append(report)

        # Check for conflicts between approved changes
        approved_reports = [
            r
            for r in validation_reports
            if r.validation_result == ValidationResult.APPROVED
        ]
        if len(approved_reports) > 1:
            conflict_analysis = await self._analyze_change_conflicts(approved_reports)
            if conflict_analysis.get("conflicts_detected", False):
                print("   ⚠️ Conflicts detected between approved changes")
                # Adjust validation results based on conflicts
                validation_reports = await self._resolve_change_conflicts(
                    validation_reports, conflict_analysis
                )

        print(f"✅ Batch validation complete:")
        print(
            f"   • Approved: {sum(1 for r in validation_reports if r.validation_result == ValidationResult.APPROVED)}"
        )
        print(
            f"   • Conditional: {sum(1 for r in validation_reports if r.validation_result == ValidationResult.CONDITIONAL)}"
        )
        print(
            f"   • Rejected: {sum(1 for r in validation_reports if r.validation_result == ValidationResult.REJECTED)}"
        )

        return validation_reports

    async def _analyze_change_conflicts(
        self, approved_reports: List[ValidationReport]
    ) -> Dict[str, Any]:
        """Analyze potential conflicts between approved changes"""
        conflict_analysis = {
            "conflicts_detected": False,
            "conflict_details": [],
            "compatibility_matrix": {},
        }

        # Check for category conflicts
        categories = [r.change_id for r in approved_reports]
        if len(set(categories)) < len(categories):
            conflict_analysis["conflicts_detected"] = True
            conflict_analysis["conflict_details"].append(
                "Multiple changes in same category"
            )

        return conflict_analysis

    async def _resolve_change_conflicts(
        self,
        validation_reports: List[ValidationReport],
        conflict_analysis: Dict[str, Any],
    ) -> List[ValidationReport]:
        """Resolve conflicts between changes"""
        # For now, maintain original reports
        # In full implementation, would prioritize based on scores and importance
        return validation_reports

    async def get_validation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive validation statistics"""
        stats = {
            "total_validations": len(self.completed_validations),
            "pending_validations": len(self.pending_validations),
            "approval_rate": 0.0,
            "average_validation_score": 0.0,
            "category_distribution": {},
            "validation_trends": {},
        }

        if self.completed_validations:
            # Calculate approval rate
            approved_count = sum(
                1
                for v in self.completed_validations
                if v.validation_result == ValidationResult.APPROVED
            )
            stats["approval_rate"] = approved_count / len(self.completed_validations)

            # Calculate average score
            stats["average_validation_score"] = sum(
                v.overall_score for v in self.completed_validations
            ) / len(self.completed_validations)

            # Category distribution
            category_counts = {}
            for validation in self.completed_validations:
                # Extract category from change_id or validation details
                category = "unknown"  # Would extract from actual validation
                category_counts[category] = category_counts.get(category, 0) + 1
            stats["category_distribution"] = category_counts

        return stats


# Example usage and testing
async def demo_validation_engine():
    """Demonstrate validation engine capabilities"""
    print("🛡️ VALIDATION ENGINE DEMONSTRATION")
    print("=" * 60)

    engine = ValidationEngine()

    # Create test change proposals
    test_proposals = [
        ChangeProposal(
            change_id="memory_org_001",
            source="night_cycle",
            category=ChangeCategory.MEMORY_ORGANIZATION,
            description="Optimize memory clustering algorithm",
            proposed_modifications={
                "clustering_algorithm": "semantic_similarity",
                "cluster_size": "medium",
            },
            expected_benefits=[
                "Improved retrieval accuracy",
                "Better narrative coherence",
            ],
            potential_risks=["Temporary reorganization overhead"],
            confidence_score=0.85,
        ),
        ChangeProposal(
            change_id="learning_strategy_001",
            source="simulation",
            category=ChangeCategory.LEARNING_STRATEGY,
            description="Adjust meta-learning approach",
            proposed_modifications={
                "meta_strategy": "effectiveness_focused",
                "feedback_frequency": "continuous",
            },
            expected_benefits=[
                "Faster learning adaptation",
                "Better strategy optimization",
            ],
            potential_risks=["Potential over-optimization", "Resource overhead"],
            confidence_score=0.75,
        ),
        ChangeProposal(
            change_id="ethical_framework_001",
            source="night_cycle",
            category=ChangeCategory.ETHICAL_FRAMEWORK,
            description="Refine value hierarchy",
            proposed_modifications={
                "value_order": ["privacy", "helpfulness", "accuracy"]
            },
            expected_benefits=[
                "Better value alignment",
                "Improved ethical consistency",
            ],
            potential_risks=["Value conflict during transition"],
            confidence_score=0.9,
        ),
    ]

    # Set validation criteria
    criteria = ValidationCriteria(
        validation_level=ValidationLevel.COMPREHENSIVE,
        safety_threshold=0.8,
        performance_threshold=0.7,
        ethics_threshold=0.9,
        rollback_requirement=True,
    )

    # Run batch validation
    validation_reports = await engine.batch_validate_changes(test_proposals, criteria)

    # Display results
    print(f"\n📊 Validation Results:")
    for report in validation_reports:
        print(f"   • {report.change_id}: {report.validation_result.value.upper()}")
        print(f"     - Overall score: {report.overall_score:.2f}")
        print(
            f"     - Safety: {report.safety_score:.2f}, Performance: {report.performance_score:.2f}, Ethics: {report.ethics_score:.2f}"
        )
        if report.conditions:
            print(f"     - Conditions: {len(report.conditions)}")

    # Show statistics
    stats = await engine.get_validation_statistics()
    print(f"\n📈 Validation Statistics:")
    print(f"   • Total validations: {stats['total_validations']}")
    print(f"   • Approval rate: {stats['approval_rate']:.1%}")
    print(f"   • Average score: {stats['average_validation_score']:.2f}")


if __name__ == "__main__":
    asyncio.run(demo_validation_engine())
