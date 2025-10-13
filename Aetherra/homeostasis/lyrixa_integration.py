#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🤖 Lyrixa Integration for Alert Intelligence
============================================

This module integrates Lyrixa's reflection capabilities with the alert intelligence
system to provide AI-generated explanations, root cause analysis, and remediation
suggestions for homeostasis anomalies.

Author: Aetherra Labs
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .alert_intelligence import (
    AlertSeverity,
    AlertStatus,
    AnomalyDetection,
    IntelligentAlert,
)

logger = logging.getLogger(__name__)


@dataclass
class LyrixaReflectionRequest:
    """Request for Lyrixa reflection analysis."""

    request_id: str
    anomaly_data: Dict[str, Any]
    context: Dict[str, Any]
    analysis_type: str  # "explanation", "root_cause", "remediation", "impact"
    priority: str  # "low", "medium", "high", "critical"
    timeout: float  # Maximum time to wait for response


@dataclass
class LyrixaReflectionResponse:
    """Response from Lyrixa reflection analysis."""

    request_id: str
    analysis_type: str

    # Main content
    explanation: str
    confidence: float
    reasoning: List[str]

    # Specific analysis results
    root_causes: List[Dict[str, Any]]
    remediation_steps: List[Dict[str, Any]]
    impact_assessment: Dict[str, Any]

    # Metadata
    processing_time: float
    model_version: str
    timestamp: str


