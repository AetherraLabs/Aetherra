#!/usr/bin/env python3
"""
🧠 Aetherra Engine Package
==========================
Core intelligence and processing engine for Aetherra AI OS.

This package contains the main processing engines that power
Aetherra's cognitive capabilities, including the Lyrixa engine
and various intelligence modules.
"""

__version__ = "1.0.0"

# Graceful imports with fallbacks
import logging

logger = logging.getLogger(__name__)

# Try to import aetherra_engine if available
try:
    from .aetherra_engine import AetherraEngine

    AETHERRA_ENGINE_AVAILABLE = True
except ImportError as e:
    logger.debug(f"AetherraEngine not available: {e}")
    AETHERRA_ENGINE_AVAILABLE = False

    # Create a mock class for development
    class AetherraEngine:
        """Mock AetherraEngine for development when actual engine isn't available."""

        def __init__(self, *args, **kwargs):
            logger.warning("Using mock LyrixaEngine - actual engine not available")

        async def process(self, *args, **kwargs):
            return {"status": "mock", "message": "LyrixaEngine not available"}


# Try to import intelligence modules
try:
    from aetherra_core.engine import intelligence

    INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    logger.debug(f"Intelligence modules not available: {e}")
    INTELLIGENCE_AVAILABLE = False

# Engine status
ENGINE_SYSTEMS = {
    "aetherra": AETHERRA_ENGINE_AVAILABLE,
    "intelligence": INTELLIGENCE_AVAILABLE,
}


def get_engine_status():
    """Get the status of all engine systems."""
    return ENGINE_SYSTEMS.copy()


# Export main components
__all__ = [
    "AetherraEngine",
    "get_engine_status",
    "ENGINE_SYSTEMS",
    "AETHERRA_ENGINE_AVAILABLE",
    "INTELLIGENCE_AVAILABLE",
]
