# SPDX-License-Identifier: GPL-3.0-or-later
"""
STORM Shadow Mode Deployment Helper

Automates Phase 1 (shadow mode) deployment of STORM:
- Verifies environment configuration
- Checks STORM initialization
- Validates metrics endpoint
- Runs smoke tests
- Provides deployment status report

Usage:
    python tools/deploy_storm_shadow.py [--check-only]
"""

import asyncio
import hashlib
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

METRICS_ENDPOINT = "http://localhost:3001/metrics"


def _deployment_capability_checker(requester: str, capability: str) -> bool:
    if requester == "maintenance":
        return capability in {
            "maintenance:deploy",
            "memory:write",
            "network:outbound",
        }

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _guardian_preflight_full_validation():
    from Aetherra.guardian.core import evaluate_intent
    from Aetherra.guardian.models import IntentDeclaration

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None

    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.deployment_gate",
            target="maintenance:storm_shadow_deployment",
            purpose="Validate STORM shadow-mode deployment readiness",
            capabilities=(
                "maintenance:deploy",
                "memory:write",
                "network:outbound",
            ),
            expected_outcome="STORM shadow-mode smoke validation and metrics readiness are checked",
            reversible=True,
            rollback_plan=(
                "Remove validation memory entries tagged deployment/test if cleanup is required"
            ),
            metadata={
                "check_only": False,
                "storm_env_enabled": os.getenv("AETHERRA_MEMORY_STORM", "0") == "1",
                "shadow_mode_env": os.getenv("AETHERRA_STORM_SHADOW_MODE", "0") == "1",
                "metrics_endpoint_hash": _hash_value(METRICS_ENDPOINT),
            },
        ),
        approval_id=approval_id,
        capability_checker=_deployment_capability_checker,
    )


def print_header(text: str) -> None:
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_status(check: str, passed: bool, detail: str = "") -> None:
    """Print check status with optional detail"""
    icon = "✅" if passed else "❌"
    status = "PASS" if passed else "FAIL"
    print(f"{icon} {check:.<50} {status}")
    if detail:
        print(f"   └─ {detail}")


def check_environment() -> tuple[bool, list[str]]:
    """Verify STORM environment variables"""
    print_header("Environment Configuration Check")

    issues = []
    all_good = True

    # Required variables
    storm_enabled = os.getenv("AETHERRA_MEMORY_STORM", "0") == "1"
    shadow_mode = os.getenv("AETHERRA_STORM_SHADOW_MODE", "0") == "1"

    print_status(
        "AETHERRA_MEMORY_STORM=1",
        storm_enabled,
        os.getenv("AETHERRA_MEMORY_STORM", "not set"),
    )
    if not storm_enabled:
        issues.append("Set AETHERRA_MEMORY_STORM=1 to enable STORM")
        all_good = False

    print_status(
        "AETHERRA_STORM_SHADOW_MODE=1",
        shadow_mode,
        os.getenv("AETHERRA_STORM_SHADOW_MODE", "not set"),
    )
    if not shadow_mode:
        issues.append("Set AETHERRA_STORM_SHADOW_MODE=1 for shadow mode")
        all_good = False

    # Optional variables (show current values)
    ot_backend = os.getenv("AETHERRA_STORM_OT_BACKEND", "auto")
    tt_rank = os.getenv("AETHERRA_STORM_TT_MAX_RANK", "32")
    k_coarse = os.getenv("AETHERRA_STORM_K_COARSE", "64")

    print("\nOptional Settings:")
    print(f"  - OT Backend: {ot_backend}")
    print(f"  - TT Max Rank: {tt_rank}")
    print(f"  - K Coarse: {k_coarse}")

    return all_good, issues


