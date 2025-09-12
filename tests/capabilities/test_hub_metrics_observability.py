# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio
import os
import re
import time

import pytest
import requests

from aetherra_hub.compat import start_hub_server

HAS_FLASK = True
try:
    import flask  # noqa: F401
except Exception:
    HAS_FLASK = False


def _get_metrics_text(port: int) -> str:
    r = requests.get(f"http://localhost:{port}/metrics", timeout=5)
    assert r.status_code == 200
    return r.text


def _parse_metric_value(text: str, pattern: str, default: float = 0.0) -> float:
    m = re.search(pattern, text)
    if not m:
        return default
    try:
        return float(m.group(1))
    except Exception:
        return default


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_metrics_expose_core_series():
    port = 3017
    server = start_hub_server(port=port)
    assert server.is_running()

    txt = _get_metrics_text(port)

    # Core chat series should be present
    assert "aetherra_chat_requests_total" in txt
    assert "aetherra_chat_streams_current" in txt
    assert "aetherra_chat_latency_ms_sum" in txt
    assert "aetherra_chat_latency_count" in txt
    assert "aetherra_chat_ttft_ms_sum" in txt
    assert "aetherra_chat_ttft_count" in txt
    assert "aetherra_chat_chunks_total" in txt
    assert 'aetherra_chat_fallback_total{path="mock"}' in txt
    assert 'aetherra_chat_fallback_total{path="engine"}' in txt
    assert 'aetherra_chat_ttft_ms_bucket{le="+Inf"}' in txt


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_metrics_fallback_mock_increments():
    port = 3018
    server = start_hub_server(port=port)
    assert server.is_running()

    # Baseline
    txt0 = _get_metrics_text(port)
    base = _parse_metric_value(
        txt0, r'aetherra_chat_fallback_total\{path="mock"\} ([-+]?[0-9]*\.?[0-9]+)'
    )

    # Trigger Lyrixa offline fallback path
    r = requests.post(
        f"http://localhost:{port}/api/lyrixa/chat",
        json={"message": "hi"},
        timeout=5,
    )
    assert r.status_code == 200

    txt1 = _get_metrics_text(port)
    after = _parse_metric_value(
        txt1, r'aetherra_chat_fallback_total\{path="mock"\} ([-+]?[0-9]*\.?[0-9]+)'
    )

    assert after >= base + 1.0


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_metrics_ttft_increments_after_stream():
    # Enable AI stream endpoints for this test
    os.environ["AETHERRA_AI_API_ENABLED"] = "1"
    os.environ["AETHERRA_AI_API_STREAM"] = "1"
    os.environ["AETHERRA_AI_API_REQUIRE_TOKEN"] = "0"

    port = 3019
    server = start_hub_server(port=port)
    assert server.is_running()

    txt0 = _get_metrics_text(port)
    base_ttft = _parse_metric_value(
        txt0, r"aetherra_chat_ttft_count ([-+]?[0-9]*\.?[0-9]+)"
    )

    # Open a POST stream and drain until final
    with requests.post(
        f"http://localhost:{port}/api/ai/stream",
        json={"message": "ping"},
        stream=True,
        timeout=15,
    ) as resp:
        assert resp.status_code == 200
        saw_final = False
        t0 = time.time()
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                # SSE event delimiter
                continue
            if line.startswith("event:") and "final" in line:
                saw_final = True
                break
            # Guard against hanging
            if time.time() - t0 > 10:
                break
        assert saw_final

    # TTFT count should have increased by at least 1
    txt1 = _get_metrics_text(port)
    after_ttft = _parse_metric_value(
        txt1, r"aetherra_chat_ttft_count ([-+]?[0-9]*\.?[0-9]+)"
    )
    assert after_ttft >= base_ttft + 1.0


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_metrics_per_principal_gauge_emitted():
    # Enable AI stream endpoints
    os.environ["AETHERRA_AI_API_ENABLED"] = "1"
    os.environ["AETHERRA_AI_API_STREAM"] = "1"
    os.environ["AETHERRA_AI_API_REQUIRE_TOKEN"] = "0"

    port = 3020
    server = start_hub_server(port=port)
    assert server.is_running()

    principal = "test-user"
    # Open and drain a short stream with principal header
    with requests.post(
        f"http://localhost:{port}/api/ai/stream",
        json={"message": "hello from principal"},
        headers={"X-Aetherra-Principal": principal},
        stream=True,
        timeout=15,
    ) as resp:
        assert resp.status_code == 200
        # Drain quickly until final
        for line in resp.iter_lines(decode_unicode=True):
            if line and line.startswith("event:") and "final" in line:
                break

    # After stream ends, gauge should be present (value may be 0 after decrement)
    txt = _get_metrics_text(port)
    assert (
        f'aetherra_chat_streams_current_by_principal{{principal="{principal}"}}' in txt
    )


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_metrics_chunks_total_increments_with_chunking_stream():
    # Enable AI stream endpoints
    os.environ["AETHERRA_AI_API_ENABLED"] = "1"
    os.environ["AETHERRA_AI_API_STREAM"] = "1"
    os.environ["AETHERRA_AI_API_REQUIRE_TOKEN"] = "0"

    # Register a stub engine that emits chunk callbacks
    class ChunkingEngine:
        async def process_message(self, msg: str, ctx: dict | None = None):
            cbs = (ctx or {}).get("_callbacks") or {}
            on_chunk = cbs.get("on_chunk")
            if callable(on_chunk):
                for i in range(3):
                    on_chunk(text=f"piece-{i}")
                    await asyncio.sleep(0.01)
            return {"response": "ok"}

    async def _register(engine):
        from aetherra_service_registry import get_service_registry

        reg = await get_service_registry()
        await reg.register_service("aetherra_engine", engine)

    port = 3021
    server = start_hub_server(port=port)
    assert server.is_running()
    asyncio.run(_register(ChunkingEngine()))
    # Small warm-up to reduce flakiness after rapid server startup
    time.sleep(0.1)

    txt0 = _get_metrics_text(port)
    base_chunks = _parse_metric_value(
        txt0, r"aetherra_chat_chunks_total ([-+]?[0-9]*\.?[0-9]+)"
    )

    # Run a stream to completion (tolerate rare transport timeout; rely on metrics)
    try:
        with requests.post(
            f"http://localhost:{port}/api/ai/stream",
            json={"message": "emit chunks"},
            stream=True,
            timeout=10,
        ) as resp:
            assert resp.status_code == 200
            for line in resp.iter_lines(decode_unicode=True):
                if line and line.startswith("event:") and "final" in line:
                    break
    except requests.exceptions.ConnectionError:
        # If the SSE transport flakes, we still verify chunk metric increments below.
        pass

    # Allow for slight async delay in metrics flush; poll briefly
    attempts = 0
    after_chunks = base_chunks
    while attempts < 10 and after_chunks < base_chunks + 3.0:
        txt1 = _get_metrics_text(port)
        after_chunks = _parse_metric_value(
            txt1, r"aetherra_chat_chunks_total ([-+]?[0-9]*\.?[0-9]+)"
        )
        if after_chunks >= base_chunks + 3.0:
            break
        attempts += 1
        time.sleep(0.05)
    assert after_chunks >= base_chunks + 3.0


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_metrics_breaker_open_increments_on_timeout():
    # Enable AI stream endpoints
    os.environ["AETHERRA_AI_API_ENABLED"] = "1"
    os.environ["AETHERRA_AI_API_STREAM"] = "1"
    os.environ["AETHERRA_AI_API_REQUIRE_TOKEN"] = "0"

    # Engine that simulates a timeout failure
    class TimeoutEngine:
        async def process_message(self, msg: str, ctx: dict | None = None):
            raise Exception("timeout: simulated upstream")

    async def _register(engine):
        from aetherra_service_registry import get_service_registry

        reg = await get_service_registry()
        await reg.register_service("aetherra_engine", engine)

    port = 3022
    server = start_hub_server(port=port)
    assert server.is_running()
    asyncio.run(_register(TimeoutEngine()))

    txt0 = _get_metrics_text(port)
    base_breaker = _parse_metric_value(
        txt0, r"aetherra_chat_breaker_open_total ([-+]?[0-9]*\.?[0-9]+)"
    )

    # Run a stream; expect error/final and breaker metrics increment
    with requests.post(
        f"http://localhost:{port}/api/ai/stream",
        json={"message": "trigger timeout"},
        stream=True,
        timeout=10,
    ) as resp:
        assert resp.status_code == 200
        for line in resp.iter_lines(decode_unicode=True):
            if line and line.startswith("event:") and "final" in line:
                break

    txt1 = _get_metrics_text(port)
    after_breaker = _parse_metric_value(
        txt1, r"aetherra_chat_breaker_open_total ([-+]?[0-9]*\.?[0-9]+)"
    )
    assert after_breaker >= base_breaker + 1.0
