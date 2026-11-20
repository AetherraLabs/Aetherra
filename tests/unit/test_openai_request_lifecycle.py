"""Offline acceptance of canonical OpenAI request ownership."""

import asyncio
import inspect
import json
import socket
import sys
import threading
import time
from types import SimpleNamespace

import httpx
import pytest

from Aetherra.core import multi_llm_manager as module


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setenv("AETHERRA_SKIP_DOTENV", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://synthetic.invalid/v1")
    for name in ("OPENAI_ORG_ID", "OPENAI_PROJECT_ID"):
        monkeypatch.delenv(name, raising=False)

    def forbidden(*args, **kwargs):
        raise AssertionError("network access forbidden")

    original_connect = socket.socket.connect

    def connect(sock, address):
        if address[0] in {"127.0.0.1", "::1"} and any(
            frame.function in {"socketpair", "_socketpair", "_fallback_socketpair"}
            and frame.frame.f_globals.get("__name__") == "socket"
            for frame in inspect.stack()
        ):
            return original_connect(sock, address)
        return forbidden()

    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", connect)


class FakeAsyncClient:
    def __init__(self, settings, *, content="synthetic answer", fail=False):
        self.settings = settings
        self.content = content
        self.fail = fail
        self.started = asyncio.Event()
        self.close_started = asyncio.Event()
        self.request_gate = None
        self.close_gate = None
        self.close_error = False
        self.cancelled = False
        self.closed = False
        self.close_calls = 0
        self.request_settings = None
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    async def create(self, **kwargs):
        self.request_settings = kwargs
        self.started.set()
        try:
            if self.request_gate is not None:
                await self.request_gate.wait()
            if self.fail:
                raise RuntimeError("synthetic private failure")
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))]
            )
        except asyncio.CancelledError:
            self.cancelled = True
            raise

    async def close(self):
        self.close_calls += 1
        self.close_started.set()
        if self.close_gate is not None:
            await self.close_gate.wait()
        if self.close_error:
            raise RuntimeError("synthetic private close failure")
        await self.settings["http_client"].aclose()
        self.closed = True

    def is_closed(self):
        return self.closed


@pytest.fixture
def factory(monkeypatch):
    clients = []
    sync_clients = []
    options = {}

    def make_async(**settings):
        client = FakeAsyncClient(settings, **options)
        clients.append(client)
        return client

    def make_sync(**settings):
        def create(**kwargs):
            time.sleep(0.06)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(message=SimpleNamespace(content="synthetic answer"))
                ]
            )

        client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=create))
        )
        sync_clients.append(client)
        return client

    monkeypatch.setitem(
        sys.modules,
        "openai",
        SimpleNamespace(
            OpenAI=make_sync,
            AsyncOpenAI=make_async,
            DefaultAsyncHttpxClient=httpx.AsyncClient,
            DefaultHttpxClient=httpx.Client,
        ),
    )
    return SimpleNamespace(clients=clients, sync_clients=sync_clients, options=options)


def config():
    return module.LLMConfig(
        provider=module.LLMProvider.OPENAI, model_name="gpt-4o", timeout=1.0
    )


def test_constructor_does_not_open_transport(factory):
    module.OpenAIProvider()
    assert factory.clients == []
    assert factory.sync_clients == []


@pytest.mark.asyncio
async def test_generate_yields_and_obeys_outer_deadline(factory):
    original_factory = sys.modules["openai"].AsyncOpenAI

    def gated(**settings):
        client = original_factory(**settings)
        client.request_gate = asyncio.Event()
        return client

    sys.modules["openai"].AsyncOpenAI = gated
    # Construction captures the SDK factory; set the gate before constructing.
    provider = module.OpenAIProvider()
    progressed = asyncio.Event()

    async def companion():
        await asyncio.sleep(0)
        progressed.set()

    observer = asyncio.create_task(companion())
    try:
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(
                provider.generate(config(), "synthetic prompt"), 0.02
            )
        assert progressed.is_set()
        assert factory.clients[0].cancelled
        assert factory.clients[0].is_closed()
    finally:
        await observer


