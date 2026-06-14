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

# Use path-based availability checks to avoid cross-thread import deadlocks.
# Eager submodule imports here caused a Python 3.13 _DeadlockError when
# server.py imported engine on the main thread while the launcher loaded
# memory on the background thread — both trying to acquire each other's locks.
import logging
from pathlib import Path as _Path

logger = logging.getLogger(__name__)

_CORE_DIR = _Path(__file__).parent
MEMORY_AVAILABLE = (_CORE_DIR / "memory" / "__init__.py").exists()
ENGINE_AVAILABLE = (_CORE_DIR / "engine" / "__init__.py").exists()
ORCHESTRATION_AVAILABLE = (_CORE_DIR / "orchestration" / "__init__.py").exists()
PLUGINS_AVAILABLE = (_CORE_DIR / "plugins" / "__init__.py").exists()
CONFIG_AVAILABLE = (_CORE_DIR / "config" / "__init__.py").exists()

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
CORE_MODULE_PATH = _Path(__file__).parent
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
