# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Consciousness Core Module
=========================

Always-on awareness system. No flags, no simulation.
Real perception → felt experience → narrative continuity.
"""

from .consciousness_core import ConsciousnessCore
from .think_stream import ThinkStream, get_think_stream
from .types import (
    Event,
    Focus,
    Intent,
    LedgerEntry,
    NarrativeMoment,
    Plan,
    PlanStep,
    QualiaVector,
)

__all__ = [
    "ConsciousnessCore",
    "ThinkStream",
    "get_think_stream",
    "Event",
    "Focus",
    "Intent",
    "LedgerEntry",
    "NarrativeMoment",
    "Plan",
    "PlanStep",
    "QualiaVector",
]
