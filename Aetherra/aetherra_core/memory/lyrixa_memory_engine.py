# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Lyrixa Memory Engine
=======================
Compatibility alias for Aetherra memory systems.
This provides the LyrixaMemoryEngine interface that plugins expect.
"""

# Local imports
# Import the actual memory engine and create an alias
from .aetherra_memory_engine import AetherraMemoryEngine as LyrixaMemoryEngine
from .enhanced_memory import LyrixaEnhancedMemorySystem

# Re-export for backward compatibility
__all__ = ["LyrixaMemoryEngine", "LyrixaEnhancedMemorySystem"]
