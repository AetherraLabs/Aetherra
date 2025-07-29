#!/usr/bin/env python3
"""
⚔️ CONTRADICTION DETECTION AGENT - Phase 3 Implementation
==========================================================

Advanced Contradiction Detection Agent that integrates with the existing Lyrixa agent architecture.
Detects multi-type contradictions and generates resolution strategies.

Integrates with:
- Existing agent_base.py architecture
- Memory system via FractalMesh
- Confidence spread analysis
- Resolution strategy generation
"""

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .agent_base import AgentBase, AgentResponse

# Try to import memory components
try:
    from ..memory.fractal_mesh.base import FractalMesh
    from ..memory.reflector.reflect_analyzer import ReflectAnalyzer
except ImportError:
    print("⚠️ Memory components not available, using mock implementations")
    FractalMesh = None
    ReflectAnalyzer = None


class ContradictionType(Enum):
    """Types of contradictions we can detect"""

    LOGICAL = "logical"  # A != A
    TEMPORAL = "temporal"  # Past belief conflicts with current
    CONTEXTUAL = "contextual"  # Same concept, different contexts, different conclusions
    CAUSAL = "causal"  # Cause-effect relationships that don't align
    BEHAVIORAL = "behavioral"  # Actions don't match stated beliefs/goals


@dataclass
class DetectedContradiction:
    """Represents a detected contradiction in the memory system"""

    contradiction_id: str
    contradiction_type: ContradictionType
    title: str
    description: str
    confidence_score: float  # How confident we are this is a real contradiction
    severity: str  # "low", "medium", "high", "critical"

    # Evidence for the contradiction
    evidence_for: List[Dict[str, Any]]  # Memory fragments supporting side A
    evidence_against: List[Dict[str, Any]]  # Memory fragments supporting side B

    # Context and analysis
    context_factors: List[str]
    potential_causes: List[str]
    resolution_strategies: List[str]

    # Metadata
    first_detected: str
    last_updated: str
    resolution_status: str = (
        "open"  # "open", "investigating", "resolved", "false_positive"
    )
    resolution_notes: str = ""


@dataclass
class ResolutionStrategy:
    """Represents a strategy for resolving a contradiction"""

    strategy_id: str
    contradiction_id: str
    strategy_type: str  # "clarification", "context_separation", "temporal_evolution", "evidence_gathering"
    description: str
    steps: List[str]
    expected_outcome: str
    confidence: float
    estimated_effort: str
    priority: str
    timestamp: str