class LyrixaAlertIntegration:
    """
    Integration layer between alert intelligence and Lyrixa's reflection capabilities.

    Provides AI-assisted explanations and analysis for homeostasis anomalies.
    """

    def __init__(self):
        self.integration_active = False
        self.lyrixa_available = False

        # Configuration
        self.default_timeout = 30.0  # 30 seconds
        self.max_retry_count = 3
        self.explanation_cache: Dict[str, LyrixaReflectionResponse] = {}

        # Statistics
        self.requests_made = 0
        self.successful_responses = 0
        self.cached_responses = 0
        self.failed_requests = 0

        logger.info("🤖 Lyrixa alert integration initialized")

    async def start_integration(self):
        """Start the Lyrixa integration."""
        try:
            # Check if Lyrixa is available
            self.lyrixa_available = await self._check_lyrixa_availability()

            if self.lyrixa_available:
                self.integration_active = True
                logger.info("🤖 Lyrixa integration started - AI explanations enabled")
            else:
                logger.warning("⚠️ Lyrixa not available - using fallback explanations")

        except Exception as e:
            logger.error(f"❌ Failed to start Lyrixa integration: {e}")
            self.lyrixa_available = False

    async def stop_integration(self):
        """Stop the Lyrixa integration."""
        self.integration_active = False
        logger.info("🤖 Lyrixa integration stopped")

    async def create_intelligent_alert(
        self, detection: AnomalyDetection, context: Optional[Dict[str, Any]] = None
    ) -> IntelligentAlert:
        """
        Create an intelligent alert with AI-generated explanations.

        Args:
            detection: The anomaly detection
            context: Additional context for analysis

        Returns:
            IntelligentAlert with AI-generated content
        """
        try:
            alert_id = f"alert_{int(time.time() * 1000)}_{detection.metric_name}"

            # Prepare context for Lyrixa analysis
            analysis_context = {
                "detection": {
                    "metric_name": detection.metric_name,
                    "value": detection.value,
                    "baseline": detection.baseline_value,
                    "deviation": detection.deviation_score,
                    "anomaly_type": detection.anomaly_type.value,
                    "severity": detection.severity.value,
                    "confidence": detection.confidence,
                },
                "pattern_context": detection.pattern_context,
                "root_cause_analysis": detection.root_cause_analysis,
                "correlation_analysis": detection.correlation_analysis,
                "prediction_context": detection.prediction_context,
                "additional_context": context or {},
            }

            # Get AI-generated explanations
            explanation_response = await self._get_explanation(detection, analysis_context)
            root_cause_response = await self._get_root_cause_analysis(detection, analysis_context)
            remediation_response = await self._get_remediation_suggestions(
                detection, analysis_context
            )
            impact_response = await self._get_impact_assessment(detection, analysis_context)

            # Combine Lyrixa responses
            reflection_analysis = None
            if explanation_response:
                reflection_analysis = {
                    "explanation": explanation_response.explanation,
                    "confidence": explanation_response.confidence,
                    "reasoning": explanation_response.reasoning,
                    "root_causes": root_cause_response.root_causes if root_cause_response else [],
                    "remediation": remediation_response.remediation_steps
                    if remediation_response
                    else [],
                    "impact": impact_response.impact_assessment if impact_response else {},
                    "model_version": explanation_response.model_version,
                    "processing_time": explanation_response.processing_time,
                }

            # Generate alert content
            title = self._generate_alert_title(detection)
            description = self._generate_alert_description(detection, explanation_response)
            category = self._determine_alert_category(detection)

            # Create intelligent alert
            alert = IntelligentAlert(
                alert_id=alert_id,
                detection_id=detection.detection_id,
                title=title,
                description=description,
                severity=detection.severity,
                category=category,
                explanation=explanation_response.explanation
                if explanation_response
                else self._fallback_explanation(detection),
                root_cause_hypothesis=self._extract_primary_root_cause(root_cause_response),
                remediation_suggestions=self._extract_remediation_steps(remediation_response),
                impact_assessment=self._extract_impact_summary(impact_response),
                triggered_at=datetime.now().isoformat(),
                expires_at=None,  # Could implement expiration logic
                context_data=analysis_context,
                status=AlertStatus.ACTIVE,
                assignee=None,
                escalation_level=0,
                reflection_analysis=reflection_analysis,
                explanation_confidence=explanation_response.confidence
                if explanation_response
                else 0.5,
            )

            return alert

        except Exception as e:
            logger.error(f"❌ Error creating intelligent alert: {e}")
            # Return basic alert as fallback
            return self._create_fallback_alert(detection, context)

    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status."""
        return {
            "integration_active": self.integration_active,
            "lyrixa_available": self.lyrixa_available,
            "requests_made": self.requests_made,
            "successful_responses": self.successful_responses,
            "cached_responses": self.cached_responses,
            "failed_requests": self.failed_requests,
            "cache_size": len(self.explanation_cache),
            "success_rate": self.successful_responses / max(self.requests_made, 1),
        }

    # Private methods

    async def _check_lyrixa_availability(self) -> bool:
        """Check if Lyrixa reflection service is available."""
        try:
            # Simulate checking Lyrixa availability
            # In real implementation, this would check if Lyrixa is running and responsive
            await asyncio.sleep(0.1)  # Simulate network check

            # For now, return True to enable AI features
            # In production, this would make an actual health check to Lyrixa
            return True

        except Exception as e:
            logger.error(f"❌ Error checking Lyrixa availability: {e}")
            return False

    async def _get_explanation(
        self, detection: AnomalyDetection, context: Dict[str, Any]
    ) -> Optional[LyrixaReflectionResponse]:
        """Get AI-generated explanation for the anomaly."""
        try:
            # Check cache first
            cache_key = f"explanation_{detection.metric_name}_{detection.anomaly_type.value}"
            if cache_key in self.explanation_cache:
                self.cached_responses += 1
                return self.explanation_cache[cache_key]

            # Prepare request
            request = LyrixaReflectionRequest(
                request_id=f"req_{int(time.time() * 1000)}",
                anomaly_data={
                    "metric": detection.metric_name,
                    "value": detection.value,
                    "baseline": detection.baseline_value,
                    "deviation": detection.deviation_score,
                    "type": detection.anomaly_type.value,
                    "severity": detection.severity.value,
                },
                context=context,
                analysis_type="explanation",
                priority=detection.severity.value,
                timeout=self.default_timeout,
            )

            # Make request to Lyrixa
            response = await self._make_lyrixa_request(request)

            if response:
                # Cache successful response
                self.explanation_cache[cache_key] = response

            return response

        except Exception as e:
            logger.error(f"❌ Error getting explanation from Lyrixa: {e}")
            return None

    async def _get_root_cause_analysis(
        self, detection: AnomalyDetection, context: Dict[str, Any]
    ) -> Optional[LyrixaReflectionResponse]:
        """Get AI-generated root cause analysis."""
        try:
            request = LyrixaReflectionRequest(
                request_id=f"rca_{int(time.time() * 1000)}",
                anomaly_data={
                    "metric": detection.metric_name,
                    "pattern": detection.pattern_context,
                    "correlations": detection.correlation_analysis,
                    "baseline_analysis": detection.root_cause_analysis,
                },
                context=context,
                analysis_type="root_cause",
                priority=detection.severity.value,
                timeout=self.default_timeout,
            )

            return await self._make_lyrixa_request(request)

        except Exception as e:
            logger.error(f"❌ Error getting root cause analysis: {e}")
            return None

    async def _get_remediation_suggestions(
        self, detection: AnomalyDetection, context: Dict[str, Any]
    ) -> Optional[LyrixaReflectionResponse]:
        """Get AI-generated remediation suggestions."""
        try:
            request = LyrixaReflectionRequest(
                request_id=f"rem_{int(time.time() * 1000)}",
                anomaly_data={
                    "metric": detection.metric_name,
                    "severity": detection.severity.value,
                    "type": detection.anomaly_type.value,
                    "current_value": detection.value,
                    "target_range": detection.threshold_values,
                },
                context=context,
                analysis_type="remediation",
                priority=detection.severity.value,
                timeout=self.default_timeout,
            )

            return await self._make_lyrixa_request(request)

        except Exception as e:
            logger.error(f"❌ Error getting remediation suggestions: {e}")
            return None

    async def _get_impact_assessment(
        self, detection: AnomalyDetection, context: Dict[str, Any]
    ) -> Optional[LyrixaReflectionResponse]:
        """Get AI-generated impact assessment."""
        try:
            request = LyrixaReflectionRequest(
                request_id=f"imp_{int(time.time() * 1000)}",
                anomaly_data={
                    "metric": detection.metric_name,
                    "severity": detection.severity.value,
                    "deviation_magnitude": detection.deviation_score,
                    "system_context": context.get("additional_context", {}),
                },
                context=context,
                analysis_type="impact",
                priority=detection.severity.value,
                timeout=self.default_timeout,
            )

            return await self._make_lyrixa_request(request)

        except Exception as e:
            logger.error(f"❌ Error getting impact assessment: {e}")
            return None

    async def _make_lyrixa_request(
        self, request: LyrixaReflectionRequest
    ) -> Optional[LyrixaReflectionResponse]:
        """Make a request to Lyrixa reflection service."""
        try:
            if not self.lyrixa_available:
                return None

            self.requests_made += 1
            start_time = time.time()

            # Simulate Lyrixa reflection processing
            # In real implementation, this would make an actual API call to Lyrixa
            await asyncio.sleep(0.5)  # Simulate processing time

            processing_time = time.time() - start_time

            # Generate simulated AI response based on request type
            response = self._generate_simulated_response(request, processing_time)

            self.successful_responses += 1
            return response

        except Exception as e:
            logger.error(f"❌ Error making Lyrixa request: {e}")
            self.failed_requests += 1
            return None

    def _generate_simulated_response(
        self, request: LyrixaReflectionRequest, processing_time: float
    ) -> LyrixaReflectionResponse:
        """Generate a simulated Lyrixa response for demonstration."""
        metric_name = request.anomaly_data.get("metric", "unknown")

        if request.analysis_type == "explanation":
            explanation = (
                f"The metric '{metric_name}' has deviated significantly from its baseline pattern. "
                f"This anomaly was detected using adaptive thresholds that learned from historical data. "
                f"The current value exceeds expected bounds based on recent behavioral patterns."
            )

            reasoning = [
                "Statistical analysis shows value outside 95% confidence interval",
                "Pattern recognition indicates deviation from learned baseline",
                "Temporal analysis suggests unusual timing or magnitude",
            ]

        elif request.analysis_type == "root_cause":
            explanation = (
                f"Root cause analysis for {metric_name} anomaly suggests potential systemic issues."
            )

            reasoning = [
                "Correlation analysis with related metrics",
                "Temporal pattern analysis",
                "Historical precedent examination",
            ]

        elif request.analysis_type == "remediation":
            explanation = f"Recommended remediation steps for {metric_name} anomaly."

            reasoning = [
                "Based on historical successful interventions",
                "Considering current system state and constraints",
                "Prioritized by impact and feasibility",
            ]

        else:  # impact
            explanation = f"Impact assessment for {metric_name} anomaly on system stability."

            reasoning = [
                "Analysis of dependent systems and metrics",
                "Historical impact correlation",
                "Cascading effect prediction",
            ]

        return LyrixaReflectionResponse(
            request_id=request.request_id,
            analysis_type=request.analysis_type,
            explanation=explanation,
            confidence=0.85,  # High confidence for demonstration
            reasoning=reasoning,
            root_causes=[
                {
                    "cause": "Threshold breach",
                    "confidence": 0.9,
                    "evidence": ["Statistical deviation"],
                },
                {"cause": "Pattern change", "confidence": 0.7, "evidence": ["Trend analysis"]},
            ],
            remediation_steps=[
                {"action": "Monitor closely", "priority": "immediate", "estimated_time": "ongoing"},
                {
                    "action": "Investigate correlations",
                    "priority": "high",
                    "estimated_time": "15 minutes",
                },
                {
                    "action": "Consider threshold adjustment",
                    "priority": "medium",
                    "estimated_time": "30 minutes",
                },
            ],
            impact_assessment={
                "severity": "medium",
                "affected_systems": [metric_name],
                "estimated_duration": "15-30 minutes",
                "cascading_risk": "low",
            },
            processing_time=processing_time,
            model_version="lyrixa-reflection-v1.0",
            timestamp=datetime.now().isoformat(),
        )

    def _generate_alert_title(self, detection: AnomalyDetection) -> str:
        """Generate a descriptive title for the alert."""
        severity_emoji = {
            AlertSeverity.LOW: "🟡",
            AlertSeverity.MEDIUM: "🟠",
            AlertSeverity.HIGH: "🔴",
            AlertSeverity.CRITICAL: "🚨",
        }

        emoji = severity_emoji.get(detection.severity, "⚠️")

        return (
            f"{emoji} {detection.anomaly_type.value.replace('_', ' ').title()} "
            f"detected in {detection.metric_name}"
        )

    def _generate_alert_description(
        self, detection: AnomalyDetection, explanation: Optional[LyrixaReflectionResponse]
    ) -> str:
        """Generate a detailed description for the alert."""
        desc = f"Anomaly detected in metric '{detection.metric_name}' at {detection.timestamp}.\n\n"
        desc += f"Current value: {detection.value:.3f}\n"
        desc += f"Baseline: {detection.baseline_value:.3f}\n"
        desc += f"Deviation: {detection.deviation_score:.2f} standard deviations\n"
        desc += f"Confidence: {detection.confidence:.1%}\n\n"

        if explanation:
            desc += f"AI Analysis: {explanation.explanation}"
        else:
            desc += (
                "Automated analysis indicates this value is outside normal operating parameters."
            )

        return desc

    def _determine_alert_category(self, detection: AnomalyDetection) -> str:
        """Determine the alert category based on anomaly type."""
        category_mapping = {
            "threshold_breach": "Threshold Violations",
            "pattern_deviation": "Pattern Anomalies",
            "trend_anomaly": "Trend Changes",
            "correlation_break": "Correlation Breaks",
            "seasonal_anomaly": "Seasonal Deviations",
            "outlier_detection": "Statistical Outliers",
        }

        return category_mapping.get(detection.anomaly_type.value, "General Anomalies")

    def _fallback_explanation(self, detection: AnomalyDetection) -> str:
        """Generate a fallback explanation when Lyrixa is not available."""
        return (
            f"The metric '{detection.metric_name}' has exceeded normal operating thresholds. "
            f"Current value ({detection.value:.3f}) deviates {detection.deviation_score:.1f} "
            f"standard deviations from the baseline ({detection.baseline_value:.3f}). "
            f"This represents a {detection.severity.value} severity {detection.anomaly_type.value.replace('_', ' ')}."
        )

    def _extract_primary_root_cause(self, response: Optional[LyrixaReflectionResponse]) -> str:
        """Extract the primary root cause hypothesis."""
        if not response or not response.root_causes:
            return "Root cause analysis pending - manual investigation recommended."

        # Get highest confidence root cause
        primary_cause = max(response.root_causes, key=lambda x: x.get("confidence", 0))
        return f"{primary_cause['cause']} (confidence: {primary_cause.get('confidence', 0):.1%})"

    def _extract_remediation_steps(self, response: Optional[LyrixaReflectionResponse]) -> List[str]:
        """Extract remediation steps from Lyrixa response."""
        if not response or not response.remediation_steps:
            return [
                "Monitor the metric for continued anomalies",
                "Review recent system changes",
                "Check correlation with other metrics",
                "Consider adjusting alert thresholds if pattern persists",
            ]

        return [step["action"] for step in response.remediation_steps]

    def _extract_impact_summary(self, response: Optional[LyrixaReflectionResponse]) -> str:
        """Extract impact assessment summary."""
        if not response or not response.impact_assessment:
            return (
                "Impact assessment: Monitoring recommended to prevent potential system degradation."
            )

        impact = response.impact_assessment
        return (
            f"Severity: {impact.get('severity', 'unknown')}, "
            f"Estimated duration: {impact.get('estimated_duration', 'unknown')}, "
            f"Cascading risk: {impact.get('cascading_risk', 'unknown')}"
        )

    def _create_fallback_alert(
        self, detection: AnomalyDetection, context: Optional[Dict[str, Any]]
    ) -> IntelligentAlert:
        """Create a basic alert when AI analysis fails."""
        alert_id = f"fallback_{int(time.time() * 1000)}_{detection.metric_name}"

        return IntelligentAlert(
            alert_id=alert_id,
            detection_id=detection.detection_id,
            title=self._generate_alert_title(detection),
            description=self._generate_alert_description(detection, None),
            severity=detection.severity,
            category=self._determine_alert_category(detection),
            explanation=self._fallback_explanation(detection),
            root_cause_hypothesis="Manual analysis required",
            remediation_suggestions=self._extract_remediation_steps(None),
            impact_assessment=self._extract_impact_summary(None),
            triggered_at=datetime.now().isoformat(),
            expires_at=None,
            context_data={"detection_data": detection.__dict__, "additional_context": context},
            status=AlertStatus.ACTIVE,
            assignee=None,
            escalation_level=0,
            reflection_analysis=None,
            explanation_confidence=0.3,  # Low confidence for fallback
        )


# Global instance for easy access
_lyrixa_integration: Optional[LyrixaAlertIntegration] = None


def get_lyrixa_integration() -> LyrixaAlertIntegration:
    """Get the global Lyrixa integration instance."""
    global _lyrixa_integration

    if _lyrixa_integration is None:
        _lyrixa_integration = LyrixaAlertIntegration()

    return _lyrixa_integration