@pytest.mark.asyncio
async def test_success_closes_request_client(factory, monkeypatch):
    provider = module.OpenAIProvider()
    monkeypatch.setenv("OPENAI_API_KEY", "changed-synthetic-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://changed.invalid/v1")
    assert (
        await provider.generate(
            config(), "synthetic prompt", temperature=0.3, max_tokens=7
        )
        == "synthetic answer"
    )
    assert len(factory.clients) == 1
    client = factory.clients[0]
    assert client.is_closed()
    assert client.close_calls == 1
    assert client.settings["api_key"] == "synthetic-test-key"
    assert client.settings["base_url"] == "https://synthetic.invalid/v1"
    assert "max_retries" not in client.settings
    assert client.request_settings == {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "synthetic prompt"}],
        "temperature": 0.3,
        "max_tokens": 7,
        "timeout": 1.0,
    }


@pytest.mark.asyncio
async def test_failure_closes_request_client(factory):
    factory.options["fail"] = True
    with pytest.raises(RuntimeError, match="^openai_generation_failed$"):
        await module.OpenAIProvider().generate(config(), "synthetic prompt")
    assert factory.clients[0].is_closed()
    assert factory.clients[0].close_calls == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("content", [None, "", "   ", 42])
async def test_invalid_response_is_not_success(factory, content):
    factory.options["content"] = content
    with pytest.raises(RuntimeError, match="^openai_response_invalid$"):
        await module.OpenAIProvider().generate(config(), "synthetic prompt")
    assert factory.clients[0].is_closed()


