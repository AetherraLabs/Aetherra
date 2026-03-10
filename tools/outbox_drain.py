#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Outbox Drain / Replay Tool
-------------------------
Replays deferred write intents from the Aetherra Outbox (WAL) back into the
Agent Fabric. Supports dry-run and apply modes.

Usage examples:
  # Inspect queued entries
  python tools/outbox_drain.py --dry-run

  # Apply queued entries using a local full-capability fabric and clear on success
  # (ensures executor/toolsmith are enabled and not read-only)
  # PowerShell:
  #   $env:AAR_MODE="full"; python tools/outbox_drain.py --apply --clear-on-success
    # CMD:
        #   set AAR_MODE=full&& set AAR_READ_ONLY=0&& python tools\\outbox_drain.py --apply --clear-on-success
"""

from __future__ import annotations

# Standard library imports
import argparse
import asyncio
import json
import sys
from typing import Any


async def _get_fabric():
    # Aetherra imports
    from aetherra_agent_fabric import get_agent_fabric
    from aetherra_service_registry import get_service_registry, register_service

    reg = await get_service_registry()
    fabric = reg.get_service("agent_fabric")
    if not fabric:
        fabric = await get_agent_fabric(reg)
        await fabric.start()
        await register_service(
            "agent_fabric", fabric, metadata={"type": "agents", "drain_bootstrap": True}
        )
    return fabric


async def _status_summary() -> dict[str, Any]:
    fabric = await _get_fabric()
    st = await fabric.handle_message("agents.status", {})
    return {k: st.get(k) for k in ("mode", "read_only", "outbox", "outbox_size")}


def _summarize_entry(obj: dict[str, Any]) -> dict[str, Any]:
    key = obj.get("key")
    ts = obj.get("ts")
    p = obj.get("payload") or {}
    intent = p.get("intent")
    agent = p.get("agent")
    action = p.get("action")
    goal = p.get("goal")
    return {
        "key": key,
        "ts": ts,
        "intent": intent,
        "agent": agent,
        "action": action,
        "goal": goal,
    }


async def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Drain deferred entries from the Aetherra Outbox/WAL"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List what would be applied without executing",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply queued entries (execute against Fabric)",
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="Optional max number of entries to process"
    )
    parser.add_argument(
        "--clear-on-success",
        action="store_true",
        help="Clear entire outbox after successful apply run",
    )
    args = parser.parse_args(argv)

    # Show current fabric mode info
    try:
        st = await _status_summary()
        print(
            f"[FABRIC] mode={st.get('mode')} read_only={st.get('read_only')} outbox={st.get('outbox')} size={st.get('outbox_size')}"
        )
        if args.apply and (st.get("mode") != "full" or st.get("read_only") is True):
            print(
                "[WARN] Fabric is not in full-capability or read_only is enabled. Writes may be re-queued."
            )
    except Exception as e:
        print(f"[WARN] Could not determine fabric status: {e}")

    # Load entries
    # Aetherra imports
    from aetherra_outbox import Outbox

    outbox = Outbox()
    entries = list(outbox.iter_entries() or [])
    if args.limit and args.limit > 0:
        entries = entries[: args.limit]

    print(f"[OUTBOX] Loaded {len(entries)} entries")
    if not entries:
        return 0

    summaries = [_summarize_entry(e) for e in entries]
    print(json.dumps(summaries, indent=2))

    if args.dry_run and not args.apply:
        return 0

    # Apply queued entries
    fabric = await _get_fabric()
    applied = 0
    requeued = 0
    for obj in entries:
        p = (obj or {}).get("payload") or {}
        intent = p.get("intent")
        try:
            if intent == "agent.run":
                # Replay original payload directly
                res = await fabric.handle_message("agent.run", p.get("payload") or {})
            elif intent == "execute":
                # Map execute intent to executor agent call
                res = await fabric.handle_message(
                    "agent.run",
                    {
                        "agent": "agent.executor",
                        "action": p.get("action") or "generic",
                        "params": {"goal": p.get("goal")},
                    },
                )
            else:
                print(f"[SKIP] Unknown intent: {intent}")
                continue
            if res and res.get("ok") and not res.get("queued"):
                applied += 1
            elif res and res.get("queued"):
                requeued += 1
            else:
                print(f"[WARN] Entry {obj.get('key')} apply returned: {res}")
        except Exception as e:
            print(f"[ERROR] Failed to apply entry {obj.get('key')}: {e}")

    print(f"[APPLY] applied={applied} requeued={requeued} total={len(entries)}")
    if args.clear_on_success and applied > 0 and requeued == 0:
        try:
            outbox.clear()
            print("[OUTBOX] Cleared")
        except Exception as e:
            print(f"[WARN] Failed to clear outbox: {e}")

    # Return 0 if everything applied and not requeued; else 1
    return (
        0 if (applied > 0 and requeued == 0) or (applied == 0 and requeued == 0) else 1
    )


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:])))
