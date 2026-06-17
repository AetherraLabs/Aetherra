import asyncio
import json

import pytest

from aetherra_event_bus import EventBus


class _Registry:
    def __init__(self):
        self.messages = []

    async def broadcast_message(self, message_type, data):
        self.messages.append((message_type, data))


@pytest.fixture
def guardian_env(monkeypatch, tmp_path):
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


def _write_capability_policy(root, allow_map):
    policy_file = root / "policy" / "capabilities.json"
    policy_file.parent.mkdir(parents=True, exist_ok=True)
    policy_file.write_text(json.dumps({"allow": allow_map}), encoding="utf-8")


def test_event_publish_writes_guardian_audit_without_payload_values(guardian_env):
    bus = EventBus(_Registry())

    result = asyncio.run(
        bus.publish(
            "kernel",
            {
                "type": "lifecycle",
                "source": "event_bus",
                "token": "do-not-audit-this-value",
            },
        )
    )
    entries = _audit_entries(guardian_env)

    assert result == {"ok": True}
    assert entries[-1]["details"]["intent"]["action"] == "event_bus.publish"
    assert "event_bus_mutation" in entries[-1]["details"]["risk"]["factors"]
    assert "do-not-audit-this-value" not in json.dumps(entries[-1])


def test_event_publish_blocks_explicit_source_without_capability(
    monkeypatch, guardian_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    bus = EventBus(_Registry())

    with pytest.raises(PermissionError, match="missing_capability"):
        asyncio.run(
            bus.publish(
                "kernel",
                {"type": "unsafe", "source": "untrusted_service"},
            )
        )

    assert bus.get_metrics()["events_published_total"] == 0


def test_event_subscribe_and_ack_write_guardian_audit(guardian_env):
    bus = EventBus(_Registry())

    assert asyncio.run(bus.subscribe("plugins", "event_bus")) == {"ok": True}
    assert asyncio.run(bus.publish("plugins", {"type": "loaded"})) == {"ok": True}
    assert asyncio.run(bus.ack("plugins", 1)) == {"ok": True}
    entries = _audit_entries(guardian_env)

    assert entries[-3]["details"]["intent"]["action"] == "event_bus.subscribe"
    assert entries[-2]["details"]["intent"]["action"] == "event_bus.publish"
    assert entries[-1]["details"]["intent"]["action"] == "event_bus.ack"
    assert bus.get_status()["topics"]["plugins"]["backlog"] == 0


def test_command_event_publish_requires_command_capability(monkeypatch, guardian_env):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    _write_capability_policy(
        guardian_env,
        {"operator": ["event:publish"]},
    )
    bus = EventBus(_Registry())

    with pytest.raises(PermissionError, match="missing_capability"):
        asyncio.run(
            bus.publish(
                "kernel.control",
                {"type": "shutdown", "source": "operator"},
            )
        )

    entries = _audit_entries(guardian_env)
    assert entries[-1]["details"]["intent"]["action"] == "event_bus.publish_command"
    assert entries[-1]["details"]["intent"]["capabilities"] == [
        "event:publish",
        "event:command",
    ]
    assert bus.get_metrics()["events_published_total"] == 0


def test_command_event_publish_allows_explicit_command_capability(
    monkeypatch, guardian_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    _write_capability_policy(
        guardian_env,
        {"operator": ["event:publish", "event:command"]},
    )
    bus = EventBus(_Registry())

    result = asyncio.run(
        bus.publish(
            "kernel.control",
            {"type": "shutdown", "source": "operator"},
        )
    )

    assert result == {"ok": True}
    entries = _audit_entries(guardian_env)
    assert entries[-1]["details"]["intent"]["action"] == "event_bus.publish_command"
    assert entries[-1]["details"]["intent"]["metadata"]["privileged"] is True
    assert bus.get_status()["topics"]["kernel.control"]["backlog"] == 1


def test_message_routed_command_publish_uses_guardian_gate(monkeypatch, guardian_env):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    _write_capability_policy(
        guardian_env,
        {"operator": ["event:publish"]},
    )
    bus = EventBus(_Registry())

    with pytest.raises(PermissionError, match="missing_capability"):
        asyncio.run(
            bus.handle_message(
                "kernel.event.publish",
                {
                    "topic": "system.command",
                    "event": {"type": "execute", "source": "operator"},
                },
            )
        )

    assert bus.get_status()["topics"] == {}
