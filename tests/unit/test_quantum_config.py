#!/usr/bin/env python3
# Standard library imports
import os

print("🔍 Checking quantum memory configuration...")
print(f"AETHERRA_QFAC_IN_OS: {os.getenv('AETHERRA_QFAC_IN_OS')}")
print(f"AETHERRA_QFAC_MODE: {os.getenv('AETHERRA_QFAC_MODE')}")
print(f"AETHERRA_QFAC_BACKEND: {os.getenv('AETHERRA_QFAC_BACKEND')}")
print(f"AETHERRA_QFAC_VALIDATED: {os.getenv('AETHERRA_QFAC_VALIDATED')}")
print(f"AETHERRA_QFAC_POLICY: {os.getenv('AETHERRA_QFAC_POLICY')}")

print("\n🧪 Testing QFAC policy resolution...")
try:
    # Aetherra imports
    from Aetherra.aetherra_core.memory.qfac_policy import QFACPolicy

    policy = QFACPolicy()
    result = policy.resolve_mode("dev", "hybrid", None)
    print(f"Policy result: {result}")

    print("\n⚛️ Testing quantum memory bridge initialization...")
    # Aetherra imports
    from Aetherra.aetherra_core.memory.quantum_memory_bridge import QuantumMemoryBridge

    bridge = QuantumMemoryBridge(quantum_backend="qiskit", max_qubits=16)
    print(f"Quantum bridge stats: {bridge.stats}")
    print("✅ Quantum memory bridge initialized successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
    # Standard library imports
    import traceback

    traceback.print_exc()
