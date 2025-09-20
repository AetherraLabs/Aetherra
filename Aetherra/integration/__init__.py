# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔗 Aetherra Integration Layer
============================
Core integration components for connecting Aetherra with external systems and internal modules.

This package provides:
- Adapters: Interface implementations for different data sources and systems
- Bridges: Communication layers between Aetherra and Lyrixa
- Protocols: Standard communication protocols and message formats
- Monitoring: Integration health and performance monitoring

Key Components:
- AetherraLyrixaBridge: Main communication bridge
- MemoryAdapterImpl: Memory system integration
- Integration protocols and standards
"""

# Standard library imports
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Integration system status
INTEGRATION_SYSTEMS = {
    "adapters": False,
    "bridges": False,
    "protocols": False,
    "monitoring": False,
}


def get_integration_status() -> Dict[str, Any]:
    """Get current integration system status."""
    return {
        "systems": INTEGRATION_SYSTEMS.copy(),
        "total_systems": len(INTEGRATION_SYSTEMS),
        "active_systems": sum(INTEGRATION_SYSTEMS.values()),
        "health": "healthy" if any(INTEGRATION_SYSTEMS.values()) else "inactive",
    }


# Lazy imports for core integration components
def get_aetherra_lyrixa_bridge():
    """Get the main Aetherra-Lyrixa communication bridge."""
    try:
        # Local imports
        from .bridges.aetherra_lyrixa_bridge import AetherraLyrixaBridge

        INTEGRATION_SYSTEMS["bridges"] = True
        return AetherraLyrixaBridge
    except ImportError as e:
        logger.warning(f"Failed to import AetherraLyrixaBridge: {e}")
        return None


def get_memory_adapter():
    """Get the memory adapter implementation."""
    try:
        # Local imports
        from .adapters.memory_adapter_impl import MemoryAdapterImpl

        INTEGRATION_SYSTEMS["adapters"] = True
        return MemoryAdapterImpl
    except ImportError as e:
        logger.warning(f"Failed to import MemoryAdapterImpl: {e}")
        return None


def get_memory_bridge_adapter():
    """Get the memory bridge adapter."""
    try:
        # Local imports
        from .bridges.memory_adapter import MemoryIntegrationAdapter

        INTEGRATION_SYSTEMS["adapters"] = True
        return MemoryIntegrationAdapter
    except ImportError as e:
        logger.warning(f"Failed to import memory bridge adapter: {e}")
        return None


# Initialize integration systems
def initialize_integration_systems():
    """Initialize all integration systems."""
    logger.info("🔗 Initializing Aetherra Integration Layer...")

    # Check adapter availability
    try:
        # Standard library imports
        import importlib.util

        spec = importlib.util.find_spec("Aetherra.integration.adapters")
        if spec is not None:
            INTEGRATION_SYSTEMS["adapters"] = True
            logger.info("✅ Adapters system available")
        else:
            logger.warning("[WARN] Adapters system not available")
    except Exception:
        logger.warning("[WARN] Adapters system not available")

    # Check bridges availability
    try:
        # Standard library imports
        import importlib.util

        spec = importlib.util.find_spec("Aetherra.integration.bridges")
        if spec is not None:
            INTEGRATION_SYSTEMS["bridges"] = True
            logger.info("✅ Bridges system available")
        else:
            logger.warning("[WARN] Bridges system not available")
    except Exception:
        logger.warning("[WARN] Bridges system not available")

    # Check protocols availability
    try:
        # Standard library imports
        import importlib.util

        spec = importlib.util.find_spec("Aetherra.integration.protocols")
        if spec is not None:
            INTEGRATION_SYSTEMS["protocols"] = True
            logger.info("✅ Protocols system available")
        else:
            logger.warning("[WARN] Protocols system not available")
    except Exception:
        logger.warning("[WARN] Protocols system not available")

    # Check monitoring availability
    try:
        # Standard library imports
        import importlib.util

        spec = importlib.util.find_spec("Aetherra.integration.monitoring")
        if spec is not None:
            INTEGRATION_SYSTEMS["monitoring"] = True
            logger.info("✅ Monitoring system available")
        else:
            logger.warning("[WARN] Monitoring system not available")
    except Exception:
        logger.warning("[WARN] Monitoring system not available")

    active_count = sum(INTEGRATION_SYSTEMS.values())
    total_count = len(INTEGRATION_SYSTEMS)
    logger.info(f"🔗 Integration Layer: {active_count}/{total_count} systems active")

    return INTEGRATION_SYSTEMS


# Auto-initialize on import
try:
    initialize_integration_systems()
except Exception as e:
    logger.error(f"❌ Failed to initialize integration systems: {e}")

__all__ = [
    "get_integration_status",
    "get_aetherra_lyrixa_bridge",
    "get_memory_adapter",
    "get_memory_bridge_adapter",
    "initialize_integration_systems",
    "INTEGRATION_SYSTEMS",
]
