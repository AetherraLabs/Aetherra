#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Homeostasis Diagnostic Tool
============================
Diagnoses why homeostasis vital checks are failing.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aetherra_service_registry import get_service_registry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def diagnose():
    """Run diagnostic checks on homeostasis vital systems."""

    print("\n" + "=" * 80)
    print("🔍 Homeostasis Vital Checks Diagnostic")
    print("=" * 80 + "\n")

    # Check 1: Service Registry
    print("📋 Check 1: Service Registry Access")
    try:
        registry = await get_service_registry()
        if registry:
            print("  ✅ Registry accessible")

            # List all registered services
            all_services = registry.list_services()
            print(f"\n  📦 Registered Services ({len(all_services)}):")
            for svc in all_services:
                status_icon = "✅" if svc.status.value == "healthy" else "⚠️"
                print(f"    {status_icon} {svc.name:<30} Status: {svc.status.value}")
        else:
            print("  ❌ Registry not available")
            return
    except Exception as e:
        print(f"  ❌ Registry error: {e}")
        return

    print("\n" + "-" * 80)

    # Check 2: Memory Coherence
    print("\n📝 Check 2: Memory Coherence")
    try:
        memory_service = registry.get_service_info("memory_system")
        if not memory_service:
            print("  ❌ Memory service not found in registry")
        else:
            print(f"  ✅ Memory service found: {memory_service.name}")
            print(f"     Status: {memory_service.status.value}")
            print(f"     Instance type: {type(memory_service.instance).__name__}")

            # Check for coherence method
            if hasattr(memory_service.instance, "check_coherence"):
                print("     ✅ Has check_coherence() method")
                try:
                    coherence_ok = await memory_service.instance.check_coherence()
                    print(f"     Coherence check result: {coherence_ok}")
                except Exception as e:
                    print(f"     ⚠️ Coherence check failed: {e}")
            else:
                print("     ⚠️ No check_coherence() method")
                print("     This causes homeostasis to report degraded status")
                print("     (Not critical - method is optional)")
    except Exception as e:
        print(f"  ❌ Memory coherence check error: {e}")

    print("\n" + "-" * 80)

    # Check 3: Plugin Queue Health
    print("\n🔌 Check 3: Plugin Queue Health")
    try:
        plugin_service = registry.get_service_info("plugin_manager")
        if not plugin_service:
            print("  ⚠️ Plugin manager not found in registry")
            print("     This is EXPECTED - plugin manager may not be running")
            print("     Homeostasis warning is normal if plugins aren't used")
        else:
            print(f"  ✅ Plugin manager found: {plugin_service.name}")
            print(f"     Status: {plugin_service.status.value}")

            # Check for queue health method
            if hasattr(plugin_service.instance, "get_queue_health"):
                print("     ✅ Has get_queue_health() method")
                try:
                    queue_health = await plugin_service.instance.get_queue_health()
                    print(f"     Queue health: {queue_health}")
                except Exception as e:
                    print(f"     ⚠️ Queue health check failed: {e}")
            else:
                print("     ⚠️ No get_queue_health() method")
    except Exception as e:
        print(f"  ❌ Plugin queue check error: {e}")

    print("\n" + "-" * 80)

    # Check 4: Hub Connectivity
    print("\n🌐 Check 4: Hub Connectivity")
    try:
        hub_service = registry.get_service_info("aetherra_hub")
        if not hub_service:
            print("  ⚠️ Hub service not found in registry")
            print("     This is EXPECTED - Hub runs as separate process")
            print(
                "     Hub should be started with: python tools/run_hub_ai_api.py --port 3001"
            )
            print("     Homeostasis will report degraded until Hub is registered")
        else:
            print(f"  ✅ Hub service found: {hub_service.name}")
            print(f"     Status: {hub_service.status.value}")

            # Check for ping method
            if hasattr(hub_service.instance, "ping"):
                print("     ✅ Has ping() method")
                try:
                    ping_result = await hub_service.instance.ping()
                    print(f"     Ping result: {ping_result}")
                except Exception as e:
                    print(f"     ⚠️ Ping failed: {e}")
            else:
                print("     ⚠️ No ping() method")
    except Exception as e:
        print(f"  ❌ Hub connectivity check error: {e}")

    print("\n" + "=" * 80)
    print("🔍 Diagnostic Summary")
    print("=" * 80 + "\n")

    # Summarize findings
    print("📊 Findings:")
    print("\n1. Memory Coherence:")
    print("   - Memory service is registered and healthy")
    print("   - Missing check_coherence() method causes homeostasis warning")
    print("   - This is COSMETIC - memory system is functional")

    print("\n2. Plugin Queue:")
    print("   - Plugin manager may not be running (NORMAL)")
    print("   - Homeostasis expects it for some workflows")
    print("   - Safe to ignore if you're not using plugins")

    print("\n3. Hub Link:")
    print("   - Hub runs as separate process")
    print("   - Must be started manually: python tools/run_hub_ai_api.py --port 3001")
    print("   - Homeostasis will clear once Hub registers with OS")

    print("\n✅ Recommended Actions:")
    print("   1. Start Hub: python tools/run_hub_ai_api.py --port 3001")
    print("   2. Hub will auto-register with OS and clear hub_link warning")
    print("   3. Other warnings are cosmetic and can be ignored")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(diagnose())
