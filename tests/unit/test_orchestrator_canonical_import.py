import importlib
import sys
import warnings


def test_canonical_import_only():
    # Canonical import must work
    mod = importlib.import_module("Aetherra.aetherra_core.agents.agent_orchestrator")
    assert hasattr(mod, "AgentOrchestrator")
    # Deprecated path should emit DeprecationWarning but still provide the same symbols
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Clear shim module to force re-import and warning emission
        sys.modules.pop("Aetherra.aetherra_core.orchestration.agent_orchestrator", None)
        sh = importlib.import_module(
            "Aetherra.aetherra_core.orchestration.agent_orchestrator"
        )
        assert any(issubclass(x.category, DeprecationWarning) for x in w), (
            "no DeprecationWarning emitted"
        )
        assert hasattr(sh, "AgentOrchestrator")
        assert sh.AgentOrchestrator is mod.AgentOrchestrator
        assert sh.Task is mod.Task
        assert sh.Agent is mod.Agent
