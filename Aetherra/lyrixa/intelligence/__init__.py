# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Lyrixa Intelligence Module
=========================

Advanced intelligence and meta-reasoning capabilities for Lyrixa.
Includes full AI intelligence integration and consciousness-aware processing.
"""

from .meta_reasoning import (
    ConfidenceLevel,
    DecisionTrace,
    DecisionType,
    MetaReasoningEngine,
)

# Import the full intelligence system
try:
    # Local imports
    from .lyrixa_full_intelligence import LyrixaIntelligenceCore

    __all__ = [
        "ConfidenceLevel",
        "DecisionTrace",
        "DecisionType",
        "LyrixaIntelligenceCore",
        "MetaReasoningEngine",
    ]
except ImportError:
    LyrixaIntelligenceCore = None
    __all__ = [
        "ConfidenceLevel",
        "DecisionTrace",
        "DecisionType",
        "MetaReasoningEngine",
    ]
