"""
🤖 Lyrixa Agents Module
======================

This module provides the base agent architecture and core agents
for the Aetherra AI OS, including specialized enhanced agents for
specific domain tasks.
"""

from .agent_base import AgentBase

try:
    from .lyrixa_ai import LyrixaAI
except ImportError:
    LyrixaAI = None

try:
    from .escalation_agent import EscalationAgent
except ImportError:
    EscalationAgent = None

try:
    from .goal_agent import GoalAgent
except ImportError:
    GoalAgent = None

# Enhanced Specialized Agents
try:
    from .data_agent import DataAgent
except ImportError:
    DataAgent = None

try:
    from .technical_agent import TechnicalAgent
except ImportError:
    TechnicalAgent = None

try:
    from .support_agent import SupportAgent
except ImportError:
    SupportAgent = None

try:
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
