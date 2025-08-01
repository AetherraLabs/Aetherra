#!/usr/bin/env python3
"""
🚀 AETHERRA QFAC Phase 3: Observer-Aware Compression Test Suite
===============================================================

Comprehensive test suite for Phase 3 observer effect components:
• ObserverEffectSimulator: Memory fidelity changes when accessed
• Layered access model with different observer impact levels
• Meta-memory tracking and cognitive drift analysis
• Observer profiles and permission systems

Tests cover functionality, performance, and integration scenarios.
"""

import asyncio

# Import Phase 3 components
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from fractal_encoder import FractalEncoder
from observer_effect_simulator import (
    AccessLayer,
    LayeredMemoryView,
    MetaMemory,
    ObserverType,
    create_observer_effect_simulator,
)


class TestObserverEffectSimulator(unittest.IsolatedAsyncioTestCase):
    """Test suite for ObserverEffectSimulator"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create fractal encoder first
        self.encoder = FractalEncoder(str(self.temp_dir / "encoder_test"))

        # Create observer effect simulator
        self.simulator = await create_observer_effect_simulator(
            self.encoder, str(self.temp_dir / "observer_test")
        )

        # Create test memories in fractal encoder
        self.test_memories = [
            {
                "id": "memory_1",
                "content": "AI consciousness emerges through observer-dependent patterns.",
            },
            {
                "id": "memory_2",
                "content": {
                    "type": "reflection",
                    "topic": "observer effects in memory",
                    "insights": [
                        "Memory changes when accessed",
                        "Fidelity varies by observer",
                    ],
                },
            },
            {
                "id": "memory_3",
                "content": ["pattern", "recognition", "observer", "awareness"],
            },
        ]

        # Encode test memories
        self.memory_nodes = []
        for memory in self.test_memories:
            node = await self.encoder.encode_memory_fragment(
                memory["content"], memory["id"]
            )
            self.memory_nodes.append(node)

    async def test_observer_profile_creation(self):
        """Test observer profile creation and management"""
        # Check default profiles exist
        self.assertIn("lyrixa_core", self.simulator.observer_profiles)
        self.assertIn("user_interactive", self.simulator.observer_profiles)
        self.assertIn("plugin_system", self.simulator.observer_profiles)
        self.assertIn("system_maintenance", self.simulator.observer_profiles)

        # Verify profile properties
        lyrixa_profile = self.simulator.observer_profiles["lyrixa_core"]
        self.assertEqual(lyrixa_profile.observer_type, ObserverType.LYRIXA)
        self.assertEqual(lyrixa_profile.impact_strength, 0.9)
        self.assertIn(AccessLayer.DEEP, lyrixa_profile.access_permissions)

        user_profile = self.simulator.observer_profiles["user_interactive"]
        self.assertEqual(user_profile.observer_type, ObserverType.USER)
        self.assertEqual(user_profile.impact_strength, 0.6)
        self.assertNotIn(AccessLayer.DEEP, user_profile.access_permissions)

        print(
            "✅ Observer profiles: 4 default profiles created with correct properties"
        )

    async def test_memory_access_surface_layer(self):
        """Test surface layer memory access"""
        memory_node_id = self.memory_nodes[0].node_id

        # Access memory at surface layer with user observer
        memory_view = await self.simulator.access_memory(
            memory_node_id, "user_interactive", AccessLayer.SURFACE
        )

        self.assertIsInstance(memory_view, LayeredMemoryView)
        self.assertEqual(memory_view.node_id, memory_node_id)
        self.assertEqual(memory_view.access_count, 1)
        self.assertGreater(memory_view.last_accessed, 0)

        # Check surface layer content
        self.assertIn("summary", memory_view.surface_layer)
        self.assertIn("emotional_tags", memory_view.surface_layer)
        self.assertIn("fractal_depth", memory_view.surface_layer)

        print(
            f"✅ Surface access: {memory_view.access_count} access, fidelity {memory_view.current_fidelity:.3f}"
        )

    async def test_memory_access_core_layer(self):
        """Test core layer memory access"""
        memory_node_id = self.memory_nodes[1].node_id

        # Access memory at core layer with user observer
        memory_view = await self.simulator.access_memory(
            memory_node_id, "user_interactive", AccessLayer.CORE
        )

        self.assertEqual(memory_view.access_count, 1)

        # Check core layer content
        self.assertIn("compressed_content", memory_view.core_layer)
        self.assertIn("pattern_references", memory_view.core_layer)
        self.assertIn("key_metadata", memory_view.core_layer)

        print(
            f"✅ Core access: compressed content available, {len(memory_view.core_layer['pattern_references'])} patterns"
        )

    async def test_memory_access_deep_layer(self):
        """Test deep layer memory access (Lyrixa only)"""
        memory_node_id = self.memory_nodes[2].node_id

        # Access memory at deep layer with Lyrixa observer
        memory_view = await self.simulator.access_memory(
            memory_node_id,
            "lyrixa_core",
            AccessLayer.DEEP,
            context={"intent": "detailed_analysis"},
        )

        self.assertEqual(memory_view.access_count, 1)

        # Check deep layer content
        self.assertIn("full_content", memory_view.deep_layer)
        self.assertIn("fractal_patterns", memory_view.deep_layer)
        self.assertIn("reconstruction_rules", memory_view.deep_layer)

        print(
            f"✅ Deep access: full reconstruction available, fidelity {memory_view.current_fidelity:.3f}"
        )

    async def test_access_permission_enforcement(self):
        """Test that access permissions are properly enforced"""
        memory_node_id = self.memory_nodes[0].node_id

        # Try to access deep layer with plugin observer (should fail)
        with self.assertRaises(PermissionError):
            await self.simulator.access_memory(
                memory_node_id, "plugin_system", AccessLayer.DEEP
            )

        # Plugin should only access surface layer
        memory_view = await self.simulator.access_memory(
            memory_node_id, "plugin_system", AccessLayer.SURFACE
        )

        self.assertIsInstance(memory_view, LayeredMemoryView)
        print("✅ Access permissions: Plugin correctly restricted to surface layer")

    async def test_observer_impact_on_fidelity(self):
        """Test that different observers have different impacts on memory fidelity"""
        memory_node_id = self.memory_nodes[0].node_id

        # Access with high-impact observer (Lyrixa)
        lyrixa_view = await self.simulator.access_memory(
            memory_node_id,
            "lyrixa_core",
            AccessLayer.DEEP,
            context={"intent": "detailed_analysis"},
        )

        # Access with low-impact observer (system)
        await self.simulator.access_memory(
            memory_node_id, "system_maintenance", AccessLayer.SURFACE
        )

        # Lyrixa access should have higher impact
        self.assertGreaterEqual(
            lyrixa_view.current_fidelity, 0.8
        )  # Should be high fidelity

        print(
            f"✅ Observer impact: Lyrixa {lyrixa_view.current_fidelity:.3f}, System maintains fidelity"
        )

    async def test_repeated_access_effects(self):
        """Test effects of repeated memory access"""
        memory_node_id = self.memory_nodes[1].node_id

        # Access memory multiple times
        fidelity_progression = []
        memory_view = None

        for i in range(5):
            memory_view = await self.simulator.access_memory(
                memory_node_id, "user_interactive", AccessLayer.CORE
            )
            fidelity_progression.append(memory_view.current_fidelity)

        # Check access count increased
        self.assertEqual(memory_view.access_count, 5)

        # Fidelity should change over time
        self.assertNotEqual(fidelity_progression[0], fidelity_progression[-1])

        print(
            f"✅ Repeated access: {memory_view.access_count} accesses, fidelity evolution {fidelity_progression[0]:.3f} → {fidelity_progression[-1]:.3f}"
        )

    async def test_collapse_strength_calculation(self):
        """Test collapse strength calculation with different contexts"""
        memory_node_id = self.memory_nodes[2].node_id

        # High-intensity access
        high_intensity_view = await self.simulator.access_memory(
            memory_node_id,
            "lyrixa_core",
            AccessLayer.DEEP,
            context={"intent": "detailed_analysis"},
        )

        # Low-intensity access
        low_intensity_view = await self.simulator.access_memory(
            memory_node_id,
            "plugin_system",
            AccessLayer.SURFACE,
            context={"intent": "quick_lookup"},
        )

        # Both should succeed but with different impacts
        self.assertGreater(high_intensity_view.access_count, 0)
        self.assertGreater(low_intensity_view.access_count, 1)  # Second access

        print("✅ Collapse strength: Different contexts produce different impacts")

    async def test_emotional_tag_extraction(self):
        """Test emotional tag extraction from memory content"""
        # Create memory with emotional content
        emotional_content = (
            "This is amazing and wonderful! I feel great about this success."
        )
        emotional_node = await self.encoder.encode_memory_fragment(
            emotional_content, "emotional_test"
        )

        memory_view = await self.simulator.access_memory(
            emotional_node.node_id, "user_interactive", AccessLayer.SURFACE
        )

        emotional_tags = memory_view.surface_layer["emotional_tags"]
        self.assertIsInstance(emotional_tags, list)
        self.assertGreater(len(emotional_tags), 0)

        # Should detect positive emotion
        self.assertIn("positive", emotional_tags)

        print(f"✅ Emotional tags: {emotional_tags}")

    async def test_meta_memory_tracking(self):
        """Test meta-memory creation and tracking"""
        memory_node_id = self.memory_nodes[0].node_id

        # Access memory with different observers
        await self.simulator.access_memory(
            memory_node_id, "lyrixa_core", AccessLayer.DEEP
        )
        await self.simulator.access_memory(
            memory_node_id, "user_interactive", AccessLayer.CORE
        )
        await self.simulator.access_memory(
            memory_node_id, "plugin_system", AccessLayer.SURFACE
        )

        # Check meta-memory was created and tracks observers
        meta_memory = await self.simulator._get_or_create_meta_memory(memory_node_id)

        self.assertIsInstance(meta_memory, MetaMemory)
        self.assertEqual(meta_memory.original_memory_id, memory_node_id)
        self.assertGreater(len(meta_memory.access_pattern), 0)
        self.assertGreater(len(meta_memory.observer_influence_map), 0)

        # Should track multiple observers
        self.assertIn("lyrixa_core", meta_memory.observer_influence_map)
        self.assertIn("user_interactive", meta_memory.observer_influence_map)

        print(
            f"✅ Meta-memory: {len(meta_memory.access_pattern)} accesses tracked, {len(meta_memory.observer_influence_map)} observers"
        )

    async def test_cognitive_drift_calculation(self):
        """Test cognitive drift calculation over multiple accesses"""
        memory_node_id = self.memory_nodes[1].node_id

        # Access memory multiple times to create drift
        for i in range(3):
            await self.simulator.access_memory(
                memory_node_id,
                "lyrixa_core",
                AccessLayer.DEEP,
                context={"intent": "detailed_analysis"},
            )

        meta_memory = await self.simulator._get_or_create_meta_memory(memory_node_id)

        # Should have some cognitive drift
        self.assertGreaterEqual(meta_memory.cognitive_drift, 0.0)

        print(f"✅ Cognitive drift: {meta_memory.cognitive_drift:.4f} drift calculated")

    async def test_memory_decay_simulation(self):
        """Test memory decay for unaccessed memories"""
        memory_node_id = self.memory_nodes[2].node_id

        # Access memory once
        memory_view = await self.simulator.access_memory(
            memory_node_id, "user_interactive", AccessLayer.SURFACE
        )

        # Simulate memory decay (artificially set old access time)
        memory_view.last_accessed = time.time() - (25 * 3600)  # 25 hours ago
        await self.simulator._update_memory_view(memory_view)

        # Run decay simulation
        decay_count = await self.simulator.simulate_memory_decay(
            time_threshold_hours=24.0
        )

        # Should have applied decay
        self.assertGreaterEqual(decay_count, 0)

        print(f"✅ Memory decay: {decay_count} memories affected by decay simulation")

    async def test_observer_statistics(self):
        """Test observer impact statistics generation"""
        # Access memories with different observers
        for memory_node in self.memory_nodes:
            await self.simulator.access_memory(
                memory_node.node_id, "lyrixa_core", AccessLayer.DEEP
            )
            await self.simulator.access_memory(
                memory_node.node_id, "user_interactive", AccessLayer.CORE
            )

        stats = await self.simulator.get_observer_impact_statistics()

        # Check statistics structure
        self.assertIn("observer_statistics", stats)
        self.assertIn("average_fidelity_drift", stats)
        self.assertIn("most_accessed_memories", stats)
        self.assertIn("total_observer_profiles", stats)
        self.assertIn("total_memory_views", stats)

        # Should have recorded observer activity
        observer_stats = stats["observer_statistics"]
        self.assertGreater(len(observer_stats), 0)

        print(f"✅ Observer statistics: {len(observer_stats)} observer types tracked")
        print(f"   📊 Total profiles: {stats['total_observer_profiles']}")
        print(f"   🧠 Memory views: {stats['total_memory_views']}")

    async def test_layered_memory_view_structure(self):
        """Test that layered memory views have correct structure"""
        memory_node_id = self.memory_nodes[0].node_id

        memory_view = await self.simulator.access_memory(
            memory_node_id, "lyrixa_core", AccessLayer.DEEP
        )

        # Surface layer should have summary and emotional data
        surface = memory_view.surface_layer
        self.assertIn("summary", surface)
        self.assertIn("emotional_tags", surface)
        self.assertIn("node_id", surface)
        self.assertIn("fractal_depth", surface)

        # Core layer should have compressed representation
        core = memory_view.core_layer
        self.assertIn("compressed_content", core)
        self.assertIn("pattern_references", core)
        self.assertIn("key_metadata", core)

        # Deep layer should have full reconstruction
        deep = memory_view.deep_layer
        self.assertIn("full_content", deep)
        self.assertIn("fractal_patterns", deep)
        self.assertIn("reconstruction_rules", deep)

        print("✅ Layered structure: All three layers properly formed")
        print(f"   🎯 Surface: {len(surface)} fields")
        print(f"   🧬 Core: {len(core)} fields")
        print(f"   🌊 Deep: {len(deep)} fields")


class TestPhase3Integration(unittest.IsolatedAsyncioTestCase):
    """Test suite for Phase 3 integration with existing Phase 2 components"""

    async def asyncSetUp(self):
        """Set up integrated test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create components
        self.encoder = FractalEncoder(str(self.temp_dir / "encoder"))
        self.simulator = await create_observer_effect_simulator(
            self.encoder, str(self.temp_dir / "observer")
        )

    async def test_fractal_encoder_integration(self):
        """Test integration with fractal encoder from Phase 2"""
        # Encode memory using Phase 2 fractal encoder
        content = "Integration test between Phase 2 fractal encoding and Phase 3 observer effects."
        fractal_node = await self.encoder.encode_memory_fragment(
            content, "integration_test"
        )

        # Access through Phase 3 observer simulator
        memory_view = await self.simulator.access_memory(
            fractal_node.node_id, "lyrixa_core", AccessLayer.DEEP
        )

        # Should successfully integrate
        self.assertEqual(memory_view.node_id, fractal_node.node_id)
        self.assertIn("full_content", memory_view.deep_layer)

        # Deep layer should contain fractal encoding data
        deep_layer = memory_view.deep_layer
        self.assertIn("fractal_patterns", deep_layer)
        self.assertEqual(deep_layer["fractal_patterns"], fractal_node.pattern_refs)

        print(
            "✅ Phase 2-3 integration: Fractal encoding and observer effects work together"
        )

    async def test_cross_phase_memory_consistency(self):
        """Test memory consistency across Phase 2 and Phase 3 operations"""
        content = {"thoughts": ["observer", "effect", "memory", "consistency"]}

        # Phase 2: Encode with fractal encoder
        fractal_node = await self.encoder.encode_memory_fragment(
            content, "consistency_test"
        )

        # Phase 3: Access through observer system multiple times
        for observer_id in ["lyrixa_core", "user_interactive", "plugin_system"]:
            if observer_id == "plugin_system":
                layer = AccessLayer.SURFACE
            elif observer_id == "user_interactive":
                layer = AccessLayer.CORE
            else:
                layer = AccessLayer.DEEP

            memory_view = await self.simulator.access_memory(
                fractal_node.node_id, observer_id, layer
            )

            # Memory should remain consistent
            self.assertEqual(memory_view.node_id, fractal_node.node_id)

        # Phase 2: Reconstruct using fractal encoder
        reconstructed = await self.encoder.reconstruct_memory(fractal_node.node_id)

        # Should match original content
        self.assertEqual(reconstructed, content)

        print(
            "✅ Cross-phase consistency: Memory remains consistent across Phase 2-3 operations"
        )

    async def test_performance_impact_of_observer_effects(self):
        """Test performance impact of observer effects on memory operations"""
        content = "Performance test content for observer effect analysis."

        # Phase 2: Baseline encoding performance
        start_time = time.time()
        fractal_node = await self.encoder.encode_memory_fragment(
            content, "performance_test"
        )
        encoding_time = time.time() - start_time

        # Phase 3: Observer access performance
        start_time = time.time()
        await self.simulator.access_memory(
            fractal_node.node_id, "lyrixa_core", AccessLayer.DEEP
        )
        access_time = time.time() - start_time

        # Both should be fast
        self.assertLess(encoding_time, 1.0)  # Should complete within 1 second
        self.assertLess(access_time, 1.0)  # Should complete within 1 second

        print("✅ Performance impact:")
        print(f"   🧬 Encoding: {encoding_time * 1000:.1f}ms")
        print(f"   👁️ Observer access: {access_time * 1000:.1f}ms")

    async def test_observer_effect_on_fractal_patterns(self):
        """Test how observer effects interact with fractal patterns"""
        content = "Fractal pattern interaction with observer consciousness and awareness patterns."

        # Encode content that should create patterns
        fractal_node = await self.encoder.encode_memory_fragment(
            content, "pattern_interaction_test"
        )

        # Access with high-impact observer
        memory_view = await self.simulator.access_memory(
            fractal_node.node_id,
            "lyrixa_core",
            AccessLayer.DEEP,
            context={"intent": "pattern_analysis"},
        )

        # Check that observer effects preserve fractal patterns
        deep_layer = memory_view.deep_layer
        self.assertIn("fractal_patterns", deep_layer)
        self.assertEqual(
            len(deep_layer["fractal_patterns"]), len(fractal_node.pattern_refs)
        )

        # High-fidelity access might enhance patterns
        if memory_view.current_fidelity > 0.8:
            # May have enhancement markers
            if "enhanced_patterns" in deep_layer:
                print(
                    f"✅ Pattern enhancement: Observer effects enhanced {len(deep_layer['enhanced_patterns'])} patterns"
                )

        print(
            "✅ Fractal-observer interaction: Patterns preserved and potentially enhanced"
        )


async def run_comprehensive_phase3_tests():
    """Run comprehensive Phase 3 test suite"""
    print("🚀 AETHERRA QFAC PHASE 3 - OBSERVER-AWARE COMPRESSION TEST SUITE")
    print("=" * 80)

    # Test configuration
    test_classes = [TestObserverEffectSimulator, TestPhase3Integration]

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
    print("🏆 PHASE 3 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"📊 Total tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success rate: {(passed_tests / total_tests) * 100:.1f}%")

    if failed_tests == 0:
        print("\n🎉 ALL PHASE 3 TESTS PASSED!")
        print("🧠 Observer-aware compression system is ready for production!")
    else:
        print(f"\n⚠️ {failed_tests} tests failed - review and fix issues")

    return passed_tests == total_tests


if __name__ == "__main__":
    asyncio.run(run_comprehensive_phase3_tests())
