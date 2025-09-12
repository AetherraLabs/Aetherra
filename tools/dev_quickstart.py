#!/usr/bin/env python3
"""Developer ultra-quick start helper.

Goals:
 1. Ensure chat env flags are set (non-destructive: won't overwrite if already defined)
 2. Launch Hub server (best-effort) on default port (AETHERRA_HUB_PORT or 3001)
 3. Probe /api/lyrixa/chat with a sample message and print JSON result
 4. Provide follow-up hints (metrics endpoint, streaming, stop instructions)

Usage:
  python tools/dev_quickstart.py --auto-chat

Flags:
  --auto-chat      Set AETHERRA_AI_API_ENABLED=1 and AETHERRA_AI_API_STREAM=1 if unset
  --port <int>     Override hub port (default 3001)
  --message <str>  Sample message (default 'hello alpha')
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request


def _info(msg: str):
    print(f"[quickstart] {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--auto-chat", action="store_true", help="Auto-export chat flags if unset"
    )
    ap.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("AETHERRA_HUB_PORT", "3001") or 3001),
    )
    ap.add_argument("--message", default="hello alpha")
    args = ap.parse_args()

    if args.auto_chat:
        if "AETHERRA_AI_API_ENABLED" not in os.environ:
            os.environ["AETHERRA_AI_API_ENABLED"] = "1"
            _info("Set AETHERRA_AI_API_ENABLED=1")
        if "AETHERRA_AI_API_STREAM" not in os.environ:
            os.environ["AETHERRA_AI_API_STREAM"] = "1"
            _info("Set AETHERRA_AI_API_STREAM=1")

    port = args.port

    # Launch hub server in background using compatibility module (legacy shim retired).
    # We intentionally spawn a subprocess so output streams are visible and isolation preserved.
    _info(f"Starting hub on port {port} via aetherra_hub.compat ...")
    hub_proc = subprocess.Popen(
        [sys.executable, "-m", "aetherra_hub.compat"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env={**os.environ, "AETHERRA_HUB_PORT": str(port)},
    )

    # Poll for readiness of /api/lyrixa/chat
    def _is_up():
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except Exception:
            return False

    for _ in range(60):
        if _is_up():
            break
        time.sleep(0.25)
    else:
        _info("Hub did not open port in time (15s). Check output below:")
        try:
            out = hub_proc.stdout.read(4000) if hub_proc.stdout else ""
            print(out)
        except Exception:
            pass
        return 2

    # Small delay to let Flask finish route registration
    time.sleep(0.5)

    data = json.dumps({"message": args.message}).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/lyrixa/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            body = r.read().decode("utf-8")
            try:
                js = json.loads(body)
            except Exception:
                js = {"raw": body}
            _info("Chat response:")
            print(json.dumps(js, indent=2)[:4000])
    except urllib.error.HTTPError as e:
        _info(f"HTTP error {e.code}: {e.read().decode('utf-8', 'replace')[:400]}")
    except Exception as e:
        _info(f"Error calling chat endpoint: {e}")

    _info(
        "Next: visit http://localhost:{}/metrics for Prometheus metrics.".format(port)
    )
    _info(
        "To try streaming enable SSE: POST /api/ai/stream with same JSON (when stream flag set)."
    )
    _info("Press Ctrl+C to stop (this will terminate the hub).")

    # Stream hub output until user interrupts
    try:
        if hub_proc.stdout:
            for line in hub_proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
    except KeyboardInterrupt:
        _info("Stopping hub...")
    finally:
        try:
            hub_proc.terminate()
        except Exception:
            pass
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
