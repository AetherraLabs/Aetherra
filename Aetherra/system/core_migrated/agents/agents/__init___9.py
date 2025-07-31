# Lyrixa Agents Package
"""
Modular agent system for Lyrixa AI Assistant
"""

try:
    # Try relative imports first (when used as a package)
    from .agent_base import AgentBase, AgentResponse
    from .core_agent import LyrixaAI
    from .escalation_agent import EscalationAgent
    from .goal_agent import GoalAgent
    from .plugin_agent import PluginAgent
    from .reflection_agent import ReflectionAgent
    from .self_evaluation_agent import SelfEvaluationAgent
except ImportError:
    # Fall back to absolute imports (when imported directly)
    try:
        from Aetherra.lyrixa.agents.agent_base import AgentBase, AgentResponse
        from Aetherra.lyrixa.agents.core_agent import LyrixaAI
        from Aetherra.lyrixa.agents.escalation_agent import EscalationAgent
        from Aetherra.lyrixa.agents.goal_agent import GoalAgent
        from Aetherra.lyrixa.agents.plugin_agent import PluginAgent
        from Aetherra.lyrixa.agents.reflection_agent import ReflectionAgent
        from Aetherra.lyrixa.agents.self_evaluation_agent import SelfEvaluationAgent
    except ImportError:
        # If all imports fail, create placeholder classes
        print("⚠️ Using placeholder agent classes")

        class AgentBase:
            def __init__(self, *args, **kwargs):
                pass

        class AgentResponse:
            def __init__(self, message="", confidence=0.5):
                self.message = message
                self.confidence = confidence

        class LyrixaAI(AgentBase):
            def respond(self, message):
                return AgentResponse("I'm processing through my core systems...")

        class EscalationAgent(AgentBase):
            pass

        class GoalAgent(AgentBase):
            pass

        class PluginAgent(AgentBase):
            pass

        class ReflectionAgent(AgentBase):
            pass

        class SelfEvaluationAgent(AgentBase):
            pass

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
