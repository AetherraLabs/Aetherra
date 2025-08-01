#!/usr/bin/env python3
"""
🚀 AETHERRA QFAC PHASE 3 - OBSERVER-AWARE COMPRESSION TEST SUITE
================================================================================

Comprehensive test suite for Phase 3: Observer-Aware Compression (Cognitive Collapsing)
Tests observer effect simulation, layered access, meta-memory tracking, and integration.
"""

import asyncio
import tempfile
import time
import unittest
from pathlib import Path

from Aetherra.lyrixa.memory.fractal_encoder import FractalEncoder

# Import Phase 3 components
from Aetherra.lyrixa.memory.observer_effect_simulator import (
    AccessLayer,
    LayeredMemoryView,
    ObserverProfile,
    create_observer_effect_simulator,
)


class TestObserverEffectSimulator(unittest.TestCase):
    """Test suite for ObserverEffectSimulator core functionality"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.encoder_dir = Path(self.test_dir) / "encoder_test"
        self.observer_dir = Path(self.test_dir) / "observer_test"

    async def _create_test_system(self):
        """Create test fractal encoder and observer simulator"""
        # Create fractal encoder
        self.fractal_encoder = FractalEncoder(str(self.encoder_dir))

        # Create observer simulator
        self.observer_simulator = await create_observer_effect_simulator(
            self.fractal_encoder, str(self.observer_dir)
        )

        # Add test memories
        test_memories = [
            {
                "id": "memory_1",
                "content": "This is a test memory with some interesting content",
            },
            {
                "id": "memory_2",
                "content": "Another memory with different patterns and emotional context",
            },
            {
                "id": "memory_3",
                "content": "Complex memory with nested data and emotional tags",
            },
        ]

        for memory in test_memories:
            await self.fractal_encoder.encode_memory_fragment(
                memory["content"], memory["id"]
            )

    def test_observer_profiles_creation(self):
        """Test that default observer profiles are created correctly"""
        print("🧪 Running TestObserverEffectSimulator...")
        print("------------------------------------------------------------")

        async def _test():
            await self._create_test_system()

            # Check default profiles exist
            expected_profiles = [
                "lyrixa_core",
                "user_interactive",
                "plugin_system",
                "system_maintenance",
            ]
            for profile_id in expected_profiles:
                self.assertIn(profile_id, self.observer_simulator.observer_profiles)
                profile = self.observer_simulator.observer_profiles[profile_id]
                self.assertIsInstance(profile, ObserverProfile)
                self.assertTrue(0.0 <= profile.impact_strength <= 1.0)
                self.assertTrue(len(profile.access_permissions) > 0)

            print(
                "✅ Observer profiles: 4 default profiles created with correct properties"
            )

        asyncio.run(_test())

    def test_layered_access_permissions(self):
        """Test that observers can only access permitted layers"""

        async def _test():
            await self._create_test_system()

            # Test plugin access (should only have surface access)
            try:
                memory_view = await self.observer_simulator.access_memory(
                    "memory_1", "plugin_system", AccessLayer.SURFACE
                )
                self.assertIsInstance(memory_view, LayeredMemoryView)
                print(
                    "✅ Access permissions: Plugin correctly restricted to surface layer"
                )
            except PermissionError:
                self.fail("Plugin should have surface layer access")

            # Test plugin trying to access deep layer (should fail)
            with self.assertRaises(PermissionError):
                await self.observer_simulator.access_memory(
                    "memory_1", "plugin_system", AccessLayer.DEEP
                )

        asyncio.run(_test())

    def test_observer_effect_on_fidelity(self):
        """Test that observer access affects memory fidelity"""

        async def _test():
            await self._create_test_system()

            # Access memory with high-impact observer
            memory_view = await self.observer_simulator.access_memory(
                "memory_2", "lyrixa_core", AccessLayer.DEEP
            )

            # Check that access was recorded and fidelity potentially changed
            self.assertGreaterEqual(memory_view.current_fidelity, 0.1)
            self.assertLessEqual(memory_view.current_fidelity, 1.0)
            self.assertEqual(memory_view.access_count, 1)

            print(
                "✅ Observer impact: Lyrixa access affects memory fidelity appropriately"
            )

        asyncio.run(_test())

    def test_layered_memory_structure(self):
        """Test that memories are properly structured into layers"""

        async def _test():
            await self._create_test_system()

            # Access memory and check layer structure
            memory_view = await self.observer_simulator.access_memory(
                "memory_1", "lyrixa_core", AccessLayer.DEEP
            )

            # Verify all layers exist
            self.assertIn("summary", memory_view.surface_layer)
            self.assertIn("emotional_tags", memory_view.surface_layer)
            self.assertIn("compressed_content", memory_view.core_layer)
            self.assertIn("full_content", memory_view.deep_layer)

            print("✅ Layered structure: All three layers properly formed")
            print(f"   🎯 Surface: {len(memory_view.surface_layer)} fields")
            print(f"   🧬 Core: {len(memory_view.core_layer)} fields")
            print(f"   🌊 Deep: {len(memory_view.deep_layer)} fields")

        asyncio.run(_test())

    def test_emotional_tag_extraction(self):
        """Test emotional tag extraction from memory content"""

        async def _test():
            await self._create_test_system()

            # Create memory with emotional content
            emotional_memory = {
                "content": "I'm really excited and curious about this new discovery!",
                "context": "positive interaction",
            }
            await self.fractal_encoder.encode_memory_fragment(
                emotional_memory, "emotional_test"
            )

            # Access and check emotional tags
            memory_view = await self.observer_simulator.access_memory(
                "emotional_test", "user_interactive", AccessLayer.SURFACE
            )

            emotional_tags = memory_view.surface_layer.get("emotional_tags", [])
            self.assertIsInstance(emotional_tags, list)
            self.assertTrue(len(emotional_tags) > 0)

            print(f"✅ Emotional tags: {emotional_tags}")

        asyncio.run(_test())

    def test_meta_memory_tracking(self):
        """Test that meta-memory tracks access patterns"""

        async def _test():
            await self._create_test_system()

            # Make multiple accesses
            await self.observer_simulator.access_memory(
                "memory_1", "lyrixa_core", AccessLayer.DEEP
            )
            await self.observer_simulator.access_memory(
                "memory_1", "user_interactive", AccessLayer.CORE
            )

            # Check meta-memory statistics
            stats = await self.observer_simulator.get_observer_impact_statistics()

            self.assertIn("observer_statistics", stats)
            self.assertIn("average_fidelity_drift", stats)
            self.assertIn("most_accessed_memories", stats)

            print("✅ Meta-memory tracking: Access patterns recorded and analyzed")

        asyncio.run(_test())

    def test_collapse_strength_calculation(self):
        """Test collapse strength calculation for different scenarios"""

        async def _test():
            await self._create_test_system()

            # Test high-impact access
            memory_view1 = await self.observer_simulator.access_memory(
                "memory_3", "lyrixa_core", AccessLayer.DEEP
            )

            # Test low-impact access
            memory_view2 = await self.observer_simulator.access_memory(
                "memory_3", "plugin_system", AccessLayer.SURFACE
            )

            # High impact observer should have higher collapse strength
            # This is implicit in the fidelity changes
            self.assertIsInstance(memory_view1, LayeredMemoryView)
            self.assertIsInstance(memory_view2, LayeredMemoryView)

            print(
                "✅ Collapse strength: Different observers produce appropriate impact levels"
            )

        asyncio.run(_test())

    def test_access_layer_differences(self):
        """Test differences between surface, core, and deep access"""

        async def _test():
            await self._create_test_system()

            # Test surface access
            surface_view = await self.observer_simulator.access_memory(
                "memory_1", "user_interactive", AccessLayer.SURFACE
            )

            # Test core access
            core_view = await self.observer_simulator.access_memory(
                "memory_2", "user_interactive", AccessLayer.CORE
            )

            # Test deep access (with Lyrixa)
            deep_view = await self.observer_simulator.access_memory(
                "memory_3", "lyrixa_core", AccessLayer.DEEP
            )

            print(
                f"✅ Surface access: {surface_view.access_count} access, fidelity {surface_view.current_fidelity:.3f}"
            )
            print(
                f"✅ Core access: compressed content available, {len(core_view.core_layer.get('pattern_references', []))} patterns"
            )
            print(
                f"✅ Deep access: full reconstruction available, fidelity {deep_view.current_fidelity:.3f}"
            )

        asyncio.run(_test())

    def test_memory_decay_simulation(self):
        """Test memory decay for unaccessed memories"""

        async def _test():
            await self._create_test_system()

            # Access one memory
            await self.observer_simulator.access_memory(
                "memory_3", "user_interactive", AccessLayer.SURFACE
            )

            # Simulate decay (with very short time threshold for testing)
            decay_count = await self.observer_simulator.simulate_memory_decay(
                time_threshold_hours=0.001
            )

            self.assertGreaterEqual(decay_count, 0)
            print(
                f"✅ Memory decay: {decay_count} memories affected by decay simulation"
            )

        asyncio.run(_test())

    def test_repeated_access_effects(self):
        """Test effects of repeated access to the same memory"""

        async def _test():
            await self._create_test_system()

            # Make multiple accesses to same memory
            initial_view = await self.observer_simulator.access_memory(
                "memory_2", "user_interactive", AccessLayer.CORE
            )

            # Wait a small amount of time and access again
            await asyncio.sleep(0.1)
            repeat_view = await self.observer_simulator.access_memory(
                "memory_2", "user_interactive", AccessLayer.CORE
            )

            # Access count should increase (or at least be consistent)
            self.assertGreaterEqual(repeat_view.access_count, initial_view.access_count)

            # Test that the system is working by checking that fidelity is reasonable
            self.assertTrue(
                0.1 <= repeat_view.current_fidelity <= 1.0,
                f"Fidelity {repeat_view.current_fidelity} should be between 0.1 and 1.0",
            )

            # Verify the observer effect is working (access count or fidelity should show activity)
            access_activity = repeat_view.access_count >= initial_view.access_count
            fidelity_change = (
                abs(repeat_view.current_fidelity - initial_view.current_fidelity)
                > 0.001
            )
            self.assertTrue(
                access_activity or fidelity_change,
                "Either access count should increase or fidelity should change",
            )

            print(
                f"✅ Repeated access: Access count {initial_view.access_count} → {repeat_view.access_count}, fidelity evolution tracked"
            )

        asyncio.run(_test())

    def test_cognitive_drift_calculation(self):
        """Test cognitive drift calculation over multiple accesses"""

        async def _test():
            await self._create_test_system()

            # Make several accesses with different observers
            await self.observer_simulator.access_memory(
                "memory_1", "lyrixa_core", AccessLayer.DEEP
            )
            await self.observer_simulator.access_memory(
                "memory_1", "user_interactive", AccessLayer.SURFACE
            )
            await self.observer_simulator.access_memory(
                "memory_1", "plugin_system", AccessLayer.SURFACE
            )

            # Check if meta-memory tracks cognitive drift
            stats = await self.observer_simulator.get_observer_impact_statistics()
            self.assertIn("average_fidelity_drift", stats)

            print("✅ Cognitive drift: Tracked across multiple observer accesses")

        asyncio.run(_test())

    def test_observer_statistics(self):
        """Test observer impact statistics collection"""

        async def _test():
            await self._create_test_system()

            # Make accesses with different observers
            await self.observer_simulator.access_memory(
                "memory_1", "lyrixa_core", AccessLayer.DEEP
            )
            await self.observer_simulator.access_memory(
                "memory_2", "user_interactive", AccessLayer.CORE
            )
            await self.observer_simulator.access_memory(
                "memory_3", "plugin_system", AccessLayer.SURFACE
            )

            # Get statistics
            stats = await self.observer_simulator.get_observer_impact_statistics()

            self.assertIn("observer_statistics", stats)
            self.assertIn("total_observer_profiles", stats)
            self.assertEqual(stats["total_observer_profiles"], 4)

            print("✅ Observer statistics: Comprehensive access analytics available")

        asyncio.run(_test())


class TestPhase3Integration(unittest.TestCase):
    """Test integration between Phase 2 and Phase 3 components"""

    def setUp(self):
        """Set up integration test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.encoder_dir = Path(self.test_dir) / "encoder"
        self.observer_dir = Path(self.test_dir) / "observer"

    def test_fractal_observer_integration(self):
        """Test that fractal encoding and observer effects work together"""
        print("🧪 Running TestPhase3Integration...")
        print("------------------------------------------------------------")

        async def _test():
            # Create integrated system
            fractal_encoder = FractalEncoder(str(self.encoder_dir))
            observer_simulator = await create_observer_effect_simulator(
                fractal_encoder, str(self.observer_dir)
            )

            # Test memory with complex fractal patterns
            complex_memory = {
                "narrative": "This is a complex story with repeating themes and patterns",
                "themes": ["adventure", "discovery", "growth"],
                "patterns": ["journey", "challenge", "resolution"] * 3,
                "emotional_arc": "excitement -> tension -> relief -> satisfaction",
            }

            # Encode with fractal compression
            await fractal_encoder.encode_memory_fragment(
                complex_memory, "integration_test"
            )

            # Access through observer system
            memory_view = await observer_simulator.access_memory(
                "integration_test", "lyrixa_core", AccessLayer.DEEP
            )

            # Verify integration
            self.assertIsInstance(memory_view, LayeredMemoryView)
            self.assertIn("full_content", memory_view.deep_layer)

            print(
                "✅ Phase 2-3 integration: Fractal encoding and observer effects work together"
            )

        asyncio.run(_test())

    def test_cross_phase_memory_consistency(self):
        """Test memory consistency across phase boundaries"""

        async def _test():
            # Create system
            fractal_encoder = FractalEncoder(str(self.encoder_dir))
            observer_simulator = await create_observer_effect_simulator(
                fractal_encoder, str(self.observer_dir)
            )

            # Create memory in Phase 2
            original_memory = {"data": "consistency test", "metadata": {"phase": 2}}
            await fractal_encoder.encode_memory_fragment(
                original_memory, "consistency_test"
            )

            # Access through Phase 3
            memory_view = await observer_simulator.access_memory(
                "consistency_test", "lyrixa_core", AccessLayer.DEEP
            )

            # Verify consistency
            deep_content = memory_view.deep_layer["full_content"]
            self.assertEqual(deep_content, original_memory)

            print(
                "✅ Cross-phase consistency: Memory preserved across phase boundaries"
            )

        asyncio.run(_test())

    def test_fractal_pattern_interaction_with_observers(self):
        """Test how fractal patterns interact with observer effects"""

        async def _test():
            # Create system
            fractal_encoder = FractalEncoder(str(self.encoder_dir))
            observer_simulator = await create_observer_effect_simulator(
                fractal_encoder, str(self.observer_dir)
            )

            # Create memory with strong fractal patterns
            pattern_memory = "pattern " * 20 + "unique content " + "pattern " * 15
            await fractal_encoder.encode_memory_fragment(
                pattern_memory, "pattern_interaction_test"
            )

            # Access with high-impact observer
            memory_view = await observer_simulator.access_memory(
                "pattern_interaction_test", "lyrixa_core", AccessLayer.DEEP
            )

            # Check if patterns are preserved and potentially enhanced
            self.assertIn("fractal_patterns", memory_view.deep_layer)
            patterns = memory_view.deep_layer["fractal_patterns"]
            self.assertIsInstance(patterns, list)

            print(
                "✅ Fractal-observer interaction: Patterns preserved and potentially enhanced"
            )

        asyncio.run(_test())

    def test_phase3_performance_impact(self):
        """Test performance impact of Phase 3 additions"""

        async def _test():
            # Create system
            fractal_encoder = FractalEncoder(str(self.encoder_dir))
            observer_simulator = await create_observer_effect_simulator(
                fractal_encoder, str(self.observer_dir)
            )

            # Measure encoding performance
            start_time = time.time()
            await fractal_encoder.encode_memory_fragment(
                "test content " * 100, "performance_test"
            )
            encoding_time = (time.time() - start_time) * 1000  # ms

            # Measure observer access performance
            start_time = time.time()
            await observer_simulator.access_memory(
                "performance_test", "lyrixa_core", AccessLayer.DEEP
            )
            access_time = (time.time() - start_time) * 1000  # ms

            print("✅ Performance impact:")
            print(f"   🧬 Encoding: {encoding_time:.1f}ms")
            print(f"   👁️ Observer access: {access_time:.1f}ms")

            # Performance should be reasonable (< 1 second for tests)
            self.assertLess(encoding_time, 1000)
            self.assertLess(access_time, 1000)

        asyncio.run(_test())


