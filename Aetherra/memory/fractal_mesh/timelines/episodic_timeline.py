"""
⏰ Episodic Timeline Manager
===========================

Manages temporal sequences of memory fragments with narrative continuity.
Enables story-like recall, causal relationship tracking, and temporal pattern recognition.
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from ..base import EpisodicChain, MemoryFragment, MemoryFragmentType


@dataclass
class TemporalPattern:
    """Represents a recurring temporal pattern in memory"""

    pattern_id: str
    pattern_type: str  # "daily", "weekly", "situational"
    fragments: List[str]  # Fragment IDs that follow this pattern
    temporal_signature: Dict[str, Any]  # Time-based characteristics
    confidence: float
    last_occurrence: datetime


@dataclass
class NarrativeArc:
    """Represents a narrative story arc across memory fragments"""

    arc_id: str
    title: str
    fragments: List[str]  # Ordered fragment IDs
    key_moments: List[str]  # Important fragment IDs
    themes: List[str]
    emotional_trajectory: List[float]  # Emotional valence over time
    resolution_status: str  # "ongoing", "resolved", "abandoned"
    significance_score: float


@dataclass
class CausalLink:
    """Represents a causal relationship between memory fragments"""

    cause_fragment_id: str
    effect_fragment_id: str
    relationship_type: str  # "direct", "indirect", "enabling", "preventing"
    confidence: float
    temporal_delay: timedelta
    detected_at: datetime


class EpisodicTimeline:
    """
    Manages temporal sequences and narrative structures in memory

    Features:
    - Episodic chain construction
    - Narrative arc detection
    - Causal relationship mapping
    - Temporal pattern recognition
    - Story-like memory retrieval
    """

    def __init__(self, db_path: str = "episodic_timeline.db"):
        self.db_path = db_path
        self.episodic_chains: Dict[str, EpisodicChain] = {}
        self.narrative_arcs: Dict[str, NarrativeArc] = {}
        self.causal_links: List[CausalLink] = []
        self.temporal_patterns: Dict[str, TemporalPattern] = {}

        self.max_chain_gap = timedelta(hours=6)  # Max time gap in episodic chains
        self.min_chain_length = 3  # Minimum fragments to form a chain
        self.causal_window = timedelta(hours=24)  # Max time for causal relationships

        self._init_database()
        self._load_existing_data()

    def _init_database(self):
        """Initialize episodic timeline database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodic_chains (
                    chain_id TEXT PRIMARY KEY,
                    fragments TEXT NOT NULL,
                    narrative_arc TEXT,
                    causal_links TEXT,
                    temporal_span_start TEXT,
                    temporal_span_end TEXT,
                    significance_score REAL,
                    created_at TEXT,
                    last_updated TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS narrative_arcs (
                    arc_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    fragments TEXT,
                    key_moments TEXT,
                    themes TEXT,
                    emotional_trajectory TEXT,
                    resolution_status TEXT,
                    significance_score REAL,
                    created_at TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS causal_links (
                    link_id TEXT PRIMARY KEY,
                    cause_fragment_id TEXT NOT NULL,
                    effect_fragment_id TEXT NOT NULL,
                    relationship_type TEXT,
                    confidence REAL,
                    temporal_delay TEXT,
                    detected_at TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS temporal_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    fragments TEXT,
                    temporal_signature TEXT,
                    confidence REAL,
                    last_occurrence TEXT
                )
            """)

            conn.commit()
        finally:
            conn.close()

    def _load_existing_data(self):
        """Load existing timeline data from database"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Load episodic chains
            cursor = conn.execute("SELECT * FROM episodic_chains")
            for row in cursor.fetchall():
                chain = self._row_to_chain(row)
                self.episodic_chains[chain.chain_id] = chain

            # Load narrative arcs
            cursor = conn.execute("SELECT * FROM narrative_arcs")
            for row in cursor.fetchall():
                arc = self._row_to_arc(row)
                self.narrative_arcs[arc.arc_id] = arc

            # Load causal links
            cursor = conn.execute("SELECT * FROM causal_links")
            for row in cursor.fetchall():
                link = self._row_to_causal_link(row)
                self.causal_links.append(link)

        finally:
            conn.close()

    def process_new_fragment(self, fragment: MemoryFragment) -> List[str]:
        """Process new fragment for episodic timeline integration"""
        affected_chains = []

        if fragment.fragment_type == MemoryFragmentType.EPISODIC:
            # Try to add to existing chains
            chain_id = self._find_or_create_chain(fragment)
            if chain_id:
                affected_chains.append(chain_id)

            # Detect causal relationships
            self._detect_causal_relationships(fragment)

            # Update temporal patterns
            self._update_temporal_patterns(fragment)

            # Update narrative arcs
            self._update_narrative_arcs(fragment)

        return affected_chains

    def _find_or_create_chain(self, fragment: MemoryFragment) -> Optional[str]:
        """Find existing chain to extend or create new one"""
        best_chain = None
        best_score = 0.0

        # Look for chains within temporal window
        for chain in self.episodic_chains.values():
            if not chain.fragments:
                continue

            # Get the last fragment time in the chain (would need fragment access)
            chain_end = chain.temporal_span[1]
            time_gap = fragment.created_at - chain_end

            if timedelta() <= time_gap <= self.max_chain_gap:
                # Calculate compatibility score
                compatibility = self._calculate_chain_compatibility(fragment, chain)
                if compatibility > best_score:
                    best_score = compatibility
                    best_chain = chain

        # Add to best chain if found
        if best_chain and best_score > 0.3:  # Minimum compatibility threshold
            best_chain.fragments.append(fragment.fragment_id)
            best_chain.temporal_span = (
                best_chain.temporal_span[0],
                fragment.created_at,
            )
            best_chain.significance_score = self._calculate_chain_significance(
                best_chain
            )
            self._persist_chain(best_chain)
            return best_chain.chain_id

        # Create new chain if fragment has episodic potential
        if self._has_episodic_potential(fragment):
            chain_id = str(uuid.uuid4())
            new_chain = EpisodicChain(
                chain_id=chain_id,
                fragments=[fragment.fragment_id],
                narrative_arc="Emerging narrative",
                causal_links={},
                temporal_span=(fragment.created_at, fragment.created_at),
                significance_score=fragment.confidence_score,
            )

            self.episodic_chains[chain_id] = new_chain
            self._persist_chain(new_chain)
            return chain_id

        return None

    def _calculate_chain_compatibility(
        self, fragment: MemoryFragment, chain: EpisodicChain
    ) -> float:
        """Calculate how well a fragment fits into an existing chain"""
        # Factors: concept overlap, temporal proximity, narrative coherence

        # Simplified compatibility based on symbolic tags
        # Would need access to chain fragments for full analysis
        compatibility = 0.5  # Base compatibility

        # Bonus for narrative role continuity
        if fragment.narrative_role:
            compatibility += 0.2

        # Temporal bonus (closer in time = more compatible)
        time_gap = abs((fragment.created_at - chain.temporal_span[1]).total_seconds())
        temporal_bonus = max(0, 0.3 * (1 - time_gap / (6 * 3600)))  # 6 hour decay
        compatibility += temporal_bonus

        return min(compatibility, 1.0)

    def _has_episodic_potential(self, fragment: MemoryFragment) -> bool:
        """Check if fragment has potential for episodic chaining"""
        # Factors: narrative role, confidence, content richness

        if fragment.confidence_score < 0.3:
            return False

        if fragment.narrative_role:
            return True

        # Check content richness
        if isinstance(fragment.content, dict):
            return len(fragment.content) > 2

        return len(str(fragment.content)) > 50  # Arbitrary threshold

    def _detect_causal_relationships(self, new_fragment: MemoryFragment):
        """Detect potential causal relationships with existing fragments"""
        # Look for fragments within causal window
        cutoff_time = new_fragment.created_at - self.causal_window

        # This would iterate through recent fragments to find causal patterns
        # Simplified for now - would use semantic analysis to detect causality

        causal_keywords = [
            "because",
            "caused",
            "resulted",
            "led to",
            "due to",
            "therefore",
        ]
        content_text = str(new_fragment.content).lower()

        if any(keyword in content_text for keyword in causal_keywords):
            # Simple causal relationship detected - would be more sophisticated
            link = CausalLink(
                cause_fragment_id="placeholder",  # Would identify actual cause
                effect_fragment_id=new_fragment.fragment_id,
                relationship_type="direct",
                confidence=0.6,
                temporal_delay=timedelta(minutes=30),  # Estimated
                detected_at=datetime.now(),
            )

            self.causal_links.append(link)
            self._persist_causal_link(link)

    def _update_temporal_patterns(self, fragment: MemoryFragment):
        """Update temporal pattern recognition"""
        # Extract time-based features
        timestamp = fragment.created_at
        hour = timestamp.hour
        day_of_week = timestamp.weekday()

        # Look for recurring patterns (simplified)
        pattern_key = f"daily_{hour}"

        if pattern_key not in self.temporal_patterns:
            self.temporal_patterns[pattern_key] = TemporalPattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type="daily",
                fragments=[],
                temporal_signature={"hour": hour},
                confidence=0.1,
                last_occurrence=timestamp,
            )

        pattern = self.temporal_patterns[pattern_key]
        pattern.fragments.append(fragment.fragment_id)
        pattern.last_occurrence = timestamp
        pattern.confidence = min(1.0, pattern.confidence + 0.1)

        self._persist_temporal_pattern(pattern)

    def _update_narrative_arcs(self, fragment: MemoryFragment):
        """Update narrative arc detection and tracking"""
        # Look for existing arcs that this fragment might continue
        for arc in self.narrative_arcs.values():
            if self._fragment_fits_arc(fragment, arc):
                arc.fragments.append(fragment.fragment_id)

                # Update emotional trajectory (simplified)
                emotional_value = (
                    fragment.confidence_score
                )  # Proxy for emotional valence
                arc.emotional_trajectory.append(emotional_value)

                # Update themes based on fragment symbolic tags
                arc.themes.extend(
                    [tag for tag in fragment.symbolic_tags if tag not in arc.themes]
                )

                self._persist_narrative_arc(arc)
                return

        # Create new narrative arc if fragment has narrative potential
        if self._has_narrative_potential(fragment):
            arc_id = str(uuid.uuid4())
            new_arc = NarrativeArc(
                arc_id=arc_id,
                title=f"Arc starting {fragment.created_at.strftime('%Y-%m-%d')}",
                fragments=[fragment.fragment_id],
                key_moments=[fragment.fragment_id]
                if fragment.confidence_score > 0.7
                else [],
                themes=list(fragment.symbolic_tags),
                emotional_trajectory=[fragment.confidence_score],
                resolution_status="ongoing",
                significance_score=fragment.confidence_score,
            )

            self.narrative_arcs[arc_id] = new_arc
            self._persist_narrative_arc(new_arc)

    def _fragment_fits_arc(self, fragment: MemoryFragment, arc: NarrativeArc) -> bool:
        """Check if fragment fits into existing narrative arc"""
        # Check thematic overlap
        theme_overlap = len(set(fragment.symbolic_tags) & set(arc.themes))
        return theme_overlap > 0

    def _has_narrative_potential(self, fragment: MemoryFragment) -> bool:
        """Check if fragment has potential to start a narrative arc"""
        return (
            fragment.confidence_score > 0.5
            and len(fragment.symbolic_tags) > 1
            and fragment.fragment_type == MemoryFragmentType.EPISODIC
        )

    def _calculate_chain_significance(self, chain: EpisodicChain) -> float:
        """Calculate the significance score of an episodic chain"""
        # Factors: length, temporal span, causal density

        length_factor = min(len(chain.fragments) / 10, 1.0)  # Normalize to 10 fragments

        # Temporal span factor (longer spans = more significant, up to a point)
        span_hours = (
            chain.temporal_span[1] - chain.temporal_span[0]
        ).total_seconds() / 3600
        span_factor = min(span_hours / (24 * 7), 1.0)  # Normalize to 1 week

        # Causal density (more causal links = more significant)
        causal_density = len(chain.causal_links) / max(len(chain.fragments) - 1, 1)

        significance = length_factor * 0.4 + span_factor * 0.3 + causal_density * 0.3
        return significance

    def get_episodic_story(
        self, time_range: Tuple[datetime, datetime], min_significance: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Get episodic story within time range"""
        story_elements = []

        # Find relevant chains
        relevant_chains = []
        for chain in self.episodic_chains.values():
            if (
                chain.temporal_span[0] <= time_range[1]
                and chain.temporal_span[1] >= time_range[0]
                and chain.significance_score >= min_significance
            ):
                relevant_chains.append(chain)

        # Sort by temporal order
        relevant_chains.sort(key=lambda c: c.temporal_span[0])

        for chain in relevant_chains:
            story_elements.append(
                {
                    "type": "episodic_chain",
                    "chain_id": chain.chain_id,
                    "narrative_arc": chain.narrative_arc,
                    "temporal_span": (
                        chain.temporal_span[0].isoformat(),
                        chain.temporal_span[1].isoformat(),
                    ),
                    "fragment_count": len(chain.fragments),
                    "significance": chain.significance_score,
                }
            )

        return story_elements

    def get_causal_network(self, fragment_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get causal network around a specific fragment"""
        network = {
            "center_fragment": fragment_id,
            "causes": [],
            "effects": [],
            "indirect_relationships": [],
        }

        # Direct causes and effects
        for link in self.causal_links:
            if link.effect_fragment_id == fragment_id:
                network["causes"].append(
                    {
                        "fragment_id": link.cause_fragment_id,
                        "relationship_type": link.relationship_type,
                        "confidence": link.confidence,
                        "temporal_delay": str(link.temporal_delay),
                    }
                )
            elif link.cause_fragment_id == fragment_id:
                network["effects"].append(
                    {
                        "fragment_id": link.effect_fragment_id,
                        "relationship_type": link.relationship_type,
                        "confidence": link.confidence,
                        "temporal_delay": str(link.temporal_delay),
                    }
                )

        return network

    def detect_temporal_patterns(
        self, pattern_type: str = "daily"
    ) -> List[TemporalPattern]:
        """Get detected temporal patterns of specified type"""
        return [
            pattern
            for pattern in self.temporal_patterns.values()
            if pattern.pattern_type == pattern_type and pattern.confidence > 0.3
        ]

    # Persistence methods
    def _persist_chain(self, chain: EpisodicChain):
        """Persist episodic chain to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO episodic_chains
                (chain_id, fragments, narrative_arc, causal_links, temporal_span_start,
                 temporal_span_end, significance_score, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    chain.chain_id,
                    json.dumps(chain.fragments),
                    chain.narrative_arc,
                    json.dumps(chain.causal_links),
                    chain.temporal_span[0].isoformat(),
                    chain.temporal_span[1].isoformat(),
                    chain.significance_score,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _persist_narrative_arc(self, arc: NarrativeArc):
        """Persist narrative arc to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO narrative_arcs
                (arc_id, title, fragments, key_moments, themes, emotional_trajectory,
                 resolution_status, significance_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    arc.arc_id,
                    arc.title,
                    json.dumps(arc.fragments),
                    json.dumps(arc.key_moments),
                    json.dumps(arc.themes),
                    json.dumps(arc.emotional_trajectory),
                    arc.resolution_status,
                    arc.significance_score,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _persist_causal_link(self, link: CausalLink):
        """Persist causal link to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            link_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO causal_links
                (link_id, cause_fragment_id, effect_fragment_id, relationship_type,
                 confidence, temporal_delay, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    link_id,
                    link.cause_fragment_id,
                    link.effect_fragment_id,
                    link.relationship_type,
                    link.confidence,
                    str(link.temporal_delay),
                    link.detected_at.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _persist_temporal_pattern(self, pattern: TemporalPattern):
        """Persist temporal pattern to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO temporal_patterns
                (pattern_id, pattern_type, fragments, temporal_signature,
                 confidence, last_occurrence)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    pattern.pattern_id,
                    pattern.pattern_type,
                    json.dumps(pattern.fragments),
                    json.dumps(pattern.temporal_signature),
                    pattern.confidence,
                    pattern.last_occurrence.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    # Database row conversion methods
    def _row_to_chain(self, row) -> EpisodicChain:
        """Convert database row to EpisodicChain object"""
        return EpisodicChain(
            chain_id=row[0],
            fragments=json.loads(row[1]),
            narrative_arc=row[2] or "No narrative",
            causal_links=json.loads(row[3]) if row[3] else {},
            temporal_span=(
                datetime.fromisoformat(row[4]),
                datetime.fromisoformat(row[5]),
            ),
            significance_score=row[6] or 0.0,
        )

    def _row_to_arc(self, row) -> NarrativeArc:
        """Convert database row to NarrativeArc object"""
        return NarrativeArc(
            arc_id=row[0],
            title=row[1],
            fragments=json.loads(row[2]) if row[2] else [],
            key_moments=json.loads(row[3]) if row[3] else [],
            themes=json.loads(row[4]) if row[4] else [],
            emotional_trajectory=json.loads(row[5]) if row[5] else [],
            resolution_status=row[6] or "ongoing",
            significance_score=row[7] or 0.0,
        )

    def _row_to_causal_link(self, row) -> CausalLink:
        """Convert database row to CausalLink object"""
        return CausalLink(
            cause_fragment_id=row[1],
            effect_fragment_id=row[2],
            relationship_type=row[3] or "unknown",
            confidence=row[4] or 0.5,
            temporal_delay=timedelta(
                seconds=int(row[5].split(":")[0]) * 3600
                + int(row[5].split(":")[1]) * 60
            )
            if row[5]
            else timedelta(),
            detected_at=datetime.fromisoformat(row[6]),
        )
