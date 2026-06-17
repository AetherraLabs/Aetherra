import asyncio
import json

import pytest

from aetherra_service_registry import AetherraServiceRegistry, ServiceStatus


class _DemoService:
    pass


class _MessageService:
    def __init__(self):
        self.messages = []

    async def handle_message(self, message_type, data):
        self.messages.append((message_type, data))


@pytest.fixture
def registry_env(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    return tmp_path


def _audit_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_service_registration_writes_guardian_audit(registry_env):
    registry = AetherraServiceRegistry()

    result = asyncio.run(
        registry.register_service(
            "demo_service",
            _DemoService(),
            metadata={
                "guardian_requester": "registry-admin",
                "token": "do-not-audit-this-value",
            },
            dependencies=["kernel_loop"],
        )
    )
    entries = _audit_entries(registry_env)

    assert result is True
    assert registry.get_service_info("demo_service") is not None
    assert entries[-1]["event_type"] == "guardian_decision"
    assert entries[-1]["details"]["intent"]["action"] == "service_registry.register"
    assert "service_registry_mutation" in entries[-1]["details"]["risk"]["factors"]
    assert "do-not-audit-this-value" not in json.dumps(entries[-1])


def test_service_registration_blocked_by_missing_capability(monkeypatch, registry_env):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(registry_env / "policy"))
    registry = AetherraServiceRegistry()

    result = asyncio.run(
        registry.register_service(
            "blocked_service",
            _DemoService(),
            metadata={"guardian_requester": "registry-admin"},
        )
    )
    entries = _audit_entries(registry_env)

    assert result is False
    assert registry.get_service_info("blocked_service") is None
    assert entries[-1]["details"]["decision"]["status"] == "deny"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_internal_service_registration_allowed_in_production(monkeypatch, registry_env):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    registry = AetherraServiceRegistry()

    result = asyncio.run(registry.register_service("boot_service", _DemoService()))
    entries = _audit_entries(registry_env)

    assert result is True
    assert registry.get_service_info("boot_service") is not None
    assert entries[-1]["details"]["intent"]["requester"] == "service_registry"
    assert entries[-1]["details"]["intent"]["action"] == "service_registry.register"


def test_service_unregistration_writes_guardian_audit(registry_env):
    registry = AetherraServiceRegistry()
    asyncio.run(
        registry.register_service(
            "demo_service",
            _DemoService(),
            metadata={
                "guardian_requester": "registry-admin",
                "secret": "do-not-audit-this-value",
            },
        )
    )

    result = asyncio.run(registry.unregister_service("demo_service"))
    entries = _audit_entries(registry_env)

    assert result is True
    assert registry.get_service_info("demo_service") is None
    assert entries[-1]["details"]["intent"]["action"] == "service_registry.unregister"
    assert entries[-1]["details"]["intent"]["target"] == "service_registry:service"
    assert "do-not-audit-this-value" not in json.dumps(entries[-1])


def test_service_status_update_writes_guardian_audit_without_metadata_values(
    registry_env,
):
    registry = AetherraServiceRegistry()
    asyncio.run(registry.register_service("demo_service", _DemoService()))

    asyncio.run(
        registry.update_service_status(
            "demo_service",
            ServiceStatus.DEGRADED,
            metadata={"reason": "do-not-audit-this-status-reason"},
        )
    )
    entries = _audit_entries(registry_env)

    assert registry.get_service_info("demo_service").status == ServiceStatus.DEGRADED
    assert entries[-1]["details"]["intent"]["action"] == (
        "service_registry.status_update"
    )
    assert "do-not-audit-this-status-reason" not in json.dumps(entries[-1])


