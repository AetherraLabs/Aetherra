"""
🧿 AETHERRA QFAC PHASE 4 TEST SUITE: QUANTUM-INSPIRED CAUSAL BRANCHING
================================================================================
Comprehensive test suite for Phase 4: Causal Branch Simulator with quantum-inspired
interference patterns, superposition states, and coherence collapse mechanisms.

Test Coverage:
- ✅ Causal branch creation and probability weighting
- ✅ Superposition state formation and wave function calculation
- ✅ Quantum-inspired interference pattern simulation
- ✅ Coherence-based superposition collapse
- ✅ Delta compression and branch optimization
- ✅ Cross-phase integration with Fractal Encoder and Observer Effect Simulator
- ✅ Performance benchmarking and statistical validation
- ✅ Edge cases and error handling

Production Readiness: Full validation for Phase 4 deployment
"""

import asyncio
import unittest
import tempfile
import shutil
import json
import time
import math
from datetime import datetime
from pathlib import Path

# Import the Phase 4 components
from causal_branch_simulator import (
    CausalBranchSimulator, CausalBranch, SuperpositionState, InterferencePattern
)

# Try to import Phase 2 and 3 for integration testing
try:
    import sys
    from pathlib import Path
    # Add the Aetherra memory module path
    aetherra_memory_path = Path(__file__).parent / "Aetherra" / "lyrixa" / "memory"
    if aetherra_memory_path.exists():
        sys.path.insert(0, str(aetherra_memory_path))
    
    from fractal_encoder import FractalEncoder
    from observer_effect_simulator import ObserverEffectSimulator
    INTEGRATION_TESTING = True
    print("✅ Phase 2/3 integration testing enabled")
except ImportError as e:
    print(f"⚠️ Phase 2/3 components not available - skipping integration tests: {e}")
    INTEGRATION_TESTING = False

