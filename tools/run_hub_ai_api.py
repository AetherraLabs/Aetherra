#!/usr/bin/env python3
"""
Start Aetherra Hub with AI API enabled for local testing.

Usage:
  python tools/run_hub_ai_api.py --port 3012 [--require-token] [--token SECRET]

This sets in-process environment flags:
  AETHERRA_AI_API_ENABLED=1
  AETHERRA_AI_API_STREAM=1
  AETHERRA_AI_API_REQUIRE_TOKEN=0 or 1
  AETHERRA_AI_API_TOKEN=... (if provided)

Then starts the Hub on the given port and keeps it running.
"""

from __future__ import annotations

import argparse
import os
import sys
import time


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=3001)
    p.add_argument("--require-token", action="store_true")
    p.add_argument("--token", default="")
    args = p.parse_args()

    # Desired flags for this run (store first; some loaders may override later)
    desired_flags = {
        "AETHERRA_AI_API_ENABLED": "1",
        "AETHERRA_AI_API_STREAM": "1",
        "AETHERRA_AI_API_REQUIRE_TOKEN": "1" if args.require_token else "0",
    }
    if args.token:
        desired_flags["AETHERRA_AI_API_TOKEN"] = args.token
    # Apply before imports
    os.environ.update(desired_flags)

    try:
        from aetherra_hub_server import AetherraHubServer
    except Exception as e:
        print(f"[ERR] failed to import hub server: {e}")
        return 1

    # Re-apply after imports in case a .env loader overwrote them
    os.environ.update(desired_flags)

    server = AetherraHubServer(args.port)
    ok = server.start_server()
    if not ok:
        print(f"[ERR] failed to start Hub on {args.port}")
        return 1

    # Register a minimal demo engine so /api/ai/* works end-to-end in this process
    try:
        import asyncio

        from aetherra_service_registry import register_service

        class _DemoEngine:
            async def process_message(self, msg: str, ctx: dict):
                text = f"Echo: {msg}"
                return {
                    "result": {
                        "response": text
                        + "\n[demo-engine] Provide your own engine for real answers.",
                        "context": ctx or {},
                    }
                }

        # Minimal Lyrixa chat stub so that /api/stats reports lyrixa_chat as registered
        class _LyrixaChatStub:
            async def initialize(self):  # parity with real service init
                return True

            async def handle_message(self, message_type: str, data: dict):
                mt = (message_type or "").lower()
                payload = data or {}
                msg = str(payload.get("message") or payload.get("content") or "").strip()
                # Deterministic reply mirroring Hub fallback schema keys
                return {
                    "text": ("[lyrixa-stub] " + (msg or "Hello")),
                    "suggestions": [],
                    "applied_changes": [],
                    "identity": {"name": "Lyrixa", "title": "Lyrixa AI Assistant"},
                    "awareness": {"note": "stubbed in run_hub_ai_api"},
                }

        async def _register():
            await register_service("aetherra_engine", _DemoEngine())
            await register_service("lyrixa_chat", _LyrixaChatStub())

        asyncio.run(_register())
        print("[OK] Registered demo engine (aetherra_engine) and lyrixa_chat stub in-process")
    except Exception as e:
        print(f"[WARN] Could not register demo engine/lyrixa_chat stub: {e}")

    print(f"[OK] Hub with AI API on http://127.0.0.1:{args.port}")
    # Re-apply flags one more time in case start_server triggered a .env reload
    os.environ.update(desired_flags)
    print(
        f"      AI enabled={os.environ.get('AETHERRA_AI_API_ENABLED')} stream={os.environ.get('AETHERRA_AI_API_STREAM')} require_token={os.environ.get('AETHERRA_AI_API_REQUIRE_TOKEN')}"
    )
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[STOP] Hub exiting")
        return 0


if __name__ == "__main__":
    sys.exit(main())
