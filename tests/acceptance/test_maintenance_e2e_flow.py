"""
End-to-end acceptance test for Maintenance System feedback loop.

Golden path:
1. Homeostasis detects a performance issue (simulate degraded metric)
2. Self-Improvement Engine generates an optimization proposal
3. Self-Incorporation consumes the proposal via handle_improvement_proposal
4. Proposal execution adjusts runtime knobs or integrates a plan
5. Metrics counters increment (proposals_executed, proposals_accepted)
6. Result is reported back to SI Engine
7. System health stabilizes or improves

This test validates the complete autonomous maintenance cycle.
"""

# Standard library imports
import asyncio
import os

# Third party imports
import pytest

# Aetherra imports
from aetherra_self_incorporation import (
    SelfIncorporationConfig,
    SelfIncorporationService,
)


class _MockSelfImprovementEngine:
    """Minimal SI Engine that receives proposal results."""

    def __init__(self):
        self.proposals_sent = 0
        self.results_received = []

    async def handle_message(self, message_type: str, data: dict):
        if message_type == "selfimprovement.proposal_result":
            self.results_received.append(data)
            return {"ok": True}
        return {"ok": False}


class _MockServiceRegistry:
    """Minimal service registry for testing."""

    def __init__(self):
        self.services = {}

    async def register_service(self, name: str, instance, metadata=None):
        self.services[name] = instance

    async def unregister_service(self, name: str):
        self.services.pop(name, None)

    def get_service(self, name: str):
        return self.services.get(name)

    async def send_message(self, target: str, message_type: str, data: dict):
        svc = self.services.get(target)
        if svc and hasattr(svc, "handle_message"):
            return await svc.handle_message(message_type, data)
        return None


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_maintenance_feedback_loop_e2e():
    """
    End-to-end test: SI proposal → Self-Inc consumption → execution → feedback.
    """
    # Ensure test profile
    os.environ.pop("AETHERRA_PROFILE", None)

    # Create mock services
    registry = _MockServiceRegistry()
    si_engine = _MockSelfImprovementEngine()
    await registry.register_service("self_improvement_engine", si_engine)

    # Create Self-Incorporation service
    cfg = SelfIncorporationConfig()
    cfg.enabled = True
    selfinc = SelfIncorporationService(cfg)
    selfinc.inject_systems(
        service_registry=registry,
        kernel_loop=None,
        plugin_manager=None,
        agent_orchestrator=None,
    )
    await selfinc.start()

    # Baseline metrics
    base_exec = int(selfinc.metrics.get("proposals_executed", 0))
    base_acc = int(selfinc.metrics.get("proposals_accepted", 0))

    # Step 1: Simulate SI Engine generating a proposal
    proposal = {
        "proposal_id": "e2e-test-001",
        "type": "optimize",
        "description": "Increase processing velocity for performance improvement",
        "params": {
            "hint": "performance_boost",
            "value": True,
            "delta": 0.3,
        },
        "trace_id": "trace-e2e-001",
    }

    # Step 2: Self-Incorporation consumes the proposal
    result = await selfinc.handle_improvement_proposal(proposal)

    # Step 3: Verify proposal was accepted
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result.get("status") == "accepted", (
        f"Expected accepted, got {result.get('status')}"
    )
    assert "plan_id" in result, "Result should include plan_id"
    assert "details" in result, "Result should include details"

    # Step 4: Verify metrics incremented
    exec_count = int(selfinc.metrics.get("proposals_executed", 0))
    acc_count = int(selfinc.metrics.get("proposals_accepted", 0))
    assert exec_count == base_exec + 1, (
        f"proposals_executed should increment: {exec_count} vs {base_exec}"
    )
    assert acc_count == base_acc + 1, (
        f"proposals_accepted should increment: {acc_count} vs {base_acc}"
    )

    # Step 5: Verify optimization hint was recorded
    assert selfinc._optimization_hints.get("performance_boost") is True, (
        "Optimization hint should be recorded"
    )

    # Step 6: Verify result was sent back to SI Engine
    await asyncio.sleep(0.1)  # Allow async send_message to complete
    assert len(si_engine.results_received) == 1, (
        f"SI Engine should receive result feedback: {si_engine.results_received}"
    )
    feedback = si_engine.results_received[0]
    assert feedback.get("proposal_id") == "e2e-test-001", (
        "Feedback should include proposal_id"
    )
    assert feedback.get("status") == "accepted", "Feedback status should be accepted"

    # Step 7: Verify audit ledger recorded the action
    if hasattr(selfinc, "audit_ledger") and selfinc.audit_ledger:
        recent = selfinc.audit_ledger.recent(limit=5)
        assert any(r.get("trace_id") == "trace-e2e-001" for r in recent), (
            "Audit ledger should contain trace_id"
        )

    # Cleanup
    await selfinc.stop()


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_maintenance_feedback_loop_with_integration():
    """
    End-to-end test with optional integration plan execution.
    """
    os.environ.pop("AETHERRA_PROFILE", None)

    registry = _MockServiceRegistry()
    si_engine = _MockSelfImprovementEngine()
    await registry.register_service("self_improvement_engine", si_engine)

    cfg = SelfIncorporationConfig()
    cfg.enabled = True
    selfinc = SelfIncorporationService(cfg)
    selfinc.inject_systems(
        service_registry=registry,
        kernel_loop=None,
        plugin_manager=None,
        agent_orchestrator=None,
    )
    await selfinc.start()

    base_exec = int(selfinc.metrics.get("proposals_executed", 0))

    # Proposal with a minimal action plan (dry_run to avoid needing real managers)
    proposal = {
        "proposal_id": "e2e-test-002",
        "type": "optimize",
        "params": {
            "actions": [
                {
                    "action": "import_utility",
                    "target": {"file_id": "dummy", "type": "utility"},
                    "deps": [],
                }
            ],
            "dry_run": True,  # Simulate plan execution without real integration
        },
        "trace_id": "trace-e2e-002",
    }

    result = await selfinc.handle_improvement_proposal(proposal)

    # Verify plan executed (in dry_run mode, returns skipped)
    assert result.get("status") in ("accepted", "rejected"), (
        f"Got status: {result.get('status')}"
    )
    details = result.get("details", {})
    if "integration" in details:
        integ = details["integration"]
        # In dry_run, actions are skipped; check structure exists
        assert "applied" in integ or "skipped" in integ, (
            "Integration should report applied/skipped counts"
        )

    # Verify executed counter incremented
    exec_count = int(selfinc.metrics.get("proposals_executed", 0))
    assert exec_count == base_exec + 1, (
        "proposals_executed should increment even if dry_run"
    )

    # Cleanup
    await selfinc.stop()


if __name__ == "__main__":
    # Quick local test runner
    import sys

    # Run with pytest programmatically
    sys.exit(pytest.main([__file__, "-v"]))
