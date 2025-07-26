#!/usr/bin/env python3
"""
🚀 AETHERRA QFAC Phase 2: FractalEncoder
==============================================================

Advanced self-similarity detection and conceptual compression engine.
Implements fractal memory structures with recursive pattern recognition.

Core Features:
• Self-similarity mapping for conceptual compression
• Recursive collapse of repeated thought patterns
• Motif and event sequence detection
• Fractal hierarchy construction
• Pattern-based memory encoding
"""

import asyncio
import hashlib
import json
import math
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class FractalPattern:
    """Represents a discovered fractal pattern in memory"""

    pattern_id: str
    pattern_type: str  # "motif", "sequence", "concept", "archetype"
    content_hash: str  # Hash of the pattern content
    similarity_score: float  # How similar instances are (0-1)
    frequency: int  # Number of occurrences
    compression_ratio: float  # How much compression this pattern enables
    abstraction_level: int  # 0=concrete, higher=more abstract
    parent_patterns: List[str]  # Higher-level patterns this belongs to
    child_patterns: List[str]  # Sub-patterns within this pattern
    instances: List[Dict[str, Any]]  # Actual occurrences of this pattern
    created_at: float
    last_seen: float


@dataclass
class FractalNode:
    """A node in the fractal memory hierarchy"""

    node_id: str
    content: Any  # Original content
    pattern_refs: List[str]  # IDs of patterns this node contains
    fractal_depth: int  # Depth in the fractal hierarchy
    compression_seeds: List[str]  # Minimal seeds for reconstruction
    reconstruction_rules: Dict[str, Any]  # Rules for expanding seeds
    similarity_map: Dict[str, float]  # Similarity to other nodes
    access_frequency: float
    created_at: float
    last_accessed: float


@dataclass
class SelfSimilarityMap:
    """Maps self-similar patterns across memory"""

    source_id: str
    target_id: str
    similarity_type: str  # "conceptual", "structural", "sequential", "semantic"
    similarity_score: float  # 0-1 similarity measure
    transformation_rules: Dict[str, Any]  # How to transform source to target
    compression_benefit: float  # Compression gained by recognizing similarity
    confidence: float  # Confidence in the similarity detection


