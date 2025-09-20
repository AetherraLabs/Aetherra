#!/usr/bin/env python3
# Standard library imports
import sys

print("🔍 Testing Qiskit imports directly...")

try:
    # Third party imports
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    from qiskit.circuit.library import QFT
    from qiskit.providers.aer import AerSimulator

    print("✅ All core Qiskit components imported successfully")

    # Test creating a simple circuit
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    print("✅ Simple quantum circuit created successfully")

    # Test AerSimulator
    sim = AerSimulator()
    print(f"✅ AerSimulator initialized: {sim}")

except Exception as e:
    print(f"❌ Error: {e}")
    # Standard library imports
    import traceback

    traceback.print_exc()
