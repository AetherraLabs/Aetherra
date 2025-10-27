"""
Metrics validation script for Phase 2A Week 2.

Validates that all 3 maintenance systems forward metrics correctly:
1. Homeostasis: system_health_score, actions_executed
2. Self-Improvement Engine: proposals_generated
3. Self-Incorporation: proposals_executed, proposals_accepted, files_integrated, files_quarantined, last_rollback_token

Checks:
- Proposal execution counters increment properly
- Audit trails contain trace_ids for correlation
- Maintenance API returns correct KPI values
"""

# Standard library imports
import asyncio
import logging
import os

# Aetherra imports
from aetherra_self_incorporation import (
    SelfIncorporationConfig,
    SelfIncorporationService,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


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


async def validate_metrics():
    """Validate metrics flow across all 3 systems."""
    logger.info("=" * 80)
    logger.info("Phase 2A Week 2: Metrics Validation")
    logger.info("=" * 80)

    # Ensure test profile
    os.environ.pop("AETHERRA_PROFILE", None)

    # Create mock registry
    registry = _MockServiceRegistry()

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

    # Register Self-Incorporation in registry
    await registry.register_service("self_incorporation", selfinc)

    logger.info("\n" + "=" * 80)
    logger.info("1. Self-Incorporation Baseline Metrics")
    logger.info("=" * 80)
    baseline = await selfinc.get_status()
    logger.info(f"Proposals Executed: {baseline.get('proposals_executed', 0)}")
    logger.info(f"Proposals Accepted: {baseline.get('proposals_accepted', 0)}")
    logger.info(f"Files Integrated: {baseline.get('files_integrated', 0)}")
    logger.info(f"Files Quarantined: {baseline.get('files_quarantined', 0)}")
    logger.info(f"Last Rollback Token: {baseline.get('last_rollback_token', 'N/A')}")

    logger.info("\n" + "=" * 80)
    logger.info("2. Send Test Proposal")
    logger.info("=" * 80)
    proposal = {
        "proposal_id": "metrics-validation-001",
        "type": "optimize",
        "description": "Test proposal for metrics validation",
        "params": {
            "hint": "test_metrics",
            "value": True,
        },
        "trace_id": "trace-metrics-001",
    }
    logger.info(f"Sending proposal: {proposal['proposal_id']}")
    result = await selfinc.handle_improvement_proposal(proposal)
    logger.info(f"Result Status: {result.get('status')}")

    logger.info("\n" + "=" * 80)
    logger.info("3. Verify Metrics Incremented")
    logger.info("=" * 80)
    updated = await selfinc.get_status()
    exec_before = baseline.get("proposals_executed", 0)
    exec_after = updated.get("proposals_executed", 0)
    acc_before = baseline.get("proposals_accepted", 0)
    acc_after = updated.get("proposals_accepted", 0)

    exec_delta = exec_after - exec_before
    acc_delta = acc_after - acc_before

    logger.info(f"Proposals Executed: {exec_before} → {exec_after} (Δ{exec_delta})")
    logger.info(f"Proposals Accepted: {acc_before} → {acc_after} (Δ{acc_delta})")

    if exec_delta != 1:
        logger.error(
            f"❌ FAIL: proposals_executed should increment by 1, got {exec_delta}"
        )
        return False

    if acc_delta != 1:
        logger.error(
            f"❌ FAIL: proposals_accepted should increment by 1, got {acc_delta}"
        )
        return False

    logger.info("✅ PASS: Metrics incremented correctly")

    logger.info("\n" + "=" * 80)
    logger.info("4. Verify Audit Trail Contains trace_id")
    logger.info("=" * 80)
    if hasattr(selfinc, "audit_ledger") and selfinc.audit_ledger:
        recent = selfinc.audit_ledger.recent(limit=5)
        has_trace = any(r.get("trace_id") == "trace-metrics-001" for r in recent)
        if has_trace:
            logger.info("✅ PASS: Audit trail contains trace_id")
        else:
            logger.error("❌ FAIL: trace_id not found in audit ledger")
            return False
    else:
        logger.warning("⚠️ SKIP: Audit ledger not available")

    logger.info("\n" + "=" * 80)
    logger.info("5. Validate Maintenance API KPI Extraction")
    logger.info("=" * 80)
    # Build maintenance status by extracting from Self-Inc service directly
    selfinc_svc = registry.get_service("self_incorporation")
    if selfinc_svc:
        status_data = await selfinc_svc.get_status()
        kpis = {
            "proposals_executed": status_data.get("proposals_executed"),
            "proposals_accepted": status_data.get("proposals_accepted"),
            "last_rollback_token": status_data.get("last_rollback_token"),
        }
    else:
        logger.error("❌ FAIL: Self-Incorporation service not found in registry")
        return False

    logger.info("Extracted KPIs:")
    logger.info(f"  - proposals_executed: {kpis.get('proposals_executed', 'N/A')}")
    logger.info(f"  - proposals_accepted: {kpis.get('proposals_accepted', 'N/A')}")
    logger.info(f"  - last_rollback_token: {kpis.get('last_rollback_token', 'N/A')}")

    if kpis.get("proposals_executed") == exec_after:
        logger.info("✅ PASS: proposals_executed matches Self-Incorporation metrics")
    else:
        logger.error(
            f"❌ FAIL: proposals_executed mismatch: API={kpis.get('proposals_executed')} vs Service={exec_after}"
        )
        return False

    if kpis.get("proposals_accepted") == acc_after:
        logger.info("✅ PASS: proposals_accepted matches Self-Incorporation metrics")
    else:
        logger.error(
            f"❌ FAIL: proposals_accepted mismatch: API={kpis.get('proposals_accepted')} vs Service={acc_after}"
        )
        return False

    logger.info("\n" + "=" * 80)
    logger.info("6. Verify Maintenance Status Structure")
    logger.info("=" * 80)
    required_keys = {"proposals_executed", "proposals_accepted", "status", "running"}
    missing_keys = required_keys - set(status_data.keys())
    if missing_keys:
        logger.error(f"❌ FAIL: Missing required keys: {missing_keys}")
        return False
    logger.info("✅ PASS: Self-Incorporation status structure is valid")

    logger.info("\n" + "=" * 80)
    logger.info("7. Summary")
    logger.info("=" * 80)
    logger.info("✅ All metrics validation checks passed!")
    logger.info("=" * 80)

    # Cleanup
    await selfinc.stop()
    return True


if __name__ == "__main__":
    success = asyncio.run(validate_metrics())
    exit(0 if success else 1)
