#!/usr/bin/env python3
"""
📖 Narrative Integrity Index
============================

Monitors the consistency and coherence of Lyrixa's narrative understanding
and storytelling capabilities across different contexts.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class NarrativeEvent:
    """Represents a narrative coherence measurement"""

    timestamp: str
    context: str
    coherence_score: float
    consistency_score: float
    creativity_score: float
    factual_accuracy: float


class NarrativeIntegrityMonitor:
    """Monitors narrative integrity and coherence"""

    def __init__(self, data_dir: str = "narrative_data"):
        self.data_dir = data_dir
        self.events: List[NarrativeEvent] = []

    def record_narrative_event(
        self, context: str, metrics: Dict[str, float]
    ) -> NarrativeEvent:
        """Record a narrative coherence measurement"""
        event = NarrativeEvent(
            timestamp=datetime.now().isoformat(),
            context=context,
            coherence_score=metrics.get("coherence", 0.75),
            consistency_score=metrics.get("consistency", 0.80),
            creativity_score=metrics.get("creativity", 0.70),
            factual_accuracy=metrics.get("factual_accuracy", 0.85),
        )

        self.events.append(event)
        return event

    def get_narrative_integrity_index(self) -> float:
        """Calculate current narrative integrity index"""
        if not self.events:
            return 0.77  # Default placeholder

        recent_events = self.events[-10:]
        total_score = 0

        for event in recent_events:
            # Weighted average of different narrative aspects
            score = (
                event.coherence_score * 0.3
                + event.consistency_score * 0.3
                + event.creativity_score * 0.2
                + event.factual_accuracy * 0.2
            )
            total_score += score

        return total_score / len(recent_events)

    def get_narrative_breakdown(self) -> Dict[str, float]:
        """Get breakdown of narrative scores"""
        if not self.events:
            return {
                "coherence": 0.75,
                "consistency": 0.80,
                "creativity": 0.70,
                "factual_accuracy": 0.85,
                "overall_integrity": 0.77,
            }

        recent_events = self.events[-10:]

        return {
            "coherence": sum(e.coherence_score for e in recent_events)
            / len(recent_events),
            "consistency": sum(e.consistency_score for e in recent_events)
            / len(recent_events),
            "creativity": sum(e.creativity_score for e in recent_events)
            / len(recent_events),
            "factual_accuracy": sum(e.factual_accuracy for e in recent_events)
            / len(recent_events),
            "overall_integrity": self.get_narrative_integrity_index(),
        }

    def get_narrative_trends(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get narrative integrity trends"""
        return [
            {
                "timestamp": event.timestamp,
                "context": event.context,
                "scores": {
                    "coherence": event.coherence_score,
                    "consistency": event.consistency_score,
                    "creativity": event.creativity_score,
                    "factual_accuracy": event.factual_accuracy,
                },
            }
            for event in self.events[-15:]  # Last 15 events
        ]
