#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Headless smoke test for Aetherra OS.
Performs end-to-end probe: service start/stop, health checks, indices validation.
"""

# Standard library imports
import asyncio
import os
import sys
import time
from pathlib import Path

# Ensure project root on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


async def check_service_health() -> bool:
    """Check if core services can be imported and initialized."""
    try:
        # Aetherra imports
        from aetherra_self_incorporation import (
            SelfIncorporationConfig,
            SelfIncorporationService,
        )
        from aetherra_service_registry import ServiceRegistry

        # Test service registry
        ServiceRegistry()

        # Test self-incorporation service initialization
        config = SelfIncorporationConfig()
        service = SelfIncorporationService(config)

        # Basic health check
        health = await service.health_check()
        if health.get("status") != "starting":
            print(f"[SMOKE][WARN] Service status: {health.get('status')}")

        print("[SMOKE][OK] Core services can initialize")
        return True

    except Exception as e:
        print(f"[SMOKE][FAIL] Service health check failed: {e}")
        return False


def check_indices_present() -> bool:
    """Verify critical database indices and files are present or can be created."""
    """Verify critical database indices and files are present or can be created."""
    try:
        # Check if index directories exist or can be created
        index_paths = [
            Path("introspection.db"),
            Path("lyrixa_improvement.db"),
            Path("lyrixa_orchestrator.db"),
        ]

        for path in index_paths:
            if path.exists():
                print(f"[SMOKE][OK] Index exists: {path}")
            else:
                # Try to create parent directory if needed
                path.parent.mkdir(parents=True, exist_ok=True)
                print(f"[SMOKE][OK] Index path available: {path}")

        # Check config files
        config_files = [
            Path("config.json"),
            Path("aetherra_plugin_catalog.json"),
        ]

        for config_file in config_files:
            if config_file.exists():
                print(f"[SMOKE][OK] Config file exists: {config_file}")
            else:
                print(f"[SMOKE][WARN] Config file missing: {config_file}")

        return True

    except Exception as e:
        print(f"[SMOKE][FAIL] Index check failed: {e}")
        return False


async def test_service_lifecycle() -> bool:
    """Test basic service start/stop lifecycle."""
    try:
        # Aetherra imports
        from aetherra_self_incorporation import (
            SelfIncorporationConfig,
            SelfIncorporationService,
        )

        # Create service with minimal config
        config = SelfIncorporationConfig()
        service = SelfIncorporationService(config)

        # Test start
        print("[SMOKE] Testing service start...")
        await service.start()

        # Check status
        status = await service.get_status()
        if not status.get("running"):
            print("[SMOKE][WARN] Service reports not running after start")
        else:
            print("[SMOKE][OK] Service started successfully")

        # Test stop
        print("[SMOKE] Testing service stop...")
        await service.stop()

        final_status = await service.get_status()
        if final_status.get("running"):
            print("[SMOKE][WARN] Service still running after stop")
        else:
            print("[SMOKE][OK] Service stopped successfully")

        return True

    except Exception as e:
        print(f"[SMOKE][FAIL] Service lifecycle test failed: {e}")
        return False


async def main() -> int:
    """Main smoke test orchestrator."""
    print("[SMOKE] Starting Aetherra OS smoke test...")

    # Set quiet mode
    os.environ.setdefault("AETHERRA_QUIET", "1")

    start_time = time.time()
    all_passed = True

    # Test 1: Check indices and config files
    print("\n[SMOKE] Phase 1: Checking indices and config files...")
    if not check_indices_present():
        all_passed = False

    # Test 2: Check service health
    print("\n[SMOKE] Phase 2: Checking service health...")
    if not await check_service_health():
        all_passed = False

    # Test 3: Test service lifecycle
    print("\n[SMOKE] Phase 3: Testing service lifecycle...")
    if not await test_service_lifecycle():
        all_passed = False

    # Summary
    duration = time.time() - start_time
    print(f"\n[SMOKE] Test completed in {duration:.2f}s")

    if all_passed:
        print("[SMOKE][PASS] All smoke tests passed!")
        return 0

    print("[SMOKE][FAIL] Some smoke tests failed!")
    return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[SMOKE] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"[SMOKE][FATAL] Unexpected error: {e}")
        sys.exit(2)
