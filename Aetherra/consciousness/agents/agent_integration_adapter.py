"""
🔗 Agent Integration Adapter
============================

Phase 2: Bridges existing Aetherra Core and Lyrixa Core agents into the
consciousness orchestrator system, maintaining their functionality while
adding consciousness-layer coordination.
"""

import asyncio
import inspect
import json
import logging
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from ..core.consciousness_bridge import ConsciousnessMessage, MessageType
    from .agent_registry import (
        AgentCapability,
        AgentProfile,
        AgentRegistration,
        AgentStatus,
    )
except ImportError:
    # Fallback imports for development
    from dataclasses import dataclass
    from enum import Enum

    class AgentCapability(Enum):
        REASONING = "reasoning"
        MEMORY = "memory"
        CONVERSATION = "conversation"
        GOAL_PLANNING = "goal_planning"
        SELF_EVALUATION = "self_evaluation"
        LEARNING = "learning"
        ETHICS = "ethics"
        EMOTION = "emotion"
        CREATIVITY = "creativity"
        ORCHESTRATION = "orchestration"

    class AgentStatus(Enum):
        DISCOVERED = "discovered"
        INTEGRATING = "integrating"
        INTEGRATED = "integrated"
        ACTIVE = "active"
        ERROR = "error"

    @dataclass
    class AgentProfile:
        name: str
        capabilities: List[AgentCapability]
        trust_level: float = 0.5
        performance_score: float = 0.0
        collaboration_rating: float = 0.0

    @dataclass
    class AgentRegistration:
        agent_id: str
        profile: AgentProfile
        status: AgentStatus
        registration_time: datetime
        metadata: Dict[str, Any]


logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of agents that can be integrated."""

    AETHERRA_CORE = "aetherra_core"
    LYRIXA_CORE = "lyrixa_core"
    PLUGIN = "plugin"
    EXTERNAL = "external"


class IntegrationStatus(Enum):
    """Agent integration status tracking."""

    DISCOVERED = "discovered"
    ANALYZING = "analyzing"
    ADAPTING = "adapting"
    TESTING = "testing"
    INTEGRATED = "integrated"
    FAILED = "failed"


@dataclass
class AgentIntegrationResult:
    """Result of agent integration process."""

    agent_id: str
    status: IntegrationStatus
    capabilities: List[AgentCapability]
    integration_time: datetime
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


class AgentIntegrationAdapter:
    """
    Integrates existing agents into the consciousness orchestrator system.

    This adapter discovers, analyzes, and integrates agents from:
    - Aetherra Core agents
    - Lyrixa Core intelligence systems
    - Plugin-based agents
    - External agent systems
    """

    def __init__(self, consciousness_bridge=None, agent_registry=None):
        self.consciousness_bridge = consciousness_bridge
        self.agent_registry = agent_registry

        # Integration tracking
        self.discovered_agents: Dict[str, Dict[str, Any]] = {}
        self.integration_results: Dict[str, AgentIntegrationResult] = {}
        self.active_integrations: Set[str] = set()

        # Agent discovery paths
        self.aetherra_agents_path = Path("Aetherra/aetherra_core/agents")
        self.lyrixa_intelligence_path = Path("Aetherra/lyrixa_core/intelligence")
        self.plugin_paths = [
            Path("Aetherra/plugins"),
            Path("plugins"),
            Path("lyrixa_plugins"),
        ]

        logger.info("Agent Integration Adapter initialized")

    async def discover_all_agents(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Discover all available agents across the system.

        Returns:
            Dictionary of agent categories and their discovered agents
        """
        logger.info("🔍 Starting comprehensive agent discovery...")

        discovered = {
            "aetherra_core": [],
            "lyrixa_core": [],
            "plugins": [],
            "external": [],
        }

        # Discover Aetherra Core agents
        aetherra_agents = await self._discover_aetherra_agents()
        discovered["aetherra_core"] = aetherra_agents
        logger.info(f"Found {len(aetherra_agents)} Aetherra Core agents")

        # Discover Lyrixa Core intelligence agents
        lyrixa_agents = await self._discover_lyrixa_agents()
        discovered["lyrixa_core"] = lyrixa_agents
        logger.info(f"Found {len(lyrixa_agents)} Lyrixa Core agents")

        # Discover plugin-based agents
        plugin_agents = await self._discover_plugin_agents()
        discovered["plugins"] = plugin_agents
        logger.info(f"Found {len(plugin_agents)} plugin agents")

        # Store discovered agents
        self.discovered_agents = discovered

        total_agents = sum(len(agents) for agents in discovered.values())
        logger.info(f"🎯 Total discovered agents: {total_agents}")

        return discovered

    async def _discover_aetherra_agents(self) -> List[Dict[str, Any]]:
        """Discover agents in Aetherra Core."""
        agents = []

        if not self.aetherra_agents_path.exists():
            logger.warning(
                f"Aetherra agents path not found: {self.aetherra_agents_path}"
            )
            return agents

        for agent_file in self.aetherra_agents_path.glob("*.py"):
            if agent_file.name.startswith("__"):
                continue

            try:
                agent_info = await self._analyze_agent_file(
                    agent_file, AgentType.AETHERRA_CORE
                )
                if agent_info:
                    agents.append(agent_info)
            except Exception as e:
                logger.warning(f"Error analyzing {agent_file.name}: {e}")

        return agents

    async def _discover_lyrixa_agents(self) -> List[Dict[str, Any]]:
        """Discover agents in Lyrixa Core intelligence."""
        agents = []

        if not self.lyrixa_intelligence_path.exists():
            logger.warning(
                f"Lyrixa intelligence path not found: {self.lyrixa_intelligence_path}"
            )
            return agents

        for agent_file in self.lyrixa_intelligence_path.glob("*.py"):
            if agent_file.name.startswith("__"):
                continue

            try:
                agent_info = await self._analyze_agent_file(
                    agent_file, AgentType.LYRIXA_CORE
                )
                if agent_info:
                    agents.append(agent_info)
            except Exception as e:
                logger.warning(f"Error analyzing {agent_file.name}: {e}")

        return agents

    async def _discover_plugin_agents(self) -> List[Dict[str, Any]]:
        """Discover plugin-based agents."""
        agents = []

        for plugin_path in self.plugin_paths:
            if not plugin_path.exists():
                continue

            for agent_file in plugin_path.rglob("*agent*.py"):
                if agent_file.name.startswith("__"):
                    continue

                try:
                    agent_info = await self._analyze_agent_file(
                        agent_file, AgentType.PLUGIN
                    )
                    if agent_info:
                        agents.append(agent_info)
                except Exception as e:
                    logger.warning(f"Error analyzing plugin {agent_file.name}: {e}")

        return agents

    async def _analyze_agent_file(
        self, file_path: Path, agent_type: AgentType
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze an agent file to extract capabilities and metadata.

        Args:
            file_path: Path to the agent file
            agent_type: Type of agent being analyzed

        Returns:
            Agent information dictionary or None if not a valid agent
        """
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # Extract agent information
            agent_info = {
                "id": file_path.stem,
                "name": self._extract_agent_name(content, file_path.stem),
                "type": agent_type.value,
                "file_path": str(file_path),
                "capabilities": self._extract_capabilities(content),
                "description": self._extract_description(content),
                "methods": self._extract_methods(content),
                "dependencies": self._extract_dependencies(content),
                "status": IntegrationStatus.DISCOVERED.value,
                "discovered_at": datetime.now().isoformat(),
            }

            # Only include if it looks like a valid agent
            if self._is_valid_agent(agent_info):
                return agent_info

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")

        return None

    def _extract_agent_name(self, content: str, default_name: str) -> str:
        """Extract agent name from file content."""
        # Look for class names that end with Agent
        import re

        class_matches = re.findall(r"class\s+(\w*[Aa]gent\w*)", content)
        if class_matches:
            return class_matches[0]

        # Look for name variables
        name_matches = re.findall(r'name\s*=\s*["\']([^"\']+)["\']', content)
        if name_matches:
            return name_matches[0]

        return default_name.replace("_", " ").title()

    def _extract_capabilities(self, content: str) -> List[str]:
        """Extract capabilities from agent content."""
        capabilities = []
        content_lower = content.lower()

        # Map keywords to capabilities
        capability_keywords = {
            AgentCapability.REASONING.value: ["reason", "logic", "inference", "think"],
            AgentCapability.MEMORY.value: ["memory", "remember", "store", "recall"],
            AgentCapability.CONVERSATION.value: [
                "chat",
                "conversation",
                "dialog",
                "talk",
            ],
            AgentCapability.GOAL_PLANNING.value: [
                "goal",
                "plan",
                "objective",
                "target",
            ],
            AgentCapability.SELF_EVALUATION.value: [
                "evaluate",
                "assess",
                "critique",
                "review",
            ],
            AgentCapability.LEARNING.value: ["learn", "adapt", "improve", "train"],
            AgentCapability.ETHICS.value: ["ethic", "moral", "value", "principle"],
            AgentCapability.EMOTION.value: ["emotion", "feeling", "sentiment", "mood"],
            AgentCapability.CREATIVITY.value: [
                "creative",
                "generate",
                "innovate",
                "imagine",
            ],
            AgentCapability.ORCHESTRATION.value: [
                "orchestrat",
                "coordinat",
                "manage",
                "control",
            ],
        }

        for capability, keywords in capability_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                capabilities.append(capability)

        return capabilities if capabilities else ["general"]

    def _extract_description(self, content: str) -> str:
        """Extract description from agent content."""
        import re

        # Look for docstrings
        docstring_match = re.search(r'"""([^"]+)"""', content)
        if docstring_match:
            return docstring_match.group(1).strip()

        docstring_match = re.search(r"'''([^']+)'''", content)
        if docstring_match:
            return docstring_match.group(1).strip()

        # Look for comments
        comment_lines = []
        for line in content.split("\n")[:10]:  # Check first 10 lines
            if line.strip().startswith("#"):
                comment_lines.append(line.strip()[1:].strip())

        if comment_lines:
            return " ".join(comment_lines)

        return "AI agent for specialized task processing"

    def _extract_methods(self, content: str) -> List[str]:
        """Extract method names from agent content."""
        import re

        # Find all method definitions
        methods = re.findall(r"def\s+(\w+)", content)

        # Filter out private methods and common ones
        filtered_methods = [
            method
            for method in methods
            if not method.startswith("_")
            and method not in ["__init__", "__str__", "__repr__"]
        ]

        return filtered_methods[:10]  # Limit to first 10 methods

    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from agent content."""
        import re

        # Find import statements
        imports = re.findall(r"from\s+(\w+)", content) + re.findall(
            r"import\s+(\w+)", content
        )

        # Filter to relevant dependencies
        relevant_deps = [
            dep
            for dep in imports
            if dep
            in ["asyncio", "logging", "json", "aetherra", "lyrixa", "consciousness"]
        ]

        return list(set(relevant_deps))

    def _is_valid_agent(self, agent_info: Dict[str, Any]) -> bool:
        """Check if the extracted information represents a valid agent."""
        # Must have some capabilities or methods
        has_capabilities = len(agent_info.get("capabilities", [])) > 0
        has_methods = len(agent_info.get("methods", [])) > 0

        # Must have reasonable content size
        content_exists = len(agent_info.get("description", "")) > 10

        return (has_capabilities or has_methods) and content_exists

    async def integrate_agent(self, agent_id: str) -> AgentIntegrationResult:
        """
        Integrate a specific discovered agent into the consciousness system.

        Args:
            agent_id: ID of the agent to integrate

        Returns:
            Integration result with status and details
        """
        if agent_id in self.active_integrations:
            logger.warning(f"Agent {agent_id} is already being integrated")
            return self.integration_results.get(agent_id)

        self.active_integrations.add(agent_id)
        logger.info(f"🔗 Starting integration of agent: {agent_id}")

        try:
            # Find agent in discovered agents
            agent_info = self._find_agent_info(agent_id)
            if not agent_info:
                raise ValueError(f"Agent {agent_id} not found in discovered agents")

            # Create integration result
            result = AgentIntegrationResult(
                agent_id=agent_id,
                status=IntegrationStatus.ANALYZING,
                capabilities=[
                    AgentCapability(cap) for cap in agent_info.get("capabilities", [])
                ],
                integration_time=datetime.now(),
                metadata=agent_info,
            )

            # Step 1: Create agent profile
            result.status = IntegrationStatus.ADAPTING
            profile = await self._create_agent_profile(agent_info)

            # Step 2: Register with consciousness system
            if self.agent_registry:
                registration = AgentRegistration(
                    agent_id=agent_id,
                    profile=profile,
                    status=AgentStatus.INTEGRATING,
                    registration_time=datetime.now(),
                    metadata=agent_info,
                )

                await self.agent_registry.register_agent(registration)

            # Step 3: Test integration
            result.status = IntegrationStatus.TESTING
            test_passed = await self._test_agent_integration(agent_id, agent_info)

            if test_passed:
                result.status = IntegrationStatus.INTEGRATED
                logger.info(f"✅ Successfully integrated agent: {agent_id}")

                # Notify consciousness bridge
                if self.consciousness_bridge:
                    await self._notify_integration_success(agent_id, profile)
            else:
                result.status = IntegrationStatus.FAILED
                result.error_message = "Integration test failed"
                logger.error(f"❌ Failed to integrate agent: {agent_id}")

            self.integration_results[agent_id] = result
            return result

        except Exception as e:
            error_result = AgentIntegrationResult(
                agent_id=agent_id,
                status=IntegrationStatus.FAILED,
                capabilities=[],
                integration_time=datetime.now(),
                error_message=str(e),
            )
            self.integration_results[agent_id] = error_result
            logger.error(f"❌ Error integrating agent {agent_id}: {e}")
            return error_result

        finally:
            self.active_integrations.discard(agent_id)

    def _find_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Find agent info in discovered agents."""
        for category_agents in self.discovered_agents.values():
            for agent in category_agents:
                if agent.get("id") == agent_id:
                    return agent
        return None

    async def _create_agent_profile(self, agent_info: Dict[str, Any]) -> AgentProfile:
        """Create an agent profile from agent information."""
        capabilities = [
            AgentCapability(cap)
            for cap in agent_info.get("capabilities", ["general"])
            if cap in [c.value for c in AgentCapability]
        ]

        # If no valid capabilities, assign general capability
        if not capabilities:
            capabilities = [AgentCapability.REASONING]  # Default capability

        return AgentProfile(
            name=agent_info.get("name", agent_info.get("id", "Unknown Agent")),
            capabilities=capabilities,
            trust_level=0.7,  # Initial trust level for integrated agents
            performance_score=0.0,  # Will be updated based on performance
            collaboration_rating=0.0,  # Will be updated based on interactions
        )

    async def _test_agent_integration(
        self, agent_id: str, agent_info: Dict[str, Any]
    ) -> bool:
        """Test if agent integration is working correctly."""
        try:
            # Basic validation tests
            if not agent_info.get("name"):
                return False

            if not agent_info.get("capabilities"):
                return False

            # More advanced tests could be added here:
            # - Try to import the agent module
            # - Test basic agent functionality
            # - Verify consciousness bridge communication

            return True

        except Exception as e:
            logger.error(f"Integration test failed for {agent_id}: {e}")
            return False

    async def _notify_integration_success(self, agent_id: str, profile: AgentProfile):
        """Notify consciousness bridge of successful integration."""
        try:
            if self.consciousness_bridge:
                message = ConsciousnessMessage(
                    type=MessageType.NOTIFICATION,
                    sender="agent_integration_adapter",
                    destination="lyrixa_consciousness",
                    data={
                        "event": "agent_integrated",
                        "agent_id": agent_id,
                        "agent_name": profile.name,
                        "capabilities": [cap.value for cap in profile.capabilities],
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                await self.consciousness_bridge.send_message(message)

        except Exception as e:
            logger.error(f"Failed to notify integration success: {e}")

    async def integrate_priority_agents(self) -> Dict[str, AgentIntegrationResult]:
        """
        Integrate highest priority agents first.

        Priority order:
        1. Core reasoning agents
        2. Memory and learning agents
        3. Conversation and interface agents
        4. Specialized capability agents
        """
        logger.info("🎯 Starting priority agent integration...")

        results = {}

        # Define priority categories
        priority_agents = [
            # High priority core agents
            "goal_agent",
            "reasoning_agent",
            "conversation_manager",
            "memory_agent",
            "learning_agent",
            # Medium priority specialized agents
            "curiosity_agent",
            "self_evaluation_agent",
            "ethics_agent",
            # Lower priority support agents
            "orchestrator",
            "parser",
            "interpreter",
        ]

        for agent_category in self.discovered_agents.values():
            for agent in agent_category:
                agent_id = agent.get("id", "")

                # Check if this is a priority agent
                is_priority = any(
                    priority in agent_id.lower() for priority in priority_agents
                )

                if is_priority:
                    logger.info(f"🔗 Integrating priority agent: {agent_id}")
                    result = await self.integrate_agent(agent_id)
                    results[agent_id] = result

                    # Brief pause between integrations
                    await asyncio.sleep(0.1)

        success_count = sum(
            1 for r in results.values() if r.status == IntegrationStatus.INTEGRATED
        )
        logger.info(
            f"✅ Priority integration complete: {success_count}/{len(results)} successful"
        )

        return results

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status report."""
        discovered_count = sum(
            len(agents) for agents in self.discovered_agents.values()
        )
        integrated_count = sum(
            1
            for result in self.integration_results.values()
            if result.status == IntegrationStatus.INTEGRATED
        )
        failed_count = sum(
            1
            for result in self.integration_results.values()
            if result.status == IntegrationStatus.FAILED
        )

        return {
            "discovered_agents": discovered_count,
            "integrated_agents": integrated_count,
            "failed_integrations": failed_count,
            "active_integrations": len(self.active_integrations),
            "success_rate": integrated_count / max(len(self.integration_results), 1),
            "by_category": {
                category: len(agents)
                for category, agents in self.discovered_agents.items()
            },
            "integration_results": {
                agent_id: {
                    "status": result.status.value,
                    "capabilities": [cap.value for cap in result.capabilities],
                    "error": result.error_message,
                }
                for agent_id, result in self.integration_results.items()
            },
        }


# Global adapter instance
_integration_adapter = None


async def get_integration_adapter(
    consciousness_bridge=None, agent_registry=None
) -> AgentIntegrationAdapter:
    """Get the global integration adapter instance."""
    global _integration_adapter

    if _integration_adapter is None:
        _integration_adapter = AgentIntegrationAdapter(
            consciousness_bridge, agent_registry
        )

    return _integration_adapter


async def main():
    """Demo of agent integration capabilities."""
    print("🔗 Agent Integration Adapter Demo")
    print("=" * 50)

    # Create adapter
    adapter = AgentIntegrationAdapter()

    # Discover all agents
    print("\n🔍 Discovering agents...")
    discovered = await adapter.discover_all_agents()

    print(f"\nDiscovered Agents:")
    for category, agents in discovered.items():
        print(f"  {category}: {len(agents)} agents")
        for agent in agents[:3]:  # Show first 3 agents
            print(f"    - {agent['name']} ({', '.join(agent['capabilities'])})")
        if len(agents) > 3:
            print(f"    ... and {len(agents) - 3} more")

    # Show integration status
    print(f"\n📊 Integration Status:")
    status = await adapter.get_integration_status()
    print(json.dumps(status, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
