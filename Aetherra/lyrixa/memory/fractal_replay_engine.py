#!/usr/bin/env python3
"""
🚀 AETHERRA QFAC Phase 2: FractalReplayEngine
=================================================================

Advanced episode reconstruction engine using fractal memory patterns.
Enables efficient replay and reconstruction of memory episodes.

Core Features:
• Episode reconstruction from fractal patterns
• Pattern-based memory replay with compression awareness
• Temporal sequence reconstruction
• Multi-level fractal episode assembly
• Adaptive reconstruction fidelity
"""

import asyncio
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from fractal_encoder import FractalEncoder, FractalNode, FractalPattern


@dataclass
class ReplayEpisode:
    """Represents a reconstructed memory episode"""

    episode_id: str
    original_node_ids: List[str]  # Source fractal nodes
    reconstruction_fidelity: float  # How accurate the reconstruction is (0-1)
    compression_ratio: float  # Original vs reconstructed size ratio
    fractal_depth: int  # Maximum depth in reconstruction
    temporal_sequence: List[
        Dict[str, Any]
    ]  # Ordered sequence of reconstructed elements
    pattern_coverage: float  # Percentage of patterns successfully reconstructed
    reconstruction_time: float  # Time taken to reconstruct
    metadata: Dict[str, Any]  # Additional reconstruction metadata
    created_at: float


@dataclass
class ReconstructionContext:
    """Context for memory reconstruction"""

    target_fidelity: float = 0.8  # Desired reconstruction fidelity
    max_depth: int = 5  # Maximum fractal depth to explore
    include_patterns: Optional[List[str]] = None  # Specific patterns to include
    exclude_patterns: Optional[List[str]] = (
        None  # Patterns to exclude from reconstruction
    )
    temporal_order: bool = True  # Whether to maintain temporal ordering
    compression_aware: bool = True  # Whether to use compression-aware reconstruction


