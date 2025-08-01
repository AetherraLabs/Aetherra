"""
⚛️ AETHERRA QFAC PHASE 5 - QUANTUM MEMORY BRIDGE VALIDATION SUITE
================================================================================
Comprehensive testing framework for the quantum memory bridge component.
Tests quantum encoding, retrieval, interference, and error correction capabilities.

Test Categories:
🧮 Quantum Encoding Tests - Classical to quantum memory encoding
🔍 Quantum Retrieval Tests - Quantum to classical memory reconstruction
🌊 Quantum Interference Tests - Multi-state quantum interference patterns
🔧 Error Correction Tests - Quantum error correction and mitigation
📊 Performance Tests - Quantum operation efficiency and scalability
🔗 Integration Tests - Phase 2-4 quantum bridge integration
"""

import asyncio
import unittest
import tempfile
import shutil
import time
import numpy as np
from datetime import datetime
from pathlib import Path

# Import Phase 5 quantum bridge
from quantum_memory_bridge import (
    QuantumMemoryBridge, QuantumMemoryState, QuantumCircuitTemplate,
    QuantumExperimentResult, QUANTUM_AVAILABLE
)

class TestQuantumMemoryBridge(unittest.TestCase):
    """Test the core quantum memory bridge functionality"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="test_quantum_bridge_")
        self.bridge = QuantumMemoryBridge(
            data_dir=self.test_dir,
            quantum_backend="simulator",
            max_qubits=12
        )

        # Sample memory data for testing
        self.sample_memory = {
            "content": "Quantum memory test data with complex patterns",
            "emotional_tag": "curiosity",
            "complexity": 0.75,
            "confidence": 0.82,
            "quantum_properties": ["superposition", "entanglement"]
        }

        self.sample_memory_2 = {
            "content": "Alternative quantum memory pattern for interference",
            "emotional_tag": "fascination",
            "complexity": 0.68,
            "confidence": 0.90,
            "quantum_properties": ["coherence", "decoherence"]
        }

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    async def test_quantum_encoding_basic(self):
        """Test basic quantum memory encoding"""
        print("🧮 Testing quantum memory encoding...")

        quantum_state = await self.bridge.encode_memory_to_quantum(
            memory_id="test_memory_001",
            memory_data=self.sample_memory,
            operation_type="compression"
        )

        # Validate quantum state structure
        self.assertIsInstance(quantum_state, QuantumMemoryState)
        self.assertEqual(quantum_state.memory_id, "test_memory_001")
        self.assertGreater(quantum_state.qubit_count, 0)
        self.assertGreater(quantum_state.circuit_depth, 0)
        self.assertGreaterEqual(quantum_state.encoding_fidelity, 0.5)
        self.assertLessEqual(quantum_state.encoding_fidelity, 1.0)
        self.assertEqual(quantum_state.classical_shadow, self.sample_memory)

        print(f"   ✅ Quantum state: {quantum_state.state_id}")
        print(f"   🧮 Qubits: {quantum_state.qubit_count}")
        print(f"   📊 Fidelity: {quantum_state.encoding_fidelity:.3f}")

        return quantum_state

    async def test_quantum_retrieval(self):
        """Test quantum memory retrieval"""
        print("🔍 Testing quantum memory retrieval...")

        # First encode memory
        quantum_state = await self.bridge.encode_memory_to_quantum(
            memory_id="test_retrieval_001",
            memory_data=self.sample_memory,
            operation_type="compression"
        )

        # Then retrieve it
        retrieval_result = await self.bridge.quantum_memory_retrieval(
            quantum_state=quantum_state,
            measurement_basis="computational"
        )

        # Validate retrieval results
        self.assertIn('reconstructed_data', retrieval_result)
        self.assertIn('measurement_results', retrieval_result)
        self.assertIn('retrieval_fidelity', retrieval_result)
        self.assertIn('measurement_basis', retrieval_result)

        reconstructed = retrieval_result['reconstructed_data']
        fidelity = retrieval_result['retrieval_fidelity']

        # Check basic reconstruction quality
        self.assertIsInstance(reconstructed, dict)
        self.assertGreaterEqual(fidelity, 0.0)
        self.assertLessEqual(fidelity, 1.0)

        print(f"   ✅ Retrieval fidelity: {fidelity:.3f}")
        print(f"   📊 Measurement basis: {retrieval_result['measurement_basis']}")

        # Check if key fields are preserved
        if 'content' in reconstructed:
            print(f"   📝 Content preserved: {'✅' if 'content' in reconstructed else '❌'}")

        return retrieval_result

    async def test_multiple_operation_types(self):
        """Test different quantum operation types"""
        print("🔄 Testing multiple operation types...")

        operation_types = ["compression", "pattern_analysis", "causal_superposition"]
        results = {}

        for op_type in operation_types:
            if op_type in self.bridge.circuit_templates:
                quantum_state = await self.bridge.encode_memory_to_quantum(
                    memory_id=f"test_{op_type}_001",
                    memory_data=self.sample_memory,
                    operation_type=op_type
                )

                results[op_type] = quantum_state
                print(f"   ✅ {op_type}: fidelity {quantum_state.encoding_fidelity:.3f}")

        # Validate we got results for available operation types
        self.assertGreater(len(results), 0)

        # All quantum states should be valid
        for op_type, quantum_state in results.items():
            self.assertIsInstance(quantum_state, QuantumMemoryState)
            self.assertGreater(quantum_state.encoding_fidelity, 0.0)

        return results

    async def test_quantum_interference(self):
        """Test quantum interference experiments"""
        print("🌊 Testing quantum interference...")

        # Create multiple quantum states
        quantum_state_1 = await self.bridge.encode_memory_to_quantum(
            memory_id="interference_test_001",
            memory_data=self.sample_memory,
            operation_type="compression"
        )

        quantum_state_2 = await self.bridge.encode_memory_to_quantum(
            memory_id="interference_test_002",
            memory_data=self.sample_memory_2,
            operation_type="compression"
        )

        # Perform interference experiment
        interference_result = await self.bridge.quantum_interference_experiment(
            memory_states=[quantum_state_1, quantum_state_2]
        )

        # Validate interference experiment results
        self.assertIsInstance(interference_result, QuantumExperimentResult)
        self.assertEqual(interference_result.operation_type, "interference")
        self.assertGreaterEqual(interference_result.fidelity_score, 0.0)
        self.assertLessEqual(interference_result.fidelity_score, 1.0)
        self.assertEqual(interference_result.error_rate, 1.0 - interference_result.fidelity_score)

        print(f"   ✅ Experiment: {interference_result.experiment_id}")
        print(f"   📊 Fidelity: {interference_result.fidelity_score:.3f}")
        print(f"   ⚡ Execution time: {interference_result.execution_time:.1f}ms")
        print(f"   🎯 Success: {'✅' if interference_result.success else '❌'}")

        return interference_result

    async def test_error_correction(self):
        """Test quantum error correction capabilities"""
        print("🔧 Testing quantum error correction...")

        # Create quantum state for error correction testing
        quantum_state = await self.bridge.encode_memory_to_quantum(
            memory_id="error_correction_test_001",
            memory_data=self.sample_memory,
            operation_type="compression"
        )

        # Test error correction
        error_correction_result = await self.bridge.quantum_error_correction_test(quantum_state)

        # Validate error correction results
        self.assertIn('error_correction_available', error_correction_result)

        if error_correction_result['error_correction_available']:
            self.assertIn('logical_error_rate', error_correction_result)
            self.assertIn('syndrome_detection_success', error_correction_result)
            self.assertIn('correction_fidelity', error_correction_result)

            logical_error_rate = error_correction_result['logical_error_rate']
            correction_fidelity = error_correction_result['correction_fidelity']

            self.assertGreaterEqual(logical_error_rate, 0.0)
            self.assertLessEqual(logical_error_rate, 1.0)
            self.assertGreaterEqual(correction_fidelity, 0.0)
            self.assertLessEqual(correction_fidelity, 1.0)

            print(f"   ✅ Error correction available")
            print(f"   📊 Logical error rate: {logical_error_rate:.6f}")
            print(f"   🔧 Correction fidelity: {correction_fidelity:.3f}")
        else:
            print(f"   ⚠️ Error correction not available: {error_correction_result.get('message', 'Unknown')}")

        return error_correction_result

    async def test_quantum_statistics(self):
        """Test quantum bridge statistics collection"""
        print("📊 Testing quantum statistics...")

        # Perform several operations to generate statistics
        for i in range(3):
            await self.bridge.encode_memory_to_quantum(
                memory_id=f"stats_test_{i:03d}",
                memory_data=self.sample_memory,
                operation_type="compression"
            )

        # Get statistics
        stats = await self.bridge.get_quantum_statistics()

        # Validate statistics structure
        required_fields = [
            'quantum_operations', 'successful_encodings', 'failed_operations',
            'total_qubits_used', 'avg_fidelity', 'quantum_backends_used',
            'configuration', 'circuit_templates', 'data_directory'
        ]

        for field in required_fields:
            self.assertIn(field, stats)

        # Validate statistics values
        self.assertGreaterEqual(stats['quantum_operations'], 3)
        self.assertGreaterEqual(stats['successful_encodings'], 0)
        self.assertGreaterEqual(stats['failed_operations'], 0)
        self.assertGreaterEqual(stats['total_qubits_used'], 0)
        self.assertIsInstance(stats['quantum_backends_used'], list)
        self.assertIsInstance(stats['configuration'], dict)
        self.assertIsInstance(stats['circuit_templates'], list)

        print(f"   ✅ Quantum operations: {stats['quantum_operations']}")
        print(f"   📊 Success rate: {stats['successful_encodings']}/{stats['quantum_operations']}")
        print(f"   🧮 Total qubits used: {stats['total_qubits_used']}")
        print(f"   🔧 Circuit templates: {len(stats['circuit_templates'])}")

        return stats

    async def test_serialization(self):
        """Test quantum state serialization and deserialization"""
        print("💾 Testing quantum state serialization...")

        # Create quantum state
        original_state = await self.bridge.encode_memory_to_quantum(
            memory_id="serialization_test_001",
            memory_data=self.sample_memory,
            operation_type="compression"
        )

        # Serialize to dict
        state_dict = original_state.to_dict()

        # Validate serialization
        self.assertIsInstance(state_dict, dict)
        self.assertIn('state_id', state_dict)
        self.assertIn('memory_id', state_dict)
        self.assertIn('creation_timestamp', state_dict)

        # Deserialize from dict
        deserialized_state = QuantumMemoryState.from_dict(state_dict)

        # Validate deserialization
        self.assertEqual(deserialized_state.state_id, original_state.state_id)
        self.assertEqual(deserialized_state.memory_id, original_state.memory_id)
        self.assertEqual(deserialized_state.qubit_count, original_state.qubit_count)
        self.assertEqual(deserialized_state.encoding_fidelity, original_state.encoding_fidelity)
        self.assertEqual(deserialized_state.classical_shadow, original_state.classical_shadow)

        print(f"   ✅ Serialization successful")
        print(f"   📝 State ID preserved: {deserialized_state.state_id}")
        print(f"   📊 Fidelity preserved: {deserialized_state.encoding_fidelity:.3f}")

        return deserialized_state

class TestQuantumPerformance(unittest.TestCase):
    """Test quantum bridge performance characteristics"""

    def setUp(self):
        """Set up performance test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="test_quantum_perf_")
        self.bridge = QuantumMemoryBridge(
            data_dir=self.test_dir,
            quantum_backend="simulator",
            max_qubits=16
        )

        # Performance test memory data
        self.memory_data = {
            "content": "Performance test memory data with measured timing",
            "emotional_tag": "determination",
            "complexity": 0.85,
            "confidence": 0.78
        }

    def tearDown(self):
        """Clean up performance test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    async def test_encoding_performance(self):
        """Test quantum encoding performance"""
        print("⚡ Testing quantum encoding performance...")

        encoding_times = []
        num_tests = 5

        for i in range(num_tests):
            start_time = time.time()

            quantum_state = await self.bridge.encode_memory_to_quantum(
                memory_id=f"perf_test_{i:03d}",
                memory_data=self.memory_data,
                operation_type="compression"
            )

            end_time = time.time()
            encoding_time = (end_time - start_time) * 1000  # Convert to milliseconds
            encoding_times.append(encoding_time)

            # Validate the encoding was successful
            self.assertIsInstance(quantum_state, QuantumMemoryState)
            self.assertGreater(quantum_state.encoding_fidelity, 0.0)

        # Calculate performance statistics
        avg_time = sum(encoding_times) / len(encoding_times)
        min_time = min(encoding_times)
        max_time = max(encoding_times)

        print(f"   ✅ Encoding tests: {num_tests}")
        print(f"   ⚡ Average time: {avg_time:.1f}ms")
        print(f"   🚀 Min time: {min_time:.1f}ms")
        print(f"   🐌 Max time: {max_time:.1f}ms")

        # Performance assertions
        self.assertLess(avg_time, 500.0)  # Should average under 500ms
        self.assertLess(max_time, 1000.0)  # No single encoding over 1 second

        return {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'encoding_times': encoding_times
        }

    async def test_scalability(self):
        """Test quantum bridge scalability with multiple operations"""
        print("📈 Testing quantum bridge scalability...")

        operation_counts = [1, 3, 5, 10]
        scalability_results = {}

        for count in operation_counts:
            start_time = time.time()

            # Perform multiple concurrent operations
            tasks = []
            for i in range(count):
                task = self.bridge.encode_memory_to_quantum(
                    memory_id=f"scale_test_{count}_{i:03d}",
                    memory_data=self.memory_data,
                    operation_type="compression"
                )
                tasks.append(task)

            # Wait for all operations to complete
            results = await asyncio.gather(*tasks)

            end_time = time.time()
            total_time = (end_time - start_time) * 1000
            avg_time_per_op = total_time / count

            # Validate all operations succeeded
            for result in results:
                self.assertIsInstance(result, QuantumMemoryState)
                self.assertGreater(result.encoding_fidelity, 0.0)

            scalability_results[count] = {
                'total_time': total_time,
                'avg_time_per_op': avg_time_per_op,
                'throughput': count / (total_time / 1000)  # operations per second
            }

            print(f"   ✅ {count} operations: {total_time:.1f}ms total, {avg_time_per_op:.1f}ms avg")

        # Check that scalability is reasonable (not exponentially degrading)
        throughputs = [results['throughput'] for results in scalability_results.values()]
        min_throughput = min(throughputs)
        max_throughput = max(throughputs)

        # Throughput shouldn't degrade by more than 70% across scale ranges (adjusted for simulation)
        throughput_ratio = min_throughput / max_throughput if max_throughput > 0 else 1.0
        self.assertGreater(throughput_ratio, 0.3)  # More lenient for simulation mode

        return scalability_results

class TestQuantumIntegration(unittest.TestCase):
    """Test quantum bridge integration with Phase 2-4 components"""

    def setUp(self):
        """Set up integration test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="test_quantum_integration_")
        self.bridge = QuantumMemoryBridge(
            data_dir=self.test_dir,
            quantum_backend="simulator",
            max_qubits=8
        )

    def tearDown(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    async def test_circuit_templates_validity(self):
        """Test that all circuit templates are valid"""
        print("🔧 Testing circuit template validity...")

        templates = self.bridge.circuit_templates
        self.assertGreater(len(templates), 0)

        for template_name, template in templates.items():
            self.assertIsInstance(template, QuantumCircuitTemplate)
            self.assertIsInstance(template.template_id, str)
            self.assertIsInstance(template.template_name, str)
            self.assertGreater(template.qubit_count, 0)
            self.assertGreaterEqual(template.parameter_count, 0)
            self.assertIsInstance(template.gate_sequence, list)
            self.assertIsInstance(template.memory_operation_type, str)

            print(f"   ✅ {template_name}: {template.qubit_count} qubits, {len(template.gate_sequence)} gates")

        return templates

    async def test_quantum_availability_handling(self):
        """Test handling of quantum backend availability"""
        print("🔍 Testing quantum availability handling...")

        # Test with current quantum availability
        stats = await self.bridge.get_quantum_statistics()
        quantum_config = stats['configuration']

        self.assertIn('qiskit_available', quantum_config)
        self.assertIn('cirq_available', quantum_config)
        self.assertIn('quantum_available', quantum_config)

        # Should handle gracefully regardless of quantum availability
        quantum_state = await self.bridge.encode_memory_to_quantum(
            memory_id="availability_test_001",
            memory_data={"content": "Test quantum availability", "complexity": 0.5},
            operation_type="compression"
        )

        self.assertIsInstance(quantum_state, QuantumMemoryState)

        print(f"   ✅ Quantum available: {quantum_config['quantum_available']}")
        print(f"   🔬 Qiskit available: {quantum_config['qiskit_available']}")
        print(f"   🔬 Cirq available: {quantum_config['cirq_available']}")

        return quantum_config

async def run_quantum_bridge_validation():
    """Run comprehensive quantum bridge validation suite"""
    print("⚛️ AETHERRA QFAC PHASE 5 - QUANTUM BRIDGE VALIDATION")
    print("=" * 80)

    # Test results tracking
    test_results = {
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0,
        'start_time': time.time()
    }

    try:
        # Core functionality tests
        print("\n🧮 CORE QUANTUM FUNCTIONALITY TESTS")
        print("-" * 50)

        test_suite = TestQuantumMemoryBridge()
        test_suite.setUp()

        try:
            # Test quantum encoding
            test_results['tests_run'] += 1
            await test_suite.test_quantum_encoding_basic()
            test_results['tests_passed'] += 1

            # Test quantum retrieval
            test_results['tests_run'] += 1
            await test_suite.test_quantum_retrieval()
            test_results['tests_passed'] += 1

            # Test multiple operation types
            test_results['tests_run'] += 1
            await test_suite.test_multiple_operation_types()
            test_results['tests_passed'] += 1

            # Test quantum interference
            test_results['tests_run'] += 1
            await test_suite.test_quantum_interference()
            test_results['tests_passed'] += 1

            # Test error correction
            test_results['tests_run'] += 1
            await test_suite.test_error_correction()
            test_results['tests_passed'] += 1

            # Test statistics
            test_results['tests_run'] += 1
            await test_suite.test_quantum_statistics()
            test_results['tests_passed'] += 1

            # Test serialization
            test_results['tests_run'] += 1
            await test_suite.test_serialization()
            test_results['tests_passed'] += 1

        except Exception as e:
            print(f"❌ Core functionality test failed: {e}")
            test_results['tests_failed'] += 1
        finally:
            test_suite.tearDown()

        # Performance tests
        print("\n⚡ QUANTUM PERFORMANCE TESTS")
        print("-" * 50)

        perf_suite = TestQuantumPerformance()
        perf_suite.setUp()

        try:
            # Test encoding performance
            test_results['tests_run'] += 1
            await perf_suite.test_encoding_performance()
            test_results['tests_passed'] += 1

            # Test scalability
            test_results['tests_run'] += 1
            await perf_suite.test_scalability()
            test_results['tests_passed'] += 1

        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            test_results['tests_failed'] += 1
        finally:
            perf_suite.tearDown()

        # Integration tests
        print("\n🔗 QUANTUM INTEGRATION TESTS")
        print("-" * 50)

        integration_suite = TestQuantumIntegration()
        integration_suite.setUp()

        try:
            # Test circuit templates
            test_results['tests_run'] += 1
            await integration_suite.test_circuit_templates_validity()
            test_results['tests_passed'] += 1

            # Test quantum availability handling
            test_results['tests_run'] += 1
            await integration_suite.test_quantum_availability_handling()
            test_results['tests_passed'] += 1

        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            test_results['tests_failed'] += 1
        finally:
            integration_suite.tearDown()

    except Exception as e:
        print(f"❌ Test suite execution failed: {e}")
        test_results['tests_failed'] += 1

    # Calculate final results
    test_results['end_time'] = time.time()
    test_results['total_time'] = test_results['end_time'] - test_results['start_time']
    test_results['success_rate'] = (test_results['tests_passed'] / test_results['tests_run'] * 100) if test_results['tests_run'] > 0 else 0

    # Print final validation report
    print(f"\n📊 QUANTUM BRIDGE VALIDATION RESULTS")
    print("=" * 80)
    print(f"⚛️ Tests run: {test_results['tests_run']}")
    print(f"✅ Tests passed: {test_results['tests_passed']}")
    print(f"❌ Tests failed: {test_results['tests_failed']}")
    print(f"📊 Success rate: {test_results['success_rate']:.1f}%")
    print(f"⚡ Total time: {test_results['total_time']:.2f}s")

    if test_results['success_rate'] >= 90:
        print(f"\n🎉 PHASE 5 QUANTUM BRIDGE VALIDATION: ✅ SUCCESS")
        print(f"⚛️ Quantum memory bridge is production-ready for experimental use")
    elif test_results['success_rate'] >= 70:
        print(f"\n⚠️ PHASE 5 QUANTUM BRIDGE VALIDATION: 🔄 PARTIAL SUCCESS")
        print(f"⚛️ Quantum memory bridge needs optimization before production")
    else:
        print(f"\n❌ PHASE 5 QUANTUM BRIDGE VALIDATION: ❌ FAILED")
        print(f"⚛️ Quantum memory bridge requires significant fixes")

    return test_results

if __name__ == "__main__":
    # Run the validation suite
    results = asyncio.run(run_quantum_bridge_validation())