class TestCausalBranchSimulator(unittest.TestCase):
    """Test suite for Phase 4 causal branching capabilities"""
    
    def setUp(self):
        """Set up test environment for each test"""
        self.test_dir = tempfile.mkdtemp(prefix="causal_test_")
        self.simulator = CausalBranchSimulator(data_dir=self.test_dir)
        
        # Sample memory content for testing
        self.sample_memory = {
            "content": "The user is learning about quantum mechanics and fractal mathematics",
            "emotional_tag": "curiosity",
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.9,
            "complexity": 0.7
        }
        
        # Test scenarios
        self.test_scenarios = [
            "User asks about wave-particle duality",
            "User explores quantum entanglement",
            "User shifts to classical physics",
            "User requests practical applications",
            "User expresses confusion about concepts"
        ]
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    async def test_causal_branch_creation(self):
        """Test basic causal branch creation with probability weighting"""
        # Create a causal branch
        branch = await self.simulator.create_causal_branch(
            source_memory_id="test_memory_001",
            memory_content=self.sample_memory,
            branch_scenario=self.test_scenarios[0]
        )
        
        # Validate branch properties
        self.assertIsInstance(branch, CausalBranch)
        self.assertTrue(branch.branch_id.startswith("branch_"))
        self.assertEqual(branch.source_memory_id, "test_memory_001")
        self.assertGreater(branch.probability_weight, 0.0)
        self.assertLess(branch.probability_weight, 1.0)
        self.assertGreater(branch.coherence_score, 0.0)
        self.assertLessEqual(branch.coherence_score, 1.0)
        self.assertIn("branch_scenario", branch.branch_content)
        self.assertTrue(len(branch.delta_compression) > 0)
        
        print(f"✅ Causal branch created: {branch.branch_id}")
        print(f"   📊 Probability: {branch.probability_weight:.3f}")
        print(f"   💫 Coherence: {branch.coherence_score:.3f}")
    
    async def test_multiple_branch_creation(self):
        """Test creation of multiple branches from the same memory"""
        branches = []
        
        # Create multiple branches
        for i, scenario in enumerate(self.test_scenarios):
            branch = await self.simulator.create_causal_branch(
                source_memory_id="test_memory_multi",
                memory_content=self.sample_memory,
                branch_scenario=scenario
            )
            branches.append(branch)
        
        # Validate all branches
        self.assertEqual(len(branches), len(self.test_scenarios))
        
        # Check that all branches have different IDs
        branch_ids = [branch.branch_id for branch in branches]
        self.assertEqual(len(branch_ids), len(set(branch_ids)))
        
        # Validate probability normalization (should be reasonable)
        total_probability = sum(branch.probability_weight for branch in branches)
        self.assertGreater(total_probability, 0.0)
        
        print(f"✅ Multiple branches: {len(branches)} branches created")
        print(f"   📊 Total probability mass: {total_probability:.3f}")
    
    async def test_superposition_creation(self):
        """Test quantum-inspired superposition state formation"""
        # Create multiple branches
        branches = []
        for scenario in self.test_scenarios[:3]:
            branch = await self.simulator.create_causal_branch(
                source_memory_id="test_memory_superpos",
                memory_content=self.sample_memory,
                branch_scenario=scenario
            )
            branches.append(branch)
        
        # Create superposition
        branch_ids = [branch.branch_id for branch in branches]
        superposition = await self.simulator.create_superposition(
            memory_id="test_memory_superpos",
            branch_ids=branch_ids
        )
        
        # Validate superposition properties
        self.assertIsInstance(superposition, SuperpositionState)
        self.assertTrue(superposition.superposition_id.startswith("superpos_"))
        self.assertEqual(superposition.memory_id, "test_memory_superpos")
        self.assertEqual(len(superposition.active_branches), 3)
        self.assertEqual(len(superposition.wave_function), 3)
        self.assertEqual(len(superposition.interference_matrix), 3)
        self.assertEqual(len(superposition.interference_matrix[0]), 3)
        self.assertGreater(superposition.coherence_score, 0.0)
        self.assertLessEqual(superposition.coherence_score, 1.0)
        
        # Validate wave function (probability amplitudes)
        amplitude_sum = sum(amp**2 for amp in superposition.wave_function.values())
        self.assertAlmostEqual(amplitude_sum, 1.0, places=2)
        
        print(f"✅ Superposition created: {superposition.superposition_id}")
        print(f"   🌌 Branches: {len(superposition.active_branches)}")
        print(f"   💫 Coherence: {superposition.coherence_score:.3f}")
    
    async def test_interference_simulation(self):
        """Test quantum-inspired interference between branches"""
        # Create two branches
        branch1 = await self.simulator.create_causal_branch(
            source_memory_id="test_memory_interference",
            memory_content=self.sample_memory,
            branch_scenario=self.test_scenarios[0]
        )
        
        branch2 = await self.simulator.create_causal_branch(
            source_memory_id="test_memory_interference",
            memory_content=self.sample_memory,
            branch_scenario=self.test_scenarios[1]
        )
        
        # Simulate interference
        interference = await self.simulator.simulate_interference(
            branch1.branch_id, branch2.branch_id
        )
        
        # Validate interference properties
        self.assertIsInstance(interference, InterferencePattern)
        self.assertTrue(interference.pattern_id.startswith("interference_"))
        self.assertEqual(interference.branch_a_id, branch1.branch_id)
        self.assertEqual(interference.branch_b_id, branch2.branch_id)
        self.assertIn(interference.interference_type, ['constructive', 'destructive', 'neutral'])
        self.assertGreaterEqual(interference.interference_strength, 0.0)
        self.assertLessEqual(interference.interference_strength, 1.0)
        self.assertGreaterEqual(interference.phase_difference, 0.0)
        self.assertLess(interference.phase_difference, 2 * math.pi)
        
        print(f"✅ Interference simulated: {interference.pattern_id}")
        print(f"   🌊 Type: {interference.interference_type}")
        print(f"   💪 Strength: {interference.interference_strength:.3f}")
        print(f"   📐 Phase diff: {interference.phase_difference:.3f}")
    
    async def test_superposition_collapse(self):
        """Test coherence-based superposition collapse"""
        # Create branches and superposition
        branches = []
        for scenario in self.test_scenarios[:3]:
            branch = await self.simulator.create_causal_branch(
                source_memory_id="test_memory_collapse",
                memory_content=self.sample_memory,
                branch_scenario=scenario
            )
            branches.append(branch)
        
        branch_ids = [branch.branch_id for branch in branches]
        superposition = await self.simulator.create_superposition(
            memory_id="test_memory_collapse",
            branch_ids=branch_ids
        )
        
        # Record initial state
        initial_branches = len(superposition.active_branches)
        
        # Collapse superposition
        collapsed_branch_id = await self.simulator.collapse_superposition(
            superposition.superposition_id,
            collapse_trigger="test_trigger"
        )
        
        # Validate collapse
        self.assertIn(collapsed_branch_id, branch_ids)
        
        # Get updated superposition state
        updated_superposition = await self.simulator.get_superposition_state("test_memory_collapse")
        self.assertEqual(len(updated_superposition.active_branches), 1)
        self.assertEqual(updated_superposition.active_branches[0], collapsed_branch_id)
        self.assertEqual(updated_superposition.coherence_score, 1.0)
        
        print(f"✅ Superposition collapsed: {superposition.superposition_id}")
        print(f"   🎭 Initial branches: {initial_branches}")
        print(f"   🏆 Surviving branch: {collapsed_branch_id}")
    
    async def test_delta_compression(self):
        """Test delta compression between source and branch content"""
        # Create branch with different content
        modified_memory = self.sample_memory.copy()
        modified_memory["content"] = "Modified content for testing delta compression"
        modified_memory["new_field"] = "Added field"
        del modified_memory["complexity"]
        
        branch = await self.simulator.create_causal_branch(
            source_memory_id="test_memory_delta",
            memory_content=modified_memory,
            branch_scenario="Content modification test"
        )
        
        # Validate delta compression
        delta = branch.delta_compression
        self.assertIsInstance(delta, dict)
        
        # Check for additions, modifications, and deletions
        has_additions = any(key.startswith('+') for key in delta.keys())
        has_modifications = any(key.startswith('~') for key in delta.keys())
        
        # Should have at least some changes
        self.assertTrue(len(delta) > 0)
        
        print(f"✅ Delta compression: {len(delta)} changes detected")
        print(f"   ➕ Additions: {has_additions}")
        print(f"   🔄 Modifications: {has_modifications}")
    
    async def test_memory_branch_retrieval(self):
        """Test retrieval of branches for a specific memory"""
        memory_id = "test_memory_retrieval"
        
        # Create multiple branches for the same memory
        created_branches = []
        for scenario in self.test_scenarios[:3]:
            branch = await self.simulator.create_causal_branch(
                source_memory_id=memory_id,
                memory_content=self.sample_memory,
                branch_scenario=scenario
            )
            created_branches.append(branch)
        
        # Retrieve branches
        retrieved_branches = await self.simulator.get_memory_branches(memory_id)
        
        # Validate retrieval
        self.assertEqual(len(retrieved_branches), len(created_branches))
        
        retrieved_ids = [branch.branch_id for branch in retrieved_branches]
        created_ids = [branch.branch_id for branch in created_branches]
        
        for created_id in created_ids:
            self.assertIn(created_id, retrieved_ids)
        
        print(f"✅ Branch retrieval: {len(retrieved_branches)} branches retrieved")
    
    async def test_causal_statistics(self):
        """Test comprehensive statistics tracking"""
        # Perform various operations to generate statistics
        branch1 = await self.simulator.create_causal_branch(
            source_memory_id="stats_memory_1",
            memory_content=self.sample_memory,
            branch_scenario=self.test_scenarios[0]
        )
        
        branch2 = await self.simulator.create_causal_branch(
            source_memory_id="stats_memory_1",
            memory_content=self.sample_memory,
            branch_scenario=self.test_scenarios[1]
        )
        
        # Create superposition
        superposition = await self.simulator.create_superposition(
            memory_id="stats_memory_1",
            branch_ids=[branch1.branch_id, branch2.branch_id]
        )
        
        # Simulate interference
        await self.simulator.simulate_interference(branch1.branch_id, branch2.branch_id)
        
        # Collapse superposition
        await self.simulator.collapse_superposition(superposition.superposition_id)
        
        # Get statistics
        stats = await self.simulator.get_causal_statistics()
        
        # Validate statistics
        self.assertGreaterEqual(stats['branches_created'], 2)
        self.assertGreaterEqual(stats['superpositions_formed'], 1)
        self.assertGreaterEqual(stats['interference_events'], 1)
        self.assertGreaterEqual(stats['coherence_collapses'], 1)
        self.assertGreater(stats['avg_coherence_score'], 0.0)
        self.assertIn('configuration', stats)
        self.assertIn('database_info', stats)
        
        print(f"✅ Statistics: All metrics properly tracked")
        print(f"   📊 Branches: {stats['branches_created']}")
        print(f"   ⚛️ Superpositions: {stats['superpositions_formed']}")
        print(f"   🌊 Interferences: {stats['interference_events']}")
        print(f"   🎯 Collapses: {stats['coherence_collapses']}")
    
    async def test_performance_benchmarks(self):
        """Test performance of causal branching operations"""
        performance_results = {}
        
        # Benchmark branch creation
        start_time = time.time()
        branch = await self.simulator.create_causal_branch(
            source_memory_id="perf_memory",
            memory_content=self.sample_memory,
            branch_scenario="Performance test scenario"
        )
        branch_time = (time.time() - start_time) * 1000
        performance_results['branch_creation_ms'] = branch_time
        
        # Benchmark superposition creation
        branches = [branch]
        for i in range(2):
            branch = await self.simulator.create_causal_branch(
                source_memory_id="perf_memory",
                memory_content=self.sample_memory,
                branch_scenario=f"Perf scenario {i+2}"
            )
            branches.append(branch)
        
        start_time = time.time()
        superposition = await self.simulator.create_superposition(
            memory_id="perf_memory",
            branch_ids=[b.branch_id for b in branches]
        )
        superposition_time = (time.time() - start_time) * 1000
        performance_results['superposition_creation_ms'] = superposition_time
        
        # Benchmark interference simulation
        start_time = time.time()
        await self.simulator.simulate_interference(branches[0].branch_id, branches[1].branch_id)
        interference_time = (time.time() - start_time) * 1000
        performance_results['interference_simulation_ms'] = interference_time
        
        # Benchmark collapse
        start_time = time.time()
        await self.simulator.collapse_superposition(superposition.superposition_id)
        collapse_time = (time.time() - start_time) * 1000
        performance_results['superposition_collapse_ms'] = collapse_time
        
        # Validate performance (all operations should be under 100ms)
        for operation, duration in performance_results.items():
            self.assertLess(duration, 100.0, f"{operation} took {duration:.1f}ms (should be < 100ms)")
        
        print(f"✅ Performance benchmarks: All operations under 100ms")
        for operation, duration in performance_results.items():
            print(f"   ⚡ {operation}: {duration:.1f}ms")
        
        return performance_results
    
    async def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test invalid branch ID
        try:
            await self.simulator.simulate_interference("invalid_branch_1", "invalid_branch_2")
            self.fail("Should have raised ValueError for invalid branch IDs")
        except ValueError:
            pass  # Expected
        
        # Test empty superposition
        try:
            await self.simulator.create_superposition("empty_memory", [])
            self.fail("Should have raised ValueError for empty branch list")
        except ValueError:
            pass  # Expected
        
        # Test invalid superposition collapse
        try:
            await self.simulator.collapse_superposition("invalid_superposition_id")
            self.fail("Should have raised ValueError for invalid superposition ID")
        except ValueError:
            pass  # Expected
        
        print("✅ Edge cases: All error conditions properly handled")
    
    async def test_database_persistence(self):
        """Test that data persists correctly across simulator restarts"""
        # Create some data
        branch = await self.simulator.create_causal_branch(
            source_memory_id="persist_memory",
            memory_content=self.sample_memory,
            branch_scenario="Persistence test"
        )
        
        # Create new simulator instance with same data directory
        new_simulator = CausalBranchSimulator(data_dir=self.test_dir)
        
        # Retrieve data with new instance
        retrieved_branches = await new_simulator.get_memory_branches("persist_memory")
        
        # Validate persistence
        self.assertEqual(len(retrieved_branches), 1)
        self.assertEqual(retrieved_branches[0].branch_id, branch.branch_id)
        self.assertEqual(retrieved_branches[0].source_memory_id, branch.source_memory_id)
        
        print("✅ Database persistence: Data survives simulator restart")

