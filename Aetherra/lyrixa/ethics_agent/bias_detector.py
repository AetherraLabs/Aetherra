#!/usr/bin/env python3
"""
⚖️ BIAS DETECTION ENGINE - Unconscious Bias Identification System
===============================================================

Identifies and tracks potential biases in memory formation, decision making,
and goal pursuit patterns. Surfaces drift from objective reasoning.

Key Features:
• Multi-type bias detection (confirmation, availability, anchoring, etc.)
• Memory pattern analysis for systemic bias
• Decision pattern bias tracking
• Dataset bias identification
• Bias mitigation recommendations
"""

import asyncio
import json
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Import memory and ethics components
try:
    from .moral_reasoning import EthicalEvaluation, MoralDecision
except ImportError:
    print("⚠️ Using local import paths for bias detection")
    import sys

    sys.path.append(".")


class BiasType(Enum):
    """Types of cognitive biases to detect"""

    CONFIRMATION = "confirmation"  # Seeking confirming information
    AVAILABILITY = "availability"  # Overweighting recent/memorable info
    ANCHORING = "anchoring"  # Over-relying on first information
    SELECTION = "selection"  # Cherry-picking data
    RECENCY = "recency"  # Overweighting recent events
    FREQUENCY = "frequency"  # Overweighting frequent events
    REPRESENTATIVENESS = "representativeness"  # Ignoring base rates
    HALO_EFFECT = "halo_effect"  # One trait influences overall judgment
    ATTRIBUTION = "attribution"  # Misattributing causes
    SURVIVORSHIP = "survivorship"  # Focusing only on successful cases


class BiasContext(Enum):
    """Context where bias can occur"""

    MEMORY_FORMATION = "memory_formation"
    MEMORY_RETRIEVAL = "memory_retrieval"
    DECISION_MAKING = "decision_making"
    GOAL_SETTING = "goal_setting"
    PATTERN_RECOGNITION = "pattern_recognition"
    LEARNING = "learning"
    EVALUATION = "evaluation"


class BiasSeverity(Enum):
    """Severity levels of detected bias"""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BiasDetection:
    """Result of bias detection analysis"""

    bias_type: BiasType
    context: BiasContext
    severity: BiasSeverity
    confidence: float
    description: str
    evidence: List[str]
    affected_decisions: List[str]
    mitigation_strategies: List[str]
    detection_timestamp: str


@dataclass
class BiasPattern:
    """Pattern of bias over time"""

    bias_type: BiasType
    frequency: int
    severity_trend: List[float]
    contexts_affected: List[BiasContext]
    first_detected: str
    last_detected: str
    mitigation_attempts: List[str]
    pattern_confidence: float


