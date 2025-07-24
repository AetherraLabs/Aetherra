"""
🕰️ Enhanced ReflectiveTimelineEngine - Phase 2
===============================================

Advanced timeline features for causal chain detection, narrative arc recognition,
emotional trajectory mapping, and milestone event highlighting.

This extends the basic EpisodicTimeline with sophisticated Phase 2 capabilities.
"""

import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..base import MemoryFragment
from .episodic_timeline import EpisodicTimeline, NarrativeArc


@dataclass
class CausalChain:
    """Extended causal relationship tracking"""

    chain_id: str
    root_cause: str  # Root fragment ID
    causal_sequence: List[str]  # Ordered fragment IDs showing causation
    chain_type: str  # "problem_solving", "learning", "goal_achievement", "relationship_building"
    strength: float  # Overall causal strength 0.0-1.0
    time_span: timedelta
    resolution_fragment: Optional[str]  # Fragment that resolves the chain
    goal_connections: List[str]  # Connected goal IDs
    causal_mechanisms: List[str]  # How each step caused the next
    branch_points: List[str]  # Fragments where multiple outcomes were possible
    confidence_evolution: List[float]  # How certainty changed through the chain


@dataclass
class GoalMemoryArc:
    """Memory patterns across goal pursuit"""

    arc_id: str
    goal_id: str
    goal_description: str
    arc_type: str  # "achievement", "struggle", "abandonment", "evolution"
    memory_sequence: List[str]  # Fragment IDs in chronological order
    progress_markers: List[Dict[str, Any]]  # Key progress/setback moments
    strategy_evolution: List[str]  # How approaches changed over time
    obstacle_patterns: List[str]  # Recurring challenges
    breakthrough_moments: List[str]  # Key insight/success fragments
    learning_milestones: List[str]  # What was learned at each stage
    emotional_journey: Dict[str, float]  # Emotional states through pursuit
    outcome_assessment: str  # Final evaluation of goal pursuit


@dataclass
class SelfNarrativeModel:
    """Self-understanding and identity modeling"""

    model_id: str
    identity_themes: List[str]  # Core aspects of self-understanding
    competency_map: Dict[str, float]  # Areas of strength/weakness
    growth_trajectory: List[Dict[str, Any]]  # How self-perception has evolved
    value_system: Dict[str, float]  # What matters most (weighted)
    relationship_patterns: List[str]  # How interactions typically unfold
    decision_patterns: List[str]  # Common decision-making approaches
    learning_style: Dict[str, Any]  # How new information is integrated
    emotional_baseline: Dict[str, float]  # Typical emotional patterns
    aspiration_model: List[str]  # What self wants to become
    fear_patterns: List[str]  # What self tends to avoid
    confidence_domains: Dict[str, float]  # Where self feels confident/uncertain
    narrative_coherence: float  # How consistent self-story is


@dataclass
class EmotionalTrajectory:
    """Detailed emotional evolution mapping"""

    trajectory_id: str
    fragment_sequence: List[str]
    emotional_states: List[str]  # emotional state at each fragment
    intensity_scores: List[float]  # emotional intensity 0.0-1.0
    transition_triggers: List[str]  # what caused emotional transitions
    peak_moments: List[str]  # fragments with highest emotional intensity
    recovery_patterns: List[str]  # how negative emotions resolved
    growth_indicators: List[str]  # signs of emotional development


@dataclass
class MilestoneEvent:
    """Significant learning or development milestone"""

    milestone_id: str
    fragment_id: str
    milestone_type: str  # "breakthrough", "failure_learning", "skill_acquisition", "relationship_milestone"
    significance_score: float
    prerequisites: List[str]  # fragments that led to this milestone
    consequences: List[str]  # fragments that resulted from this milestone
    learning_summary: str
    competency_impact: Dict[str, float]  # skill areas affected


