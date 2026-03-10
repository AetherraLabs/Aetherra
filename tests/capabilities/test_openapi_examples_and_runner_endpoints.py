"""Capabilities test: OpenAPI examples present and endpoints work via runner.

This test suite starts the Hub using the tools/run_hub_ai_api.py runner to
simulate a realistic process environment, then validates:
 - Chat API OpenAPI spec includes example payloads and schemas
 - Plugin API OpenAPI spec includes examples
 - QFAC admin OpenAPI spec fields appear in the Chat API spec and endpoint responds
 - Key endpoints respond with the expected basic shapes
"""

from __future__ import annotations

import logging
import os
import socket
import subprocess
import sys
import time

# Standard library imports
from collections.abc import Generator

# Third party imports
import pytest
import requests

PORT = 3013
BASE = f"http://localhost:{PORT}"


@pytest.fixture(scope="module")
def hub_proc() -> Generator[object, None, None]:
    env = os.environ.copy()
    # Keep this suite deterministic: force-disable control token for the
    # spawned Hub process so dotenv/non-override loaders cannot re-enable it.
    env["AETHERRA_HUB_CONTROL_TOKEN"] = ""
    # Short-circuit if port already bound (another test run / developer instance)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", PORT)) == 0:
            # Reuse existing process context; yield dummy object with poll method
            class Dummy:
                def poll(self):
                    return None

            yield Dummy()  # type: ignore[misc]
            return

    cmd = [sys.executable, "tools/run_hub_ai_api.py", "--port", str(PORT)]
    proc = subprocess.Popen(cmd, env=env)
    try:
        # Wait for readiness
        deadline = time.time() + 8.0
        ready = False
        while time.time() < deadline:
            try:
                r = requests.get(f"{BASE}/api/ping", timeout=0.35)
                if r.status_code == 200:
                    ready = True
                    break
            except Exception as exc:
                logging.debug("ping failed during startup: %s", exc)
            time.sleep(0.05)
        if not ready:
            # Best-effort: index page for older paths
            for _ in range(15):
                try:
                    r = requests.get(f"{BASE}/", timeout=0.35)
                    if r.status_code in (200, 404, 405):
                        ready = True
                        break
                except Exception as exc:
                    logging.debug("index probe failed during startup: %s", exc)
                time.sleep(0.05)
        assert ready, "Hub did not become ready"
        yield proc
    finally:
        with Suppress(Exception):
            proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            with Suppress(Exception):
                proc.kill()


class Suppress:  # tiny helper to avoid importing contextlib for a single use
    def __init__(self, *exc_types):
        self.exc_types = exc_types or (Exception,)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return exc_type is not None and issubclass(exc_type, self.exc_types)


@pytest.mark.capabilities
def test_chat_openapi_has_examples_and_ai_ask_works(hub_proc):  # noqa: ARG001
    # Fetch Chat API openapi
    r = requests.get(f"{BASE}/api/openapi.json", timeout=2)
    assert r.status_code == 200
    spec = r.json()
    # Ensure ask has example request/response
    ask_post = spec["paths"]["/api/ai/ask"]["post"]
    req_ex = (
        ask_post.get("requestBody", {})
        .get("content", {})
        .get("application/json", {})
        .get("example")
    )
    assert isinstance(req_ex, dict)
    assert "message" in req_ex
    resp_ex = (
        ask_post.get("responses", {})
        .get("200", {})
        .get("content", {})
        .get("application/json", {})
        .get("example")
    )
    assert isinstance(resp_ex, dict)
    assert resp_ex.get("ok") is True

    # SSE envelope example exists
    sse_example = (
        spec.get("components", {})
        .get("schemas", {})
        .get("SSEEnvelopeV2", {})
        .get("example")
    )
    assert isinstance(sse_example, dict)
    assert set(sse_example) >= {"id", "type", "data"}

    # Exercise /api/ai/ask
    r2 = requests.post(f"{BASE}/api/ai/ask", json={"message": "hello"}, timeout=3)
    assert r2.status_code in (
        200,
        501,
    )  # 501 if API disabled (should be enabled by runner)
    if r2.status_code == 200:
        body = r2.json()
        assert isinstance(body, dict)
        assert body.get("ok") is True
        assert "result" in body
        assert isinstance(body["result"], dict)


@pytest.mark.capabilities
def test_plugins_openapi_has_examples(hub_proc):  # noqa: ARG001
    r = requests.get(f"{BASE}/api/plugins/openapi.json", timeout=2)
    assert r.status_code == 200
    spec = r.json()
    # List example
    list_200 = spec["paths"]["/api/plugins"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]
    assert "example" in list_200
    assert "plugins" in list_200["example"]

    # Register request example
    reg_req_ex = spec["paths"]["/api/plugins/register"]["post"]["requestBody"][
        "content"
    ]["application/json"].get("example")
    assert isinstance(reg_req_ex, dict)
    assert "name" in reg_req_ex

    # Register response example
    reg_resp_ex = spec["paths"]["/api/plugins/register"]["post"]["responses"]["200"][
        "content"
    ]["application/json"].get("example")
    assert isinstance(reg_resp_ex, dict)
    assert "name" in reg_resp_ex


@pytest.mark.capabilities
def test_qfac_admin_openapi_and_endpoint(hub_proc):  # noqa: ARG001
    r = requests.get(f"{BASE}/api/openapi.json", timeout=2)
    assert r.status_code == 200
    spec = r.json()
    # QFAC show response example exists
    show_200 = spec["paths"]["/api/qfac/admin/show"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]
    assert "schema" in show_200
    assert ("example" in show_200) or ("examples" in show_200)
    # Optional parity_by_k presence in schema (follow-on)
    qfac_schema = spec["components"]["schemas"].get("QfacAdminShow", {})
    props = qfac_schema.get("properties", {})
    assert "retrieval_policy" in props
    assert "parity_counters" in props

    # Hit the endpoint. In tokenless mode this should be open; if this
    # environment enables a control token, authenticate and continue.
    r2 = requests.get(f"{BASE}/api/qfac/admin/show", timeout=3)
    if r2.status_code == 401:
        token = (os.environ.get("AETHERRA_HUB_CONTROL_TOKEN") or "").strip()
        assert token, "QFAC admin returned 401 but no control token is configured"
        r2 = requests.get(
            f"{BASE}/api/qfac/admin/show",
            headers={"Authorization": f"Bearer {token}"},
            timeout=3,
        )
    assert r2.status_code == 200
    body = r2.json()
    assert isinstance(body, dict)
    assert set(body.keys()) >= {"available", "retrieval_policy", "parity_counters"}
