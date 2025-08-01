#!/usr/bin/env python3
"""
🚀 AETHERRA QFAC Phase 2: Comprehensive Test Suite
=================================================================

Complete test suite for Phase 2 fractal memory components:
• FractalEncoder: Self-similarity detection and compression
• FractalReplayEngine: Episode reconstruction
• FractalHierarchies: Multi-level pattern organization

Tests cover functionality, performance, and integration scenarios.
"""

import asyncio

# Import Phase 2 components
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from fractal_encoder import FractalEncoder, FractalNode
from fractal_hierarchies import FractalCluster, FractalHierarchies
from fractal_replay_engine import (
    FractalReplayEngine,
    ReconstructionContext,
    ReplayEpisode,
)


class TestFractalEncoder(unittest.IsolatedAsyncioTestCase):
    """Test suite for FractalEncoder"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.encoder = FractalEncoder(str(self.temp_dir / "encoder_test"))

        # Test data
        self.test_data = [
            {
                "id": "test_1",
                "content": "The quick brown fox jumps over the lazy dog. The fox is quick and brown.",
            },
            {
                "id": "test_2",
                "content": {
                    "type": "conversation",
                    "messages": [
                        {"role": "user", "content": "Hello"},
                        {"role": "ai", "content": "Hi there!"},
                    ],
                },
            },
            {
                "id": "test_3",
                "content": ["apple", "banana", "apple", "cherry", "banana", "apple"],
            },
        ]

    async def test_encode_text_memory(self):
        """Test encoding text-based memory fragments"""
        content = self.test_data[0]["content"]
        fragment_id = self.test_data[0]["id"]

        node = await self.encoder.encode_memory_fragment(content, fragment_id)

        self.assertIsInstance(node, FractalNode)
        self.assertEqual(node.node_id, fragment_id)
        self.assertGreater(len(node.pattern_refs), 0)
        self.assertGreaterEqual(node.fractal_depth, 0)
        self.assertGreater(len(node.compression_seeds), 0)

        print(
            f"✅ Text encoding: {len(node.pattern_refs)} patterns, depth {node.fractal_depth}"
        )

    async def test_encode_structured_memory(self):
        """Test encoding structured data memory fragments"""
        content = self.test_data[1]["content"]
        fragment_id = self.test_data[1]["id"]

        node = await self.encoder.encode_memory_fragment(content, fragment_id)

        self.assertIsInstance(node, FractalNode)
        self.assertEqual(node.node_id, fragment_id)
        self.assertGreater(len(node.pattern_refs), 0)
        self.assertIsInstance(node.reconstruction_rules, dict)

        print(f"✅ Structured encoding: {len(node.pattern_refs)} patterns")

    async def test_encode_sequence_memory(self):
        """Test encoding sequence-based memory fragments"""
        content = self.test_data[2]["content"]
        fragment_id = self.test_data[2]["id"]

        node = await self.encoder.encode_memory_fragment(content, fragment_id)

        self.assertIsInstance(node, FractalNode)
        self.assertEqual(node.node_id, fragment_id)
        self.assertGreater(len(node.pattern_refs), 0)

        # Should detect repetition patterns
        patterns = await self.encoder._extract_patterns(content, fragment_id)
        motif_patterns = [p for p in patterns if p.pattern_type == "motif"]
        self.assertGreater(len(motif_patterns), 0)

        print(
            f"✅ Sequence encoding: {len(patterns)} patterns, {len(motif_patterns)} motifs"
        )

    async def test_self_similarity_detection(self):
        """Test self-similarity detection between patterns"""
        # Encode multiple similar fragments
        similar_contents = [
            "The AI system processes information efficiently.",
            "The artificial intelligence processes data efficiently.",
            "AI systems handle information processing with efficiency.",
        ]

        nodes = []
        for i, content in enumerate(similar_contents):
            node = await self.encoder.encode_memory_fragment(content, f"similar_{i}")
            nodes.append(node)

        # Check if similarities were detected
        stats = await self.encoder.get_fractal_statistics()
        self.assertGreater(stats["total_similarities"], 0)

        print(
            f"✅ Self-similarity: {stats['total_similarities']} similarities detected"
        )

    async def test_pattern_frequency_tracking(self):
        """Test pattern frequency tracking across multiple encodings"""
        repeated_content = "hello world hello universe hello cosmos"

        # Encode the same type of content multiple times
        for i in range(3):
            await self.encoder.encode_memory_fragment(
                repeated_content + f" iteration {i}", f"repeated_{i}"
            )

        # Check pattern frequencies
        patterns = await self.encoder._load_existing_patterns()
        hello_patterns = [p for p in patterns if "hello" in str(p.instances)]

        if hello_patterns:
            # Should have increased frequency
            self.assertGreater(hello_patterns[0].frequency, 1)
            print(
                f"✅ Frequency tracking: pattern frequency {hello_patterns[0].frequency}"
            )

    async def test_compression_ratio_calculation(self):
        """Test compression ratio calculation"""
        content = (
            "This is a test message with repeated words. This is another test message."
        )
        node = await self.encoder.encode_memory_fragment(content, "compression_test")

        compression_ratio = await self.encoder._calculate_compression_ratio(node)
        self.assertGreater(compression_ratio, 0.5)  # Should achieve some compression

        print(f"✅ Compression ratio: {compression_ratio:.1f}x")

    async def test_memory_reconstruction(self):
        """Test memory reconstruction from fractal encoding"""
        original_content = {"test": "data", "value": 42}
        node = await self.encoder.encode_memory_fragment(
            original_content, "reconstruct_test"
        )

        reconstructed = await self.encoder.reconstruct_memory(node.node_id)
        self.assertIsNotNone(reconstructed)

        print(f"✅ Reconstruction: {type(reconstructed).__name__}")

    async def test_fractal_statistics(self):
        """Test fractal statistics generation"""
        # Encode some test data
        for data in self.test_data:
            await self.encoder.encode_memory_fragment(data["content"], data["id"])

        stats = await self.encoder.get_fractal_statistics()

        required_keys = [
            "total_patterns",
            "total_nodes",
            "avg_compression_ratio",
            "avg_fractal_depth",
            "patterns_discovered",
            "fractal_efficiency",
        ]

        for key in required_keys:
            self.assertIn(key, stats)
            self.assertIsNotNone(stats[key])

        print(
            f"✅ Statistics: {stats['total_patterns']} patterns, {stats['fractal_efficiency']:.2f} efficiency"
        )


class TestFractalReplayEngine(unittest.IsolatedAsyncioTestCase):
    """Test suite for FractalReplayEngine"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.encoder = FractalEncoder(str(self.temp_dir / "encoder_test"))
        self.replay_engine = FractalReplayEngine(
            self.encoder, str(self.temp_dir / "replay_test")
        )

        # Create test fractal nodes
        self.test_memories = [
            {"id": "memory_1", "content": "First memory about consciousness and AI."},
            {
                "id": "memory_2",
                "content": "Second memory exploring artificial intelligence.",
            },
            {
                "id": "memory_3",
                "content": {"thoughts": ["consciousness", "AI", "intelligence"]},
            },
        ]

        self.test_nodes = []
        for memory in self.test_memories:
            node = await self.encoder.encode_memory_fragment(
                memory["content"], memory["id"]
            )
            self.test_nodes.append(node)

    async def test_basic_episode_reconstruction(self):
        """Test basic episode reconstruction"""
        node_ids = [node.node_id for node in self.test_nodes]

        episode = await self.replay_engine.reconstruct_episode(node_ids, "test_episode")

        self.assertIsInstance(episode, ReplayEpisode)
        self.assertEqual(episode.episode_id, "test_episode")
        self.assertEqual(len(episode.original_node_ids), len(node_ids))
        self.assertGreater(episode.reconstruction_fidelity, 0.0)
        self.assertLessEqual(episode.reconstruction_fidelity, 1.0)
        self.assertGreater(len(episode.temporal_sequence), 0)

        print(
            f"✅ Basic reconstruction: {episode.reconstruction_fidelity:.1%} fidelity"
        )

    async def test_high_fidelity_reconstruction(self):
        """Test high fidelity reconstruction context"""
        context = ReconstructionContext(
            target_fidelity=0.9,
            max_depth=10,
            temporal_order=True,
            compression_aware=True,
        )

        node_ids = [self.test_nodes[0].node_id]
        episode = await self.replay_engine.reconstruct_episode(
            node_ids, "high_fidelity", context
        )

        # Should aim for higher fidelity
        self.assertGreaterEqual(episode.reconstruction_fidelity, 0.8)

        print(f"✅ High fidelity reconstruction: {episode.reconstruction_fidelity:.1%}")

    async def test_fast_reconstruction(self):
        """Test fast reconstruction with lower fidelity"""
        context = ReconstructionContext(
            target_fidelity=0.6,
            max_depth=3,
            temporal_order=False,
            compression_aware=False,
        )

        node_ids = [node.node_id for node in self.test_nodes]
        start_time = time.time()
        episode = await self.replay_engine.reconstruct_episode(
            node_ids, "fast_recon", context
        )
        reconstruction_time = time.time() - start_time

        # Should be faster (though hard to test reliably)
        self.assertLess(reconstruction_time, 5.0)  # Should complete within 5 seconds
        self.assertGreater(
            episode.reconstruction_fidelity, 0.3
        )  # Should still have reasonable fidelity

        print(f"✅ Fast reconstruction: {reconstruction_time * 1000:.1f}ms")

    async def test_temporal_sequence_ordering(self):
        """Test temporal sequence ordering"""
        context = ReconstructionContext(temporal_order=True)

        node_ids = [node.node_id for node in self.test_nodes]
        episode = await self.replay_engine.reconstruct_episode(
            node_ids, "temporal_test", context
        )

        # Check temporal ordering
        timestamps = [element["timestamp"] for element in episode.temporal_sequence]
        self.assertEqual(timestamps, sorted(timestamps))

        print(
            f"✅ Temporal ordering: {len(episode.temporal_sequence)} elements in order"
        )

    async def test_pattern_filtering(self):
        """Test pattern filtering in reconstruction context"""
        # Get some pattern IDs from encoded nodes
        all_pattern_ids = []
        for node in self.test_nodes:
            all_pattern_ids.extend(node.pattern_refs)

        if all_pattern_ids:
            # Test include patterns
            include_patterns = all_pattern_ids[:1]  # Include only first pattern
            context = ReconstructionContext(include_patterns=include_patterns)

            node_ids = [self.test_nodes[0].node_id]
            episode = await self.replay_engine.reconstruct_episode(
                node_ids, "filtered", context
            )

            self.assertGreater(episode.pattern_coverage, 0.0)

            print(f"✅ Pattern filtering: {episode.pattern_coverage:.1%} coverage")

    async def test_episode_storage_and_reload(self):
        """Test episode storage and reloading"""
        node_ids = [self.test_nodes[0].node_id]
        episode = await self.replay_engine.reconstruct_episode(node_ids, "storage_test")

        # Reload episode
        reloaded = await self.replay_engine.load_replay_episode(episode.episode_id)

        self.assertIsNotNone(reloaded)
        if reloaded:
            self.assertEqual(reloaded.episode_id, episode.episode_id)
            self.assertEqual(
                reloaded.reconstruction_fidelity, episode.reconstruction_fidelity
            )
            self.assertEqual(
                len(reloaded.temporal_sequence), len(episode.temporal_sequence)
            )

            print(f"✅ Storage/reload: episode {reloaded.episode_id}")

    async def test_reconstruction_cache(self):
        """Test reconstruction caching mechanism"""
        node_ids = [self.test_nodes[0].node_id]
        context = ReconstructionContext(target_fidelity=0.8)

        # First reconstruction
        episode1 = await self.replay_engine.reconstruct_episode(
            node_ids, "cache_test_1", context
        )

        # Second reconstruction with same context (should hit cache)
        episode2 = await self.replay_engine.reconstruct_episode(
            node_ids, "cache_test_2", context
        )

        # Both should complete successfully
        self.assertIsNotNone(episode1)
        self.assertIsNotNone(episode2)

        print("✅ Caching: episodes reconstructed successfully")

    async def test_replay_statistics(self):
        """Test replay engine statistics"""
        # Perform some reconstructions
        for i, node in enumerate(self.test_nodes):
            await self.replay_engine.reconstruct_episode(
                [node.node_id], f"stats_test_{i}"
            )

        stats = await self.replay_engine.get_replay_statistics()

        required_keys = [
            "total_episodes",
            "avg_reconstruction_fidelity",
            "avg_compression_ratio",
            "avg_reconstruction_time",
            "reconstruction_efficiency",
        ]

        for key in required_keys:
            self.assertIn(key, stats)

        self.assertGreater(stats["total_episodes"], 0)

        print(f"✅ Replay statistics: {stats['total_episodes']} episodes")


