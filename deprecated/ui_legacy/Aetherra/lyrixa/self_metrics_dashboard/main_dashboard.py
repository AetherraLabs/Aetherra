# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
📊 Main Dashboard Module
========================

Main dashboard implementation for the self metrics dashboard.
"""

# Local imports
from . import SelfMetricsDashboard, main_dashboard


def get_main_dashboard_instance() -> SelfMetricsDashboard:
    """Get the main dashboard instance."""
    return main_dashboard


# For compatibility with web interface server imports
MainDashboard = SelfMetricsDashboard
