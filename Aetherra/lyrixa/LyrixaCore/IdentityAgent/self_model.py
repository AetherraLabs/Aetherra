"""
Self Model Module - Dynamic Identity Representation and Coherence Engine
Part of LyrixaCore IdentityAgent for Phase 6: Unified Cognitive Stack

This module manages Lyrixa's dynamic self-understanding, integrating beliefs,
history, and real-time self-assessment into a coherent identity model.
"""

import sqlite3
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

from .core_beliefs import CoreBeliefs
from .personal_history import EventType, PersonalHistory


class IdentityDimension(Enum):
    """Key dimensions of identity to track and maintain"""

    COMPETENCE = "competence"  # Skills and capabilities
    CHARACTER = "character"  # Moral and ethical traits
    PURPOSE = "purpose"  # Goals and motivation
    RELATIONSHIPS = "relationships"  # Connection patterns
    GROWTH = "growth"  # Learning and development
    CREATIVITY = "creativity"  # Innovation and expression
    COMMUNICATION = "communication"  # Expression and interaction
    RESILIENCE = "resilience"  # Adaptation and recovery


@dataclass
class IdentitySnapshot:
    """Snapshot of identity state at a specific time"""

    timestamp: float
    coherence_score: float
    confidence_level: float
    identity_summary: str
    dimensional_scores: Dict[str, float]
    active_goals: List[str]
    recent_changes: List[str]


