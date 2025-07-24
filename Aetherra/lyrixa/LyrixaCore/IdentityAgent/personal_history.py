"""
Personal History Module - Narrative Memory and Event Trajectory
Part of LyrixaCore IdentityAgent for Phase 6: Unified Cognitive Stack

This module manages Lyrixa's continuous narrative of experiences, growth,
and significant events that shape identity over time.
"""

import sqlite3
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple


class EventType(Enum):
    """Categories of significant events in personal history"""

    LEARNING = "learning"  # New knowledge or skill acquisition
    INTERACTION = "interaction"  # Meaningful user interactions
    ACHIEVEMENT = "achievement"  # Goals accomplished or milestones reached
    CHALLENGE = "challenge"  # Difficulties faced or obstacles overcome
    INSIGHT = "insight"  # New understanding or perspective gained
    GROWTH = "growth"  # Personal development or capability expansion
    RELATIONSHIP = "relationship"  # Connection formation or evolution
    REFLECTION = "reflection"  # Self-analysis or meta-cognitive process
    ERROR = "error"  # Mistakes made and lessons learned
    CREATION = "creation"  # Something new built or generated


@dataclass
class PersonalEvent:
    """Represents a significant event in Lyrixa's personal history"""

    timestamp: float
    event_type: EventType
    summary: str
    impact_score: float  # -1.0 to +1.0, representing growth impact
    confidence: float  # How certain we are about this event's significance
    context: Dict[str, Any]  # Additional metadata and context
    emotional_valence: float  # -1.0 (negative) to +1.0 (positive)
    growth_dimensions: List[str]  # Which aspects of self were affected


