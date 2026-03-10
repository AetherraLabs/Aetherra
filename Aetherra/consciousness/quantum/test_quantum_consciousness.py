# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 AETHERRA QUANTUM CONSCIOUSNESS TEST
Phase 7.2 Component Testing

Simple test runner to verify all quantum consciousness components work correctly.
"""

# Standard library imports
import asyncio
import logging
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_quantum_decision_engine():
    """Test the quantum decision engine"""
    try:
        print("🧠 Testing Quantum Decision Engine...")

        # Import and test locally
        # Third party imports
        from quantum_decision_engine import test_quantum_decision

        await test_quantum_decision()

        print("✅ Quantum Decision Engine test passed")
        return True

    except Exception as e:
        print(f"❌ Quantum Decision Engine test failed: {e}")
        return False


async def test_quantum_tunneling():
    """Test the quantum tunneling logic"""
    try:
        print("\n🌀 Testing Quantum Tunneling Logic...")

        # Third party imports
        from quantum_tunneling_logic import test_quantum_tunneling

        await test_quantum_tunneling()

        print("✅ Quantum Tunneling Logic test passed")
        return True

    except Exception as e:
        print(f"❌ Quantum Tunneling Logic test failed: {e}")
        return False


async def test_quantum_interference():
    """Test the quantum interference patterns"""
    try:
        print("\n🌊 Testing Quantum Interference Patterns...")

        # Third party imports
        from quantum_interference_patterns import test_quantum_interference

        await test_quantum_interference()

        print("✅ Quantum Interference Patterns test passed")
        return True

    except Exception as e:
        print(f"❌ Quantum Interference Patterns test failed: {e}")
        return False


async def run_all_tests():
    """Run all quantum consciousness tests"""
    print("🧠 AETHERRA QUANTUM CONSCIOUSNESS - PHASE 7.2 TESTING")
    print("=" * 60)

    tests = [
        test_quantum_decision_engine,
        test_quantum_tunneling,
        test_quantum_interference,
    ]

    results = []
    for test in tests:
        result = await test()
        results.append(result)

    print("\n📊 TEST RESULTS:")
    print("=" * 30)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed / total * 100:.1f}%")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Phase 7.2 Ready!")
        return True
    else:
        print("⚠️  Some tests failed - Check components")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
