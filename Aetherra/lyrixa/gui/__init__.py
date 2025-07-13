"""
Lyrixa GUI Module

Advanced GUI components for the Lyrixa AI Assistant, including:
- Enhanced Lyrixa Window (Main GUI)
- Analytics Dashboard
- Suggestion Notifications
- Configuration Manager
- Performance Monitor

Integrates with the Enhanced Lyrixa GUI and Anticipation Engine.
"""

from .analytics_dashboard import AnalyticsDashboard
from .configuration_manager import ConfigurationManager
from .enhanced_lyrixa import EnhancedLyrixaWindow
from .performance_monitor import PerformanceMonitor
from .suggestion_notifications import SuggestionNotificationSystem

__all__ = [
    "EnhancedLyrixaWindow",
    "AnalyticsDashboard",
    "SuggestionNotificationSystem",
    "ConfigurationManager",
    "PerformanceMonitor",
]

__version__ = "3.0.0"
__author__ = "Aetherra Project"
__description__ = "Advanced GUI components for Lyrixa AI Assistant"