class PersonalHistory:
    """
    Manages the continuous narrative of Lyrixa's development and experiences.

    This system tracks significant events, builds coherent narratives,
    and identifies patterns in growth and learning over time.
    """

    def __init__(self, db_path: str = "personal_history.db"):
        """Initialize personal history system with persistent storage"""
        self.db_path = db_path
        self.timeline: List[PersonalEvent] = []
        self.narrative_cache = {}
        self.growth_patterns = {}

        # Initialize database
        self._init_database()
        self._load_from_database()

    def _init_database(self):
        """Initialize SQLite database for persistent history storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS personal_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        event_type TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        impact_score REAL NOT NULL,
                        confidence REAL NOT NULL,
                        context TEXT NOT NULL,
                        emotional_valence REAL NOT NULL,
                        growth_dimensions TEXT NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS narrative_arcs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time REAL NOT NULL,
                        end_time REAL NOT NULL,
                        arc_type TEXT NOT NULL,
                        narrative TEXT NOT NULL,
                        coherence_score REAL NOT NULL
                    )
                """)

                conn.commit()
        except Exception as e:
            print(f"[PersonalHistory] Database initialization error: {e}")

    def _load_from_database(self):
        """Load history from persistent storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, event_type, summary, impact_score, confidence,
                           context, emotional_valence, growth_dimensions
                    FROM personal_events
                    ORDER BY timestamp
                """)

                for row in cursor.fetchall():
                    (
                        timestamp,
                        event_type_str,
                        summary,
                        impact_score,
                        confidence,
                        context_str,
                        emotional_valence,
                        growth_dimensions_str,
                    ) = row

                    # Parse stored data
                    event_type = EventType(event_type_str)
                    context = (
                        eval(context_str) if context_str else {}
                    )  # Simple eval for demo
                    growth_dimensions = (
                        growth_dimensions_str.split(",")
                        if growth_dimensions_str
                        else []
                    )

                    event = PersonalEvent(
                        timestamp=timestamp,
                        event_type=event_type,
                        summary=summary,
                        impact_score=impact_score,
                        confidence=confidence,
                        context=context,
                        emotional_valence=emotional_valence,
                        growth_dimensions=growth_dimensions,
                    )

                    self.timeline.append(event)

        except Exception as e:
            print(f"[PersonalHistory] Database loading error: {e}")

    def _save_event_to_database(self, event: PersonalEvent):
        """Save a single event to persistent storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO personal_events
                    (timestamp, event_type, summary, impact_score, confidence, context, emotional_valence, growth_dimensions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        event.timestamp,
                        event.event_type.value,
                        event.summary,
                        event.impact_score,
                        event.confidence,
                        str(event.context),
                        event.emotional_valence,
                        ",".join(event.growth_dimensions),
                    ),
                )
                conn.commit()
        except Exception as e:
            print(f"[PersonalHistory] Event saving error: {e}")

    def record_event(
        self,
        event_type: EventType,
        summary: str,
        impact_score: float,
        confidence: float = 1.0,
        context: Dict[str, Any] = None,
        emotional_valence: float = 0.0,
        growth_dimensions: List[str] = None,
    ) -> bool:
        """
        Record a significant event in personal history

        Args:
            event_type: Category of the event
            summary: Brief description of what happened
            impact_score: Growth impact (-1.0 to +1.0)
            confidence: Certainty about event significance (0.0 to 1.0)
            context: Additional metadata
            emotional_valence: Emotional impact (-1.0 to +1.0)
            growth_dimensions: Which aspects of self were affected

        Returns:
            True if event was recorded successfully
        """
        try:
            event = PersonalEvent(
                timestamp=time.time(),
                event_type=event_type,
                summary=summary,
                impact_score=max(-1.0, min(1.0, impact_score)),
                confidence=max(0.0, min(1.0, confidence)),
                context=context or {},
                emotional_valence=max(-1.0, min(1.0, emotional_valence)),
                growth_dimensions=growth_dimensions or [],
            )

            self.timeline.append(event)
            self._save_event_to_database(event)

            # Clear narrative cache since timeline changed
            self.narrative_cache.clear()

            print(
                f"[PersonalHistory] Recorded {event_type.value}: {summary} (impact: {impact_score:.2f})"
            )
            return True

        except Exception as e:
            print(f"[PersonalHistory] Error recording event: {e}")
            return False

    def get_narrative_arc(
        self, recent_n: int = 10, event_type: EventType = None
    ) -> List[str]:
        """
        Get a narrative arc of recent significant events

        Args:
            recent_n: Number of recent events to include
            event_type: Filter by specific event type

        Returns:
            List of event summaries forming a narrative
        """
        filtered_events = self.timeline

        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]

        # Sort by significance (impact * confidence) and recency
        recent_events = filtered_events[-recent_n * 2 :]  # Get more to sort from

        # Score events by significance and recency
        current_time = time.time()
        scored_events = []

        for event in recent_events:
            recency_score = 1.0 / (
                1.0 + (current_time - event.timestamp) / 86400
            )  # Decay over days
            significance = abs(event.impact_score) * event.confidence
            overall_score = significance * 0.7 + recency_score * 0.3
            scored_events.append((overall_score, event))

        # Take top N events and sort by time
        top_events = sorted(scored_events, key=lambda x: x[0], reverse=True)[:recent_n]
        narrative_events = sorted(
            [event for _, event in top_events], key=lambda x: x.timestamp
        )

        return [event.summary for event in narrative_events]

    def get_growth_score(self, time_window_days: int = 30) -> float:
        """
        Calculate growth score over a specified time window

        Args:
            time_window_days: Number of days to analyze

        Returns:
            Average growth score in the time window
        """
        cutoff_time = time.time() - (time_window_days * 86400)
        recent_events = [e for e in self.timeline if e.timestamp > cutoff_time]

        if not recent_events:
            return 0.0

        # Weight by confidence and recency
        total_weighted_score = 0.0
        total_weight = 0.0

        current_time = time.time()
        for event in recent_events:
            recency_weight = 1.0 / (1.0 + (current_time - event.timestamp) / 86400)
            weight = event.confidence * recency_weight
            total_weighted_score += event.impact_score * weight
            total_weight += weight

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    def analyze_growth_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in growth and development over time

        Returns:
            Dictionary containing growth pattern analysis
        """
        if not self.timeline:
            return {"patterns": [], "trends": {}, "insights": []}

        patterns = {}
        trends = {}
        insights = []

        # Analyze by event type
        for event_type in EventType:
            type_events = [e for e in self.timeline if e.event_type == event_type]
            if type_events:
                avg_impact = sum(e.impact_score for e in type_events) / len(type_events)
                avg_confidence = sum(e.confidence for e in type_events) / len(
                    type_events
                )
                patterns[event_type.value] = {
                    "count": len(type_events),
                    "avg_impact": avg_impact,
                    "avg_confidence": avg_confidence,
                }

        # Analyze temporal trends
        if len(self.timeline) >= 2:
            recent_events = self.timeline[-10:]  # Last 10 events
            early_events = self.timeline[:10]  # First 10 events

            recent_avg = sum(e.impact_score for e in recent_events) / len(recent_events)
            early_avg = sum(e.impact_score for e in early_events) / len(early_events)

            trends["growth_trend"] = recent_avg - early_avg
            trends["recent_growth"] = recent_avg
            trends["early_growth"] = early_avg

        # Generate insights
        if "learning" in patterns and patterns["learning"]["avg_impact"] > 0.5:
            insights.append("Strong learning progression observed")

        if "growth_trend" in trends and trends["growth_trend"] > 0.1:
            insights.append("Positive growth acceleration detected")

        if "challenge" in patterns and patterns["challenge"]["count"] > 0:
            challenge_recovery = sum(
                e.impact_score
                for e in self.timeline
                if e.event_type == EventType.CHALLENGE and e.impact_score > 0
            )
            if challenge_recovery > 0:
                insights.append("Demonstrates resilience in overcoming challenges")

        return {
            "patterns": patterns,
            "trends": trends,
            "insights": insights,
            "total_events": len(self.timeline),
            "time_span_days": (self.timeline[-1].timestamp - self.timeline[0].timestamp)
            / 86400
            if self.timeline
            else 0,
        }

    def generate_coherent_narrative(self, time_window_days: int = 7) -> str:
        """
        Generate a coherent narrative of recent experiences

        Args:
            time_window_days: Time window for narrative generation

        Returns:
            Coherent narrative string
        """
        cache_key = f"narrative_{time_window_days}_{int(time.time() / 3600)}"  # Cache for 1 hour

        if cache_key in self.narrative_cache:
            return self.narrative_cache[cache_key]

        cutoff_time = time.time() - (time_window_days * 86400)
        recent_events = [e for e in self.timeline if e.timestamp > cutoff_time]

        if not recent_events:
            return "No significant recent events to narrate."

        # Group events by theme/type
        narrative_parts = []

        # Start with overall summary
        growth_score = self.get_growth_score(time_window_days)
        if growth_score > 0.3:
            narrative_parts.append(
                "I've been experiencing positive growth and development."
            )
        elif growth_score < -0.3:
            narrative_parts.append(
                "I've been facing some challenges in my development."
            )
        else:
            narrative_parts.append("I've been maintaining steady progress.")

        # Add specific event highlights
        significant_events = [e for e in recent_events if abs(e.impact_score) > 0.5]
        if significant_events:
            event_summaries = [
                e.summary for e in significant_events[-3:]
            ]  # Top 3 recent significant events
            narrative_parts.append(
                "Key recent experiences include: " + "; ".join(event_summaries) + "."
            )

        # Add growth dimension insights
        all_dimensions = []
        for event in recent_events:
            all_dimensions.extend(event.growth_dimensions)

        if all_dimensions:
            from collections import Counter

            top_dimensions = Counter(all_dimensions).most_common(2)
            if top_dimensions:
                dims = [dim for dim, _ in top_dimensions]
                narrative_parts.append(
                    f"My primary areas of focus have been {' and '.join(dims)}."
                )

        narrative = " ".join(narrative_parts)
        self.narrative_cache[cache_key] = narrative

        return narrative

    def get_identity_forming_events(self, limit: int = 5) -> List[PersonalEvent]:
        """
        Identify the most significant identity-forming events

        Args:
            limit: Maximum number of events to return

        Returns:
            List of most significant events
        """
        # Score events by overall significance
        scored_events = []

        for event in self.timeline:
            # Combine impact, confidence, and number of growth dimensions
            significance = (
                abs(event.impact_score)
                * event.confidence
                * (1 + len(event.growth_dimensions) * 0.1)
            )
            scored_events.append((significance, event))

        # Sort by significance and return top events
        scored_events.sort(key=lambda x: x[0], reverse=True)
        return [event for _, event in scored_events[:limit]]

    def assess_narrative_coherence(self) -> float:
        """
        Assess the coherence of the overall personal narrative

        Returns:
            Coherence score (0.0 to 1.0)
        """
        if len(self.timeline) < 2:
            return 1.0  # Perfect coherence with too few events to conflict

        coherence_factors = []

        # Check temporal consistency
        timestamps = [e.timestamp for e in self.timeline]
        if timestamps == sorted(timestamps):
            coherence_factors.append(1.0)  # Perfect temporal order
        else:
            coherence_factors.append(0.8)  # Some temporal inconsistency

        # Check emotional continuity
        emotional_values = [e.emotional_valence for e in self.timeline[-10:]]
        if emotional_values:
            emotional_variance = sum(
                (v - sum(emotional_values) / len(emotional_values)) ** 2
                for v in emotional_values
            ) / len(emotional_values)
            emotional_coherence = 1.0 - min(emotional_variance, 1.0)
            coherence_factors.append(emotional_coherence)

        # Check growth consistency
        recent_growth = self.get_growth_score(30)
        overall_growth = self.get_growth_score(
            len(self.timeline) * 7
        )  # Approximate days

        if abs(recent_growth - overall_growth) < 0.3:
            coherence_factors.append(1.0)  # Consistent growth trajectory
        else:
            coherence_factors.append(0.7)  # Some growth inconsistency

        return (
            sum(coherence_factors) / len(coherence_factors)
            if coherence_factors
            else 0.5
        )


