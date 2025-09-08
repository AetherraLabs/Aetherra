#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
probe_ai_endpoints.py

Quick probe for Aetherra Hub AI endpoints: /api/ai/ask and /api/ai/stream (POST + GET alias).
Requires the Hub to be running. Provide --host, --port, and --token when token is required.

Exit codes:
 0 = all checks passed
 1 = failure
"""

from __future__ import annotations

import argparse
import json
import sys
import time

import requests


def check_ask(base: str, token: str | None) -> tuple[bool, str]:
    headers = {}
    if token:
        headers["X-Aetherra-Token"] = token
    r = requests.post(
        f"{base}/api/ai/ask",
        headers=headers,
        json={"message": "hello from probe"},
        timeout=10,
    )
    if r.status_code != 200:
        return False, f"ask status={r.status_code} body={r.text[:256]}"
    try:
        data = r.json()
    except Exception:
        return False, f"ask non-json: {r.text[:256]}"
    if not bool(data.get("ok")):
        return False, f"ask not ok: {data}"
    return True, "ask ok"


def read_sse_lines(resp, max_events=2, timeout=5.0) -> tuple[bool, str]:
    """Read a few SSE lines safely with a time limit."""
    start = time.time()
    events = []
    for line in resp.iter_lines(decode_unicode=True):
        if line:
            events.append(line)
            if len(events) >= max_events:
                break
        if time.time() - start > timeout:
            break
    if not events:
        return False, "no sse lines"
    return True, " | ".join(events[:6])


def check_stream_post(base: str, token: str | None) -> tuple[bool, str]:
    headers = {"Accept": "text/event-stream"}
    if token:
        headers["X-Aetherra-Token"] = token
    r = requests.post(
        f"{base}/api/ai/stream",
        headers=headers,
        json={"message": "hello stream (POST)"},
        stream=True,
        timeout=10,
    )
    if r.status_code != 200:
        return False, f"stream POST status={r.status_code} body={r.text[:256]}"
    ok, desc = read_sse_lines(r)
    return (ok, f"stream POST: {desc}")


def check_stream_get(base: str, token: str | None) -> tuple[bool, str]:
    headers = {"Accept": "text/event-stream"}
    params = {"message": "hello stream (GET)"}
    if token:
        params["token"] = token
    r = requests.get(
        f"{base}/api/ai/stream",
        headers=headers,
        params=params,
        stream=True,
        timeout=10,
    )
    if r.status_code != 200:
        return False, f"stream GET status={r.status_code} body={r.text[:256]}"
    ok, desc = read_sse_lines(r)
    return (ok, f"stream GET: {desc}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="http://localhost")
    p.add_argument("--port", type=int, default=3015)
    p.add_argument("--token", default=None)
    args = p.parse_args()

    base = f"{args.host}:{args.port}"
    steps = [
        ("ask", check_ask),
        ("stream_post", check_stream_post),
        ("stream_get", check_stream_get),
    ]
    results = []
    ok_all = True
    for name, fn in steps:
        try:
            ok, desc = fn(base, args.token)
        except Exception as e:
            ok, desc = False, f"{name} error: {e}"
        results.append({"step": name, "ok": ok, "desc": desc})
        ok_all = ok_all and ok
    print(json.dumps({"ok": ok_all, "results": results}, indent=2))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
