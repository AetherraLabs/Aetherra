# Lyrixa Agents Package
"""
Modular agent system for Lyrixa AI Assistant
"""

from .agent_base import AgentBase, AgentResponse
from .core_agent import LyrixaAI
from .escalation_agent import EscalationAgent
from .goal_agent import GoalAgent
from .plugin_agent import PluginAgent
from .reflection_agent import ReflectionAgent
from .self_evaluation_agent import SelfEvaluationAgent

__all__ = [
    "LyrixaAI",
    "GoalAgent",
    "PluginAgent",
    "ReflectionAgent",
    "EscalationAgent",
    "SelfEvaluationAgent",
    "AgentBase",
    "AgentResponse",
]