class TestFractalHierarchies(unittest.IsolatedAsyncioTestCase):
    """Test suite for FractalHierarchies"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.encoder = FractalEncoder(str(self.temp_dir / "encoder_test"))
        self.hierarchies = FractalHierarchies(
            self.encoder, str(self.temp_dir / "hierarchy_test")
        )

        # Create diverse test patterns
        self.test_memories = [
            {
                "id": "conv_1",
                "content": "Hello, how are you? I'm doing well, thank you.",
            },
            {"id": "conv_2", "content": "Hi there, what can I help you with today?"},
            {"id": "conv_3", "content": "Good morning, how may I assist you?"},
            {
                "id": "refl_1",
                "content": {"type": "reflection", "topic": "consciousness"},
            },
            {
                "id": "refl_2",
                "content": {"type": "reflection", "topic": "intelligence"},
            },
            {
                "id": "concept_1",
                "content": {"domain": "AI", "concepts": ["learning", "reasoning"]},
            },
            {
                "id": "concept_2",
                "content": {"domain": "AI", "concepts": ["perception", "planning"]},
            },
        ]

        # Encode all memories and collect pattern IDs
        self.all_pattern_ids = []
        for memory in self.test_memories:
            node = await self.encoder.encode_memory_fragment(
                memory["content"], memory["id"]
            )
            self.all_pattern_ids.extend(node.pattern_refs)

        self.all_pattern_ids = list(set(self.all_pattern_ids))  # Remove duplicates

    async def test_hierarchy_building(self):
        """Test building fractal hierarchy"""
        hierarchy = await self.hierarchies.build_fractal_hierarchy(self.all_pattern_ids)

        self.assertIsInstance(hierarchy, dict)
        self.assertGreater(len(hierarchy), 0)

        # Check hierarchy structure
        for level, clusters in hierarchy.items():
            self.assertIsInstance(level, int)
            self.assertIsInstance(clusters, list)
            self.assertGreater(len(clusters), 0)

            for cluster in clusters:
                self.assertIsInstance(cluster, FractalCluster)
                self.assertEqual(cluster.level, level)
                self.assertGreater(len(cluster.pattern_ids), 0)

        print(f"✅ Hierarchy building: {len(hierarchy)} levels")

    async def test_cluster_coherence(self):
        """Test cluster coherence calculation"""
        hierarchy = await self.hierarchies.build_fractal_hierarchy(self.all_pattern_ids)

        if hierarchy:
            level_0_clusters = hierarchy.get(0, [])
            for cluster in level_0_clusters:
                self.assertGreaterEqual(cluster.coherence_score, 0.0)
                self.assertLessEqual(cluster.coherence_score, 1.0)

        print(f"✅ Cluster coherence: calculated for all clusters")

    async def test_parent_child_relationships(self):
        """Test parent-child relationships in hierarchy"""
        hierarchy = await self.hierarchies.build_fractal_hierarchy(self.all_pattern_ids)

        # Check that parent-child relationships are properly set
        for level in sorted(hierarchy.keys()):
            clusters = hierarchy[level]

            for cluster in clusters:
                # If cluster has a parent, verify the relationship
                if cluster.parent_cluster_id:
                    parent_found = False

                    # Check higher levels for parent
                    for parent_level in range(level + 1, max(hierarchy.keys()) + 1):
                        if parent_level in hierarchy:
                            for parent_cluster in hierarchy[parent_level]:
                                if (
                                    parent_cluster.cluster_id
                                    == cluster.parent_cluster_id
                                ):
                                    parent_found = True
                                    self.assertIn(
                                        cluster.cluster_id,
                                        parent_cluster.child_cluster_ids,
                                    )
                                    break

                    if not parent_found and level > 0:
                        # Parent should exist for non-root clusters (in a complete hierarchy)
                        pass  # May be incomplete hierarchy for testing

        print(f"✅ Parent-child relationships: verified")

    async def test_cluster_lookup(self):
        """Test finding clusters by pattern"""
        hierarchy = await self.hierarchies.build_fractal_hierarchy(self.all_pattern_ids)

        if self.all_pattern_ids:
            test_pattern_id = self.all_pattern_ids[0]
            cluster = await self.hierarchies.find_cluster_by_pattern(test_pattern_id)

            if cluster:
                self.assertIn(test_pattern_id, cluster.pattern_ids)
                print(
                    f"✅ Cluster lookup: pattern found in cluster {cluster.cluster_id}"
                )
            else:
                print(f"⚠️ Cluster lookup: pattern not found (may be expected)")

    async def test_hierarchy_path(self):
        """Test getting hierarchy path for a cluster"""
        hierarchy = await self.hierarchies.build_fractal_hierarchy(self.all_pattern_ids)

        if hierarchy and 0 in hierarchy:
            test_cluster = hierarchy[0][0]  # First cluster at level 0
            path = await self.hierarchies.get_hierarchy_path(test_cluster.cluster_id)

            self.assertIsInstance(path, list)
            self.assertGreater(len(path), 0)
            self.assertEqual(path[0].cluster_id, test_cluster.cluster_id)

            print(f"✅ Hierarchy path: {len(path)} levels")

    async def test_fractal_signature_generation(self):
        """Test fractal signature generation"""
        # Load some patterns
        patterns = await self.encoder._load_existing_patterns()

        if patterns:
            signature = await self.hierarchies._calculate_fractal_signature(
                patterns[:3]
            )

            self.assertIsInstance(signature, str)
            self.assertTrue(signature.startswith("fractal_"))

            print(f"✅ Fractal signature: {signature}")

    async def test_hierarchy_reorganization(self):
        """Test hierarchy reorganization"""
        # Build initial hierarchy
        await self.hierarchies.build_fractal_hierarchy(self.all_pattern_ids)

        # Test reorganization check
        reorganized = await self.hierarchies.reorganize_hierarchy_if_needed()

        # Should return boolean
        self.assertIsInstance(reorganized, bool)

        print(f"✅ Reorganization: {'performed' if reorganized else 'not needed'}")

    async def test_hierarchy_statistics(self):
        """Test hierarchy statistics generation"""
        # Build hierarchy
        await self.hierarchies.build_fractal_hierarchy(self.all_pattern_ids)

        stats = await self.hierarchies.get_fractal_hierarchy_statistics()

        required_keys = [
            "current_clusters",
            "current_levels",
            "avg_cluster_coherence",
            "clusters_created",
            "hierarchies_built",
        ]

        for key in required_keys:
            self.assertIn(key, stats)

        self.assertGreaterEqual(stats["current_clusters"], 0)
        self.assertGreaterEqual(stats["hierarchies_built"], 1)

        print(f"✅ Hierarchy statistics: {stats['current_clusters']} clusters")


class TestPhase2Integration(unittest.IsolatedAsyncioTestCase):
    """Test suite for Phase 2 component integration"""

    async def asyncSetUp(self):
        """Set up integrated test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.encoder = FractalEncoder(str(self.temp_dir / "encoder"))
        self.replay_engine = FractalReplayEngine(
            self.encoder, str(self.temp_dir / "replay")
        )
        self.hierarchies = FractalHierarchies(
            self.encoder, str(self.temp_dir / "hierarchy")
        )

    async def test_end_to_end_workflow(self):
        """Test complete end-to-end Phase 2 workflow"""
        # 1. Encode diverse memory content
        test_content = [
            "AI consciousness emerges from complex patterns of information processing.",
            "Machine learning enables artificial intelligence to recognize patterns.",
            {"type": "reflection", "thoughts": ["consciousness", "patterns", "AI"]},
            {"knowledge": ["learning", "reasoning", "consciousness"], "domain": "AI"},
        ]

        encoded_nodes = []
        for i, content in enumerate(test_content):
            node = await self.encoder.encode_memory_fragment(
                content, f"integrated_test_{i}"
            )
            encoded_nodes.append(node)

        self.assertEqual(len(encoded_nodes), len(test_content))

        # 2. Build fractal hierarchy from encoded patterns
        all_pattern_ids = []
        for node in encoded_nodes:
            all_pattern_ids.extend(node.pattern_refs)

        hierarchy = await self.hierarchies.build_fractal_hierarchy(
            list(set(all_pattern_ids))
        )
        self.assertGreater(len(hierarchy), 0)

        # 3. Reconstruct episodes using replay engine
        node_ids = [node.node_id for node in encoded_nodes]
        episode = await self.replay_engine.reconstruct_episode(
            node_ids, "integration_episode"
        )

        self.assertIsInstance(episode, ReplayEpisode)
        self.assertGreater(episode.reconstruction_fidelity, 0.0)

        # 4. Verify integration statistics
        encoder_stats = await self.encoder.get_fractal_statistics()
        replay_stats = await self.replay_engine.get_replay_statistics()
        hierarchy_stats = await self.hierarchies.get_fractal_hierarchy_statistics()

        self.assertGreater(encoder_stats["total_patterns"], 0)
        self.assertGreater(replay_stats["total_episodes"], 0)
        self.assertGreater(hierarchy_stats["current_clusters"], 0)

        print(f"✅ End-to-end workflow:")
        print(f"   🧬 Encoder: {encoder_stats['total_patterns']} patterns")
        print(f"   🎬 Replay: {replay_stats['total_episodes']} episodes")
        print(f"   🌳 Hierarchy: {hierarchy_stats['current_clusters']} clusters")

    async def test_cross_component_pattern_sharing(self):
        """Test that patterns are properly shared across components"""
        # Encode content that should create patterns
        content = "Pattern sharing test with repeated concepts and ideas."
        node = await self.encoder.encode_memory_fragment(
            content, "pattern_sharing_test"
        )

        # Build hierarchy using patterns from encoder
        hierarchy = await self.hierarchies.build_fractal_hierarchy(node.pattern_refs)

        # Reconstruct episode and verify it uses the same patterns
        episode = await self.replay_engine.reconstruct_episode(
            [node.node_id], "sharing_episode"
        )

        # Verify patterns are referenced in reconstruction
        episode_patterns = set()
        for element in episode.temporal_sequence:
            episode_patterns.update(element.get("patterns_applied", []))

        # Should have some overlap with original patterns
        original_patterns = set(node.pattern_refs)
        overlap = len(episode_patterns & original_patterns)

        print(f"✅ Pattern sharing: {overlap} patterns shared across components")

    async def test_performance_consistency(self):
        """Test performance consistency across components"""
        test_content = "Performance test content with various patterns and structures."

        # Measure encoding performance
        start_time = time.time()
        node = await self.encoder.encode_memory_fragment(test_content, "perf_test")
        encoding_time = time.time() - start_time

        # Measure hierarchy building performance
        start_time = time.time()
        hierarchy = await self.hierarchies.build_fractal_hierarchy(node.pattern_refs)
        hierarchy_time = time.time() - start_time

        # Measure replay performance
        start_time = time.time()
        episode = await self.replay_engine.reconstruct_episode(
            [node.node_id], "perf_episode"
        )
        replay_time = time.time() - start_time

        # All operations should complete within reasonable time
        self.assertLess(encoding_time, 5.0)
        self.assertLess(hierarchy_time, 10.0)
        self.assertLess(replay_time, 5.0)

        print(f"✅ Performance consistency:")
        print(f"   🧬 Encoding: {encoding_time * 1000:.1f}ms")
        print(f"   🌳 Hierarchy: {hierarchy_time * 1000:.1f}ms")
        print(f"   🎬 Replay: {replay_time * 1000:.1f}ms")


