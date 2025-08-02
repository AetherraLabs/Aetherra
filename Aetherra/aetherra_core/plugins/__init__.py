#!/usr/bin/env python3
"""
🔌 Aetherra Plugins Package
===========================
Plugin system and management for Aetherra AI OS.

This package manages the loading, execution, and coordination
of various plugins that extend Aetherra's capabilities.
"""

__version__ = "1.0.0"

# Graceful imports with fallbacks
import logging
logger = logging.getLogger(__name__)

# Try to import plugin manager if available
try:
    from .plugin_manager import PluginManager
    PLUGIN_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.debug(f"PluginManager not available: {e}")
    PLUGIN_MANAGER_AVAILABLE = False
    
    # Create a mock class for development
    class PluginManager:
        """Mock PluginManager for development when actual manager isn't available."""
        def __init__(self, *args, **kwargs):
            logger.warning("Using mock PluginManager - actual manager not available")
        
        async def load_plugin(self, *args, **kwargs):
            return {"status": "mock", "message": "PluginManager not available"}

# Plugin status
PLUGIN_SYSTEMS = {
    'manager': PLUGIN_MANAGER_AVAILABLE,
}

def get_plugin_status():
    """Get the status of all plugin systems."""
    return PLUGIN_SYSTEMS.copy()

# Export main components
__all__ = [
    'PluginManager',
    'get_plugin_status',
    'PLUGIN_SYSTEMS',
    'PLUGIN_MANAGER_AVAILABLE',
]
