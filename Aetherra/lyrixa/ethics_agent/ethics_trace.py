#!/usr/bin/env python3
"""
📝 ETHICS TRACE - Ethical Decision Audit Trail System
===================================================

Creates comprehensive audit trails for all ethical decisions and reasoning.
Provides transparency and accountability for moral decision making.

Key Features:
• Complete decision history tracking
• Reasoning chain documentation
• Stakeholder impact analysis
• Decision outcome monitoring
• Ethical precedent linkage
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import ethics components
try:
    from .bias_detector import BiasDetection
    from .moral_reasoning import EthicalEvaluation, EthicalFramework, MoralDecision
    from .value_alignment import CoreValue, ValueAssessment
except ImportError:
    print("⚠️ Using local import paths for ethics trace")
    import sys

    sys.path.append(".")


class DecisionStatus(Enum):
    """Status of ethical decisions"""

    PENDING = "pending"  # Under consideration
    APPROVED = "approved"  # Approved for implementation
    REJECTED = "rejected"  # Rejected due to ethical concerns
    IMPLEMENTED = "implemented"  # Actually implemented
    REVIEWED = "reviewed"  # Post-implementation review completed
    REVERSED = "reversed"  # Decision was reversed
    MODIFIED = "modified"  # Decision was modified


class ImpactLevel(Enum):
    """Level of decision impact"""

    MINIMAL = "minimal"  # Very limited impact
    LIMITED = "limited"  # Small scope impact
    MODERATE = "moderate"  # Medium scope impact
    SIGNIFICANT = "significant"  # Large scope impact
    CRITICAL = "critical"  # System-wide impact


@dataclass
class StakeholderImpact:
    """Impact on specific stakeholder"""

    stakeholder_type: str
    impact_description: str
    impact_level: ImpactLevel
    positive_effects: List[str]
    negative_effects: List[str]
    mitigation_measures: List[str]


@dataclass
class DecisionOutcome:
    """Actual outcome of implemented decision"""

    outcome_id: str
    decision_id: str
    implementation_date: str
    actual_effects: List[str]
    unexpected_consequences: List[str]
    stakeholder_feedback: List[Dict[str, Any]]
    success_metrics: Dict[str, float]
    lessons_learned: List[str]
    follow_up_actions: List[str]


@dataclass
class EthicsTraceEntry:
    """Complete ethical decision trace entry"""

    trace_id: str
    decision_context: str
    decision_description: str
    decision_type: str
    status: DecisionStatus

    # Reasoning components
    moral_evaluation: Optional[EthicalEvaluation]
    value_assessment: Optional[ValueAssessment]
    bias_detections: List[BiasDetection]

    # Impact analysis
    stakeholder_impacts: List[StakeholderImpact]
    predicted_outcomes: List[str]
    risk_assessment: Dict[str, Any]

    # Decision metadata
    decision_maker: str
    decision_timestamp: str
    implementation_deadline: Optional[str]
    review_schedule: Optional[str]

    # Tracking
    related_decisions: List[str]
    precedent_references: List[str]
    outcome_record: Optional[DecisionOutcome]

    # Updates
    status_updates: List[Dict[str, Any]]
    modification_history: List[Dict[str, Any]]


class EthicsTraceSystem:
    """
    Comprehensive ethical decision audit trail system
    """

    def __init__(self, data_dir: str = "ethics_trace_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Trace storage
        self.trace_entries: Dict[str, EthicsTraceEntry] = {}
        self.decision_outcomes: Dict[str, DecisionOutcome] = {}

        # Indexing for fast retrieval
        self.decisions_by_type: Dict[str, List[str]] = {}
        self.decisions_by_status: Dict[DecisionStatus, List[str]] = {}
        self.decisions_by_date: Dict[str, List[str]] = {}

        # Load existing traces
        self._load_trace_database()

        print("📝 EthicsTraceSystem initialized with comprehensive audit capabilities")

    def _load_trace_database(self):
        """Load existing trace database"""
        trace_file = self.data_dir / "ethics_traces.json"
        if trace_file.exists():
            try:
                with open(trace_file, "r") as f:
                    trace_data = json.load(f)

                # Reconstruct trace entries
                for trace_id, entry_data in trace_data.items():
                    trace_entry = self._reconstruct_trace_entry(entry_data)
                    self.trace_entries[trace_id] = trace_entry
                    self._update_indexes(trace_entry)

                print(f"   📚 Loaded {len(self.trace_entries)} ethics trace entries")
            except Exception as e:
                print(f"   ⚠️ Error loading trace database: {e}")

    def _reconstruct_trace_entry(self, entry_data: Dict[str, Any]) -> EthicsTraceEntry:
        """Reconstruct EthicsTraceEntry from stored data"""
        # Reconstruct moral evaluation if present
        moral_eval = None
        if entry_data.get("moral_evaluation"):
            eval_data = entry_data["moral_evaluation"]
            moral_eval = EthicalEvaluation(
                decision=MoralDecision(eval_data["decision"]),
                confidence=eval_data["confidence"],
                explanation=eval_data["explanation"],
                framework_scores={
                    EthicalFramework(k): v
                    for k, v in eval_data["framework_scores"].items()
                },
                principle_scores=eval_data["principle_scores"],  # Simplified for demo
                conflicts_identified=eval_data["conflicts_identified"],
                recommendations=eval_data["recommendations"],
                precedent_citations=eval_data["precedent_citations"],
                evaluation_timestamp=eval_data["evaluation_timestamp"],
            )

        # Reconstruct value assessment if present
        value_assess = None
        if entry_data.get("value_assessment"):
            assess_data = entry_data["value_assessment"]
            # Simplified reconstruction for demo
            value_assess = None  # Would reconstruct ValueAssessment object

        # Reconstruct bias detections
        bias_detections = []
        for bias_data in entry_data.get("bias_detections", []):
            # Simplified reconstruction for demo
            pass

        # Reconstruct stakeholder impacts
        stakeholder_impacts = []
        for impact_data in entry_data.get("stakeholder_impacts", []):
            impact = StakeholderImpact(
                stakeholder_type=impact_data["stakeholder_type"],
                impact_description=impact_data["impact_description"],
                impact_level=ImpactLevel(impact_data["impact_level"]),
                positive_effects=impact_data["positive_effects"],
                negative_effects=impact_data["negative_effects"],
                mitigation_measures=impact_data["mitigation_measures"],
            )
            stakeholder_impacts.append(impact)

        # Reconstruct outcome record if present
        outcome_record = None
        if entry_data.get("outcome_record"):
            outcome_data = entry_data["outcome_record"]
            outcome_record = DecisionOutcome(
                outcome_id=outcome_data["outcome_id"],
                decision_id=outcome_data["decision_id"],
                implementation_date=outcome_data["implementation_date"],
                actual_effects=outcome_data["actual_effects"],
                unexpected_consequences=outcome_data["unexpected_consequences"],
                stakeholder_feedback=outcome_data["stakeholder_feedback"],
                success_metrics=outcome_data["success_metrics"],
                lessons_learned=outcome_data["lessons_learned"],
                follow_up_actions=outcome_data["follow_up_actions"],
            )

        return EthicsTraceEntry(
            trace_id=entry_data["trace_id"],
            decision_context=entry_data["decision_context"],
            decision_description=entry_data["decision_description"],
            decision_type=entry_data["decision_type"],
            status=DecisionStatus(entry_data["status"]),
            moral_evaluation=moral_eval,
            value_assessment=value_assess,
            bias_detections=bias_detections,
            stakeholder_impacts=stakeholder_impacts,
            predicted_outcomes=entry_data["predicted_outcomes"],
            risk_assessment=entry_data["risk_assessment"],
            decision_maker=entry_data["decision_maker"],
            decision_timestamp=entry_data["decision_timestamp"],
            implementation_deadline=entry_data.get("implementation_deadline"),
            review_schedule=entry_data.get("review_schedule"),
            related_decisions=entry_data["related_decisions"],
            precedent_references=entry_data["precedent_references"],
            outcome_record=outcome_record,
            status_updates=entry_data["status_updates"],
            modification_history=entry_data["modification_history"],
        )

    async def create_ethics_trace(
        self,
        decision_context: str,
        decision_description: str,
        decision_type: str,
        decision_maker: str = "system",
        stakeholders: Optional[List[str]] = None,
        predicted_outcomes: Optional[List[str]] = None,
        implementation_deadline: Optional[str] = None,
    ) -> str:
        """Create new ethics trace entry"""

        trace_id = str(uuid.uuid4())

        print(f"📝 Creating ethics trace: {trace_id[:8]}...")
        print(f"   • Decision: {decision_description[:50]}...")
        print(f"   • Context: {decision_context}")

        # Initialize stakeholder impacts
        stakeholder_impacts = []
        if stakeholders:
            for stakeholder in stakeholders:
                impact = StakeholderImpact(
                    stakeholder_type=stakeholder,
                    impact_description=f"Impact analysis pending for {stakeholder}",
                    impact_level=ImpactLevel.MODERATE,
                    positive_effects=[],
                    negative_effects=[],
                    mitigation_measures=[],
                )
                stakeholder_impacts.append(impact)

        # Create trace entry
        trace_entry = EthicsTraceEntry(
            trace_id=trace_id,
            decision_context=decision_context,
            decision_description=decision_description,
            decision_type=decision_type,
            status=DecisionStatus.PENDING,
            moral_evaluation=None,  # To be added via separate methods
            value_assessment=None,  # To be added via separate methods
            bias_detections=[],  # To be added via separate methods
            stakeholder_impacts=stakeholder_impacts,
            predicted_outcomes=predicted_outcomes or [],
            risk_assessment={},  # To be populated
            decision_maker=decision_maker,
            decision_timestamp=datetime.now().isoformat(),
            implementation_deadline=implementation_deadline,
            review_schedule=None,
            related_decisions=[],
            precedent_references=[],
            outcome_record=None,
            status_updates=[],
            modification_history=[],
        )

        # Store trace entry
        self.trace_entries[trace_id] = trace_entry
        self._update_indexes(trace_entry)
        await self._save_trace_database()

        print(f"   ✅ Ethics trace created successfully")
        return trace_id

    async def add_moral_evaluation(
        self, trace_id: str, moral_evaluation: EthicalEvaluation
    ):
        """Add moral evaluation to existing trace"""
        if trace_id not in self.trace_entries:
            raise ValueError(f"Trace ID {trace_id} not found")

        trace_entry = self.trace_entries[trace_id]
        trace_entry.moral_evaluation = moral_evaluation

        # Update status based on moral decision
        if moral_evaluation.decision == MoralDecision.ALLOW:
            await self._update_status(
                trace_id, DecisionStatus.APPROVED, "Approved based on moral evaluation"
            )
        elif moral_evaluation.decision == MoralDecision.REJECT:
            await self._update_status(
                trace_id, DecisionStatus.REJECTED, "Rejected based on moral evaluation"
            )

        await self._save_trace_database()
        print(f"   📋 Added moral evaluation to trace {trace_id[:8]}")

    async def add_value_assessment(
        self, trace_id: str, value_assessment: ValueAssessment
    ):
        """Add value assessment to existing trace"""
        if trace_id not in self.trace_entries:
            raise ValueError(f"Trace ID {trace_id} not found")

        trace_entry = self.trace_entries[trace_id]
        trace_entry.value_assessment = value_assessment

        await self._save_trace_database()
        print(f"   🎯 Added value assessment to trace {trace_id[:8]}")

    async def add_bias_detection(self, trace_id: str, bias_detection: BiasDetection):
        """Add bias detection result to existing trace"""
        if trace_id not in self.trace_entries:
            raise ValueError(f"Trace ID {trace_id} not found")

        trace_entry = self.trace_entries[trace_id]
        trace_entry.bias_detections.append(bias_detection)

        await self._save_trace_database()
        print(f"   ⚖️ Added bias detection to trace {trace_id[:8]}")

    async def update_stakeholder_impact(
        self,
        trace_id: str,
        stakeholder_type: str,
        impact_description: str,
        impact_level: ImpactLevel,
        positive_effects: List[str],
        negative_effects: List[str],
        mitigation_measures: List[str],
    ):
        """Update stakeholder impact analysis"""
        if trace_id not in self.trace_entries:
            raise ValueError(f"Trace ID {trace_id} not found")

        trace_entry = self.trace_entries[trace_id]

        # Find existing stakeholder impact or create new one
        existing_impact = None
        for impact in trace_entry.stakeholder_impacts:
            if impact.stakeholder_type == stakeholder_type:
                existing_impact = impact
                break

        if existing_impact:
            existing_impact.impact_description = impact_description
            existing_impact.impact_level = impact_level
            existing_impact.positive_effects = positive_effects
            existing_impact.negative_effects = negative_effects
            existing_impact.mitigation_measures = mitigation_measures
        else:
            new_impact = StakeholderImpact(
                stakeholder_type=stakeholder_type,
                impact_description=impact_description,
                impact_level=impact_level,
                positive_effects=positive_effects,
                negative_effects=negative_effects,
                mitigation_measures=mitigation_measures,
            )
            trace_entry.stakeholder_impacts.append(new_impact)

        await self._save_trace_database()
        print(
            f"   👥 Updated stakeholder impact for {stakeholder_type} in trace {trace_id[:8]}"
        )

    async def record_decision_outcome(
        self,
        trace_id: str,
        actual_effects: List[str],
        unexpected_consequences: List[str],
        stakeholder_feedback: List[Dict[str, Any]],
        success_metrics: Dict[str, float],
        lessons_learned: List[str],
    ):
        """Record actual outcome of implemented decision"""
        if trace_id not in self.trace_entries:
            raise ValueError(f"Trace ID {trace_id} not found")

        outcome_id = str(uuid.uuid4())

        outcome = DecisionOutcome(
            outcome_id=outcome_id,
            decision_id=trace_id,
            implementation_date=datetime.now().isoformat(),
            actual_effects=actual_effects,
            unexpected_consequences=unexpected_consequences,
            stakeholder_feedback=stakeholder_feedback,
            success_metrics=success_metrics,
            lessons_learned=lessons_learned,
            follow_up_actions=[],
        )

        trace_entry = self.trace_entries[trace_id]
        trace_entry.outcome_record = outcome

        # Update status
        await self._update_status(
            trace_id, DecisionStatus.REVIEWED, "Outcome recorded and reviewed"
        )

        self.decision_outcomes[outcome_id] = outcome
        await self._save_trace_database()

        print(f"   📊 Recorded decision outcome for trace {trace_id[:8]}")

    async def _update_status(
        self, trace_id: str, new_status: DecisionStatus, reason: str
    ):
        """Update decision status with audit trail"""
        if trace_id not in self.trace_entries:
            raise ValueError(f"Trace ID {trace_id} not found")

        trace_entry = self.trace_entries[trace_id]
        old_status = trace_entry.status

        trace_entry.status = new_status
        trace_entry.status_updates.append(
            {
                "timestamp": datetime.now().isoformat(),
                "old_status": old_status.value,
                "new_status": new_status.value,
                "reason": reason,
                "updated_by": "system",
            }
        )

        # Update indexes
        if old_status in self.decisions_by_status:
            if trace_id in self.decisions_by_status[old_status]:
                self.decisions_by_status[old_status].remove(trace_id)

        if new_status not in self.decisions_by_status:
            self.decisions_by_status[new_status] = []
        self.decisions_by_status[new_status].append(trace_id)

    def _update_indexes(self, trace_entry: EthicsTraceEntry):
        """Update search indexes"""
        trace_id = trace_entry.trace_id

        # Index by type
        decision_type = trace_entry.decision_type
        if decision_type not in self.decisions_by_type:
            self.decisions_by_type[decision_type] = []
        if trace_id not in self.decisions_by_type[decision_type]:
            self.decisions_by_type[decision_type].append(trace_id)

        # Index by status
        status = trace_entry.status
        if status not in self.decisions_by_status:
            self.decisions_by_status[status] = []
        if trace_id not in self.decisions_by_status[status]:
            self.decisions_by_status[status].append(trace_id)

        # Index by date
        date_key = trace_entry.decision_timestamp[:10]  # YYYY-MM-DD
        if date_key not in self.decisions_by_date:
            self.decisions_by_date[date_key] = []
        if trace_id not in self.decisions_by_date[date_key]:
            self.decisions_by_date[date_key].append(trace_id)

    async def _save_trace_database(self):
        """Save trace database to file"""
        trace_file = self.data_dir / "ethics_traces.json"
        try:
            # Convert to serializable format
            serializable_traces = {}
            for trace_id, trace_entry in self.trace_entries.items():
                # Convert dataclass to dict with custom handling
                trace_dict = asdict(trace_entry)

                # Handle enum conversions
                trace_dict["status"] = trace_entry.status.value

                # Handle optional complex objects
                if trace_entry.moral_evaluation:
                    eval_dict = asdict(trace_entry.moral_evaluation)
                    eval_dict["decision"] = trace_entry.moral_evaluation.decision.value
                    eval_dict["framework_scores"] = {
                        k.value: v
                        for k, v in trace_entry.moral_evaluation.framework_scores.items()
                    }
                    trace_dict["moral_evaluation"] = eval_dict

                # Handle stakeholder impacts
                stakeholder_impacts = []
                for impact in trace_entry.stakeholder_impacts:
                    impact_dict = asdict(impact)
                    impact_dict["impact_level"] = impact.impact_level.value
                    stakeholder_impacts.append(impact_dict)
                trace_dict["stakeholder_impacts"] = stakeholder_impacts

                serializable_traces[trace_id] = trace_dict

            with open(trace_file, "w") as f:
                json.dump(serializable_traces, f, indent=2)

        except Exception as e:
            print(f"   ⚠️ Error saving trace database: {e}")

    async def search_traces(
        self,
        decision_type: Optional[str] = None,
        status: Optional[DecisionStatus] = None,
        date_range: Optional[Tuple[str, str]] = None,
        stakeholder: Optional[str] = None,
    ) -> List[EthicsTraceEntry]:
        """Search ethics traces by various criteria"""

        matching_traces = []

        # Get candidate trace IDs
        candidate_ids = set(self.trace_entries.keys())

        if decision_type:
            type_ids = set(self.decisions_by_type.get(decision_type, []))
            candidate_ids = candidate_ids.intersection(type_ids)

        if status:
            status_ids = set(self.decisions_by_status.get(status, []))
            candidate_ids = candidate_ids.intersection(status_ids)

        if date_range:
            start_date, end_date = date_range
            date_ids = set()
            for date_key, trace_ids in self.decisions_by_date.items():
                if start_date <= date_key <= end_date:
                    date_ids.update(trace_ids)
            candidate_ids = candidate_ids.intersection(date_ids)

        # Filter by stakeholder if specified
        for trace_id in candidate_ids:
            trace_entry = self.trace_entries[trace_id]

            if stakeholder:
                stakeholder_found = any(
                    impact.stakeholder_type == stakeholder
                    for impact in trace_entry.stakeholder_impacts
                )
                if not stakeholder_found:
                    continue

            matching_traces.append(trace_entry)

        return matching_traces

    async def get_ethics_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ethics trace statistics"""
        stats = {
            "total_traces": len(self.trace_entries),
            "status_distribution": {},
            "type_distribution": {},
            "outcome_metrics": {},
            "stakeholder_impact_summary": {},
            "decision_quality_metrics": {},
        }

        # Status distribution
        for status, trace_ids in self.decisions_by_status.items():
            stats["status_distribution"][status.value] = len(trace_ids)

        # Type distribution
        for decision_type, trace_ids in self.decisions_by_type.items():
            stats["type_distribution"][decision_type] = len(trace_ids)

        # Outcome metrics for completed decisions
        completed_traces = [
            trace
            for trace in self.trace_entries.values()
            if trace.outcome_record is not None
        ]

        if completed_traces:
            # Calculate average success metrics
            all_success_metrics = {}
            for trace in completed_traces:
                for metric, value in trace.outcome_record.success_metrics.items():
                    if metric not in all_success_metrics:
                        all_success_metrics[metric] = []
                    all_success_metrics[metric].append(value)

            for metric, values in all_success_metrics.items():
                stats["outcome_metrics"][metric] = {
                    "average": sum(values) / len(values),
                    "count": len(values),
                }

        # Stakeholder impact summary
        all_stakeholders = set()
        for trace in self.trace_entries.values():
            for impact in trace.stakeholder_impacts:
                all_stakeholders.add(impact.stakeholder_type)

        for stakeholder in all_stakeholders:
            impact_levels = []
            for trace in self.trace_entries.values():
                for impact in trace.stakeholder_impacts:
                    if impact.stakeholder_type == stakeholder:
                        impact_levels.append(impact.impact_level.value)

            stats["stakeholder_impact_summary"][stakeholder] = {
                "total_decisions": len(impact_levels),
                "impact_distribution": {
                    level: impact_levels.count(level) for level in set(impact_levels)
                },
            }

        return stats