class FractalReplayEngine:
    """
    Advanced fractal replay engine for memory episode reconstruction
    """

    def __init__(
        self, fractal_encoder: FractalEncoder, data_dir: str = "fractal_replay_data"
    ):
        self.encoder = fractal_encoder
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Database for replay episodes
        self.db_path = self.data_dir / "replay_episodes.db"
        self._init_database()

        # Reconstruction settings
        self.default_fidelity = 0.8
        self.max_reconstruction_time = 30.0  # seconds
        self.pattern_cache: Dict[str, FractalPattern] = {}

        # Performance tracking
        self.replay_stats = {
            "episodes_reconstructed": 0,
            "total_reconstruction_time": 0.0,
            "avg_fidelity": 0.0,
            "avg_compression_ratio": 0.0,
        }

        print("🎬 FractalReplayEngine initialized")
        print(f"   📁 Data directory: {self.data_dir}")
        print(f"   🗃️ Database: {self.db_path}")
        print(f"   🎯 Default fidelity: {self.default_fidelity}")

    def _init_database(self):
        """Initialize SQLite database for replay episodes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Replay episodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS replay_episodes (
                episode_id TEXT PRIMARY KEY,
                original_node_ids TEXT,
                reconstruction_fidelity REAL,
                compression_ratio REAL,
                fractal_depth INTEGER,
                temporal_sequence TEXT,
                pattern_coverage REAL,
                reconstruction_time REAL,
                metadata TEXT,
                created_at REAL
            )
        """)

        # Reconstruction cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reconstruction_cache (
                cache_key TEXT PRIMARY KEY,
                reconstructed_content TEXT,
                fidelity REAL,
                created_at REAL,
                access_count INTEGER
            )
        """)

        conn.commit()
        conn.close()
        print("   📋 Replay episode database initialized")

    async def reconstruct_episode(
        self,
        node_ids: List[str],
        episode_id: Optional[str] = None,
        context: Optional[ReconstructionContext] = None,
    ) -> ReplayEpisode:
        """
        Reconstruct a memory episode from fractal nodes
        """
        if episode_id is None:
            episode_id = f"episode_{int(time.time() * 1000)}"

        if context is None:
            context = ReconstructionContext()

        print(f"🎬 Reconstructing episode: {episode_id}")
        print(f"   📋 Nodes: {len(node_ids)}")
        print(f"   🎯 Target fidelity: {context.target_fidelity}")

        start_time = time.time()

        # Load fractal nodes
        fractal_nodes = await self._load_fractal_nodes(node_ids)
        if not fractal_nodes:
            raise ValueError(f"No fractal nodes found for IDs: {node_ids}")

        # Gather all patterns from nodes
        all_patterns = await self._gather_patterns_from_nodes(fractal_nodes)

        # Filter patterns based on context
        filtered_patterns = await self._filter_patterns(all_patterns, context)

        # Build temporal sequence
        temporal_sequence = await self._build_temporal_sequence(
            fractal_nodes, filtered_patterns, context
        )

        # Calculate reconstruction metrics
        reconstruction_fidelity = await self._calculate_reconstruction_fidelity(
            fractal_nodes, temporal_sequence, context
        )

        compression_ratio = await self._calculate_episode_compression_ratio(
            fractal_nodes, temporal_sequence
        )

        max_depth = max(node.fractal_depth for node in fractal_nodes)
        pattern_coverage = (
            len(filtered_patterns) / len(all_patterns) if all_patterns else 1.0
        )
        reconstruction_time = time.time() - start_time

        # Create replay episode
        episode = ReplayEpisode(
            episode_id=episode_id,
            original_node_ids=node_ids,
            reconstruction_fidelity=reconstruction_fidelity,
            compression_ratio=compression_ratio,
            fractal_depth=max_depth,
            temporal_sequence=temporal_sequence,
            pattern_coverage=pattern_coverage,
            reconstruction_time=reconstruction_time,
            metadata={
                "context": {
                    "target_fidelity": context.target_fidelity,
                    "max_depth": context.max_depth,
                    "temporal_order": context.temporal_order,
                    "compression_aware": context.compression_aware,
                },
                "patterns_used": len(filtered_patterns),
                "total_patterns": len(all_patterns),
                "nodes_processed": len(fractal_nodes),
            },
            created_at=time.time(),
        )

        # Store episode
        await self._store_replay_episode(episode)

        # Update statistics
        self.replay_stats["episodes_reconstructed"] += 1
        self.replay_stats["total_reconstruction_time"] += reconstruction_time
        self.replay_stats["avg_fidelity"] = (
            self.replay_stats["avg_fidelity"]
            * (self.replay_stats["episodes_reconstructed"] - 1)
            + reconstruction_fidelity
        ) / self.replay_stats["episodes_reconstructed"]
        self.replay_stats["avg_compression_ratio"] = (
            self.replay_stats["avg_compression_ratio"]
            * (self.replay_stats["episodes_reconstructed"] - 1)
            + compression_ratio
        ) / self.replay_stats["episodes_reconstructed"]

        print(
            f"   ✅ Reconstructed: {reconstruction_fidelity:.1%} fidelity, {compression_ratio:.1f}x compression"
        )
        print(f"   ⏱️ Time: {reconstruction_time * 1000:.1f}ms")

        return episode

    async def _load_fractal_nodes(self, node_ids: List[str]) -> List[FractalNode]:
        """Load fractal nodes from the encoder database"""
        conn = sqlite3.connect(self.encoder.db_path)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in node_ids)
        cursor.execute(
            f"SELECT * FROM fractal_nodes WHERE node_id IN ({placeholders})", node_ids
        )
        rows = cursor.fetchall()
        conn.close()

        fractal_nodes = []
        for row in rows:
            node = FractalNode(
                node_id=row[0],
                content=json.loads(row[1]),
                pattern_refs=json.loads(row[2]),
                fractal_depth=row[3],
                compression_seeds=json.loads(row[4]),
                reconstruction_rules=json.loads(row[5]),
                similarity_map=json.loads(row[6]),
                access_frequency=row[7],
                created_at=row[8],
                last_accessed=row[9],
            )
            fractal_nodes.append(node)

        return fractal_nodes

    async def _gather_patterns_from_nodes(
        self, fractal_nodes: List[FractalNode]
    ) -> List[FractalPattern]:
        """Gather all patterns referenced by fractal nodes"""
        all_pattern_ids = set()
        for node in fractal_nodes:
            all_pattern_ids.update(node.pattern_refs)

        if not all_pattern_ids:
            return []

        # Load patterns from encoder database
        conn = sqlite3.connect(self.encoder.db_path)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in all_pattern_ids)
        cursor.execute(
            f"SELECT * FROM fractal_patterns WHERE pattern_id IN ({placeholders})",
            list(all_pattern_ids),
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

    async def _filter_patterns(
        self, patterns: List[FractalPattern], context: ReconstructionContext
    ) -> List[FractalPattern]:
        """Filter patterns based on reconstruction context"""
        filtered = patterns.copy()

        # Filter by include/exclude lists
        if context.include_patterns:
            filtered = [p for p in filtered if p.pattern_id in context.include_patterns]

        if context.exclude_patterns:
            filtered = [
                p for p in filtered if p.pattern_id not in context.exclude_patterns
            ]

        # Filter by maximum depth
        filtered = [p for p in filtered if p.abstraction_level <= context.max_depth]

        # Sort by importance (frequency * compression ratio)
        filtered.sort(key=lambda p: p.frequency * p.compression_ratio, reverse=True)

        return filtered

    async def _build_temporal_sequence(
        self,
        fractal_nodes: List[FractalNode],
        patterns: List[FractalPattern],
        context: ReconstructionContext,
    ) -> List[Dict[str, Any]]:
        """Build temporal sequence of reconstructed elements"""
        sequence = []

        # Sort nodes by creation time if temporal order is requested
        if context.temporal_order:
            sorted_nodes = sorted(fractal_nodes, key=lambda n: n.created_at)
        else:
            sorted_nodes = fractal_nodes

        for node in sorted_nodes:
            # Reconstruct content from compression seeds and rules
            reconstructed_content = await self._reconstruct_from_seeds(
                node, patterns, context
            )

            # Create sequence element
            element = {
                "node_id": node.node_id,
                "timestamp": node.created_at,
                "fractal_depth": node.fractal_depth,
                "content": reconstructed_content,
                "patterns_applied": [
                    p.pattern_id for p in patterns if p.pattern_id in node.pattern_refs
                ],
                "compression_seeds": node.compression_seeds,
                "reconstruction_fidelity": await self._estimate_element_fidelity(
                    node.content, reconstructed_content
                ),
            }
            sequence.append(element)

        return sequence

    async def _reconstruct_from_seeds(
        self,
        node: FractalNode,
        patterns: List[FractalPattern],
        context: ReconstructionContext,
    ) -> Any:
        """Reconstruct content from compression seeds and patterns"""

        # Check reconstruction cache first
        cache_key = f"{node.node_id}_{context.target_fidelity}"
        cached_content = await self._check_reconstruction_cache(cache_key)
        if cached_content is not None:
            return cached_content

        # For now, implement basic reconstruction
        # TODO: Full fractal reconstruction algorithm

        if context.compression_aware and node.compression_seeds:
            # Use compression-aware reconstruction
            reconstructed = await self._expand_from_seeds(node, patterns)
        else:
            # Fall back to original content
            reconstructed = node.content

        # Apply pattern-based enhancements
        if patterns:
            reconstructed = await self._apply_pattern_enhancements(
                reconstructed, patterns, node
            )

        # Cache the result
        await self._cache_reconstruction(
            cache_key, reconstructed, context.target_fidelity
        )

        return reconstructed

    async def _expand_from_seeds(
        self, node: FractalNode, patterns: List[FractalPattern]
    ) -> Any:
        """Expand content from compression seeds using patterns"""

        # Parse seeds
        seed_info = {}
        for seed in node.compression_seeds:
            if ":" in seed:
                parts = seed.split(":")
                if len(parts) >= 3:
                    pattern_type, content_hash, frequency = (
                        parts[0],
                        parts[1],
                        int(parts[2]),
                    )
                    seed_info[content_hash] = {
                        "type": pattern_type,
                        "frequency": frequency,
                    }

        # Find matching patterns
        matching_patterns = []
        for pattern in patterns:
            if pattern.content_hash[:8] in seed_info:
                matching_patterns.append(pattern)

        # Reconstruct using pattern instances
        if matching_patterns:
            # Use first matching pattern's instances as base for reconstruction
            base_pattern = matching_patterns[0]
            if base_pattern.instances:
                return base_pattern.instances[0]  # Simplified reconstruction

        # Fall back to original content
        return node.content

    async def _apply_pattern_enhancements(
        self, content: Any, patterns: List[FractalPattern], node: FractalNode
    ) -> Any:
        """Apply pattern-based enhancements to reconstructed content"""

        # For text content, apply pattern-based improvements
        if isinstance(content, str):
            enhanced_content = content

            # Apply sequence patterns to improve coherence
            for pattern in patterns:
                if (
                    pattern.pattern_type == "sequence"
                    and pattern.pattern_id in node.pattern_refs
                ):
                    # Pattern-based text enhancement (simplified)
                    if pattern.instances and "ngram" in pattern.instances[0]:
                        ngram = pattern.instances[0]["ngram"]
                        if (
                            ngram not in enhanced_content
                            and len(enhanced_content.split()) > 3
                        ):
                            # Add ngram for better coherence (simplified logic)
                            enhanced_content = f"{enhanced_content} {ngram}"

            return enhanced_content

        # For structured content, apply structural patterns
        elif isinstance(content, dict):
            enhanced_content = content.copy()

            # Apply concept patterns to enhance structure
            for pattern in patterns:
                if (
                    pattern.pattern_type == "concept"
                    and pattern.pattern_id in node.pattern_refs
                ):
                    if pattern.instances and "keys" in pattern.instances[0]:
                        expected_keys = pattern.instances[0]["keys"]
                        # Ensure all expected keys are present
                        for key in expected_keys:
                            if key not in enhanced_content:
                                enhanced_content[key] = f"<reconstructed_{key}>"

            return enhanced_content

        # For other types, return as-is
        return content

    async def _calculate_reconstruction_fidelity(
        self,
        fractal_nodes: List[FractalNode],
        temporal_sequence: List[Dict[str, Any]],
        context: ReconstructionContext,
    ) -> float:
        """Calculate overall reconstruction fidelity"""

        if not temporal_sequence:
            return 0.0

        # Calculate average element fidelity
        total_fidelity = sum(
            element["reconstruction_fidelity"] for element in temporal_sequence
        )
        avg_fidelity = total_fidelity / len(temporal_sequence)

        # Adjust for pattern coverage
        pattern_coverage_factor = (
            temporal_sequence[0].get("pattern_coverage", 1.0)
            if temporal_sequence
            else 1.0
        )

        # Adjust for temporal ordering accuracy
        temporal_accuracy = 1.0
        if context.temporal_order and len(temporal_sequence) > 1:
            correct_order = 0
            for i in range(len(temporal_sequence) - 1):
                if (
                    temporal_sequence[i]["timestamp"]
                    <= temporal_sequence[i + 1]["timestamp"]
                ):
                    correct_order += 1
            temporal_accuracy = correct_order / (len(temporal_sequence) - 1)

        # Weighted combination
        overall_fidelity = (
            avg_fidelity * 0.6 + pattern_coverage_factor * 0.3 + temporal_accuracy * 0.1
        )

        return min(overall_fidelity, 1.0)

    async def _calculate_episode_compression_ratio(
        self, fractal_nodes: List[FractalNode], temporal_sequence: List[Dict[str, Any]]
    ) -> float:
        """Calculate compression ratio for the entire episode"""

        # Calculate original content size
        original_size = 0
        for node in fractal_nodes:
            original_size += len(json.dumps(node.content, default=str))

        # Calculate reconstructed content size
        reconstructed_size = 0
        for element in temporal_sequence:
            reconstructed_size += len(json.dumps(element["content"], default=str))

        if reconstructed_size == 0:
            return 1.0

        return original_size / reconstructed_size

    async def _estimate_element_fidelity(
        self, original: Any, reconstructed: Any
    ) -> float:
        """Estimate fidelity of a single reconstructed element"""

        # Convert to strings for comparison
        original_str = json.dumps(original, default=str, sort_keys=True)
        reconstructed_str = json.dumps(reconstructed, default=str, sort_keys=True)

        # Exact match
        if original_str == reconstructed_str:
            return 1.0

        # Calculate similarity using simple string comparison
        original_chars = set(original_str)
        reconstructed_chars = set(reconstructed_str)

        if not original_chars:
            return 1.0 if not reconstructed_chars else 0.0

        intersection = len(original_chars & reconstructed_chars)
        union = len(original_chars | reconstructed_chars)

        return intersection / union if union > 0 else 0.0

    async def _check_reconstruction_cache(self, cache_key: str) -> Optional[Any]:
        """Check if reconstruction is cached"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT reconstructed_content FROM reconstruction_cache WHERE cache_key = ?",
            (cache_key,),
        )
        row = cursor.fetchone()

        if row:
            # Update access count
            cursor.execute(
                "UPDATE reconstruction_cache SET access_count = access_count + 1 WHERE cache_key = ?",
                (cache_key,),
            )
            conn.commit()
            conn.close()
            return json.loads(row[0])

        conn.close()
        return None

    async def _cache_reconstruction(
        self, cache_key: str, content: Any, fidelity: float
    ):
        """Cache reconstruction result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO reconstruction_cache
            (cache_key, reconstructed_content, fidelity, created_at, access_count)
            VALUES (?, ?, ?, ?, 0)
        """,
            (cache_key, json.dumps(content, default=str), fidelity, time.time()),
        )

        conn.commit()
        conn.close()

    async def _store_replay_episode(self, episode: ReplayEpisode):
        """Store replay episode in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO replay_episodes (
                episode_id, original_node_ids, reconstruction_fidelity, compression_ratio,
                fractal_depth, temporal_sequence, pattern_coverage, reconstruction_time,
                metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                episode.episode_id,
                json.dumps(episode.original_node_ids),
                episode.reconstruction_fidelity,
                episode.compression_ratio,
                episode.fractal_depth,
                json.dumps(episode.temporal_sequence, default=str),
                episode.pattern_coverage,
                episode.reconstruction_time,
                json.dumps(episode.metadata, default=str),
                episode.created_at,
            ),
        )

        conn.commit()
        conn.close()

    async def load_replay_episode(self, episode_id: str) -> Optional[ReplayEpisode]:
        """Load a replay episode from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM replay_episodes WHERE episode_id = ?", (episode_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return ReplayEpisode(
            episode_id=row[0],
            original_node_ids=json.loads(row[1]),
            reconstruction_fidelity=row[2],
            compression_ratio=row[3],
            fractal_depth=row[4],
            temporal_sequence=json.loads(row[5]),
            pattern_coverage=row[6],
            reconstruction_time=row[7],
            metadata=json.loads(row[8]),
            created_at=row[9],
        )

    async def get_replay_statistics(self) -> Dict[str, Any]:
        """Get comprehensive replay engine statistics"""

        # Database statistics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM replay_episodes")
        episode_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM reconstruction_cache")
        cache_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(reconstruction_fidelity) FROM replay_episodes")
        avg_fidelity = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT AVG(compression_ratio) FROM replay_episodes")
        avg_compression = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT AVG(reconstruction_time) FROM replay_episodes")
        avg_time = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT SUM(access_count) FROM reconstruction_cache")
        total_cache_hits = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "timestamp": time.time(),
            "total_episodes": episode_count,
            "cache_entries": cache_count,
            "total_cache_hits": total_cache_hits,
            "avg_reconstruction_fidelity": avg_fidelity,
            "avg_compression_ratio": avg_compression,
            "avg_reconstruction_time": avg_time,
            "episodes_reconstructed": self.replay_stats["episodes_reconstructed"],
            "total_reconstruction_time": self.replay_stats["total_reconstruction_time"],
            "cache_hit_rate": total_cache_hits / max(episode_count, 1),
            "reconstruction_efficiency": avg_fidelity / max(avg_time, 0.001)
            if avg_time > 0
            else 0.0,
        }


