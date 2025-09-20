# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
QFAC Diagnostic Dashboard
Provides analytics and debugging info for all QFAC phases.

This module exposes two integration surfaces:
- QFACDashboard class (preferred in-process integration used by QFACMemorySystem)
- A tiny Flask app/blueprint for optional HTTP metrics
"""

# Standard library imports
import time
from typing import Any, Dict

# Third party imports
from flask import Blueprint, Flask, jsonify

# --- In-process dashboard API used by QFACMemorySystem ---


class QFACDashboard:
    """Lightweight dashboard facade returning live QFAC metrics.

    Contract:
    - async start_dashboard(mode: str = "text") -> None
    - async stop_dashboard() -> None
    - async get_dashboard_summary() -> Dict[str, Any]
    """

    def __init__(self, analyzer):
        # analyzer is MemoryCompressionAnalyzer, providing async performance metrics
        self.analyzer = analyzer
        self._started = False
        self._mode = "text"

    async def start_dashboard(self, mode: str = "text"):
        # For headless/test environments we don't spin up UI; just mark started
        self._started = True
        self._mode = mode

    async def stop_dashboard(self):
        self._started = False

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        # Pull phase metrics (always available via stubbed state tracker)
        # Local imports
        from .qfac_state_tracker import get_qfac_phase_metrics

        phases = get_qfac_phase_metrics()

        # Pull compression performance snapshot from analyzer
        performance = await self.analyzer.monitor_compression_performance()

        return {
            "status": "ok",
            "mode": self._mode,
            "started": self._started,
            "timestamp": time.time(),
            "phases": phases,
            "performance": performance,
            "compression_health": performance.get("overall_health", 0.0),
        }


# --- Optional Flask endpoints for external consumers ---

app = Flask(__name__)
qfac_dashboard = Blueprint("qfac_dashboard", __name__)


@app.route("/qfac/metrics")
def qfac_metrics():
    # Local imports
    from .qfac_state_tracker import get_qfac_phase_metrics

    return jsonify(get_qfac_phase_metrics())


# For test compatibility
if __name__ == "__main__":
    app.run()