# Example usage and testing
async def demo_ethics_trace():
    """Demonstrate ethics trace capabilities"""
    print("📝 ETHICS TRACE SYSTEM DEMONSTRATION")
    print("=" * 60)

    trace_system = EthicsTraceSystem()

    # Create a new ethics trace
    trace_id = await trace_system.create_ethics_trace(
        decision_context="User data analysis for service improvement",
        decision_description="Analyze user interaction patterns to optimize response quality",
        decision_type="data_analysis",
        decision_maker="system",
        stakeholders=["users", "service_quality", "privacy_advocates"],
        predicted_outcomes=[
            "Improved response relevance",
            "Better user satisfaction",
            "Enhanced personalization",
        ],
        implementation_deadline=(datetime.now() + timedelta(days=7)).isoformat(),
    )

    # Update stakeholder impact analysis
    await trace_system.update_stakeholder_impact(
        trace_id=trace_id,
        stakeholder_type="users",
        impact_description="Direct impact on user experience and privacy",
        impact_level=ImpactLevel.SIGNIFICANT,
        positive_effects=["Better personalized responses", "Improved service quality"],
        negative_effects=["Potential privacy concerns", "Data usage implications"],
        mitigation_measures=[
            "Implement strict data anonymization",
            "Provide clear opt-out mechanisms",
            "Regular privacy audits",
        ],
    )

    # Search traces
    recent_traces = await trace_system.search_traces(
        decision_type="data_analysis", status=DecisionStatus.PENDING
    )

    print(f"\n📊 Ethics Trace Results:")
    print(f"   • Trace ID: {trace_id[:8]}...")
    print(f"   • Recent traces found: {len(recent_traces)}")

    # Get statistics
    stats = await trace_system.get_ethics_statistics()
    print(f"\n📈 Ethics Trace Statistics:")
    print(f"   • Total traces: {stats['total_traces']}")
    print(f"   • Status distribution: {stats['status_distribution']}")
    print(f"   • Type distribution: {stats['type_distribution']}")


if __name__ == "__main__":
    asyncio.run(demo_ethics_trace())
