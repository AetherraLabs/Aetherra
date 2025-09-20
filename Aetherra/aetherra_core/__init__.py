#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌌 Aetherra Core Package
========================
Core modules for the Aetherra AI Operating System.

This package contains the fundamental components that power Aetherra's
intelligence, memory, orchestration, and cognitive systems.
"""

__version__ = "1.0.0"
__author__ = "AetherraLabs"
__email__ = "contact@aetherralabs.com"

# Standard library imports
# Core module imports with graceful fallbacks
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import core components with fallbacks
try:
    # Aetherra imports
    from Aetherra.aetherra_core import memory  # noqa: F401

    MEMORY_AVAILABLE = True
except ImportError as e:
    logger.debug(f"Memory system not available: {e}")
    MEMORY_AVAILABLE = False

try:
    # Aetherra imports
    from Aetherra.aetherra_core import engine  # noqa: F401

    ENGINE_AVAILABLE = True
except ImportError as e:
    logger.debug(f"Engine system not available: {e}")
    ENGINE_AVAILABLE = False

try:
    # Aetherra imports
    from Aetherra.aetherra_core import orchestration  # noqa: F401

    ORCHESTRATION_AVAILABLE = True
except ImportError as e:
    logger.debug(f"Orchestration system not available: {e}")
    ORCHESTRATION_AVAILABLE = False

try:
    # Aetherra imports
    from Aetherra.aetherra_core import plugins  # noqa: F401

    PLUGINS_AVAILABLE = True
except ImportError as e:
    logger.debug(f"Plugin system not available: {e}")
    PLUGINS_AVAILABLE = False

try:
    # Aetherra imports
    from Aetherra.aetherra_core import config  # noqa: F401

    CONFIG_AVAILABLE = True
except ImportError as e:
    logger.debug(f"Config system not available: {e}")
    CONFIG_AVAILABLE = False

# Availability flags for external components
CORE_SYSTEMS = {
    "memory": MEMORY_AVAILABLE,
    "engine": ENGINE_AVAILABLE,
    "orchestration": ORCHESTRATION_AVAILABLE,
    "plugins": PLUGINS_AVAILABLE,
    "config": CONFIG_AVAILABLE,
}


def get_system_status():
    """Get the status of all core systems."""
    return CORE_SYSTEMS.copy()


def check_dependencies():
    """Check if all required dependencies are available."""
    # Standard library imports
    import importlib.util as _spec

    required = ["asyncio", "json", "logging"]
    return [name for name in required if _spec.find_spec(name) is None]


# Module-level constants
CORE_MODULE_PATH = Path(__file__).parent
PROJECT_ROOT = CORE_MODULE_PATH.parent.parent

# Export main components
__all__ = [
    "get_system_status",
    "check_dependencies",
    "CORE_SYSTEMS",
    "CORE_MODULE_PATH",
    "PROJECT_ROOT",
    "MEMORY_AVAILABLE",
    "ENGINE_AVAILABLE",
    "ORCHESTRATION_AVAILABLE",
    "PLUGINS_AVAILABLE",
    "CONFIG_AVAILABLE",
]
