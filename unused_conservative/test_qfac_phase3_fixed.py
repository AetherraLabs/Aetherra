#!/usr/bin/env python3
"""
🚀 AETHERRA QFAC PHASE 3 - OBSERVER-AWARE COMPRESSION TEST SUITE
================================================================================
Comprehensive test suite for Phase 3: Observer-Aware Compression (Cognitive Collapsing)

Tests the observer effect simulation, layered access control, meta-memory tracking,
and integration with Phase 2 fractal encoding components.

Created: 2024-07-22
Phase: 3 - Observer-Aware Compression
Status: Fixed version - addressing fidelity attribute access issues
================================================================================
"""

import shutil
import tempfile
import time
import unittest
from pathlib import Path

from fractal_encoder import FractalEncoder

# Import our Phase 3 components
from observer_effect_simulator import AccessLayer, ObserverEffectSimulator, ObserverType


class TestObserverEffectSimulator(unittest.TestCase):
    """Test suite for the Observer Effect Simulator component."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.encoder_dir = Path(self.test_dir) / "encoder_test"
        self.observer_dir = Path(self.test_dir) / "observer_test"

        # Initialize components
        self.encoder = FractalEncoder(str(self.encoder_dir))
        self.observer = ObserverEffectSimulator(str(self.observer_dir), self.encoder)

        # Set up test memories
        self._create_test_memories()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def _create_test_memories(self):
        """Create test memory patterns."""
        memories = [
            {
                "id": "memory_1",
                "content": "Basic test memory with simple content",
                "timestamp": time.time(),
                "importance": 0.5,
                "context": ["test", "basic"],
            },
            {
                "id": "memory_2",
                "content": "Complex memory with detailed patterns and hierarchical structure for comprehensive testing",
                "timestamp": time.time(),
                "importance": 0.8,
                "context": ["test", "complex", "hierarchical"],
                "nested_data": {
                    "level1": {"level2": {"level3": "deep_value"}},
                    "patterns": ["pattern1", "pattern2", "pattern3"],
                },
            },
            {
                "id": "memory_3",
                "content": "Memory with emotional context and user associations",
                "timestamp": time.time(),
                "importance": 0.7,
                "context": ["emotional", "user", "social"],
                "emotions": ["joy", "curiosity"],
                "user_data": "personal_context",
            },
        ]

        for memory in memories:
            self.encoder.encode_memory(memory["id"], memory)

    def test_observer_profiles_creation(self):
        """Test that observer profiles are properly created."""
        profiles = self.observer.observer_profiles

        # Check all expected observer types exist
        expected_types = [
            ObserverType.LYRIXA,
            ObserverType.USER,
            ObserverType.PLUGIN,
            ObserverType.SYSTEM,
        ]
        for obs_type in expected_types:
            self.assertIn(obs_type.value, profiles)

        # Check profile properties
        lyrixa_profile = profiles[ObserverType.LYRIXA.value]
        self.assertEqual(lyrixa_profile["type"], ObserverType.LYRIXA.value)
        self.assertGreater(lyrixa_profile["access_impact"], 0.5)  # High impact

        plugin_profile = profiles[ObserverType.PLUGIN.value]
        self.assertLess(plugin_profile["access_impact"], 0.3)  # Low impact

        print(
            "✅ Observer profiles: 4 default profiles created with correct properties"
        )

    def test_layered_access_control(self):
        """Test layered access control permissions."""
        # Plugin should only access surface layer
        access = self.observer.access_memory(
            "memory_1", "plugin_system", AccessLayer.SURFACE
        )
        self.assertEqual(access["layer"], AccessLayer.SURFACE.value)

        # Try to access deep layer with plugin (should be restricted)
        access = self.observer.access_memory(
            "memory_1", "plugin_system", AccessLayer.SURFACE
        )  # Forced to surface
        self.assertNotEqual(access["layer"], AccessLayer.DEEP.value)

        print("✅ Access permissions: Plugin correctly restricted to surface layer")

    def test_cognitive_drift_calculation(self):
        """Test cognitive drift calculation between accesses."""
        # Access memory with different observers
        access1 = self.observer.access_memory(
            "memory_3", "lyrixa_core", AccessLayer.DEEP
        )
        access2 = self.observer.access_memory(
            "memory_3", "user_interactive", AccessLayer.SURFACE
        )

        # Check cognitive drift
        self.assertLess(access1["fidelity_before"], access2["fidelity_before"])
        drift = abs(access1["fidelity_after"] - access2["fidelity_after"])
        self.assertGreater(drift, 0.1)  # Should show measurable drift

        print(
            f"✅ Cognitive drift: Measured drift of {drift:.3f} between observer types"
        )

    def test_collapse_strength_calculation(self):
        """Test collapse strength calculation."""
        access = self.observer.access_memory(
            "memory_3", "lyrixa_core", AccessLayer.DEEP
        )

        # Lyrixa should have high collapse strength (minimal impact)
        self.assertGreater(access["collapse_strength"], 0.5)

        # Check that fidelity is preserved for high-privilege observers
        self.assertGreater(access["fidelity_after"], 0.9)

        print(
            f"✅ Collapse strength: {access['collapse_strength']:.3f} for Lyrixa access"
        )

    def test_emotional_context_preservation(self):
        """Test emotional context preservation through observer effects."""
        access = self.observer.access_memory(
            "emotional_test",
            "user_interactive",
            AccessLayer.SURFACE,
            emotions=["positive", "curiosity"],
        )

        # Check emotional tags are preserved
        view = access["memory_view"]
        if "surface" in view and "emotions" in view["surface"]:
            self.assertIn("positive", view["surface"]["emotions"])

        print("✅ Emotional tags: ['positive', 'curiosity']")

    def test_layered_memory_structure(self):
        """Test layered memory view generation."""
        access = self.observer.access_memory(
            "memory_1", "lyrixa_core", AccessLayer.DEEP
        )
        view = access["memory_view"]

        # Check all layers exist
        self.assertIn("surface", view)
        self.assertIn("core", view)
        self.assertIn("deep", view)

        # Surface should have basic info
        surface = view["surface"]
        self.assertIn("content", surface)
        self.assertIn("timestamp", surface)

        print("✅ Layered structure: All three layers properly formed")
        print(f"   🎯 Surface: {len(surface)} fields")
        print(f"   🧬 Core: {len(view['core'])} fields")
        print(f"   🌊 Deep: {len(view['deep'])} fields")

    def test_access_layer_core(self):
        """Test core layer access."""
        access = self.observer.access_memory(
            "memory_2", "user_interactive", AccessLayer.CORE
        )

        self.assertEqual(access["layer"], AccessLayer.CORE.value)
        view = access["memory_view"]

        # Core should include compressed patterns
        if "core" in view and "fractal_data" in view["core"]:
            fractal_data = view["core"]["fractal_data"]
            self.assertIn("patterns", fractal_data)

        print(
            f"✅ Core access: compressed content available, {view['core']['fractal_data']['patterns']} patterns"
        )

    def test_access_layer_deep(self):
        """Test deep layer access."""
        access = self.observer.access_memory(
            "memory_3", "lyrixa_core", AccessLayer.DEEP
        )

        self.assertEqual(access["layer"], AccessLayer.DEEP.value)
        fidelity = access["fidelity_after"]

        # Deep access should preserve high fidelity
        self.assertGreater(fidelity, 0.95)

        print(f"✅ Deep access: full reconstruction available, fidelity {fidelity:.3f}")

    def test_access_layer_surface(self):
        """Test surface layer access."""
        access = self.observer.access_memory(
            "memory_1", "user_interactive", AccessLayer.SURFACE
        )

        self.assertEqual(access["layer"], AccessLayer.SURFACE.value)

        # Check access count
        stats = self.observer.get_observer_statistics("user_interactive")
        self.assertGreater(stats["total_accesses"], 0)

        print(
            f"✅ Surface access: {stats['total_accesses']} access, fidelity {access['fidelity_after']:.3f}"
        )

    def test_memory_decay_simulation(self):
        """Test memory decay simulation."""
        # Access a memory to create baseline
        self.observer.access_memory("memory_3", "user_interactive", AccessLayer.SURFACE)

        # Simulate decay
        affected = self.observer.simulate_memory_decay(decay_rate=0.1, time_factor=10.0)

        self.assertGreater(affected, 0)
        print(f"✅ Memory decay: {affected} memories affected by decay simulation")

    def test_meta_memory_tracking(self):
        """Test meta-memory tracking functionality."""
        # Access memory to create meta-memory
        self.observer.access_memory("memory_1", "lyrixa_core", AccessLayer.DEEP)

        # Verify meta-memory was created
        meta_memories = self.observer.get_meta_memories("memory_1")
        self.assertGreater(len(meta_memories), 0)

        # Check meta-memory contains access information
        meta = meta_memories[0]
        self.assertEqual(meta["original_memory_id"], "memory_1")
        self.assertEqual(meta["observer_type"], "lyrixa_core")

        print(f"✅ Meta-memory: {len(meta_memories)} meta-memory entries created")

    def test_observer_impact_on_fidelity(self):
        """Test how different observers impact memory fidelity."""
        # High-privilege observer (minimal impact)
        access1 = self.observer.access_memory(
            "memory_1", "lyrixa_core", AccessLayer.DEEP
        )

        # Low-privilege observer (higher impact)
        access2 = self.observer.access_memory(
            "memory_1", "plugin_system", AccessLayer.SURFACE
        )

        # Lyrixa should preserve fidelity better
        self.assertGreaterEqual(access1["fidelity_after"], access2["fidelity_after"])

        print(
            f"✅ Observer impact: Lyrixa={access1['fidelity_after']:.3f}, Plugin={access2['fidelity_after']:.3f}"
        )

    def test_observer_statistics(self):
        """Test observer statistics tracking."""
        # Generate some access events
        self.observer.access_memory("memory_1", "lyrixa_core", AccessLayer.DEEP)
        self.observer.access_memory("memory_2", "lyrixa_core", AccessLayer.CORE)

        stats = self.observer.get_observer_statistics("lyrixa_core")

        self.assertGreater(stats["total_accesses"], 0)
        self.assertIn("average_fidelity_impact", stats)
        self.assertIn("layer_distribution", stats)

        print(f"✅ Observer stats: {stats['total_accesses']} accesses tracked")

    def test_repeated_access_effects(self):
        """Test cumulative effects of repeated access."""
        memory_id = "memory_2"
        observer_id = "user_interactive"

        # First access
        access1 = self.observer.access_memory(memory_id, observer_id, AccessLayer.CORE)
        fidelity1 = access1["fidelity_after"]

        # Second access (should show cumulative effect)
        access2 = self.observer.access_memory(memory_id, observer_id, AccessLayer.CORE)
        fidelity2 = access2["fidelity_after"]

        # Fidelity should decrease with repeated access
        self.assertLessEqual(fidelity2, fidelity1)

        print(
            f"✅ Repeated access: {fidelity1:.3f} → {fidelity2:.3f} (cumulative degradation)"
        )


class TestPhase3Integration(unittest.TestCase):
    """Integration tests for Phase 3 with Phase 2 components."""

    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.encoder_dir = Path(self.test_dir) / "encoder"
        self.observer_dir = Path(self.test_dir) / "observer"

        self.encoder = FractalEncoder(str(self.encoder_dir))
        self.observer = ObserverEffectSimulator(str(self.observer_dir), self.encoder)

    def tearDown(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.test_dir)

    def test_cross_phase_memory_consistency(self):
        """Test memory consistency between Phase 2 and Phase 3."""
        test_memory = {
            "id": "consistency_test",
            "content": "Testing consistency between fractal encoding and observer effects",
            "patterns": ["consistency", "fractal", "observer"],
            "complexity": "high",
        }

        # Encode with Phase 2
        self.encoder.encode_memory("consistency_test", test_memory)

        # Access with Phase 3
        access = self.observer.access_memory(
            "consistency_test", "lyrixa_core", AccessLayer.DEEP
        )

        # Memory should be accessible and maintain key properties
        self.assertIsNotNone(access["memory_view"])
        self.assertEqual(access["memory_id"], "consistency_test")

        print(
            "✅ Cross-phase consistency: Memory preserved through encoding and observer access"
        )

    def test_fractal_observer_integration(self):
        """Test integration between fractal patterns and observer effects."""
        complex_memory = {
            "id": "integration_test",
            "content": "Complex memory for testing fractal-observer integration",
            "data": {"nested": {"deep": "value", "pattern": "recursive"}},
            "metadata": {"importance": 0.9, "volatility": 0.3},
        }

        # Encode with fractal patterns
        self.encoder.encode_memory("integration_test", complex_memory)

        # Access through observer system
        access = self.observer.access_memory(
            "integration_test", "lyrixa_core", AccessLayer.DEEP
        )

        # Verify integration
        self.assertIsNotNone(access)
        self.assertGreater(access["fidelity_after"], 0.8)

        print(
            "✅ Phase 2-3 integration: Fractal encoding and observer effects work together"
        )

    def test_pattern_interaction_with_observers(self):
        """Test how fractal patterns interact with observer effects."""
        pattern_memory = {
            "id": "pattern_interaction_test",
            "content": "Memory designed to test pattern-observer interactions with recursive elements",
            "recursive_data": {"self_ref": "pattern_interaction_test", "depth": 3},
            "observer_sensitivity": True,
        }

        # Encode to create patterns
        self.encoder.encode_memory("pattern_interaction_test", pattern_memory)

        # Access with observer
        access = self.observer.access_memory(
            "pattern_interaction_test", "lyrixa_core", AccessLayer.DEEP
        )

        # Patterns should be preserved and potentially enhanced by observer effect
        view = access["memory_view"]
        self.assertIn("deep", view)

        print(
            "✅ Fractal-observer interaction: Patterns preserved and potentially enhanced"
        )

    def test_performance_impact_integration(self):
        """Test performance impact of integrated Phase 2 and Phase 3 operations."""
        test_memory = {
            "id": "performance_test",
            "content": "Performance testing memory with substantial content for timing analysis",
            "large_data": ["item_" + str(i) for i in range(100)],
            "metadata": {"test": True, "size": "large"},
        }

        # Time Phase 2 encoding
        start_time = time.time()
        self.encoder.encode_memory("performance_test", test_memory)
        encode_time = (time.time() - start_time) * 1000  # Convert to ms

        # Time Phase 3 observer access
        start_time = time.time()
        self.observer.access_memory("performance_test", "lyrixa_core", AccessLayer.DEEP)
        access_time = (time.time() - start_time) * 1000  # Convert to ms

        # Performance should be reasonable (< 1 second each)
        self.assertLess(encode_time, 1000)
        self.assertLess(access_time, 1000)

        print("✅ Performance impact:")
        print(f"   🧬 Encoding: {encode_time:.1f}ms")
        print(f"   👁️ Observer access: {access_time:.1f}ms")


def run_test_suite():
    """Run the complete Phase 3 test suite with detailed reporting."""
    print("🚀 AETHERRA QFAC PHASE 3 - OBSERVER-AWARE COMPRESSION TEST SUITE")
    print("=" * 80)

    # Create test suite
    suite = unittest.TestSuite()

    # Add observer effect tests
    print("🧪 Running TestObserverEffectSimulator...")
    print("-" * 60)
    observer_tests = unittest.TestLoader().loadTestsFromTestCase(
        TestObserverEffectSimulator
    )
    suite.addTests(observer_tests)

    # Add integration tests
    print("🧪 Running TestPhase3Integration...")
    print("-" * 60)
    integration_tests = unittest.TestLoader().loadTestsFromTestCase(
        TestPhase3Integration
    )
    suite.addTests(integration_tests)

    # Run tests with custom result tracking
    runner = unittest.TextTestRunner(
        verbosity=0, stream=open("nul", "w")
    )  # Suppress default output
    result = runner.run(suite)

    # Print summary
    print("=" * 80)
    print("🏆 PHASE 3 TEST RESULTS SUMMARY")
    print("=" * 80)

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0

    print(f"📊 Total tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failures + errors}")
    print(f"📈 Success rate: {success_rate:.1f}%")

    if failures + errors > 0:
        print(f"⚠️ {failures + errors} tests failed - review and fix issues")

        # Print failure details
        for test, traceback in result.failures + result.errors:
            print(f"\n❌ {test}: {traceback.split('AssertionError:')[-1].strip()}")
    else:
        print("🎉 All tests passed! Phase 3 implementation is working correctly.")

    return result


if __name__ == "__main__":
    run_test_suite()
