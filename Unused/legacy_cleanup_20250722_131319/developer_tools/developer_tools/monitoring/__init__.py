"""
Aetherra & Lyrixa Developer Tools - Monitoring Package

This package provides comprehensive monitoring and health checking tools for the project.
"""

# Import monitoring tools with error handling
try:
    from .health_dashboard import ProjectHealthDashboard, HealthConfig
    __all__ = ['ProjectHealthDashboard', 'HealthConfig']
except ImportError as e:
    print(f"Warning: Could not import health_dashboard: {e}")
    __all__ = []

try:
    from .error_tracker import ErrorTracker, ErrorConfig
    __all__.extend(['ErrorTracker', 'ErrorConfig'])
except ImportError as e:
    print(f"Warning: Could not import error_tracker: {e}")

try:
    from .performance_profiler import PerformanceProfiler, PerformanceMetrics, ProfileSession
    __all__.extend(['PerformanceProfiler', 'PerformanceMetrics', 'ProfileSession'])
except ImportError as e:
    print(f"Warning: Could not import performance_profiler: {e}")

# Package version
__version__ = "1.0.0"