def test_external_service_status_update_denial_preserves_status(
    monkeypatch, registry_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(registry_env / "policy"))
    registry = AetherraServiceRegistry()
    asyncio.run(registry.register_service("demo_service", _DemoService()))

    with pytest.raises(PermissionError):
        asyncio.run(
            registry.update_service_status(
                "demo_service",
                ServiceStatus.FAILED,
                metadata={"guardian_requester": "external-registry-client"},
            )
        )

    entries = _audit_entries(registry_env)
    assert registry.get_service_info("demo_service").status == ServiceStatus.HEALTHY
    assert entries[-1]["details"]["intent"]["action"] == (
        "service_registry.status_update"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_service_heartbeat_update_writes_guardian_audit(registry_env):
    registry = AetherraServiceRegistry()
    asyncio.run(registry.register_service("demo_service", _DemoService()))
    before = registry.get_service_info("demo_service").last_heartbeat

    asyncio.run(registry.update_heartbeat("demo_service"))
    entries = _audit_entries(registry_env)

    assert registry.get_service_info("demo_service").last_heartbeat >= before
    assert entries[-1]["details"]["intent"]["action"] == (
        "service_registry.heartbeat_update"
    )


def test_external_service_heartbeat_denial_preserves_timestamp(
    monkeypatch, registry_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(registry_env / "policy"))
    registry = AetherraServiceRegistry()
    asyncio.run(registry.register_service("demo_service", _DemoService()))
    before = registry.get_service_info("demo_service").last_heartbeat

    with pytest.raises(PermissionError):
        asyncio.run(
            registry.update_heartbeat(
                "demo_service", requester="external-registry-client"
            )
        )

    entries = _audit_entries(registry_env)
    assert registry.get_service_info("demo_service").last_heartbeat == before
    assert entries[-1]["details"]["intent"]["action"] == (
        "service_registry.heartbeat_update"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_self_heartbeat_flag_guardian_denial_preserves_metadata(
    monkeypatch, registry_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(registry_env / "policy"))
    registry = AetherraServiceRegistry()
    asyncio.run(registry.register_service("demo_service", _DemoService()))

    result = registry.mark_service_self_heartbeat(
        "demo_service",
        enabled=True,
        requester="external-registry-client",
    )
    entries = _audit_entries(registry_env)

    assert result is False
    assert registry.is_self_heartbeating("demo_service") is False
    assert entries[-1]["details"]["intent"]["action"] == (
        "service_registry.self_heartbeat_flag"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_service_message_dispatch_writes_guardian_audit_without_payload_values(
    registry_env,
):
    registry = AetherraServiceRegistry()
    service = _MessageService()
    asyncio.run(registry.register_service("demo_service", service))

    result = asyncio.run(
        registry.send_message(
            "demo_service",
            "secret.message",
            {"token": "do-not-audit-this-message-value"},
        )
    )
    entries = _audit_entries(registry_env)

    assert result is True
    assert service.messages == [
        ("secret.message", {"token": "do-not-audit-this-message-value"})
    ]
    assert entries[-1]["details"]["intent"]["action"] == (
        "service_registry.send_message"
    )
    assert "do-not-audit-this-message-value" not in json.dumps(entries[-1])


def test_external_service_message_denial_stops_handler(monkeypatch, registry_env):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(registry_env / "policy"))
    registry = AetherraServiceRegistry()
    service = _MessageService()
    asyncio.run(registry.register_service("demo_service", service))

    result = asyncio.run(
        registry.send_message(
            "demo_service",
            "blocked.message",
            {"secret": "blocked"},
            requester="external-registry-client",
        )
    )
    entries = _audit_entries(registry_env)

    assert result is False
    assert service.messages == []
    assert entries[-1]["details"]["intent"]["action"] == (
        "service_registry.send_message"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_service_broadcast_writes_guardian_audit_and_dispatches(registry_env):
    registry = AetherraServiceRegistry()
    service = _MessageService()
    asyncio.run(registry.register_service("demo_service", service))

    asyncio.run(
        registry.broadcast_message(
            "broadcast.secret",
            {"payload": "do-not-audit-this-broadcast-value"},
        )
    )
    entries = _audit_entries(registry_env)

    assert service.messages == [
        ("broadcast.secret", {"payload": "do-not-audit-this-broadcast-value"})
    ]
    assert any(
        entry["details"]["intent"]["action"] == "service_registry.broadcast_message"
        for entry in entries
    )
    broadcast_entry = next(
        entry
        for entry in reversed(entries)
        if entry["details"]["intent"]["action"] == "service_registry.broadcast_message"
    )
    assert "do-not-audit-this-broadcast-value" not in json.dumps(broadcast_entry)


def test_external_broadcast_denial_stops_all_handlers(monkeypatch, registry_env):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(registry_env / "policy"))
    registry = AetherraServiceRegistry()
    service = _MessageService()
    asyncio.run(registry.register_service("demo_service", service))

    with pytest.raises(PermissionError):
        asyncio.run(
            registry.broadcast_message(
                "blocked.broadcast",
                {"payload": "blocked"},
                requester="external-registry-client",
            )
        )
    entries = _audit_entries(registry_env)

    assert service.messages == []
    assert entries[-1]["details"]["intent"]["action"] == (
        "service_registry.broadcast_message"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_event_subscription_guardian_denial_preserves_handlers(
    monkeypatch, registry_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(registry_env / "policy"))
    registry = AetherraServiceRegistry()

    def handler(_event):
        return None

    with pytest.raises(PermissionError):
        registry.subscribe_to_events(
            "service.registered",
            handler,
            requester="external-registry-client",
        )
    entries = _audit_entries(registry_env)

    assert registry._event_handlers == {}
    assert entries[-1]["details"]["intent"]["action"] == "service_registry.subscribe"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"
