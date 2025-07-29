#!/usr/bin/env python3
"""
🚀 AETHERRA QFAC Phase 2: Fractal Hierarchies Extension
=================================================================

Extension to ConceptClusters for fractal memory hierarchies.
Enables recursive pattern organization and multi-level abstraction.

Core Features:
• Hierarchical fractal cluster organization
• Multi-level pattern abstraction
• Recursive similarity mapping
• Dynamic hierarchy restructuring
• Cross-level pattern bridging
"""

import asyncio
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from fractal_encoder import FractalEncoder, FractalPattern


@dataclass
class FractalCluster:
    """Represents a fractal cluster in the hierarchy"""

    cluster_id: str
    level: int  # Hierarchy level (0=leaf, higher=more abstract)
    parent_cluster_id: Optional[str]  # Parent cluster (None for root)
    child_cluster_ids: List[str]  # Child clusters
    pattern_ids: List[str]  # Patterns belonging to this cluster
    fractal_signature: str  # Unique signature of the fractal structure
    similarity_threshold: float  # Minimum similarity for cluster membership
    compression_ratio: float  # Compression achieved by this cluster
    abstraction_level: int  # Conceptual abstraction level
    coherence_score: float  # How coherent/consistent the cluster is
    temporal_stability: float  # How stable the cluster is over time
    created_at: float
    last_updated: float


@dataclass
class HierarchyMetrics:
    """Metrics for fractal hierarchy performance"""

    total_levels: int
    total_clusters: int
    avg_branching_factor: float
    max_depth: int
    compression_efficiency: float
    hierarchy_coherence: float
    pattern_coverage: float
    reorganization_frequency: float


