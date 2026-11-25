"""Real-audit broadcasts preserve lifecycle progress and target ownership.

No runtime patch is applied here. Each async recipient returns immediately,
which exposes a broadcast loop that never actually suspends.
"""

# Standard library imports
import asyncio
import json
import threading

# Third party imports
import pytest

# Aetherra imports
from Aetherra.security.audit_ledger import SecurityAuditLedger
from aetherra_service_registry import AetherraServiceRegistry, ServiceStatus


@pytest.fixture
def governed(monkeypatch, tmp_path):
    policy = tmp_path / "policy.json"
    policy.write_text(
        json.dumps(
            {
                "version": 1,
                "default": "deny",
                "allow": [
                    {
                        "requester": "service_registry",
                        "subsystem": "service_registry",
                        "action": "service_registry.*",
                        "target": "service_registry:service",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    for key, value in {
        "AETHERRA_PROFILE": "test",
        "AETHERRA_WORKSPACE_ROOT": str(tmp_path),
        "AETHERRA_GUARDIAN_POLICY": str(policy),
        "AETHERRA_GUARDIAN_STATE_DIR": str(tmp_path / "guardian"),
        "AETHERRA_GUARDIAN_ENABLED": "1",
        "AETHERRA_GUARDIAN_MODE": "enforcing",
        "AETHERRA_GUARDIAN_REQUIRE_POLICY": "1",
        "AETHERRA_REQUIRE_CAPABILITIES": "1",
        "AETHERRA_AUDIT": "1",
        "AETHERRA_SIGNING_STRICT": "1",
        "AETHERRA_SCRIPT_VERIFY_STRICT": "1",
    }.items():
        monkeypatch.setenv(key, value)
    for key in (
        "AETHERRA_REGISTRY_URL",
        "AETHERRA_SECURITY_AUDIT_SECRET",
        "AETHERRA_SECURITY_STATE_SECRET",
        "AETHERRA_GUARDIAN_APPROVAL_ID",
    ):
        monkeypatch.delenv(key, raising=False)
    ledger = tmp_path / ".aetherra/security/audit.jsonl"
    yield policy, ledger
    assert SecurityAuditLedger(ledger).verify_integrity(require_signed_records=True)


class Recipient:
    def __init__(self, name, deliveries):
        self.name = name
        self.deliveries = deliveries

    async def handle_message(self, message_type, data):
        self.deliveries.append(self.name)
        return {"ok": True}


async def recipients(registry, names, deliveries):
    for name in names:
        assert await registry.register_service(name, Recipient(name, deliveries))


def audit_actions(path):
    return [
        record["details"]["intent"]["action"]
        for record in map(json.loads, path.read_text(encoding="utf-8").splitlines())
    ]


def test_real_audited_broadcast_yields_to_queued_loop_heartbeat(governed):
    deliveries = []
    heartbeat_progress = []

    async def exercise():
        registry = AetherraServiceRegistry()
        await recipients(registry, ("first", "second", "third"), deliveries)
        asyncio.get_running_loop().call_soon(
            lambda: heartbeat_progress.append(tuple(deliveries))
        )
        await registry.broadcast_message("kernel.health", {})
        await asyncio.sleep(0)  # Flush a callback that the old loop starved.

    asyncio.run(exercise())
    assert deliveries == ["first", "second", "third"]
    assert heartbeat_progress
    assert len(heartbeat_progress[0]) < 3, "Broadcast starved the loop heartbeat"
    actions = audit_actions(governed[1])
    assert actions.count("service_registry.broadcast_message") == 1
    assert actions.count("service_registry.send_message") == 3


def test_completed_real_status_preflight_delivers_before_broadcast_finishes(governed):
    deliveries = []
    delivery_progress = []
    queued = threading.Event()

    async def exercise():
        registry = AetherraServiceRegistry()
        owner = object()
        assert await registry.register_service("observer", owner)
        await recipients(registry, ("first", "second", "third"), deliveries)
        loop = asyncio.get_running_loop()
        original = loop.call_soon_threadsafe

        def track_delivery(callback, *args, context=None):
            if getattr(callback, "__qualname__", "").endswith(
                "_bounded_status_preflight.<locals>.deliver"
            ):

                def deliver(*values):
                    delivery_progress.append(tuple(deliveries))
                    callback(*values)

                result = original(deliver, *args, context=context)
                queued.set()
                return result
            return original(callback, *args, context=context)

        loop.call_soon_threadsafe = track_delivery
        updating = asyncio.create_task(
            registry.update_service_status(
                "observer",
                ServiceStatus.HEALTHY,
                expected_instance=owner,
                nonblocking_preflight=True,
                preflight_timeout=1.0,
            )
        )
        try:
            await asyncio.sleep(0)  # Admit the actual registry authorization worker.
            # Deliberately hold this loop briefly until the real worker has queued
            # its completion. This Event establishes ordering, not a sleep estimate.
            assert queued.wait(2), "real authorization did not queue its completion"
            assert not updating.done()
            await registry.broadcast_message("kernel.health", {})
            assert await updating is True
        finally:
            await asyncio.gather(updating, return_exceptions=True)
            loop.call_soon_threadsafe = original

    asyncio.run(exercise())
    assert deliveries == ["first", "second", "third"]
    assert delivery_progress
    assert len(delivery_progress[0]) < 3, "Broadcast starved an authorized receipt"
    assert "service_registry.status_update" in audit_actions(governed[1])


@pytest.mark.parametrize("mutation", ["remove", "replace", "degrade"])
def test_broadcast_rechecks_registration_after_yield(governed, mutation):
    deliveries = []

    async def exercise():
        registry = AetherraServiceRegistry()
        await recipients(registry, ("first", "target", "last"), deliveries)
        old_info = registry.get_service_info("target")

        async def change_registration():
            if mutation == "remove":
                assert await registry.unregister_service("target")
            elif mutation == "replace":
                assert await registry.register_service(
                    "target", Recipient("replacement", deliveries)
                )
                assert registry.get_service_info("target") is not old_info
            else:
                await registry.update_service_status("target", ServiceStatus.DEGRADED)

        change = asyncio.create_task(change_registration())
        try:
            await registry.broadcast_message("kernel.health", {})
        finally:
            await change

    asyncio.run(exercise())
    assert deliveries == [
        "first",
        "last",
    ], "a changed registration received an in-flight broadcast after queued mutation"


def test_broadcast_snapshot_excludes_additions_and_survives_removal(governed):
    deliveries = []

    async def exercise():
        registry = AetherraServiceRegistry()

        class FirstRecipient(Recipient):
            async def handle_message(self, message_type, data):
                self.deliveries.append(self.name)
                assert await registry.unregister_service("target")
                assert await registry.register_service(
                    "new", Recipient("new", deliveries)
                )
                return {"ok": True}

        assert await registry.register_service(
            "first", FirstRecipient("first", deliveries)
        )
        await recipients(registry, ("target", "last"), deliveries)
        await registry.broadcast_message("kernel.health", {})

    asyncio.run(exercise())
    assert deliveries == ["first", "last"]


def test_broadcast_keeps_exclusions_and_denial_before_dispatch(governed):
    deliveries = []

    async def exercise():
        registry = AetherraServiceRegistry()
        await recipients(registry, ("first", "second", "third"), deliveries)
        await registry.broadcast_message("kernel.health", {}, exclude=["second"])
        assert deliveries == ["first", "third"]
        policy = json.loads(governed[0].read_text(encoding="utf-8"))
        policy["deny"] = [{"action": "service_registry.broadcast_message"}]
        governed[0].write_text(json.dumps(policy), encoding="utf-8")
        with pytest.raises(PermissionError):
            await registry.broadcast_message("kernel.health", {})
        assert deliveries == ["first", "third"]

    asyncio.run(exercise())
