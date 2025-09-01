#!/usr/bin/env python3
"""
Chat Stream Demo
- Minimal CLI to stream chat output from the Aetherra Hub developer AI API when enabled.
- Falls back to non-streaming /api/ai/ask if streaming is unavailable.

Usage:
  python demos/chat_stream_demo.py --prompt "Explain HMR in two sentences"

Env (optional):
  AETHERRA_BASE_URL           e.g., http://127.0.0.1:3001
  AETHERRA_WEB_HOST/PORT      defaults: localhost / 3001
  AETHERRA_HUB_HOST/PORT      fallback host/port
  AETHERRA_AI_API_TOKEN       bearer for X-Aetherra-Token
  AETHERRA_HUB_CONTROL_TOKEN  alternate token if AI token not set

Exit codes:
  0 success, 1 request error, 2 API unavailable/disabled
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, Optional

try:
    import requests
except Exception:
    print("requests is required. Please install it in your environment.")
    sys.exit(2)


def resolve_base_url() -> str:
    env = os.environ.get("AETHERRA_BASE_URL")
    if env:
        return env.rstrip("/")
    host = (
        os.environ.get("AETHERRA_WEB_HOST")
        or os.environ.get("AETHERRA_HUB_HOST")
        or "127.0.0.1"
    )
    try:
        port = int(
            os.environ.get("AETHERRA_WEB_PORT")
            or os.environ.get("AETHERRA_HUB_PORT")
            or 3001
        )
    except Exception:
        port = 3001
    return f"http://{host}:{port}"


def get_headers() -> Dict[str, str]:
    token = os.environ.get("AETHERRA_AI_API_TOKEN") or os.environ.get(
        "AETHERRA_HUB_CONTROL_TOKEN"
    )
    return {"X-Aetherra-Token": token} if token else {}


def try_stream(base: str, prompt: str) -> Optional[int]:
    url = base.rstrip("/") + "/api/ai/stream"
    payload = {"message": prompt}
    headers = get_headers()
    try:
        with requests.post(
            url, json=payload, headers=headers, stream=True, timeout=10
        ) as r:
            if r.status_code == 501:
                print(
                    "[INFO] Streaming API disabled (501). Falling back to /api/ai/ask."
                )
                return None
            if r.status_code == 403:
                print("[ERR] Forbidden (403). If required, set AETHERRA_AI_API_TOKEN.")
                return 1
            r.raise_for_status()
            print(f"[STREAM] connected: {url}")
            for raw in r.iter_lines(decode_unicode=True):
                if not raw:
                    continue
                line = str(raw)
                if line.startswith(":"):
                    # comment/keepalive
                    continue
                # Expect SSE: event: <name> / data: <json>
                if line.startswith("event:"):
                    evt = line.split(":", 1)[1].strip()
                    print(f"[SSE] event={evt}")
                    continue
                if line.startswith("data:"):
                    data = line.split(":", 1)[1].strip()
                    print(f"[SSE] data={data}")
                    # If final, we can decide to stop; let server close normally
                    continue
                # Fallback: print raw
                print(f"[SSE] {line}")
            print("[DONE] stream closed")
            return 0
    except requests.HTTPError as he:
        code = getattr(he.response, "status_code", None)
        if code in (404, 405):
            print("[INFO] Streaming endpoint not found. Falling back to /api/ai/ask.")
            return None
        print(f"[ERR] streaming HTTP error: {he}")
        return 1
    except Exception as e:
        print(f"[ERR] streaming failed: {e}")
        return 1


def try_ask(base: str, prompt: str) -> int:
    url = base.rstrip("/") + "/api/ai/ask"
    payload = {"message": prompt}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        if r.status_code == 501:
            print(
                "[INFO] AI API disabled (501). Enable AETHERRA_AI_API_ENABLED=1 on the Hub and retry."
            )
            return 2
        if r.status_code == 403:
            print("[ERR] Forbidden (403). If required, set AETHERRA_AI_API_TOKEN.")
            return 1
        r.raise_for_status()
        data = r.json()
        if (
            isinstance(data, dict)
            and data.get("ok")
            and isinstance(data.get("result"), dict)
        ):
            out = data["result"].get("response") or data["result"].get("text")
            if out:
                print("[RESPONSE] " + str(out))
            else:
                print("[JSON] " + json.dumps(data))
            return 0
        print("[JSON] " + json.dumps(data))
        return 0 if isinstance(data, dict) and data.get("ok") else 1
    except requests.HTTPError as he:
        print(f"[ERR] ask HTTP error: {he}")
        return 1
    except Exception as e:
        print(f"[ERR] ask failed: {e}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Chat stream demo")
    parser.add_argument("--prompt", required=True, help="message to send")
    args = parser.parse_args()

    base = resolve_base_url()
    print(f"[BASE] {base}")

    rc = try_stream(base, args.prompt)
    if rc is None:
        return try_ask(base, args.prompt)
    return int(rc)


if __name__ == "__main__":
    sys.exit(main())