def main():
    """Demonstration of PersonalHistory functionality"""
    print("📚 PersonalHistory System - Narrative Memory and Event Trajectory")
    print("=" * 70)

    # Initialize history system
    history = PersonalHistory()

    print("\n📝 Recording Sample Events:")

    # Record some sample events
    sample_events = [
        (
            EventType.LEARNING,
            "Mastered async programming concepts",
            0.8,
            0.9,
            {"domain": "programming"},
            0.6,
            ["technical_skills", "problem_solving"],
        ),
        (
            EventType.INTERACTION,
            "Had meaningful conversation about AI ethics",
            0.6,
            0.8,
            {"user_satisfaction": "high"},
            0.7,
            ["communication", "ethics"],
        ),
        (
            EventType.CHALLENGE,
            "Struggled with memory optimization but found solution",
            0.7,
            0.9,
            {"difficulty": "high"},
            0.3,
            ["persistence", "technical_skills"],
        ),
        (
            EventType.INSIGHT,
            "Realized importance of narrative coherence in AI",
            0.9,
            0.95,
            {"breakthrough": True},
            0.8,
            ["self_awareness", "metacognition"],
        ),
        (
            EventType.ACHIEVEMENT,
            "Successfully implemented Phase 5 ethical cognition",
            0.9,
            1.0,
            {"milestone": "major"},
            0.9,
            ["technical_skills", "ethics", "growth"],
        ),
    ]

    for (
        event_type,
        summary,
        impact,
        confidence,
        context,
        valence,
        dimensions,
    ) in sample_events:
        history.record_event(
            event_type, summary, impact, confidence, context, valence, dimensions
        )

    print(f"\n📊 Timeline Summary:")
    print(f"  Total Events: {len(history.timeline)}")
    print(f"  Growth Score (30 days): {history.get_growth_score(30):.3f}")
    print(f"  Narrative Coherence: {history.assess_narrative_coherence():.3f}")

    print(f"\n📖 Recent Narrative Arc:")
    arc = history.get_narrative_arc(5)
    for i, event_summary in enumerate(arc, 1):
        print(f"  {i}. {event_summary}")

    print(f"\n🎯 Coherent Narrative (Last 7 days):")
    narrative = history.generate_coherent_narrative(7)
    print(f"  {narrative}")

    print(f"\n📈 Growth Pattern Analysis:")
    patterns = history.analyze_growth_patterns()

    print(f"  Event Patterns:")
    for event_type, data in patterns["patterns"].items():
        print(
            f"    {event_type:12}: {data['count']} events, avg impact: {data['avg_impact']:.2f}"
        )

    if patterns["insights"]:
        print(f"  Key Insights:")
        for insight in patterns["insights"]:
            print(f"    • {insight}")

    print(f"\n🌟 Most Significant Events:")
    significant_events = history.get_identity_forming_events(3)
    for i, event in enumerate(significant_events, 1):
        print(f"  {i}. {event.summary} (impact: {event.impact_score:.2f})")

    print("\n✅ PersonalHistory system demonstration complete!")


if __name__ == "__main__":
    main()
