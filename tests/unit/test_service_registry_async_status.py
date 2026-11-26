"""Cancellation-safe, audited registry status updates for runtime observers."""

# Standard library imports
import asyncio
import json
import threading
import time
from contextlib import contextmanager

# Third party imports
import pytest

# Aetherra imports
from Aetherra.security.audit_ledger import SecurityAuditLedger
from aetherra_service_registry import (
    AetherraServiceRegistry,
    ServiceInfo,
    ServiceStatus,
)


@pytest.fixture
def registry_env(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    monkeypatch.delenv("AETHERRA_GUARDIAN_POLICY", raising=False)
    return tmp_path


def _audit_entries(root):
    path = root / ".aetherra" / "security" / "audit.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _registered():
    registry = AetherraServiceRegistry()
    instance = object()
    assert asyncio.run(registry.register_service("observer", instance))
    return registry, instance


@contextmanager
def _contended_ledger(root):
    ledger = SecurityAuditLedger(root / ".aetherra" / "security" / "audit.jsonl")
    acquired = threading.Event()
    release = threading.Event()

    def hold_lock():
        with ledger._lock:
            acquired.set()
            release.wait(5)

    holder = threading.Thread(target=hold_lock, daemon=True)
    holder.start()
    assert acquired.wait(1)
    try:
        yield release
    finally:
        release.set()
        holder.join(1)
        assert not holder.is_alive()


def _observe_append(monkeypatch):
    append = SecurityAuditLedger.append
    entered = threading.Event()
    workers = []

    def observed_append(ledger, **kwargs):
        workers.append(threading.current_thread())
        entered.set()
        return append(ledger, **kwargs)

    monkeypatch.setattr(SecurityAuditLedger, "append", observed_append)
    return entered, workers


async def _until(predicate):
    async with asyncio.timeout(1):
        while not predicate():
            await asyncio.sleep(0.001)


def test_status_audits_before_mutation_and_broadcasts_on_owner_loop(registry_env):
    registry, instance = _registered()
    seen = []
    owner_thread = threading.get_ident()

    async def scenario():
        owner_loop = asyncio.get_running_loop()

        async def handler(event):
            entry = _audit_entries(registry_env)[-1]
            assert (
                entry["details"]["intent"]["action"] == "service_registry.status_update"
            )
            assert entry["details"]["decision"]["status"] in {"allow", "allow_limited"}
            assert entry["hash"]
            assert asyncio.get_running_loop() is owner_loop
            assert threading.get_ident() == owner_thread
            assert (
                registry.get_service_info("observer").status is ServiceStatus.DEGRADED
            )
            seen.append(event)

        registry.subscribe_to_events("service.status_changed", handler)
        applied = await registry.update_service_status(
            "observer",
            ServiceStatus.DEGRADED,
            {"tick_count": 2},
            expected_instance=instance,
            nonblocking_preflight=True,
            preflight_timeout=1,
        )
        assert applied is True
        heartbeat = registry.get_service_info("observer").last_heartbeat
        assert (
            await registry.update_service_status(
                "observer",
                ServiceStatus.DEGRADED,
                {"tick_count": 3},
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=1,
            )
            is True
        )
        assert registry.get_service_info("observer").last_heartbeat >= heartbeat

    asyncio.run(scenario())
    assert seen == [
        {
            "service_name": "observer",
            "old_status": "healthy",
            "new_status": "degraded",
            "metadata": {"tick_count": 2},
        }
    ]
    assert registry.get_service_info("observer").metadata["tick_count"] == 3
    assert SecurityAuditLedger(
        registry_env / ".aetherra/security/audit.jsonl"
    ).verify_integrity(require_signed_records=True)


def test_contended_audit_times_out_without_worker_accumulation_or_late_update(
    monkeypatch, registry_env
):
    registry, instance = _registered()
    info = registry.get_service_info("observer")
    original_heartbeat = info.last_heartbeat
    entered, workers = _observe_append(monkeypatch)
    events = []
    registry.subscribe_to_events("service.status_changed", events.append)
    entered.clear()
    workers.clear()

    async def scenario(release):
        task = asyncio.create_task(
            registry.update_service_status(
                "observer",
                ServiceStatus.FAILED,
                {"tick_count": 5},
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=0.05,
            )
        )
        await _until(entered.is_set)
        # A shutdown request/sentinel must run while the real ledger remains locked.
        sentinel = asyncio.Event()
        asyncio.get_running_loop().call_soon(sentinel.set)
        await asyncio.wait_for(sentinel.wait(), 0.2)
        with pytest.raises(TimeoutError):
            await task
        for _ in range(3):
            with pytest.raises(TimeoutError):
                await registry.update_service_status(
                    "observer",
                    ServiceStatus.STOPPING,
                    expected_instance=instance,
                    nonblocking_preflight=True,
                    preflight_timeout=0.05,
                )
        waiting = asyncio.create_task(
            registry.update_service_status(
                "observer",
                ServiceStatus.STOPPING,
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=1,
            )
        )
        await asyncio.sleep(0.02)
        waiting.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiting
        assert len(workers) == 1
        assert workers[0].daemon
        assert workers[0].is_alive()
        assert info.status is ServiceStatus.HEALTHY
        assert info.last_heartbeat == original_heartbeat
        assert "tick_count" not in info.metadata
        release.set()
        await _until(lambda: not workers[0].is_alive())
        await asyncio.sleep(0)
        assert info.status is ServiceStatus.HEALTHY
        assert not events
        assert (
            await registry.update_service_status(
                "observer",
                ServiceStatus.STOPPING,
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=1,
            )
            is True
        )
        assert info.status is ServiceStatus.STOPPING

    with _contended_ledger(registry_env) as release:
        asyncio.run(scenario(release))


@pytest.mark.asyncio
async def test_status_preflight_preserves_worker_timeout_identity():
    registry = AetherraServiceRegistry()
    worker_error = TimeoutError("synthetic authorization failure")

    def authorize():
        raise worker_error

    with pytest.raises(TimeoutError) as caught:
        await registry._bounded_status_preflight(authorize, 1)

    assert caught.value is worker_error


def test_cancellation_exits_loop_before_audit_unlock_and_never_mutates_later(
    monkeypatch, registry_env
):
    registry, instance = _registered()
    info = registry.get_service_info("observer")
    original_heartbeat = info.last_heartbeat
    entered, workers = _observe_append(monkeypatch)

    async def scenario():
        task = asyncio.create_task(
            registry.update_service_status(
                "observer",
                ServiceStatus.FAILED,
                {"private": "do-not-apply"},
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=1,
            )
        )
        await _until(entered.is_set)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, 0.2)
        assert workers[0].is_alive()
        assert workers[0].daemon

    with _contended_ledger(registry_env):
        started = time.monotonic()
        asyncio.run(scenario())
        assert time.monotonic() - started < 1
        assert workers[0].is_alive()
    workers[0].join(1)
    assert not workers[0].is_alive()
    assert info.status is ServiceStatus.HEALTHY
    assert info.last_heartbeat == original_heartbeat
    assert "private" not in info.metadata


