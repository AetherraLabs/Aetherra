"""
📚 Memory Narrator
==================

Generates coherent narratives from memory fragments.
Transforms factual memory logs into story-like recollections.
"""

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..fractal_mesh.base import EpisodicChain, MemoryFragment


@dataclass
class MemoryNarrative:
    """A generated narrative from memory fragments"""

    narrative_id: str
    title: str
    story: str
    source_fragments: List[str]
    narrative_type: str  # "daily", "weekly", "project", "thematic"
    emotional_tone: str  # "positive", "negative", "neutral", "mixed"
    key_insights: List[str]
    generated_at: datetime
    confidence: float


class MemoryNarrator:
    """
    Generates narrative descriptions from memory fragments

    Transforms raw memory data into coherent stories that help
    Lyrixa understand her own experience and development.
    """

    def __init__(self):
        self.narrative_templates = {
            "daily": "Over the past day, {summary}. Key moments included {highlights}.",
            "weekly": "This week's journey involved {summary}. Notable developments: {highlights}.",
            "project": "The {project_name} project has evolved: {summary}. Progress includes {highlights}.",
            "struggle": "Recent challenges with {topic} showed {summary}. Resolution attempts: {highlights}.",
            "growth": "Growth in {area} demonstrated {summary}. Milestones achieved: {highlights}.",
        }

    def generate_daily_narrative(
        self, fragments: List[MemoryFragment]
    ) -> MemoryNarrative:
        """Generate a narrative for a day's worth of fragments"""
        if not fragments:
            return self._empty_narrative("daily")

        # Sort fragments by time
        sorted_fragments = sorted(fragments, key=lambda f: f.created_at)

        # Extract key themes and activities
        themes = set()
        activities = []

        for fragment in sorted_fragments:
            themes.update(fragment.symbolic_tags)
            if fragment.narrative_role:
                activities.append(fragment.narrative_role)

        # Generate summary
        summary = self._generate_summary(sorted_fragments, "daily")
        highlights = self._extract_highlights(sorted_fragments)

        story = self.narrative_templates["daily"].format(
            summary=summary, highlights=highlights
        )

        return MemoryNarrative(
            narrative_id=str(uuid.uuid4()),
            title=f"Daily Summary - {sorted_fragments[0].created_at.strftime('%Y-%m-%d')}",
            story=story,
            source_fragments=[f.fragment_id for f in fragments],
            narrative_type="daily",
            emotional_tone=self._detect_emotional_tone(fragments),
            key_insights=self._extract_insights(fragments),
            generated_at=datetime.now(),
            confidence=self._calculate_narrative_confidence(fragments),
        )

    def generate_weekly_narrative(
        self, fragments: List[MemoryFragment]
    ) -> MemoryNarrative:
        """Generate a narrative for a week's worth of fragments"""
        if not fragments:
            return self._empty_narrative("weekly")

        # Group fragments by day
        daily_groups = self._group_by_day(fragments)

        # Generate weekly themes and progression
        weekly_progression = []
        overall_themes = set()

        for day, day_fragments in daily_groups.items():
            day_themes = set()
            for fragment in day_fragments:
                day_themes.update(fragment.symbolic_tags)
                overall_themes.update(fragment.symbolic_tags)

            if day_themes:
                weekly_progression.append(f"{day}: {', '.join(list(day_themes)[:3])}")

        summary = f"progressed through themes of {', '.join(list(overall_themes)[:5])}"
        highlights = "; ".join(weekly_progression[:5])

        story = self.narrative_templates["weekly"].format(
            summary=summary, highlights=highlights
        )

        return MemoryNarrative(
            narrative_id=str(uuid.uuid4()),
            title=f"Weekly Summary - Week of {min(fragments, key=lambda f: f.created_at).created_at.strftime('%Y-%m-%d')}",
            story=story,
            source_fragments=[f.fragment_id for f in fragments],
            narrative_type="weekly",
            emotional_tone=self._detect_emotional_tone(fragments),
            key_insights=self._extract_insights(fragments),
            generated_at=datetime.now(),
            confidence=self._calculate_narrative_confidence(fragments),
        )

    def generate_thematic_narrative(
        self, fragments: List[MemoryFragment], theme: str
    ) -> MemoryNarrative:
        """Generate a narrative around a specific theme"""
        if not fragments:
            return self._empty_narrative("thematic")

        # Filter fragments related to theme
        relevant_fragments = [f for f in fragments if theme in f.symbolic_tags]

        if not relevant_fragments:
            return self._empty_narrative("thematic")

        # Analyze theme evolution
        theme_evolution = self._analyze_theme_evolution(relevant_fragments, theme)

        # Generate narrative based on theme type
        if any(
            keyword in theme.lower()
            for keyword in ["problem", "issue", "error", "fail"]
        ):
            template_type = "struggle"
            story = self.narrative_templates["struggle"].format(
                topic=theme,
                summary=theme_evolution["summary"],
                highlights=theme_evolution["highlights"],
            )
        elif any(
            keyword in theme.lower()
            for keyword in ["learn", "improve", "success", "achieve"]
        ):
            template_type = "growth"
            story = self.narrative_templates["growth"].format(
                area=theme,
                summary=theme_evolution["summary"],
                highlights=theme_evolution["highlights"],
            )
        else:
            template_type = "project"
            story = self.narrative_templates["project"].format(
                project_name=theme,
                summary=theme_evolution["summary"],
                highlights=theme_evolution["highlights"],
            )

        return MemoryNarrative(
            narrative_id=str(uuid.uuid4()),
            title=f"Theme Narrative: {theme.title()}",
            story=story,
            source_fragments=[f.fragment_id for f in relevant_fragments],
            narrative_type="thematic",
            emotional_tone=self._detect_emotional_tone(relevant_fragments),
            key_insights=self._extract_insights(relevant_fragments),
            generated_at=datetime.now(),
            confidence=self._calculate_narrative_confidence(relevant_fragments),
        )

    def generate_episodic_narrative(
        self, chain: EpisodicChain, fragments: List[MemoryFragment]
    ) -> MemoryNarrative:
        """Generate a narrative from an episodic chain"""
        chain_fragments = [f for f in fragments if f.fragment_id in chain.fragments]

        if not chain_fragments:
            return self._empty_narrative("episodic")

        # Sort by temporal order
        sorted_fragments = sorted(chain_fragments, key=lambda f: f.created_at)

        # Create narrative arc
        beginning = self._describe_beginning(sorted_fragments[:2])
        middle = self._describe_development(
            sorted_fragments[1:-1] if len(sorted_fragments) > 2 else []
        )
        end = self._describe_resolution(
            sorted_fragments[-2:] if len(sorted_fragments) > 1 else sorted_fragments
        )

        story_parts = [part for part in [beginning, middle, end] if part]
        story = " ".join(story_parts)

        return MemoryNarrative(
            narrative_id=str(uuid.uuid4()),
            title=f"Episodic Story: {chain.narrative_arc}",
            story=story,
            source_fragments=[f.fragment_id for f in chain_fragments],
            narrative_type="episodic",
            emotional_tone=self._detect_emotional_tone(chain_fragments),
            key_insights=self._extract_insights(chain_fragments),
            generated_at=datetime.now(),
            confidence=chain.significance_score,
        )

    def _generate_summary(
        self, fragments: List[MemoryFragment], narrative_type: str
    ) -> str:
        """Generate a summary of fragments"""
        if not fragments:
            return "nothing significant occurred"

        # Extract dominant themes
        all_themes = []
        for fragment in fragments:
            all_themes.extend(fragment.symbolic_tags)

        # Count theme frequency
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        # Get top themes
        top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        if top_themes:
            theme_names = [theme for theme, count in top_themes]
            if len(theme_names) == 1:
                return f"focused primarily on {theme_names[0]}"
            elif len(theme_names) == 2:
                return f"involved work with {theme_names[0]} and {theme_names[1]}"
            else:
                return (
                    f"covered {theme_names[0]}, {theme_names[1]}, and {theme_names[2]}"
                )

        return f"involved {len(fragments)} different activities"

    def _extract_highlights(self, fragments: List[MemoryFragment]) -> str:
        """Extract key highlights from fragments"""
        highlights = []

        # Get high-confidence fragments as highlights
        high_confidence = [f for f in fragments if f.confidence_score > 0.7]

        for fragment in high_confidence[:3]:  # Limit to top 3
            if fragment.narrative_role:
                highlights.append(fragment.narrative_role)
            elif fragment.symbolic_tags:
                highlights.append(f"work on {list(fragment.symbolic_tags)[0]}")
            else:
                highlights.append("significant activity")

        if highlights:
            return ", ".join(highlights)
        else:
            return "various routine activities"

    def _detect_emotional_tone(self, fragments: List[MemoryFragment]) -> str:
        """Detect overall emotional tone of fragments"""
        if not fragments:
            return "neutral"

        # Use confidence scores as proxy for emotional valence
        avg_confidence = sum(f.confidence_score for f in fragments) / len(fragments)

        # Simple emotion detection based on keywords and confidence
        emotional_keywords = {
            "positive": ["success", "achieve", "complete", "good", "excellent", "fix"],
            "negative": ["error", "fail", "problem", "issue", "bad", "broken"],
            "neutral": ["update", "change", "work", "process", "review"],
        }

        emotion_scores = {"positive": 0, "negative": 0, "neutral": 0}

        for fragment in fragments:
            content_text = str(fragment.content).lower()
            for emotion, keywords in emotional_keywords.items():
                for keyword in keywords:
                    if keyword in content_text:
                        emotion_scores[emotion] += 1

        # Combine keyword analysis with confidence
        if (
            avg_confidence > 0.7
            and emotion_scores["positive"] > emotion_scores["negative"]
        ):
            return "positive"
        elif (
            avg_confidence < 0.4
            or emotion_scores["negative"] > emotion_scores["positive"]
        ):
            return "negative"
        elif emotion_scores["positive"] > 0 and emotion_scores["negative"] > 0:
            return "mixed"
        else:
            return "neutral"

    def _extract_insights(self, fragments: List[MemoryFragment]) -> List[str]:
        """Extract key insights from fragments"""
        insights = []

        # Pattern detection insights
        themes = []
        for fragment in fragments:
            themes.extend(fragment.symbolic_tags)

        # Find recurring themes
        theme_counts = {}
        for theme in themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        recurring_themes = [theme for theme, count in theme_counts.items() if count > 1]

        if recurring_themes:
            insights.append(f"Recurring focus on: {', '.join(recurring_themes[:3])}")

        # Confidence pattern insights
        high_conf_count = len([f for f in fragments if f.confidence_score > 0.7])
        low_conf_count = len([f for f in fragments if f.confidence_score < 0.3])

        if high_conf_count > len(fragments) * 0.7:
            insights.append("High confidence period with clear achievements")
        elif low_conf_count > len(fragments) * 0.5:
            insights.append("Period of uncertainty requiring further exploration")

        return insights[:3]  # Limit to top 3 insights

    def _calculate_narrative_confidence(self, fragments: List[MemoryFragment]) -> float:
        """Calculate confidence in the generated narrative"""
        if not fragments:
            return 0.0

        # Based on fragment confidence and quantity
        avg_confidence = sum(f.confidence_score for f in fragments) / len(fragments)
        quantity_factor = min(
            len(fragments) / 10, 1.0
        )  # More fragments = more confident

        return avg_confidence * 0.7 + quantity_factor * 0.3

    def _group_by_day(
        self, fragments: List[MemoryFragment]
    ) -> Dict[str, List[MemoryFragment]]:
        """Group fragments by day"""
        groups = {}

        for fragment in fragments:
            day_key = fragment.created_at.strftime("%Y-%m-%d")
            if day_key not in groups:
                groups[day_key] = []
            groups[day_key].append(fragment)

        return groups

    def _analyze_theme_evolution(
        self, fragments: List[MemoryFragment], theme: str
    ) -> Dict[str, str]:
        """Analyze how a theme evolved over time"""
        if not fragments:
            return {"summary": "no data available", "highlights": "none"}

        # Sort by time to see progression
        sorted_fragments = sorted(fragments, key=lambda f: f.created_at)

        # Simple progression analysis
        confidence_progression = [f.confidence_score for f in sorted_fragments]

        if len(confidence_progression) > 1:
            trend = confidence_progression[-1] - confidence_progression[0]
            if trend > 0.2:
                summary = f"showed steady improvement and growing mastery"
            elif trend < -0.2:
                summary = f"encountered increasing challenges requiring attention"
            else:
                summary = f"maintained consistent engagement with varying results"
        else:
            summary = f"was explored with {confidence_progression[0]:.1f} confidence"

        # Extract specific highlights
        high_conf_fragments = [f for f in sorted_fragments if f.confidence_score > 0.7]
        if high_conf_fragments:
            highlights = f"{len(high_conf_fragments)} successful interactions"
        else:
            highlights = "ongoing exploration and learning"

        return {"summary": summary, "highlights": highlights}

    def _describe_beginning(self, fragments: List[MemoryFragment]) -> str:
        """Describe the beginning of an episodic sequence"""
        if not fragments:
            return ""

        first_fragment = fragments[0]
        themes = list(first_fragment.symbolic_tags)[:2]

        if themes:
            return f"The sequence began with {' and '.join(themes)}."
        else:
            return "The sequence started with initial exploration."

    def _describe_development(self, fragments: List[MemoryFragment]) -> str:
        """Describe the development/middle of an episodic sequence"""
        if not fragments:
            return ""

        all_themes = set()
        for fragment in fragments:
            all_themes.update(fragment.symbolic_tags)

        if all_themes:
            return f"Development involved {', '.join(list(all_themes)[:3])}."
        else:
            return "The situation continued to evolve."

    def _describe_resolution(self, fragments: List[MemoryFragment]) -> str:
        """Describe the resolution/end of an episodic sequence"""
        if not fragments:
            return ""

        last_fragment = fragments[-1]

        if last_fragment.confidence_score > 0.7:
            return "The sequence concluded successfully with high confidence."
        elif last_fragment.confidence_score < 0.3:
            return "The sequence ended with unresolved questions requiring further attention."
        else:
            return "The sequence reached a stable conclusion."

    def _empty_narrative(self, narrative_type: str) -> MemoryNarrative:
        """Create an empty narrative for when no fragments are available"""
        return MemoryNarrative(
            narrative_id=str(uuid.uuid4()),
            title=f"Empty {narrative_type.title()} Narrative",
            story="No significant memory fragments available for this period.",
            source_fragments=[],
            narrative_type=narrative_type,
            emotional_tone="neutral",
            key_insights=["No data available for analysis"],
            generated_at=datetime.now(),
            confidence=0.0,
        )
