#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio

# Aetherra imports
from aetherra_service_registry import get_service_registry


async def test():
    print("Testing shared registry access...")
    registry = await get_service_registry(enable_shared=True)
    print(f"Registry created: {registry}")
    print(f"Shared enabled: {registry._shared_enabled}")
    services = registry.list_services()
    print(f"Local services: {list(services.keys())}")

    if registry._shared_registry:
        shared_services = registry._shared_registry.list_services()
        print(f"Shared services: {list(shared_services.keys())}")
    else:
        print("No shared registry found")


asyncio.run(test())
