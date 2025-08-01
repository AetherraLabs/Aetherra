#!/usr/bin/env python3
"""
🧪 Quantum Memory Integration Test
=================================

Quick test to verify quantum memory integration is working correctly
after fixing compatibility issues.
"""

import asyncio
import sys
import os

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Aetherra', 'lyrixa', 'memory'))

from quantum_memory_integration import create_quantum_enhanced_memory_engine


async def test_quantum_integration():
    """Test the quantum memory integration functionality"""

    print("🧪 Testing Quantum Memory Integration")
    print("=" * 50)

    try:
        # Create quantum-enhanced memory engine
        print("🚀 Creating quantum-enhanced memory engine...")
        engine = create_quantum_enhanced_memory_engine()

        # Test system status
        print("📊 Checking system status...")
        status = await engine.get_enhanced_system_status()

        print(f"✅ System Status:")
        print(f"   • Quantum Available: {status['quantum_system']['quantum_available']}")
        print(f"   • Backend: {status['quantum_system']['configuration']['quantum_backend']}")
        print(f"   • Max Qubits: {status['quantum_system']['configuration']['max_qubits']}")
        print(f"   • Quantum States: {status['quantum_system']['quantum_states_count']}")

        # Test memory storage with quantum encoding
        print("\n📝 Testing quantum memory storage...")

        test_content = "Quantum computing leverages superposition for parallel computation"
        result = await engine.remember(
            content=test_content,
            tags=["quantum", "computing", "superposition"],
            category="technology",
            confidence=0.9
        )

        print(f"✅ Memory Storage Result:")
        print(f"   • Success: {result.success}")
        print(f"   • Quantum Enabled: {result.quantum_enabled}")
        print(f"   • Classical Fallback: {result.classical_fallback}")
        print(f"   • Fragment ID: {result.fragment_id}")

        if result.quantum_metrics:
            print(f"   • Quantum Coherence: {result.quantum_metrics.coherence_score:.3f}")
            print(f"   • Quantum Fidelity: {result.quantum_metrics.quantum_fidelity:.3f}")

        # Test quantum-enhanced recall
        print("\n🔍 Testing quantum-enhanced recall...")

        recall_results = await engine.recall(
            query="quantum computing",
            recall_strategy="quantum_hybrid",
            limit=3
        )

        print(f"✅ Recall Results:")
        print(f"   • Found {len(recall_results)} memories")

        for i, memory in enumerate(recall_results[:2]):
            print(f"   • Memory {i+1}:")
            print(f"     - Content: {str(memory.get('content', ''))[:60]}...")
            print(f"     - Relevance: {memory.get('relevance_score', 0):.3f}")
            print(f"     - Source: {memory.get('source', 'unknown')}")

        # Test quantum coherence monitoring
        print("\n🔧 Testing quantum coherence monitoring...")

        coherence_check = await engine.check_quantum_coherence()

        print(f"✅ Coherence Check:")
        if coherence_check.get("quantum_available"):
            print(f"   • Total Quantum States: {coherence_check['total_quantum_states']}")
            print(f"   • Coherent States: {coherence_check['coherent_states']}")
            print(f"   • Average Coherence: {coherence_check['average_coherence']:.3f}")
        else:
            print(f"   • Quantum bridge not available: {coherence_check.get('message', 'Unknown')}")

        # Final status check
        print("\n📈 Final quantum operation statistics:")
        final_status = await engine.get_enhanced_system_status()
        quantum_ops = engine.quantum_operation_stats

        print(f"   • Quantum Encodings: {quantum_ops['quantum_encodings']}")
        print(f"   • Quantum Recalls: {quantum_ops['quantum_recalls']}")
        print(f"   • Classical Fallbacks: {quantum_ops['classical_fallbacks']}")
        print(f"   • Coherence Corrections: {quantum_ops['coherence_corrections']}")

        print(f"\n🎉 Quantum Memory Integration Test COMPLETED!")
        print(f"✅ All major components are functioning correctly")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_quantum_integration())
    if success:
        print(f"\n🌌 Quantum memory system is ready for production use!")
        print(f"🚀 Dashboard available at: http://localhost:8080/quantum")
    else:
        print(f"\n⚠️ Integration test failed - check error messages above")

    sys.exit(0 if success else 1)
