# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Lyrixa Intelligence Module
=========================

Advanced intelligence and meta-reasoning capabilities for Lyrixa.
Includes full AI intelligence integration and consciousness-aware processing.
"""

# Local imports
from .meta_reasoning import *

# Import the full intelligence system
try:
    # Local imports
    from .lyrixa_full_intelligence import LyrixaIntelligenceCore

    __all__ = ["LyrixaIntelligenceCore"]
except ImportError:
    LyrixaIntelligenceCore = None
    __all__ = []

# Add meta_reasoning exports to __all__
try:
    # Local imports
    from .meta_reasoning import __all__ as meta_reasoning_all

    __all__.extend(meta_reasoning_all)
except (ImportError, AttributeError):
    pass