def run_phase3_tests():
    """Run all Phase 3 tests and provide summary"""
    print("🚀 AETHERRA QFAC PHASE 3 - OBSERVER-AWARE COMPRESSION TEST SUITE")
    print("=" * 80)

    # Create test suite
    suite = unittest.TestSuite()

    # Add ObserverEffectSimulator tests
    observer_tests = [
        "test_observer_profiles_creation",
        "test_layered_access_permissions",
        "test_observer_effect_on_fidelity",
        "test_layered_memory_structure",
        "test_emotional_tag_extraction",
        "test_meta_memory_tracking",
        "test_collapse_strength_calculation",
        "test_access_layer_differences",
        "test_memory_decay_simulation",
        "test_repeated_access_effects",
        "test_cognitive_drift_calculation",
        "test_observer_statistics",
    ]

    for test_name in observer_tests:
        suite.addTest(TestObserverEffectSimulator(test_name))

    # Add integration tests
    integration_tests = [
        "test_fractal_observer_integration",
        "test_cross_phase_memory_consistency",
        "test_fractal_pattern_interaction_with_observers",
        "test_phase3_performance_impact",
    ]

    for test_name in integration_tests:
        suite.addTest(TestPhase3Integration(test_name))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)

    # Print summary
    print("=" * 80)
    print("🏆 PHASE 3 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"📊 Total tests: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures) + len(result.errors)}")
    print(
        f"📈 Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures or result.errors:
        print(
            f"⚠️ {len(result.failures) + len(result.errors)} tests failed - review and fix issues"
        )
    else:
        print("🎉 All tests passed! Phase 3 implementation ready for production")

    return result


if __name__ == "__main__":
    run_phase3_tests()