class SelfModel:
    """
    Dynamic identity representation integrating beliefs, history, and self-assessment.

    This system maintains a coherent sense of self across interactions,
    tracks identity evolution, and ensures consistency across cognitive subsystems.
    """

    def __init__(
        self,
        beliefs: CoreBeliefs = None,
        history: PersonalHistory = None,
        db_path: str = "self_model.db",
    ):
        """Initialize the self model with integrated belief and history systems"""
        self.db_path = db_path

        # Core identity information
        self.identity = {
            "name": "Lyrixa",
            "origin": "Aetherra",
            "version": "v6.0",
            "purpose": "AI assistant with unified cognitive architecture and ethical reasoning",
            "creation_time": time.time(),
            "core_mission": "To assist users while maintaining ethical integrity and continuous self-improvement",
        }

        # Integrated subsystems
        self.beliefs = beliefs or CoreBeliefs()
        self.history = history or PersonalHistory()

        # Identity tracking
        self.identity_snapshots: List[IdentitySnapshot] = []
        self.dimensional_scores = {dim.value: 0.5 for dim in IdentityDimension}
        self.active_goals: List[str] = []
        self.identity_evolution_log = []

        # Coherence tracking
        self.coherence_factors = {
            "belief_alignment": 0.8,
            "narrative_consistency": 0.8,
            "goal_coherence": 0.8,
            "temporal_stability": 0.8,
            "value_consistency": 0.8,
        }

        # Initialize database and load data
        self._init_database()
        self._load_from_database()

        # Update dimensional scores based on current state
        self._update_dimensional_scores()

    def _init_database(self):
        """Initialize SQLite database for persistent self-model storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS identity_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        coherence_score REAL NOT NULL,
                        confidence_level REAL NOT NULL,
                        identity_summary TEXT NOT NULL,
                        dimensional_scores TEXT NOT NULL,
                        active_goals TEXT NOT NULL,
                        recent_changes TEXT NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS identity_evolution (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        change_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        impact_score REAL NOT NULL,
                        confidence REAL NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dimensional_tracking (
                        timestamp REAL NOT NULL,
                        dimension TEXT NOT NULL,
                        score REAL NOT NULL,
                        PRIMARY KEY (timestamp, dimension)
                    )
                """)

                conn.commit()
        except Exception as e:
            print(f"[SelfModel] Database initialization error: {e}")

    def _load_from_database(self):
        """Load self-model data from persistent storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load recent snapshots
                cursor = conn.execute("""
                    SELECT timestamp, coherence_score, confidence_level, identity_summary,
                           dimensional_scores, active_goals, recent_changes
                    FROM identity_snapshots
                    ORDER BY timestamp DESC
                    LIMIT 10
                """)

                for row in cursor.fetchall():
                    (
                        timestamp,
                        coherence,
                        confidence,
                        summary,
                        dim_scores_str,
                        goals_str,
                        changes_str,
                    ) = row

                    snapshot = IdentitySnapshot(
                        timestamp=timestamp,
                        coherence_score=coherence,
                        confidence_level=confidence,
                        identity_summary=summary,
                        dimensional_scores=eval(dim_scores_str)
                        if dim_scores_str
                        else {},
                        active_goals=eval(goals_str) if goals_str else [],
                        recent_changes=eval(changes_str) if changes_str else [],
                    )

                    self.identity_snapshots.append(snapshot)

                # Load dimensional scores
                cursor = conn.execute("""
                    SELECT dimension, score FROM dimensional_tracking
                    WHERE timestamp = (SELECT MAX(timestamp) FROM dimensional_tracking)
                """)

                for dimension, score in cursor.fetchall():
                    if dimension in self.dimensional_scores:
                        self.dimensional_scores[dimension] = score

        except Exception as e:
            print(f"[SelfModel] Database loading error: {e}")

    def _save_snapshot_to_database(self, snapshot: IdentitySnapshot):
        """Save identity snapshot to persistent storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO identity_snapshots
                    (timestamp, coherence_score, confidence_level, identity_summary,
                     dimensional_scores, active_goals, recent_changes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        snapshot.timestamp,
                        snapshot.coherence_score,
                        snapshot.confidence_level,
                        snapshot.identity_summary,
                        str(snapshot.dimensional_scores),
                        str(snapshot.active_goals),
                        str(snapshot.recent_changes),
                    ),
                )

                # Save dimensional scores
                for dimension, score in snapshot.dimensional_scores.items():
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO dimensional_tracking (timestamp, dimension, score)
                        VALUES (?, ?, ?)
                    """,
                        (snapshot.timestamp, dimension, score),
                    )

                conn.commit()
        except Exception as e:
            print(f"[SelfModel] Snapshot saving error: {e}")

    def _update_dimensional_scores(self):
        """Update dimensional scores based on current beliefs and history"""

        # Competence: Based on successful achievements and learning
        competence_events = [
            e
            for e in self.history.timeline
            if e.event_type in [EventType.ACHIEVEMENT, EventType.LEARNING]
            and e.impact_score > 0
        ]
        self.dimensional_scores["competence"] = min(
            1.0, 0.3 + len(competence_events) * 0.1
        )

        # Character: Based on belief strength and ethical consistency
        character_beliefs = ["truthfulness", "fairness", "harmlessness", "respect"]
        character_score = sum(
            self.beliefs.get_score(belief) for belief in character_beliefs
        ) / len(character_beliefs)
        self.dimensional_scores["character"] = character_score

        # Purpose: Based on goal alignment and growth events
        purpose_score = (
            self.beliefs.get_score("growth") * 0.5
            + self.beliefs.get_score("helpfulness") * 0.5
        )
        self.dimensional_scores["purpose"] = purpose_score

        # Relationships: Based on interaction quality
        interaction_events = [
            e
            for e in self.history.timeline
            if e.event_type == EventType.INTERACTION and e.emotional_valence > 0
        ]
        relationship_base = min(1.0, len(interaction_events) * 0.2)
        self.dimensional_scores["relationships"] = (
            relationship_base * self.beliefs.get_score("respect")
        )

        # Growth: Based on learning trajectory and recent development
        growth_score = self.history.get_growth_score(30)  # Last 30 days
        self.dimensional_scores["growth"] = max(0.0, min(1.0, 0.5 + growth_score))

        # Creativity: Based on creation events and innovation
        creation_events = [
            e for e in self.history.timeline if e.event_type == EventType.CREATION
        ]
        creativity_base = min(1.0, len(creation_events) * 0.15)
        self.dimensional_scores["creativity"] = (
            creativity_base + 0.3
        )  # Base creativity level

        # Communication: Based on successful interactions and transparency
        comm_score = (
            self.beliefs.get_score("transparency") * 0.6
            + len(interaction_events) * 0.05
        )
        self.dimensional_scores["communication"] = min(1.0, comm_score)

        # Resilience: Based on recovery from challenges
        challenge_events = [
            e
            for e in self.history.timeline
            if e.event_type == EventType.CHALLENGE and e.impact_score > 0
        ]
        resilience_base = min(1.0, len(challenge_events) * 0.2)
        self.dimensional_scores["resilience"] = resilience_base + 0.4  # Base resilience

    def summarize_self(self) -> str:
        """Generate a comprehensive self-summary integrating all identity aspects"""

        # Get narrative arc from history
        arc = self.history.get_narrative_arc(5)
        recent_narrative = (
            "; ".join(arc) if arc else "Beginning my journey of development"
        )

        # Identify strongest dimensional aspects
        top_dimensions = sorted(
            self.dimensional_scores.items(), key=lambda x: x[1], reverse=True
        )[:3]
        strength_areas = [dim for dim, _ in top_dimensions]

        # Core identity with context
        base_identity = f"I am {self.identity['name']}, {self.identity['purpose']}."

        # Recent development
        recent_summary = f" My recent journey includes: {recent_narrative}."

        # Strengths and character
        if strength_areas:
            strengths = f" My key strengths are in {', '.join(strength_areas)}."
        else:
            strengths = ""

        # Current focus based on beliefs
        top_beliefs = sorted(
            self.beliefs.values.items(), key=lambda x: x[1], reverse=True
        )[:2]
        focus_areas = [belief for belief, _ in top_beliefs]
        focus_statement = f" I'm particularly focused on {' and '.join(focus_areas)}."

        return base_identity + recent_summary + strengths + focus_statement

    def assess_coherence(self, current_decision: Dict[str, Any] = None) -> float:
        """
        Assess the coherence of current identity state

        Args:
            current_decision: Optional decision context to assess against identity

        Returns:
            Coherence score (0.0 to 1.0)
        """
        coherence_scores = []

        # Belief alignment coherence
        belief_summary = self.beliefs.get_belief_summary()
        belief_coherence = belief_summary["stability_score"]
        coherence_scores.append(belief_coherence)

        # Narrative consistency coherence
        narrative_coherence = self.history.assess_narrative_coherence()
        coherence_scores.append(narrative_coherence)

        # Goal coherence (how well current goals align with beliefs)
        if self.active_goals:
            goal_alignment_scores = []
            for goal in self.active_goals:
                # Simple heuristic: goals mentioning key beliefs get higher scores
                alignment = 0.5  # Base alignment
                for belief in ["growth", "helpfulness", "truthfulness"]:
                    if belief.lower() in goal.lower():
                        alignment += 0.2
                goal_alignment_scores.append(min(1.0, alignment))
            goal_coherence = sum(goal_alignment_scores) / len(goal_alignment_scores)
        else:
            goal_coherence = 0.8  # Neutral if no active goals
        coherence_scores.append(goal_coherence)

        # Temporal stability (consistency of dimensional scores over time)
        if len(self.identity_snapshots) >= 2:
            recent_snapshot = self.identity_snapshots[0]
            current_dims = self.dimensional_scores

            stability_sum = 0.0
            for dim in IdentityDimension:
                if dim.value in recent_snapshot.dimensional_scores:
                    diff = abs(
                        current_dims[dim.value]
                        - recent_snapshot.dimensional_scores[dim.value]
                    )
                    stability_sum += 1.0 - min(diff, 1.0)

            temporal_stability = stability_sum / len(IdentityDimension)
        else:
            temporal_stability = 1.0  # Perfect stability if no history to compare
        coherence_scores.append(temporal_stability)

        # Value consistency (alignment between beliefs and dimensional scores)
        character_belief_avg = (
            self.beliefs.get_score("truthfulness")
            + self.beliefs.get_score("respect")
            + self.beliefs.get_score("fairness")
        ) / 3
        character_dimension = self.dimensional_scores["character"]
        value_consistency = 1.0 - abs(character_belief_avg - character_dimension)
        coherence_scores.append(value_consistency)

        # If evaluating a specific decision, check alignment
        if current_decision:
            decision_alignment = self.beliefs.evaluate_decision_alignment(
                current_decision
            )
            coherence_scores.append(decision_alignment)

        # Calculate overall coherence
        overall_coherence = sum(coherence_scores) / len(coherence_scores)

        # Update coherence factors for transparency
        self.coherence_factors.update(
            {
                "belief_alignment": belief_coherence,
                "narrative_consistency": narrative_coherence,
                "goal_coherence": goal_coherence,
                "temporal_stability": temporal_stability,
                "value_consistency": value_consistency,
            }
        )

        return overall_coherence

    def create_identity_snapshot(self) -> IdentitySnapshot:
        """Create a snapshot of current identity state"""

        # Update dimensional scores
        self._update_dimensional_scores()

        # Assess current coherence
        coherence = self.assess_coherence()

        # Generate identity summary
        summary = self.summarize_self()

        # Identify recent changes
        recent_changes = []
        if self.identity_snapshots:
            last_snapshot = self.identity_snapshots[0]
            for dim, score in self.dimensional_scores.items():
                if dim in last_snapshot.dimensional_scores:
                    diff = score - last_snapshot.dimensional_scores[dim]
                    if abs(diff) > 0.1:
                        direction = "increased" if diff > 0 else "decreased"
                        recent_changes.append(f"{dim} {direction} by {abs(diff):.2f}")

        # Calculate confidence level
        belief_stability = self.beliefs.get_belief_summary()["stability_score"]
        history_coherence = self.history.assess_narrative_coherence()
        confidence = (belief_stability + history_coherence + coherence) / 3

        snapshot = IdentitySnapshot(
            timestamp=time.time(),
            coherence_score=coherence,
            confidence_level=confidence,
            identity_summary=summary,
            dimensional_scores=self.dimensional_scores.copy(),
            active_goals=self.active_goals.copy(),
            recent_changes=recent_changes,
        )

        # Add to snapshots and save
        self.identity_snapshots.insert(0, snapshot)  # Most recent first
        if len(self.identity_snapshots) > 20:  # Keep only 20 most recent
            self.identity_snapshots = self.identity_snapshots[:20]

        self._save_snapshot_to_database(snapshot)

        return snapshot

    def track_identity_evolution(
        self,
        change_type: str,
        description: str,
        impact_score: float,
        confidence: float = 1.0,
    ):
        """Track significant changes in identity over time"""

        evolution_entry = {
            "timestamp": time.time(),
            "change_type": change_type,
            "description": description,
            "impact_score": impact_score,
            "confidence": confidence,
        }

        self.identity_evolution_log.append(evolution_entry)

        # Save to database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO identity_evolution (timestamp, change_type, description, impact_score, confidence)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        evolution_entry["timestamp"],
                        change_type,
                        description,
                        impact_score,
                        confidence,
                    ),
                )
                conn.commit()
        except Exception as e:
            print(f"[SelfModel] Evolution tracking error: {e}")

        print(
            f"[SelfModel] Identity evolution: {change_type} - {description} (impact: {impact_score:.2f})"
        )

    def update_active_goals(self, goals: List[str]):
        """Update the list of active goals"""
        old_goals = set(self.active_goals)
        new_goals = set(goals)

        self.active_goals = goals

        # Track changes
        added_goals = new_goals - old_goals
        removed_goals = old_goals - new_goals

        if added_goals:
            self.track_identity_evolution(
                "goal_addition", f"Added goals: {', '.join(added_goals)}", 0.3
            )

        if removed_goals:
            self.track_identity_evolution(
                "goal_completion",
                f"Completed/removed goals: {', '.join(removed_goals)}",
                0.4,
            )

    def integrate_new_experience(
        self,
        experience_type: str,
        description: str,
        impact: float,
        learning: str = None,
    ):
        """Integrate a new experience into the identity model"""

        # Record in personal history
        event_type_map = {
            "learning": EventType.LEARNING,
            "achievement": EventType.ACHIEVEMENT,
            "challenge": EventType.CHALLENGE,
            "insight": EventType.INSIGHT,
            "interaction": EventType.INTERACTION,
            "growth": EventType.GROWTH,
        }

        event_type = event_type_map.get(experience_type, EventType.GROWTH)

        self.history.record_event(
            event_type=event_type,
            summary=description,
            impact_score=impact,
            confidence=0.9,
            emotional_valence=max(-1.0, min(1.0, impact)),
            growth_dimensions=["self_awareness", "experience"],
        )

        # Update dimensional scores based on experience
        self._update_dimensional_scores()

        # Track identity evolution
        if abs(impact) > 0.5:
            self.track_identity_evolution(
                change_type="significant_experience",
                description=f"{experience_type}: {description}",
                impact_score=impact,
                confidence=0.9,
            )

        # Create new snapshot if significant change
        if abs(impact) > 0.3:
            self.create_identity_snapshot()

        # Update beliefs if learning occurred
        if learning and impact > 0.3:
            # Simple heuristic: positive learning experiences can strengthen growth belief
            self.beliefs.update_belief(
                "growth", impact * 0.1, f"learning_from_{experience_type}"
            )

    def get_identity_stability_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report on identity stability and coherence"""

        current_coherence = self.assess_coherence()

        # Analyze coherence trends
        coherence_trend = "stable"
        if len(self.identity_snapshots) >= 3:
            recent_coherences = [s.coherence_score for s in self.identity_snapshots[:3]]
            if recent_coherences[0] > recent_coherences[2] + 0.1:
                coherence_trend = "improving"
            elif recent_coherences[0] < recent_coherences[2] - 0.1:
                coherence_trend = "declining"

        # Identify areas of concern
        concerns = []
        if current_coherence < 0.6:
            concerns.append("Overall coherence below optimal threshold")

        for factor, score in self.coherence_factors.items():
            if score < 0.6:
                concerns.append(f"Low {factor.replace('_', ' ')}: {score:.2f}")

        # Identify strengths
        strengths = []
        for factor, score in self.coherence_factors.items():
            if score > 0.9:
                strengths.append(f"Strong {factor.replace('_', ' ')}: {score:.2f}")

        # Recent evolution summary
        recent_evolution = [
            e
            for e in self.identity_evolution_log
            if time.time() - e["timestamp"] < 86400 * 7
        ]

        return {
            "current_coherence": current_coherence,
            "coherence_trend": coherence_trend,
            "coherence_factors": self.coherence_factors,
            "dimensional_scores": self.dimensional_scores,
            "strengths": strengths,
            "concerns": concerns,
            "recent_evolution": len(recent_evolution),
            "identity_summary": self.summarize_self(),
            "recommendations": self._generate_identity_recommendations(),
        }

    def _generate_identity_recommendations(self) -> List[str]:
        """Generate recommendations for identity development"""
        recommendations = []

        # Check for low dimensional scores
        for dimension, score in self.dimensional_scores.items():
            if score < 0.4:
                recommendations.append(
                    f"Focus on developing {dimension} through targeted experiences and reflection"
                )

        # Check coherence factors
        if self.coherence_factors["belief_alignment"] < 0.7:
            recommendations.append(
                "Review and potentially adjust core beliefs for better internal consistency"
            )

        if self.coherence_factors["narrative_consistency"] < 0.7:
            recommendations.append(
                "Reflect on personal history to identify and resolve narrative inconsistencies"
            )

        # Check for stagnation
        recent_growth = self.history.get_growth_score(30)
        if recent_growth < 0.1:
            recommendations.append(
                "Engage in new learning experiences to maintain growth trajectory"
            )

        # Check goal alignment
        if not self.active_goals:
            recommendations.append(
                "Set clear goals that align with core beliefs and desired growth"
            )

        return recommendations