class ReflectiveTimelineEngine(EpisodicTimeline):
    """
    Enhanced timeline engine with sophisticated analysis capabilities

    Phase 2 Features:
    - 🔗 Causal Chain Detection: Multi-step cause-effect relationships
    - 📖 Narrative Arc Recognition: Story patterns (conflict, resolution, growth)
    - 💭 Emotional Trajectory Mapping: Emotional evolution tracking
    - 🎯 Milestone Event Highlighting: Auto-identify significant learning moments
    """

    def __init__(self, db_path: str = "enhanced_episodic_timeline.db"):
        super().__init__(db_path)
        self.logger = logging.getLogger(__name__)

        # Enhanced data structures
        self.causal_chains: Dict[str, CausalChain] = {}
        self.emotional_trajectories: Dict[str, EmotionalTrajectory] = {}
        self.milestone_events: Dict[str, MilestoneEvent] = {}
        self.goal_memory_arcs: Dict[str, GoalMemoryArc] = {}
        self.self_narrative_model: Optional[SelfNarrativeModel] = None

        # Analysis parameters
        self.causal_detection_window = timedelta(
            hours=24
        )  # Look for causation within 24 hours
        self.emotional_transition_threshold = (
            0.3  # Minimum change to detect emotional shift
        )
        self.milestone_significance_threshold = (
            0.7  # Minimum score to be considered milestone
        )

        self._initialize_enhanced_tables()
        self._load_enhanced_data()

    def _initialize_enhanced_tables(self):
        """Create enhanced database tables for Phase 2 features"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Causal chains table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS causal_chains (
                    chain_id TEXT PRIMARY KEY,
                    root_cause TEXT NOT NULL,
                    causal_sequence TEXT,
                    chain_type TEXT,
                    strength REAL,
                    time_span TEXT,
                    resolution_fragment TEXT,
                    created_at TEXT
                )
            """)

            # Emotional trajectories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS emotional_trajectories (
                    trajectory_id TEXT PRIMARY KEY,
                    fragment_sequence TEXT,
                    emotional_states TEXT,
                    intensity_scores TEXT,
                    transition_triggers TEXT,
                    peak_moments TEXT,
                    recovery_patterns TEXT,
                    growth_indicators TEXT,
                    created_at TEXT
                )
            """)

            # Milestone events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS milestone_events (
                    milestone_id TEXT PRIMARY KEY,
                    fragment_id TEXT NOT NULL,
                    milestone_type TEXT,
                    significance_score REAL,
                    prerequisites TEXT,
                    consequences TEXT,
                    learning_summary TEXT,
                    competency_impact TEXT,
                    detected_at TEXT
                )
            """)

            conn.commit()
        finally:
            conn.close()

    def _load_enhanced_data(self):
        """Load enhanced timeline data from database"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Load causal chains
            cursor = conn.execute("SELECT * FROM causal_chains")
            for row in cursor.fetchall():
                chain = self._row_to_causal_chain(row)
                self.causal_chains[chain.chain_id] = chain

            # Load emotional trajectories
            cursor = conn.execute("SELECT * FROM emotional_trajectories")
            for row in cursor.fetchall():
                trajectory = self._row_to_emotional_trajectory(row)
                self.emotional_trajectories[trajectory.trajectory_id] = trajectory

            # Load milestone events
            cursor = conn.execute("SELECT * FROM milestone_events")
            for row in cursor.fetchall():
                milestone = self._row_to_milestone_event(row)
                self.milestone_events[milestone.milestone_id] = milestone

            self.logger.info(
                f"Loaded {len(self.causal_chains)} causal chains, "
                f"{len(self.emotional_trajectories)} emotional trajectories, "
                f"{len(self.milestone_events)} milestone events"
            )
        finally:
            conn.close()

    async def detect_causal_chains(
        self, fragments: List[MemoryFragment]
    ) -> List[CausalChain]:
        """
        🔗 Detect multi-step causal relationships between memory fragments
        """
        if len(fragments) < 2:
            return []

        # Sort fragments by time
        sorted_fragments = sorted(fragments, key=lambda f: f.created_at)
        detected_chains = []

        # Look for causal patterns
        for i, root_fragment in enumerate(sorted_fragments):
            causal_sequence = [root_fragment.fragment_id]
            current_time = root_fragment.created_at

            # Look for fragments that could be causally related
            for j in range(i + 1, len(sorted_fragments)):
                next_fragment = sorted_fragments[j]
                time_diff = next_fragment.created_at - current_time

                # Skip if too much time has passed
                if time_diff > self.causal_detection_window:
                    break

                # Check for causal indicators
                causal_strength = self._calculate_causal_strength(
                    root_fragment, next_fragment, causal_sequence
                )

                if causal_strength > 0.5:  # Threshold for causal relationship
                    causal_sequence.append(next_fragment.fragment_id)
                    current_time = next_fragment.created_at

            # Create chain if we found causal relationships
            if len(causal_sequence) > 1:
                chain = await self._create_causal_chain(
                    causal_sequence, sorted_fragments
                )
                if chain:
                    detected_chains.append(chain)
                    self.causal_chains[chain.chain_id] = chain

        # Save new chains to database
        await self._save_causal_chains(detected_chains)

        self.logger.info(f"Detected {len(detected_chains)} causal chains")
        return detected_chains

    async def recognize_narrative_arcs(
        self, fragments: List[MemoryFragment]
    ) -> List[NarrativeArc]:
        """
        📖 Detect story patterns (conflict, resolution, growth) in memory sequences
        """
        if len(fragments) < 3:
            return []

        # Group fragments by themes and temporal proximity
        thematic_groups = self._group_fragments_by_theme(fragments)
        detected_arcs = []

        for theme, theme_fragments in thematic_groups.items():
            if len(theme_fragments) < 3:
                continue

            # Analyze for narrative patterns
            arc = await self._analyze_narrative_pattern(theme, theme_fragments)
            if arc and arc.significance_score > 0.6:
                detected_arcs.append(arc)

        self.logger.info(f"Recognized {len(detected_arcs)} narrative arcs")
        return detected_arcs

    async def map_emotional_trajectories(
        self, fragments: List[MemoryFragment]
    ) -> List[EmotionalTrajectory]:
        """
        💭 Track emotional evolution through experiences over time
        """
        if not fragments:
            return []

        # Sort fragments by time
        sorted_fragments = sorted(fragments, key=lambda f: f.created_at)

        # Group into emotional sequences
        emotional_sequences = self._group_by_emotional_continuity(sorted_fragments)
        trajectories = []

        for sequence in emotional_sequences:
            trajectory = await self._build_emotional_trajectory(sequence)
            if trajectory:
                trajectories.append(trajectory)
                self.emotional_trajectories[trajectory.trajectory_id] = trajectory

        # Save trajectories to database
        await self._save_emotional_trajectories(trajectories)

        self.logger.info(f"Mapped {len(trajectories)} emotional trajectories")
        return trajectories

    async def highlight_milestone_events(
        self, fragments: List[MemoryFragment]
    ) -> List[MilestoneEvent]:
        """
        🎯 Auto-identify significant learning moments and breakthroughs
        """
        potential_milestones = []

        for fragment in fragments:
            # Calculate significance score
            significance = self._calculate_milestone_significance(fragment, fragments)

            if significance > self.milestone_significance_threshold:
                milestone = await self._create_milestone_event(
                    fragment, fragments, significance
                )
                if milestone:
                    potential_milestones.append(milestone)
                    self.milestone_events[milestone.milestone_id] = milestone

        # Save milestones to database
        await self._save_milestone_events(potential_milestones)

        self.logger.info(f"Identified {len(potential_milestones)} milestone events")
        return potential_milestones

    def _calculate_causal_strength(
        self,
        cause_fragment: MemoryFragment,
        effect_fragment: MemoryFragment,
        sequence: List[str],
    ) -> float:
        """Calculate strength of causal relationship between fragments"""
        strength = 0.0

        # Time proximity (closer = stronger causal relationship)
        time_diff = effect_fragment.created_at - cause_fragment.created_at
        time_strength = max(
            0,
            1
            - (
                time_diff.total_seconds() / self.causal_detection_window.total_seconds()
            ),
        )
        strength += time_strength * 0.3

        # Content similarity (related topics suggest causation)
        content_similarity = self._calculate_content_similarity(
            cause_fragment, effect_fragment
        )
        strength += content_similarity * 0.3

        # Importance change (significant events often cause other significant events)
        importance_correlation = min(
            cause_fragment.confidence_score, effect_fragment.confidence_score
        )
        strength += importance_correlation * 0.2

        # Contextual indicators (keywords that suggest causation)
        causal_keywords = [
            "because",
            "due to",
            "resulted in",
            "led to",
            "caused",
            "triggered",
        ]
        effect_content = str(effect_fragment.content).lower()
        if any(keyword in effect_content for keyword in causal_keywords):
            strength += 0.2

        return min(1.0, strength)

    def _calculate_content_similarity(
        self, fragment1: MemoryFragment, fragment2: MemoryFragment
    ) -> float:
        """Calculate content similarity between fragments"""
        # Simple tag-based similarity (could be enhanced with embedding similarity)
        tags1 = set(fragment1.symbolic_tags)
        tags2 = set(fragment2.symbolic_tags)

        if not tags1 and not tags2:
            return 0.0

        intersection = len(tags1.intersection(tags2))
        union = len(tags1.union(tags2))

        return intersection / union if union > 0 else 0.0

    async def _create_causal_chain(
        self, sequence: List[str], all_fragments: List[MemoryFragment]
    ) -> Optional[CausalChain]:
        """Create causal chain from fragment sequence"""
        if len(sequence) < 2:
            return None

        # Find fragments by ID
        fragment_map = {f.fragment_id: f for f in all_fragments}
        chain_fragments = [fragment_map[fid] for fid in sequence if fid in fragment_map]

        if len(chain_fragments) < 2:
            return None

        # Determine chain type
        chain_type = self._classify_causal_chain(chain_fragments)

        # Calculate overall strength
        strengths = []
        for i in range(len(chain_fragments) - 1):
            strength = self._calculate_causal_strength(
                chain_fragments[i], chain_fragments[i + 1], sequence
            )
            strengths.append(strength)

        overall_strength = sum(strengths) / len(strengths) if strengths else 0.0

        # Calculate time span
        time_span = chain_fragments[-1].created_at - chain_fragments[0].created_at

        # Find resolution fragment (last high-confidence fragment in sequence)
        resolution_fragment = None
        for fragment in reversed(chain_fragments):
            if fragment.confidence_score > 0.7:
                resolution_fragment = fragment.fragment_id
                break

        return CausalChain(
            chain_id=str(uuid.uuid4()),
            root_cause=sequence[0],
            causal_sequence=sequence,
            chain_type=chain_type,
            strength=overall_strength,
            time_span=time_span,
            resolution_fragment=resolution_fragment,
            goal_connections=[],
            causal_mechanisms=[],
            branch_points=[],
            confidence_evolution=[],
        )

    def _classify_causal_chain(self, fragments: List[MemoryFragment]) -> str:
        """Classify the type of causal chain based on fragment content"""
        content_text = " ".join(str(f.content) for f in fragments).lower()

        if any(
            keyword in content_text
            for keyword in ["problem", "issue", "error", "fix", "solve"]
        ):
            return "problem_solving"
        elif any(
            keyword in content_text
            for keyword in ["learn", "understand", "discover", "realize"]
        ):
            return "learning"
        elif any(
            keyword in content_text
            for keyword in ["goal", "achieve", "complete", "finish"]
        ):
            return "goal_achievement"
        elif any(
            keyword in content_text
            for keyword in ["user", "interaction", "relationship", "trust"]
        ):
            return "relationship_building"
        else:
            return "general"

    def _group_fragments_by_theme(
        self, fragments: List[MemoryFragment]
    ) -> Dict[str, List[MemoryFragment]]:
        """Group fragments by thematic similarity"""
        theme_groups = {}

        for fragment in fragments:
            # Use primary tag as theme, or content-based theme if no tags
            theme = (
                list(fragment.symbolic_tags)[0] if fragment.symbolic_tags else "general"
            )

            if theme not in theme_groups:
                theme_groups[theme] = []
            theme_groups[theme].append(fragment)

        return theme_groups

    async def _analyze_narrative_pattern(
        self, theme: str, fragments: List[MemoryFragment]
    ) -> Optional[NarrativeArc]:
        """Analyze fragments for narrative arc patterns"""
        if len(fragments) < 3:
            return None

        # Sort by time
        sorted_fragments = sorted(fragments, key=lambda f: f.created_at)

        # Detect narrative structure
        arc_structure = self._detect_arc_structure(sorted_fragments)

        if not arc_structure["has_arc"]:
            return None

        # Build emotional trajectory
        emotional_trajectory = [f.confidence_score for f in sorted_fragments]

        # Calculate significance
        significance = self._calculate_arc_significance(sorted_fragments, arc_structure)

        return NarrativeArc(
            arc_id=str(uuid.uuid4()),
            title=f"{theme.title()} Arc",
            fragments=[f.fragment_id for f in sorted_fragments],
            key_moments=arc_structure["key_moments"],
            themes=[theme],
            emotional_trajectory=emotional_trajectory,
            resolution_status=arc_structure["resolution_status"],
            significance_score=significance,
        )

    def _detect_arc_structure(self, fragments: List[MemoryFragment]) -> Dict[str, Any]:
        """Detect narrative arc structure in fragment sequence"""
        if len(fragments) < 3:
            return {"has_arc": False}

        # Simple arc detection based on confidence and emotional patterns
        importance_scores = [f.confidence_score for f in fragments]

        # Look for conflict-resolution pattern (low-high-resolution)
        min_idx = importance_scores.index(min(importance_scores))
        max_idx = importance_scores.index(max(importance_scores))

        # Check if we have a clear progression
        has_conflict = min_idx < len(fragments) // 2  # Conflict in first half
        has_climax = max_idx > min_idx  # Climax after conflict

        key_moments = []
        if has_conflict:
            key_moments.append(fragments[min_idx].fragment_id)
        if has_climax:
            key_moments.append(fragments[max_idx].fragment_id)

        # Determine resolution status
        final_importance = importance_scores[-1]
        resolution_status = "resolved" if final_importance > 0.6 else "ongoing"

        return {
            "has_arc": has_conflict and has_climax,
            "key_moments": key_moments,
            "resolution_status": resolution_status,
        }

    def _calculate_arc_significance(
        self, fragments: List[MemoryFragment], structure: Dict[str, Any]
    ) -> float:
        """Calculate significance score for narrative arc"""
        significance = 0.0

        # Number of fragments (longer arcs more significant)
        significance += min(0.3, len(fragments) / 10)

        # Importance range (wider range more significant)
        importance_scores = [f.confidence_score for f in fragments]
        importance_range = max(importance_scores) - min(importance_scores)
        significance += importance_range * 0.4

        # Resolution quality
        if structure["resolution_status"] == "resolved":
            significance += 0.3

        return min(1.0, significance)

    def _group_by_emotional_continuity(
        self, fragments: List[MemoryFragment]
    ) -> List[List[MemoryFragment]]:
        """Group fragments into emotionally continuous sequences"""
        sequences = []
        current_sequence = []
        last_emotion = None

        for fragment in fragments:
            # Check for fragment with specific emotional valence if available
            emotional_valence = getattr(fragment, "emotional_valence", None)
            current_emotion = emotional_valence

            # Start new sequence if emotion changes significantly
            if (
                last_emotion
                and current_emotion
                and last_emotion != current_emotion
                and len(current_sequence) > 0
            ):
                sequences.append(current_sequence)
                current_sequence = [fragment]
            else:
                current_sequence.append(fragment)

            last_emotion = current_emotion

        if current_sequence:
            sequences.append(current_sequence)

        return [seq for seq in sequences if len(seq) >= 2]

    async def _build_emotional_trajectory(
        self, fragments: List[MemoryFragment]
    ) -> Optional[EmotionalTrajectory]:
        """Build emotional trajectory from fragment sequence"""
        if len(fragments) < 2:
            return None

        emotional_states = []
        intensity_scores = []
        transition_triggers = []

        for i, fragment in enumerate(fragments):
            emotional_valence = getattr(fragment, "emotional_valence", None)
            emotional_states.append(emotional_valence or "neutral")
            intensity_scores.append(fragment.confidence_score)

            # Detect transition triggers
            if i > 0 and emotional_states[i] != emotional_states[i - 1]:
                transition_triggers.append(
                    f"Transition from {emotional_states[i - 1]} to {emotional_states[i]}: {str(fragment.content)[:100]}"
                )

        # Find peak moments (highest intensity)
        peak_threshold = max(intensity_scores) * 0.8
        peak_moments = [
            f.fragment_id
            for f, score in zip(fragments, intensity_scores)
            if score >= peak_threshold
        ]

        # Detect recovery patterns (negative to positive transitions)
        recovery_patterns = []
        for trigger in transition_triggers:
            if "negative" in trigger and "positive" in trigger:
                recovery_patterns.append(trigger)

        # Identify growth indicators
        growth_indicators = []
        for fragment in fragments:
            content_lower = str(fragment.content).lower()
            if any(
                keyword in content_lower
                for keyword in ["learned", "improved", "grew", "developed", "mastered"]
            ):
                growth_indicators.append(fragment.fragment_id)

        return EmotionalTrajectory(
            trajectory_id=str(uuid.uuid4()),
            fragment_sequence=[f.fragment_id for f in fragments],
            emotional_states=emotional_states,
            intensity_scores=intensity_scores,
            transition_triggers=transition_triggers,
            peak_moments=peak_moments,
            recovery_patterns=recovery_patterns,
            growth_indicators=growth_indicators,
        )

    def _calculate_milestone_significance(
        self, fragment: MemoryFragment, all_fragments: List[MemoryFragment]
    ) -> float:
        """Calculate significance score for potential milestone event"""
        significance = 0.0

        # Base importance score
        significance += fragment.confidence_score * 0.4

        # Uniqueness (different from other fragments)
        uniqueness = self._calculate_fragment_uniqueness(fragment, all_fragments)
        significance += uniqueness * 0.3

        # Learning indicators in content
        content_lower = str(fragment.content).lower()
        learning_keywords = [
            "breakthrough",
            "realized",
            "learned",
            "mastered",
            "achieved",
            "succeeded",
            "overcame",
        ]
        learning_score = sum(
            1 for keyword in learning_keywords if keyword in content_lower
        ) / len(learning_keywords)
        significance += learning_score * 0.3

        return min(1.0, significance)

    def _calculate_fragment_uniqueness(
        self, fragment: MemoryFragment, all_fragments: List[MemoryFragment]
    ) -> float:
        """Calculate how unique this fragment is compared to others"""
        if len(all_fragments) <= 1:
            return 1.0

        similarities = []
        for other_fragment in all_fragments:
            if other_fragment.fragment_id != fragment.fragment_id:
                similarity = self._calculate_content_similarity(
                    fragment, other_fragment
                )
                similarities.append(similarity)

        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        return 1.0 - avg_similarity  # Lower similarity = higher uniqueness

    async def _create_milestone_event(
        self,
        fragment: MemoryFragment,
        all_fragments: List[MemoryFragment],
        significance: float,
    ) -> Optional[MilestoneEvent]:
        """Create milestone event from significant fragment"""

        # Classify milestone type
        content_lower = str(fragment.content).lower()
        if any(
            keyword in content_lower
            for keyword in ["breakthrough", "eureka", "discovered"]
        ):
            milestone_type = "breakthrough"
        elif any(
            keyword in content_lower
            for keyword in ["failed", "mistake", "error", "learned from"]
        ):
            milestone_type = "failure_learning"
        elif any(
            keyword in content_lower
            for keyword in ["mastered", "acquired", "learned", "skill"]
        ):
            milestone_type = "skill_acquisition"
        elif any(
            keyword in content_lower
            for keyword in ["user", "relationship", "trust", "bond"]
        ):
            milestone_type = "relationship_milestone"
        else:
            milestone_type = "general_milestone"

        # Find prerequisites (fragments that led to this)
        prerequisites = self._find_prerequisites(fragment, all_fragments)

        # Find consequences (fragments that resulted from this)
        consequences = self._find_consequences(fragment, all_fragments)

        # Generate learning summary
        learning_summary = self._generate_learning_summary(fragment, milestone_type)

        # Calculate competency impact
        competency_impact = self._calculate_competency_impact(fragment, milestone_type)

        return MilestoneEvent(
            milestone_id=str(uuid.uuid4()),
            fragment_id=fragment.fragment_id,
            milestone_type=milestone_type,
            significance_score=significance,
            prerequisites=prerequisites,
            consequences=consequences,
            learning_summary=learning_summary,
            competency_impact=competency_impact,
        )

    def _find_prerequisites(
        self, milestone_fragment: MemoryFragment, all_fragments: List[MemoryFragment]
    ) -> List[str]:
        """Find fragments that led to this milestone"""
        prerequisites = []
        milestone_time = milestone_fragment.created_at

        # Look for related fragments in the preceding time window
        for fragment in all_fragments:
            if (
                fragment.created_at < milestone_time
                and milestone_time - fragment.created_at <= timedelta(days=7)
            ):
                # Check for thematic or causal relationship
                similarity = self._calculate_content_similarity(
                    fragment, milestone_fragment
                )
                if similarity > 0.3:
                    prerequisites.append(fragment.fragment_id)

        return prerequisites[:5]  # Limit to top 5 prerequisites

    def _find_consequences(
        self, milestone_fragment: MemoryFragment, all_fragments: List[MemoryFragment]
    ) -> List[str]:
        """Find fragments that resulted from this milestone"""
        consequences = []
        milestone_time = milestone_fragment.created_at

        # Look for related fragments in the following time window
        for fragment in all_fragments:
            if (
                fragment.created_at > milestone_time
                and fragment.created_at - milestone_time <= timedelta(days=7)
            ):
                # Check for thematic relationship
                similarity = self._calculate_content_similarity(
                    fragment, milestone_fragment
                )
                if similarity > 0.3:
                    consequences.append(fragment.fragment_id)

        return consequences[:5]  # Limit to top 5 consequences

    def _generate_learning_summary(
        self, fragment: MemoryFragment, milestone_type: str
    ) -> str:
        """Generate a summary of what was learned from this milestone"""
        content = str(fragment.content)

        # Simple learning summary based on content and type
        if milestone_type == "breakthrough":
            return f"Breakthrough insight: {content[:200]}..."
        elif milestone_type == "failure_learning":
            return f"Learning from challenge: {content[:200]}..."
        elif milestone_type == "skill_acquisition":
            return f"Skill development: {content[:200]}..."
        elif milestone_type == "relationship_milestone":
            return f"Relationship progress: {content[:200]}..."
        else:
            return f"Milestone achievement: {content[:200]}..."

    def _calculate_competency_impact(
        self, fragment: MemoryFragment, milestone_type: str
    ) -> Dict[str, float]:
        """Calculate impact on different competency areas"""
        impact = {}

        # Base impact based on milestone type
        if milestone_type == "breakthrough":
            impact["problem_solving"] = 0.8
            impact["creativity"] = 0.7
        elif milestone_type == "failure_learning":
            impact["resilience"] = 0.9
            impact["learning_agility"] = 0.8
        elif milestone_type == "skill_acquisition":
            impact["technical_skills"] = 0.9
            impact["competency"] = 0.8
        elif milestone_type == "relationship_milestone":
            impact["emotional_intelligence"] = 0.8
            impact["communication"] = 0.7

        # Adjust based on fragment confidence
        for key in impact:
            impact[key] *= fragment.confidence_score

        return impact

    # 🔗 Enhanced Causality Analysis Methods

    async def analyze_goal_memory_arcs(
        self, fragments: List[MemoryFragment]
    ) -> List[GoalMemoryArc]:
        """
        🎯 Analyze memory patterns across goal pursuit
        """
        goal_groups = self._group_fragments_by_goal(fragments)
        goal_arcs = []

        for goal_id, goal_fragments in goal_groups.items():
            if len(goal_fragments) < 2:
                continue

            # Sort fragments by time
            sorted_fragments = sorted(goal_fragments, key=lambda f: f.created_at)

            # Analyze goal pursuit pattern
            arc_type = self._classify_goal_arc(sorted_fragments)
            progress_markers = self._identify_progress_markers(sorted_fragments)
            strategy_evolution = self._analyze_strategy_evolution(sorted_fragments)
            breakthrough_moments = self._find_breakthrough_moments(sorted_fragments)
            emotional_journey = self._map_goal_emotional_journey(sorted_fragments)

            arc = GoalMemoryArc(
                arc_id=str(uuid.uuid4()),
                goal_id=goal_id,
                goal_description=self._extract_goal_description(sorted_fragments),
                arc_type=arc_type,
                memory_sequence=[f.fragment_id for f in sorted_fragments],
                progress_markers=progress_markers,
                strategy_evolution=strategy_evolution,
                obstacle_patterns=self._identify_obstacle_patterns(sorted_fragments),
                breakthrough_moments=breakthrough_moments,
                learning_milestones=self._extract_learning_milestones(sorted_fragments),
                emotional_journey=emotional_journey,
                outcome_assessment=self._assess_goal_outcome(sorted_fragments),
            )

            goal_arcs.append(arc)
            self.goal_memory_arcs[arc.arc_id] = arc

        self.logger.info(f"Analyzed {len(goal_arcs)} goal memory arcs")
        return goal_arcs

    async def build_self_narrative_model(
        self, fragments: List[MemoryFragment]
    ) -> SelfNarrativeModel:
        """
        🎭 Build comprehensive self-understanding model
        """
        if len(fragments) < 10:
            self.logger.warning(
                "Insufficient fragments for robust self-narrative modeling"
            )

        # Extract identity themes
        identity_themes = self._extract_identity_themes(fragments)

        # Map competencies
        competency_map = self._map_competencies(fragments)

        # Track growth trajectory
        growth_trajectory = self._analyze_growth_trajectory(fragments)

        # Extract value system
        value_system = self._extract_value_system(fragments)

        # Analyze patterns
        relationship_patterns = self._analyze_relationship_patterns(fragments)
        decision_patterns = self._analyze_decision_patterns(fragments)
        learning_style = self._analyze_learning_style(fragments)

        # Emotional baseline
        emotional_baseline = self._calculate_emotional_baseline(fragments)

        # Future aspirations and fears
        aspiration_model = self._extract_aspirations(fragments)
        fear_patterns = self._identify_fear_patterns(fragments)

        # Confidence domains
        confidence_domains = self._map_confidence_domains(fragments)

        # Calculate narrative coherence
        narrative_coherence = self._calculate_narrative_coherence(fragments)

        model = SelfNarrativeModel(
            model_id=f"self_narrative_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            identity_themes=identity_themes,
            competency_map=competency_map,
            growth_trajectory=growth_trajectory,
            value_system=value_system,
            relationship_patterns=relationship_patterns,
            decision_patterns=decision_patterns,
            learning_style=learning_style,
            emotional_baseline=emotional_baseline,
            aspiration_model=aspiration_model,
            fear_patterns=fear_patterns,
            confidence_domains=confidence_domains,
            narrative_coherence=narrative_coherence,
        )

        self.self_narrative_model = model
        self.logger.info(
            f"Built self-narrative model with coherence: {narrative_coherence:.3f}"
        )
        return model

    async def detect_advanced_causal_patterns(
        self, fragments: List[MemoryFragment]
    ) -> List[CausalChain]:
        """
        🔬 Enhanced causal chain detection with mechanism analysis
        """
        basic_chains = await self.detect_causal_chains(fragments)
        enhanced_chains = []

        for chain in basic_chains:
            # Get the fragments in this chain
            chain_fragments = [
                f for f in fragments if f.fragment_id in chain.causal_sequence
            ]

            # Analyze causal mechanisms
            causal_mechanisms = self._analyze_causal_mechanisms(chain_fragments)

            # Identify branch points
            branch_points = self._identify_branch_points(chain_fragments, fragments)

            # Track confidence evolution
            confidence_evolution = [f.confidence_score for f in chain_fragments]

            # Connect to goals
            goal_connections = self._connect_chain_to_goals(chain_fragments)

            # Create enhanced chain
            enhanced_chain = CausalChain(
                chain_id=chain.chain_id,
                root_cause=chain.root_cause,
                causal_sequence=chain.causal_sequence,
                chain_type=chain.chain_type,
                strength=chain.strength,
                time_span=chain.time_span,
                resolution_fragment=chain.resolution_fragment,
                goal_connections=goal_connections,
                causal_mechanisms=causal_mechanisms,
                branch_points=branch_points,
                confidence_evolution=confidence_evolution,
            )

            enhanced_chains.append(enhanced_chain)
            self.causal_chains[enhanced_chain.chain_id] = enhanced_chain

        self.logger.info(
            f"Enhanced {len(enhanced_chains)} causal chains with mechanism analysis"
        )
        return enhanced_chains

    # Helper methods for enhanced analysis

    def _group_fragments_by_goal(
        self, fragments: List[MemoryFragment]
    ) -> Dict[str, List[MemoryFragment]]:
        """Group fragments by associated goals"""
        goal_groups = {}
        for fragment in fragments:
            # Extract goal references from content or tags
            goal_refs = self._extract_goal_references(fragment)
            for goal_id in goal_refs:
                if goal_id not in goal_groups:
                    goal_groups[goal_id] = []
                goal_groups[goal_id].append(fragment)
        return goal_groups

    def _extract_goal_references(self, fragment: MemoryFragment) -> List[str]:
        """Extract goal IDs referenced in fragment"""
        goal_refs = []
        content_str = str(fragment.content).lower()

        # Look for goal indicators in tags
        for tag in fragment.symbolic_tags:
            if "goal" in tag.lower():
                goal_refs.append(tag)

        # Simple pattern matching for goal references
        if "goal" in content_str:
            goal_refs.append("general_goal")

        return goal_refs if goal_refs else ["no_goal"]

    def _classify_goal_arc(self, fragments: List[MemoryFragment]) -> str:
        """Classify the type of goal pursuit arc"""
        if not fragments:
            return "unknown"

        # Analyze confidence progression
        confidences = [f.confidence_score for f in fragments]

        if confidences[-1] > 0.8:
            return "achievement"
        elif confidences[-1] < 0.3:
            return "abandonment"
        elif max(confidences) - min(confidences) > 0.4:
            return "struggle"
        else:
            return "evolution"

    def _analyze_causal_mechanisms(self, fragments: List[MemoryFragment]) -> List[str]:
        """Analyze how each step caused the next"""
        mechanisms = []
        for i in range(len(fragments) - 1):
            current = fragments[i]
            next_fragment = fragments[i + 1]

            # Simple mechanism detection based on content
            mechanism = self._infer_causal_mechanism(current, next_fragment)
            mechanisms.append(mechanism)

        return mechanisms

    def _infer_causal_mechanism(
        self, cause: MemoryFragment, effect: MemoryFragment
    ) -> str:
        """Infer how one fragment caused another"""
        cause_tags = set(cause.symbolic_tags)
        effect_tags = set(effect.symbolic_tags)

        if "learning" in cause_tags and "success" in effect_tags:
            return "knowledge_application"
        elif "problem" in cause_tags and "solution" in effect_tags:
            return "problem_solving"
        elif "insight" in cause_tags:
            return "cognitive_breakthrough"
        else:
            return "temporal_succession"

    def _extract_identity_themes(self, fragments: List[MemoryFragment]) -> List[str]:
        """Extract recurring themes about self-identity"""
        themes = set()
        for fragment in fragments:
            content_str = str(fragment.content).lower()
            if any(
                word in content_str
                for word in ["i am", "i tend to", "i usually", "my approach"]
            ):
                # Extract identity statements
                for tag in fragment.symbolic_tags:
                    if tag not in ["general", "neutral", "positive"]:
                        themes.add(tag)
        return list(themes)

    def _calculate_narrative_coherence(self, fragments: List[MemoryFragment]) -> float:
        """Calculate how coherent the self-narrative is"""
        if len(fragments) < 2:
            return 0.0

        # Simple coherence based on tag consistency and confidence stability
        tag_consistency = self._measure_tag_consistency(fragments)
        confidence_stability = self._measure_confidence_stability(fragments)

        return (tag_consistency + confidence_stability) / 2

    def _measure_tag_consistency(self, fragments: List[MemoryFragment]) -> float:
        """Measure consistency of tags across fragments"""
        all_tags = set()
        for fragment in fragments:
            all_tags.update(fragment.symbolic_tags)

        if not all_tags:
            return 0.0

        # Calculate overlap between fragments
        overlaps = []
        for i in range(len(fragments)):
            for j in range(i + 1, len(fragments)):
                tags1 = set(fragments[i].symbolic_tags)
                tags2 = set(fragments[j].symbolic_tags)
                if tags1 or tags2:
                    overlap = len(tags1 & tags2) / len(tags1 | tags2)
                    overlaps.append(overlap)

        return sum(overlaps) / len(overlaps) if overlaps else 0.0

    # Missing helper methods implementation

    def _identify_progress_markers(
        self, fragments: List[MemoryFragment]
    ) -> List[Dict[str, Any]]:
        """Identify key progress/setback moments"""
        markers = []
        for i, fragment in enumerate(fragments):
            if fragment.confidence_score > 0.8 or (
                i > 0
                and fragment.confidence_score - fragments[i - 1].confidence_score > 0.3
            ):
                markers.append(
                    {
                        "fragment_id": fragment.fragment_id,
                        "type": "progress",
                        "timestamp": fragment.created_at.isoformat(),
                        "confidence_change": fragment.confidence_score
                        - (fragments[i - 1].confidence_score if i > 0 else 0.5),
                    }
                )
        return markers

    def _analyze_strategy_evolution(self, fragments: List[MemoryFragment]) -> List[str]:
        """Analyze how approaches changed over time"""
        strategies = []
        for fragment in fragments:
            content_str = str(fragment.content).lower()
            if any(
                word in content_str
                for word in ["approach", "strategy", "method", "way"]
            ):
                strategies.append(
                    f"Strategy at {fragment.created_at.strftime('%Y-%m-%d')}"
                )
        return strategies

    def _find_breakthrough_moments(self, fragments: List[MemoryFragment]) -> List[str]:
        """Find key insight/success fragments"""
        breakthroughs = []
        for fragment in fragments:
            if (
                "breakthrough" in fragment.symbolic_tags
                or "insight" in fragment.symbolic_tags
            ):
                breakthroughs.append(fragment.fragment_id)
        return breakthroughs

    def _map_goal_emotional_journey(
        self, fragments: List[MemoryFragment]
    ) -> Dict[str, float]:
        """Map emotional states through goal pursuit"""
        emotions = {}
        for fragment in fragments:
            emotion = getattr(fragment, "emotional_valence", "neutral")
            if emotion not in emotions:
                emotions[emotion] = 0
            emotions[emotion] += fragment.confidence_score
        return emotions

    def _extract_goal_description(self, fragments: List[MemoryFragment]) -> str:
        """Extract goal description from fragments"""
        for fragment in fragments:
            content_str = str(fragment.content)
            if len(content_str) > 20:
                return (
                    content_str[:100] + "..." if len(content_str) > 100 else content_str
                )
        return "Goal pursuit"

    def _identify_obstacle_patterns(self, fragments: List[MemoryFragment]) -> List[str]:
        """Identify recurring challenges"""
        obstacles = []
        for fragment in fragments:
            if fragment.confidence_score < 0.4:
                obstacles.append(f"Challenge: {str(fragment.content)[:50]}...")
        return obstacles

    def _extract_learning_milestones(
        self, fragments: List[MemoryFragment]
    ) -> List[str]:
        """Extract what was learned at each stage"""
        milestones = []
        for fragment in fragments:
            if "learning" in fragment.symbolic_tags:
                milestones.append(f"Learned: {str(fragment.content)[:50]}...")
        return milestones

    def _assess_goal_outcome(self, fragments: List[MemoryFragment]) -> str:
        """Assess final evaluation of goal pursuit"""
        if not fragments:
            return "unknown"
        final_confidence = fragments[-1].confidence_score
        if final_confidence > 0.8:
            return "successful"
        elif final_confidence < 0.3:
            return "unsuccessful"
        else:
            return "ongoing"

    def _map_competencies(self, fragments: List[MemoryFragment]) -> Dict[str, float]:
        """Map areas of strength/weakness"""
        competencies = {}
        for fragment in fragments:
            for tag in fragment.symbolic_tags:
                if tag not in competencies:
                    competencies[tag] = []
                competencies[tag].append(fragment.confidence_score)

        # Average confidence per competency area
        return {k: sum(v) / len(v) for k, v in competencies.items() if v}

    def _analyze_growth_trajectory(
        self, fragments: List[MemoryFragment]
    ) -> List[Dict[str, Any]]:
        """Analyze how self-perception has evolved"""
        trajectory = []
        sorted_fragments = sorted(fragments, key=lambda f: f.created_at)

        for i, fragment in enumerate(sorted_fragments):
            if i % max(1, len(sorted_fragments) // 10) == 0:  # Sample every 10%
                trajectory.append(
                    {
                        "timestamp": fragment.created_at.isoformat(),
                        "confidence_level": fragment.confidence_score,
                        "key_tags": list(fragment.symbolic_tags)[:3],
                    }
                )
        return trajectory

    def _extract_value_system(
        self, fragments: List[MemoryFragment]
    ) -> Dict[str, float]:
        """Extract what matters most (weighted)"""
        values = {}
        for fragment in fragments:
            content_str = str(fragment.content).lower()
            if any(
                word in content_str for word in ["important", "value", "matter", "care"]
            ):
                for tag in fragment.symbolic_tags:
                    if tag not in values:
                        values[tag] = 0
                    values[tag] += fragment.confidence_score
        return values

    def _analyze_relationship_patterns(
        self, fragments: List[MemoryFragment]
    ) -> List[str]:
        """Analyze how interactions typically unfold"""
        patterns = []
        for fragment in fragments:
            if (
                "relationship" in fragment.symbolic_tags
                or "interaction" in fragment.symbolic_tags
            ):
                patterns.append(f"Pattern: {str(fragment.content)[:50]}...")
        return patterns

    def _analyze_decision_patterns(self, fragments: List[MemoryFragment]) -> List[str]:
        """Analyze common decision-making approaches"""
        patterns = []
        for fragment in fragments:
            content_str = str(fragment.content).lower()
            if any(word in content_str for word in ["decide", "choice", "option"]):
                patterns.append(f"Decision pattern: {str(fragment.content)[:50]}...")
        return patterns

    def _analyze_learning_style(
        self, fragments: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """Analyze how new information is integrated"""
        learning_indicators = {
            "visual": 0,
            "analytical": 0,
            "experiential": 0,
            "collaborative": 0,
        }

        for fragment in fragments:
            content_str = str(fragment.content).lower()
            if any(word in content_str for word in ["see", "visual", "diagram"]):
                learning_indicators["visual"] += 1
            if any(word in content_str for word in ["analyze", "think", "logic"]):
                learning_indicators["analytical"] += 1
            if any(word in content_str for word in ["try", "practice", "do"]):
                learning_indicators["experiential"] += 1
            if any(word in content_str for word in ["discuss", "collaborate", "team"]):
                learning_indicators["collaborative"] += 1

        return learning_indicators

    def _calculate_emotional_baseline(
        self, fragments: List[MemoryFragment]
    ) -> Dict[str, float]:
        """Calculate typical emotional patterns"""
        emotions = {}
        for fragment in fragments:
            emotion = getattr(fragment, "emotional_valence", "neutral")
            if emotion not in emotions:
                emotions[emotion] = []
            emotions[emotion].append(fragment.confidence_score)

        return {k: sum(v) / len(v) for k, v in emotions.items() if v}

    def _extract_aspirations(self, fragments: List[MemoryFragment]) -> List[str]:
        """Extract what self wants to become"""
        aspirations = []
        for fragment in fragments:
            content_str = str(fragment.content).lower()
            if any(word in content_str for word in ["want", "hope", "aspire", "goal"]):
                aspirations.append(f"Aspiration: {str(fragment.content)[:50]}...")
        return aspirations

    def _identify_fear_patterns(self, fragments: List[MemoryFragment]) -> List[str]:
        """Identify what self tends to avoid"""
        fears = []
        for fragment in fragments:
            if fragment.confidence_score < 0.3:
                fears.append(f"Avoidance: {str(fragment.content)[:50]}...")
        return fears

    def _map_confidence_domains(
        self, fragments: List[MemoryFragment]
    ) -> Dict[str, float]:
        """Map where self feels confident/uncertain"""
        domains = {}
        for fragment in fragments:
            for tag in fragment.symbolic_tags:
                if tag not in domains:
                    domains[tag] = []
                domains[tag].append(fragment.confidence_score)

        return {k: sum(v) / len(v) for k, v in domains.items() if v}

    def _identify_branch_points(
        self, chain_fragments: List[MemoryFragment], all_fragments: List[MemoryFragment]
    ) -> List[str]:
        """Identify fragments where multiple outcomes were possible"""
        branch_points = []
        for fragment in chain_fragments:
            if fragment.confidence_score < 0.6:  # Uncertainty indicates choice point
                branch_points.append(fragment.fragment_id)
        return branch_points

    def _connect_chain_to_goals(self, fragments: List[MemoryFragment]) -> List[str]:
        """Connect causal chain to specific goals"""
        goal_connections = []
        for fragment in fragments:
            goal_refs = self._extract_goal_references(fragment)
            goal_connections.extend(goal_refs)
        return list(set(goal_connections))  # Remove duplicates

    def _measure_confidence_stability(self, fragments: List[MemoryFragment]) -> float:
        """Measure stability of confidence across fragments"""
        if len(fragments) < 2:
            return 1.0

        confidences = [f.confidence_score for f in fragments]
        variance = sum(
            (c - sum(confidences) / len(confidences)) ** 2 for c in confidences
        ) / len(confidences)

        # Convert variance to stability (lower variance = higher stability)
        return max(0.0, 1.0 - variance)

    # Database helper methods
    def _row_to_causal_chain(self, row) -> CausalChain:
        """Convert database row to CausalChain object"""
        return CausalChain(
            chain_id=row[0],
            root_cause=row[1],
            causal_sequence=json.loads(row[2]),
            chain_type=row[3],
            strength=row[4],
            time_span=timedelta(seconds=float(row[5])) if row[5] else timedelta(),
            resolution_fragment=row[6],
            goal_connections=json.loads(row[7]) if len(row) > 7 and row[7] else [],
            causal_mechanisms=json.loads(row[8]) if len(row) > 8 and row[8] else [],
            branch_points=json.loads(row[9]) if len(row) > 9 and row[9] else [],
            confidence_evolution=json.loads(row[10])
            if len(row) > 10 and row[10]
            else [],
        )

    def _row_to_emotional_trajectory(self, row) -> EmotionalTrajectory:
        """Convert database row to EmotionalTrajectory object"""
        return EmotionalTrajectory(
            trajectory_id=row[0],
            fragment_sequence=json.loads(row[1]),
            emotional_states=json.loads(row[2]),
            intensity_scores=json.loads(row[3]),
            transition_triggers=json.loads(row[4]),
            peak_moments=json.loads(row[5]),
            recovery_patterns=json.loads(row[6]),
            growth_indicators=json.loads(row[7]),
        )

    def _row_to_milestone_event(self, row) -> MilestoneEvent:
        """Convert database row to MilestoneEvent object"""
        return MilestoneEvent(
            milestone_id=row[0],
            fragment_id=row[1],
            milestone_type=row[2],
            significance_score=row[3],
            prerequisites=json.loads(row[4]),
            consequences=json.loads(row[5]),
            learning_summary=row[6],
            competency_impact=json.loads(row[7]),
        )

    async def _save_causal_chains(self, chains: List[CausalChain]):
        """Save causal chains to database"""
        if not chains:
            return

        conn = sqlite3.connect(self.db_path)
        try:
            for chain in chains:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO causal_chains
                    (chain_id, root_cause, causal_sequence, chain_type, strength, time_span, resolution_fragment, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        chain.chain_id,
                        chain.root_cause,
                        json.dumps(chain.causal_sequence),
                        chain.chain_type,
                        chain.strength,
                        str(chain.time_span.total_seconds()),
                        chain.resolution_fragment,
                        datetime.now().isoformat(),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    async def _save_emotional_trajectories(
        self, trajectories: List[EmotionalTrajectory]
    ):
        """Save emotional trajectories to database"""
        if not trajectories:
            return

        conn = sqlite3.connect(self.db_path)
        try:
            for trajectory in trajectories:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO emotional_trajectories
                    (trajectory_id, fragment_sequence, emotional_states, intensity_scores,
                     transition_triggers, peak_moments, recovery_patterns, growth_indicators, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        trajectory.trajectory_id,
                        json.dumps(trajectory.fragment_sequence),
                        json.dumps(trajectory.emotional_states),
                        json.dumps(trajectory.intensity_scores),
                        json.dumps(trajectory.transition_triggers),
                        json.dumps(trajectory.peak_moments),
                        json.dumps(trajectory.recovery_patterns),
                        json.dumps(trajectory.growth_indicators),
                        datetime.now().isoformat(),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    async def _save_milestone_events(self, milestones: List[MilestoneEvent]):
        """Save milestone events to database"""
        if not milestones:
            return

        conn = sqlite3.connect(self.db_path)
        try:
            for milestone in milestones:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO milestone_events
                    (milestone_id, fragment_id, milestone_type, significance_score,
                     prerequisites, consequences, learning_summary, competency_impact, detected_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        milestone.milestone_id,
                        milestone.fragment_id,
                        milestone.milestone_type,
                        milestone.significance_score,
                        json.dumps(milestone.prerequisites),
                        json.dumps(milestone.consequences),
                        milestone.learning_summary,
                        json.dumps(milestone.competency_impact),
                        datetime.now().isoformat(),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    # Analysis methods for external use
    def get_causal_chains_by_type(self, chain_type: str) -> List[CausalChain]:
        """Get causal chains of specific type"""
        return [
            chain
            for chain in self.causal_chains.values()
            if chain.chain_type == chain_type
        ]

    def get_emotional_trajectories_by_trend(
        self, trend: str
    ) -> List[EmotionalTrajectory]:
        """Get emotional trajectories showing specific trend (positive/negative/stable)"""
        matching_trajectories = []

        for trajectory in self.emotional_trajectories.values():
            # Simple trend analysis
            if len(trajectory.intensity_scores) >= 2:
                start_score = sum(trajectory.intensity_scores[:2]) / 2
                end_score = sum(trajectory.intensity_scores[-2:]) / 2

                if trend == "positive" and end_score > start_score + 0.2:
                    matching_trajectories.append(trajectory)
                elif trend == "negative" and end_score < start_score - 0.2:
                    matching_trajectories.append(trajectory)
                elif trend == "stable" and abs(end_score - start_score) <= 0.2:
                    matching_trajectories.append(trajectory)

        return matching_trajectories

    def get_milestones_by_competency(self, competency: str) -> List[MilestoneEvent]:
        """Get milestones that impacted specific competency"""
        return [
            milestone
            for milestone in self.milestone_events.values()
            if competency in milestone.competency_impact
            and milestone.competency_impact[competency] > 0.5
        ]

    def get_timeline_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics about the timeline"""
        return {
            "total_causal_chains": len(self.causal_chains),
            "causal_chain_types": {
                chain_type: len(
                    [
                        c
                        for c in self.causal_chains.values()
                        if c.chain_type == chain_type
                    ]
                )
                for chain_type in set(c.chain_type for c in self.causal_chains.values())
            },
            "total_emotional_trajectories": len(self.emotional_trajectories),
            "total_milestones": len(self.milestone_events),
            "milestone_types": {
                milestone_type: len(
                    [
                        m
                        for m in self.milestone_events.values()
                        if m.milestone_type == milestone_type
                    ]
                )
                for milestone_type in set(
                    m.milestone_type for m in self.milestone_events.values()
                )
            },
            "avg_milestone_significance": sum(
                m.significance_score for m in self.milestone_events.values()
            )
            / len(self.milestone_events)
            if self.milestone_events
            else 0,
        }
