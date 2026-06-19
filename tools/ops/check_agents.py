#!/usr/bin/env python
"""Quick script to check registered agents in orchestrator."""

import asyncio

from aetherra_service_registry import get_service_registry


async def check():
    reg = await get_service_registry()
    eng = reg.get_service("aetherra_engine")
    if not eng:
        print("No engine found")
        return

    orch = getattr(eng, "agent_orchestrator", None)
    if not orch:
        print("No orchestrator found")
        return

    print(f"Total agents: {len(orch.agents)}")
    print(f"Orchestration active: {orch.orchestration_active}")
    print(f"Task queue length: {len(orch.task_queue)}")
    print(f"Total tasks: {len(orch.tasks)}")
    print("\nAgents:")
    for aid, a in orch.agents.items():
        print(f"  {aid}: {a.name}")
        print(f"    Capabilities: {a.capabilities}")
        print(f"    Status: {a.status}")

    print("\nPending tasks:")
    for tid in orch.task_queue:
        t = orch.tasks.get(tid)
        if t:
            print(f"  {tid}: {t.name} - requires {t.required_capabilities}")


asyncio.run(check())