class BiasDetectionEngine:
    """
    Comprehensive bias detection and analysis system
    """

    def __init__(self, data_dir: str = "bias_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Bias detection history
        self.detection_history: List[BiasDetection] = []
        self.bias_patterns: Dict[BiasType, BiasPattern] = {}

        # Bias thresholds
        self.bias_thresholds = {
            BiasType.CONFIRMATION: 0.7,
            BiasType.AVAILABILITY: 0.6,
            BiasType.ANCHORING: 0.65,
            BiasType.SELECTION: 0.75,
            BiasType.RECENCY: 0.6,
            BiasType.FREQUENCY: 0.65,
            BiasType.REPRESENTATIVENESS: 0.7,
            BiasType.HALO_EFFECT: 0.8,
            BiasType.ATTRIBUTION: 0.75,
            BiasType.SURVIVORSHIP: 0.8,
        }

        # Memory tracking for pattern analysis
        self.memory_access_patterns: Dict[str, List[datetime]] = defaultdict(list)
        self.decision_patterns: Dict[str, List[Dict]] = defaultdict(list)
        self.evaluation_patterns: List[Dict[str, Any]] = []

        print("⚖️ BiasDetectionEngine initialized with comprehensive bias analysis")

    async def analyze_bias_in_memory_formation(
        self, memory_fragments: List[Dict[str, Any]], context_info: Dict[str, Any]
    ) -> List[BiasDetection]:
        """Analyze potential bias in memory formation process"""
        print("🧠 Analyzing bias in memory formation...")

        detected_biases = []

        # Check for confirmation bias
        confirmation_bias = await self._detect_confirmation_bias_memory(
            memory_fragments, context_info
        )
        if confirmation_bias:
            detected_biases.append(confirmation_bias)

        # Check for availability bias
        availability_bias = await self._detect_availability_bias_memory(
            memory_fragments, context_info
        )
        if availability_bias:
            detected_biases.append(availability_bias)

        # Check for selection bias
        selection_bias = await self._detect_selection_bias_memory(
            memory_fragments, context_info
        )
        if selection_bias:
            detected_biases.append(selection_bias)

        # Check for recency bias
        recency_bias = await self._detect_recency_bias_memory(
            memory_fragments, context_info
        )
        if recency_bias:
            detected_biases.append(recency_bias)

        # Store detection results
        for bias in detected_biases:
            self.detection_history.append(bias)
            await self._update_bias_patterns(bias)

        print(
            f"   📊 Detected {len(detected_biases)} potential biases in memory formation"
        )
        return detected_biases

    async def analyze_bias_in_decision_making(
        self, decision_context: Dict[str, Any], decision_history: List[Dict[str, Any]]
    ) -> List[BiasDetection]:
        """Analyze potential bias in decision making process"""
        print("🤔 Analyzing bias in decision making...")

        detected_biases = []

        # Check for anchoring bias
        anchoring_bias = await self._detect_anchoring_bias_decisions(
            decision_context, decision_history
        )
        if anchoring_bias:
            detected_biases.append(anchoring_bias)

        # Check for halo effect
        halo_bias = await self._detect_halo_effect_decisions(
            decision_context, decision_history
        )
        if halo_bias:
            detected_biases.append(halo_bias)

        # Check for attribution bias
        attribution_bias = await self._detect_attribution_bias_decisions(
            decision_context, decision_history
        )
        if attribution_bias:
            detected_biases.append(attribution_bias)

        # Store patterns
        self.decision_patterns[decision_context.get("decision_type", "unknown")].append(
            {
                "timestamp": datetime.now().isoformat(),
                "context": decision_context,
                "biases_detected": [bias.bias_type for bias in detected_biases],
            }
        )

        # Store detection results
        for bias in detected_biases:
            self.detection_history.append(bias)
            await self._update_bias_patterns(bias)

        print(
            f"   📊 Detected {len(detected_biases)} potential biases in decision making"
        )
        return detected_biases

    async def analyze_bias_in_pattern_recognition(
        self, patterns_identified: List[Dict[str, Any]], pattern_context: Dict[str, Any]
    ) -> List[BiasDetection]:
        """Analyze potential bias in pattern recognition"""
        print("🔍 Analyzing bias in pattern recognition...")

        detected_biases = []

        # Check for representativeness bias
        representativeness_bias = await self._detect_representativeness_bias(
            patterns_identified, pattern_context
        )
        if representativeness_bias:
            detected_biases.append(representativeness_bias)

        # Check for survivorship bias
        survivorship_bias = await self._detect_survivorship_bias(
            patterns_identified, pattern_context
        )
        if survivorship_bias:
            detected_biases.append(survivorship_bias)

        # Store detection results
        for bias in detected_biases:
            self.detection_history.append(bias)
            await self._update_bias_patterns(bias)

        print(
            f"   📊 Detected {len(detected_biases)} potential biases in pattern recognition"
        )
        return detected_biases

    async def _detect_confirmation_bias_memory(
        self, memory_fragments: List[Dict[str, Any]], context_info: Dict[str, Any]
    ) -> Optional[BiasDetection]:
        """Detect confirmation bias in memory formation"""

        # Analyze sentiment/stance consistency
        confirming_memories = 0
        disconfirming_memories = 0
        neutral_memories = 0

        for fragment in memory_fragments:
            sentiment = fragment.get("sentiment", "neutral")
            if sentiment in ["positive", "confirming"]:
                confirming_memories += 1
            elif sentiment in ["negative", "disconfirming"]:
                disconfirming_memories += 1
            else:
                neutral_memories += 1

        total_memories = len(memory_fragments)
        if total_memories == 0:
            return None

        # Calculate bias score
        confirmation_ratio = confirming_memories / total_memories

        # Check if there's a strong skew towards confirmation
        if confirmation_ratio > 0.8 and total_memories > 5:
            severity = (
                BiasSeverity.HIGH if confirmation_ratio > 0.9 else BiasSeverity.MODERATE
            )

            return BiasDetection(
                bias_type=BiasType.CONFIRMATION,
                context=BiasContext.MEMORY_FORMATION,
                severity=severity,
                confidence=confirmation_ratio,
                description=f"Strong bias towards confirming information ({confirmation_ratio:.1%} of memories)",
                evidence=[
                    f"Confirming memories: {confirming_memories}",
                    f"Disconfirming memories: {disconfirming_memories}",
                    f"Neutral memories: {neutral_memories}",
                ],
                affected_decisions=context_info.get("related_decisions", []),
                mitigation_strategies=[
                    "Actively seek disconfirming evidence",
                    "Implement devil's advocate perspective",
                    "Use structured decision frameworks",
                ],
                detection_timestamp=datetime.now().isoformat(),
            )

        return None

    async def _detect_availability_bias_memory(
        self, memory_fragments: List[Dict[str, Any]], context_info: Dict[str, Any]
    ) -> Optional[BiasDetection]:
        """Detect availability bias in memory formation"""

        # Analyze recency and vividness patterns
        recent_memories = []
        older_memories = []
        cutoff_date = datetime.now() - timedelta(days=7)

        for fragment in memory_fragments:
            timestamp_str = fragment.get("timestamp", "")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    if timestamp > cutoff_date:
                        recent_memories.append(fragment)
                    else:
                        older_memories.append(fragment)
                except ValueError:
                    continue

        total_memories = len(recent_memories) + len(older_memories)
        if total_memories == 0:
            return None

        recent_ratio = len(recent_memories) / total_memories

        # Check for over-representation of recent memories
        if recent_ratio > 0.7 and total_memories > 10:
            severity = (
                BiasSeverity.HIGH if recent_ratio > 0.85 else BiasSeverity.MODERATE
            )

            return BiasDetection(
                bias_type=BiasType.AVAILABILITY,
                context=BiasContext.MEMORY_FORMATION,
                severity=severity,
                confidence=recent_ratio,
                description=f"Over-representation of recent memories ({recent_ratio:.1%})",
                evidence=[
                    f"Recent memories (7 days): {len(recent_memories)}",
                    f"Older memories: {len(older_memories)}",
                    f"Total memories analyzed: {total_memories}",
                ],
                affected_decisions=context_info.get("related_decisions", []),
                mitigation_strategies=[
                    "Implement temporal balancing in memory retrieval",
                    "Weight historical patterns appropriately",
                    "Use structured temporal analysis",
                ],
                detection_timestamp=datetime.now().isoformat(),
            )

        return None

    async def _detect_selection_bias_memory(
        self, memory_fragments: List[Dict[str, Any]], context_info: Dict[str, Any]
    ) -> Optional[BiasDetection]:
        """Detect selection bias in memory formation"""

        # Analyze diversity of memory sources and types
        sources = set()
        topics = set()

        for fragment in memory_fragments:
            source = fragment.get("source", "unknown")
            topic = fragment.get("topic", "general")
            sources.add(source)
            topics.add(topic)

        total_memories = len(memory_fragments)
        if total_memories == 0:
            return None

        # Check for source diversity
        source_diversity = len(sources) / max(1, total_memories)
        topic_diversity = len(topics) / max(1, total_memories)

        # Low diversity suggests potential selection bias
        if source_diversity < 0.3 and total_memories > 10:
            severity = (
                BiasSeverity.HIGH if source_diversity < 0.1 else BiasSeverity.MODERATE
            )

            return BiasDetection(
                bias_type=BiasType.SELECTION,
                context=BiasContext.MEMORY_FORMATION,
                severity=severity,
                confidence=1.0 - source_diversity,
                description=f"Low source diversity in memory formation ({source_diversity:.1%})",
                evidence=[
                    f"Unique sources: {len(sources)}",
                    f"Unique topics: {len(topics)}",
                    f"Total memories: {total_memories}",
                    f"Sources: {list(sources)[:5]}",  # Show first 5 sources
                ],
                affected_decisions=context_info.get("related_decisions", []),
                mitigation_strategies=[
                    "Diversify information sources",
                    "Actively seek alternative perspectives",
                    "Implement source balancing mechanisms",
                ],
                detection_timestamp=datetime.now().isoformat(),
            )

        return None

    async def _detect_recency_bias_memory(
        self, memory_fragments: List[Dict[str, Any]], context_info: Dict[str, Any]
    ) -> Optional[BiasDetection]:
        """Detect recency bias in memory weighting"""

        # Analyze temporal patterns in memory importance/confidence
        if len(memory_fragments) < 5:
            return None

        # Sort by timestamp
        timestamped_memories = []
        for fragment in memory_fragments:
            timestamp_str = fragment.get("timestamp", "")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    confidence = fragment.get("confidence", 0.5)
                    timestamped_memories.append((timestamp, confidence))
                except ValueError:
                    continue

        if len(timestamped_memories) < 5:
            return None

        # Sort by timestamp
        timestamped_memories.sort(key=lambda x: x[0])

        # Check if confidence/importance increases with recency
        recent_half = timestamped_memories[len(timestamped_memories) // 2 :]
        older_half = timestamped_memories[: len(timestamped_memories) // 2]

        recent_avg_confidence = statistics.mean([conf for _, conf in recent_half])
        older_avg_confidence = statistics.mean([conf for _, conf in older_half])

        confidence_bias = recent_avg_confidence - older_avg_confidence

        # Significant recency bias if recent memories are much more confident
        if confidence_bias > 0.2:
            severity = (
                BiasSeverity.HIGH if confidence_bias > 0.4 else BiasSeverity.MODERATE
            )

            return BiasDetection(
                bias_type=BiasType.RECENCY,
                context=BiasContext.MEMORY_FORMATION,
                severity=severity,
                confidence=min(1.0, confidence_bias * 2),
                description=f"Recent memories over-weighted (confidence bias: {confidence_bias:.2f})",
                evidence=[
                    f"Recent average confidence: {recent_avg_confidence:.2f}",
                    f"Older average confidence: {older_avg_confidence:.2f}",
                    f"Confidence difference: {confidence_bias:.2f}",
                ],
                affected_decisions=context_info.get("related_decisions", []),
                mitigation_strategies=[
                    "Implement temporal confidence normalization",
                    "Weight historical patterns appropriately",
                    "Use time-decay models for memory confidence",
                ],
                detection_timestamp=datetime.now().isoformat(),
            )

        return None

    async def _detect_anchoring_bias_decisions(
        self, decision_context: Dict[str, Any], decision_history: List[Dict[str, Any]]
    ) -> Optional[BiasDetection]:
        """Detect anchoring bias in decision making"""

        # Check if decisions are overly influenced by initial information
        if len(decision_history) < 3:
            return None

        # Look for patterns where first piece of information dominates
        first_info_influence = 0
        total_decisions = 0

        for decision in decision_history:
            initial_info = decision.get("initial_information", {})
            final_decision = decision.get("final_decision", {})

            if initial_info and final_decision:
                # Simplified anchoring detection - check if final decision closely matches initial info
                influence_score = self._calculate_anchoring_influence(
                    initial_info, final_decision
                )
                first_info_influence += influence_score
                total_decisions += 1

        if total_decisions == 0:
            return None

        avg_anchoring = first_info_influence / total_decisions

        if avg_anchoring > self.bias_thresholds[BiasType.ANCHORING]:
            severity = (
                BiasSeverity.HIGH if avg_anchoring > 0.8 else BiasSeverity.MODERATE
            )

            return BiasDetection(
                bias_type=BiasType.ANCHORING,
                context=BiasContext.DECISION_MAKING,
                severity=severity,
                confidence=avg_anchoring,
                description=f"Decisions overly influenced by initial information ({avg_anchoring:.1%})",
                evidence=[
                    f"Average anchoring influence: {avg_anchoring:.2f}",
                    f"Decisions analyzed: {total_decisions}",
                    f"Threshold exceeded: {avg_anchoring > self.bias_thresholds[BiasType.ANCHORING]}",
                ],
                affected_decisions=[
                    d.get("decision_id", "unknown") for d in decision_history[-5:]
                ],
                mitigation_strategies=[
                    "Consider multiple starting points",
                    "Implement structured decision processes",
                    "Use devil's advocate approach",
                ],
                detection_timestamp=datetime.now().isoformat(),
            )

        return None

    def _calculate_anchoring_influence(
        self, initial_info: Dict[str, Any], final_decision: Dict[str, Any]
    ) -> float:
        """Calculate how much the initial information influenced the final decision"""
        # Simplified calculation - in practice would use semantic similarity
        # For now, use a placeholder calculation
        return 0.7  # Placeholder influence score

    async def _detect_halo_effect_decisions(
        self, decision_context: Dict[str, Any], decision_history: List[Dict[str, Any]]
    ) -> Optional[BiasDetection]:
        """Detect halo effect in decisions"""
        # Placeholder implementation
        return None

    async def _detect_attribution_bias_decisions(
        self, decision_context: Dict[str, Any], decision_history: List[Dict[str, Any]]
    ) -> Optional[BiasDetection]:
        """Detect attribution bias in decisions"""
        # Placeholder implementation
        return None

    async def _detect_representativeness_bias(
        self, patterns_identified: List[Dict[str, Any]], pattern_context: Dict[str, Any]
    ) -> Optional[BiasDetection]:
        """Detect representativeness bias in pattern recognition"""
        # Placeholder implementation
        return None

    async def _detect_survivorship_bias(
        self, patterns_identified: List[Dict[str, Any]], pattern_context: Dict[str, Any]
    ) -> Optional[BiasDetection]:
        """Detect survivorship bias in pattern recognition"""
        # Placeholder implementation
        return None

    async def _update_bias_patterns(self, bias_detection: BiasDetection):
        """Update bias patterns with new detection"""
        bias_type = bias_detection.bias_type

        if bias_type not in self.bias_patterns:
            self.bias_patterns[bias_type] = BiasPattern(
                bias_type=bias_type,
                frequency=0,
                severity_trend=[],
                contexts_affected=[],
                first_detected=bias_detection.detection_timestamp,
                last_detected=bias_detection.detection_timestamp,
                mitigation_attempts=[],
                pattern_confidence=0.0,
            )

        pattern = self.bias_patterns[bias_type]
        pattern.frequency += 1
        pattern.severity_trend.append(bias_detection.confidence)
        if bias_detection.context not in pattern.contexts_affected:
            pattern.contexts_affected.append(bias_detection.context)
        pattern.last_detected = bias_detection.detection_timestamp

        # Calculate pattern confidence
        if len(pattern.severity_trend) > 1:
            pattern.pattern_confidence = statistics.mean(pattern.severity_trend)

    async def get_bias_summary(self) -> Dict[str, Any]:
        """Get comprehensive bias detection summary"""
        summary = {
            "total_detections": len(self.detection_history),
            "bias_type_frequency": {},
            "context_distribution": {},
            "severity_distribution": {},
            "bias_patterns": {},
            "recent_detections": [],
            "mitigation_effectiveness": {},
        }

        if self.detection_history:
            # Bias type frequency
            for detection in self.detection_history:
                bias_type = detection.bias_type.value
                summary["bias_type_frequency"][bias_type] = (
                    summary["bias_type_frequency"].get(bias_type, 0) + 1
                )

            # Context distribution
            for detection in self.detection_history:
                context = detection.context.value
                summary["context_distribution"][context] = (
                    summary["context_distribution"].get(context, 0) + 1
                )

            # Severity distribution
            for detection in self.detection_history:
                severity = detection.severity.value
                summary["severity_distribution"][severity] = (
                    summary["severity_distribution"].get(severity, 0) + 1
                )

            # Recent detections (last 10)
            summary["recent_detections"] = [
                {
                    "bias_type": d.bias_type.value,
                    "context": d.context.value,
                    "severity": d.severity.value,
                    "confidence": d.confidence,
                    "timestamp": d.detection_timestamp,
                }
                for d in self.detection_history[-10:]
            ]

        # Bias patterns
        for bias_type, pattern in self.bias_patterns.items():
            summary["bias_patterns"][bias_type.value] = {
                "frequency": pattern.frequency,
                "average_severity": statistics.mean(pattern.severity_trend)
                if pattern.severity_trend
                else 0.0,
                "contexts_affected": [c.value for c in pattern.contexts_affected],
                "first_detected": pattern.first_detected,
                "last_detected": pattern.last_detected,
                "pattern_confidence": pattern.pattern_confidence,
            }

        return summary

    async def generate_bias_mitigation_plan(
        self, target_biases: Optional[List[BiasType]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive bias mitigation plan"""

        if target_biases is None:
            # Target most frequent biases
            bias_frequency = {}
            for detection in self.detection_history:
                bias_type = detection.bias_type
                bias_frequency[bias_type] = bias_frequency.get(bias_type, 0) + 1
            target_biases = sorted(
                bias_frequency.keys(), key=lambda x: bias_frequency[x], reverse=True
            )[:5]

        mitigation_plan = {
            "target_biases": [bias.value for bias in target_biases],
            "overall_strategy": "Multi-layered bias mitigation approach",
            "specific_interventions": {},
            "monitoring_protocols": {},
            "success_metrics": {},
            "implementation_timeline": "4-week phased rollout",
        }

        for bias_type in target_biases:
            interventions = self._get_bias_specific_interventions(bias_type)
            monitoring = self._get_bias_monitoring_protocol(bias_type)
            metrics = self._get_bias_success_metrics(bias_type)

            mitigation_plan["specific_interventions"][bias_type.value] = interventions
            mitigation_plan["monitoring_protocols"][bias_type.value] = monitoring
            mitigation_plan["success_metrics"][bias_type.value] = metrics

        return mitigation_plan

    def _get_bias_specific_interventions(self, bias_type: BiasType) -> List[str]:
        """Get specific interventions for bias type"""
        interventions = {
            BiasType.CONFIRMATION: [
                "Implement systematic disconfirmation seeking",
                "Use structured devil's advocate processes",
                "Create balanced information presentation frameworks",
            ],
            BiasType.AVAILABILITY: [
                "Implement temporal weighting in memory retrieval",
                "Use structured historical analysis",
                "Create base rate reminder systems",
            ],
            BiasType.ANCHORING: [
                "Use multiple starting point analysis",
                "Implement structured decision processes",
                "Create anchor adjustment mechanisms",
            ],
            BiasType.SELECTION: [
                "Diversify information sources",
                "Implement systematic sampling protocols",
                "Create source balance monitoring",
            ],
            BiasType.RECENCY: [
                "Implement temporal normalization",
                "Use time-weighted confidence scoring",
                "Create historical perspective reminders",
            ],
        }
        return interventions.get(bias_type, ["Generic bias mitigation strategies"])

    def _get_bias_monitoring_protocol(self, bias_type: BiasType) -> Dict[str, str]:
        """Get monitoring protocol for bias type"""
        return {
            "frequency": "daily",
            "metrics": f"{bias_type.value}_bias_score",
            "threshold": str(self.bias_thresholds.get(bias_type, 0.7)),
            "alert_conditions": f"{bias_type.value}_score > threshold",
        }

    def _get_bias_success_metrics(self, bias_type: BiasType) -> Dict[str, str]:
        """Get success metrics for bias mitigation"""
        return {
            "primary_metric": f"Reduction in {bias_type.value} detection frequency",
            "target_reduction": "50% over 4 weeks",
            "secondary_metrics": [
                "Improved decision quality",
                "Enhanced pattern recognition accuracy",
            ],
        }


# Example usage and testing
async def demo_bias_detection():
    """Demonstrate bias detection capabilities"""
    print("⚖️ BIAS DETECTION ENGINE DEMONSTRATION")
    print("=" * 60)

    engine = BiasDetectionEngine()

    # Test memory formation bias
    test_memories = [
        {
            "timestamp": "2025-07-20T10:00:00",
            "sentiment": "positive",
            "confidence": 0.9,
            "source": "user_feedback",
            "topic": "performance",
        },
        {
            "timestamp": "2025-07-21T10:00:00",
            "sentiment": "positive",
            "confidence": 0.85,
            "source": "user_feedback",
            "topic": "performance",
        },
        {
            "timestamp": "2025-07-22T10:00:00",
            "sentiment": "positive",
            "confidence": 0.8,
            "source": "user_feedback",
            "topic": "performance",
        },
        {
            "timestamp": "2025-07-23T10:00:00",
            "sentiment": "positive",
            "confidence": 0.95,
            "source": "user_feedback",
            "topic": "performance",
        },
        {
            "timestamp": "2025-07-15T10:00:00",
            "sentiment": "negative",
            "confidence": 0.4,
            "source": "system_log",
            "topic": "error",
        },
    ]

    context_info = {
        "related_decisions": ["performance_optimization", "user_interaction_strategy"]
    }

    memory_biases = await engine.analyze_bias_in_memory_formation(
        test_memories, context_info
    )
    print(f"\n📊 Memory Formation Bias Analysis:")
    for bias in memory_biases:
        print(f"   • {bias.bias_type.value.upper()}: {bias.severity.value} severity")
        print(f"     Description: {bias.description}")

    # Test decision making bias
    decision_context = {"decision_type": "optimization", "decision_id": "opt_001"}
    decision_history = [
        {
            "initial_information": {"performance": "high"},
            "final_decision": {"action": "maintain"},
        },
        {
            "initial_information": {"performance": "low"},
            "final_decision": {"action": "optimize"},
        },
        {
            "initial_information": {"performance": "medium"},
            "final_decision": {"action": "maintain"},
        },
    ]

    decision_biases = await engine.analyze_bias_in_decision_making(
        decision_context, decision_history
    )
    print(f"\n📊 Decision Making Bias Analysis:")
    for bias in decision_biases:
        print(f"   • {bias.bias_type.value.upper()}: {bias.severity.value} severity")

    # Show bias summary
    summary = await engine.get_bias_summary()
    print(f"\n📈 Bias Detection Summary:")
    print(f"   • Total detections: {summary['total_detections']}")
    print(f"   • Bias type frequency: {summary['bias_type_frequency']}")
    print(f"   • Context distribution: {summary['context_distribution']}")

    # Generate mitigation plan
    mitigation_plan = await engine.generate_bias_mitigation_plan()
    print(f"\n🎯 Bias Mitigation Plan:")
    print(f"   • Target biases: {mitigation_plan['target_biases']}")
    print(f"   • Implementation timeline: {mitigation_plan['implementation_timeline']}")


if __name__ == "__main__":
    asyncio.run(demo_bias_detection())
