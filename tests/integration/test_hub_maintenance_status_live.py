#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Live check: Unified Maintenance Status endpoint

Starts no services on its own. Assumes a local Hub is running on port 3001.
Use the VS Code task "Run Hub (AI API 3001)" to start it, then run this test.

This integration check is resilient: it prints the response and exits without
raising if the Hub is not reachable.
"""

# Standard library imports
import contextlib
import http.client
import json
import logging
import sys


def check_hub_maintenance_status():
    host = "localhost"
    port = 3001
    path = "/api/maintenance/status"
    url = f"http://{host}:{port}{path}"
    print(f"\n🔧 Checking maintenance status: {url}")
    try:
        conn = http.client.HTTPConnection(host, port, timeout=5)
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read()
        data = json.loads(body)
        print("Status code:", resp.status)
        print("Keys:", list(data.keys()))
        overall = data.get("overall", {})
        print("Overall:", overall)
        homeo = data.get("homeostasis", {})
        si = data.get("self_improvement", {})
        selfinc = data.get("self_incorporation", {})
        print("Homeostasis available:", homeo.get("available"))
        print("Self-Improvement available:", si.get("available"))
        print("Self-Incorporation available:", selfinc.get("available"))
        # Lightweight sanity
        assert isinstance(data.get("ok"), bool)
        assert isinstance(overall, dict)
        print("✅ Maintenance endpoint reachable and returned JSON.")
    except Exception as e:
        print(f"⚠️  Could not reach Hub at {url}: {e}")
        print("Hint: Start it with the VS Code task 'Run Hub (AI API 3001)'.")
    finally:
        with contextlib.suppress(Exception):
            conn.close()


if __name__ == "__main__":
    check_hub_maintenance_status()