@pytest.mark.parametrize(
    "replacement", ["foreign_info", "same_instance_info", "foreign_instance", "status"]
)
def test_waiting_update_rechecks_exact_registration_before_mutation(
    monkeypatch, registry_env, replacement
):
    registry, instance = _registered()
    original = registry.get_service_info("observer")
    entered, workers = _observe_append(monkeypatch)

    async def scenario(release):
        task = asyncio.create_task(
            registry.update_service_status(
                "observer",
                ServiceStatus.FAILED,
                {"tick_count": 4},
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=1,
            )
        )
        await _until(entered.is_set)
        if replacement in {"foreign_info", "same_instance_info"}:
            registry._services["observer"] = ServiceInfo(
                "observer",
                instance if replacement == "same_instance_info" else object(),
                status=ServiceStatus.STARTING,
            )
        elif replacement == "foreign_instance":
            original.instance = object()
        else:
            original.status = ServiceStatus.STOPPING
        release.set()
        assert await task is False
        current = registry.get_service_info("observer")
        assert current.status is not ServiceStatus.FAILED
        assert "tick_count" not in current.metadata
        assert "tick_count" not in original.metadata
        await _until(lambda: not workers[0].is_alive())

    with _contended_ledger(registry_env) as release:
        asyncio.run(scenario(release))


def test_owned_update_does_not_touch_a_different_or_missing_service(registry_env):
    registry, instance = _registered()
    before = _audit_entries(registry_env)

    async def scenario():
        for name, owner in [("observer", object()), ("missing", instance)]:
            assert (
                await registry.update_service_status(
                    name,
                    ServiceStatus.FAILED,
                    expected_instance=owner,
                    nonblocking_preflight=True,
                    preflight_timeout=1,
                )
                is False
            )

    asyncio.run(scenario())
    assert registry.get_service_info("observer").status is ServiceStatus.HEALTHY
    assert _audit_entries(registry_env) == before


def test_missing_audit_receipt_denies_opt_in_update(monkeypatch, registry_env):
    registry, instance = _registered()
    before = registry.get_service_info("observer").last_heartbeat

    def unavailable_append(*args, **kwargs):
        raise OSError("synthetic audit unavailable")

    monkeypatch.setattr(SecurityAuditLedger, "append", unavailable_append)
    with pytest.raises(PermissionError, match="audit"):
        asyncio.run(
            registry.update_service_status(
                "observer",
                ServiceStatus.FAILED,
                {"tick_count": 9},
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=1,
            )
        )
    info = registry.get_service_info("observer")
    assert info.status is ServiceStatus.HEALTHY
    assert info.last_heartbeat == before
    assert "tick_count" not in info.metadata


def test_opt_in_update_keeps_capability_denial(monkeypatch, registry_env):
    registry, instance = _registered()
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(registry_env / "policy"))
    with pytest.raises(PermissionError, match="missing_capability"):
        asyncio.run(
            registry.update_service_status(
                "observer",
                ServiceStatus.FAILED,
                {"guardian_requester": "external"},
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=1,
            )
        )
    assert registry.get_service_info("observer").status is ServiceStatus.HEALTHY
    assert _audit_entries(registry_env)[-1]["details"]["decision"]["status"] == "deny"


