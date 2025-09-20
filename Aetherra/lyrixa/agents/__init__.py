# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🤖 Lyrixa Agents Module
======================

This module provides the base agent architecture and core agents
for the Aetherra AI OS, including specialized enhanced agents for
specific domain tasks.
"""

# Local imports
from .agent_base import AgentBase

try:
    # Local imports
    from .lyrixa_ai import LyrixaAI
except ImportError:
    LyrixaAI = None

try:
    # Local imports
    from .escalation_agent import EscalationAgent
except ImportError:
    EscalationAgent = None

try:
    # Local imports
    from .goal_agent import GoalAgent
except ImportError:
    GoalAgent = None

# Enhanced Specialized Agents
try:
    # Local imports
    from .data_agent import DataAgent
except ImportError:
    DataAgent = None

try:
    # Local imports
    from .technical_agent import TechnicalAgent
except ImportError:
    TechnicalAgent = None

try:
    # Local imports
    from .support_agent import SupportAgent
except ImportError:
    SupportAgent = None

try:
    # Local imports
    from .security_agent import SecurityAgent
except ImportError:
    SecurityAgent = None

__all__ = [
    "AgentBase",
    "LyrixaAI",
    "EscalationAgent",
    "GoalAgent",
    "DataAgent",
    "TechnicalAgent",
    "SupportAgent",
    "SecurityAgent",
]
