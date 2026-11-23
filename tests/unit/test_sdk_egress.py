"""Production SDK egress enforcement with disposable policy and no network."""

# Standard library imports
import importlib
import json
from pathlib import Path
from unittest.mock import Mock
from uuid import UUID

# Third party imports
import httpx
import pytest

# Aetherra imports
from tests.unit.test_openai_request_lifecycle import configure_sdk_policies
from tests.unit.test_openai_request_lifecycle import offline as offline


def sdk():
    return importlib.import_module("Aetherra.security.sdk_egress")


@pytest.fixture
def policies(tmp_path, monkeypatch):
    return configure_sdk_policies(tmp_path, monkeypatch)


def permit():
    module = sdk()
    return module.authorize_sdk_send(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        "POST",
        httpx.URL("https://synthetic.invalid/v1/chat/completions"),
    )


def test_permit_is_signed_bound_and_private(policies, tmp_path):
    result = permit()
    assert result.owner is sdk().SdkOwner.CORE_LLM
    assert result.timeout_sec == 1
    assert result.max_concurrency == 2
    path = tmp_path / ".aetherra/security/audit.jsonl"
    # Aetherra imports
    from Aetherra.security.audit_ledger import SecurityAuditLedger

    assert SecurityAuditLedger(path).verify_integrity(require_signed_records=True)
    records = [json.loads(line) for line in path.read_text().splitlines()]
    record = next(
        record for record in records if record["hash"] == result.decision_audit_id
    )
    intent = record["details"]["intent"]
    assert str(UUID(int=intent["metadata"]["sdk_attempt_id"])) == result.attempt_id
    assert intent["requester"] == "core:llm"
    assert "synthetic-test-key" not in path.read_text()


def test_authorization_cost_sample(policies):
    # Standard library imports
    import statistics
    import time

    elapsed = []
    path = policies.parent / ".aetherra/security/audit.jsonl"
    for _ in range(10):
        start = time.perf_counter()
        permit()
        elapsed.append((time.perf_counter() - start) * 1000)
    print(
        "SDK_AUTH_SAMPLE "
        + json.dumps(
            {
                "attempts": len(elapsed),
                "ledger_records": len(path.read_text().splitlines()),
                "ledger_bytes": path.stat().st_size,
                "median_ms": round(statistics.median(elapsed), 3),
                "max_ms": round(max(elapsed), 3),
            }
        )
    )
    assert len(elapsed) == 10


@pytest.mark.parametrize(
    "endpoint",
    [
        "",
        "http://synthetic.invalid/v1",
        "https://synthetic.invalid:0/v1",
        "https://user:secret@synthetic.invalid/v1",
        "https://synthetic.invalid/v1?token=secret",
        "https://synthetic.invalid/v1#secret",
    ],
)
def test_endpoint_rejects_unsafe_route(endpoint):
    with pytest.raises(sdk().SdkEgressError):
        sdk().SdkEndpoint.parse(endpoint)


@pytest.mark.parametrize(
    ("url", "method"),
    [
        ("https://other.invalid/v1/chat/completions", "POST"),
        ("https://synthetic.invalid:9443/v1/chat/completions", "POST"),
        ("https://synthetic.invalid:0/v1/chat/completions", "POST"),
        ("https://synthetic.invalid/v1/chat/completions/extra", "POST"),
        ("https://synthetic.invalid/v1/chat/completions?secret=x", "POST"),
        ("https://synthetic.invalid/v1/chat/completions", "GET"),
    ],
)
def test_actual_route_must_match(policies, url, method):
    with pytest.raises(sdk().SdkEgressError):
        sdk().authorize_sdk_send(
            sdk().SdkOwner.CORE_LLM,
            sdk().SdkEndpoint.parse("https://synthetic.invalid/v1"),
            method,
            httpx.URL(url),
        )


@pytest.mark.parametrize(
    "failure",
    [
        "missing_capability",
        "missing_network_policy",
        "malformed_network_policy",
        "malformed_capability_policy",
        "guardian_denied",
        "guardian_disabled",
        "monitor",
    ],
)
def test_preflight_failures_deny(policies, monkeypatch, failure):
    if failure == "missing_capability":
        (policies / "capabilities.json").write_text('{"allow":{"core:llm":[]}}')
    elif failure == "missing_network_policy":
        (policies / "net_policy.json").unlink()
    elif failure == "malformed_network_policy":
        (policies / "net_policy.json").write_text('{"allow_domains":"*"}')
    elif failure == "malformed_capability_policy":
        (policies / "capabilities.json").write_text(
            '{"allow":{"core:llm":"network:outbound"}}'
        )
    elif failure == "guardian_denied":
        Path(__import__("os").environ["AETHERRA_GUARDIAN_POLICY"]).write_text(
            '{"default":"deny"}'
        )
    elif failure == "guardian_disabled":
        monkeypatch.setenv("AETHERRA_GUARDIAN_ENABLED", "0")
    else:
        monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "monitor")
    with pytest.raises(sdk().SdkEgressError):
        permit()