def check_storm_config() -> tuple[bool, list[str]]:
    """Verify STORM configuration loads correctly"""
    print_header("STORM Configuration Check")

    issues = []

    try:
        from Aetherra.aetherra_core.memory.storm.engine import StormConfig

        cfg = StormConfig.from_env()

        print_status("STORM config loaded", True)
        print_status("STORM enabled", cfg.enabled, f"enabled={cfg.enabled}")
        print_status("Shadow mode", cfg.shadow_mode, f"shadow_mode={cfg.shadow_mode}")
        print_status("OT backend", True, f"backend={cfg.ot_backend}")
        print_status("TT max rank", True, f"rank={cfg.tt_max_rank}")

        if not cfg.enabled:
            issues.append("STORM is not enabled in config")
            return False, issues

        if not cfg.shadow_mode:
            issues.append("Shadow mode is not enabled in config")
            return False, issues

        return True, issues

    except Exception as e:
        print_status("STORM config loaded", False, f"Error: {e}")
        issues.append(f"Failed to load STORM config: {e}")
        return False, issues


async def check_memory_engine() -> tuple[bool, list[str]]:
    """Verify memory engine initializes with STORM"""
    print_header("Memory Engine Initialization Check")

    issues = []

    try:
        from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
            AetherraMemoryEngineAdvanced,
        )

        engine = AetherraMemoryEngineAdvanced()

        print_status("Memory engine initialized", True)

        # Check STORM engine
        has_storm = engine._storm_engine is not None
        print_status("STORM engine attached", has_storm)

        if not has_storm:
            issues.append("STORM engine not attached to memory engine")
            return False, issues

        # Check shadow mode
        in_shadow = engine._storm_engine.config.shadow_mode if has_storm else False
        print_status("Shadow mode active", in_shadow, f"shadow_mode={in_shadow}")

        if not in_shadow:
            issues.append("Shadow mode not active in STORM engine")
            return False, issues

        return True, issues

    except Exception as e:
        print_status("Memory engine initialized", False, f"Error: {e}")
        issues.append(f"Failed to initialize memory engine: {e}")
        return False, issues


async def run_smoke_test() -> tuple[bool, list[str]]:
    """Run basic STORM smoke test"""
    print_header("STORM Smoke Test")

    issues = []

    try:
        from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
            AetherraMemoryEngineAdvanced,
        )

        engine = AetherraMemoryEngineAdvanced()

        # Store test memory
        print("  Storing test memory...")
        await engine.remember(
            content="STORM shadow mode deployment test memory",
            tags=["deployment", "test"],
            category="validation",
        )
        print_status("Store memory", True)

        # Recall with hybrid strategy (should trigger shadow)
        print("  Recalling with storm_hybrid...")
        result = await engine.recall_typed(
            query="deployment test",
            recall_strategy="storm_hybrid",
            limit=5,
        )

        print_status(
            "Recall completed",
            True,
            f"source={result.source}, items={len(result.items)}",
        )

        # In shadow mode, source should be baseline (hybrid/base)
        is_baseline = result.source in ("base", "hybrid")
        print_status(
            "Returns baseline (shadow mode)", is_baseline, f"source={result.source}"
        )

        if not is_baseline:
            issues.append(
                f"Expected baseline source in shadow mode, got: {result.source}"
            )
            return False, issues

        # Check metadata exists
        has_metadata = result.metadata is not None
        print_status("Metadata present", has_metadata)

        if not has_metadata:
            issues.append("Metadata missing from recall result")

        return True, issues

    except Exception as e:
        print_status("Smoke test", False, f"Error: {e}")
        issues.append(f"Smoke test failed: {e}")
        return False, issues


def check_metrics_available() -> tuple[bool, list[str]]:
    """Check if STORM metrics are available"""
    print_header("Metrics Availability Check")

    issues = []

    try:
        import requests

        # Try to reach metrics endpoint
        response = requests.get(METRICS_ENDPOINT, timeout=5)

        if response.status_code == 200:
            print_status(
                "Metrics endpoint accessible", True, METRICS_ENDPOINT
            )

            # Check for STORM metrics
            metrics_text = response.text
            has_storm_metrics = "storm_recalls_total" in metrics_text

            print_status("STORM metrics present", has_storm_metrics)

            if not has_storm_metrics:
                issues.append("STORM metrics not found in /metrics endpoint")
                print("   ℹ️  Note: Metrics may appear after first STORM recall")

            return True, []  # Don't fail if metrics not present yet

        print_status(
            "Metrics endpoint accessible", False, f"Status: {response.status_code}"
        )
        issues.append(f"Metrics endpoint returned {response.status_code}")
        print("   ℹ️  Start Hub first: python aetherra_hub_server.py")
        return False, issues

    except requests.exceptions.ConnectionError:
        print_status("Metrics endpoint accessible", False, "Connection refused")
        print("   ℹ️  Hub not running. Start with: python aetherra_hub_server.py")
        return False, ["Hub not running"]

    except Exception as e:
        print_status("Metrics endpoint accessible", False, f"Error: {e}")
        issues.append(f"Failed to check metrics: {e}")
        return False, issues