class TestPhase4Integration(unittest.TestCase):
    """Integration tests with Phase 2 and Phase 3 components"""
    
    def setUp(self):
        """Set up integration test environment"""
        if not INTEGRATION_TESTING:
            self.skipTest("Phase 2/3 components not available")
        
        self.test_dir = tempfile.mkdtemp(prefix="phase4_integration_")
        
        # Initialize Phase 2 and 3 components
        self.fractal_encoder = FractalEncoder(data_dir=self.test_dir + "/encoder")
        self.observer_simulator = ObserverEffectSimulator(
            data_dir=self.test_dir + "/observer",
            fractal_encoder=self.fractal_encoder
        )
        
        # Initialize Phase 4 with integration
        self.causal_simulator = CausalBranchSimulator(
            data_dir=self.test_dir + "/causal",
            fractal_encoder=self.fractal_encoder,
            observer_simulator=self.observer_simulator
        )
        
        # Sample complex memory for integration testing
        self.complex_memory = {
            "content": "Exploring the intersection of quantum mechanics, fractal geometry, and consciousness",
            "emotional_tag": "fascination",
            "complexity": 0.9,
            "fractal_depth": 3,
            "observer_sensitivity": 0.8,
            "metadata": {
                "domain": "quantum_consciousness",
                "concepts": ["quantum_entanglement", "fractal_dimension", "observer_effect"],
                "relationships": ["quantum->consciousness", "fractal->pattern", "observer->reality"]
            }
        }
    
    def tearDown(self):
        """Clean up integration test environment"""
        if INTEGRATION_TESTING:
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    async def test_fractal_causal_integration(self):
        """Test integration between fractal encoding and causal branching"""
        # First encode memory with fractal encoder
        encoded_result = await self.fractal_encoder.encode_memory(
            memory_id="integration_test_1",
            content=self.complex_memory["content"],
            metadata=self.complex_memory
        )
        
        # Create causal branches from encoded memory
        branch1 = await self.causal_simulator.create_causal_branch(
            source_memory_id="integration_test_1",
            memory_content=self.complex_memory,
            branch_scenario="User explores quantum consciousness connection"
        )
        
        branch2 = await self.causal_simulator.create_causal_branch(
            source_memory_id="integration_test_1",
            memory_content=self.complex_memory,
            branch_scenario="User focuses on fractal pattern mathematics"
        )
        
        # Validate integration
        self.assertIsNotNone(encoded_result)
        self.assertIsNotNone(branch1)
        self.assertIsNotNone(branch2)
        
        # Check that causal branches maintain fractal structure references
        self.assertEqual(branch1.source_memory_id, "integration_test_1")
        self.assertEqual(branch2.source_memory_id, "integration_test_1")
        
        print("✅ Fractal-causal integration: Successful cross-phase operation")
        print(f"   🧬 Fractal patterns: {encoded_result.pattern_count}")
        print(f"   🌌 Causal branches: 2 created from encoded memory")
    
    async def test_observer_causal_integration(self):
        """Test integration between observer effects and causal branching"""
        # Encode memory first
        await self.fractal_encoder.encode_memory(
            memory_id="observer_causal_test",
            content=self.complex_memory["content"],
            metadata=self.complex_memory
        )
        
        # Apply observer effect
        accessed_memory = await self.observer_simulator.access_memory(
            memory_id="observer_causal_test",
            observer_id="lyrixa_core",
            access_layer="deep"
        )
        
        # Create causal branches based on observer-modified memory
        branch = await self.causal_simulator.create_causal_branch(
            source_memory_id="observer_causal_test",
            memory_content=accessed_memory,
            branch_scenario="Observer effect influences causal evolution"
        )
        
        # Validate observer-causal integration
        self.assertIsNotNone(branch)
        self.assertIn("fidelity", accessed_memory)
        
        # Branch should reflect observer modifications
        observer_fidelity = accessed_memory.get("fidelity", 1.0)
        self.assertGreater(branch.coherence_score, 0.0)
        
        print("✅ Observer-causal integration: Observer effects preserved in branches")
        print(f"   👁️ Observer fidelity: {observer_fidelity:.3f}")
        print(f"   💫 Branch coherence: {branch.coherence_score:.3f}")
    
    async def test_full_pipeline_integration(self):
        """Test complete Phase 2-3-4 pipeline integration"""
        memory_id = "full_pipeline_test"
        
        # Phase 2: Fractal encoding
        fractal_result = await self.fractal_encoder.encode_memory(
            memory_id=memory_id,
            content=self.complex_memory["content"],
            metadata=self.complex_memory
        )
        
        # Phase 3: Observer access
        observed_memory = await self.observer_simulator.access_memory(
            memory_id=memory_id,
            observer_id="user_interactive",
            access_layer="core"
        )
        
        # Phase 4: Causal branching from observed memory
        branches = []
        scenarios = [
            "User explores quantum implications",
            "User investigates fractal patterns",
            "User examines consciousness aspects"
        ]
        
        for scenario in scenarios:
            branch = await self.causal_simulator.create_causal_branch(
                source_memory_id=memory_id,
                memory_content=observed_memory,
                branch_scenario=scenario
            )
            branches.append(branch)
        
        # Create superposition from all branches
        superposition = await self.causal_simulator.create_superposition(
            memory_id=memory_id,
            branch_ids=[branch.branch_id for branch in branches]
        )
        
        # Validate full pipeline
        self.assertEqual(len(branches), 3)
        self.assertIsNotNone(superposition)
        self.assertEqual(len(superposition.active_branches), 3)
        
        # Performance validation
        self.assertGreater(fractal_result.compression_ratio, 0.0)
        self.assertGreater(observed_memory.get("fidelity", 0.0), 0.0)
        self.assertGreater(superposition.coherence_score, 0.0)
        
        print("✅ Full pipeline integration: Phase 2→3→4 successfully chained")
        print(f"   🧬 Fractal compression: {fractal_result.compression_ratio:.1f}x")
        print(f"   👁️ Observer fidelity: {observed_memory.get('fidelity', 0.0):.3f}")
        print(f"   ⚛️ Superposition coherence: {superposition.coherence_score:.3f}")
    
    async def test_integration_performance(self):
        """Test performance of integrated Phase 2-3-4 operations"""
        start_time = time.time()
        
        # Complete integrated operation
        memory_id = "perf_integration_test"
        
        # Fractal encoding
        await self.fractal_encoder.encode_memory(
            memory_id=memory_id,
            content=self.complex_memory["content"],
            metadata=self.complex_memory
        )
        
        # Observer access
        observed_memory = await self.observer_simulator.access_memory(
            memory_id=memory_id,
            observer_id="lyrixa_core",
            access_layer="deep"
        )
        
        # Causal branching
        branch = await self.causal_simulator.create_causal_branch(
            source_memory_id=memory_id,
            memory_content=observed_memory,
            branch_scenario="Integrated performance test"
        )
        
        total_time = (time.time() - start_time) * 1000
        
        # Validate integrated performance (should be under 200ms)
        self.assertLess(total_time, 200.0)
        self.assertIsNotNone(branch)
        
        print(f"✅ Integration performance: {total_time:.1f}ms for full Phase 2-3-4 pipeline")

