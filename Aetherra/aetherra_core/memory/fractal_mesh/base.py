"""
🧠 FractalMesh Core Engine
=========================

The central orchestration engine for multi-dimensional memory operations.
Coordinates between episodic, symbolic, and associative memory layers.
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class MemoryFragmentType(Enum):
    """Types of memory fragments in the fractal mesh"""

    EPISODIC = "episodic"  # Time-bound experience chunks
    SEMANTIC = "semantic"  # Concept-based knowledge
    PROCEDURAL = "procedural"  # Process and skill memories
    ASSOCIATIVE = "associative"  # Cross-context connections
    EMOTIONAL = "emotional"  # Valence-tagged experiences


class MemoryRelevanceStrategy(Enum):
    """Strategies for determining memory relevance"""

    TEMPORAL_PROXIMITY = "temporal"
    SEMANTIC_SIMILARITY = "semantic"
    ASSOCIATIVE_STRENGTH = "associative"
    NOVELTY_DETECTION = "novelty"
    PATTERN_COMPLETION = "pattern"


@dataclass
class MemoryFragment:
    """A fragment of memory in the fractal mesh"""

    fragment_id: str
    content: Dict[str, Any]
    fragment_type: MemoryFragmentType
    temporal_tags: Dict[str, Any]  # When, duration, sequence
    symbolic_tags: Set[str]  # What themes/concepts
    associative_links: List[str]  # Connected fragment IDs
    confidence_score: float  # How certain is this memory
    access_pattern: Dict[str, Any]  # How often accessed, when
    narrative_role: Optional[str]  # Role in larger story
    created_at: datetime
    last_evolved: datetime


@dataclass
class ConceptCluster:
    """A cluster of semantically related memories"""

    cluster_id: str
    central_concept: str
    related_concepts: Set[str]
    member_fragments: Set[str]
    cluster_strength: float
    temporal_evolution: List[Tuple[datetime, float]]  # How concept evolved
    narrative_themes: List[str]


@dataclass
class EpisodicChain:
    """A temporal sequence of related memory fragments"""

    chain_id: str
    fragments: List[str]  # Ordered fragment IDs
    narrative_arc: str  # Overall story of this chain
    causal_links: Dict[str, List[str]]  # fragment_id -> caused fragments
    temporal_span: Tuple[datetime, datetime]
    significance_score: float


class FractalMeshCore:
    def mutate_fragment(
        self, fragment: MemoryFragment, mutation_type: str = "observer_effect"
    ) -> MemoryFragment:
        # Stub: Mark the fragment as mutated (for test/demo purposes)
        fragment.content["mutated"] = True
        fragment.content["mutation_type"] = mutation_type
        return fragment

    def simulate_causal_branch(self, branch_id: str):
        # Stub: Return a simple simulated branch result
        return {"branch_id": branch_id, "status": "simulated", "fragments": []}

    """
    Core engine for multi-dimensional memory management

    Coordinates between:
    - Vector embeddings (current fast retrieval)
    - Episodic timelines (narrative continuity)
    - Concept clusters (symbolic reasoning)
    - Associative networks (creative connections)
    """

    def __init__(self, db_path: str = "fractal_memory.db"):
        self.db_path = Path(db_path)
        self.fragments: Dict[str, MemoryFragment] = {}
        self.concept_clusters: Dict[str, ConceptCluster] = {}
        self.episodic_chains: Dict[str, EpisodicChain] = {}

        # Caches for performance
        self.temporal_index: Dict[datetime, List[str]] = {}
        self.concept_index: Dict[str, Set[str]] = {}
        self.association_graph: Dict[str, Set[str]] = {}

        self._init_database()
        self._load_existing_fragments()

    def _init_database(self):
        """Initialize the fractal mesh database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_fragments (
                    fragment_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    fragment_type TEXT NOT NULL,
                    temporal_tags TEXT,
                    symbolic_tags TEXT,
                    associative_links TEXT,
                    confidence_score REAL,
                    access_pattern TEXT,
                    narrative_role TEXT,
                    created_at TEXT,
                    last_evolved TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS concept_clusters (
                    cluster_id TEXT PRIMARY KEY,
                    central_concept TEXT NOT NULL,
                    related_concepts TEXT,
                    member_fragments TEXT,
                    cluster_strength REAL,
                    temporal_evolution TEXT,
                    narrative_themes TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodic_chains (
                    chain_id TEXT PRIMARY KEY,
                    fragments TEXT NOT NULL,
                    narrative_arc TEXT,
                    causal_links TEXT,
                    temporal_span_start TEXT,
                    temporal_span_end TEXT,
                    significance_score REAL
                )
            """)

            # Indexes for performance
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_fragments_temporal ON memory_fragments (created_at)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_fragments_type ON memory_fragments (fragment_type)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_clusters_concept ON concept_clusters (central_concept)"
            )

            conn.commit()
        finally:
            conn.close()

    def _load_existing_fragments(self):
        """Load existing memory fragments from database"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("SELECT * FROM memory_fragments")
            for row in cursor.fetchall():
                fragment = self._row_to_fragment(row)
                self.fragments[fragment.fragment_id] = fragment
                self._update_indexes(fragment)
        finally:
            conn.close()

    def store_fragment(self, fragment: MemoryFragment) -> str:
        """Store a memory fragment in the fractal mesh"""
        self.fragments[fragment.fragment_id] = fragment
        self._update_indexes(fragment)
        self._persist_fragment(fragment)

        # Trigger clustering and chain detection
        self._update_concept_clusters(fragment)
        self._update_episodic_chains(fragment)

        return fragment.fragment_id

    def retrieve_by_concept(
        self, concept: str, limit: int = 10
    ) -> List[MemoryFragment]:
        """Retrieve fragments related to a concept"""
        related_fragment_ids = self.concept_index.get(concept, set())
        fragments = [
            self.fragments[fid] for fid in related_fragment_ids if fid in self.fragments
        ]

        # Sort by relevance (combination of confidence and recency)
        fragments.sort(
            key=lambda f: (
                f.confidence_score * 0.7 + self._temporal_relevance(f.created_at) * 0.3
            ),
            reverse=True,
        )

        return fragments[:limit]

    def retrieve_episodic_sequence(
        self, start_time: datetime, end_time: datetime, min_significance: float = 0.1
    ) -> List[EpisodicChain]:
        """Retrieve episodic chains within a time range"""
        relevant_chains = []

        for chain in self.episodic_chains.values():
            chain_start, chain_end = chain.temporal_span
            # Check for overlap with requested time range
            if (
                chain_start <= end_time
                and chain_end >= start_time
                and chain.significance_score >= min_significance
            ):
                relevant_chains.append(chain)

        # Sort by significance and temporal relevance
        relevant_chains.sort(key=lambda c: c.significance_score, reverse=True)
        return relevant_chains

    def find_analogous_patterns(
        self, query_fragment: MemoryFragment, limit: int = 5
    ) -> List[Tuple[MemoryFragment, float]]:
        """Find fragments with analogous patterns to the query"""
        similar_fragments = []
        query_concepts = query_fragment.symbolic_tags

        for fid, fragment in self.fragments.items():
            if fid == query_fragment.fragment_id:
                continue

            # Calculate similarity based on shared concepts and associative links
            concept_overlap = len(query_concepts & fragment.symbolic_tags)
            associative_strength = len(
                set(query_fragment.associative_links) & set(fragment.associative_links)
            )

            if concept_overlap > 0 or associative_strength > 0:
                similarity = (concept_overlap * 0.6 + associative_strength * 0.4) / max(
                    len(query_concepts | fragment.symbolic_tags), 1
                )
                similar_fragments.append((fragment, similarity))

        # Sort by similarity and return top matches
        similar_fragments.sort(key=lambda x: x[1], reverse=True)
        return similar_fragments[:limit]

    def detect_memory_drift(
        self, time_window: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Detect changes in memory patterns over time"""
        cutoff_time = datetime.now() - time_window
        recent_fragments = [
            f for f in self.fragments.values() if f.created_at >= cutoff_time
        ]

        # Analyze concept frequency changes
        recent_concepts = {}
        for fragment in recent_fragments:
            for concept in fragment.symbolic_tags:
                recent_concepts[concept] = recent_concepts.get(concept, 0) + 1

        # Compare with historical patterns (simplified)
        historical_fragments = [
            f for f in self.fragments.values() if f.created_at < cutoff_time
        ]
        historical_concepts = {}
        for fragment in historical_fragments[-100:]:  # Sample recent history
            for concept in fragment.symbolic_tags:
                historical_concepts[concept] = historical_concepts.get(concept, 0) + 1

        # Calculate drift metrics
        emerging_concepts = set(recent_concepts.keys()) - set(
            historical_concepts.keys()
        )
        declining_concepts = set(historical_concepts.keys()) - set(
            recent_concepts.keys()
        )

        return {
            "time_window": str(time_window),
            "total_recent_fragments": len(recent_fragments),
            "emerging_concepts": list(emerging_concepts),
            "declining_concepts": list(declining_concepts),
            "concept_frequency_changes": self._calculate_frequency_changes(
                recent_concepts, historical_concepts
            ),
        }

    def _update_indexes(self, fragment: MemoryFragment):
        """Update internal indexes with new fragment"""
        # Temporal index
        day_key = fragment.created_at.replace(hour=0, minute=0, second=0, microsecond=0)
        if day_key not in self.temporal_index:
            self.temporal_index[day_key] = []
        self.temporal_index[day_key].append(fragment.fragment_id)

        # Concept index
        for concept in fragment.symbolic_tags:
            if concept not in self.concept_index:
                self.concept_index[concept] = set()
            self.concept_index[concept].add(fragment.fragment_id)

        # Association graph
        if fragment.fragment_id not in self.association_graph:
            self.association_graph[fragment.fragment_id] = set()
        for linked_id in fragment.associative_links:
            self.association_graph[fragment.fragment_id].add(linked_id)
            # Bidirectional links
            if linked_id not in self.association_graph:
                self.association_graph[linked_id] = set()
            self.association_graph[linked_id].add(fragment.fragment_id)

    def _update_concept_clusters(self, fragment: MemoryFragment):
        """Update concept clusters based on new fragment"""
        # Simplified clustering - find existing clusters to join or create new
        for concept in fragment.symbolic_tags:
            existing_cluster = None
            for cluster in self.concept_clusters.values():
                if (
                    concept in cluster.related_concepts
                    or concept == cluster.central_concept
                ):
                    existing_cluster = cluster
                    break

            if existing_cluster:
                existing_cluster.member_fragments.add(fragment.fragment_id)
                existing_cluster.related_concepts.update(fragment.symbolic_tags)
            else:
                # Create new cluster
                cluster_id = str(uuid.uuid4())
                new_cluster = ConceptCluster(
                    cluster_id=cluster_id,
                    central_concept=concept,
                    related_concepts=fragment.symbolic_tags.copy(),
                    member_fragments={fragment.fragment_id},
                    cluster_strength=1.0,
                    temporal_evolution=[(datetime.now(), 1.0)],
                    narrative_themes=[],
                )
                self.concept_clusters[cluster_id] = new_cluster

    def _update_episodic_chains(self, fragment: MemoryFragment):
        """Update episodic chains based on temporal and causal relationships"""
        if fragment.fragment_type != MemoryFragmentType.EPISODIC:
            return

        # Find nearby fragments in time to potentially chain
        time_window = timedelta(hours=24)  # Look within 24 hours
        nearby_fragments = []

        for other_id, other_fragment in self.fragments.items():
            if (
                other_id != fragment.fragment_id
                and other_fragment.fragment_type == MemoryFragmentType.EPISODIC
                and abs(
                    (fragment.created_at - other_fragment.created_at).total_seconds()
                )
                <= time_window.total_seconds()
            ):
                nearby_fragments.append(other_fragment)

        if nearby_fragments:
            # Simplified chain creation - group by temporal proximity
            chain_id = str(uuid.uuid4())
            all_fragments = [fragment] + nearby_fragments
            all_fragments.sort(key=lambda f: f.created_at)

            new_chain = EpisodicChain(
                chain_id=chain_id,
                fragments=[f.fragment_id for f in all_fragments],
                narrative_arc="Temporal sequence",  # Would be enhanced by narrative generator
                causal_links={},  # Would be enhanced by causal analysis
                temporal_span=(
                    all_fragments[0].created_at,
                    all_fragments[-1].created_at,
                ),
                significance_score=sum(f.confidence_score for f in all_fragments)
                / len(all_fragments),
            )
            self.episodic_chains[chain_id] = new_chain

    def _temporal_relevance(self, timestamp: datetime) -> float:
        """Calculate temporal relevance (more recent = higher score)"""
        import math

        age_hours = (datetime.now() - timestamp).total_seconds() / 3600
        # Exponential decay with half-life of 7 days
        return math.exp(-age_hours / (7 * 24))

    def _calculate_frequency_changes(
        self, recent: Dict[str, int], historical: Dict[str, int]
    ) -> Dict[str, float]:
        """Calculate changes in concept frequencies"""
        changes = {}
        all_concepts = set(recent.keys()) | set(historical.keys())

        for concept in all_concepts:
            recent_freq = recent.get(concept, 0)
            historical_freq = historical.get(concept, 0)

            if historical_freq == 0:
                changes[concept] = float("inf") if recent_freq > 0 else 0
            else:
                changes[concept] = (recent_freq - historical_freq) / historical_freq

        return changes

    def _persist_fragment(self, fragment: MemoryFragment):
        """Persist fragment to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO memory_fragments
                (fragment_id, content, fragment_type, temporal_tags, symbolic_tags,
                 associative_links, confidence_score, access_pattern, narrative_role,
                 created_at, last_evolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    fragment.fragment_id,
                    json.dumps(fragment.content),
                    fragment.fragment_type.value,
                    json.dumps(fragment.temporal_tags),
                    json.dumps(list(fragment.symbolic_tags)),
                    json.dumps(fragment.associative_links),
                    fragment.confidence_score,
                    json.dumps(fragment.access_pattern),
                    fragment.narrative_role,
                    fragment.created_at.isoformat(),
                    fragment.last_evolved.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _row_to_fragment(self, row) -> MemoryFragment:
        """Convert database row to MemoryFragment object"""
        return MemoryFragment(
            fragment_id=row[0],
            content=json.loads(row[1]),
            fragment_type=MemoryFragmentType(row[2]),
            temporal_tags=json.loads(row[3]) if row[3] else {},
            symbolic_tags=set(json.loads(row[4])) if row[4] else set(),
            associative_links=json.loads(row[5]) if row[5] else [],
            confidence_score=row[6] or 1.0,
            access_pattern=json.loads(row[7]) if row[7] else {},
            narrative_role=row[8],
            created_at=datetime.fromisoformat(row[9]),
            last_evolved=datetime.fromisoformat(row[10]) if row[10] else datetime.now(),
        )
