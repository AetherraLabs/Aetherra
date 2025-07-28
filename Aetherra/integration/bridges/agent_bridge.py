"""
Agent Integration Bridge - Connect migrated agents to clean architecture
"""

import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class AgentIntegrationBridge:
    """Bridge to manage agent integration in clean architecture"""

    def __init__(self, aetherra_v2_root: Path):
        self.aetherra_v2_root = Path(aetherra_v2_root)
        self.registry_file = (
            self.aetherra_v2_root / "integration" / "agent_registry.json"
        )
        self.agents = {}
        self.loaded_agents = {}

        self._load_agent_registry()

    def _load_agent_registry(self):
        """Load the agent registry"""
        if self.registry_file.exists():
            with open(self.registry_file, "r", encoding="utf-8") as f:
                self.agents = json.load(f)
        else:
            print("Warning: Agent registry not found")

    def get_agents_by_category(self, category: str) -> List[Dict]:
        """Get all agents in a specific category"""
        return self.agents.get("agents_by_category", {}).get(category, [])

    def get_all_categories(self) -> List[str]:
        """Get all agent categories"""
        return list(self.agents.get("categories", {}).keys())

    def load_agent(self, agent_name: str) -> Optional[Any]:
        """Dynamically load an agent by name"""
        if agent_name in self.loaded_agents:
            return self.loaded_agents[agent_name]

        # Find agent in registry
        agent_path = self.agents.get("agent_locations", {}).get(agent_name)
        if not agent_path:
            print(f"Agent not found: {agent_name}")
            return None

        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(agent_name, agent_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.loaded_agents[agent_name] = module
            print(f"Loaded agent: {agent_name}")
            return module

        except Exception as e:
            print(f"Failed to load agent {agent_name}: {e}")
            return None

    def get_lyrixa_agents(self) -> List[Dict]:
        """Get all Lyrixa agents"""
        return self.get_agents_by_category("lyrixa_agent")

    def get_aetherra_agents(self) -> List[Dict]:
        """Get all Aetherra agents"""
        return self.get_agents_by_category("aetherra_agent")

    def get_cognitive_agents(self) -> List[Dict]:
        """Get all cognitive agents"""
        return self.get_agents_by_category("cognitive_agent")

    def get_orchestrator_agents(self) -> List[Dict]:
        """Get all orchestrator agents"""
        return self.get_agents_by_category("orchestrator_agent")

    def get_agent_summary(self) -> Dict:
        """Get summary of all agents"""
        return {
            "total_agents": self.agents.get("total_agents", 0),
            "categories": self.agents.get("categories", {}),
            "loaded_agents": len(self.loaded_agents),
        }

    def test_agent_loading(self):
        """Test loading a few agents to verify integration"""
        print("Testing agent loading...")

        # Test loading a few agents from each category
        for category in self.get_all_categories():
            agents = self.get_agents_by_category(category)
            if agents:
                # Try loading the first agent
                first_agent = agents[0]
                agent_file = first_agent["file"]
                print(f"  Testing {category}: {agent_file}")

                result = self.load_agent(agent_file)
                if result:
                    print(f"    Successfully loaded {agent_file}")
                else:
                    print(f"    Failed to load {agent_file}")

        print("\nAgent Loading Summary:")
        summary = self.get_agent_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
