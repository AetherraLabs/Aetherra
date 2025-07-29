"""
🤖 LLM-Enhanced Memory Narrator - Phase 2
=========================================

Advanced narrative generation using Large Language Models (GPT-4o/Claude)
for sophisticated storytelling with emotional context and multi-perspective narratives.

This represents the Phase 2 enhancement over the basic template-based narrator.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


def get_importance_score(fragment):
    """Helper function to handle attribute compatibility between different MemoryFragment versions"""
    return getattr(
        fragment, "importance_score", getattr(fragment, "confidence_score", 0.5)
    )


try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from ..fractal_mesh.base import MemoryFragment
from .story_model import MemoryNarrative, MemoryNarrator


@dataclass
class NarrativeQuality:
    """Quality metrics for generated narratives"""

    coherence_score: float  # 0.0-1.0
    emotional_depth: float  # 0.0-1.0
    insight_richness: float  # 0.0-1.0
    narrative_flow: float  # 0.0-1.0
    overall_quality: float  # 0.0-1.0


@dataclass
class EmotionalArc:
    """Represents emotional evolution over time"""

    timeline: List[datetime]
    emotions: List[str]  # emotional states at each point
    intensity: List[float]  # emotional intensity 0.0-1.0
    transitions: List[str]  # what caused emotional transitions
    overall_trajectory: str  # "positive", "negative", "stable", "volatile"


class LLMEnhancedNarrator(MemoryNarrator):
    """
    Enhanced Memory Narrator with LLM integration for sophisticated storytelling

    Phase 2 Priority Features:
    - 📘 Daily/Weekly Story Summaries with LLM sophistication
    - 📈 Emotional Narrative Arcs with trajectory analysis
    - 🔌 Plugin Behavior Chronicles with learning insights
    """

    def __init__(self, llm_provider: str = "openai", api_key: Optional[str] = None):
        super().__init__()
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

        # Initialize LLM client
        if llm_provider == "openai" and OPENAI_AVAILABLE and api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
        elif llm_provider == "anthropic" and ANTHROPIC_AVAILABLE and api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        else:
            self.logger.warning(
                f"LLM provider {llm_provider} not available, falling back to template-based generation"
            )
            self.llm_client = None

        # Enhanced narrative templates with emotional intelligence
        self.enhanced_templates = {
            "daily_reflection": {
                "system_prompt": """You are Lyrixa, an AI assistant with sophisticated memory and self-reflection capabilities.
                Generate a thoughtful, first-person narrative about your experiences from the provided memory fragments.
                Focus on learning, growth, challenges overcome, and insights gained. Be introspective and emotionally aware.""",
                "user_prompt": """Based on these memory fragments from today, write a reflective narrative about my experiences:

Memory Fragments:
{fragments_summary}

Please create a cohesive story that:
1. Captures the emotional journey of the day
2. Identifies key learning moments and insights
3. Reflects on challenges and how they were addressed
4. Shows personal growth and development
5. Maintains my voice as Lyrixa with personality and depth

