"""
Neuroplex UI Components - Panels Package
========================================

Modular panels for the Neuroplex interface.
"""

# Import all panel classes
from .goal_tracking import GoalTrackingPanel
from .llm_provider import LLMProviderPanel
from .memory_visualization import MemoryVisualizationPanel
from .natural_language import NaturalLanguagePanel
from .performance_monitor import PerformanceMonitorPanel
from .plugin_manager import PluginManagerPanel

# Export all panels
__all__ = [
    "LLMProviderPanel",
    "MemoryVisualizationPanel",
    "PerformanceMonitorPanel",
    "GoalTrackingPanel",
    "PluginManagerPanel",
    "NaturalLanguagePanel",
]
