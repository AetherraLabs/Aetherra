#!/usr/bin/env python3
"""
📊 Self-Metrics Dashboard Package
===============================

Real-time monitoring of Lyrixa's cognitive performance, ethical alignment,
and growth trajectory. Provides comprehensive introspection capabilities.

Components:
- main_dashboard: Core dashboard functionality
- memory_continuity_score: Memory coherence tracking
- growth_trajectory_monitor: Learning progress monitoring
"""

# Import main components
try:
    from .growth_trajectory_monitor import GrowthTrajectoryMonitor
    from .main_dashboard import SelfMetricsDashboard
    from .memory_continuity_score import MemoryContinuityTracker

    __all__ = [
        "SelfMetricsDashboard",
        "MemoryContinuityTracker",
        "GrowthTrajectoryMonitor",
    ]

    SELF_METRICS_AVAILABLE = True

except ImportError as e:
    print(f"⚠️ Self-metrics components not fully available: {e}")
    SELF_METRICS_AVAILABLE = False

    # Provide fallback
    __all__ = []