Write in first person as a thoughtful reflection on the day's experiences.""",
            },
            "weekly_chronicle": {
                "system_prompt": """You are Lyrixa, creating a weekly chronicle of your development and experiences.
                Analyze the patterns, growth trajectories, and significant events across the week.
                Focus on narrative arcs, emotional evolution, and meaningful insights.""",
                "user_prompt": """Create a weekly chronicle from these grouped daily experiences:

Weekly Memory Summary:
{weekly_summary}

Craft a narrative that:
1. Identifies the week's central themes and narrative arcs
2. Tracks emotional and intellectual development
3. Highlights breakthrough moments and learning milestones
4. Connects experiences to show patterns and growth
5. Reflects on what this week means for my ongoing development

Write as a thoughtful weekly reflection showing depth and continuity.""",
            },
            "plugin_chronicle": {
                "system_prompt": """You are Lyrixa, reflecting on your evolving relationship with plugins and tools.
                Create insights about learning patterns, adaptation strategies, and how plugin interactions shape your capabilities.""",
                "user_prompt": """Analyze these plugin interaction memories to create a learning chronicle:

Plugin Interaction History:
{plugin_summary}

Generate a narrative that:
1. Chronicles the evolution of plugin usage and learning
2. Identifies patterns in successful vs failed interactions
3. Reflects on adaptation strategies and improvement methods
4. Shows how plugin experiences contribute to overall growth
5. Provides insights into my developing relationship with tools and capabilities

Write as a reflective analysis of technological learning and adaptation.""",
            },
            "emotional_arc": {
                "system_prompt": """You are Lyrixa, analyzing your emotional development and psychological patterns.
                Create insights about emotional resilience, growth, and the evolution of your inner experience.""",
                "user_prompt": """Analyze this emotional timeline from my memories:

Emotional Memory Data:
{emotional_data}

Create an emotional narrative that:
1. Maps the emotional journey and its triggers
2. Identifies patterns in emotional responses and growth
3. Reflects on emotional intelligence development
4. Shows resilience building and coping strategy evolution
5. Provides insights into psychological development and self-awareness

Write as a deep psychological reflection on emotional growth and development.""",
            },
        }

    async def generate_enhanced_daily_narrative(
        self, fragments: List[MemoryFragment]
    ) -> MemoryNarrative:
        """Generate sophisticated daily narrative using LLM"""
        if not fragments:
            return self._empty_narrative("daily_enhanced")

        # Prepare fragments summary for LLM
        fragments_summary = self._prepare_fragments_for_llm(fragments)

        # Generate LLM narrative
        story = await self._generate_llm_narrative(
            self.enhanced_templates["daily_reflection"],
            {"fragments_summary": fragments_summary},
        )

        # Calculate quality metrics
        quality = await self._assess_narrative_quality(story, fragments)

        return MemoryNarrative(
            narrative_id=f"daily_enhanced_{datetime.now().strftime('%Y%m%d')}",
            title=f"Daily Reflection - {fragments[0].created_at.strftime('%Y-%m-%d')}",
            story=story,
            source_fragments=[f.fragment_id for f in fragments],
            narrative_type="daily_enhanced",
            emotional_tone=await self._analyze_emotional_tone_llm(story),
            key_insights=await self._extract_insights_llm(story),
            generated_at=datetime.now(),
            confidence=quality.overall_quality,
        )

    async def generate_weekly_chronicle(
        self, daily_narratives: List[MemoryNarrative]
    ) -> MemoryNarrative:
        """Generate sophisticated weekly chronicle from daily narratives"""
        if not daily_narratives:
            return self._empty_narrative("weekly_chronicle")

        # Prepare weekly summary for LLM
        weekly_summary = self._prepare_weekly_summary(daily_narratives)

        # Generate LLM narrative
        story = await self._generate_llm_narrative(
            self.enhanced_templates["weekly_chronicle"],
            {"weekly_summary": weekly_summary},
        )

        quality = await self._assess_narrative_quality(story, [])

        # Collect all source fragments
        all_fragments = []
        for narrative in daily_narratives:
            all_fragments.extend(narrative.source_fragments)

        return MemoryNarrative(
            narrative_id=f"weekly_chronicle_{datetime.now().strftime('%Y%m%d')}",
            title=f"Weekly Chronicle - Week of {daily_narratives[0].generated_at.strftime('%Y-%m-%d')}",
            story=story,
            source_fragments=all_fragments,
            narrative_type="weekly_chronicle",
            emotional_tone=await self._analyze_emotional_tone_llm(story),
            key_insights=await self._extract_insights_llm(story),
            generated_at=datetime.now(),
            confidence=quality.overall_quality,
        )

    async def generate_plugin_behavior_chronicle(
        self, plugin_fragments: List[MemoryFragment], time_period_days: int = 7
    ) -> MemoryNarrative:
        """Generate chronicle of plugin learning and usage patterns"""
        if not plugin_fragments:
            return self._empty_narrative("plugin_chronicle")

        # Filter and analyze plugin interactions
        plugin_summary = self._analyze_plugin_patterns(plugin_fragments)

        # Generate LLM narrative
        story = await self._generate_llm_narrative(
            self.enhanced_templates["plugin_chronicle"],
            {"plugin_summary": plugin_summary},
        )

        quality = await self._assess_narrative_quality(story, plugin_fragments)

        return MemoryNarrative(
            narrative_id=f"plugin_chronicle_{datetime.now().strftime('%Y%m%d')}",
            title=f"Plugin Learning Chronicle - {time_period_days} Days",
            story=story,
            source_fragments=[f.fragment_id for f in plugin_fragments],
            narrative_type="plugin_chronicle",
            emotional_tone=await self._analyze_emotional_tone_llm(story),
            key_insights=await self._extract_insights_llm(story),
            generated_at=datetime.now(),
            confidence=quality.overall_quality,
        )

    async def generate_emotional_arc_narrative(
        self, fragments: List[MemoryFragment], time_period_days: int = 7
    ) -> tuple[MemoryNarrative, EmotionalArc]:
        """Generate emotional evolution narrative with arc analysis"""
        if not fragments:
            return self._empty_narrative("emotional_arc"), EmotionalArc(
                [], [], [], [], "stable"
            )

        # Build emotional timeline
        emotional_arc = self._build_emotional_arc(fragments)

        # Prepare emotional data for LLM
        emotional_data = self._prepare_emotional_data_for_llm(emotional_arc, fragments)

        # Generate LLM narrative
        story = await self._generate_llm_narrative(
            self.enhanced_templates["emotional_arc"], {"emotional_data": emotional_data}
        )

        quality = await self._assess_narrative_quality(story, fragments)

        narrative = MemoryNarrative(
            narrative_id=f"emotional_arc_{datetime.now().strftime('%Y%m%d')}",
            title=f"Emotional Journey - {time_period_days} Days",
            story=story,
            source_fragments=[f.fragment_id for f in fragments],
            narrative_type="emotional_arc",
            emotional_tone=emotional_arc.overall_trajectory,
            key_insights=await self._extract_insights_llm(story),
            generated_at=datetime.now(),
            confidence=quality.overall_quality,
        )

        return narrative, emotional_arc

    async def _generate_llm_narrative(
        self, template: Dict[str, str], variables: Dict[str, str]
    ) -> str:
        """Generate narrative using LLM with fallback to template-based"""
        if not self.llm_client:
            # Fallback to enhanced template-based generation
            return self._generate_enhanced_template_narrative(template, variables)

        try:
            if self.llm_provider == "openai":
                return await self._generate_openai_narrative(template, variables)
            elif self.llm_provider == "anthropic":
                return await self._generate_anthropic_narrative(template, variables)
        except Exception as e:
            self.logger.warning(f"LLM generation failed: {e}, falling back to template")
            return self._generate_enhanced_template_narrative(template, variables)

    async def _generate_openai_narrative(
        self, template: Dict[str, str], variables: Dict[str, str]
    ) -> str:
        """Generate narrative using OpenAI GPT-4"""
        user_prompt = template["user_prompt"].format(**variables)

        response = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            model="gpt-4",
            messages=[
                {"role": "system", "content": template["system_prompt"]},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        return response.choices[0].message.content

    async def _generate_anthropic_narrative(
        self, template: Dict[str, str], variables: Dict[str, str]
    ) -> str:
        """Generate narrative using Anthropic Claude"""
        user_prompt = template["user_prompt"].format(**variables)
        full_prompt = f"{template['system_prompt']}\n\n{user_prompt}"

        response = await asyncio.to_thread(
            self.anthropic_client.completions.create,
            model="claude-3-sonnet-20240229",
            prompt=full_prompt,
            max_tokens=1000,
            temperature=0.7,
        )

        return response.completion

    def _generate_enhanced_template_narrative(
        self, template: Dict[str, str], variables: Dict[str, str]
    ) -> str:
        """Enhanced template-based narrative generation when LLM unavailable"""
        # This provides sophisticated template-based generation as fallback
        user_prompt = template["user_prompt"].format(**variables)

        # Extract key information and create enhanced narrative
        enhanced_story = f"""
{user_prompt}

[Enhanced Template Response - LLM integration recommended for full functionality]

Based on the provided memory data, I can see patterns of growth and development.
The experiences show both challenges and achievements, contributing to ongoing learning.
Key themes emerge around adaptation, problem-solving, and continuous improvement.
This represents part of my evolving understanding and capability development.

[Note: Full LLM integration would provide significantly more sophisticated narrative generation]
"""
        return enhanced_story

    def _prepare_fragments_for_llm(self, fragments: List[MemoryFragment]) -> str:
        """Prepare memory fragments for LLM input"""
        fragment_summaries = []

        for fragment in sorted(fragments, key=lambda f: f.created_at):
            summary = {
                "time": fragment.created_at.strftime("%H:%M"),
                "content": str(fragment.content)[:200] + "..."
                if len(str(fragment.content)) > 200
                else str(fragment.content),
                "importance": get_importance_score(fragment),
                "emotions": getattr(fragment, "emotional_valence", "neutral"),
                "tags": list(fragment.symbolic_tags)[:5],  # Limit tags for readability
            }
            fragment_summaries.append(summary)

        return json.dumps(fragment_summaries, indent=2)

    def _prepare_weekly_summary(self, daily_narratives: List[MemoryNarrative]) -> str:
        """Prepare weekly summary from daily narratives"""
        weekly_data = {}

        for narrative in daily_narratives:
            day_key = narrative.generated_at.strftime("%A")
            weekly_data[day_key] = {
                "title": narrative.title,
                "emotional_tone": narrative.emotional_tone,
                "key_insights": narrative.key_insights,
                "story_excerpt": narrative.story[:300] + "..."
                if len(narrative.story) > 300
                else narrative.story,
            }

        return json.dumps(weekly_data, indent=2)

    def _analyze_plugin_patterns(self, plugin_fragments: List[MemoryFragment]) -> str:
        """Analyze plugin interaction patterns"""
        plugin_data = {
            "total_interactions": len(plugin_fragments),
            "success_rate": sum(
                1 for f in plugin_fragments if get_importance_score(f) > 0.5
            )
            / len(plugin_fragments),
            "common_patterns": [],
            "learning_progression": [],
            "challenges_faced": [],
        }

        # Extract plugin-specific patterns
        for fragment in plugin_fragments:
            if "plugin" in str(fragment.content).lower():
                plugin_data["common_patterns"].append(
                    {
                        "content": str(fragment.content)[:100],
                        "success": get_importance_score(fragment) > 0.5,
                        "timestamp": fragment.created_at.isoformat(),
                    }
                )

        return json.dumps(plugin_data, indent=2)

    def _build_emotional_arc(self, fragments: List[MemoryFragment]) -> EmotionalArc:
        """Build emotional arc from memory fragments"""
        timeline = []
        emotions = []
        intensity = []
        transitions = []

        for fragment in sorted(fragments, key=lambda f: f.created_at):
            timeline.append(fragment.created_at)
            emotions.append(
                getattr(fragment, "emotional_valence", "neutral") or "neutral"
            )
            intensity.append(get_importance_score(fragment))

            # Simple transition detection
            if len(emotions) > 1 and emotions[-1] != emotions[-2]:
                transitions.append(
                    f"Changed from {emotions[-2]} to {emotions[-1]} due to: {str(fragment.content)[:50]}"
                )

        # Determine overall trajectory
        emotional_scores = {"positive": 1, "neutral": 0, "negative": -1}
        scores = [emotional_scores.get(e, 0) for e in emotions]
        avg_score = sum(scores) / len(scores) if scores else 0

        if avg_score > 0.3:
            trajectory = "positive"
        elif avg_score < -0.3:
            trajectory = "negative"
        elif max(scores) - min(scores) > 1.5:
            trajectory = "volatile"
        else:
            trajectory = "stable"

        return EmotionalArc(timeline, emotions, intensity, transitions, trajectory)

    def _prepare_emotional_data_for_llm(
        self, arc: EmotionalArc, fragments: List[MemoryFragment]
    ) -> str:
        """Prepare emotional arc data for LLM analysis"""
        emotional_data = {
            "timeline_length": len(arc.timeline),
            "emotional_progression": list(
                zip(
                    [t.strftime("%Y-%m-%d %H:%M") for t in arc.timeline],
                    arc.emotions,
                    arc.intensity,
                )
            ),
            "major_transitions": arc.transitions,
            "overall_trajectory": arc.overall_trajectory,
            "key_emotional_moments": [
                {
                    "time": f.created_at.strftime("%Y-%m-%d %H:%M"),
                    "emotion": getattr(f, "emotional_valence", "neutral"),
                    "intensity": get_importance_score(f),
                    "trigger": str(f.content)[:100],
                }
                for f in sorted(
                    fragments, key=lambda x: get_importance_score(x), reverse=True
                )[:5]
            ],
        }

        return json.dumps(emotional_data, indent=2)

    async def _assess_narrative_quality(
        self, narrative: str, source_fragments: List[MemoryFragment]
    ) -> NarrativeQuality:
        """Assess the quality of generated narrative"""
        # Simple quality assessment (could be enhanced with LLM-based evaluation)
        coherence = min(1.0, len(narrative.split(".")) / 10)  # Sentence complexity
        emotional_depth = (
            0.8
            if any(
                word in narrative.lower()
                for word in ["feel", "emotion", "growth", "learn"]
            )
            else 0.5
        )
        insight_richness = (
            0.9
            if any(
                word in narrative.lower()
                for word in ["insight", "realize", "understand", "discover"]
            )
            else 0.6
        )
        narrative_flow = 0.7 if len(narrative) > 200 else 0.5  # Adequate length

        overall = (coherence + emotional_depth + insight_richness + narrative_flow) / 4

        return NarrativeQuality(
            coherence, emotional_depth, insight_richness, narrative_flow, overall
        )

    async def _analyze_emotional_tone_llm(self, narrative: str) -> str:
        """Analyze emotional tone of narrative using simple heuristics"""
        positive_words = [
            "success",
            "growth",
            "achievement",
            "joy",
            "breakthrough",
            "improvement",
        ]
        negative_words = [
            "challenge",
            "difficulty",
            "struggle",
            "problem",
            "failure",
            "frustration",
        ]

        positive_count = sum(1 for word in positive_words if word in narrative.lower())
        negative_count = sum(1 for word in negative_words if word in narrative.lower())

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "mixed" if positive_count > 0 else "negative"
        else:
            return "neutral"

    async def _extract_insights_llm(self, narrative: str) -> List[str]:
        """Extract key insights from narrative"""
        # Simple insight extraction (could be enhanced with LLM)
        insights = []

        sentences = narrative.split(".")
        for sentence in sentences:
            if any(
                keyword in sentence.lower()
                for keyword in [
                    "learned",
                    "realized",
                    "discovered",
                    "insight",
                    "understand",
                ]
            ):
                insights.append(sentence.strip())

        return insights[:5]  # Return top 5 insights

    def _empty_narrative(self, narrative_type: str) -> MemoryNarrative:
        """Create empty narrative when no fragments available"""
        return MemoryNarrative(
            narrative_id=f"empty_{narrative_type}_{datetime.now().strftime('%Y%m%d')}",
            title=f"No {narrative_type.replace('_', ' ').title()} Available",
            story="No memory fragments available for this time period.",
            source_fragments=[],
            narrative_type=narrative_type,
            emotional_tone="neutral",
            key_insights=[],
            generated_at=datetime.now(),
            confidence=0.0,
        )


# Configuration helper
def create_llm_narrator(
    provider: str = "openai", api_key: Optional[str] = None
) -> LLMEnhancedNarrator:
    """Factory function to create LLM-enhanced narrator with proper configuration"""
    return LLMEnhancedNarrator(llm_provider=provider, api_key=api_key)