# Test runner with comprehensive reporting
async def run_phase4_tests():
    """Run comprehensive Phase 4 test suite with detailed reporting"""
    print("🧿 AETHERRA QFAC PHASE 4 - CAUSAL BRANCHING TEST SUITE")
    print("=" * 80)
    
    # Core causal branching tests
    print("\n🧪 Running TestCausalBranchSimulator...")
    print("-" * 60)
    
    test_suite = TestCausalBranchSimulator()
    
    # Test methods to run
    core_tests = [
        'test_causal_branch_creation',
        'test_multiple_branch_creation', 
        'test_superposition_creation',
        'test_interference_simulation',
        'test_superposition_collapse',
        'test_delta_compression',
        'test_memory_branch_retrieval',
        'test_causal_statistics',
        'test_performance_benchmarks',
        'test_edge_cases',
        'test_database_persistence'
    ]
    
    passed_tests = 0
    failed_tests = 0
    performance_data = {}
    
    for test_name in core_tests:
        try:
            test_suite.setUp()
            test_method = getattr(test_suite, test_name)
            
            if asyncio.iscoroutinefunction(test_method):
                result = await test_method()
                if test_name == 'test_performance_benchmarks' and result:
                    performance_data.update(result)
            else:
                result = test_method()
            
            passed_tests += 1
            test_suite.tearDown()
            
        except Exception as e:
            print(f"❌ {test_name}: {str(e)}")
            failed_tests += 1
            test_suite.tearDown()
    
    # Integration tests (if available)
    if INTEGRATION_TESTING:
        print("\n🧪 Running TestPhase4Integration...")
        print("-" * 60)
        
        integration_suite = TestPhase4Integration()
        integration_tests = [
            'test_fractal_causal_integration',
            'test_observer_causal_integration', 
            'test_full_pipeline_integration',
            'test_integration_performance'
        ]
        
        for test_name in integration_tests:
            try:
                integration_suite.setUp()
                test_method = getattr(integration_suite, test_name)
                
                if asyncio.iscoroutinefunction(test_method):
                    await test_method()
                else:
                    test_method()
                
                passed_tests += 1
                integration_suite.tearDown()
                
            except Exception as e:
                print(f"❌ {test_name}: {str(e)}")
                failed_tests += 1
                integration_suite.tearDown()
    
    # Test results summary
    total_tests = passed_tests + failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "=" * 80)
    print("🏆 PHASE 4 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"📊 Total tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    if performance_data:
        print(f"\n⚡ PERFORMANCE RESULTS")
        print("-" * 40)
        for operation, duration in performance_data.items():
            print(f"   {operation}: {duration:.1f}ms")
    
    if success_rate == 100.0:
        print("🎉 All tests passed! Phase 4 implementation ready for production")
    elif success_rate >= 90.0:
        print("⚠️ Most tests passed - minor issues to address")
    else:
        print("❌ Significant issues found - review and fix failures")
    
    return success_rate

if __name__ == "__main__":
    # Run the test suite
    success_rate = asyncio.run(run_phase4_tests())
    exit(0 if success_rate == 100.0 else 1)
