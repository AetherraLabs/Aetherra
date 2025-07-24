"""
Agent Collaboration Manager for Aetherra
Tracks agent load, expertise, health, and suggests optimal pairings for complex tasks.
"""

import random
from typing import Any, Dict, List

# In-memory registry of agents (stub)
agent_registry: List[Dict[str, Any]] = []


def register_agent(name: str, expertise: List[str], health: float = 1.0, load: int = 0):
    agent_registry.append(
        {"name": name, "expertise": expertise, "health": health, "load": load}
    )


def get_agent_status() -> List[Dict[str, Any]]:
    return agent_registry


def suggest_agent_pairings(task: str, n: int = 2) -> List[Dict[str, Any]]:
    """
    Suggest optimal agent pairings for a given task based on expertise, health, and load.
    """
    # Simple heuristic: prefer healthy, low-load, relevant-expertise agents
    candidates = [
        a
        for a in agent_registry
        if a["health"] > 0.7
        and a["load"] < 3
        and any(e in task for e in a["expertise"])
    ]
    if len(candidates) < n:
        # Fallback: fill with random agents
        candidates += random.sample(
            agent_registry, min(n - len(candidates), len(agent_registry))
        )
    return candidates[:n]


def enable_agent_chaining(agents: List[Dict[str, Any]], task: str) -> str:
    """
    Enable chained or parallel agent behavior for a complex task.
    """
    agent_names = [a["name"] for a in agents]
    return f"Agents {', '.join(agent_names)} assigned to task: {task} (chained/parallel mode)"


# Example usage (remove in production)
if __name__ == "__main__":
    register_agent("AgentA", ["nlp", "forecast"], health=0.95, load=1)
    register_agent("AgentB", ["vision", "reasoning"], health=0.9, load=0)
    register_agent("AgentC", ["planning", "plugin"], health=0.8, load=2)
    print(get_agent_status())
    pairings = suggest_agent_pairings("plugin reasoning task")
    print(pairings)
    print(enable_agent_chaining(pairings, "plugin reasoning task"))
