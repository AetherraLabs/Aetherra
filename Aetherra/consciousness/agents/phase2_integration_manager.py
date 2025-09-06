# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Phase 2 Agent Integration Manager
====================================

Manages the integration of discovered agents into the consciousness orchestrator.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class Phase2IntegrationManager:
    """
    Manages Phase 2 agent integration process.

    This manager coordinates the integration of existing agents with the
    consciousness orchestrator, ensuring collective intelligence capabilities.
    """

    def __init__(self):
        # Integration tracking
        self.integration_progress = {
            "phase": "Phase 2: Agent Integration",
            "status": "initializing",
            "total_discovered": 0,
            "total_integrated": 0,
            "integration_rate": 0.0,
            "priority_agents": [],
            "failed_integrations": [],
            "successful_integrations": [],
        }

        self.integration_adapter = None
        logger.info("Phase 2 Integration Manager initialized")

    async def initialize(self):
        """Initialize the integration manager and its components."""
        try:
            # Import and create integration adapter
            from .agent_integration_adapter import get_integration_adapter

            self.integration_adapter = await get_integration_adapter()
            self.integration_progress["status"] = "ready"
            logger.info("✅ Phase 2 Integration Manager ready")

        except Exception as e:
            self.integration_progress["status"] = "error"
            logger.error(f"❌ Failed to initialize integration manager: {e}")
            raise

    async def begin_phase_2_integration(self) -> Dict[str, Any]:
        """
        Begin Phase 2 agent integration process.

        Returns:
            Integration progress and results
        """
        logger.info("🚀 Starting Phase 2: Agent Integration")
        self.integration_progress["status"] = "discovering"

        try:
            # Step 1: Discover all available agents
            await self._discover_agents()

            # Step 2: Categorize agents by priority
            await self._categorize_agents()

            # Step 3: Begin priority agent integration
            await self._integrate_priority_agents()

            # Step 4: Integrate remaining agents
            await self._integrate_remaining_agents()

            # Step 5: Generate integration report
            await self._generate_integration_report()

            self.integration_progress["status"] = "completed"
            logger.info("✅ Phase 2 integration completed successfully")

        except Exception as e:
            self.integration_progress["status"] = "failed"
            logger.error(f"❌ Phase 2 integration failed: {e}")
            raise

        return self.integration_progress

    async def _discover_agents(self):
        """Discover all available agents in the system."""
        logger.info("🔍 Discovering agents across the system...")

        if not self.integration_adapter:
            raise Exception("Integration adapter not initialized")

        discovered = await self.integration_adapter.discover_all_agents()

        total_discovered = sum(len(agents) for agents in discovered.values())
        self.integration_progress["total_discovered"] = total_discovered

        logger.info(f"📊 Discovered {total_discovered} agents total")
        for category, agents in discovered.items():
            logger.info(f"  {category}: {len(agents)} agents")

    async def _categorize_agents(self):
        """Categorize agents by integration priority."""
        logger.info("🎯 Categorizing agents by priority...")

        discovered = await self.integration_adapter.discover_all_agents()

        # Priority keywords for high-value agents
        priority_keywords = [
            # Core intelligence
            "conversation",
            "memory",
            "reasoning",
            "goal",
            "learning",
            # Specialized capabilities
            "curiosity",
            "self_evaluation",
            "ethics",
            "emotion",
            "planning",
            # Management and orchestration
            "orchestrator",
            "manager",
            "coordinator",
            "supervisor",
        ]

        priority_agents = []

        for category_agents in discovered.values():
            for agent in category_agents:
                agent_id = agent.get("id", "").lower()
                agent_name = agent.get("name", "").lower()

                # Check if agent matches priority keywords
                is_priority = any(
                    keyword in agent_id or keyword in agent_name
                    for keyword in priority_keywords
                )

                if is_priority:
                    priority_agents.append(agent.get("id"))

        self.integration_progress["priority_agents"] = priority_agents
        logger.info(f"🎯 Identified {len(priority_agents)} priority agents")

    async def _integrate_priority_agents(self):
        """Integrate priority agents first."""
        logger.info("🔗 Integrating priority agents...")
        self.integration_progress["status"] = "integrating_priority"

        priority_count = 0
        priority_limit = 10  # Limit to first 10 priority agents

        for agent_id in self.integration_progress["priority_agents"][:priority_limit]:
            try:
                logger.info(f"🔗 Integrating priority agent: {agent_id}")
                result = await self.integration_adapter.integrate_agent(agent_id)

                from .agent_integration_adapter import IntegrationStatus

                if result.status == IntegrationStatus.INTEGRATED:
                    priority_count += 1
                    self.integration_progress["successful_integrations"].append(
                        {
                            "agent_id": agent_id,
                            "priority": True,
                            "capabilities": [cap.value for cap in result.capabilities],
                            "integration_time": result.integration_time.isoformat(),
                        }
                    )
                    logger.info(f"✅ Successfully integrated {agent_id}")
                else:
                    self.integration_progress["failed_integrations"].append(
                        {
                            "agent_id": agent_id,
                            "error": result.error_message,
                            "priority": True,
                        }
                    )
                    logger.warning(
                        f"⚠️ Failed to integrate {agent_id}: {result.error_message}"
                    )

                # Brief pause between integrations
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"❌ Failed to integrate priority agent {agent_id}: {e}")
                self.integration_progress["failed_integrations"].append(
                    {"agent_id": agent_id, "error": str(e), "priority": True}
                )

        logger.info(
            f"✅ Integrated {priority_count}/{min(len(self.integration_progress['priority_agents']), priority_limit)} priority agents"
        )
        return priority_count

    async def _integrate_remaining_agents(self):
        """Integrate remaining non-priority agents."""
        logger.info("🔄 Integrating remaining agents...")
        self.integration_progress["status"] = "integrating_remaining"

        # Get list of all discovered agents
        all_agents = []
        discovered = await self.integration_adapter.discover_all_agents()

        for category_agents in discovered.values():
            for agent in category_agents:
                agent_id = agent.get("id")
                if (
                    agent_id
                    and agent_id not in self.integration_progress["priority_agents"]
                ):
                    all_agents.append(agent_id)

        # Integrate up to 20 additional agents
        remaining_limit = 20
        remaining_count = 0

        for agent_id in all_agents[:remaining_limit]:
            try:
                result = await self.integration_adapter.integrate_agent(agent_id)

                from .agent_integration_adapter import IntegrationStatus

                if result.status == IntegrationStatus.INTEGRATED:
                    remaining_count += 1
                    self.integration_progress["successful_integrations"].append(
                        {
                            "agent_id": agent_id,
                            "priority": False,
                            "capabilities": [cap.value for cap in result.capabilities],
                            "integration_time": result.integration_time.isoformat(),
                        }
                    )
                else:
                    self.integration_progress["failed_integrations"].append(
                        {
                            "agent_id": agent_id,
                            "error": result.error_message,
                            "priority": False,
                        }
                    )

                # Brief pause between integrations
                await asyncio.sleep(0.05)

            except Exception as e:
                logger.error(f"❌ Failed to integrate agent {agent_id}: {e}")

        # Calculate totals
        priority_integrated = len(
            [
                i
                for i in self.integration_progress["successful_integrations"]
                if i["priority"]
            ]
        )
        total_integrated = priority_integrated + remaining_count

        self.integration_progress["total_integrated"] = total_integrated
        self.integration_progress["integration_rate"] = total_integrated / max(
            self.integration_progress["total_discovered"], 1
        )

        logger.info(f"✅ Integrated {remaining_count} additional agents")
        logger.info(
            f"📊 Total integration rate: {self.integration_progress['integration_rate']:.1%}"
        )

    async def _generate_integration_report(self):
        """Generate comprehensive integration report."""
        logger.info("📋 Generating integration report...")

        # Calculate statistics
        total_integrated = len(self.integration_progress["successful_integrations"])
        total_failed = len(self.integration_progress["failed_integrations"])

        # Group by capabilities
        capability_counts = {}
        for integration in self.integration_progress["successful_integrations"]:
            for capability in integration["capabilities"]:
                capability_counts[capability] = capability_counts.get(capability, 0) + 1

        # Create detailed report
        report = {
            "phase": "Phase 2: Agent Integration",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_discovered": self.integration_progress["total_discovered"],
                "total_integrated": total_integrated,
                "total_failed": total_failed,
                "integration_rate": f"{self.integration_progress['integration_rate']:.1%}",
                "priority_agents_integrated": len(
                    [
                        i
                        for i in self.integration_progress["successful_integrations"]
                        if i["priority"]
                    ]
                ),
            },
            "capability_distribution": capability_counts,
            "successful_integrations": self.integration_progress[
                "successful_integrations"
            ],
            "failed_integrations": self.integration_progress["failed_integrations"],
        }

        # Save report to file
        import json

        report_file = "phase2_integration_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Integration report saved to {report_file}")
        return report

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status and metrics."""
        return {**self.integration_progress, "timestamp": datetime.now().isoformat()}

    async def get_integrated_agents_summary(self) -> Dict[str, Any]:
        """Get summary of successfully integrated agents."""
        successful = self.integration_progress["successful_integrations"]

        # Count by capability
        by_capability = {}
        for integration in successful:
            for capability in integration["capabilities"]:
                by_capability[capability] = by_capability.get(capability, 0) + 1

        # Count by priority
        priority_count = len([i for i in successful if i["priority"]])
        regular_count = len(successful) - priority_count

        return {
            "total_integrated": len(successful),
            "priority_agents": priority_count,
            "regular_agents": regular_count,
            "by_capability": by_capability,
            "integration_rate": self.integration_progress["integration_rate"],
            "recent_integrations": successful[-5:] if successful else [],  # Last 5
        }


async def run_phase_2_integration():
    """Run Phase 2 integration standalone."""
    logger.info("🚀 Starting Phase 2 Integration")

    try:
        # Create integration manager
        integration_manager = Phase2IntegrationManager()
        await integration_manager.initialize()

        # Run Phase 2 integration
        result = await integration_manager.begin_phase_2_integration()

        print("\n🎉 Phase 2 Integration Results:")
        print(f"  Total Discovered: {result['total_discovered']}")
        print(f"  Total Integrated: {result['total_integrated']}")
        print(f"  Integration Rate: {result['integration_rate']:.1%}")
        print(f"  Priority Agents: {len(result['priority_agents'])}")
        print(f"  Failed Integrations: {len(result['failed_integrations'])}")

        # Get detailed summary
        summary = await integration_manager.get_integrated_agents_summary()
        print("\n📊 Integration Summary:")
        print(f"  Successfully Integrated: {summary['total_integrated']} agents")
        print(f"  Priority Agents: {summary['priority_agents']}")
        print(f"  Regular Agents: {summary['regular_agents']}")
        print(f"  Capabilities Added: {len(summary['by_capability'])} types")

        if summary["by_capability"]:
            print("\n🎯 Top Capabilities:")
            sorted_caps = sorted(
                summary["by_capability"].items(), key=lambda x: x[1], reverse=True
            )
            for cap, count in sorted_caps[:5]:
                print(f"    {cap}: {count} agents")

        return integration_manager

    except Exception as e:
        logger.error(f"❌ Phase 2 integration failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    asyncio.run(run_phase_2_integration())