class FractalHierarchies:
    """
    Advanced fractal hierarchies for multi-level pattern organization
    """

    def __init__(
        self,
        fractal_encoder: FractalEncoder,
        data_dir: str = "fractal_hierarchies_data",
    ):
        self.encoder = fractal_encoder
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Database for fractal hierarchies
        self.db_path = self.data_dir / "fractal_hierarchies.db"
        self._init_database()

        # Hierarchy configuration
        self.max_hierarchy_depth = 8
        self.min_cluster_size = 3
        self.default_similarity_threshold = 0.7
        self.reorganization_trigger = 0.6  # Reorganize when coherence drops below this

        # Hierarchy cache
        self.cluster_cache: Dict[str, FractalCluster] = {}
        self.hierarchy_cache: Dict[int, List[FractalCluster]] = {}

        # Performance tracking
        self.hierarchy_stats = {
            "clusters_created": 0,
            "hierarchies_built": 0,
            "reorganizations": 0,
            "total_processing_time": 0.0,
        }

        print("🌳 FractalHierarchies initialized")
        print(f"   📁 Data directory: {self.data_dir}")
        print(f"   🗃️ Database: {self.db_path}")
        print(f"   📊 Max depth: {self.max_hierarchy_depth}")
        print(f"   🎯 Min cluster size: {self.min_cluster_size}")

    def _init_database(self):
        """Initialize SQLite database for fractal hierarchies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Fractal clusters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fractal_clusters (
                cluster_id TEXT PRIMARY KEY,
                level INTEGER,
                parent_cluster_id TEXT,
                child_cluster_ids TEXT,
                pattern_ids TEXT,
                fractal_signature TEXT,
                similarity_threshold REAL,
                compression_ratio REAL,
                abstraction_level INTEGER,
                coherence_score REAL,
                temporal_stability REAL,
                created_at REAL,
                last_updated REAL
            )
        """)

        # Hierarchy metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hierarchy_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                total_levels INTEGER,
                total_clusters INTEGER,
                avg_branching_factor REAL,
                max_depth INTEGER,
                compression_efficiency REAL,
                hierarchy_coherence REAL,
                pattern_coverage REAL,
                reorganization_frequency REAL
            )
        """)

        # Cross-level bridges table (for patterns that span multiple levels)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cross_level_bridges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_cluster_id TEXT,
                target_cluster_id TEXT,
                bridge_type TEXT,
                bridge_strength REAL,
                pattern_overlap TEXT,
                created_at REAL
            )
        """)

        conn.commit()
        conn.close()
        print("   📋 Fractal hierarchies database initialized")

    async def build_fractal_hierarchy(
        self, pattern_ids: Optional[List[str]] = None
    ) -> Dict[int, List[FractalCluster]]:
        """
        Build a complete fractal hierarchy from patterns
        """
        print("🌳 Building fractal hierarchy...")
        start_time = time.time()

        # Load patterns to organize
        if pattern_ids is None:
            patterns = await self.encoder._load_existing_patterns()
        else:
            patterns = await self._load_specific_patterns(pattern_ids)

        if not patterns:
            print("   ⚠️ No patterns found to organize")
            return {}

        print(f"   📋 Organizing {len(patterns)} patterns")

        # Build hierarchy level by level
        hierarchy = {}
        current_level_patterns = patterns
        level = 0

        while current_level_patterns and level < self.max_hierarchy_depth:
            print(f"   🔄 Building level {level}...")

            # Create clusters for current level
            level_clusters = await self._create_level_clusters(
                current_level_patterns, level
            )
            hierarchy[level] = level_clusters

            print(f"   ✅ Level {level}: {len(level_clusters)} clusters")

            # Prepare for next level by creating meta-patterns from clusters
            if len(level_clusters) > 1:
                current_level_patterns = await self._create_meta_patterns(
                    level_clusters, level
                )
                level += 1
            else:
                break

        # Store hierarchy
        await self._store_hierarchy(hierarchy)

        # Update cache
        self.hierarchy_cache = hierarchy

        # Calculate and store metrics
        metrics = await self._calculate_hierarchy_metrics(hierarchy)
        await self._store_hierarchy_metrics(metrics)

        processing_time = time.time() - start_time
        self.hierarchy_stats["hierarchies_built"] += 1
        self.hierarchy_stats["total_processing_time"] += processing_time

        print(f"   ✅ Hierarchy built: {len(hierarchy)} levels, {processing_time:.2f}s")
        print(
            f"   📊 Metrics: {metrics.total_clusters} clusters, {metrics.compression_efficiency:.1%} efficiency"
        )

        return hierarchy

    async def _create_level_clusters(
        self, patterns: List[FractalPattern], level: int
    ) -> List[FractalCluster]:
        """Create clusters for a specific hierarchy level"""

        if not patterns:
            return []

        clusters = []
        remaining_patterns = patterns.copy()

        while remaining_patterns:
            # Start new cluster with highest frequency pattern
            seed_pattern = max(
                remaining_patterns, key=lambda p: p.frequency * p.compression_ratio
            )
            cluster_patterns = [seed_pattern]
            remaining_patterns.remove(seed_pattern)

            # Find similar patterns for this cluster
            for pattern in remaining_patterns.copy():
                similarity = await self._calculate_cluster_similarity(
                    seed_pattern, pattern
                )

                if similarity >= self.default_similarity_threshold:
                    cluster_patterns.append(pattern)
                    remaining_patterns.remove(pattern)

            # Create cluster if it meets minimum size requirements
            if len(cluster_patterns) >= self.min_cluster_size or level > 0:
                cluster = await self._create_fractal_cluster(cluster_patterns, level)
                clusters.append(cluster)
                self.hierarchy_stats["clusters_created"] += 1

        return clusters

    async def _create_fractal_cluster(
        self, patterns: List[FractalPattern], level: int
    ) -> FractalCluster:
        """Create a fractal cluster from patterns"""

        # Generate cluster ID
        pattern_hash = "_".join(sorted(p.pattern_id for p in patterns))
        cluster_id = f"cluster_L{level}_{hash(pattern_hash) % 100000}"

        # Calculate fractal signature
        fractal_signature = await self._calculate_fractal_signature(patterns)

        # Calculate cluster metrics
        compression_ratio = sum(p.compression_ratio for p in patterns) / len(patterns)
        abstraction_level = max(p.abstraction_level for p in patterns) + level
        coherence_score = await self._calculate_cluster_coherence(patterns)

        cluster = FractalCluster(
            cluster_id=cluster_id,
            level=level,
            parent_cluster_id=None,  # Will be set when building parent levels
            child_cluster_ids=[],
            pattern_ids=[p.pattern_id for p in patterns],
            fractal_signature=fractal_signature,
            similarity_threshold=self.default_similarity_threshold,
            compression_ratio=compression_ratio,
            abstraction_level=abstraction_level,
            coherence_score=coherence_score,
            temporal_stability=1.0,  # Initial stability
            created_at=time.time(),
            last_updated=time.time(),
        )

        # Store in database
        await self._store_fractal_cluster(cluster)

        return cluster

    async def _calculate_cluster_similarity(
        self, pattern1: FractalPattern, pattern2: FractalPattern
    ) -> float:
        """Calculate similarity between patterns for clustering"""

        # Use the encoder's pattern similarity calculation
        return await self.encoder._calculate_pattern_similarity(pattern1, pattern2)

    async def _calculate_fractal_signature(self, patterns: List[FractalPattern]) -> str:
        """Calculate unique fractal signature for a cluster"""

        # Combine pattern types and abstraction levels
        type_signature = "_".join(sorted(p.pattern_type for p in patterns))
        level_signature = "_".join(
            str(p.abstraction_level)
            for p in sorted(patterns, key=lambda x: x.abstraction_level)
        )
        frequency_signature = "_".join(
            str(p.frequency)
            for p in sorted(patterns, key=lambda x: x.frequency, reverse=True)
        )

        combined = f"{type_signature}|{level_signature}|{frequency_signature}"
        return f"fractal_{hash(combined) % 1000000}"

    async def _calculate_cluster_coherence(
        self, patterns: List[FractalPattern]
    ) -> float:
        """Calculate how coherent/consistent a cluster is"""

        if len(patterns) <= 1:
            return 1.0

        # Calculate pairwise similarities
        total_similarity = 0.0
        pairs = 0

        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                similarity = await self._calculate_cluster_similarity(
                    patterns[i], patterns[j]
                )
                total_similarity += similarity
                pairs += 1

        return total_similarity / pairs if pairs > 0 else 0.0

    async def _create_meta_patterns(
        self, clusters: List[FractalCluster], level: int
    ) -> List[FractalPattern]:
        """Create meta-patterns from clusters for next hierarchy level"""

        meta_patterns = []

        for cluster in clusters:
            # Create a meta-pattern representing this cluster
            meta_pattern = FractalPattern(
                pattern_id=f"meta_{cluster.cluster_id}",
                pattern_type="archetype",  # Meta-patterns are archetypes
                content_hash=cluster.fractal_signature,
                similarity_score=cluster.coherence_score,
                frequency=len(cluster.pattern_ids),
                compression_ratio=cluster.compression_ratio,
                abstraction_level=cluster.abstraction_level,
                parent_patterns=[],
                child_patterns=cluster.pattern_ids,
                instances=[
                    {
                        "cluster_id": cluster.cluster_id,
                        "level": cluster.level,
                        "pattern_count": len(cluster.pattern_ids),
                    }
                ],
                created_at=cluster.created_at,
                last_seen=cluster.last_updated,
            )
            meta_patterns.append(meta_pattern)

        return meta_patterns

    async def _store_hierarchy(self, hierarchy: Dict[int, List[FractalCluster]]):
        """Store hierarchy and update parent-child relationships"""

        # Update parent-child relationships
        for level in sorted(hierarchy.keys()):
            if level + 1 in hierarchy:
                # Map child clusters to parent clusters
                child_clusters = hierarchy[level]
                parent_clusters = hierarchy[level + 1]

                for parent in parent_clusters:
                    # Find child clusters that belong to this parent
                    for child in child_clusters:
                        # Check if child's patterns overlap with parent's patterns
                        if await self._check_parent_child_relationship(child, parent):
                            child.parent_cluster_id = parent.cluster_id
                            parent.child_cluster_ids.append(child.cluster_id)

                            # Update in database
                            await self._store_fractal_cluster(child)
                            await self._store_fractal_cluster(parent)

    async def _check_parent_child_relationship(
        self, child: FractalCluster, parent: FractalCluster
    ) -> bool:
        """Check if child cluster should belong to parent cluster"""

        # Check pattern overlap
        child_patterns = set(child.pattern_ids)
        parent_patterns = set(parent.pattern_ids)

        # If parent contains meta-patterns derived from child, it's a parent
        if f"meta_{child.cluster_id}" in parent.pattern_ids:
            return True

        # Check abstraction level relationship
        if parent.abstraction_level > child.abstraction_level:
            # Check if there's sufficient conceptual overlap
            overlap = len(child_patterns & parent_patterns)
            overlap_ratio = overlap / len(child_patterns) if child_patterns else 0.0
            return overlap_ratio >= 0.3  # 30% overlap threshold

        return False

    async def _store_fractal_cluster(self, cluster: FractalCluster):
        """Store fractal cluster in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO fractal_clusters (
                cluster_id, level, parent_cluster_id, child_cluster_ids, pattern_ids,
                fractal_signature, similarity_threshold, compression_ratio, abstraction_level,
                coherence_score, temporal_stability, created_at, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                cluster.cluster_id,
                cluster.level,
                cluster.parent_cluster_id,
                json.dumps(cluster.child_cluster_ids),
                json.dumps(cluster.pattern_ids),
                cluster.fractal_signature,
                cluster.similarity_threshold,
                cluster.compression_ratio,
                cluster.abstraction_level,
                cluster.coherence_score,
                cluster.temporal_stability,
                cluster.created_at,
                cluster.last_updated,
            ),
        )

        conn.commit()
        conn.close()

    async def _load_specific_patterns(
        self, pattern_ids: List[str]
    ) -> List[FractalPattern]:
        """Load specific patterns by IDs"""
        conn = sqlite3.connect(self.encoder.db_path)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in pattern_ids)
        cursor.execute(
            f"SELECT * FROM fractal_patterns WHERE pattern_id IN ({placeholders})",
            pattern_ids,
        )
        rows = cursor.fetchall()
        conn.close()

        patterns = []
        for row in rows:
            pattern = FractalPattern(
                pattern_id=row[0],
                pattern_type=row[1],
                content_hash=row[2],
                similarity_score=row[3],
                frequency=row[4],
                compression_ratio=row[5],
                abstraction_level=row[6],
                parent_patterns=json.loads(row[7]) if row[7] else [],
                child_patterns=json.loads(row[8]) if row[8] else [],
                instances=json.loads(row[9]) if row[9] else [],
                created_at=row[10],
                last_seen=row[11],
            )
            patterns.append(pattern)

        return patterns

    async def _calculate_hierarchy_metrics(
        self, hierarchy: Dict[int, List[FractalCluster]]
    ) -> HierarchyMetrics:
        """Calculate comprehensive hierarchy metrics"""

        if not hierarchy:
            return HierarchyMetrics(0, 0, 0.0, 0, 0.0, 0.0, 0.0, 0.0)

        total_levels = len(hierarchy)
        total_clusters = sum(len(clusters) for clusters in hierarchy.values())
        max_depth = max(hierarchy.keys()) if hierarchy else 0

        # Calculate branching factor
        branching_factors = []
        for level, clusters in hierarchy.items():
            for cluster in clusters:
                if cluster.child_cluster_ids:
                    branching_factors.append(len(cluster.child_cluster_ids))

        avg_branching_factor = (
            sum(branching_factors) / len(branching_factors)
            if branching_factors
            else 0.0
        )

        # Calculate compression efficiency
        all_compression_ratios = []
        for clusters in hierarchy.values():
            all_compression_ratios.extend(
                cluster.compression_ratio for cluster in clusters
            )

        compression_efficiency = (
            sum(all_compression_ratios) / len(all_compression_ratios)
            if all_compression_ratios
            else 0.0
        )

        # Calculate hierarchy coherence
        all_coherence_scores = []
        for clusters in hierarchy.values():
            all_coherence_scores.extend(cluster.coherence_score for cluster in clusters)

        hierarchy_coherence = (
            sum(all_coherence_scores) / len(all_coherence_scores)
            if all_coherence_scores
            else 0.0
        )

        # Calculate pattern coverage (simplified - assumes all patterns are covered)
        pattern_coverage = 1.0

        # Calculate reorganization frequency (based on temporal stability)
        all_stability_scores = []
        for clusters in hierarchy.values():
            all_stability_scores.extend(
                cluster.temporal_stability for cluster in clusters
            )

        avg_stability = (
            sum(all_stability_scores) / len(all_stability_scores)
            if all_stability_scores
            else 1.0
        )
        reorganization_frequency = 1.0 - avg_stability

        return HierarchyMetrics(
            total_levels=total_levels,
            total_clusters=total_clusters,
            avg_branching_factor=avg_branching_factor,
            max_depth=max_depth,
            compression_efficiency=compression_efficiency,
            hierarchy_coherence=hierarchy_coherence,
            pattern_coverage=pattern_coverage,
            reorganization_frequency=reorganization_frequency,
        )

    async def _store_hierarchy_metrics(self, metrics: HierarchyMetrics):
        """Store hierarchy metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO hierarchy_metrics (
                timestamp, total_levels, total_clusters, avg_branching_factor,
                max_depth, compression_efficiency, hierarchy_coherence,
                pattern_coverage, reorganization_frequency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                time.time(),
                metrics.total_levels,
                metrics.total_clusters,
                metrics.avg_branching_factor,
                metrics.max_depth,
                metrics.compression_efficiency,
                metrics.hierarchy_coherence,
                metrics.pattern_coverage,
                metrics.reorganization_frequency,
            ),
        )

        conn.commit()
        conn.close()

    async def find_cluster_by_pattern(
        self, pattern_id: str
    ) -> Optional[FractalCluster]:
        """Find the cluster containing a specific pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM fractal_clusters
            WHERE pattern_ids LIKE ?
        """,
            (f'%"{pattern_id}"%',),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return FractalCluster(
            cluster_id=row[0],
            level=row[1],
            parent_cluster_id=row[2],
            child_cluster_ids=json.loads(row[3]),
            pattern_ids=json.loads(row[4]),
            fractal_signature=row[5],
            similarity_threshold=row[6],
            compression_ratio=row[7],
            abstraction_level=row[8],
            coherence_score=row[9],
            temporal_stability=row[10],
            created_at=row[11],
            last_updated=row[12],
        )

    async def get_hierarchy_path(self, cluster_id: str) -> List[FractalCluster]:
        """Get the path from leaf to root for a cluster"""
        path = []
        current_id = cluster_id

        while current_id:
            cluster = await self._load_cluster_by_id(current_id)
            if not cluster:
                break

            path.append(cluster)
            current_id = cluster.parent_cluster_id

        return path

    async def _load_cluster_by_id(self, cluster_id: str) -> Optional[FractalCluster]:
        """Load a cluster by its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM fractal_clusters WHERE cluster_id = ?", (cluster_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return FractalCluster(
            cluster_id=row[0],
            level=row[1],
            parent_cluster_id=row[2],
            child_cluster_ids=json.loads(row[3]),
            pattern_ids=json.loads(row[4]),
            fractal_signature=row[5],
            similarity_threshold=row[6],
            compression_ratio=row[7],
            abstraction_level=row[8],
            coherence_score=row[9],
            temporal_stability=row[10],
            created_at=row[11],
            last_updated=row[12],
        )

    async def reorganize_hierarchy_if_needed(self) -> bool:
        """Check if hierarchy needs reorganization and do it if necessary"""

        # Load current hierarchy metrics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT hierarchy_coherence FROM hierarchy_metrics
            ORDER BY timestamp DESC LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        if not row:
            return False

        current_coherence = row[0]

        if current_coherence < self.reorganization_trigger:
            print(f"🔄 Reorganizing hierarchy (coherence: {current_coherence:.1%})")

            # Rebuild hierarchy
            await self.build_fractal_hierarchy()
            self.hierarchy_stats["reorganizations"] += 1

            return True

        return False

    async def get_fractal_hierarchy_statistics(self) -> Dict[str, Any]:
        """Get comprehensive fractal hierarchy statistics"""

        # Database statistics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM fractal_clusters")
        cluster_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT level) FROM fractal_clusters")
        level_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(coherence_score) FROM fractal_clusters")
        avg_coherence = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT AVG(compression_ratio) FROM fractal_clusters")
        avg_compression = cursor.fetchone()[0] or 0.0

        # Get latest metrics
        cursor.execute("""
            SELECT * FROM hierarchy_metrics
            ORDER BY timestamp DESC LIMIT 1
        """)

        metrics_row = cursor.fetchone()
        conn.close()

        latest_metrics = None
        if metrics_row:
            latest_metrics = {
                "total_levels": metrics_row[2],
                "total_clusters": metrics_row[3],
                "avg_branching_factor": metrics_row[4],
                "max_depth": metrics_row[5],
                "compression_efficiency": metrics_row[6],
                "hierarchy_coherence": metrics_row[7],
                "pattern_coverage": metrics_row[8],
                "reorganization_frequency": metrics_row[9],
            }

        return {
            "timestamp": time.time(),
            "current_clusters": cluster_count,
            "current_levels": level_count,
            "avg_cluster_coherence": avg_coherence,
            "avg_cluster_compression": avg_compression,
            "clusters_created": self.hierarchy_stats["clusters_created"],
            "hierarchies_built": self.hierarchy_stats["hierarchies_built"],
            "reorganizations": self.hierarchy_stats["reorganizations"],
            "total_processing_time": self.hierarchy_stats["total_processing_time"],
            "latest_metrics": latest_metrics,
        }


# Example usage and testing
async def demo_fractal_hierarchies():
    """Demonstrate fractal hierarchies capabilities"""
    print("🌳 FRACTAL HIERARCHIES DEMONSTRATION")
    print("=" * 70)

    # Initialize encoder and hierarchies
    encoder = FractalEncoder()
    hierarchies = FractalHierarchies(encoder)

    # Create test patterns with various types and abstraction levels
    test_memories = [
        {
            "id": "conv_1",
            "content": "Hello, how are you today? I'm doing well, thank you!",
        },
        {
            "id": "conv_2",
            "content": "Hello, what can I help you with? I'm here to assist you.",
        },
        {
            "id": "conv_3",
            "content": "Good morning, how can I help? I'm ready to help you today.",
        },
        {
            "id": "refl_1",
            "content": {
                "type": "reflection",
                "thoughts": ["consciousness", "awareness", "understanding"],
            },
        },
        {
            "id": "refl_2",
            "content": {
                "type": "reflection",
                "thoughts": ["intelligence", "cognition", "thinking"],
            },
        },
        {
            "id": "refl_3",
            "content": {
                "type": "reflection",
                "thoughts": ["consciousness", "cognition", "self-awareness"],
            },
        },
        {
            "id": "concept_1",
            "content": {
                "category": "AI",
                "concepts": ["neural networks", "machine learning"],
            },
        },
        {
            "id": "concept_2",
            "content": {
                "category": "AI",
                "concepts": ["deep learning", "artificial intelligence"],
            },
        },
        {
            "id": "concept_3",
            "content": {
                "category": "Physics",
                "concepts": ["quantum mechanics", "relativity"],
            },
        },
        {
            "id": "narrative_1",
            "content": "The AI pondered the nature of consciousness and self-awareness.",
        },
        {
            "id": "narrative_2",
            "content": "Artificial intelligence explores the boundaries of machine consciousness.",
        },
        {
            "id": "narrative_3",
            "content": "The quantum nature of reality influences our understanding of physics.",
        },
    ]

    print("\n🧬 Encoding fractal patterns...")
    pattern_ids = []
    for memory in test_memories:
        node = await encoder.encode_memory_fragment(memory["content"], memory["id"])
        pattern_ids.extend(node.pattern_refs)
        print(f"   ✅ {memory['id']}: {len(node.pattern_refs)} patterns")

    # Remove duplicates
    unique_pattern_ids = list(set(pattern_ids))
    print(f"   📊 Total unique patterns: {len(unique_pattern_ids)}")

    print("\n🌳 Building fractal hierarchy...")
    hierarchy = await hierarchies.build_fractal_hierarchy(unique_pattern_ids)

    print("\n📊 Hierarchy Structure:")
    for level in sorted(hierarchy.keys()):
        clusters = hierarchy[level]
        print(f"   Level {level}: {len(clusters)} clusters")
        for i, cluster in enumerate(clusters[:3]):  # Show first 3 clusters
            print(
                f"     Cluster {i + 1}: {len(cluster.pattern_ids)} patterns, {cluster.coherence_score:.1%} coherence"
            )

    print("\n🔍 Testing cluster lookup...")
    if unique_pattern_ids:
        test_pattern_id = unique_pattern_ids[0]
        cluster = await hierarchies.find_cluster_by_pattern(test_pattern_id)
        if cluster:
            print(
                f"   ✅ Pattern {test_pattern_id} found in cluster {cluster.cluster_id}"
            )

            # Get hierarchy path
            path = await hierarchies.get_hierarchy_path(cluster.cluster_id)
            print(f"   📍 Hierarchy path: {' → '.join(c.cluster_id for c in path)}")

    print("\n🔄 Testing reorganization...")
    reorganized = await hierarchies.reorganize_hierarchy_if_needed()
    print(f"   {'✅ Reorganized' if reorganized else '⏭️ No reorganization needed'}")

    print("\n📊 Fractal Hierarchy Statistics:")
    stats = await hierarchies.get_fractal_hierarchy_statistics()
    print(f"   🌳 Current clusters: {stats['current_clusters']}")
    print(f"   📊 Current levels: {stats['current_levels']}")
    print(f"   🎯 Average coherence: {stats['avg_cluster_coherence']:.1%}")
    print(f"   📈 Average compression: {stats['avg_cluster_compression']:.1f}x")
    print(f"   🏗️ Total hierarchies built: {stats['hierarchies_built']}")
    print(f"   🔄 Reorganizations: {stats['reorganizations']}")

    if stats["latest_metrics"]:
        metrics = stats["latest_metrics"]
        print("   📋 Latest metrics:")
        print(f"     • Total levels: {metrics['total_levels']}")
        print(f"     • Max depth: {metrics['max_depth']}")
        print(f"     • Branching factor: {metrics['avg_branching_factor']:.1f}")
        print(f"     • Compression efficiency: {metrics['compression_efficiency']:.1%}")
        print(f"     • Hierarchy coherence: {metrics['hierarchy_coherence']:.1%}")

    print("\n🎉 Fractal Hierarchies demonstration complete!")

    return hierarchies


if __name__ == "__main__":
    asyncio.run(demo_fractal_hierarchies())
