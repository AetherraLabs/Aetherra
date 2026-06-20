import pytest

from aetherra_os_launcher import AetherraOSLauncher


class _FakeRegistry:
    def __init__(self):
        self.status_updates = []

    async def update_service_status(self, name, status):
        self.status_updates.append((name, status))


class _FakeMaintenanceService:
    def get_status(self):
        return {"available": True}


@pytest.mark.asyncio
async def test_launcher_loads_maintenance_system(monkeypatch):
    calls = []

    async def fake_register_maintenance_service(*, project_root):
        calls.append(project_root)
        return _FakeMaintenanceService()

    monkeypatch.setattr(
        "Aetherra.maintenance.register_maintenance_service",
        fake_register_maintenance_service,
    )

    launcher = AetherraOSLauncher()
    launcher.service_registry = _FakeRegistry()

    await launcher._load_maintenance_system({"maintenance_enabled": True})

    assert len(calls) == 1
    assert "maintenance" in launcher.systems
    assert launcher.systems["maintenance"].get_status()["available"] is True
    assert [name for name, _status in launcher.service_registry.status_updates] == [
        "maintenance_system",
        "aetherra_maintenance",
    ]


@pytest.mark.asyncio
async def test_launcher_can_disable_maintenance_system(monkeypatch):
    async def fake_register_maintenance_service(*, project_root):
        raise AssertionError("Maintenance registration should not be called")

    monkeypatch.setattr(
        "Aetherra.maintenance.register_maintenance_service",
        fake_register_maintenance_service,
    )

    launcher = AetherraOSLauncher()
    launcher.service_registry = _FakeRegistry()

    await launcher._load_maintenance_system({"maintenance_enabled": False})

    assert "maintenance" not in launcher.systems
    assert launcher.service_registry.status_updates == []