@pytest.mark.parametrize(
    "timeout", [0, -1, float("nan"), float("inf"), None, "bad", True]
)
def test_invalid_timeout_cannot_start_an_update(registry_env, timeout):
    registry, instance = _registered()
    before = _audit_entries(registry_env)
    with pytest.raises(ValueError, match="timeout"):
        asyncio.run(
            registry.update_service_status(
                "observer",
                ServiceStatus.FAILED,
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=timeout,
            )
        )
    assert registry.get_service_info("observer").status is ServiceStatus.HEALTHY
    assert _audit_entries(registry_env) == before


def test_opt_in_update_keeps_explicit_guardian_policy_denial(monkeypatch, registry_env):
    registry, instance = _registered()
    policy_path = registry_env / "status-policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "default": "allow",
                "deny": [{"action": "service_registry.status_update"}],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AETHERRA_GUARDIAN_POLICY", str(policy_path))
    with pytest.raises(PermissionError, match="guardian_policy_denied"):
        asyncio.run(
            registry.update_service_status(
                "observer",
                ServiceStatus.FAILED,
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=1,
            )
        )
    assert registry.get_service_info("observer").status is ServiceStatus.HEALTHY
    assert _audit_entries(registry_env)[-1]["details"]["decision"]["status"] == "deny"


@pytest.mark.parametrize("guard_result", [True, False, None, 1, "raises"])
def test_apply_guard_runs_on_owner_loop_after_audit_and_can_only_refuse(
    registry_env, guard_result
):
    registry, instance = _registered()
    before = registry.get_service_info("observer").last_heartbeat
    owner_thread = threading.get_ident()
    checks = []

    async def scenario():
        owner_loop = asyncio.get_running_loop()

        def still_owned():
            assert asyncio.get_running_loop() is owner_loop
            assert threading.get_ident() == owner_thread
            assert (
                _audit_entries(registry_env)[-1]["details"]["intent"]["action"]
                == "service_registry.status_update"
            )
            checks.append(True)
            if guard_result == "raises":
                raise RuntimeError("synthetic owner unavailable")
            return guard_result

        applied = await registry.update_service_status(
            "observer",
            ServiceStatus.DEGRADED,
            expected_instance=instance,
            nonblocking_preflight=True,
            preflight_timeout=1,
            apply_if=still_owned,
        )
        assert applied is (guard_result is True)

    asyncio.run(scenario())
    assert checks == [True]
    info = registry.get_service_info("observer")
    if guard_result is True:
        assert info.status is ServiceStatus.DEGRADED
    else:
        assert info.status is ServiceStatus.HEALTHY
        assert info.last_heartbeat == before


def test_apply_guard_cannot_bypass_guardian_denial(monkeypatch, registry_env):
    registry, instance = _registered()
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(registry_env / "policy"))
    checks = []

    def approval():
        checks.append(True)
        return True

    with pytest.raises(PermissionError, match="missing_capability"):
        asyncio.run(
            registry.update_service_status(
                "observer",
                ServiceStatus.FAILED,
                {"guardian_requester": "external"},
                expected_instance=instance,
                nonblocking_preflight=True,
                preflight_timeout=1,
                apply_if=approval,
            )
        )
    assert not checks
    assert registry.get_service_info("observer").status is ServiceStatus.HEALTHY


@pytest.mark.asyncio
async def test_two_owned_status_updates_share_one_bounded_worker_slot(
    monkeypatch, registry_env
):
    registry = AetherraServiceRegistry()
    first, second = object(), object()
    assert await registry.register_service("first", first)
    assert await registry.register_service("second", second)
    owner_loop = asyncio.get_running_loop()
    owner_thread = threading.get_ident()
    events = []

    async def handler(event):
        assert asyncio.get_running_loop() is owner_loop
        assert threading.get_ident() == owner_thread
        events.append(event["service_name"])

    registry.subscribe_to_events("service.status_changed", handler)
    entered, workers = _observe_append(monkeypatch)
    tasks = []
    with _contended_ledger(registry_env) as release:
        try:
            tasks.append(
                asyncio.create_task(
                    registry.update_service_status(
                        "first",
                        ServiceStatus.DEGRADED,
                        expected_instance=first,
                        nonblocking_preflight=True,
                        preflight_timeout=1,
                    )
                )
            )
            await _until(entered.is_set)
            tasks.append(
                asyncio.create_task(
                    registry.update_service_status(
                        "second",
                        ServiceStatus.FAILED,
                        expected_instance=second,
                        nonblocking_preflight=True,
                        preflight_timeout=1,
                    )
                )
            )
            await asyncio.sleep(0.02)
            assert not tasks[1].done()
            assert len(workers) == 1
            release.set()
            assert await asyncio.gather(*tasks) == [True, True]
            assert registry.get_service_info("first").status is ServiceStatus.DEGRADED
            assert registry.get_service_info("second").status is ServiceStatus.FAILED
            assert events == ["first", "second"]
            assert len(workers) == 2
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