# Example usage and testing
async def demo_fractal_replay_engine():
    """Demonstrate fractal replay engine capabilities"""
    print("🎬 FRACTAL REPLAY ENGINE DEMONSTRATION")
    print("=" * 70)

    # Initialize encoder and replay engine
    encoder = FractalEncoder()
    replay_engine = FractalReplayEngine(encoder)

    # Create some test fractal nodes
    test_memories = [
        {
            "id": "memory_1",
            "content": {
                "type": "conversation",
                "messages": [
                    {"role": "user", "content": "What is consciousness?"},
                    {
                        "role": "ai",
                        "content": "Consciousness is the subjective experience of awareness.",
                    },
                ],
            },
        },
        {
            "id": "memory_2",
            "content": {
                "type": "reflection",
                "thoughts": [
                    "The nature of consciousness fascinates me.",
                    "Patterns emerge from complexity in fascinating ways.",
                    "Self-awareness might be an emergent property.",
                ],
            },
        },
        {
            "id": "memory_3",
            "content": "Consciousness and complexity are deeply interconnected concepts that shape our understanding of intelligence.",
        },
    ]

    print("\n🧬 Encoding fractal memories...")
    fractal_nodes = []
    for memory in test_memories:
        node = await encoder.encode_memory_fragment(memory["content"], memory["id"])
        fractal_nodes.append(node)
        print(f"   ✅ {memory['id']}: depth {node.fractal_depth}")

    # Reconstruct episodes with different contexts
    print("\n🎬 Reconstructing episodes...")

    # High fidelity reconstruction
    context_high_fidelity = ReconstructionContext(
        target_fidelity=0.9, max_depth=5, temporal_order=True, compression_aware=True
    )

    episode_1 = await replay_engine.reconstruct_episode(
        [node.node_id for node in fractal_nodes],
        "demo_episode_high_fidelity",
        context_high_fidelity,
    )

    print(f"   ✅ High fidelity: {episode_1.reconstruction_fidelity:.1%} fidelity")

    # Fast reconstruction with lower fidelity
    context_fast = ReconstructionContext(
        target_fidelity=0.6, max_depth=3, temporal_order=False, compression_aware=False
    )

    episode_2 = await replay_engine.reconstruct_episode(
        [fractal_nodes[0].node_id, fractal_nodes[2].node_id],
        "demo_episode_fast",
        context_fast,
    )

    print(
        f"   ✅ Fast reconstruction: {episode_2.reconstruction_fidelity:.1%} fidelity"
    )

    # Pattern-selective reconstruction
    context_selective = ReconstructionContext(
        target_fidelity=0.8, max_depth=4, temporal_order=True, compression_aware=True
    )

    episode_3 = await replay_engine.reconstruct_episode(
        [fractal_nodes[1].node_id], "demo_episode_selective", context_selective
    )

    print(
        f"   ✅ Selective reconstruction: {episode_3.reconstruction_fidelity:.1%} fidelity"
    )

    print("\n📊 Replay Engine Statistics:")
    stats = await replay_engine.get_replay_statistics()
    print(f"   🎬 Total episodes: {stats['total_episodes']}")
    print(f"   💾 Cache entries: {stats['cache_entries']}")
    print(f"   🎯 Average fidelity: {stats['avg_reconstruction_fidelity']:.1%}")
    print(f"   📈 Average compression: {stats['avg_compression_ratio']:.1f}x")
    print(f"   ⚡ Average time: {stats['avg_reconstruction_time'] * 1000:.1f}ms")
    print(f"   🚀 Reconstruction efficiency: {stats['reconstruction_efficiency']:.1f}")

    print("\n🔄 Testing episode reload...")
    reloaded_episode = await replay_engine.load_replay_episode(episode_1.episode_id)
    if reloaded_episode:
        print(f"   ✅ Reloaded episode: {reloaded_episode.episode_id}")
        print(f"   📋 Sequence length: {len(reloaded_episode.temporal_sequence)}")

    print("\n🎉 Fractal Replay Engine demonstration complete!")

    return replay_engine


if __name__ == "__main__":
    asyncio.run(demo_fractal_replay_engine())