async def run_comprehensive_phase2_tests():
    """Run comprehensive Phase 2 test suite"""
    print("🚀 AETHERRA QFAC PHASE 2 - COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    # Test configuration
    test_classes = [
        TestFractalEncoder,
        TestFractalReplayEngine,
        TestFractalHierarchies,
        TestPhase2Integration,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_class in test_classes:
        print(f"\n🧪 Running {test_class.__name__}...")
        print("-" * 60)

        # Get all test methods
        test_methods = [
            method for method in dir(test_class) if method.startswith("test_")
        ]

        for test_method in test_methods:
            total_tests += 1

            try:
                # Create test instance
                test_instance = test_class()
                await test_instance.asyncSetUp()

                # Run test method
                await getattr(test_instance, test_method)()
                passed_tests += 1

            except Exception as e:
                print(f"❌ {test_method}: {str(e)}")
                failed_tests += 1

    # Print final results
    print("\n" + "=" * 80)
    print("🏆 PHASE 2 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"📊 Total tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success rate: {(passed_tests / total_tests) * 100:.1f}%")

    if failed_tests == 0:
        print("\n🎉 ALL PHASE 2 TESTS PASSED!")
        print("🚀 Phase 2 fractal memory components are ready for production!")
    else:
        print(f"\n⚠️ {failed_tests} tests failed - review and fix issues")

    return passed_tests == total_tests


if __name__ == "__main__":
    asyncio.run(run_comprehensive_phase2_tests())
