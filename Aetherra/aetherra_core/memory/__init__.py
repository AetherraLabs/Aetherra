# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Package exports for memory module

# Local imports
# Re-export key engines for convenience
from .aetherra_memory_engine import (  # noqa: F401
    AetherraMemoryEngineAdvanced,
    MemorySystemConfig,
)

MEMORY_AVAILABLE = True

__all__ = [
    "MEMORY_AVAILABLE",
    "AetherraMemoryEngineAdvanced",
    "MemorySystemConfig",
]