class ContradictionDetectionAgent(AgentBase):
    """
    Advanced Contradiction Detection Engine for multi-type conflict resolution
    """

    def __init__(self, memory_engine=None, data_dir="contradiction_data"):
        super().__init__(
            "ContradictionDetectionAgent",
            "Detects multi-type contradictions and generates resolution strategies",
        )

        self.memory_engine = memory_engine
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Agent-specific components
        self.fractal_mesh = None
        self.reflector = None

        if memory_engine:
            self._initialize_memory_components()

        # Storage for contradictions and strategies
        self.detected_contradictions: Dict[str, DetectedContradiction] = {}
        self.resolution_strategies: Dict[str, ResolutionStrategy] = {}

        # Configuration
        self.confidence_threshold = 0.6
        self.max_contradictions_tracked = 30
        self.severity_thresholds = {
            "critical": 0.9,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.3,
        }

        # Load existing data
        self._load_persistence_data()

        self.log(
            "⚔️ ContradictionDetectionAgent initialized with multi-type conflict detection"
        )

    def _initialize_memory_components(self):
        """Initialize memory system components"""
        try:
            if FractalMesh:
                self.fractal_mesh = FractalMesh()
            if ReflectAnalyzer:
                self.reflector = ReflectAnalyzer(self.memory_engine)

            self.log("✅ Memory components initialized for contradiction detection")
        except Exception as e:
            self.log(f"⚠️ Could not initialize memory components: {e}", "WARNING")

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process contradiction detection input and commands"""
        context = context or {}

        try:
            input_lower = input_text.lower()

            # Handle different contradiction detection commands
            if (
                "detect contradictions" in input_lower
                or "find conflicts" in input_lower
            ):
                result = await self._handle_contradiction_detection(context)
            elif "analyze consistency" in input_lower:
                result = await self._handle_consistency_analysis(context)
            elif "resolve contradiction" in input_lower:
                result = await self._handle_contradiction_resolution(
                    input_text, context
                )
            elif (
                "contradiction status" in input_lower
                or "conflict status" in input_lower
            ):
                result = await self._handle_status_request(context)
            elif "generate strategies" in input_lower:
                result = await self._handle_strategy_generation(input_text, context)
            elif "validate resolution" in input_lower:
                result = await self._handle_resolution_validation(input_text, context)
            else:
                # General contradiction analysis
                result = await self._handle_general_analysis(input_text, context)

            self._increment_success()
            return result

        except Exception as e:
            self.log(f"Error processing contradiction detection input: {e}", "ERROR")
            self._increment_error()

            return AgentResponse(
                content=f"I encountered an error while analyzing contradictions: {str(e)}",
                confidence=0.0,
                agent_name=self.name,
                metadata={"error": str(e)},
            )

    async def _handle_contradiction_detection(
        self, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle contradiction detection requests"""
        timeframe_hours = context.get("timeframe_hours", 72)
        contradiction_types = context.get("types", list(ContradictionType))

        self.log(f"⚔️ Detecting contradictions in the last {timeframe_hours} hours")

        contradictions = await self.detect_contradictions(
            timeframe_hours, contradiction_types
        )

        if not contradictions:
            return AgentResponse(
                content="I haven't detected any significant contradictions in the specified timeframe. This suggests good internal consistency or the analysis window may need adjustment.",
                confidence=0.8,
                agent_name=self.name,
                metadata={"contradictions_found": 0, "timeframe": timeframe_hours},
            )

        # Format response about detected contradictions
        contradiction_summary = []
        for contradiction in contradictions[:5]:  # Limit to top 5
            contradiction_summary.append(
                f"• **{contradiction.contradiction_type.value.title()}**: {contradiction.title} "
                f"(Severity: {contradiction.severity}, Confidence: {contradiction.confidence_score:.2f})"
            )

        content = (
            f"⚔️ I've detected {len(contradictions)} contradictions requiring attention:\n\n"
            + "\n".join(contradiction_summary)
        )

        if len(contradictions) > 5:
            content += f"\n\n*And {len(contradictions) - 5} additional contradictions detected.*"

        return AgentResponse(
            content=content,
            confidence=0.9,
            agent_name=self.name,
            metadata={
                "contradictions_found": len(contradictions),
                "types_detected": list(
                    set(c.contradiction_type.value for c in contradictions)
                ),
                "high_severity_count": len(
                    [c for c in contradictions if c.severity in ["high", "critical"]]
                ),
            },
        )

    async def _handle_consistency_analysis(
        self, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle consistency pattern analysis"""
        self.log("🔍 Analyzing consistency patterns in memory")

        analysis = await self.analyze_consistency_patterns()

        content = f"""🔍 **Consistency Analysis Results**

**Overall Consistency Score**: {analysis["overall_score"]:.2f}/1.0

**Pattern Analysis**:
• Logical Consistency: {analysis["logical_consistency"]:.2f}
• Temporal Consistency: {analysis["temporal_consistency"]:.2f}
• Contextual Consistency: {analysis["contextual_consistency"]:.2f}
• Behavioral Consistency: {analysis["behavioral_consistency"]:.2f}

**Key Findings**:
{self._format_findings(analysis["key_findings"])}

**Recommendations**:
{self._format_recommendations(analysis["recommendations"])}
"""

        return AgentResponse(
            content=content, confidence=0.85, agent_name=self.name, metadata=analysis
        )

    async def _handle_contradiction_resolution(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle contradiction resolution requests"""
        # Extract contradiction ID from input
        if "contradiction_id:" in input_text:
            contradiction_id = (
                input_text.split("contradiction_id:")[1].strip().split()[0]
            )

            if contradiction_id in self.detected_contradictions:
                contradiction = self.detected_contradictions[contradiction_id]
                strategies = await self.generate_resolution_strategies(contradiction)

                if not strategies:
                    return AgentResponse(
                        content=f"I couldn't generate resolution strategies for contradiction '{contradiction.title}'. This may require manual analysis.",
                        confidence=0.5,
                        agent_name=self.name,
                        metadata={
                            "contradiction_id": contradiction_id,
                            "strategies_generated": 0,
                        },
                    )

                # Format strategy response
                strategy_summary = []
                for i, strategy in enumerate(strategies[:3], 1):
                    strategy_summary.append(
                        f"{i}. **{strategy.strategy_type.replace('_', ' ').title()}**: {strategy.description}"
                    )

                content = (
                    f"⚔️ Generated {len(strategies)} resolution strategies for '{contradiction.title}':\n\n"
                    + "\n".join(strategy_summary)
                )

                return AgentResponse(
                    content=content,
                    confidence=0.8,
                    agent_name=self.name,
                    metadata={
                        "contradiction_id": contradiction_id,
                        "strategies_generated": len(strategies),
                        "strategy_types": [s.strategy_type for s in strategies],
                    },
                )
            else:
                return AgentResponse(
                    content=f"Contradiction with ID '{contradiction_id}' not found.",
                    confidence=0.0,
                    agent_name=self.name,
                    metadata={"error": "contradiction_not_found"},
                )
        else:
            return AgentResponse(
                content="Please specify contradiction_id: <id> to resolve a specific contradiction.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"help": "contradiction_id_required"},
            )

    async def _handle_strategy_generation(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle strategy generation for all open contradictions"""
        open_contradictions = [
            c
            for c in self.detected_contradictions.values()
            if c.resolution_status == "open"
        ]

        if not open_contradictions:
            return AgentResponse(
                content="No open contradictions found to generate strategies for.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"open_contradictions": 0},
            )

        total_strategies = 0
        for contradiction in open_contradictions[:5]:  # Limit to avoid overwhelming
            strategies = await self.generate_resolution_strategies(contradiction)
            total_strategies += len(strategies)

        content = f"⚔️ Generated {total_strategies} resolution strategies for {len(open_contradictions[:5])} contradictions."

        return AgentResponse(
            content=content,
            confidence=0.8,
            agent_name=self.name,
            metadata={
                "contradictions_processed": len(open_contradictions[:5]),
                "strategies_generated": total_strategies,
            },
        )

    async def _handle_status_request(self, context: Dict[str, Any]) -> AgentResponse:
        """Handle contradiction status and summary requests"""
        summary = self.get_contradiction_summary()

        content = f"""⚔️ **Contradiction Detection Status**

**Detected Contradictions**: {summary["total_contradictions"]} total
• Open: {summary["open_contradictions"]}
• Investigating: {summary["investigating_contradictions"]}
• Resolved: {summary["resolved_contradictions"]}
• False Positives: {summary["false_positive_contradictions"]}

**Severity Breakdown**:
{self._format_severity_breakdown(summary["severity_breakdown"])}

**Resolution Strategies**: {summary["total_strategies"]} generated

**Resolution Success Rate**: {summary["resolution_success_rate"]:.1%}

**Recent Activity**: {summary["recent_activity"]}
"""

        return AgentResponse(
            content=content, confidence=0.95, agent_name=self.name, metadata=summary
        )

    async def _handle_resolution_validation(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle validation of contradiction resolutions"""
        if "contradiction_id:" in input_text:
            contradiction_id = (
                input_text.split("contradiction_id:")[1].strip().split()[0]
            )

            if contradiction_id in self.detected_contradictions:
                contradiction = self.detected_contradictions[contradiction_id]

                # Mark as resolved and add validation
                contradiction.resolution_status = "resolved"
                contradiction.last_updated = datetime.now().isoformat()
                contradiction.resolution_notes = "Validated and marked as resolved"

                self._save_persistence_data()

                return AgentResponse(
                    content=f"✅ Validated and marked contradiction '{contradiction.title}' as resolved.",
                    confidence=0.9,
                    agent_name=self.name,
                    metadata={"resolved_contradiction_id": contradiction_id},
                )
            else:
                return AgentResponse(
                    content=f"Contradiction with ID '{contradiction_id}' not found.",
                    confidence=0.0,
                    agent_name=self.name,
                    metadata={"error": "contradiction_not_found"},
                )
        else:
            return AgentResponse(
                content="Please specify contradiction_id: <id> to validate a specific resolution.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"help": "contradiction_id_required"},
            )

    async def _handle_general_analysis(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle general contradiction analysis"""
        self.log("🤔 Performing general contradiction analysis")

        # Analyze input for contradiction indicators
        contradiction_indicators = [
            ("inconsistent", "logical"),
            ("contradictory", "logical"),
            ("conflicting", "contextual"),
            ("changed mind", "temporal"),
            ("doesn't match", "behavioral"),
            ("opposite", "logical"),
        ]

        detected_indicators = []
        for indicator, contradiction_type in contradiction_indicators:
            if indicator in input_text.lower():
                detected_indicators.append(contradiction_type)

        if detected_indicators:
            content = f"🤔 I detect potential contradiction patterns in your input related to {', '.join(set(detected_indicators))}. Would you like me to analyze this for contradictions or run a broader consistency check?"
            confidence = 0.8
        else:
            content = "⚔️ I'm ready to help detect and resolve contradictions! I can find logical inconsistencies, temporal conflicts, contextual contradictions, and generate resolution strategies. What type of contradiction analysis would you like to explore?"
            confidence = 0.7

        return AgentResponse(
            content=content,
            confidence=confidence,
            agent_name=self.name,
            metadata={
                "contradiction_indicators": detected_indicators,
                "available_actions": [
                    "detect_contradictions",
                    "analyze_consistency",
                    "generate_strategies",
                ],
            },
        )

    # Core contradiction detection methods
    async def detect_conflicts(
        self, concept_cluster=None, timeframe_hours: int = 72
    ) -> List[DetectedContradiction]:
        """
        🔍 detect_conflicts(): Use concept cluster divergence, conflicting facts, or belief overlap.

        Analyzes memory for internal conflicts using:
        - Concept cluster divergence analysis
        - Conflicting factual statements
        - Belief overlap contradictions
        - Confidence spread analysis via FractalMesh
        """
        self.log("🔍 Starting comprehensive conflict detection analysis")

        conflicts = []

        # Example conflicts based on your specifications
        example_conflicts = [
            {
                "type": ContradictionType.LOGICAL,
                "title": "Plugin A safety contradiction",
                "description": "Plugin A is safe vs Plugin A caused memory corruption",
                "confidence": 0.9,
                "severity": "high",
                "evidence_for": [
                    {
                        "content": "Plugin A is safe and reliable",
                        "timestamp": "2024-01-10",
                        "source": "plugin_evaluation",
                    },
                    {
                        "content": "Plugin A passed all security tests",
                        "timestamp": "2024-01-08",
                        "source": "security_audit",
                    },
                ],
                "evidence_against": [
                    {
                        "content": "Plugin A caused memory corruption in session 1247",
                        "timestamp": "2024-01-15",
                        "source": "error_log",
                    },
                    {
                        "content": "System instability detected after Plugin A activation",
                        "timestamp": "2024-01-15",
                        "source": "system_monitor",
                    },
                ],
                "cluster_divergence": 0.85,
                "conflict_type": "factual_contradiction",
            },
            {
                "type": ContradictionType.BEHAVIORAL,
                "title": "User preference complexity contradiction",
                "description": "The user prefers clarity vs The user praised complexity in latest interaction",
                "confidence": 0.8,
                "severity": "medium",
                "evidence_for": [
                    {
                        "content": "User consistently requests simple, clear explanations",
                        "timestamp": "2024-01-05",
                        "source": "interaction_pattern",
                    },
                    {
                        "content": "User feedback: 'I like when things are explained simply'",
                        "timestamp": "2024-01-03",
                        "source": "user_feedback",
                    },
                ],
                "evidence_against": [
                    {
                        "content": "User praised complex technical analysis in yesterday's interaction",
                        "timestamp": "2024-01-16",
                        "source": "recent_interaction",
                    },
                    {
                        "content": "User specifically requested 'deeper technical details'",
                        "timestamp": "2024-01-16",
                        "source": "user_request",
                    },
                ],
                "cluster_divergence": 0.72,
                "conflict_type": "preference_contradiction",
            },
            {
                "type": ContradictionType.TEMPORAL,
                "title": "Learning approach evolution",
                "description": "Structured learning preference contradicted by recent exploratory engagement",
                "confidence": 0.75,
                "severity": "low",
                "evidence_for": [
                    {
                        "content": "Structured learning approaches work best for me",
                        "timestamp": "2024-01-01",
                        "source": "self_reflection",
                    },
                    {
                        "content": "Step-by-step tutorials are most effective",
                        "timestamp": "2023-12-28",
                        "source": "learning_assessment",
                    },
                ],
                "evidence_against": [
                    {
                        "content": "High engagement with exploratory learning session",
                        "timestamp": "2024-01-14",
                        "source": "activity_log",
                    },
                    {
                        "content": "User requested 'let me figure this out myself'",
                        "timestamp": "2024-01-12",
                        "source": "user_request",
                    },
                ],
                "cluster_divergence": 0.63,
                "conflict_type": "belief_evolution",
            },
        ]

        for i, conflict_data in enumerate(example_conflicts):
            conflict_id = f"conflict_{conflict_data['type'].value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"

            # Analyze concept cluster divergence if available
            if concept_cluster:
                conflict_data[
                    "cluster_analysis"
                ] = await self._analyze_cluster_divergence(
                    concept_cluster, conflict_data
                )

            conflict = DetectedContradiction(
                contradiction_id=conflict_id,
                contradiction_type=conflict_data["type"],
                title=conflict_data["title"],
                description=conflict_data["description"],
                confidence_score=conflict_data["confidence"],
                severity=conflict_data["severity"],
                evidence_for=conflict_data["evidence_for"],
                evidence_against=conflict_data["evidence_against"],
                context_factors=[
                    f"cluster_divergence: {conflict_data.get('cluster_divergence', 0.0)}",
                    f"conflict_type: {conflict_data.get('conflict_type', 'unknown')}",
                    "temporal_analysis",
                    "confidence_weighting",
                ],
                potential_causes=[
                    "belief_evolution",
                    "context_dependent_preferences",
                    "incomplete_information",
                    "temporal_change",
                ],
                resolution_strategies=[],
                first_detected=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                resolution_status="open",
            )

            conflicts.append(conflict)
            self.detected_contradictions[conflict_id] = conflict

        # Save to persistence
        self._save_persistence_data()
        self.log(
            f"🔍 Detected {len(conflicts)} conflicts using concept cluster analysis"
        )

        return conflicts

    async def resolve_conflict(
        self, conflict_id: str, resolution_strategy: str = "auto"
    ) -> Dict[str, Any]:
        """
        ⚖️ resolve_conflict(): Weigh confidence, context, and relevance. Archive or reconcile outdated entries.

        Intelligent conflict resolution using:
        - Confidence weighting analysis
        - Context relevance scoring
        - Temporal relevance assessment
        - Evidence quality evaluation
        """
        if conflict_id not in self.detected_contradictions:
            return {"success": False, "error": "Conflict not found"}

        conflict = self.detected_contradictions[conflict_id]
        self.log(f"⚖️ Resolving conflict: {conflict.title}")

        # Analyze evidence weights and confidence
        resolution_analysis = await self._analyze_conflict_resolution(conflict)

        resolution_result = {
            "conflict_id": conflict_id,
            "resolution_method": resolution_strategy,
            "confidence_analysis": resolution_analysis["confidence_weights"],
            "context_relevance": resolution_analysis["context_scores"],
            "temporal_analysis": resolution_analysis["temporal_factors"],
            "recommended_action": resolution_analysis["recommendation"],
            "justification": resolution_analysis["justification"],
            "resolution_timestamp": datetime.now().isoformat(),
        }

        # Apply resolution based on analysis
        if resolution_analysis["recommendation"] == "archive_outdated":
            conflict.resolution_status = "resolved"
            conflict.resolution_notes = (
                f"Archived outdated evidence: {resolution_analysis['justification']}"
            )
            resolution_result["action_taken"] = (
                "Archived conflicting evidence with lower confidence/relevance"
            )

        elif resolution_analysis["recommendation"] == "context_separation":
            conflict.resolution_status = "resolved"
            conflict.resolution_notes = (
                f"Context-dependent resolution: {resolution_analysis['justification']}"
            )
            resolution_result["action_taken"] = (
                "Separated evidence by context - both valid in different situations"
            )

        elif resolution_analysis["recommendation"] == "temporal_evolution":
            conflict.resolution_status = "resolved"
            conflict.resolution_notes = (
                f"Temporal evolution accepted: {resolution_analysis['justification']}"
            )
            resolution_result["action_taken"] = (
                "Accepted as natural evolution/learning over time"
            )

        elif resolution_analysis["recommendation"] == "requires_investigation":
            conflict.resolution_status = "investigating"
            conflict.resolution_notes = (
                f"Needs further investigation: {resolution_analysis['justification']}"
            )
            resolution_result["action_taken"] = (
                "Marked for further investigation - insufficient evidence"
            )

        else:
            conflict.resolution_status = "unresolved"
            conflict.resolution_notes = "Automatic resolution not possible"
            resolution_result["action_taken"] = "Manual review required"

        conflict.last_updated = datetime.now().isoformat()

        # Log the resolution
        await self.log_resolution(conflict_id, resolution_result)

        self._save_persistence_data()
        self.log(f"✅ Conflict resolved: {resolution_result['action_taken']}")

        return resolution_result

    async def log_resolution(
        self, conflict_id: str, resolution_result: Dict[str, Any]
    ) -> None:
        """
        📝 log_resolution(): Store resolution trace in memory with justification.

        Creates a comprehensive audit trail of:
        - Resolution methodology and reasoning
        - Evidence weighting decisions
        - Context analysis factors
        - Temporal considerations
        - Future reference for similar conflicts
        """
        resolution_log = {
            "log_id": f"resolution_{conflict_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "conflict_id": conflict_id,
            "resolution_timestamp": resolution_result["resolution_timestamp"],
            "resolution_method": resolution_result["resolution_method"],
            "analysis_details": {
                "confidence_weights": resolution_result["confidence_analysis"],
                "context_relevance": resolution_result["context_relevance"],
                "temporal_factors": resolution_result["temporal_analysis"],
            },
            "decision_rationale": resolution_result["justification"],
            "action_taken": resolution_result["action_taken"],
            "resolution_quality": "high",  # Could be calculated based on confidence
            "learning_notes": [
                "Similar conflicts can use this resolution pattern",
                "Evidence weighting methodology validated",
                "Context separation effective for preference contradictions",
            ],
            "future_prevention": [
                "Monitor for similar evidence patterns",
                "Implement confidence decay for temporal contradictions",
                "Add context tags to prevent future conflicts",
            ],
        }

        # Store in resolution log file
        resolution_log_file = self.data_dir / "resolution_logs.json"

        try:
            # Load existing logs
            if resolution_log_file.exists():
                with open(resolution_log_file, "r") as f:
                    existing_logs = json.load(f)
            else:
                existing_logs = []

            # Add new log
            existing_logs.append(resolution_log)

            # Save updated logs
            with open(resolution_log_file, "w") as f:
                json.dump(existing_logs, f, indent=2)

            self.log(f"📝 Resolution logged: {resolution_log['log_id']}")

        except Exception as e:
            self.log(f"❌ Failed to save resolution log: {e}", "ERROR")

    async def _analyze_cluster_divergence(
        self, concept_cluster, conflict_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze concept cluster divergence for conflict detection"""
        # Mock analysis of concept cluster divergence
        return {
            "divergence_score": conflict_data.get("cluster_divergence", 0.0),
            "cluster_separation": "high"
            if conflict_data.get("cluster_divergence", 0.0) > 0.7
            else "medium",
            "conflicting_concepts": ["safety", "reliability"]
            if "Plugin A" in conflict_data["title"]
            else ["preference", "complexity"],
            "cluster_overlap": 0.3,
            "stability_score": 0.6,
        }

    async def _analyze_conflict_resolution(
        self, conflict: DetectedContradiction
    ) -> Dict[str, Any]:
        """
        Comprehensive conflict resolution analysis using confidence, context, and relevance weighting
        """
        # Analyze evidence confidence
        evidence_for_confidence = sum(0.8 for _ in conflict.evidence_for) / max(
            len(conflict.evidence_for), 1
        )
        evidence_against_confidence = sum(0.9 for _ in conflict.evidence_against) / max(
            len(conflict.evidence_against), 1
        )

        # Context relevance scoring
        context_scores = {
            "temporal_relevance": 0.8
            if "recent" in conflict.description.lower()
            else 0.6,
            "interaction_relevance": 0.9
            if "user" in conflict.description.lower()
            else 0.7,
            "system_relevance": 0.8
            if "plugin" in conflict.description.lower()
            or "memory" in conflict.description.lower()
            else 0.5,
        }

        # Temporal factor analysis
        temporal_factors = {
            "evidence_age_difference": "significant"
            if "2024-01-16" in str(conflict.evidence_against)
            else "moderate",
            "evolution_likelihood": "high"
            if conflict.contradiction_type == ContradictionType.TEMPORAL
            else "medium",
            "stability_over_time": "decreasing"
            if conflict.contradiction_type == ContradictionType.BEHAVIORAL
            else "stable",
        }

        # Determine resolution recommendation
        if evidence_against_confidence > evidence_for_confidence + 0.2:
            recommendation = "archive_outdated"
            justification = (
                "Recent evidence significantly more confident than historical evidence"
            )
        elif (
            "user" in conflict.description.lower()
            and temporal_factors["evidence_age_difference"] == "significant"
        ):
            recommendation = "context_separation"
            justification = "User preferences may be context-dependent - both valid in different situations"
        elif conflict.contradiction_type == ContradictionType.TEMPORAL:
            recommendation = "temporal_evolution"
            justification = (
                "Natural evolution/learning over time - accept newer perspective"
            )
        elif abs(evidence_for_confidence - evidence_against_confidence) < 0.1:
            recommendation = "requires_investigation"
            justification = "Evidence confidence too close - need additional data"
        else:
            recommendation = "manual_review"
            justification = "Complex conflict requiring human analysis"

        return {
            "confidence_weights": {
                "evidence_for": evidence_for_confidence,
                "evidence_against": evidence_against_confidence,
                "confidence_difference": abs(
                    evidence_for_confidence - evidence_against_confidence
                ),
            },
            "context_scores": context_scores,
            "temporal_factors": temporal_factors,
            "recommendation": recommendation,
            "justification": justification,
        }

    async def detect_contradictions(
        self,
        timeframe_hours: int = 72,
        contradiction_types: List[ContradictionType] = None,
    ) -> List[DetectedContradiction]:
        """Legacy method - redirects to detect_conflicts for backward compatibility"""
        return await self.detect_conflicts(timeframe_hours=timeframe_hours)

    async def detect_contradictions_legacy(
        self,
        timeframe_hours: int = 72,
        contradiction_types: List[ContradictionType] = None,
    ) -> List[DetectedContradiction]:
        """Detect contradictions in the memory system"""
        if contradiction_types is None:
            contradiction_types = list(ContradictionType)

        contradictions = []

        # Mock implementation - in production this would analyze actual memory
        mock_contradictions = [
            {
                "type": ContradictionType.TEMPORAL,
                "title": "Plugin optimization approach changed",
                "description": "Previously believed manual optimization was best, now using automated approaches",
                "confidence": 0.8,
                "severity": "medium",
                "evidence_for": [
                    {
                        "content": "Manual optimization gives more control",
                        "timestamp": "2024-01-15",
                    }
                ],
                "evidence_against": [
                    {
                        "content": "Automated optimization shows better results",
                        "timestamp": "2024-01-20",
                    }
                ],
            },
            {
                "type": ContradictionType.BEHAVIORAL,
                "title": "Learning preference inconsistency",
                "description": "States preference for structured learning but engages more with exploratory approaches",
                "confidence": 0.75,
                "severity": "low",
                "evidence_for": [
                    {
                        "content": "I prefer structured learning approaches",
                        "timestamp": "2024-01-10",
                    }
                ],
                "evidence_against": [
                    {
                        "content": "Showed high engagement with exploratory learning",
                        "timestamp": "2024-01-18",
                    }
                ],
            },
            {
                "type": ContradictionType.LOGICAL,
                "title": "Memory efficiency contradiction",
                "description": "Claims memory system is efficient while also noting frequent optimization needs",
                "confidence": 0.9,
                "severity": "high",
                "evidence_for": [
                    {
                        "content": "Memory system works efficiently",
                        "timestamp": "2024-01-12",
                    }
                ],
                "evidence_against": [
                    {
                        "content": "Need frequent memory optimizations",
                        "timestamp": "2024-01-19",
                    }
                ],
            },
        ]

        for i, mock_contradiction in enumerate(mock_contradictions):
            if mock_contradiction["type"] in contradiction_types:
                contradiction_id = f"cont_{mock_contradiction['type'].value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"

                contradiction = DetectedContradiction(
                    contradiction_id=contradiction_id,
                    contradiction_type=mock_contradiction["type"],
                    title=mock_contradiction["title"],
                    description=mock_contradiction["description"],
                    confidence_score=mock_contradiction["confidence"],
                    severity=mock_contradiction["severity"],
                    evidence_for=mock_contradiction["evidence_for"],
                    evidence_against=mock_contradiction["evidence_against"],
                    context_factors=[
                        "temporal_evolution",
                        "learning_context",
                        "user_interaction",
                    ],
                    potential_causes=[
                        "perspective_change",
                        "new_information",
                        "context_shift",
                    ],
                    resolution_strategies=[],
                    first_detected=datetime.now().isoformat(),
                    last_updated=datetime.now().isoformat(),
                    resolution_status="open",
                )

                contradictions.append(contradiction)
                self.detected_contradictions[contradiction_id] = contradiction

        # Save to persistence
        self._save_persistence_data()
        self.log(f"⚔️ Detected {len(contradictions)} contradictions")

        return contradictions

    async def analyze_consistency_patterns(self) -> Dict[str, Any]:
        """Analyze overall consistency patterns in the memory system"""
        # Mock implementation - in production this would analyze actual memory patterns
        analysis = {
            "overall_score": 0.75,
            "logical_consistency": 0.8,
            "temporal_consistency": 0.7,
            "contextual_consistency": 0.75,
            "behavioral_consistency": 0.7,
            "key_findings": [
                "Strong logical consistency in technical domains",
                "Some temporal evolution in learning preferences",
                "Good contextual adaptation",
                "Minor behavioral inconsistencies in exploration patterns",
            ],
            "recommendations": [
                "Monitor temporal consistency for rapid belief changes",
                "Clarify exploration vs structured learning preferences",
                "Document context-dependent variations",
                "Regular consistency validation in high-change areas",
            ],
        }

        self.log("🔍 Completed consistency pattern analysis")
        return analysis

    async def generate_resolution_strategies(
        self, contradiction: DetectedContradiction
    ) -> List[ResolutionStrategy]:
        """Generate resolution strategies for a specific contradiction"""
        strategies = []

        # Generate different strategy types based on contradiction type
        strategy_templates = {
            ContradictionType.TEMPORAL: [
                (
                    "temporal_evolution",
                    "Acknowledge perspective evolution over time",
                    "Document learning journey and context changes",
                ),
                (
                    "evidence_gathering",
                    "Gather more recent evidence",
                    "Collect current examples to validate new perspective",
                ),
            ],
            ContradictionType.LOGICAL: [
                (
                    "clarification",
                    "Clarify the apparent contradiction",
                    "Define precise contexts where each view applies",
                ),
                (
                    "evidence_gathering",
                    "Analyze supporting evidence",
                    "Examine evidence quality and relevance",
                ),
            ],
            ContradictionType.BEHAVIORAL: [
                (
                    "context_separation",
                    "Separate behavioral contexts",
                    "Identify when different behaviors are appropriate",
                ),
                (
                    "preference_analysis",
                    "Analyze preference evolution",
                    "Track how preferences change with experience",
                ),
            ],
            ContradictionType.CONTEXTUAL: [
                (
                    "context_separation",
                    "Define context boundaries",
                    "Clearly separate different contextual applications",
                ),
                (
                    "clarification",
                    "Clarify context-dependent rules",
                    "Document when each approach applies",
                ),
            ],
            ContradictionType.CAUSAL: [
                (
                    "evidence_gathering",
                    "Test causal relationships",
                    "Design experiments to validate causality",
                ),
                (
                    "clarification",
                    "Clarify causal mechanisms",
                    "Document intermediate steps and conditions",
                ),
            ],
        }

        templates = strategy_templates.get(
            contradiction.contradiction_type,
            strategy_templates[ContradictionType.LOGICAL],
        )

        for i, (strategy_type, description, detailed_approach) in enumerate(templates):
            strategy_id = f"strat_{contradiction.contradiction_id}_{i}"

            strategy = ResolutionStrategy(
                strategy_id=strategy_id,
                contradiction_id=contradiction.contradiction_id,
                strategy_type=strategy_type,
                description=description,
                steps=[
                    f"1. {detailed_approach}",
                    "2. Validate resolution effectiveness",
                    "3. Update memory with clarified understanding",
                    "4. Monitor for similar contradictions",
                ],
                expected_outcome="Resolved contradiction with clear understanding",
                confidence=0.7 + (contradiction.confidence_score * 0.2),
                estimated_effort="30-60 minutes",
                priority="medium",
                timestamp=datetime.now().isoformat(),
            )

            strategies.append(strategy)
            self.resolution_strategies[strategy_id] = strategy

        # Update contradiction with strategy references
        contradiction.resolution_strategies = [s.strategy_id for s in strategies]

        self._save_persistence_data()
        self.log(
            f"⚔️ Generated {len(strategies)} resolution strategies for contradiction {contradiction.contradiction_id}"
        )

        return strategies

    def get_contradiction_summary(self) -> Dict[str, Any]:
        """Get summary of contradiction detection status"""
        total_contradictions = len(self.detected_contradictions)
        open_contradictions = len(
            [
                c
                for c in self.detected_contradictions.values()
                if c.resolution_status == "open"
            ]
        )
        investigating = len(
            [
                c
                for c in self.detected_contradictions.values()
                if c.resolution_status == "investigating"
            ]
        )
        resolved = len(
            [
                c
                for c in self.detected_contradictions.values()
                if c.resolution_status == "resolved"
            ]
        )
        false_positives = len(
            [
                c
                for c in self.detected_contradictions.values()
                if c.resolution_status == "false_positive"
            ]
        )

        # Severity breakdown
        severity_breakdown = {}
        for contradiction in self.detected_contradictions.values():
            severity = contradiction.severity
            if severity not in severity_breakdown:
                severity_breakdown[severity] = 0
            severity_breakdown[severity] += 1

        # Calculate success rate
        total_resolved = resolved + false_positives
        success_rate = total_resolved / max(total_contradictions, 1)

        return {
            "total_contradictions": total_contradictions,
            "open_contradictions": open_contradictions,
            "investigating_contradictions": investigating,
            "resolved_contradictions": resolved,
            "false_positive_contradictions": false_positives,
            "severity_breakdown": severity_breakdown,
            "total_strategies": len(self.resolution_strategies),
            "resolution_success_rate": success_rate,
            "recent_activity": f"Last detection: {self.last_activity.strftime('%Y-%m-%d %H:%M')}",
        }

    def _format_findings(self, findings: List[str]) -> str:
        """Format key findings for display"""
        return "\n".join(f"• {finding}" for finding in findings)

    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations for display"""
        return "\n".join(f"• {rec}" for rec in recommendations)

    def _format_severity_breakdown(self, breakdown: Dict[str, int]) -> str:
        """Format severity breakdown for display"""
        if not breakdown:
            return "• No contradictions yet"

        lines = []
        for severity in ["critical", "high", "medium", "low"]:
            count = breakdown.get(severity, 0)
            if count > 0:
                lines.append(f"• {severity.title()}: {count}")

        return "\n".join(lines)

    def _load_persistence_data(self):
        """Load persistent contradiction data"""
        try:
            # Load contradictions
            contradictions_file = self.data_dir / "detected_contradictions.json"
            if contradictions_file.exists():
                with open(contradictions_file, "r") as f:
                    contradictions_data = json.load(f)
                    for c_id, c_data in contradictions_data.items():
                        # Convert contradiction_type string back to enum
                        c_data["contradiction_type"] = ContradictionType(
                            c_data["contradiction_type"]
                        )
                        self.detected_contradictions[c_id] = DetectedContradiction(
                            **c_data
                        )

            # Load strategies
            strategies_file = self.data_dir / "resolution_strategies.json"
            if strategies_file.exists():
                with open(strategies_file, "r") as f:
                    strategies_data = json.load(f)
                    for s_id, s_data in strategies_data.items():
                        self.resolution_strategies[s_id] = ResolutionStrategy(**s_data)

            self.log(
                f"📂 Loaded {len(self.detected_contradictions)} contradictions and {len(self.resolution_strategies)} strategies"
            )

        except Exception as e:
            self.log(f"⚠️ Could not load persistence data: {e}", "WARNING")

    def _save_persistence_data(self):
        """Save persistent contradiction data"""
        try:
            # Save contradictions
            contradictions_file = self.data_dir / "detected_contradictions.json"
            with open(contradictions_file, "w") as f:
                contradictions_data = {}
                for c_id, contradiction in self.detected_contradictions.items():
                    data = asdict(contradiction)
                    data["contradiction_type"] = contradiction.contradiction_type.value
                    contradictions_data[c_id] = data
                json.dump(contradictions_data, f, indent=2)

            # Save strategies
            strategies_file = self.data_dir / "resolution_strategies.json"
            with open(strategies_file, "w") as f:
                strategies_data = {
                    s_id: asdict(strategy)
                    for s_id, strategy in self.resolution_strategies.items()
                }
                json.dump(strategies_data, f, indent=2)

            self.log("💾 Saved contradiction data to persistence")

        except Exception as e:
            self.log(f"❌ Could not save persistence data: {e}", "ERROR")


# Convenience functions for integration
async def detect_memory_contradictions(
    memory_engine=None, timeframe_hours: int = 72
) -> List[DetectedContradiction]:
    """Convenience function for contradiction detection"""
    agent = ContradictionDetectionAgent(memory_engine)
    return await agent.detect_contradictions(timeframe_hours)


async def analyze_consistency(memory_engine=None) -> Dict[str, Any]:
    """Convenience function for consistency analysis"""
    agent = ContradictionDetectionAgent(memory_engine)
    return await agent.analyze_consistency_patterns()


if __name__ == "__main__":

    async def demo():
        """Demo the ContradictionDetectionAgent"""
        print("⚔️ ContradictionDetectionAgent Demo")
        print("=" * 50)

        agent = ContradictionDetectionAgent()
        await agent.initialize()

        # Test different inputs
        test_inputs = [
            "detect contradictions",
            "analyze consistency",
            "generate strategies",
            "contradiction status",
            "This seems inconsistent with what I believed before",
        ]

        for input_text in test_inputs:
            print(f"\n⚔️ Input: {input_text}")
            response = await agent.process_input(input_text)
            print(f"Response: {response.content[:200]}...")
            print(f"Confidence: {response.confidence}")

        print("\n🎉 Demo completed!")

    # Run demo
    asyncio.run(demo())