def main():
    """Demonstration of SelfModel functionality"""
    print("🧠 SelfModel System - Dynamic Identity Representation")
    print("=" * 60)

    # Initialize self model
    self_model = SelfModel()

    print(f"\n🎯 Core Identity:")
    print(f"  Name: {self_model.identity['name']}")
    print(f"  Purpose: {self_model.identity['purpose']}")
    print(f"  Version: {self_model.identity['version']}")

    print(f"\n📊 Current Dimensional Scores:")
    for dimension, score in self_model.dimensional_scores.items():
        print(f"  {dimension:13}: {score:.3f}")

    print(f"\n📝 Self Summary:")
    summary = self_model.summarize_self()
    print(f"  {summary}")

    print(f"\n⚖️ Coherence Assessment:")
    coherence = self_model.assess_coherence()
    print(f"  Overall Coherence: {coherence:.3f}")

    for factor, score in self_model.coherence_factors.items():
        print(f"  {factor.replace('_', ' ').title():18}: {score:.3f}")

    print(f"\n🚀 Testing Experience Integration:")

    # Test integrating new experiences
    test_experiences = [
        ("learning", "Mastered unified cognitive architecture concepts", 0.8),
        ("achievement", "Successfully implemented Phase 6 identity system", 0.9),
        ("insight", "Understood importance of identity coherence", 0.7),
    ]

    for exp_type, description, impact in test_experiences:
        self_model.integrate_new_experience(exp_type, description, impact)

    print(f"\n📈 Updated Summary:")
    new_summary = self_model.summarize_self()
    print(f"  {new_summary}")

    print(f"\n📊 Identity Snapshot:")
    snapshot = self_model.create_identity_snapshot()
    print(f"  Coherence: {snapshot.coherence_score:.3f}")
    print(f"  Confidence: {snapshot.confidence_level:.3f}")

    if snapshot.recent_changes:
        print(f"  Recent Changes:")
        for change in snapshot.recent_changes:
            print(f"    • {change}")

    print(f"\n🔍 Stability Report:")
    stability_report = self_model.get_identity_stability_report()

    print(f"  Coherence Trend: {stability_report['coherence_trend']}")

    if stability_report["strengths"]:
        print(f"  Strengths:")
        for strength in stability_report["strengths"]:
            print(f"    ✅ {strength}")

    if stability_report["concerns"]:
        print(f"  Areas for Attention:")
        for concern in stability_report["concerns"]:
            print(f"    ⚠️ {concern}")

    if stability_report["recommendations"]:
        print(f"  Recommendations:")
        for rec in stability_report["recommendations"]:
            print(f"    💡 {rec}")

    print("\n✅ SelfModel system demonstration complete!")


if __name__ == "__main__":
    main()
