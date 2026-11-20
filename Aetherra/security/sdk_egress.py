"""Security-owned mediation for trusted OpenAI SDK callers."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import threading
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

import httpx
from Aetherra.guardian import (
    GuardianMode,
    GuardianStatus,
    IntentDeclaration,
    evaluate_intent,
    guardian_enabled,
    guardian_mode,
    record_outcome,
)
from Aetherra.guardian.audit import list_guardian_audit_records
from Aetherra.guardian.paths import workspace_root
from Aetherra.security import capabilities, net_policy
from Aetherra.security.audit_ledger import SecurityAuditLedger


class SdkOwner(StrEnum):
    CORE_LLM = "core:llm"
    LYRIXA_CHAT = "lyrixa:chat"
    CORE_AI_RUNTIME = "core:ai_runtime"
    MEMORY_NARRATOR = "memory:narrator"
    LYRIXA_CONVERSATION = "agent:lyrixa_conversation"
    LYRIXA_ENHANCED_CONVERSATION = "agent:lyrixa_enhanced_conversation"
    LYRIXA_AI = "agent:lyrixa_ai"


class SdkEgressError(RuntimeError):
    """Fixed error codes only; no request or SDK error content."""


@dataclass(frozen=True, slots=True)
class SdkEndpoint:
    origin: tuple[str, str, int]
    resource_path: str

    @classmethod
    def parse(cls, base_url: str) -> SdkEndpoint:
        try:
            url = httpx.URL(base_url)
            if (
                url.scheme != "https"
                or not url.host
                or url.userinfo
                or url.query
                or url.fragment
                or url.port == 0
            ):
                raise ValueError
            host = url.raw_host.decode("ascii").lower()
            return cls(
                ("https", host, url.port if url.port is not None else 443),
                url.path.rstrip("/") + "/chat/completions",
            )
        except Exception:
            raise SdkEgressError("sdk_endpoint_invalid") from None

    def matches(self, method: str, url: httpx.URL) -> bool:
        return (
            method == "POST"
            and not url.userinfo
            and not url.query
            and not url.fragment
            and (
                url.scheme,
                url.raw_host.decode("ascii").lower(),
                url.port if url.port is not None else 443,
            )
            == self.origin
            and url.path == self.resource_path
        )


@dataclass(frozen=True, slots=True)
class SdkPermit:
    owner: SdkOwner
    attempt_id: str
    decision_audit_id: str
    timeout_sec: float | None
    max_concurrency: int | None


def _limits() -> tuple[float | None, int | None]:
    limits = capabilities.get_capability_limits("network:outbound", require_valid_policy=True)
    if set(limits) - {"timeout_sec", "max_concurrency"}:
        raise SdkEgressError("sdk_limits_invalid")
    timeout = limits.get("timeout_sec")
    count = limits.get("max_concurrency")
    if timeout is not None and (
        isinstance(timeout, bool)
        or not isinstance(timeout, int | float)
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise SdkEgressError("sdk_limits_invalid")
    if count is not None and (type(count) is not int or count <= 0):
        raise SdkEgressError("sdk_limits_invalid")
    return float(timeout) if timeout is not None else None, count


def authorize_sdk_send(
    owner: SdkOwner, endpoint: SdkEndpoint, method: str, url: httpx.URL
) -> SdkPermit:
    try:
        if not isinstance(owner, SdkOwner) or not endpoint.matches(method, url):
            raise SdkEgressError("sdk_endpoint_denied")
        configured_mode = os.environ.get("AETHERRA_GUARDIAN_MODE", "").strip()
        if configured_mode:
            GuardianMode(configured_mode.lower())
        if not guardian_enabled() or guardian_mode() not in {
            GuardianMode.ENFORCING,
            GuardianMode.STRICT,
        }:
            raise SdkEgressError("sdk_governance_unavailable")
        if not net_policy.is_domain_allowed(str(url), owner.value, require_valid_policy=True):
            raise SdkEgressError("sdk_domain_denied")
        if "network:outbound" not in capabilities.list_capabilities(
            owner.value, require_valid_policy=True
        ):
            raise SdkEgressError("sdk_capability_denied")
        timeout, count = _limits()
        attempt = str(uuid4())
        intent = IntentDeclaration(
            requester=owner.value,
            subsystem="network",
            action="network.request",
            target="network:" + endpoint.origin[1],
            purpose="Perform governed SDK inference request",
            capabilities=("network:outbound",),
            evidence=("sdk_transport_boundary",),
            metadata={
                "sdk_attempt_id": UUID(attempt).int,
                "method": method,
                "sdk_target_digest": int.from_bytes(
                    hashlib.sha256(
                        json.dumps([endpoint.origin, endpoint.resource_path]).encode("utf-8")
                    ).digest(),
                    "big",
                ),
                "port": endpoint.origin[2],
                "path_length": len(url.path),
            },
        )
        decision = evaluate_intent(
            intent,
            capability_checker=lambda requester, cap: cap
            in capabilities.list_capabilities(requester, require_valid_policy=True),
            write_audit=True,
            require_valid_policy=True,
        )
        if decision.status not in {GuardianStatus.ALLOW, GuardianStatus.ALLOW_LIMITED}:
            raise SdkEgressError("sdk_guardian_denied")
        if set(decision.constraints) - {
            "respect_existing_security_controls",
            "guardian_approval_consumed",
            "guardian_preauthorization_consumed",
            "rollback_missing_user_approved",
        }:
            raise SdkEgressError("sdk_constraints_unconfirmed")
        ledger = SecurityAuditLedger(workspace_root() / ".aetherra/security/audit.jsonl")
        if not decision.audit_id or not ledger.verify_integrity(require_signed_records=True):
            raise SdkEgressError("sdk_audit_unconfirmed")
        matched = next(
            (
                record
                for record in list_guardian_audit_records(limit=200)
                if record.get("hash") == decision.audit_id
            ),
            None,
        )
        from Aetherra.aetherra_core.system.security_system import redact_secrets

        expected = json.loads(json.dumps(redact_secrets(intent.to_audit_dict())))
        certified = json.loads(
            json.dumps(redact_secrets(decision.with_audit_id(None).to_audit_dict()))
        )
        if (
            matched is None
            or matched.get("event_type") != "guardian_decision"
            or matched.get("details", {}).get("intent") != expected
            or matched.get("details", {}).get("decision") != certified
        ):
            raise SdkEgressError("sdk_audit_unconfirmed")
        return SdkPermit(owner, attempt, decision.audit_id, timeout, count)
    except SdkEgressError as error:
        _audit_denial(owner, str(error))
        raise
    except Exception:
        _audit_denial(owner, "sdk_policy_unavailable")
        raise SdkEgressError("sdk_policy_unavailable") from None


def _audit_denial(owner: SdkOwner, code: str):
    try:
        SecurityAuditLedger(workspace_root() / ".aetherra/security/audit.jsonl").append(
            actor=owner.value if isinstance(owner, SdkOwner) else "security:sdk",
            event_type="sdk_egress_denied",
            details={"code": code},
        )
    except Exception:
        raise SdkEgressError("sdk_denial_audit_failed") from None


_LOCK = threading.RLock()
_CONTEXTS: set[_State] = set()
_LEASES = 0
_WORKER_SLOTS = threading.BoundedSemaphore(4)
_CLEANUP_SECONDS = 5.0


class _Job:
    def __init__(self, operation: Callable, args: tuple):
        self.future: Future = Future()
        self.released = False
        self.abandoned = False

        def run():
            if not self.future.set_running_or_notify_cancel():
                return
            try:
                self.future.set_result(operation(*args))
            except SdkEgressError as error:
                self.future.set_exception(error)
            except BaseException:
                self.future.set_exception(SdkEgressError("sdk_policy_unavailable"))

        self.thread = threading.Thread(target=run, name="aetherra-sdk-policy")


class _State:
    def __init__(self, owner: SdkOwner, endpoint: SdkEndpoint):
        if not isinstance(owner, SdkOwner):
            raise SdkEgressError("sdk_owner_invalid")
        self.owner = owner
        self.endpoint = endpoint
        self.scope = workspace_root()
        self.jobs: set[_Job] = set()
        self.streams: set = set()
        self.sends: set[asyncio.Task] = set()
        self.closed = False
        self.close_task: asyncio.Task | None = None
        self.errors = 0
        self.audit_errors = 0
        self.last_error = ""
        with _LOCK:
            _CONTEXTS.add(self)

    def prune(self):
        with _LOCK:
            for job in list(self.jobs):
                if job.future.done() and not job.thread.is_alive():
                    if not job.future.cancelled():
                        job.future.exception()
                    self.jobs.remove(job)
                    if not job.released:
                        job.released = True
                        _WORKER_SLOTS.release()
            if (
                self.closed
                and not self.jobs
                and not self.streams
                and not self.sends
                and not self.errors
                and (self.close_task is None or self.close_task.done())
            ):
                _CONTEXTS.discard(self)

    def outcome(self, permit: SdkPermit, status: str):
        try:
            if not record_outcome(permit.decision_audit_id, {"status": status}):
                raise SdkEgressError("sdk_outcome_audit_failed")
        except Exception:
            self.fail("sdk_outcome_audit_failed")

    def fail(self, code: str):
        with _LOCK:
            self.errors += 1
            if code in {
                "sdk_outcome_audit_failed",
                "sdk_denial_audit_failed",
                "sdk_audit_unconfirmed",
            }:
                self.audit_errors += 1
            self.last_error = code

    async def run_job(self, operation: Callable, *args):
        with _LOCK:
            states = list(_CONTEXTS)
        for state in states:
            state.prune()
        if not _WORKER_SLOTS.acquire(blocking=False):
            raise SdkEgressError("sdk_governance_busy")
        job = _Job(operation, args)
        with _LOCK:
            self.jobs.add(job)
        try:
            job.thread.start()
        except BaseException:
            with _LOCK:
                self.jobs.remove(job)
            _WORKER_SLOTS.release()
            raise
        try:
            future = asyncio.wrap_future(job.future)
            future.add_done_callback(lambda done: None if done.cancelled() else done.exception())
            result = await asyncio.shield(future)
            while job.thread.is_alive():
                await asyncio.sleep(0.001)
            return result
        except asyncio.CancelledError:
            job.abandoned = True
            raise
        finally:
            self.prune()

    async def async_outcome(self, permit: SdkPermit, status: str):
        try:
            await self.run_job(self.outcome, permit, status)
        except SdkEgressError:
            self.fail("sdk_outcome_audit_failed")

    def reserve(self, permit: SdkPermit):
        global _LEASES
        with _LOCK:
            if self.closed:
                raise SdkEgressError("sdk_transport_closed")
            if permit.max_concurrency is not None and permit.max_concurrency <= _LEASES:
                raise SdkEgressError("sdk_concurrency_exceeded")
            _LEASES += 1

    def release(self):
        global _LEASES
        with _LOCK:
            _LEASES -= 1

    def deny(self, code: str) -> httpx.Response:
        self.last_error = code
        if code in {"sdk_denial_audit_failed", "sdk_audit_unconfirmed"}:
            self.fail(code)
        return httpx.Response(
            403,
            json={
                "error": {
                    "code": "aetherra_policy_denied",
                    "message": "Request blocked by Aetherra network governance.",
                }
            },
        )


def get_sdk_egress_status(owner: SdkOwner) -> dict:
    with _LOCK:
        states = [
            state for state in _CONTEXTS if state.owner == owner and state.scope == workspace_root()
        ]
    for state in states:
        state.prune()
    with _LOCK:
        workers = sum(len(state.jobs) for state in states)
        streams = sum(len(state.streams) for state in states)
        failures = sum(state.errors for state in states)
        audit_failures = sum(state.audit_errors for state in states)
        abandoned = sum(job.abandoned or state.closed for state in states for job in state.jobs)
        cleanup = sum(
            state.close_task is not None and not state.close_task.done() for state in states
        )
    result = {
        "status": "degraded" if failures or abandoned or cleanup else "available",
        "active_lease_count": streams,
        "policy_worker_count": workers,
        "unresolved_stream_count": streams if failures or cleanup else 0,
        "pending_cleanup_count": cleanup,
        "audit_failure_count": audit_failures,
    }
    if failures or abandoned or cleanup:
        result["error"] = {"code": "sdk_ownership_unconfirmed"}
    return result


def _clamp_timeout(request: httpx.Request, permit: SdkPermit):
    if permit.timeout_sec is None:
        return
    original = request.extensions.get("timeout", {})
    if not isinstance(original, dict):
        raise SdkEgressError("sdk_timeout_invalid")
    if any(
        value is not None
        and (
            isinstance(value, bool)
            or not isinstance(value, int | float)
            or not math.isfinite(value)
            or value <= 0
        )
        for value in original.values()
    ):
        raise SdkEgressError("sdk_timeout_invalid")
    request.extensions["timeout"] = {
        key: min(value, permit.timeout_sec) if value is not None else permit.timeout_sec
        for key, value in ((key, original.get(key)) for key in ("connect", "read", "write", "pool"))
    }


class _SyncStream(httpx.SyncByteStream):
    def __init__(self, state, inner, permit):
        self.state, self.inner, self.permit = state, inner, permit
        self.closed = False
        self._close_lock = threading.RLock()
        with _LOCK:
            state.streams.add(self)

    def __iter__(self):
        try:
            yield from self.inner
        finally:
            self.close()

    def close(self):
        with self._close_lock:
            self._close()

    def _close(self):
        if self.closed:
            return
        try:
            self.inner.close()
        except Exception:
            self.state.fail("sdk_stream_close_failed")
            raise SdkEgressError("sdk_stream_close_failed") from None
        self.closed = True
        self.state.release()
        with _LOCK:
            self.state.streams.discard(self)
        self.state.outcome(self.permit, "stream_closed")


class _AsyncStream(httpx.AsyncByteStream):
    def __init__(self, state, inner, permit):
        self.state, self.inner, self.permit = state, inner, permit
        self.closed = False
        self._close_task: asyncio.Task | None = None
        with _LOCK:
            state.streams.add(self)

    async def __aiter__(self):
        try:
            async for chunk in self.inner:
                yield chunk
        finally:
            await self.aclose()

    async def aclose(self):
        if self.closed:
            return
        if self._close_task is None:
            self._close_task = asyncio.create_task(self._close())
            self._close_task.add_done_callback(
                lambda done: None if done.cancelled() else done.exception()
            )
        await asyncio.shield(self._close_task)

    async def _close(self):
        try:
            await self.inner.aclose()
        except BaseException:
            self.state.fail("sdk_stream_close_failed")
            raise SdkEgressError("sdk_stream_close_failed") from None
        self.closed = True
        self.state.release()
        with _LOCK:
            self.state.streams.discard(self)
        await self.state.async_outcome(self.permit, "stream_closed")


class GuardedSyncTransport(httpx.BaseTransport):
    def __init__(self, owner, endpoint, inner):
        self.state = _State(owner, endpoint)
        self.inner = inner

    def handle_request(self, request):
        if self.state.closed:
            return self.state.deny("sdk_transport_closed")
        try:
            permit = authorize_sdk_send(
                self.state.owner, self.state.endpoint, request.method, request.url
            )
            _clamp_timeout(request, permit)
            self.state.reserve(permit)
        except SdkEgressError as error:
            return self.state.deny(str(error))
        lease_owned = True
        try:
            response = self.inner.handle_request(request)
            if response.is_closed:
                self.state.release()
                lease_owned = False
                self.state.outcome(permit, "stream_closed")
            else:
                response.stream = _SyncStream(self.state, response.stream, permit)
                lease_owned = False
            if 300 <= response.status_code < 400:
                response.close()
                return self.state.deny("sdk_redirect_denied")
            return response
        except BaseException:
            if lease_owned:
                self.state.release()
            self.state.outcome(permit, "transport_failed")
            raise

    def close(self):
        try:
            for stream in list(self.state.streams):
                stream.close()
        finally:
            self.inner.close()
        self.state.closed = True
        self.state.prune()


class GuardedAsyncTransport(httpx.AsyncBaseTransport):
    def __init__(self, owner, endpoint, inner):
        self.state = _State(owner, endpoint)
        self.inner = inner

    async def _authorize(self, request):
        return await self.state.run_job(
            authorize_sdk_send, self.state.owner, self.state.endpoint, request.method, request.url
        )

    async def handle_async_request(self, request):
        task = asyncio.current_task()
        with _LOCK:
            if self.state.closed:
                return self.state.deny("sdk_transport_closed")
            self.state.sends.add(task)
        try:
            return await self._dispatch(request)
        finally:
            with _LOCK:
                self.state.sends.discard(task)

    async def _dispatch(self, request):
        if self.state.closed:
            return self.state.deny("sdk_transport_closed")
        try:
            permit = await self._authorize(request)
            _clamp_timeout(request, permit)
            self.state.reserve(permit)
        except SdkEgressError as error:
            return self.state.deny(str(error))
        lease_owned = True
        try:
            response = await self.inner.handle_async_request(request)
            if response.is_closed:
                self.state.release()
                lease_owned = False
                await self.state.async_outcome(permit, "stream_closed")
            else:
                response.stream = _AsyncStream(self.state, response.stream, permit)
                lease_owned = False
            if 300 <= response.status_code < 400:
                await response.aclose()
                return self.state.deny("sdk_redirect_denied")
            return response
        except BaseException:
            if lease_owned:
                self.state.release()
            await self.state.async_outcome(permit, "transport_failed")
            raise

    async def aclose(self):
        self.state.closed = True
        if self.state.close_task is None:
            self.state.close_task = asyncio.create_task(self._close())
            self.state.close_task.add_done_callback(
                lambda done: None if done.cancelled() else done.exception()
            )
        done, _ = await asyncio.wait({self.state.close_task}, timeout=_CLEANUP_SECONDS)
        if not done:
            raise SdkEgressError("sdk_cleanup_unconfirmed")
        self.state.close_task.result()
        self.state.prune()

    async def _close(self):
        try:
            while self.state.sends:
                await asyncio.sleep(0.005)
            for stream in list(self.state.streams):
                await stream.aclose()
            while self.state.jobs:
                self.state.prune()
                if self.state.jobs:
                    await asyncio.sleep(0.005)
        finally:
            try:
                await self.inner.aclose()
            except BaseException:
                self.state.fail("sdk_transport_close_failed")
                raise SdkEgressError("sdk_transport_close_failed") from None


def _sync_inner_transport() -> httpx.BaseTransport:
    return httpx.HTTPTransport(trust_env=False)


def _async_inner_transport() -> httpx.AsyncBaseTransport:
    return httpx.AsyncHTTPTransport(trust_env=False)


def _client_settings(owner, api_key, base_url, organization, project):
    if not isinstance(owner, SdkOwner):
        raise SdkEgressError("sdk_owner_invalid")
    if not isinstance(api_key, str) or not api_key.strip():
        raise SdkEgressError("sdk_credentials_unavailable")
    target = (
        base_url
        if base_url is not None
        else os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    )
    endpoint = SdkEndpoint.parse(target)
    return endpoint, {
        "api_key": api_key,
        "base_url": target,
        "organization": organization,
        "project": project,
    }


def create_guarded_sync_openai(
    owner: SdkOwner,
    *,
    api_key: str,
    base_url: str | None = None,
    organization: str | None = None,
    project: str | None = None,
):
    endpoint, settings = _client_settings(owner, api_key, base_url, organization, project)
    import openai

    transport = GuardedSyncTransport(owner, endpoint, _sync_inner_transport())
    http_client = None
    try:
        http_client = openai.DefaultHttpxClient(
            transport=transport, follow_redirects=False, trust_env=False
        )
        return openai.OpenAI(http_client=http_client, **settings)
    except Exception:
        if http_client is None:
            transport.close()
        else:
            http_client.close()
        raise SdkEgressError("sdk_client_unavailable") from None


async def create_guarded_async_openai(
    owner: SdkOwner,
    *,
    api_key: str,
    base_url: str | None = None,
    organization: str | None = None,
    project: str | None = None,
):
    endpoint, settings = _client_settings(owner, api_key, base_url, organization, project)
    import openai

    transport = GuardedAsyncTransport(owner, endpoint, _async_inner_transport())
    http_client = None
    try:
        http_client = openai.DefaultAsyncHttpxClient(
            transport=transport, follow_redirects=False, trust_env=False
        )
        return openai.AsyncOpenAI(http_client=http_client, **settings)
    except Exception:
        if http_client is None:
            await transport.aclose()
        else:
            await http_client.aclose()
        raise SdkEgressError("sdk_client_unavailable") from None