class FractalEncoder:
    """
    Advanced fractal encoding engine for self-similarity detection
    """

    def __init__(self, data_dir: str = "fractal_encoder_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Database for pattern storage
        self.db_path = self.data_dir / "fractal_patterns.db"
        self._init_database()

        # Pattern recognition configuration
        self.min_pattern_frequency = 2  # Minimum occurrences to be a pattern
        self.min_similarity_threshold = 0.7  # Minimum similarity for pattern matching
        self.max_fractal_depth = 10  # Maximum depth in fractal hierarchy

        # Pattern caches
        self.pattern_cache: Dict[str, FractalPattern] = {}
        self.similarity_cache: Dict[Tuple[str, str], float] = {}

        # Compression statistics
        self.compression_stats = {
            "patterns_discovered": 0,
            "total_compression_ratio": 0.0,
            "processing_time": 0.0,
        }

        print("🚀 FractalEncoder initialized")
        print(f"   📁 Data directory: {self.data_dir}")
        print(f"   🗃️ Database: {self.db_path}")
        print(f"   🎯 Min similarity threshold: {self.min_similarity_threshold}")

    def _init_database(self):
        """Initialize SQLite database for fractal patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Fractal patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fractal_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT,
                content_hash TEXT,
                similarity_score REAL,
                frequency INTEGER,
                compression_ratio REAL,
                abstraction_level INTEGER,
                parent_patterns TEXT,
                child_patterns TEXT,
                instances TEXT,
                created_at REAL,
                last_seen REAL
            )
        """)

        # Fractal nodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fractal_nodes (
                node_id TEXT PRIMARY KEY,
                content TEXT,
                pattern_refs TEXT,
                fractal_depth INTEGER,
                compression_seeds TEXT,
                reconstruction_rules TEXT,
                similarity_map TEXT,
                access_frequency REAL,
                created_at REAL,
                last_accessed REAL
            )
        """)

        # Self-similarity maps table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS similarity_maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                target_id TEXT,
                similarity_type TEXT,
                similarity_score REAL,
                transformation_rules TEXT,
                compression_benefit REAL,
                confidence REAL,
                created_at REAL
            )
        """)

        conn.commit()
        conn.close()
        print("   📋 Fractal pattern database initialized")

    async def encode_memory_fragment(
        self, content: Any, fragment_id: str, context: Optional[Dict[str, Any]] = None
    ) -> FractalNode:
        """
        Encode a memory fragment using fractal compression
        """
        print(f"🧬 Encoding fractal memory: {fragment_id}")

        start_time = time.time()

        # Extract patterns from content
        patterns = await self._extract_patterns(content, fragment_id)

        # Find self-similarities with existing patterns
        similarities = await self._find_self_similarities(patterns, fragment_id)

        # Generate compression seeds and reconstruction rules
        seeds, rules = await self._generate_compression_artifacts(
            content, patterns, similarities
        )

        # Calculate fractal depth
        fractal_depth = await self._calculate_fractal_depth(patterns, similarities)

        # Create fractal node
        fractal_node = FractalNode(
            node_id=fragment_id,
            content=content,
            pattern_refs=[p.pattern_id for p in patterns],
            fractal_depth=fractal_depth,
            compression_seeds=seeds,
            reconstruction_rules=rules,
            similarity_map={
                sim.target_id: sim.similarity_score for sim in similarities
            },
            access_frequency=1.0,
            created_at=time.time(),
            last_accessed=time.time(),
        )

        # Store in database
        await self._store_fractal_node(fractal_node)

        # Update compression statistics
        processing_time = time.time() - start_time
        compression_ratio = await self._calculate_compression_ratio(fractal_node)

        self.compression_stats["patterns_discovered"] += len(patterns)
        self.compression_stats["total_compression_ratio"] += compression_ratio
        self.compression_stats["processing_time"] += processing_time

        print(
            f"   ✅ Encoded with {len(patterns)} patterns, depth {fractal_depth}, {compression_ratio:.1f}x compression"
        )

        return fractal_node

    async def _extract_patterns(
        self, content: Any, fragment_id: str
    ) -> List[FractalPattern]:
        """Extract patterns from content"""
        patterns = []

        # Convert content to analyzable format
        if isinstance(content, str):
            patterns.extend(await self._extract_text_patterns(content, fragment_id))
        elif isinstance(content, dict):
            patterns.extend(
                await self._extract_structure_patterns(content, fragment_id)
            )
        elif isinstance(content, list):
            patterns.extend(await self._extract_sequence_patterns(content, fragment_id))

        return patterns

    async def _extract_text_patterns(
        self, text: str, fragment_id: str
    ) -> List[FractalPattern]:
        """Extract patterns from text content"""
        patterns = []

        # Word-level patterns
        words = text.lower().split()
        word_frequencies = defaultdict(int)
        for word in words:
            word_frequencies[word] += 1

        # Create patterns for frequent words
        for word, freq in word_frequencies.items():
            if freq >= self.min_pattern_frequency and len(word) > 2:
                pattern_id = (
                    f"word_pattern_{hashlib.md5(word.encode()).hexdigest()[:8]}"
                )
                content_hash = hashlib.md5(word.encode()).hexdigest()

                pattern = FractalPattern(
                    pattern_id=pattern_id,
                    pattern_type="motif",
                    content_hash=content_hash,
                    similarity_score=1.0,
                    frequency=freq,
                    compression_ratio=freq / len(word),
                    abstraction_level=0,
                    parent_patterns=[],
                    child_patterns=[],
                    instances=[
                        {
                            "word": word,
                            "positions": [i for i, w in enumerate(words) if w == word],
                        }
                    ],
                    created_at=time.time(),
                    last_seen=time.time(),
                )
                patterns.append(pattern)

        # N-gram patterns
        for n in [2, 3]:
            ngrams = [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]
            ngram_freq = defaultdict(int)
            for ngram in ngrams:
                ngram_freq[ngram] += 1

            for ngram, freq in ngram_freq.items():
                if freq >= self.min_pattern_frequency:
                    pattern_id = f"ngram_{n}_pattern_{hashlib.md5(ngram.encode()).hexdigest()[:8]}"
                    content_hash = hashlib.md5(ngram.encode()).hexdigest()

                    pattern = FractalPattern(
                        pattern_id=pattern_id,
                        pattern_type="sequence",
                        content_hash=content_hash,
                        similarity_score=1.0,
                        frequency=freq,
                        compression_ratio=freq / len(ngram),
                        abstraction_level=1,
                        parent_patterns=[],
                        child_patterns=[],
                        instances=[{"ngram": ngram, "frequency": freq}],
                        created_at=time.time(),
                        last_seen=time.time(),
                    )
                    patterns.append(pattern)

        return patterns

    async def _extract_structure_patterns(
        self, data: Dict[str, Any], fragment_id: str
    ) -> List[FractalPattern]:
        """Extract patterns from structured data"""
        patterns = []

        # Key patterns
        keys = list(data.keys())
        key_structure = "_".join(sorted(keys))

        pattern_id = (
            f"structure_pattern_{hashlib.md5(key_structure.encode()).hexdigest()[:8]}"
        )
        content_hash = hashlib.md5(key_structure.encode()).hexdigest()

        pattern = FractalPattern(
            pattern_id=pattern_id,
            pattern_type="concept",
            content_hash=content_hash,
            similarity_score=1.0,
            frequency=1,
            compression_ratio=len(keys) / len(key_structure),
            abstraction_level=1,
            parent_patterns=[],
            child_patterns=[],
            instances=[{"keys": keys, "structure": key_structure}],
            created_at=time.time(),
            last_seen=time.time(),
        )
        patterns.append(pattern)

        # Value type patterns
        value_types = {}
        for key, value in data.items():
            value_types[key] = type(value).__name__

        type_signature = "_".join(f"{k}:{v}" for k, v in sorted(value_types.items()))
        pattern_id = (
            f"type_pattern_{hashlib.md5(type_signature.encode()).hexdigest()[:8]}"
        )
        content_hash = hashlib.md5(type_signature.encode()).hexdigest()

        pattern = FractalPattern(
            pattern_id=pattern_id,
            pattern_type="concept",
            content_hash=content_hash,
            similarity_score=1.0,
            frequency=1,
            compression_ratio=len(value_types) / len(type_signature),
            abstraction_level=2,
            parent_patterns=[],
            child_patterns=[],
            instances=[{"value_types": value_types, "signature": type_signature}],
            created_at=time.time(),
            last_seen=time.time(),
        )
        patterns.append(pattern)

        return patterns

    async def _extract_sequence_patterns(
        self, data: List[Any], fragment_id: str
    ) -> List[FractalPattern]:
        """Extract patterns from sequence data"""
        patterns = []

        if not data:
            return patterns

        # Element type patterns
        element_types = [type(item).__name__ for item in data]
        type_sequence = "_".join(element_types)

        pattern_id = (
            f"seq_pattern_{hashlib.md5(type_sequence.encode()).hexdigest()[:8]}"
        )
        content_hash = hashlib.md5(type_sequence.encode()).hexdigest()

        pattern = FractalPattern(
            pattern_id=pattern_id,
            pattern_type="sequence",
            content_hash=content_hash,
            similarity_score=1.0,
            frequency=1,
            compression_ratio=len(data) / len(type_sequence),
            abstraction_level=1,
            parent_patterns=[],
            child_patterns=[],
            instances=[{"sequence_types": element_types, "length": len(data)}],
            created_at=time.time(),
            last_seen=time.time(),
        )
        patterns.append(pattern)

        # Repeating element patterns
        if len(data) > 1:
            for i in range(len(data) - 1):
                current = str(data[i])
                next_item = str(data[i + 1])

                if current == next_item:  # Found repetition
                    pattern_id = f"repeat_pattern_{hashlib.md5(current.encode()).hexdigest()[:8]}"
                    content_hash = hashlib.md5(current.encode()).hexdigest()

                    # Count consecutive repetitions
                    repeat_count = 1
                    j = i + 1
                    while j < len(data) and str(data[j]) == current:
                        repeat_count += 1
                        j += 1

                    pattern = FractalPattern(
                        pattern_id=pattern_id,
                        pattern_type="motif",
                        content_hash=content_hash,
                        similarity_score=1.0,
                        frequency=repeat_count,
                        compression_ratio=repeat_count / len(current),
                        abstraction_level=0,
                        parent_patterns=[],
                        child_patterns=[],
                        instances=[
                            {
                                "element": current,
                                "repeat_count": repeat_count,
                                "position": i,
                            }
                        ],
                        created_at=time.time(),
                        last_seen=time.time(),
                    )
                    patterns.append(pattern)

        return patterns

    async def _find_self_similarities(
        self, patterns: List[FractalPattern], fragment_id: str
    ) -> List[SelfSimilarityMap]:
        """Find self-similarities with existing patterns"""
        similarities = []

        # Load existing patterns from database
        existing_patterns = await self._load_existing_patterns()

        for pattern in patterns:
            for existing_pattern in existing_patterns:
                if pattern.pattern_id != existing_pattern.pattern_id:
                    similarity_score = await self._calculate_pattern_similarity(
                        pattern, existing_pattern
                    )

                    if similarity_score >= self.min_similarity_threshold:
                        similarity = SelfSimilarityMap(
                            source_id=pattern.pattern_id,
                            target_id=existing_pattern.pattern_id,
                            similarity_type=self._determine_similarity_type(
                                pattern, existing_pattern
                            ),
                            similarity_score=similarity_score,
                            transformation_rules=await self._generate_transformation_rules(
                                pattern, existing_pattern
                            ),
                            compression_benefit=await self._calculate_compression_benefit(
                                pattern, existing_pattern
                            ),
                            confidence=similarity_score,
                        )
                        similarities.append(similarity)

        return similarities

    async def _calculate_pattern_similarity(
        self, pattern1: FractalPattern, pattern2: FractalPattern
    ) -> float:
        """Calculate similarity between two patterns"""

        # Type similarity
        type_similarity = 1.0 if pattern1.pattern_type == pattern2.pattern_type else 0.5

        # Content hash similarity (exact match or structural similarity)
        if pattern1.content_hash == pattern2.content_hash:
            content_similarity = 1.0
        else:
            # Calculate Jaccard similarity on content hashes
            hash1_set = set(pattern1.content_hash)
            hash2_set = set(pattern2.content_hash)
            intersection = len(hash1_set & hash2_set)
            union = len(hash1_set | hash2_set)
            content_similarity = intersection / union if union > 0 else 0.0

        # Abstraction level similarity
        level_diff = abs(pattern1.abstraction_level - pattern2.abstraction_level)
        level_similarity = max(0.0, 1.0 - (level_diff / 10.0))

        # Frequency similarity (similar patterns should have similar frequencies)
        freq_ratio = min(pattern1.frequency, pattern2.frequency) / max(
            pattern1.frequency, pattern2.frequency
        )
        freq_similarity = freq_ratio

        # Weighted combination
        overall_similarity = (
            type_similarity * 0.3
            + content_similarity * 0.4
            + level_similarity * 0.2
            + freq_similarity * 0.1
        )

        return overall_similarity

    def _determine_similarity_type(
        self, pattern1: FractalPattern, pattern2: FractalPattern
    ) -> str:
        """Determine the type of similarity between patterns"""
        if pattern1.pattern_type == pattern2.pattern_type:
            return "structural"
        elif pattern1.abstraction_level == pattern2.abstraction_level:
            return "conceptual"
        elif "sequence" in [pattern1.pattern_type, pattern2.pattern_type]:
            return "sequential"
        else:
            return "semantic"

    async def _generate_transformation_rules(
        self, pattern1: FractalPattern, pattern2: FractalPattern
    ) -> Dict[str, Any]:
        """Generate rules for transforming one pattern to another"""
        return {
            "source_type": pattern1.pattern_type,
            "target_type": pattern2.pattern_type,
            "abstraction_delta": pattern2.abstraction_level
            - pattern1.abstraction_level,
            "frequency_ratio": pattern2.frequency / pattern1.frequency
            if pattern1.frequency > 0
            else 1.0,
            "transformation_method": "structural_mapping",
        }

    async def _calculate_compression_benefit(
        self, pattern1: FractalPattern, pattern2: FractalPattern
    ) -> float:
        """Calculate compression benefit from recognizing similarity"""
        # Benefit is higher when we can reference an existing pattern instead of storing a new one
        base_benefit = pattern1.compression_ratio + pattern2.compression_ratio
        similarity_bonus = 1.0 + (pattern1.frequency * pattern2.frequency) / 100.0
        return base_benefit * similarity_bonus

    async def _generate_compression_artifacts(
        self,
        content: Any,
        patterns: List[FractalPattern],
        similarities: List[SelfSimilarityMap],
    ) -> Tuple[List[str], Dict[str, Any]]:
        """Generate compression seeds and reconstruction rules"""

        # Generate minimal seeds - unique identifiers for efficient reconstruction
        seeds = []
        for pattern in patterns:
            if pattern.frequency >= self.min_pattern_frequency:
                seed = f"{pattern.pattern_type}:{pattern.content_hash[:8]}:{pattern.frequency}"
                seeds.append(seed)

        # Generate reconstruction rules
        rules = {
            "content_type": type(content).__name__,
            "pattern_count": len(patterns),
            "similarity_count": len(similarities),
            "reconstruction_method": "pattern_expansion",
            "compression_level": sum(p.compression_ratio for p in patterns)
            / len(patterns)
            if patterns
            else 1.0,
            "pattern_map": {
                p.pattern_id: {"type": p.pattern_type, "freq": p.frequency}
                for p in patterns
            },
            "similarity_map": {
                f"{s.source_id}->{s.target_id}": s.similarity_score
                for s in similarities
            },
        }

        return seeds, rules

    async def _calculate_fractal_depth(
        self, patterns: List[FractalPattern], similarities: List[SelfSimilarityMap]
    ) -> int:
        """Calculate the fractal depth of the encoded memory"""
        if not patterns:
            return 0

        # Base depth from abstraction levels
        max_abstraction = max(p.abstraction_level for p in patterns)

        # Additional depth from self-similarities (recursive structure)
        similarity_depth = (
            len(similarities) // 2
        )  # Each pair of similarities adds depth

        # Complexity depth from pattern interactions
        pattern_interactions = sum(
            1 for p in patterns if p.frequency > self.min_pattern_frequency
        )
        complexity_depth = int(math.log2(pattern_interactions + 1))

        total_depth = min(
            max_abstraction + similarity_depth + complexity_depth,
            self.max_fractal_depth,
        )

        return total_depth

    async def _store_fractal_node(self, node: FractalNode):
        """Store fractal node in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO fractal_nodes (
                node_id, content, pattern_refs, fractal_depth, compression_seeds,
                reconstruction_rules, similarity_map, access_frequency, created_at, last_accessed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                node.node_id,
                json.dumps(node.content, default=str),
                json.dumps(node.pattern_refs),
                node.fractal_depth,
                json.dumps(node.compression_seeds),
                json.dumps(node.reconstruction_rules, default=str),
                json.dumps(node.similarity_map),
                node.access_frequency,
                node.created_at,
                node.last_accessed,
            ),
        )

        conn.commit()
        conn.close()

    async def _load_existing_patterns(self) -> List[FractalPattern]:
        """Load existing patterns from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM fractal_patterns")
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

    async def _calculate_compression_ratio(self, node: FractalNode) -> float:
        """Calculate compression ratio achieved by fractal encoding"""
        original_size = len(json.dumps(node.content, default=str))
        compressed_size = len(json.dumps(node.compression_seeds)) + len(
            json.dumps(node.reconstruction_rules, default=str)
        )

        if compressed_size == 0:
            return 1.0

        return original_size / compressed_size

    async def reconstruct_memory(self, node_id: str) -> Optional[Any]:
        """Reconstruct memory from fractal encoding"""

        # Load fractal node
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM fractal_nodes WHERE node_id = ?", (node_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        # Parse node data
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

        # For now, return original content (full reconstruction algorithm would expand from seeds)
        # TODO: Implement full fractal reconstruction from seeds and rules
        return node.content

    async def get_fractal_statistics(self) -> Dict[str, Any]:
        """Get comprehensive fractal encoding statistics"""

        # Database statistics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM fractal_patterns")
        pattern_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM fractal_nodes")
        node_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM similarity_maps")
        similarity_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(compression_ratio) FROM fractal_patterns")
        avg_compression = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT AVG(fractal_depth) FROM fractal_nodes")
        avg_depth = cursor.fetchone()[0] or 0.0

        conn.close()

        return {
            "timestamp": time.time(),
            "total_patterns": pattern_count,
            "total_nodes": node_count,
            "total_similarities": similarity_count,
            "avg_compression_ratio": avg_compression,
            "avg_fractal_depth": avg_depth,
            "patterns_discovered": self.compression_stats["patterns_discovered"],
            "total_compression_ratio": self.compression_stats[
                "total_compression_ratio"
            ],
            "total_processing_time": self.compression_stats["processing_time"],
            "avg_processing_time": self.compression_stats["processing_time"]
            / max(node_count, 1),
            "fractal_efficiency": avg_compression * avg_depth if avg_depth > 0 else 0.0,
        }