def test_missing_key_does_not_construct_transport(factory, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY")
    with pytest.raises(RuntimeError, match="^openai_credentials_unavailable$"):
        module.OpenAIProvider()
    assert factory.clients == []


@pytest.mark.parametrize("endpoint", ["", "   "])
def test_empty_endpoint_cannot_substitute_production(factory, monkeypatch, endpoint):
    monkeypatch.setenv("OPENAI_BASE_URL", endpoint)
    with pytest.raises(RuntimeError, match="^openai_endpoint_invalid$"):
        module.OpenAIProvider()
    assert factory.clients == []


@pytest.mark.parametrize("key", ["", "   "])
def test_blank_credentials_are_unavailable(factory, monkeypatch, key):
    monkeypatch.setenv("OPENAI_API_KEY", key)
    with pytest.raises(RuntimeError, match="^openai_credentials_unavailable$"):
        module.OpenAIProvider()
    assert factory.clients == []


def gated_provider(factory, *, request=False, close=False, close_error=False):
    make = sys.modules["openai"].AsyncOpenAI

    def gated(**settings):
        client = make(**settings)
        client.request_gate = asyncio.Event() if request else None
        client.close_gate = asyncio.Event() if close else None
        client.close_error = close_error
        return client

    sys.modules["openai"].AsyncOpenAI = gated
    return module.OpenAIProvider()


@pytest.mark.asyncio
async def test_repeated_cancellation_does_not_detach_close(factory):
    provider = gated_provider(factory, request=True, close=True)
    task = asyncio.create_task(provider.generate(config(), "synthetic prompt"))
    await asyncio.sleep(0)
    client = factory.clients[0]
    await client.started.wait()
    task.cancel()
    await client.close_started.wait()
    task.cancel()
    await asyncio.sleep(0)
    client.close_gate.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert client.is_closed()
    assert client.close_calls == 1
    assert provider.get_lifecycle_status()["unresolved_cleanup_count"] == 0


@pytest.mark.asyncio
async def test_close_failure_is_degraded(factory):
    provider = gated_provider(factory, close_error=True)
    with pytest.raises(RuntimeError, match="^openai_cleanup_failed$"):
        await provider.generate(config(), "synthetic prompt")
    status = provider.get_lifecycle_status()
    assert status["status"] == "degraded"
    assert status["unresolved_cleanup_count"] == 1
    assert "synthetic private" not in str(status)
    assert await provider.drain_pending_cleanup(timeout=0) is False


@pytest.mark.asyncio
async def test_close_deadline_retains_ownership(factory, monkeypatch):
    monkeypatch.setattr(module, "_OPENAI_CLEANUP_TIMEOUT_SECONDS", 0.02, raising=False)
    provider = gated_provider(factory, close=True)
    try:
        with pytest.raises(RuntimeError, match="^openai_cleanup_unconfirmed$"):
            await asyncio.wait_for(provider.generate(config(), "synthetic prompt"), 0.5)
        assert provider.get_lifecycle_status()["unresolved_cleanup_count"] == 1
        with pytest.raises(RuntimeError, match="^openai_cleanup_unconfirmed$"):
            await provider.generate(config(), "another synthetic prompt")
    finally:
        if factory.clients:
            factory.clients[0].close_gate.set()
    assert await provider.drain_pending_cleanup(timeout=0.5) is True
    assert provider.get_lifecycle_status()["status"] == "available"


@pytest.mark.asyncio
async def test_concurrent_requests_have_independent_clients(factory):
    provider = gated_provider(factory, request=True)
    tasks = [
        asyncio.create_task(provider.generate(config(), "synthetic prompt"))
        for _ in range(2)
    ]
    await asyncio.sleep(0)
    try:
        assert provider.get_lifecycle_status()["active_request_count"] == 2
        assert len(factory.clients) == 2
        assert await provider.drain_pending_cleanup(timeout=0) is False
        assert all(client.close_calls == 0 for client in factory.clients)
    finally:
        for client in factory.clients:
            client.request_gate.set()
        await asyncio.gather(*tasks)
    assert all(
        client.is_closed() and client.close_calls == 1 for client in factory.clients
    )
    assert await provider.drain_pending_cleanup(timeout=0) is True


@pytest.mark.asyncio
@pytest.mark.parametrize("timeout", [-1, float("inf"), float("nan"), True])
async def test_drain_rejects_invalid_bound(factory, timeout):
    with pytest.raises(ValueError, match="^llm_cleanup_timeout_invalid$"):
        await module.OpenAIProvider().drain_pending_cleanup(timeout=timeout)


def test_requests_from_distinct_loops_do_not_reuse_client(factory):
    provider = module.OpenAIProvider()
    for _ in range(2):
        assert (
            asyncio.run(provider.generate(config(), "synthetic prompt"))
            == "synthetic answer"
        )
    assert len(factory.clients) == 2
    assert all(client.is_closed() for client in factory.clients)


@pytest.mark.asyncio
async def test_foreign_loop_cleanup_is_reported_not_awaited(factory, monkeypatch):
    monkeypatch.setattr(module, "_OPENAI_CLEANUP_TIMEOUT_SECONDS", 0.02)
    provider = gated_provider(factory, close=True)
    ready = threading.Event()
    state = {}
    failures = []

    async def own_loop():
        state["loop"] = asyncio.get_running_loop()
        try:
            with pytest.raises(RuntimeError, match="^openai_cleanup_unconfirmed$"):
                await provider.generate(config(), "synthetic prompt")
            ready.set()
            await factory.clients[0].close_gate.wait()
            assert await provider.drain_pending_cleanup(timeout=0.5)
        except BaseException as error:
            failures.append(error)
            ready.set()

    thread = threading.Thread(target=lambda: asyncio.run(own_loop()))
    thread.start()
    try:
        assert ready.wait(2)
        assert failures == []
        assert await provider.drain_pending_cleanup(timeout=0.01) is False
        assert provider.get_lifecycle_status()["unresolved_cleanup_count"] == 1
    finally:
        if factory.clients and not state["loop"].is_closed():
            state["loop"].call_soon_threadsafe(factory.clients[0].close_gate.set)
        thread.join(2)
    assert not thread.is_alive()
    assert failures == []
    assert provider.get_lifecycle_status()["unresolved_cleanup_count"] == 0


def sdk_provider(monkeypatch, handler):
    import httpx
    import openai

    from Aetherra.security import sdk_egress

    monkeypatch.setattr(
        sdk_egress, "_async_inner_transport", lambda: httpx.MockTransport(handler)
    )

    real_factory = openai.AsyncOpenAI
    clients = []
    transports = []

    def create(**settings):
        transport = settings["http_client"]
        client = real_factory(**settings)
        clients.append(client)
        transports.append(transport)
        return client

    monkeypatch.setattr(openai, "AsyncOpenAI", create)
    return module.OpenAIProvider(), clients, transports


@pytest.fixture
def sdk_policies(tmp_path, monkeypatch):
    return configure_sdk_policies(tmp_path, monkeypatch)


def configure_sdk_policies(tmp_path, monkeypatch):
    directory = tmp_path / "policy"
    directory.mkdir()
    principals = [
        "core:llm",
        "lyrixa:chat",
        "core:ai_runtime",
        "memory:narrator",
        "agent:lyrixa_conversation",
        "agent:lyrixa_enhanced_conversation",
        "agent:lyrixa_ai",
    ]
    (directory / "capabilities.json").write_text(
        json.dumps(
            {
                "allow": {name: ["network:outbound"] for name in principals},
                "limits": {
                    "network:outbound": {"timeout_sec": 1, "max_concurrency": 2}
                },
            }
        ),
        encoding="utf-8",
    )
    (directory / "net_policy.json").write_text(
        json.dumps(
            {
                "allow_domains": ["synthetic.invalid"],
                "deny_domains": [],
            }
        ),
        encoding="utf-8",
    )
    guardian = tmp_path / "guardian_policy.json"
    guardian.write_text(
        json.dumps(
            {
                "default": "deny",
                "allow": [
                    {
                        "requester": name,
                        "subsystem": "network",
                        "action": "network.request",
                        "target": "network:synthetic.invalid",
                    }
                    for name in principals
                ],
            }
        ),
        encoding="utf-8",
    )
    for name, value in {
        "AETHERRA_PROFILE": "test",
        "AETHERRA_WORKSPACE_ROOT": str(tmp_path),
        "AETHERRA_POLICY_HOME": str(directory),
        "AETHERRA_REQUIRE_CAPABILITIES": "1",
        "AETHERRA_NET_STRICT": "1",
        "AETHERRA_GUARDIAN_ENABLED": "1",
        "AETHERRA_GUARDIAN_MODE": "enforcing",
        "AETHERRA_GUARDIAN_REQUIRE_POLICY": "1",
        "AETHERRA_GUARDIAN_POLICY": str(guardian),
        "AETHERRA_GUARDIAN_STATE_DIR": str(tmp_path / "guardian"),
    }.items():
        monkeypatch.setenv(name, value)
    for name in (
        "AETHERRA_PROD_UNSAFE_ALLOW",
        "AETHERRA_GUARDIAN_APPROVAL_ID",
        "AETHERRA_GUARDIAN_POLICY_HOME",
    ):
        monkeypatch.delenv(name, raising=False)
    return directory


def completion_response():
    import httpx

    return httpx.Response(
        200,
        json={
            "id": "synthetic-completion",
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
async def test_installed_sdk_response_closes_both_clients(monkeypatch, sdk_policies):
    seen = []

    async def handler(request):
        seen.append(request)
        return completion_response()

    provider, clients, transports = sdk_provider(monkeypatch, handler)
    assert await provider.generate(config(), "synthetic prompt") == "synthetic answer"
    assert len(seen) == 1
    assert clients[0].max_retries == 2
    assert clients[0].is_closed()
    assert transports[0].is_closed
    assert provider.get_lifecycle_status()["unresolved_cleanup_count"] == 0


@pytest.mark.asyncio
async def test_installed_sdk_error_closes_both_clients(monkeypatch, sdk_policies):
    import httpx

    async def handler(request):
        return httpx.Response(
            401, json={"error": {"message": "synthetic private error"}}
        )

    provider, clients, transports = sdk_provider(monkeypatch, handler)
    with pytest.raises(RuntimeError, match="^openai_generation_failed$"):
        await provider.generate(config(), "synthetic prompt")
    assert clients[0].is_closed()
    assert transports[0].is_closed


@pytest.mark.asyncio
async def test_installed_sdk_cancellation_reaches_transport(monkeypatch, sdk_policies):
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def handler(request):
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            raise

    provider, clients, transports = sdk_provider(monkeypatch, handler)
    task = asyncio.create_task(provider.generate(config(), "synthetic prompt"))
    await asyncio.wait_for(started.wait(), 1.0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert cancelled.is_set()
    assert clients[0].is_closed()
    assert transports[0].is_closed


def test_public_sync_facade_uses_fresh_sdk_clients(monkeypatch, sdk_policies):
    provider, clients, transports = sdk_provider(
        monkeypatch, lambda _: completion_response()
    )
    manager = object.__new__(module.MultiLLMManager)
    manager.providers = {module.LLMProvider.OPENAI: provider}
    manager._enabled_providers = frozenset(manager.providers)
    manager.current_model = config()
    for _ in range(2):
        assert manager.generate_response_sync("synthetic prompt") == "synthetic answer"
    assert len(clients) == 2
    assert clients[0] is not clients[1]
    assert all(client.is_closed() for client in clients)
    assert all(transport.is_closed for transport in transports)


@pytest.mark.asyncio
async def test_failed_client_construction_has_no_owned_transport(factory):
    def fail(**kwargs):
        raise RuntimeError("synthetic-private-constructor-detail")

    sys.modules["openai"].AsyncOpenAI = fail
    provider = module.OpenAIProvider()
    with pytest.raises(RuntimeError, match="^openai_client_unavailable$"):
        await provider.generate(config(), "synthetic prompt")
    assert factory.clients == []
    assert provider.get_lifecycle_status()["active_request_count"] == 0


@pytest.mark.asyncio
async def test_missing_choices_is_invalid_and_client_closes(factory, monkeypatch):
    async def missing(self, **kwargs):
        return SimpleNamespace(choices=[])

    monkeypatch.setattr(FakeAsyncClient, "create", missing)
    with pytest.raises(RuntimeError, match="^openai_response_invalid$"):
        await module.OpenAIProvider().generate(config(), "synthetic prompt")
    assert factory.clients[0].is_closed()


@pytest.mark.asyncio
async def test_manager_reports_and_retains_failed_cleanup(factory):
    provider = gated_provider(factory, close_error=True)
    manager = object.__new__(module.MultiLLMManager)
    manager.providers = {module.LLMProvider.OPENAI: provider}
    manager._enabled_providers = frozenset(manager.providers)
    manager.current_model = config()
    with pytest.raises(RuntimeError, match="^openai_cleanup_failed$"):
        await manager.generate_response("synthetic prompt")
    assert manager.get_lifecycle_status() == {
        "status": "degraded",
        "active_request_count": 0,
        "unresolved_cleanup_count": 1,
        "error": {"code": "llm_cleanup_unconfirmed"},
    }
    assert await manager.drain_pending_cleanup(timeout=0) is False


@pytest.mark.asyncio
async def test_active_generation_is_not_a_confirmed_drain(factory):
    provider = gated_provider(factory, request=True)
    manager = object.__new__(module.MultiLLMManager)
    manager.providers = {module.LLMProvider.OPENAI: provider}
    manager._enabled_providers = frozenset(manager.providers)
    manager.current_model = config()
    task = asyncio.create_task(manager.generate_response("synthetic prompt"))
    try:
        await asyncio.sleep(0)
        await factory.clients[0].started.wait()
        assert provider.get_lifecycle_status()["active_request_count"] == 1
        assert await manager.drain_pending_cleanup(timeout=0) is False
        assert not task.done()
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    assert factory.clients[0].is_closed()
    assert await manager.drain_pending_cleanup(timeout=0.5) is True
