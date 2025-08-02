#!/usr/bin/env python3
"""
🔌 Aetherra Orchestration Package
=================================
Task scheduling and system orchestration for Aetherra AI OS.

This package handles the coordination of various system components,
task scheduling, and workflow management.
"""

__version__ = "1.0.0"

# Graceful imports with fallbacks
import logging
logger = logging.getLogger(__name__)

# Try to import scheduler if available
try:
    from .scheduler import AetherraScheduler
    SCHEDULER_AVAILABLE = True
except ImportError as e:
    logger.debug(f"AetherraScheduler not available: {e}")
    SCHEDULER_AVAILABLE = False
    
    # Create a mock class for development
    class AetherraScheduler:
        """Mock AetherraScheduler for development when actual scheduler isn't available."""
        def __init__(self, *args, **kwargs):
            logger.warning("Using mock AetherraScheduler - actual scheduler not available")
        
        async def schedule_task(self, *args, **kwargs):
            return {"status": "mock", "message": "AetherraScheduler not available"}

# Orchestration status
ORCHESTRATION_SYSTEMS = {
    'scheduler': SCHEDULER_AVAILABLE,
}

def get_orchestration_status():
    """Get the status of all orchestration systems."""
    return ORCHESTRATION_SYSTEMS.copy()

# Export main components
__all__ = [
    'AetherraScheduler',
    'get_orchestration_status',
    'ORCHESTRATION_SYSTEMS',
    'SCHEDULER_AVAILABLE',
]
