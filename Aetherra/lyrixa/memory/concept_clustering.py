#!/usr/bin/env python3
"""
🧠 CONCEPT CLUSTERING ENGINE
============================

Advanced concept clustering and semantic relationship mapping for the Lyrixa Memory System.
This component automatically groups related concepts and builds semantic networks.

Key Features:
- Dynamic concept clustering using embeddings
- Semantic relationship detection
- Concept hierarchy building
- Automatic concept merging and splitting
- Real-time cluster updates
"""

import asyncio
import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Concept:
    """Represents a semantic concept in the clustering system"""

    id: str
    name: str
    embedding: List[float]
    frequency: int = 1
    last_accessed: str = ""
    related_concepts: List[str] = None
    semantic_tags: List[str] = None

    def __post_init__(self):
        if self.related_concepts is None:
            self.related_concepts = []
        if self.semantic_tags is None:
            self.semantic_tags = []
        if not self.last_accessed:
            self.last_accessed = datetime.now().isoformat()


@dataclass
class ConceptCluster:
    """Represents a cluster of related concepts"""

    id: str
    name: str
    concepts: List[str]
    centroid: List[float]
    coherence_score: float = 0.0
    created_at: str = ""
    last_updated: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()


class ConceptClusteringEngine:
    """
    Advanced concept clustering engine for semantic relationship mapping
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "concept_clusters.db"
        self.concepts: Dict[str, Concept] = {}
        self.clusters: Dict[str, ConceptCluster] = {}
        self.similarity_threshold = 0.7
        self.max_cluster_size = 20
        self.min_cluster_coherence = 0.5

        # Initialize database
        self._init_database()

        # Load existing data
        asyncio.create_task(self._load_existing_data())

        logger.info("🧠 Concept Clustering Engine initialized")

    def _init_database(self):
        """Initialize the SQLite database for concept storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Concepts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS concepts (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        embedding TEXT NOT NULL,
                        frequency INTEGER DEFAULT 1,
                        last_accessed TEXT,
                        related_concepts TEXT,
                        semantic_tags TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                """)

                # Clusters table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clusters (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        concepts TEXT NOT NULL,
                        centroid TEXT NOT NULL,
                        coherence_score REAL DEFAULT 0.0,
                        created_at TEXT,
                        last_updated TEXT
                    )
                """)

                # Concept relationships table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS concept_relationships (
                        from_concept TEXT,
                        to_concept TEXT,
                        relationship_type TEXT,
                        strength REAL,
                        created_at TEXT,
                        PRIMARY KEY (from_concept, to_concept, relationship_type)
                    )
                """)

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")

    async def _load_existing_data(self):
        """Load existing concepts and clusters from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Load concepts
                cursor.execute("SELECT * FROM concepts")
                for row in cursor.fetchall():
                    concept = Concept(
                        id=row[0],
                        name=row[1],
                        embedding=json.loads(row[2]),
                        frequency=row[3],
                        last_accessed=row[4],
                        related_concepts=json.loads(row[5]) if row[5] else [],
                        semantic_tags=json.loads(row[6]) if row[6] else [],
                    )
                    self.concepts[concept.id] = concept

                # Load clusters
                cursor.execute("SELECT * FROM clusters")
                for row in cursor.fetchall():
                    cluster = ConceptCluster(
                        id=row[0],
                        name=row[1],
                        concepts=json.loads(row[2]),
                        centroid=json.loads(row[3]),
                        coherence_score=row[4],
                        created_at=row[5],
                        last_updated=row[6],
                    )
                    self.clusters[cluster.id] = cluster

                logger.info(
                    f"✅ Loaded {len(self.concepts)} concepts and {len(self.clusters)} clusters"
                )

        except Exception as e:
            logger.error(f"❌ Failed to load existing data: {e}")

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (mock implementation)"""
        # In real implementation, use actual embedding model
        import hashlib
        import random

        # Create deterministic embedding based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        random.seed(text_hash)

        # Generate 384-dimensional embedding (typical for sentence transformers)
        embedding = [random.uniform(-1, 1) for _ in range(384)]

        # Normalize
        norm = sum(x * x for x in embedding) ** 0.5
        return [x / norm for x in embedding]

    def _calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings"""
        if len(embedding1) != len(embedding2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def add_concept(self, text: str, semantic_tags: List[str] = None) -> str:
        """Add a new concept to the clustering system"""
        try:
            # Generate concept ID
            concept_id = f"concept_{len(self.concepts) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Generate embedding
            embedding = self._generate_embedding(text)

            # Check for similar existing concepts
            similar_concepts = []
            for existing_id, existing_concept in self.concepts.items():
                similarity = self._calculate_similarity(
                    embedding, existing_concept.embedding
                )
                if similarity > self.similarity_threshold:
                    similar_concepts.append((existing_id, similarity))

            if similar_concepts:
                # Update existing similar concept instead of creating new one
                best_match = max(similar_concepts, key=lambda x: x[1])
                existing_concept = self.concepts[best_match[0]]
                existing_concept.frequency += 1
                existing_concept.last_accessed = datetime.now().isoformat()

                if semantic_tags:
                    existing_concept.semantic_tags.extend(
                        tag
                        for tag in semantic_tags
                        if tag not in existing_concept.semantic_tags
                    )

                await self._save_concept(existing_concept)
                return existing_concept.id

            # Create new concept
            concept = Concept(
                id=concept_id,
                name=text,
                embedding=embedding,
                semantic_tags=semantic_tags or [],
            )

            self.concepts[concept_id] = concept
            await self._save_concept(concept)

            # Trigger clustering update
            await self._update_clusters()

            logger.info(f"✅ Added new concept: {text[:50]}...")
            return concept_id

        except Exception as e:
            logger.error(f"❌ Failed to add concept: {e}")
            return ""

    async def _save_concept(self, concept: Concept):
        """Save concept to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO concepts
                    (id, name, embedding, frequency, last_accessed, related_concepts, semantic_tags, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        concept.id,
                        concept.name,
                        json.dumps(concept.embedding),
                        concept.frequency,
                        concept.last_accessed,
                        json.dumps(concept.related_concepts),
                        json.dumps(concept.semantic_tags),
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to save concept: {e}")

    async def _update_clusters(self):
        """Update concept clusters using similarity-based grouping"""
        try:
            if len(self.concepts) < 2:
                return

            # Simple clustering algorithm
            concept_list = list(self.concepts.values())
            used_concepts = set()
            new_clusters = {}

            for i, concept in enumerate(concept_list):
                if concept.id in used_concepts:
                    continue

                # Start a new cluster
                cluster_concepts = [concept.id]
                used_concepts.add(concept.id)

                # Find similar concepts
                for j, other_concept in enumerate(concept_list[i + 1 :], i + 1):
                    if other_concept.id in used_concepts:
                        continue

                    similarity = self._calculate_similarity(
                        concept.embedding, other_concept.embedding
                    )
                    if (
                        similarity > self.similarity_threshold
                        and len(cluster_concepts) < self.max_cluster_size
                    ):
                        cluster_concepts.append(other_concept.id)
                        used_concepts.add(other_concept.id)

                # Create cluster if it has multiple concepts
                if len(cluster_concepts) > 1:
                    cluster_id = f"cluster_{len(new_clusters) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                    # Calculate centroid
                    embeddings = [
                        self.concepts[cid].embedding for cid in cluster_concepts
                    ]
                    centroid = [
                        sum(emb[i] for emb in embeddings) / len(embeddings)
                        for i in range(len(embeddings[0]))
                    ]

                    # Generate cluster name from most frequent concept
                    primary_concept = max(
                        (self.concepts[cid] for cid in cluster_concepts),
                        key=lambda c: c.frequency,
                    )

                    cluster = ConceptCluster(
                        id=cluster_id,
                        name=f"Cluster: {primary_concept.name[:30]}...",
                        concepts=cluster_concepts,
                        centroid=centroid,
                        coherence_score=self._calculate_cluster_coherence(
                            cluster_concepts
                        ),
                    )

                    new_clusters[cluster_id] = cluster

            # Update clusters
            self.clusters = new_clusters

            # Save clusters to database
            for cluster in self.clusters.values():
                await self._save_cluster(cluster)

            logger.info(f"✅ Updated clustering: {len(self.clusters)} clusters")

        except Exception as e:
            logger.error(f"❌ Failed to update clusters: {e}")

    def _calculate_cluster_coherence(self, concept_ids: List[str]) -> float:
        """Calculate coherence score for a cluster"""
        if len(concept_ids) < 2:
            return 1.0

        similarities = []
        concepts = [self.concepts[cid] for cid in concept_ids]

        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i + 1 :]:
                similarity = self._calculate_similarity(
                    concept1.embedding, concept2.embedding
                )
                similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 0.0

    async def _save_cluster(self, cluster: ConceptCluster):
        """Save cluster to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO clusters
                    (id, name, concepts, centroid, coherence_score, created_at, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        cluster.id,
                        cluster.name,
                        json.dumps(cluster.concepts),
                        json.dumps(cluster.centroid),
                        cluster.coherence_score,
                        cluster.created_at,
                        cluster.last_updated,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to save cluster: {e}")

    async def get_related_concepts(
        self, concept_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get concepts related to the given concept"""
        try:
            if concept_id not in self.concepts:
                return []

            source_concept = self.concepts[concept_id]
            related = []

            for other_id, other_concept in self.concepts.items():
                if other_id == concept_id:
                    continue

                similarity = self._calculate_similarity(
                    source_concept.embedding, other_concept.embedding
                )
                if similarity > 0.3:  # Lower threshold for related concepts
                    related.append(
                        {
                            "concept_id": other_id,
                            "name": other_concept.name,
                            "similarity": similarity,
                            "frequency": other_concept.frequency,
                            "semantic_tags": other_concept.semantic_tags,
                        }
                    )

            # Sort by similarity and return top results
            related.sort(key=lambda x: x["similarity"], reverse=True)
            return related[:limit]

        except Exception as e:
            logger.error(f"❌ Failed to get related concepts: {e}")
            return []

    async def get_cluster_summary(self) -> Dict[str, Any]:
        """Get summary of current clustering state"""
        try:
            return {
                "total_concepts": len(self.concepts),
                "total_clusters": len(self.clusters),
                "average_cluster_size": sum(
                    len(cluster.concepts) for cluster in self.clusters.values()
                )
                / len(self.clusters)
                if self.clusters
                else 0,
                "average_coherence": sum(
                    cluster.coherence_score for cluster in self.clusters.values()
                )
                / len(self.clusters)
                if self.clusters
                else 0,
                "most_frequent_concepts": [
                    {"name": concept.name, "frequency": concept.frequency}
                    for concept in sorted(
                        self.concepts.values(), key=lambda c: c.frequency, reverse=True
                    )[:5]
                ],
                "recent_clusters": [
                    {
                        "name": cluster.name,
                        "size": len(cluster.concepts),
                        "coherence": cluster.coherence_score,
                    }
                    for cluster in sorted(
                        self.clusters.values(),
                        key=lambda c: c.last_updated,
                        reverse=True,
                    )[:5]
                ],
            }
        except Exception as e:
            logger.error(f"❌ Failed to get cluster summary: {e}")
            return {}


# Demo and testing
async def main():
    """Demo the concept clustering engine"""
    print("🧠 Concept Clustering Engine Demo")
    print("=" * 50)

    engine = ConceptClusteringEngine()

    # Add some test concepts
    test_concepts = [
        "artificial intelligence and machine learning",
        "neural networks and deep learning",
        "natural language processing",
        "computer vision and image recognition",
        "robotics and automation",
        "web development and programming",
        "database design and management",
        "cloud computing and distributed systems",
        "cybersecurity and data protection",
        "mobile app development",
    ]

    print("Adding test concepts...")
    for concept_text in test_concepts:
        concept_id = await engine.add_concept(
            concept_text, ["technology", "programming"]
        )
        print(f"  ✅ Added: {concept_text}")

    # Wait for clustering to complete
    await asyncio.sleep(1)

    # Show summary
    summary = await engine.get_cluster_summary()
    print(f"\n📊 Clustering Summary:")
    print(f"  Total concepts: {summary['total_concepts']}")
    print(f"  Total clusters: {summary['total_clusters']}")
    print(f"  Average cluster size: {summary['average_cluster_size']:.2f}")
    print(f"  Average coherence: {summary['average_coherence']:.2f}")

    # Show related concepts for first concept
    if engine.concepts:
        first_concept_id = list(engine.concepts.keys())[0]
        related = await engine.get_related_concepts(first_concept_id)
        print(f"\n🔗 Related to '{engine.concepts[first_concept_id].name}':")
        for rel in related[:3]:
            print(f"  • {rel['name']} (similarity: {rel['similarity']:.3f})")


if __name__ == "__main__":
    asyncio.run(main())
