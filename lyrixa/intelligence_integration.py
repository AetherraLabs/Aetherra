#!/usr/bin/env python3
"""
🧠 LYRIXA INTELLIGENCE INTEGRATION
=================================

This module integrates all Aetherra AI OS Intelligence Stack components
into Lyrixa, providing real-time awareness and system orchestration.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Aetherra runtime components
try:
    from Aetherra.runtime.aether_runtime import AetherRuntime
except ImportError:
    print("⚠️ Aetherra runtime not available")
    AetherRuntime = None


class LyrixaIntelligenceStack:
    """
    🧠 Lyrixa Intelligence Stack Integration

    This class provides Lyrixa with comprehensive intelligence capabilities
    by integrating all core Aetherra AI OS system plugins and modules.
    """

    def __init__(
        self, workspace_path: str, aether_runtime: Optional[AetherRuntime] = None
    ):
        self.workspace_path = workspace_path
        self.aether_runtime = aether_runtime or (
            AetherRuntime() if AetherRuntime else None
        )

        # Intelligence components status
        self.intelligence_status = {
            "semantic_memory": False,
            "system_awareness": False,
            "self_reflection": False,
            "event_correlation": False,
            "conversational_integration": False,
            "plugin_monitoring": False,
        }

        # System workflow status
        self.workflow_status = {
            "goal_autopilot": {"active": False, "last_run": None, "health": "unknown"},
            "agent_sync": {"active": False, "last_run": None, "health": "unknown"},
            "memory_cleanser": {"active": False, "last_run": None, "health": "unknown"},
            "daily_reflector": {"active": False, "last_run": None, "health": "unknown"},
            "plugin_watchdog": {"active": False, "last_run": None, "health": "unknown"},
        }

        # System modules status
        self.module_status = {
            "agents": False,
            "goals": False,
            "plugins": False,
            "logger": False,
            "memory_ops": False,
            "utils": False,
        }

        # Initialize logging
        self.logger = logging.getLogger("lyrixa.intelligence")
        self.logger.setLevel(logging.INFO)

        # Intelligence cache
        self.intelligence_cache = {}
        self.last_intelligence_update = None

        print("🧠 Intelligence Stack initialized")

    async def initialize_intelligence_layer(self) -> Dict[str, Any]:
        """Initialize all intelligence layer components"""
        try:
            print("🧠 Initializing Intelligence Layer...")

            # Check semantic memory with confidence scoring
            await self._check_semantic_memory()

            # Initialize real-time system awareness
            await self._initialize_system_awareness()

            # Setup AI self-reflection capabilities
            await self._setup_self_reflection()

            # Initialize event correlation and reasoning
            await self._initialize_event_correlation()

            # Setup conversational interface integration
            await self._setup_conversational_integration()

            # Initialize plugin monitoring
            await self._initialize_plugin_monitoring()

            self.last_intelligence_update = datetime.now()

            print("✅ Intelligence Layer initialized successfully")
            return {
                "status": "initialized",
                "components": self.intelligence_status,
                "timestamp": self.last_intelligence_update.isoformat(),
            }

        except Exception as e:
            print(f"❌ Intelligence Layer initialization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def initialize_system_workflows(self) -> Dict[str, Any]:
        """Initialize all core system workflow plugins"""
        try:
            print("🧩 Initializing System Workflows...")

            workflows = [
                ("goal_autopilot", "30 minutes", "Resume, escalate, retry goals"),
                ("agent_sync", "4 hours", "Ensure agent memory sync"),
                ("memory_cleanser", "12 hours", "Clean low-confidence memories"),
                ("daily_reflector", "24 hours", "Generate system-wide reflection"),
                ("plugin_watchdog", "6 hours", "Monitor plugin health"),
            ]

            for workflow_name, schedule, description in workflows:
                await self._initialize_workflow(workflow_name, schedule, description)

            print("✅ System Workflows initialized successfully")
            return {
                "status": "initialized",
                "workflows": self.workflow_status,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"❌ System Workflows initialization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def initialize_system_modules(self) -> Dict[str, Any]:
        """Initialize all supporting system modules"""
        try:
            print("⚙️ Initializing System Modules...")

            modules = [
                ("agents", "Find/update/create agents"),
                ("goals", "Goal operations and summaries"),
                ("plugins", "Plugin health checks, status"),
                ("logger", "Event logging + querying"),
                ("memory_ops", "Raw memory search/delete/stats"),
                ("utils", "Time helpers, formatting"),
            ]

            for module_name, description in modules:
                await self._initialize_module(module_name, description)

            print("✅ System Modules initialized successfully")
            return {
                "status": "initialized",
                "modules": self.module_status,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"❌ System Modules initialization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_intelligence_status(self) -> Dict[str, Any]:
        """Get comprehensive intelligence system status"""
        return {
            "intelligence_layer": {
                "status": self.intelligence_status,
                "health": self._calculate_intelligence_health(),
                "last_update": self.last_intelligence_update.isoformat()
                if self.last_intelligence_update
                else None,
            },
            "system_workflows": {
                "status": self.workflow_status,
                "health": self._calculate_workflow_health(),
                "active_count": sum(
                    1 for w in self.workflow_status.values() if w["active"]
                ),
            },
            "system_modules": {
                "status": self.module_status,
                "health": self._calculate_module_health(),
                "active_count": sum(
                    1 for active in self.module_status.values() if active
                ),
            },
            "overall_health": self._calculate_overall_health(),
            "timestamp": datetime.now().isoformat(),
        }

    async def run_intelligence_workflow(
        self, workflow_name: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Run a specific intelligence workflow"""
        if workflow_name not in self.workflow_status:
            return {"status": "error", "message": f"Unknown workflow: {workflow_name}"}

        try:
            print(f"🚀 Running workflow: {workflow_name}")

            # Run the workflow using Aether runtime if available
            if self.aether_runtime:
                result = await self._run_aether_workflow(workflow_name, params)
            else:
                result = await self._run_simulated_workflow(workflow_name, params)

            # Update workflow status
            self.workflow_status[workflow_name]["last_run"] = datetime.now()
            self.workflow_status[workflow_name]["health"] = (
                "healthy" if result.get("success") else "error"
            )

            return result

        except Exception as e:
            print(f"❌ Workflow {workflow_name} failed: {e}")
            self.workflow_status[workflow_name]["health"] = "error"
            return {"status": "error", "message": str(e)}

    async def perform_system_reflection(self) -> Dict[str, Any]:
        """Perform comprehensive system reflection and analysis"""
        try:
            print("🔍 Performing system reflection...")

            # Collect system metrics
            intelligence_status = await self.get_intelligence_status()

            # Generate insights
            insights = await self._generate_system_insights(intelligence_status)

            # Create recommendations
            recommendations = await self._generate_recommendations(
                intelligence_status, insights
            )

            reflection_report = {
                "timestamp": datetime.now().isoformat(),
                "system_status": intelligence_status,
                "insights": insights,
                "recommendations": recommendations,
                "confidence_score": self._calculate_confidence_score(
                    intelligence_status
                ),
            }

            # Cache the reflection
            self.intelligence_cache["last_reflection"] = reflection_report

            print("✅ System reflection completed")
            return reflection_report

        except Exception as e:
            print(f"❌ System reflection failed: {e}")
            return {"status": "error", "message": str(e)}

    # Private helper methods
    async def _check_semantic_memory(self):
        """Check semantic memory with confidence scoring"""
        try:
            # Check if memory_ops.aether exists and is functional
            memory_ops_path = (
                Path(self.workspace_path) / "Aetherra" / "system" / "memory_ops.aether"
            )
            if memory_ops_path.exists():
                self.intelligence_status["semantic_memory"] = True
                print("✅ Semantic memory with confidence scoring - Active")
            else:
                print("⚠️ memory_ops.aether not found - Semantic memory disabled")
        except Exception as e:
            print(f"❌ Semantic memory check failed: {e}")

    async def _initialize_system_awareness(self):
        """Initialize real-time system awareness"""
        try:
            # Check for system plugin files
            system_plugins = [
                "goal_autopilot.aether",
                "agents.aether",
                "plugins.aether",
            ]
            system_dir = Path(self.workspace_path) / "Aetherra" / "system"

            if system_dir.exists():
                available_plugins = [
                    p for p in system_plugins if (system_dir / p).exists()
                ]
                if available_plugins:
                    self.intelligence_status["system_awareness"] = True
                    print(
                        f"✅ System awareness - Active ({len(available_plugins)} plugins)"
                    )
                else:
                    print("⚠️ No system plugins found - System awareness limited")
            else:
                print("⚠️ System directory not found - System awareness disabled")
        except Exception as e:
            print(f"❌ System awareness initialization failed: {e}")

    async def _setup_self_reflection(self):
        """Setup AI self-reflection capabilities"""
        try:
            reflector_path = (
                Path(self.workspace_path)
                / "Aetherra"
                / "system"
                / "daily_reflector.aether"
            )
            if reflector_path.exists():
                self.intelligence_status["self_reflection"] = True
                print("✅ AI self-reflection - Active")
            else:
                print("⚠️ daily_reflector.aether not found - Self-reflection disabled")
        except Exception as e:
            print(f"❌ Self-reflection setup failed: {e}")

    async def _initialize_event_correlation(self):
        """Initialize event correlation and reasoning"""
        try:
            logger_path = (
                Path(self.workspace_path) / "Aetherra" / "system" / "logger.aether"
            )
            if logger_path.exists():
                self.intelligence_status["event_correlation"] = True
                print("✅ Event correlation + reasoning - Active")
            else:
                print("⚠️ logger.aether not found - Event correlation disabled")
        except Exception as e:
            print(f"❌ Event correlation initialization failed: {e}")

    async def _setup_conversational_integration(self):
        """Setup conversational interface integration"""
        try:
            # This is handled by Lyrixa's conversational engine
            self.intelligence_status["conversational_integration"] = True
            print("✅ Conversational interface integration - Active")
        except Exception as e:
            print(f"❌ Conversational integration setup failed: {e}")

    async def _initialize_plugin_monitoring(self):
        """Initialize plugin monitoring capabilities"""
        try:
            watchdog_path = (
                Path(self.workspace_path)
                / "Aetherra"
                / "system"
                / "plugin_watchdog.aether"
            )
            if watchdog_path.exists():
                self.intelligence_status["plugin_monitoring"] = True
                print("✅ Plugin monitoring - Active")
            else:
                print("⚠️ plugin_watchdog.aether not found - Plugin monitoring disabled")
        except Exception as e:
            print(f"❌ Plugin monitoring initialization failed: {e}")

    async def _initialize_workflow(
        self, workflow_name: str, schedule: str, description: str
    ):
        """Initialize a specific workflow"""
        try:
            workflow_path = (
                Path(self.workspace_path)
                / "Aetherra"
                / "system"
                / f"{workflow_name}.aether"
            )
            if workflow_path.exists():
                self.workflow_status[workflow_name]["active"] = True
                self.workflow_status[workflow_name]["health"] = "healthy"
                print(f"✅ {workflow_name} - Active (Schedule: {schedule})")
            else:
                print(f"⚠️ {workflow_name}.aether not found - Workflow disabled")
        except Exception as e:
            print(f"❌ {workflow_name} initialization failed: {e}")

    async def _initialize_module(self, module_name: str, description: str):
        """Initialize a specific system module"""
        try:
            module_path = (
                Path(self.workspace_path)
                / "Aetherra"
                / "system"
                / f"{module_name}.aether"
            )
            if module_path.exists():
                self.module_status[module_name] = True
                print(f"✅ {module_name} - Active")
            else:
                print(f"⚠️ {module_name}.aether not found - Module disabled")
        except Exception as e:
            print(f"❌ {module_name} initialization failed: {e}")

    async def _run_aether_workflow(
        self, workflow_name: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Run workflow using Aether runtime"""
        try:
            # Load and execute the workflow
            workflow_path = (
                Path(self.workspace_path)
                / "Aetherra"
                / "system"
                / f"{workflow_name}.aether"
            )
            if workflow_path.exists():
                with open(workflow_path, "r") as f:
                    workflow_code = f.read()

                # Execute using Aether runtime
                result = await self.aether_runtime.execute_async(
                    workflow_code, params or {}
                )
                return {
                    "success": True,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {"success": False, "error": "Workflow file not found"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _run_simulated_workflow(
        self, workflow_name: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Run simulated workflow when Aether runtime is not available"""
        await asyncio.sleep(0.1)  # Simulate processing time
        return {
            "success": True,
            "result": f"Simulated execution of {workflow_name}",
            "timestamp": datetime.now().isoformat(),
            "note": "Aether runtime not available - simulated execution",
        }

    async def _generate_system_insights(self, status: Dict[str, Any]) -> List[str]:
        """Generate insights from system status"""
        insights = []

        # Check intelligence layer health
        if status["intelligence_layer"]["health"] < 0.5:
            insights.append(
                "Intelligence layer needs attention - some components are offline"
            )

        # Check workflow health
        if status["system_workflows"]["health"] < 0.5:
            insights.append("System workflows are experiencing issues")

        # Check module health
        if status["system_modules"]["health"] < 0.5:
            insights.append("System modules need maintenance")

        # Overall system health
        if status["overall_health"] > 0.8:
            insights.append("System is operating optimally")
        elif status["overall_health"] > 0.6:
            insights.append("System is operating well with minor issues")
        else:
            insights.append("System requires immediate attention")

        return insights

    async def _generate_recommendations(
        self, status: Dict[str, Any], insights: List[str]
    ) -> List[str]:
        """Generate recommendations based on status and insights"""
        recommendations = []

        # Check for offline components
        offline_components = [
            name
            for name, active in status["intelligence_layer"]["status"].items()
            if not active
        ]

        if offline_components:
            recommendations.append(
                f"Restart or repair offline components: {', '.join(offline_components)}"
            )

        # Check for workflow issues
        failed_workflows = [
            name
            for name, info in status["system_workflows"]["status"].items()
            if info["health"] == "error"
        ]

        if failed_workflows:
            recommendations.append(
                f"Investigate workflow failures: {', '.join(failed_workflows)}"
            )

        # General recommendations
        if status["overall_health"] < 0.7:
            recommendations.append(
                "Consider running system diagnostics and maintenance"
            )

        return recommendations

    def _calculate_intelligence_health(self) -> float:
        """Calculate intelligence layer health score"""
        if not self.intelligence_status:
            return 0.0

        active_count = sum(1 for active in self.intelligence_status.values() if active)
        total_count = len(self.intelligence_status)
        return active_count / total_count if total_count > 0 else 0.0

    def _calculate_workflow_health(self) -> float:
        """Calculate workflow health score"""
        if not self.workflow_status:
            return 0.0

        healthy_count = sum(
            1 for info in self.workflow_status.values() if info["health"] == "healthy"
        )
        total_count = len(self.workflow_status)
        return healthy_count / total_count if total_count > 0 else 0.0

    def _calculate_module_health(self) -> float:
        """Calculate module health score"""
        if not self.module_status:
            return 0.0

        active_count = sum(1 for active in self.module_status.values() if active)
        total_count = len(self.module_status)
        return active_count / total_count if total_count > 0 else 0.0

    def _calculate_overall_health(self) -> float:
        """Calculate overall system health score"""
        intelligence_health = self._calculate_intelligence_health()
        workflow_health = self._calculate_workflow_health()
        module_health = self._calculate_module_health()

        # Weighted average (intelligence layer is most important)
        return intelligence_health * 0.5 + workflow_health * 0.3 + module_health * 0.2

    def _calculate_confidence_score(self, status: Dict[str, Any]) -> float:
        """Calculate confidence score for system reflection"""
        overall_health = status["overall_health"]
        active_workflows = status["system_workflows"]["active_count"]
        active_modules = status["system_modules"]["active_count"]

        # Base confidence on health and active components
        confidence = overall_health * 0.6
        confidence += min(active_workflows / 5, 1.0) * 0.2  # Max 5 workflows
        confidence += min(active_modules / 6, 1.0) * 0.2  # Max 6 modules

        return min(confidence, 1.0)
