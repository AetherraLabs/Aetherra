"""
Quantum Web Dashboard
Displays real-time quantum memory metrics: coherence, branching, entropy.
"""
from flask import Blueprint, jsonify
from memory.quantum_memory_state import get_quantum_metrics

quantum_dashboard = Blueprint('quantum_dashboard', __name__)

@quantum_dashboard.route("/api/quantum/status")
def quantum_status():
    return jsonify(get_quantum_metrics())