def test_forged_receipt_is_not_permission(policies, monkeypatch):
    # Aetherra imports
    from Aetherra.guardian.models import GuardianDecision, GuardianStatus, RiskLevel

    monkeypatch.setattr(
        sdk(),
        "evaluate_intent",
        Mock(
            return_value=GuardianDecision(
                status=GuardianStatus.ALLOW,
                risk_level=RiskLevel.LOW,
                reason="synthetic",
                audit_id="f" * 64,
            )
        ),
    )
    with pytest.raises(sdk().SdkEgressError, match="sdk_audit_unconfirmed"):
        permit()


def test_stale_receipt_is_not_permission(policies, monkeypatch):
    # Aetherra imports
    from Aetherra.guardian.models import GuardianDecision, GuardianStatus, RiskLevel

    previous = permit()
    monkeypatch.setattr(
        sdk(),
        "evaluate_intent",
        Mock(
            return_value=GuardianDecision(
                status=GuardianStatus.ALLOW,
                risk_level=RiskLevel.LOW,
                reason="synthetic",
                audit_id=previous.decision_audit_id,
            )
        ),
    )
    with pytest.raises(sdk().SdkEgressError, match="sdk_audit_unconfirmed"):
        permit()


def test_signed_denial_cannot_be_returned_as_allow(policies, monkeypatch):
    # Standard library imports
    from dataclasses import replace

    # Aetherra imports
    from Aetherra.guardian.models import GuardianStatus

    module = sdk()
    original = module.evaluate_intent
    (policies.parent / "guardian_policy.json").write_text('{"default":"deny"}')

    def misleading(*args, **kwargs):
        decision = original(*args, **kwargs)
        assert decision.status is GuardianStatus.DENY
        return replace(decision, status=GuardianStatus.ALLOW)

    monkeypatch.setattr(module, "evaluate_intent", misleading)
    with pytest.raises(module.SdkEgressError, match="sdk_audit_unconfirmed"):
        permit()


@pytest.mark.parametrize("field", ["requester", "target", "attempt", "constraints"])
def test_receipt_cannot_certify_different_authority(policies, monkeypatch, field):
    # Standard library imports
    from dataclasses import replace

    module = sdk()
    original = module.evaluate_intent

    def mismatched(intent, **kwargs):
        if field == "requester":
            changed = replace(intent, requester="lyrixa:chat")
        elif field == "target":
            changed = replace(
                intent, metadata={**intent.metadata, "sdk_target_digest": 1}
            )
        elif field == "attempt":
            changed = replace(intent, metadata={**intent.metadata, "sdk_attempt_id": 1})
        else:
            decision = original(intent, **kwargs)
            return replace(
                decision, constraints=("respect_existing_security_controls",)
            )
        return original(changed, **kwargs)

    monkeypatch.setattr(module, "evaluate_intent", mismatched)
    with pytest.raises(module.SdkEgressError, match="sdk_audit_unconfirmed"):
        permit()


@pytest.mark.parametrize("status", ["deny", "contain", "require_approval"])
@pytest.mark.asyncio
async def test_each_guardian_rejection_has_zero_delegates(
    policies, monkeypatch, status
):
    # Aetherra imports
    from Aetherra.guardian.models import GuardianDecision, GuardianStatus, RiskLevel

    module = sdk()
    monkeypatch.setattr(
        module,
        "evaluate_intent",
        lambda *args, **kwargs: GuardianDecision(
            status=GuardianStatus(status),
            risk_level=RiskLevel.HIGH,
            reason="synthetic",
        ),
    )
    seen = []
    async with httpx.AsyncClient(
        transport=module.GuardedAsyncTransport(
            module.SdkOwner.CORE_LLM,
            module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
            httpx.MockTransport(lambda request: seen.append(request) or completion()),
        )
    ) as client:
        assert (
            await client.post("https://synthetic.invalid/v1/chat/completions")
        ).status_code == 403
    assert seen == []


