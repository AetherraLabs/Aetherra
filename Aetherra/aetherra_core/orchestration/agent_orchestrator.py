"""
DEPRECATED: Aetherra.aetherra_core.orchestration.agent_orchestrator
Use Aetherra.aetherra_core.agents.agent_orchestrator instead.

This module is a thin shim that forwards the canonical AgentOrchestrator and
related symbols, and emits a DeprecationWarning on import.
"""

from __future__ import annotations

# Standard library imports
import logging
import warnings

logger = logging.getLogger(__name__)

warnings.warn(
    (
        "Aetherra.aetherra_core.orchestration.agent_orchestrator is deprecated; "
        "use Aetherra.aetherra_core.agents.agent_orchestrator instead."
    ),
    DeprecationWarning,
    stacklevel=2,
)

# Aetherra imports
# Forward canonical symbols
from Aetherra.aetherra_core.agents.agent_orchestrator import Agent as Agent
from Aetherra.aetherra_core.agents.agent_orchestrator import (  # noqa: E402
    AgentOrchestrator as AgentOrchestrator,
)
from Aetherra.aetherra_core.agents.agent_orchestrator import AgentStatus as AgentStatus
from Aetherra.aetherra_core.agents.agent_orchestrator import Task as Task
from Aetherra.aetherra_core.agents.agent_orchestrator import (
    TaskPriority as TaskPriority,
)
from Aetherra.aetherra_core.agents.agent_orchestrator import TaskStatus as TaskStatus

# Back-compat alias: legacy OrchestratedTask maps to canonical Task
OrchestratedTask = Task

__all__ = [
    "AgentOrchestrator",
    "Agent",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "AgentStatus",
    "OrchestratedTask",
]
