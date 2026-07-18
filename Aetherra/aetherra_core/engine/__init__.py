#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Aetherra Engine Package
==========================
Core intelligence and processing engine for Aetherra AI OS.

This package contains the main processing engines that power
Aetherra's cognitive capabilities and supporting intelligence modules.
"""

__version__ = "1.0.0"

# Standard library imports
# Graceful imports with fallbacks
import logging

logger = logging.getLogger(__name__)

# Try to import aetherra_engine if available.
try:
    from .aetherra_engine import AetherraEngine

    AETHERRA_ENGINE_AVAILABLE = True
    AETHERRA_ENGINE_IMPORT_ERROR = None
except ImportError as exc:
    logger.debug("AetherraEngine import unavailable: %s", type(exc).__name__)
    AETHERRA_ENGINE_AVAILABLE = False
    AETHERRA_ENGINE_IMPORT_ERROR = "engine_import_unavailable"

    class AetherraEngine:
        """Unavailable Engine placeholder that fails closed."""

        def __init__(self, *args, **kwargs):
            raise RuntimeError("AetherraEngine unavailable: engine_import_unavailable")

        async def process(self, *args, **kwargs):
            raise RuntimeError("AetherraEngine unavailable: engine_import_unavailable")


# Try to import intelligence modules
try:
    INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    logger.debug("Intelligence modules not available: %s", type(e).__name__)
    INTELLIGENCE_AVAILABLE = False

try:
    from .readiness import (
        AI_READINESS_CONTRACT_VERSION,
        assess_ai_readiness,
        build_ai_readiness_payload,
    )
except ImportError as e:
    logger.debug("AI readiness contract not available: %s", type(e).__name__)
    AI_READINESS_CONTRACT_VERSION = "unavailable"
    assess_ai_readiness = None
    build_ai_readiness_payload = None

# Engine status
ENGINE_SYSTEMS = {
    "aetherra": AETHERRA_ENGINE_AVAILABLE,
    "intelligence": INTELLIGENCE_AVAILABLE,
}


def get_engine_status():
    """Get the status of all engine systems."""
    return {
        **ENGINE_SYSTEMS,
        "engine_import_error": AETHERRA_ENGINE_IMPORT_ERROR,
    }


# Export main components
__all__ = [
    "AetherraEngine",
    "get_engine_status",
    "ENGINE_SYSTEMS",
    "AETHERRA_ENGINE_AVAILABLE",
    "AETHERRA_ENGINE_IMPORT_ERROR",
    "INTELLIGENCE_AVAILABLE",
    "AI_READINESS_CONTRACT_VERSION",
    "assess_ai_readiness",
    "build_ai_readiness_payload",
]