def print_deployment_summary(all_checks: dict[str, bool]) -> None:
    """Print final deployment summary"""
    print_header("Deployment Summary")

    all_passed = all(all_checks.values())

    for check, passed in all_checks.items():
        icon = "✅" if passed else "❌"
        print(f"{icon} {check}")

    print()

    if all_passed:
        print("🎉 All checks passed! STORM shadow mode is ready.")
        print("\n📋 Next Steps:")
        print("   1. Start Hub: python aetherra_hub_server.py")
        print("   2. Monitor metrics: curl http://localhost:3001/metrics | grep storm")
        print("   3. Check status: curl http://localhost:3001/api/memory/status")
        print("   4. Review docs/STORM_DEPLOYMENT_CHECKLIST.md for Phase 1 monitoring")
    else:
        print("⚠️  Some checks failed. Please resolve issues before deploying.")
        print("\n📋 See docs/STORM_DEPLOYMENT_CHECKLIST.md for detailed instructions")


async def main(check_only: bool = False) -> int:
    """Main deployment check"""
    print_header("STORM Shadow Mode Deployment")
    print("Phase 1: Shadow Mode (Safe Production Testing)")
    print(f"Mode: {'Check Only' if check_only else 'Full Validation'}")

    all_checks = {}

    # 1. Environment check
    env_ok, env_issues = check_environment()
    all_checks["Environment Configuration"] = env_ok

    if env_issues:
        print("\n⚠️  Issues found:")
        for issue in env_issues:
            print(f"   - {issue}")

    if not env_ok:
        print("\n❌ Environment not configured correctly. Stopping.")
        print_deployment_summary(all_checks)
        return 1

    # 2. STORM config check
    config_ok, config_issues = check_storm_config()
    all_checks["STORM Configuration"] = config_ok

    if config_issues:
        print("\n⚠️  Issues found:")
        for issue in config_issues:
            print(f"   - {issue}")

    if not config_ok:
        print("\n❌ STORM configuration failed. Stopping.")
        print_deployment_summary(all_checks)
        return 1

    # 3. Memory engine check
    engine_ok, engine_issues = await check_memory_engine()
    all_checks["Memory Engine Initialization"] = engine_ok

    if engine_issues:
        print("\n⚠️  Issues found:")
        for issue in engine_issues:
            print(f"   - {issue}")

    if not engine_ok:
        print("\n❌ Memory engine initialization failed. Stopping.")
        print_deployment_summary(all_checks)
        return 1

    if not check_only:
        guardian_decision = _guardian_preflight_full_validation()
        guardian_ok = guardian_decision.allowed
        all_checks["Guardian Deployment Gate"] = guardian_ok
        print_status(
            "Guardian deployment gate",
            guardian_ok,
            guardian_decision.reason,
        )
        if not guardian_ok:
            print("\nGuardian denied full deployment validation. Stopping.")
            print_deployment_summary(all_checks)
            return 1

        # 4. Smoke test
        smoke_ok, smoke_issues = await run_smoke_test()
        all_checks["Smoke Test"] = smoke_ok

        if smoke_issues:
            print("\n⚠️  Issues found:")
            for issue in smoke_issues:
                print(f"   - {issue}")

        # 5. Metrics check (optional)
        metrics_ok, metrics_issues = check_metrics_available()
        all_checks["Metrics Endpoint"] = metrics_ok

    # Final summary
    print_deployment_summary(all_checks)

    return 0 if all(all_checks.values()) else 1


if __name__ == "__main__":
    check_only = "--check-only" in sys.argv

    try:
        exit_code = asyncio.run(main(check_only=check_only))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
