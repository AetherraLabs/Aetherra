"""
QFAC Diagnostic Dashboard
Provides analytics and debugging info for all QFAC phases.
"""
from flask import Blueprint, jsonify
from memory.qfac_state_tracker import get_qfac_phase_metrics

qfac_dashboard = Blueprint('qfac_dashboard', __name__)

@qfac_dashboard.route("/api/qfac/metrics")
def qfac_metrics():
    return jsonify(get_qfac_phase_metrics())