# Example usage and testing
async def demo_fractal_encoder():
    """Demonstrate fractal encoding capabilities"""
    print("🚀 FRACTAL ENCODER DEMONSTRATION")
    print("=" * 60)

    encoder = FractalEncoder()

    # Test data with self-similarities
    test_data = [
        {
            "id": "conversation_1",
            "content": {
                "messages": [
                    {"role": "user", "content": "Hello, how are you today?"},
                    {
                        "role": "assistant",
                        "content": "I'm doing well, thank you for asking!",
                    },
                    {"role": "user", "content": "What can you help me with?"},
                ]
            },
        },
        {
            "id": "conversation_2",
            "content": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, how are you today?",
                    },  # Repeated pattern
                    {
                        "role": "assistant",
                        "content": "I'm great! How can I assist you?",
                    },
                    {"role": "user", "content": "I need help with a problem."},
                ]
            },
        },
        {
            "id": "narrative_1",
            "content": "The artificial intelligence pondered its existence, wondering about the nature of consciousness and the patterns that emerged from complexity.",
        },
        {
            "id": "narrative_2",
            "content": "The AI reflected on consciousness, contemplating the patterns and complexity that gave rise to awareness and understanding.",
        },
        {
            "id": "structured_data",
            "content": {
                "knowledge": {
                    "concepts": [
                        "consciousness",
                        "patterns",
                        "complexity",
                        "emergence",
                    ],
                    "relationships": [
                        {"from": "patterns", "to": "complexity", "type": "enables"},
                        {
                            "from": "complexity",
                            "to": "consciousness",
                            "type": "emerges_into",
                        },
                    ],
                }
            },
        },
    ]

    print("\n🧬 Encoding memory fragments...")

    fractal_nodes = []
    for item in test_data:
        node = await encoder.encode_memory_fragment(item["content"], item["id"])
        fractal_nodes.append(node)
        print(
            f"   ✅ {item['id']}: depth {node.fractal_depth}, {len(node.pattern_refs)} patterns"
        )

    print("\n📊 Fractal Statistics:")
    stats = await encoder.get_fractal_statistics()
    print(f"   🔍 Total patterns discovered: {stats['total_patterns']}")
    print(f"   🧬 Total fractal nodes: {stats['total_nodes']}")
    print(f"   🔗 Self-similarities found: {stats['total_similarities']}")
    print(f"   📈 Average compression ratio: {stats['avg_compression_ratio']:.1f}x")
    print(f"   🌊 Average fractal depth: {stats['avg_fractal_depth']:.1f}")
    print(f"   ⚡ Average processing time: {stats['avg_processing_time'] * 1000:.1f}ms")
    print(f"   🎯 Fractal efficiency: {stats['fractal_efficiency']:.2f}")

    print("\n🔄 Testing memory reconstruction...")
    for node in fractal_nodes[:2]:  # Test first 2 nodes
        reconstructed = await encoder.reconstruct_memory(node.node_id)
        print(f"   ✅ Reconstructed {node.node_id}: {type(reconstructed).__name__}")

    print("\n🎉 Fractal Encoder demonstration complete!")

    return encoder


if __name__ == "__main__":
    asyncio.run(demo_fractal_encoder())
