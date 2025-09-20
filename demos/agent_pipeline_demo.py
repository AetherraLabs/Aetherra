#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Agent Pipeline Demo
- Minimal CLI to exercise the Agent Fabric pipeline and print a compact, stream-friendly log.

Usage:
  python demos/agent_pipeline_demo.py --topic "quantum memory"

Notes:
- Sets AAR_MODE=headless and AAR_READ_ONLY=1 by default so the execute stage queues safely.
- Exits 0 on success; non-zero on failure.
"""

from __future__ import annotations

# Standard library imports
import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict


async def run_pipeline(topic: str) -> int:
    try:
        # Lazy imports so error messages are clean if modules are missing
        # Aetherra imports
        from aetherra_agent_fabric import AgentFabric  # type: ignore
        from aetherra_service_registry import AetherraServiceRegistry  # type: ignore
    except Exception as e:
        print(f"[ERR] Required modules not available: {e}")
        return 2

    # Environment: safe headless default
    os.environ.setdefault("AAR_MODE", "headless")
    os.environ.setdefault("AAR_READ_ONLY", "1")

    # Bring up a minimal registry + fabric
    reg = AetherraServiceRegistry()
    await reg.start()
    fabric = AgentFabric(reg)
    await fabric.start()

    print(f"[RUN] agent.pipeline goal: {topic}")
    try:
        result: Dict[str, Any] = await fabric.handle_message(
            "agent.pipeline", {"goal": topic}
        )
    except Exception as e:
        print(f"[ERR] pipeline error: {e}")
        return 1

    ok = bool(result.get("ok"))
    stages = result.get("stages") or {}

    # Stream a compact summary per stage if present
    order = ["plan", "retrieve", "summarize", "execute"]
    for name in order:
        st = stages.get(name)
        if isinstance(st, dict):
            flag = "OK" if st.get("ok") else ("QUEUED" if st.get("queued") else "ERR")
            extra = []
            if st.get("queued"):
                extra.append("queued=1")
            if "duration" in st:
                try:
                    extra.append(f"dt={float(st['duration']):.2f}s")
                except Exception:
                    pass
            meta = (" " + " ".join(extra)) if extra else ""
            print(f"[STAGE] {name:<9} {flag}{meta}")

    # Print final JSON for machine-readability
    print("[JSON] " + json.dumps({"ok": ok, "stages": list(stages.keys())}))
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Pipeline demo")
    parser.add_argument("--topic", required=True, help="goal/topic for the pipeline")
    args = parser.parse_args()

    try:
        return asyncio.run(run_pipeline(args.topic))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
