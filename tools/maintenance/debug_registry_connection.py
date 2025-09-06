#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Debug script to test shared registry connection from dashboard
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from aetherra_service_registry import get_service_registry

async def debug_registry_connection():
    print("🔍 Debug: Testing shared registry connection...")

    try:
        # Test registry connection
        registry = await get_service_registry(enable_shared=True)
        print(f"✅ Registry created: {type(registry)}")
        print(f"📊 Shared enabled: {registry._shared_enabled}")

        if registry._shared_registry:
            print(f"🌐 Shared registry object: {type(registry._shared_registry)}")

            # Get shared registry status
            shared_status = registry._shared_registry.get_registry_status()
            print(f"📋 Shared registry status:")
            for key, value in shared_status.items():
                print(f"   {key}: {value}")
        else:
            print("❌ No shared registry object found")

        # Test service listing
        services = registry.list_services()
        print(f"🔧 Services found: {len(services)}")

        for name, info in services.items():
            print(f"   - {name}: {info.status}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_registry_connection())
