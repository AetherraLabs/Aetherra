"""
QFAC Diagnostic Dashboard
Provides analytics and debugging info for all QFAC phases.
"""

from flask import Blueprint, Flask, jsonify

app = Flask(__name__)
qfac_dashboard = Blueprint("qfac_dashboard", __name__)


@app.route("/qfac/metrics")
def qfac_metrics():
    from .qfac_state_tracker import get_qfac_phase_metrics

    return jsonify(get_qfac_phase_metrics())


# For test compatibility
if __name__ == "__main__":
    app.run()
