#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio

import pytest

from aetherra_service_registry import (
    ServiceStatus,
    get_service_registry,
    register_service,
)


@pytest.mark.asyncio
async def test_service_registry_basic_registration():
    """Basic sanity test for the in-process service registry.

    This replaces the ad-hoc script-style test that attempted to pass an
    unsupported parameter. Keeps scope narrow to avoid side-effects.
    """
    registry = await get_service_registry()

    class DummyService:
        def __init__(self):
            self.alive = True

        def is_alive(self):  # exercised indirectly by heartbeat monitor
            return self.alive

    svc = DummyService()
    ok = await register_service("dummy_service", svc, metadata={"version": "1.0"})
    assert ok is True

    info = registry.get_service_info("dummy_service")
    assert info is not None
    # Dependency-free services become HEALTHY automatically
    assert info.status in {ServiceStatus.HEALTHY, ServiceStatus.STARTING}

    listed = registry.list_services()
    assert "dummy_service" in listed

    status_snapshot = registry.get_registry_status()
    assert status_snapshot["total_services"] >= 1

    # Minimal heartbeat update
    await registry.update_heartbeat("dummy_service")

    # No teardown here; global registry reused across tests.
