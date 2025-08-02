"""
📊 Main Dashboard Module
========================

Main dashboard implementation for the self metrics dashboard.
"""

from . import SelfMetricsDashboard, main_dashboard


def get_main_dashboard_instance() -> SelfMetricsDashboard:
    """Get the main dashboard instance."""
    return main_dashboard


# For compatibility with web interface server imports
MainDashboard = SelfMetricsDashboard
