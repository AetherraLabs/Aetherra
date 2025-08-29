#!/usr/bin/env python3
"""
Agent Fabric Probe
==================
Quick probe to list agents and exercise a couple of agent calls via the Service Registry.

Usage: python tools/agents_probe.py [--run planner "goal text"] [--ops]
"""

import argparse
import asyncio
import json
import sys
from typing import Any, Dict


async def main(argv):
    parser = argparse.ArgumentParser(description="Aetherra Agent Fabric Probe")
    parser.add_argument(
        "--run",
        nargs=2,
        metavar=("agent", "payload"),
        help="Run agent with a minimal payload (planner|retriever|summarizer)",
    )
    parser.add_argument(
        "--ops", action="store_true", help="Query ops agent for registry snapshot"
    )
    parser.add_argument(
        "--pipeline",
        metavar="goal",
        help="Run plan→retrieve→summarize pipeline for a goal/query",
    )
    parser.add_argument(
        "--metrics", action="store_true", help="Show Agent Fabric metrics"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show Agent Fabric status (mode, read-only, outbox)",
    )
    parser.add_argument(
        "--create-tool",
        nargs=2,
        metavar=("name", "spec"),
        help="Create a tool via Toolsmith (writes to toolshed/<name>.py)",
    )
    parser.add_argument(
        "--no-bootstrap",
        action="store_true",
        help="Do not auto-start a local Agent Fabric if not found",
    )
    args = parser.parse_args(argv)

    from aetherra_service_registry import get_service_registry

    reg = await get_service_registry()

    # Find fabric
    fabric = reg.get_service("agent_fabric")
    if not fabric:
        if args.no_bootstrap:
            print("[ERROR] agent_fabric service not found (is the OS running?)")
            return 1
        # Auto-bootstrap a local Agent Fabric in this process
        try:
            from aetherra_agent_fabric import get_agent_fabric
            from aetherra_service_registry import register_service

            fabric = await get_agent_fabric(reg)
            await fabric.start()
            await register_service(
                "agent_fabric",
                fabric,
                metadata={"type": "agents", "probe_bootstrap": True},
            )
            print("[INFO] agent_fabric not found; started a local fabric for probing.")
        except Exception as e:
            print(f"[ERROR] failed to bootstrap local Agent Fabric: {e}")
            return 1

    # List agents
    status = await fabric.handle_message("agents.status", {})
    print("[AGENTS] Registered agents:")
    for name in status.get("agents", []):
        print(f"  - {name}")

    # Optional status
    if args.status:
        print("\n[STATUS] Agent Fabric:")
        print(json.dumps(status, indent=2))

    # Optional run
    if args.run:
        name, payload_text = args.run
        payload: Dict[str, Any] = {
            "agent": f"agent.{name}",
            "text": payload_text,
            "goal": payload_text,
            "query": payload_text,
        }
        res = await fabric.handle_message("agent.run", payload)
        print("\n[RUN] Result:")
        print(json.dumps(res, indent=2))

    # Optional ops
    if args.ops:
        res = await fabric.handle_message("agent.run", {"agent": "agent.ops"})
        print("\n[OPS] Registry snapshot:")
        print(json.dumps(res.get("registry", {}), indent=2))

    # Optional pipeline
    if args.pipeline:
        res = await fabric.handle_message("agent.pipeline", {"goal": args.pipeline})
        print("\n[PIPELINE] plan→retrieve→summarize result:")
        print(json.dumps(res, indent=2))

    # Optional metrics
    if args.metrics:
        res = await fabric.handle_message("agents.metrics", {})
        print("\n[METRICS] Agent Fabric:")
        print(json.dumps(res, indent=2))

    # Optional create tool
    if args.create_tool:
        name, spec = args.create_tool
        payload = {"agent": "agent.toolsmith", "name": name, "spec": spec}
        res = await fabric.handle_message("agent.run", payload)
        print("\n[TOOLS] Toolsmith result:")
        print(json.dumps(res, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:])))
