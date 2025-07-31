"""
🎯 Concept Clustering Manager
============================

Manages symbolic clusters of memory fragments around central themes.
Enables thematic recall, contradiction detection, and concept evolution tracking.
"""

import json
import math
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from ..base import ConceptCluster, MemoryFragment, MemoryFragmentType


@dataclass
class ConceptEvolution:
    """Tracks how a concept has evolved over time"""

    concept: str
    timestamps: List[datetime]
    confidence_scores: List[float]
    associated_fragments: List[str]
    narrative_contexts: List[str]


@dataclass
class ConceptContradiction:
    """Represents detected contradictions within a concept cluster"""

    concept: str
    contradicting_fragments: List[Tuple[str, str]]  # Pairs of conflicting fragment IDs
    contradiction_type: str  # "temporal", "semantic", "causal"
    confidence: float
    detected_at: datetime


class ConceptClusterManager:
    """
    Manages symbolic memory clusters around central concepts/themes

    Features:
    - Automatic concept extraction and clustering
    - Temporal evolution tracking
    - Contradiction detection
    - Concept drift analysis
    - Narrative theme identification
    """

    def __init__(self, db_path: str = "concept_clusters.db"):
        self.db_path = db_path
        self.clusters: Dict[str, ConceptCluster] = {}
        self.concept_evolution: Dict[str, ConceptEvolution] = {}
        self.detected_contradictions: List[ConceptContradiction] = []
        self.concept_similarity_threshold = 0.7
        self.min_cluster_size = 3

        self._init_database()
        self._load_existing_clusters()

    def _init_database(self):
        """Initialize concept clustering database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS concept_clusters (
                    cluster_id TEXT PRIMARY KEY,
                    central_concept TEXT NOT NULL,
                    related_concepts TEXT,
                    member_fragments TEXT,
                    cluster_strength REAL,
                    temporal_evolution TEXT,
                    narrative_themes TEXT,
                    created_at TEXT,
                    last_updated TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS concept_evolution (
                    concept TEXT PRIMARY KEY,
                    timestamps TEXT,
                    confidence_scores TEXT,
                    associated_fragments TEXT,
                    narrative_contexts TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS concept_contradictions (
                    contradiction_id TEXT PRIMARY KEY,
                    concept TEXT NOT NULL,
                    contradicting_fragments TEXT,
                    contradiction_type TEXT,
                    confidence REAL,
                    detected_at TEXT
                )
            """)

            conn.commit()
        finally:
            conn.close()

    def _load_existing_clusters(self):
        """Load existing clusters from database"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Load clusters
            cursor = conn.execute("SELECT * FROM concept_clusters")
            for row in cursor.fetchall():
                cluster = self._row_to_cluster(row)
                self.clusters[cluster.cluster_id] = cluster

            # Load evolution data
            cursor = conn.execute("SELECT * FROM concept_evolution")
            for row in cursor.fetchall():
                evolution = self._row_to_evolution(row)
                self.concept_evolution[evolution.concept] = evolution

        finally:
            conn.close()

    def process_new_fragment(self, fragment: MemoryFragment) -> List[str]:
        """Process a new memory fragment for concept clustering"""
        affected_clusters = []

        # Extract concepts from the fragment
        fragment_concepts = self._extract_concepts(fragment)

        # Update or create clusters
        for concept in fragment_concepts:
            cluster_id = self._find_or_create_cluster(concept, fragment)
            if cluster_id:
                affected_clusters.append(cluster_id)
                self._update_concept_evolution(concept, fragment)

        # Check for contradictions
        self._check_contradictions(fragment, fragment_concepts)

        return affected_clusters

    def _extract_concepts(self, fragment: MemoryFragment) -> Set[str]:
        """Extract concepts from a memory fragment"""
        concepts = set()

        # Use existing symbolic tags
        concepts.update(fragment.symbolic_tags)

        # Extract concepts from content (simplified keyword extraction)
        if isinstance(fragment.content, dict):
            text_content = " ".join(str(v) for v in fragment.content.values())
        else:
            text_content = str(fragment.content)

        # Simple concept extraction (would be enhanced with NLP)
        concept_keywords = self._extract_keywords(text_content)
        concepts.update(concept_keywords)

        return concepts

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text (simplified approach)"""
        # This would be enhanced with proper NLP libraries like spaCy or NLTK
        import re

        # Clean and normalize text
        text = re.sub(r"[^\w\s]", " ", text.lower())
        words = text.split()

        # Filter out common stop words and short words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
        }

        meaningful_words = {
            word for word in words if len(word) > 2 and word not in stop_words
        }

        return meaningful_words

    def _find_or_create_cluster(
        self, concept: str, fragment: MemoryFragment
    ) -> Optional[str]:
        """Find existing cluster for concept or create new one"""
        # Look for existing cluster with this concept
        for cluster_id, cluster in self.clusters.items():
            if (
                concept == cluster.central_concept
                or concept in cluster.related_concepts
            ):
                # Add fragment to existing cluster
                cluster.member_fragments.add(fragment.fragment_id)
                cluster.related_concepts.update(fragment.symbolic_tags)
                cluster.cluster_strength = self._calculate_cluster_strength(cluster)
                self._persist_cluster(cluster)
                return cluster_id

        # Check if we should create a cluster with similar concepts
        similar_cluster = self._find_similar_cluster(concept, fragment)
        if similar_cluster:
            similar_cluster.related_concepts.add(concept)
            similar_cluster.member_fragments.add(fragment.fragment_id)
            similar_cluster.cluster_strength = self._calculate_cluster_strength(
                similar_cluster
            )
            self._persist_cluster(similar_cluster)
            return similar_cluster.cluster_id

        # Create new cluster
        cluster_id = str(uuid.uuid4())
        new_cluster = ConceptCluster(
            cluster_id=cluster_id,
            central_concept=concept,
            related_concepts=fragment.symbolic_tags.copy(),
            member_fragments={fragment.fragment_id},
            cluster_strength=1.0,
            temporal_evolution=[(datetime.now(), fragment.confidence_score)],
            narrative_themes=self._extract_narrative_themes(fragment),
        )

        self.clusters[cluster_id] = new_cluster
        self._persist_cluster(new_cluster)
        return cluster_id

    def _find_similar_cluster(
        self, concept: str, fragment: MemoryFragment
    ) -> Optional[ConceptCluster]:
        """Find cluster with similar concepts"""
        best_cluster = None
        best_similarity = 0.0

        for cluster in self.clusters.values():
            # Calculate concept similarity
            all_cluster_concepts = {cluster.central_concept} | cluster.related_concepts
            fragment_concepts = {concept} | fragment.symbolic_tags

            intersection = len(all_cluster_concepts & fragment_concepts)
            union = len(all_cluster_concepts | fragment_concepts)

            if union > 0:
                similarity = intersection / union
                if (
                    similarity > best_similarity
                    and similarity >= self.concept_similarity_threshold
                ):
                    best_similarity = similarity
                    best_cluster = cluster

        return best_cluster

    def _calculate_cluster_strength(self, cluster: ConceptCluster) -> float:
        """Calculate the strength/coherence of a concept cluster"""
        # Factors: number of fragments, concept overlap, temporal consistency

        fragment_count = len(cluster.member_fragments)
        concept_diversity = len(cluster.related_concepts)

        # Normalize by fragment count (more fragments = stronger, but diminishing returns)
        strength = math.log(fragment_count + 1) / math.log(10)

        # Adjust for concept diversity (some diversity good, too much bad)
        diversity_factor = min(
            concept_diversity / 10, 1.0
        )  # Optimal around 10 concepts
        strength *= 0.5 + 0.5 * diversity_factor

        return min(strength, 1.0)

    def _update_concept_evolution(self, concept: str, fragment: MemoryFragment):
        """Update the evolution tracking for a concept"""
        if concept not in self.concept_evolution:
            self.concept_evolution[concept] = ConceptEvolution(
                concept=concept,
                timestamps=[],
                confidence_scores=[],
                associated_fragments=[],
                narrative_contexts=[],
            )

        evolution = self.concept_evolution[concept]
        evolution.timestamps.append(fragment.created_at)
        evolution.confidence_scores.append(fragment.confidence_score)
        evolution.associated_fragments.append(fragment.fragment_id)

        # Extract narrative context
        if fragment.narrative_role:
            evolution.narrative_contexts.append(fragment.narrative_role)
        else:
            evolution.narrative_contexts.append("general")

        # Persist evolution data
        self._persist_concept_evolution(evolution)

    def _check_contradictions(self, fragment: MemoryFragment, concepts: Set[str]):
        """Check for contradictions with existing fragments in the same concepts"""
        for concept in concepts:
            # Find other fragments with this concept
            related_fragments = self._get_fragments_for_concept(concept)

            for other_fragment_id in related_fragments:
                if other_fragment_id != fragment.fragment_id:
                    contradiction = self._detect_contradiction(
                        fragment, other_fragment_id
                    )
                    if contradiction:
                        self.detected_contradictions.append(contradiction)
                        self._persist_contradiction(contradiction)

    def _detect_contradiction(
        self, fragment1: MemoryFragment, fragment2_id: str
    ) -> Optional[ConceptContradiction]:
        """Detect if two fragments contradict each other (simplified)"""
        # This would be enhanced with semantic analysis

        # For now, simple keyword-based contradiction detection
        content1 = str(fragment1.content).lower()

        # Would need access to fragment2 content - simplified for now
        contradiction_keywords = [
            ("success", "failure"),
            ("good", "bad"),
            ("yes", "no"),
            ("true", "false"),
            ("works", "broken"),
            ("correct", "wrong"),
        ]

        for pos_word, neg_word in contradiction_keywords:
            if pos_word in content1 and neg_word in content1:
                return ConceptContradiction(
                    concept="mixed",  # Would identify specific concept
                    contradicting_fragments=[(fragment1.fragment_id, fragment2_id)],
                    contradiction_type="semantic",
                    confidence=0.7,  # Would calculate properly
                    detected_at=datetime.now(),
                )

        return None

    def _get_fragments_for_concept(self, concept: str) -> List[str]:
        """Get all fragment IDs associated with a concept"""
        fragment_ids = []

        for cluster in self.clusters.values():
            if (
                concept == cluster.central_concept
                or concept in cluster.related_concepts
            ):
                fragment_ids.extend(cluster.member_fragments)

        return list(set(fragment_ids))  # Remove duplicates

    def _extract_narrative_themes(self, fragment: MemoryFragment) -> List[str]:
        """Extract narrative themes from fragment content"""
        # Simplified theme extraction
        themes = []

        if fragment.narrative_role:
            themes.append(fragment.narrative_role)

        # Add themes based on fragment type
        if fragment.fragment_type == MemoryFragmentType.EPISODIC:
            themes.append("experience")
        elif fragment.fragment_type == MemoryFragmentType.SEMANTIC:
            themes.append("knowledge")
        elif fragment.fragment_type == MemoryFragmentType.EMOTIONAL:
            themes.append("emotional")

        return themes

    def get_concept_clusters(self, min_strength: float = 0.1) -> List[ConceptCluster]:
        """Get all concept clusters above minimum strength"""
        return [
            cluster
            for cluster in self.clusters.values()
            if cluster.cluster_strength >= min_strength
        ]

    def get_concept_evolution(self, concept: str) -> Optional[ConceptEvolution]:
        """Get evolution data for a specific concept"""
        return self.concept_evolution.get(concept)

    def get_recent_contradictions(self, days: int = 7) -> List[ConceptContradiction]:
        """Get contradictions detected in the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        return [c for c in self.detected_contradictions if c.detected_at >= cutoff]

    def analyze_concept_drift(
        self, concept: str, time_window: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Analyze how a concept has drifted over time"""
        evolution = self.concept_evolution.get(concept)
        if not evolution:
            return {"error": "Concept not found"}

        cutoff = datetime.now() - time_window
        recent_indices = [
            i for i, ts in enumerate(evolution.timestamps) if ts >= cutoff
        ]

        if not recent_indices:
            return {"error": "No recent data for concept"}

        recent_confidence = [evolution.confidence_scores[i] for i in recent_indices]
        recent_contexts = [evolution.narrative_contexts[i] for i in recent_indices]

        # Calculate confidence trend
        confidence_trend = "stable"
        if len(recent_confidence) > 1:
            trend_slope = (recent_confidence[-1] - recent_confidence[0]) / len(
                recent_confidence
            )
            if trend_slope > 0.1:
                confidence_trend = "increasing"
            elif trend_slope < -0.1:
                confidence_trend = "decreasing"

        # Analyze context diversity
        unique_contexts = set(recent_contexts)
        context_diversity = (
            len(unique_contexts) / len(recent_contexts) if recent_contexts else 0
        )

        return {
            "concept": concept,
            "time_window": str(time_window),
            "recent_occurrences": len(recent_indices),
            "confidence_trend": confidence_trend,
            "average_confidence": sum(recent_confidence) / len(recent_confidence),
            "context_diversity": context_diversity,
            "dominant_contexts": list(unique_contexts),
        }

    def _persist_cluster(self, cluster: ConceptCluster):
        """Persist cluster to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO concept_clusters
                (cluster_id, central_concept, related_concepts, member_fragments,
                 cluster_strength, temporal_evolution, narrative_themes, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    cluster.cluster_id,
                    cluster.central_concept,
                    json.dumps(list(cluster.related_concepts)),
                    json.dumps(list(cluster.member_fragments)),
                    cluster.cluster_strength,
                    json.dumps(
                        [
                            (ts.isoformat(), score)
                            for ts, score in cluster.temporal_evolution
                        ]
                    ),
                    json.dumps(cluster.narrative_themes),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _persist_concept_evolution(self, evolution: ConceptEvolution):
        """Persist concept evolution to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO concept_evolution
                (concept, timestamps, confidence_scores, associated_fragments, narrative_contexts)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    evolution.concept,
                    json.dumps([ts.isoformat() for ts in evolution.timestamps]),
                    json.dumps(evolution.confidence_scores),
                    json.dumps(evolution.associated_fragments),
                    json.dumps(evolution.narrative_contexts),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _persist_contradiction(self, contradiction: ConceptContradiction):
        """Persist detected contradiction to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            contradiction_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO concept_contradictions
                (contradiction_id, concept, contradicting_fragments, contradiction_type,
                 confidence, detected_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    contradiction_id,
                    contradiction.concept,
                    json.dumps(
                        [list(pair) for pair in contradiction.contradicting_fragments]
                    ),
                    contradiction.contradiction_type,
                    contradiction.confidence,
                    contradiction.detected_at.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _row_to_cluster(self, row) -> ConceptCluster:
        """Convert database row to ConceptCluster object"""
        temporal_evolution_data = json.loads(row[5]) if row[5] else []
        temporal_evolution = [
            (datetime.fromisoformat(ts), score) for ts, score in temporal_evolution_data
        ]

        return ConceptCluster(
            cluster_id=row[0],
            central_concept=row[1],
            related_concepts=set(json.loads(row[2])) if row[2] else set(),
            member_fragments=set(json.loads(row[3])) if row[3] else set(),
            cluster_strength=row[4] or 1.0,
            temporal_evolution=temporal_evolution,
            narrative_themes=json.loads(row[6]) if row[6] else [],
        )

    def _row_to_evolution(self, row) -> ConceptEvolution:
        """Convert database row to ConceptEvolution object"""
        return ConceptEvolution(
            concept=row[0],
            timestamps=[datetime.fromisoformat(ts) for ts in json.loads(row[1])],
            confidence_scores=json.loads(row[2]),
            associated_fragments=json.loads(row[3]),
            narrative_contexts=json.loads(row[4]),
        )
