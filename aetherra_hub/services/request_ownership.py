"""Keep compatibility-Hub mutations serial while allowing bounded observation.

This is transport ownership, not an Engine lock. Direct Engine and Flask callers
retain their existing contracts. A stream worker can retain its request's lease
after the HTTP response has closed, until its actual work has stopped.
"""

from __future__ import annotations

# Standard library imports
import json
import threading
from contextvars import ContextVar

# Third party imports
from flask import g, request

# Local imports
from .chat_contract import normalize_trace_id, standard_headers

OBSERVATION_PATHS = frozenset(
    {"/health", "/api/hub/readiness", "/api/kernel/readiness", "/api/ai/status"}
)
_CHAT_PATHS = frozenset({"/api/ai/ask", "/api/ai/stream", "/api/lyrixa/chat"})
RESPONSE_CLOSE_KEY = "aetherra.hub.close_response"
_current_lease: ContextVar[_Lease | None] = ContextVar(
    "hub_request_lease", default=None
)


def busy_response(code="hub_busy", environ=None):
    """Reject without reading a prompt, dispatching work, or consuming an ID."""
    payload = {
        "ok": False,
        "error": {
            "code": code,
            "message": "Hub is busy; retry later",
            "retryable": True,
        },
    }
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-store",
        "Retry-After": "1",
    }
    if environ and environ.get("PATH_INFO") in _CHAT_PATHS:
        trace_id = normalize_trace_id(
            environ.get("HTTP_X_AETHERRA_TRACE_ID")
            or environ.get("HTTP_X_AETHERRA_TRACE")
        )
        payload["trace_id"] = trace_id
        headers.update(standard_headers(trace_id))
    body = json.dumps(payload).encode("utf-8")
    headers["Content-Length"] = str(len(body))
    return body, list(headers.items())


class _Lease:
    def __init__(self, owner, exclusive):
        self.owner = owner
        self.exclusive = exclusive
        self.references = 0

    def retain(self):
        with self.owner.condition:
            self.references += 1
        return _Handle(self)


class _Handle:
    def __init__(self, lease=None):
        self.lease = lease
        self.closed = False
        self.token = None

    def __enter__(self):
        self.token = _current_lease.set(self.lease)
        return self

    def __exit__(self, *_args):
        _current_lease.reset(self.token)
        self.close()

    def close(self):
        if self.lease is None:
            return
        owner = self.lease.owner
        with owner.condition:
            if self.closed:
                return
            self.closed = True
            self.lease.references -= 1
            if not self.lease.references:
                owner.active -= 1
                if self.lease.exclusive:
                    owner.exclusive = False
                owner.condition.notify_all()


def retain_current_request():
    """Own a worker until its context exits; standalone service calls are no-ops."""
    lease = _current_lease.get()
    return lease.retain() if lease is not None else _Handle()


class _OwnedResponse:
    def __init__(self, response, handle):
        self.response = response
        self.iterator = iter(response)
        self.handle = handle
        self.closed = False

    def __iter__(self):
        return self

    def __next__(self):
        token = _current_lease.set(self.handle.lease)
        try:
            return next(self.iterator)
        except StopIteration:
            # Application work is complete; do not hold its lease while the HTTP
            # server subsequently drains unread bytes or finishes socket framing.
            self.close()
            raise
        finally:
            _current_lease.reset(token)

    def close(self):
        if self.closed:
            return
        self.closed = True
        token = _current_lease.set(self.handle.lease)
        try:
            close = getattr(self.response, "close", None)
            if close is not None:
                close()
        finally:
            _current_lease.reset(token)
            self.handle.close()


class RequestOwnership:
    """Fail-fast admission: only the four audited observation routes overlap."""

    def __init__(self, app):
        self.app = app
        self.condition = threading.Condition()
        self.active = 0
        self.exclusive = False
        self.draining = False

    def __call__(self, environ, start_response):
        observation = (
            environ.get("REQUEST_METHOD") in {"GET", "HEAD"}
            and environ.get("PATH_INFO") in OBSERVATION_PATHS
        )
        with self.condition:
            if self.draining or (not observation and self.exclusive):
                rejection = "hub_draining" if self.draining else "hub_busy"
            else:
                rejection = None
                self.active += 1
                if not observation:
                    self.exclusive = True
                handle = _Lease(self, exclusive=not observation).retain()
        if rejection is not None:
            return self._reject(environ, start_response, rejection)
        token = _current_lease.set(handle.lease)
        try:
            response = _OwnedResponse(self.app(environ, start_response), handle)
            environ[RESPONSE_CLOSE_KEY] = response.close
            return response
        except BaseException:
            handle.close()
            raise
        finally:
            _current_lease.reset(token)

    def _reject(self, environ, start_response, code):
        body, headers = busy_response(code, environ)
        if not hasattr(self.app, "request_context"):
            start_response("503 Service Unavailable", headers)
            return [b"" if environ.get("REQUEST_METHOD") == "HEAD" else body]
        # Run only existing response decoration, outside the admission lock.
        # In particular preserve configured CORS without dispatching a view,
        # running admission hooks, reading the body, or consuming an ID.
        with self.app.request_context(environ):
            g.chat_trace_id = (
                dict(headers).get("X-Aetherra-Trace-Id") or normalize_trace_id()
            )
            if (
                code == "hub_busy"
                and request.method == "OPTIONS"
                and request.url_rule is not None
                and request.url_rule.provide_automatic_options
            ):
                response = self.app.make_default_options_response()
            else:
                response = self.app.response_class(body, status=503, headers=headers)
            response = self.app.process_response(response)
            return response(environ, start_response)

    def begin_drain(self):
        current = _current_lease.get()
        if current is not None and current.owner is self:
            raise RuntimeError("Hub cannot stop from its request worker")
        with self.condition:
            self.draining = True

    def wait_for_idle(self, timeout):
        with self.condition:
            return self.condition.wait_for(lambda: self.active == 0, timeout=timeout)
