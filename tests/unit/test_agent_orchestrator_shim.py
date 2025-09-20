"""Tests for deprecated agent orchestrator shim module.

Ensures that importing the legacy orchestration path emits a DeprecationWarning
and that the forwarded symbols are identical (object identity) to the
canonical implementation under aetherra_core.agents.
"""

from __future__ import annotations

# Standard library imports
import warnings


def test_legacy_orchestration_import_emits_warning_and_forwards_symbols():
    # Import canonical first
    # Aetherra imports
    from Aetherra.aetherra_core.agents.agent_orchestrator import Agent as CanonicalAgent
    from Aetherra.aetherra_core.agents.agent_orchestrator import (
        AgentOrchestrator as CanonicalOrchestrator,  # type: ignore
    )
    from Aetherra.aetherra_core.agents.agent_orchestrator import (
        AgentStatus as CanonicalAgentStatus,
    )
    from Aetherra.aetherra_core.agents.agent_orchestrator import Task as CanonicalTask
    from Aetherra.aetherra_core.agents.agent_orchestrator import (
        TaskPriority as CanonicalTaskPriority,
    )
    from Aetherra.aetherra_core.agents.agent_orchestrator import (
        TaskStatus as CanonicalTaskStatus,
    )

    with warnings.catch_warnings(record=True) as w:  # type: ignore
        warnings.simplefilter("always")
        # Aetherra imports
        from Aetherra.aetherra_core.orchestration.agent_orchestrator import (  # type: ignore  # noqa: E501
            Agent,
            AgentOrchestrator,
            AgentStatus,
            OrchestratedTask,
            Task,
            TaskPriority,
            TaskStatus,
        )

    # Must have at least one DeprecationWarning captured
    assert any(
        isinstance(x.message, DeprecationWarning) for x in w
    ), "Expected DeprecationWarning when importing deprecated orchestrator shim"

    # Identity checks: forwarded symbols should be exactly the same objects
    assert AgentOrchestrator is CanonicalOrchestrator
    assert Agent is CanonicalAgent
    assert Task is CanonicalTask
    assert OrchestratedTask is CanonicalTask  # back-compat alias
    assert TaskPriority is CanonicalTaskPriority
    assert TaskStatus is CanonicalTaskStatus
    assert AgentStatus is CanonicalAgentStatus