@pytest.mark.parametrize(
    ("base", "url"),
    [
        ("https://[::1]:9443/v1/", "https://[::1]:9443/v1/chat/completions"),
        (
            "https://b\u00fccher.invalid/v1",
            "https://xn--bcher-kva.invalid/v1/chat/completions",
        ),
    ],
)
def test_structured_endpoint_normalization(base, url):
    assert sdk().SdkEndpoint.parse(base).matches("POST", httpx.URL(url))


def test_stream_close_failure_retains_lease_and_safe_status(policies):
    # Standard library imports
    import os
    import subprocess
    import sys

    code = """
import asyncio, pytest
from tests.unit.test_sdk_egress import _assert_stream_close_failure, offline
with pytest.MonkeyPatch.context() as patch:
    offline.__wrapped__(patch)
    asyncio.run(_assert_stream_close_failure())
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        env=dict(os.environ),
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, "isolated stream failure probe failed"


async def _assert_stream_close_failure():
    module = sdk()

    class Content(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b"synthetic"

        async def aclose(self):
            raise RuntimeError("private-stream-detail")

    transport = module.GuardedAsyncTransport(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        httpx.MockTransport(lambda _: httpx.Response(200, stream=Content())),
    )
    response = await transport.handle_async_request(
        httpx.Request("POST", "https://synthetic.invalid/v1/chat/completions")
    )
    with pytest.raises(module.SdkEgressError, match="^sdk_stream_close_failed$"):
        await response.aclose()
    status = module.get_sdk_egress_status(module.SdkOwner.CORE_LLM)
    assert status["status"] == "degraded"
    assert status["active_lease_count"] == status["unresolved_stream_count"] == 1
    assert "private-stream-detail" not in str(status)
    with pytest.raises(module.SdkEgressError, match="^sdk_stream_close_failed$"):
        await transport.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure",
    [
        "owner_missing",
        "owner_blank",
        "capability_missing",
        "capability_malformed",
        "network_missing",
        "network_malformed",
        "guardian_missing",
        "guardian_malformed",
        "guardian_disabled",
        "guardian_advisory",
        "checker_failure",
        "deny",
        "contain",
        "require_approval",
    ],
)
async def test_each_preflight_denial_has_zero_delegates(policies, monkeypatch, failure):
    # Third party imports
    import openai

    # Aetherra imports
    from Aetherra.guardian.models import GuardianDecision, GuardianStatus, RiskLevel

    module = sdk()
    seen = []
    monkeypatch.setattr(
        module,
        "_async_inner_transport",
        lambda: httpx.MockTransport(
            lambda request: seen.append(request) or completion()
        ),
    )
    owner = module.SdkOwner.CORE_LLM
    if failure.startswith("owner_"):
        owner = None if failure == "owner_missing" else ""
        with pytest.raises(module.SdkEgressError, match="^sdk_owner_invalid$"):
            await module.create_guarded_async_openai(owner, api_key="synthetic-key")
        assert seen == []
        return
    if failure == "capability_missing":
        (policies / "capabilities.json").write_text('{"allow":{"core:llm":[]}}')
    elif failure == "capability_malformed":
        (policies / "capabilities.json").write_text('{"allow":[]}')
    elif failure == "network_missing":
        (policies / "net_policy.json").unlink()
    elif failure == "network_malformed":
        (policies / "net_policy.json").write_text('{"allow_domains":true}')
    elif failure == "guardian_missing":
        (policies.parent / "guardian_policy.json").unlink()
        monkeypatch.setenv("AETHERRA_GUARDIAN_REQUIRE_POLICY", "0")
    elif failure == "guardian_malformed":
        (policies.parent / "guardian_policy.json").write_text(
            '{"default":"allow","deny":[123]}'
        )
    elif failure == "guardian_disabled":
        monkeypatch.setenv("AETHERRA_GUARDIAN_ENABLED", "0")
    elif failure == "guardian_advisory":
        monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "advisory")
    elif failure == "checker_failure":

        def unavailable(*args, **kwargs):
            raise RuntimeError("private-checker-detail")

        monkeypatch.setattr(module.capabilities, "list_capabilities", unavailable)
    else:
        decision = GuardianDecision(
            status=GuardianStatus(failure),
            risk_level=RiskLevel.HIGH,
            reason="synthetic",
        )
        monkeypatch.setattr(module, "evaluate_intent", lambda *args, **kwargs: decision)
    client = await module.create_guarded_async_openai(owner, api_key="synthetic-key")
    try:
        with pytest.raises(openai.PermissionDeniedError):
            await client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": "synthetic"}]
            )
    finally:
        await client.close()
    assert seen == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure",
    [
        "missing",
        "forged",
        "stale",
        "owner",
        "attempt",
        "target",
        "decision",
        "constraints",
        "unsigned",
        "tampered",
    ],
)
async def test_audit_receipt_is_current_signed_and_bound(
    policies, monkeypatch, failure
):
    # Standard library imports
    from dataclasses import replace

    # Third party imports
    import openai

    # Aetherra imports
    from Aetherra.guardian.models import GuardianStatus

    module = sdk()
    original = module.evaluate_intent
    previous = permit() if failure == "stale" else None

    def changed(intent, **kwargs):
        actual = intent
        if failure == "owner":
            actual = replace(intent, requester="lyrixa:chat")
        elif failure == "attempt":
            actual = replace(intent, metadata={**intent.metadata, "sdk_attempt_id": 1})
        elif failure == "target":
            actual = replace(
                intent, metadata={**intent.metadata, "sdk_target_digest": 1}
            )
        if failure == "decision":
            (policies.parent / "guardian_policy.json").write_text('{"default":"deny"}')
        decision = original(actual, **kwargs)
        if failure == "missing":
            return replace(decision, audit_id=None)
        if failure == "forged":
            return replace(decision, audit_id="f" * 64)
        if failure == "stale":
            return replace(decision, audit_id=previous.decision_audit_id)
        if failure == "decision":
            return replace(decision, status=GuardianStatus.ALLOW)
        if failure == "constraints":
            return replace(
                decision, constraints=("respect_existing_security_controls",)
            )
        if failure in {"unsigned", "tampered"}:
            path = policies.parent / ".aetherra/security/audit.jsonl"
            records = [json.loads(line) for line in path.read_text().splitlines()]
            if failure == "unsigned":
                records[-1].pop("signature")
            else:
                records[-1]["signature"] = "f" * 64
            path.write_text("\n".join(json.dumps(record) for record in records) + "\n")
        return decision

    monkeypatch.setattr(module, "evaluate_intent", changed)
    seen = []
    monkeypatch.setattr(
        module,
        "_async_inner_transport",
        lambda: httpx.MockTransport(
            lambda request: seen.append(request) or completion()
        ),
    )
    client = await module.create_guarded_async_openai(
        module.SdkOwner.CORE_LLM, api_key="synthetic-key"
    )
    try:
        with pytest.raises(openai.PermissionDeniedError):
            await client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": "synthetic"}]
            )
    finally:
        await client.close()
    assert seen == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "policy",
    [
        None,
        {"default": "allow", "deny": [123]},
        {"default": "allow", "allow": [{"requster": "*"}]},
    ],
)
async def test_strict_guardian_policy_cannot_fall_back(policies, monkeypatch, policy):
    module = sdk()
    monkeypatch.setenv("AETHERRA_GUARDIAN_REQUIRE_POLICY", "0")
    path = policies.parent / "guardian_policy.json"
    if policy is None:
        path.unlink()
    else:
        path.write_text(json.dumps(policy))
    seen = []
    async with httpx.AsyncClient(
        transport=module.GuardedAsyncTransport(
            module.SdkOwner.CORE_LLM,
            module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
            httpx.MockTransport(lambda request: seen.append(request) or completion()),
        )
    ) as client:
        assert (
            await client.post("https://synthetic.invalid/v1/chat/completions")
        ).status_code == 403
    assert seen == []


@pytest.mark.parametrize("policy", [{}, {"allow_domains": []}])
def test_strict_domains_do_not_inherit_production_grants(policies, monkeypatch, policy):
    # Aetherra imports
    from Aetherra.security.net_policy import is_domain_allowed

    monkeypatch.setenv("AETHERRA_PROFILE", "production")
    (policies / "net_policy.json").write_text(json.dumps(policy))
    assert not is_domain_allowed(
        "https://ungranted.aetherra.dev/v1/chat/completions",
        "core:llm",
        require_valid_policy=True,
    )


def test_synchronous_concurrent_close_releases_once(policies):
    # Standard library imports
    import threading
    import time

    module = sdk()
    baseline = module._LEASES
    entered, release = threading.Event(), threading.Event()

    class Content(httpx.SyncByteStream):
        close_calls = 0

        def __iter__(self):
            yield b"synthetic"

        def close(self):
            self.close_calls += 1
            entered.set()
            release.wait(1)

    content = Content()
    transport = module.GuardedSyncTransport(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        httpx.MockTransport(lambda _: httpx.Response(200, stream=content)),
    )
    response = transport.handle_request(
        httpx.Request("POST", "https://synthetic.invalid/v1/chat/completions")
    )
    first = threading.Thread(target=response.stream.close)
    second = threading.Thread(target=response.stream.close)
    first.start()
    assert entered.wait(1)
    second.start()
    time.sleep(0.01)
    release.set()
    first.join(2)
    second.join(2)
    transport.close()
    assert not first.is_alive()
    assert not second.is_alive()
    assert content.close_calls == 1
    assert baseline == module._LEASES


@pytest.mark.asyncio
async def test_shutdown_during_authorization_prevents_send(policies, monkeypatch):
    # Standard library imports
    import asyncio
    import threading

    module = sdk()
    original = module.authorize_sdk_send
    entered, release = threading.Event(), threading.Event()

    def slow(*args):
        result = original(*args)
        entered.set()
        release.wait(2)
        return result

    seen = []
    monkeypatch.setattr(module, "authorize_sdk_send", slow)
    transport = module.GuardedAsyncTransport(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        httpx.MockTransport(lambda request: seen.append(request) or completion()),
    )
    send = asyncio.create_task(
        transport.handle_async_request(
            httpx.Request("POST", "https://synthetic.invalid/v1/chat/completions")
        )
    )
    try:
        for _ in range(100):
            if entered.is_set():
                break
            await asyncio.sleep(0.005)
        assert entered.is_set()
        close = asyncio.create_task(transport.aclose())
        await asyncio.sleep(0.01)
        release.set()
        response = await send
        await close
        assert response.status_code == 403
        assert seen == []
        assert (
            module.get_sdk_egress_status(module.SdkOwner.CORE_LLM)["active_lease_count"]
            == 0
        )
    finally:
        release.set()
        await transport.aclose()


@pytest.mark.parametrize("mode", ["observe", "advisory", "invalid-mode"])
def test_non_enforcing_modes_deny(policies, monkeypatch, mode):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", mode)
    with pytest.raises(sdk().SdkEgressError):
        permit()


def test_strict_guardian_mode_is_supported(policies, monkeypatch):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "strict")
    assert permit().decision_audit_id


@pytest.mark.parametrize(
    "limits",
    [
        {"timeout_sec": 0},
        {"timeout_sec": True},
        {"max_concurrency": 0},
        {"max_concurrency": 1.5},
        {"unsupported_limit": 1},
    ],
)
def test_invalid_limits_deny(policies, limits):
    (policies / "capabilities.json").write_text(
        json.dumps(
            {
                "allow": {"core:llm": ["network:outbound"]},
                "limits": {"network:outbound": limits},
            }
        )
    )
    with pytest.raises(sdk().SdkEgressError):
        permit()


@pytest.mark.asyncio
async def test_async_transport_denial_never_delegates(policies):
    calls = []
    inner = httpx.MockTransport(
        lambda request: calls.append(request) or httpx.Response(200)
    )
    transport = sdk().GuardedAsyncTransport(
        sdk().SdkOwner.CORE_LLM,
        sdk().SdkEndpoint.parse("https://synthetic.invalid/v1"),
        inner,
    )
    async with httpx.AsyncClient(transport=transport) as client:
        response = await client.post("https://other.invalid/v1/chat/completions")
    assert response.status_code == 403
    assert calls == []


def test_sync_transport_permits_and_closes(policies):
    calls = []
    inner = httpx.MockTransport(
        lambda request: calls.append(request) or httpx.Response(200, json={})
    )
    transport = sdk().GuardedSyncTransport(
        sdk().SdkOwner.CORE_LLM,
        sdk().SdkEndpoint.parse("https://synthetic.invalid/v1"),
        inner,
    )
    with httpx.Client(transport=transport) as client:
        assert (
            client.post("https://synthetic.invalid/v1/chat/completions").status_code
            == 200
        )
    assert len(calls) == 1
    assert (
        sdk().get_sdk_egress_status(sdk().SdkOwner.CORE_LLM)["active_lease_count"] == 0
    )


@pytest.mark.asyncio
async def test_redirect_cannot_create_second_send(policies):
    calls = []
    inner = httpx.MockTransport(
        lambda request: (
            calls.append(request)
            or httpx.Response(302, headers={"Location": "https://other.invalid/stolen"})
        )
    )
    transport = sdk().GuardedAsyncTransport(
        sdk().SdkOwner.CORE_LLM,
        sdk().SdkEndpoint.parse("https://synthetic.invalid/v1"),
        inner,
    )
    async with httpx.AsyncClient(transport=transport, follow_redirects=True) as client:
        response = await client.post("https://synthetic.invalid/v1/chat/completions")
    assert response.status_code == 403
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_concurrency_lease_lives_until_stream_close(policies):
    (policies / "capabilities.json").write_text(
        json.dumps(
            {
                "allow": {"core:llm": ["network:outbound"]},
                "limits": {"network:outbound": {"max_concurrency": 1}},
            }
        )
    )

    class ContentStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b"synthetic"

    inner = httpx.MockTransport(
        lambda request: httpx.Response(200, stream=ContentStream())
    )
    transport = sdk().GuardedAsyncTransport(
        sdk().SdkOwner.CORE_LLM,
        sdk().SdkEndpoint.parse("https://synthetic.invalid/v1"),
        inner,
    )
    async with httpx.AsyncClient(transport=transport) as client:
        first = await client.send(
            client.build_request(
                "POST", "https://synthetic.invalid/v1/chat/completions"
            ),
            stream=True,
        )
        second = await client.post("https://synthetic.invalid/v1/chat/completions")
        assert second.status_code == 403
        await first.aclose()
        third = await client.post("https://synthetic.invalid/v1/chat/completions")
        assert third.status_code == 200


@pytest.mark.asyncio
async def test_slow_authorization_cancel_does_not_send(policies, monkeypatch):
    # Standard library imports
    import asyncio
    import threading

    module = sdk()
    original = module.authorize_sdk_send
    started = threading.Event()
    release = threading.Event()
    calls = []

    def slow(*args):
        result = original(*args)
        started.set()
        release.wait(2)
        return result

    monkeypatch.setattr(module, "authorize_sdk_send", slow)
    transport = module.GuardedAsyncTransport(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        httpx.MockTransport(
            lambda request: calls.append(request) or httpx.Response(200)
        ),
    )
    client = httpx.AsyncClient(transport=transport)
    task = asyncio.create_task(
        client.post("https://synthetic.invalid/v1/chat/completions")
    )
    try:
        for _ in range(100):
            if started.is_set():
                break
            await asyncio.sleep(0.005)
        assert started.is_set()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        release.set()
        await client.aclose()
        assert calls == []
        assert (
            module.get_sdk_egress_status(module.SdkOwner.CORE_LLM)[
                "policy_worker_count"
            ]
            == 0
        )
    finally:
        release.set()
        if not task.done():
            task.cancel()
        await client.aclose()


def completion():
    return httpx.Response(
        200,
        json={
            "id": "synthetic",
            "object": "chat.completion",
            "created": 0,
            "model": "gpt-4o",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "synthetic answer"},
                    "finish_reason": "stop",
                }
            ],
        },
    )


@pytest.mark.asyncio
async def test_concurrent_stream_close_releases_once(policies):
    # Standard library imports
    import asyncio

    entered = asyncio.Event()
    release = asyncio.Event()

    class Content(httpx.AsyncByteStream):
        close_calls = 0

        async def __aiter__(self):
            yield b"synthetic"

        async def aclose(self):
            self.close_calls += 1
            entered.set()
            await release.wait()

    content = Content()
    module = sdk()
    baseline = module._LEASES
    transport = module.GuardedAsyncTransport(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        httpx.MockTransport(lambda _: httpx.Response(200, stream=content)),
    )
    response = await transport.handle_async_request(
        httpx.Request("POST", "https://synthetic.invalid/v1/chat/completions")
    )
    first = asyncio.create_task(response.stream.aclose())
    await asyncio.wait_for(entered.wait(), 1)
    second = asyncio.create_task(response.stream.aclose())
    await asyncio.sleep(0.01)
    release.set()
    await asyncio.gather(first, second)
    await transport.aclose()
    assert content.close_calls == 1
    assert baseline == module._LEASES


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "timeout", ["invalid", {"read": "secret"}, {"read": float("nan")}]
)
async def test_invalid_request_timeout_cannot_leak_lease(policies, timeout):
    module = sdk()
    baseline = module._LEASES
    calls = []
    transport = module.GuardedAsyncTransport(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        httpx.MockTransport(lambda request: calls.append(request) or completion()),
    )
    request = httpx.Request(
        "POST",
        "https://synthetic.invalid/v1/chat/completions",
        extensions={"timeout": timeout},
    )
    try:
        response = await transport.handle_async_request(request)
        assert response.status_code == 403
    finally:
        await transport.aclose()
    assert calls == []
    assert baseline == module._LEASES


@pytest.mark.asyncio
async def test_outcome_audit_does_not_block_event_loop(policies, monkeypatch):
    # Standard library imports
    import asyncio
    import threading

    module = sdk()
    original = module.record_outcome
    entered, release = threading.Event(), threading.Event()

    def slow(*args):
        entered.set()
        release.wait(1)
        return original(*args)

    monkeypatch.setattr(module, "record_outcome", slow)
    transport = module.GuardedAsyncTransport(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        httpx.MockTransport(lambda _: completion()),
    )
    task = asyncio.create_task(
        transport.handle_async_request(
            httpx.Request("POST", "https://synthetic.invalid/v1/chat/completions")
        )
    )
    start = asyncio.get_running_loop().time()
    try:
        while not entered.is_set():
            await asyncio.sleep(0.002)
        assert asyncio.get_running_loop().time() - start < 0.5
    finally:
        release.set()
        await task
        await transport.aclose()


@pytest.mark.asyncio
async def test_denied_capability_has_signed_safe_record(policies):
    (policies / "capabilities.json").write_text('{"allow":{"core:llm":[]}}')
    calls = []
    module = sdk()
    async with httpx.AsyncClient(
        transport=module.GuardedAsyncTransport(
            module.SdkOwner.CORE_LLM,
            module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
            httpx.MockTransport(lambda request: calls.append(request) or completion()),
        )
    ) as client:
        assert (
            await client.post(
                "https://synthetic.invalid/v1/chat/completions",
                content="private-synthetic-body",
            )
        ).status_code == 403
    path = policies.parent / ".aetherra/security/audit.jsonl"
    assert path.exists()
    # Aetherra imports
    from Aetherra.security.audit_ledger import SecurityAuditLedger

    assert SecurityAuditLedger(path).verify_integrity(require_signed_records=True)
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert records[-1]["event_type"] == "sdk_egress_denied"
    assert records[-1]["details"]["code"] == "sdk_capability_denied"
    assert "private-synthetic-body" not in path.read_text()
    assert calls == []


@pytest.mark.asyncio
async def test_wrapper_constructor_failure_closes_inner(policies, monkeypatch):
    # Third party imports
    import openai

    class Inner(httpx.AsyncBaseTransport):
        closed = False

        async def handle_async_request(self, request):
            raise AssertionError("must not send")

        async def aclose(self):
            self.closed = True

    inner = Inner()
    module = sdk()
    monkeypatch.setattr(module, "_async_inner_transport", lambda: inner)

    def fail(**kwargs):
        raise RuntimeError("private-constructor-detail")

    monkeypatch.setattr(openai, "DefaultAsyncHttpxClient", fail)
    with pytest.raises(module.SdkEgressError, match="^sdk_client_unavailable$"):
        await module.create_guarded_async_openai(
            module.SdkOwner.CORE_LLM, api_key="synthetic-key"
        )
    assert inner.closed


@pytest.mark.asyncio
async def test_audit_failure_degrades_provider_and_cleanup_receipt(
    policies, monkeypatch
):
    # Aetherra imports
    from Aetherra.core import multi_llm_manager

    module = sdk()
    monkeypatch.setattr(module, "record_outcome", lambda *args: None)
    monkeypatch.setattr(
        module,
        "_async_inner_transport",
        lambda: httpx.MockTransport(lambda _: completion()),
    )
    provider = multi_llm_manager.OpenAIProvider()
    config = multi_llm_manager.LLMConfig(
        provider=multi_llm_manager.LLMProvider.OPENAI, model_name="gpt-4o", timeout=1
    )
    assert await provider.generate(config, "synthetic") == "synthetic answer"
    assert provider.get_lifecycle_status()["status"] == "degraded"
    assert provider.get_lifecycle_status()["egress"]["audit_failure_count"] > 0
    assert await provider.drain_pending_cleanup() is False


@pytest.mark.asyncio
async def test_closed_transport_cannot_send(policies):
    calls = []
    module = sdk()
    transport = module.GuardedAsyncTransport(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        httpx.MockTransport(lambda request: calls.append(request) or completion()),
    )
    await transport.aclose()
    response = await transport.handle_async_request(
        httpx.Request("POST", "https://synthetic.invalid/v1/chat/completions")
    )
    assert response.status_code == 403
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("close_delay", [0, 0.05])
async def test_bounded_close_retains_pending_stream(policies, monkeypatch, close_delay):
    # Standard library imports
    import asyncio

    module = sdk()
    gate = asyncio.Event()

    class Content(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b"synthetic"

        async def aclose(self):
            await gate.wait()
            await asyncio.sleep(close_delay)

    transport = module.GuardedAsyncTransport(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        httpx.MockTransport(lambda _: httpx.Response(200, stream=Content())),
    )
    await transport.handle_async_request(
        httpx.Request("POST", "https://synthetic.invalid/v1/chat/completions")
    )
    try:
        # The short deadline tests a blocked stream, not normal teardown work.
        with monkeypatch.context() as deadline:
            deadline.setattr(module, "_CLEANUP_SECONDS", 0.02)
            with pytest.raises(
                module.SdkEgressError, match="^sdk_cleanup_unconfirmed$"
            ):
                await asyncio.wait_for(transport.aclose(), 0.2)
        status = module.get_sdk_egress_status(module.SdkOwner.CORE_LLM)
        assert status["status"] == "degraded"
        assert status["active_lease_count"] == 1
    finally:
        gate.set()
        await transport.aclose()
    assert (
        module.get_sdk_egress_status(module.SdkOwner.CORE_LLM)["active_lease_count"]
        == 0
    )


@pytest.mark.asyncio
async def test_environment_proxies_cannot_replace_guard(policies, monkeypatch):
    # Third party imports
    import openai

    module = sdk()
    for name in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY"):
        monkeypatch.setenv(name, "http://proxy.invalid:3128")
    client = await module.create_guarded_async_openai(
        module.SdkOwner.CORE_LLM, api_key="synthetic-key"
    )
    try:
        assert isinstance(client._client._transport, module.GuardedAsyncTransport)
        assert client._client._trust_env is False
        assert client._client.follow_redirects is False
        assert not any(client._client._mounts.values())
        assert isinstance(client, openai.AsyncOpenAI)
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_active_authorization_is_not_unresolved_ownership(policies, monkeypatch):
    # Standard library imports
    import asyncio
    import threading

    module = sdk()
    original = module.authorize_sdk_send
    entered, release = threading.Event(), threading.Event()

    def slow(*args):
        entered.set()
        release.wait(2)
        return original(*args)

    monkeypatch.setattr(module, "authorize_sdk_send", slow)
    transport = module.GuardedAsyncTransport(
        module.SdkOwner.CORE_LLM,
        module.SdkEndpoint.parse("https://synthetic.invalid/v1"),
        httpx.MockTransport(lambda _: completion()),
    )
    task = asyncio.create_task(
        transport.handle_async_request(
            httpx.Request("POST", "https://synthetic.invalid/v1/chat/completions")
        )
    )
    try:
        for _ in range(100):
            if entered.is_set():
                break
            await asyncio.sleep(0.005)
        assert entered.is_set()
        assert (
            module.get_sdk_egress_status(module.SdkOwner.CORE_LLM)["status"]
            == "available"
        )
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert (
            module.get_sdk_egress_status(module.SdkOwner.CORE_LLM)["status"]
            == "degraded"
        )
    finally:
        release.set()
        await transport.aclose()
    assert (
        module.get_sdk_egress_status(module.SdkOwner.CORE_LLM)["status"] == "available"
    )


@pytest.mark.asyncio
async def test_native_sdk_retry_reauthorizes(policies, monkeypatch):
    module = sdk()
    seen = []

    async def handler(request):
        seen.append(request)
        return (
            httpx.Response(500, json={"error": {"message": "synthetic"}})
            if len(seen) == 1
            else completion()
        )

    monkeypatch.setattr(
        module, "_async_inner_transport", lambda: httpx.MockTransport(handler)
    )
    client = await module.create_guarded_async_openai(
        module.SdkOwner.CORE_LLM,
        api_key="synthetic-key",
        base_url="https://synthetic.invalid/v1",
    )
    try:
        result = await client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": "synthetic"}]
        )
        assert result.choices[0].message.content == "synthetic answer"
        assert client.max_retries == 2
    finally:
        await client.close()
    assert len(seen) == 2
    audit = policies.parent / ".aetherra/security/audit.jsonl"
    decisions = [
        json.loads(line)
        for line in audit.read_text().splitlines()
        if json.loads(line)["event_type"] == "guardian_decision"
    ]
    assert len(decisions) == 2
    assert decisions[0]["hash"] != decisions[1]["hash"]


@pytest.mark.asyncio
async def test_native_retry_revocation_never_delegates_twice(policies, monkeypatch):
    module = sdk()
    seen = []

    def handler(request):
        seen.append(request)
        (policies / "capabilities.json").write_text('{"allow":{"core:llm":[]}}')
        return httpx.Response(500, json={"error": {"message": "synthetic"}})

    monkeypatch.setattr(
        module, "_async_inner_transport", lambda: httpx.MockTransport(handler)
    )
    client = await module.create_guarded_async_openai(
        module.SdkOwner.CORE_LLM,
        api_key="synthetic-key",
        base_url="https://synthetic.invalid/v1",
    )
    # Third party imports
    import openai

    try:
        with pytest.raises(openai.PermissionDeniedError):
            await client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": "synthetic"}]
            )
    finally:
        await client.close()
    assert len(seen) == 1
