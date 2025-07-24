#!/usr/bin/env python3
"""
🔁 LYRIXA AUTONOMOUS SELF-IMPROVEMENT SCHEDULER
==============================================

Schedules and manages autonomous self-improvement tasks.
Runs periodic introspection, analysis, and self-enhancement workflows.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.enhanced_memory import LyrixaEnhancedMemorySystem
from ..plugins.introspector_plugin import IntrospectorPlugin


class SelfImprovementScheduler:
    """Manages autonomous self-improvement cycles"""

    def __init__(
        self,
        workspace_path: str,
        memory_system: LyrixaEnhancedMemorySystem,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.workspace_path = Path(workspace_path)
        self.memory_system = memory_system
        self.config = config or {}

        # Default configuration
        self.default_config = {
            "introspection_interval_hours": 24,
            "target_files": [
                "lyrixa/assistant.py",
                "lyrixa/assistant_rebuilt.py",
                "lyrixa/core/*.py",
                "lyrixa/plugins/*.py",
                "src/aetherra/plugins/*.py",
                "*.aether",
            ],
            "analysis_depth": "medium",
            "auto_remediation_enabled": False,
            "max_issues_per_cycle": 50,
        }

        self.introspector = IntrospectorPlugin(memory_system)
        self.last_run_file = self.workspace_path / ".lyrixa_last_introspection"
        self.is_running = False

    async def start_autonomous_cycle(self):
        """Start the autonomous self-improvement cycle"""
        if self.is_running:
            print("🔄 Autonomous cycle already running")
            return

        self.is_running = True
        print("🚀 Starting Lyrixa autonomous self-improvement cycle...")

        try:
            while self.is_running:
                if await self._should_run_introspection():
                    await self._run_introspection_cycle()

                # Wait before next check (check every hour)
                await asyncio.sleep(3600)  # 1 hour

        except Exception as e:
            print(f"❌ Autonomous cycle error: {e}")
        finally:
            self.is_running = False

    async def stop_autonomous_cycle(self):
        """Stop the autonomous cycle"""
        print("🛑 Stopping autonomous self-improvement cycle...")
        self.is_running = False

    async def run_manual_introspection(self) -> Dict[str, Any]:
        """Run introspection manually (for testing or immediate analysis)"""
        print("🔍 Running manual introspection cycle...")
        return await self._run_introspection_cycle()

    async def _should_run_introspection(self) -> bool:
        """Check if it's time to run introspection"""
        interval_hours = self.config.get(
            "introspection_interval_hours",
            self.default_config["introspection_interval_hours"],
        )

        if not self.last_run_file.exists():
            return True

        try:
            last_run_data = json.loads(self.last_run_file.read_text())
            last_run_time = datetime.fromisoformat(last_run_data["timestamp"])

            time_since_last = datetime.now() - last_run_time
            return time_since_last >= timedelta(hours=interval_hours)

        except Exception:
            # If we can't read the file, assume we should run
            return True

    async def _run_introspection_cycle(self) -> Dict[str, Any]:
        """Run a complete introspection and analysis cycle"""
        cycle_start = datetime.now()
        print(f"🔍 Starting introspection cycle at {cycle_start.isoformat()}")

        # Get target files for analysis
        target_files = await self._get_target_files()

        # Run introspection analysis
        analysis_depth = self.config.get(
            "analysis_depth", self.default_config["analysis_depth"]
        )
        results = await self.introspector.main(target_files, analysis_depth)

        # Process results and generate action plan
        action_plan = await self._generate_action_plan(results)

        # Store cycle results
        cycle_data = {
            "timestamp": cycle_start.isoformat(),
            "target_files": target_files,
            "analysis_results": results,
            "action_plan": action_plan,
            "cycle_duration": (datetime.now() - cycle_start).total_seconds(),
        }

        await self._store_cycle_results(cycle_data)
        await self._update_last_run(cycle_data)

        # Execute auto-remediation if enabled
        if self.config.get("auto_remediation_enabled", False):
            await self._execute_auto_remediation(action_plan)

        print(
            f"✅ Introspection cycle complete. Found {len(results.get('insights', []))} insights"
        )

        return cycle_data

    async def _get_target_files(self) -> List[str]:
        """Get list of files to analyze"""
        target_patterns = self.config.get(
            "target_files", self.default_config["target_files"]
        )
        target_files = []

        for pattern in target_patterns:
            if "*" in pattern:
                # Handle glob patterns
                try:
                    matches = list(self.workspace_path.glob(pattern))
                    target_files.extend([str(f) for f in matches if f.is_file()])
                except Exception as e:
                    print(f"⚠️ Error processing pattern '{pattern}': {e}")
            else:
                # Handle direct file paths
                file_path = self.workspace_path / pattern
                if file_path.exists() and file_path.is_file():
                    target_files.append(str(file_path))

        # Remove duplicates and limit to manageable number
        target_files = list(set(target_files))
        max_files = 50  # Reasonable limit
        if len(target_files) > max_files:
            target_files = target_files[:max_files]
            print(f"📊 Limited analysis to {max_files} files for performance")

        return target_files

    async def _generate_action_plan(
        self, analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate action plan based on analysis results"""
        insights = analysis_results.get("insights", [])
        recommendations = analysis_results.get("recommendations", [])

        # Prioritize actions by severity
        high_priority_actions = []
        medium_priority_actions = []
        low_priority_actions = []

        for insight in insights:
            severity = insight.get("severity", "low")
            actionable = insight.get("actionable", False)

            action = {
                "type": "insight_review",
                "insight": insight,
                "priority": severity,
                "auto_executable": actionable and severity != "high",
            }

            if severity == "high":
                high_priority_actions.append(action)
            elif severity == "medium":
                medium_priority_actions.append(action)
            else:
                low_priority_actions.append(action)

        # Add recommendation actions
        for rec in recommendations:
            medium_priority_actions.append(
                {
                    "type": "recommendation",
                    "recommendation": rec,
                    "priority": "medium",
                    "auto_executable": False,
                }
            )

        action_plan = {
            "high_priority": high_priority_actions,
            "medium_priority": medium_priority_actions,
            "low_priority": low_priority_actions,
            "total_actions": len(high_priority_actions)
            + len(medium_priority_actions)
            + len(low_priority_actions),
            "auto_executable_count": sum(
                1
                for action in high_priority_actions
                + medium_priority_actions
                + low_priority_actions
                if action.get("auto_executable", False)
            ),
        }

        return action_plan

    async def _store_cycle_results(self, cycle_data: Dict[str, Any]):
        """Store introspection cycle results in memory"""
        try:
            await self.memory_system.store_enhanced_memory(
                content={
                    "cycle_data": cycle_data,
                    "insights_count": len(
                        cycle_data["analysis_results"].get("insights", [])
                    ),
                    "recommendations_count": len(
                        cycle_data["analysis_results"].get("recommendations", [])
                    ),
                    "files_analyzed": len(cycle_data["target_files"]),
                },
                context={
                    "type": "autonomous_cycle",
                    "source": "self_improvement_scheduler",
                    "cycle_timestamp": cycle_data["timestamp"],
                },
                tags=["autonomous", "self_improvement", "introspection_cycle"],
                importance=0.9,
            )
            print("📝 Stored cycle results in memory")

        except Exception as e:
            print(f"⚠️ Failed to store cycle results: {e}")

    async def _update_last_run(self, cycle_data: Dict[str, Any]):
        """Update last run timestamp"""
        try:
            last_run_data = {
                "timestamp": cycle_data["timestamp"],
                "insights_found": len(
                    cycle_data["analysis_results"].get("insights", [])
                ),
                "files_analyzed": len(cycle_data["target_files"]),
            }

            self.last_run_file.write_text(json.dumps(last_run_data, indent=2))

        except Exception as e:
            print(f"⚠️ Failed to update last run file: {e}")

    async def _execute_auto_remediation(self, action_plan: Dict[str, Any]):
        """Execute automatic remediation for safe, low-risk actions"""
        auto_executable_actions = []

        # Collect auto-executable actions
        for priority_level in ["low_priority", "medium_priority"]:
            for action in action_plan.get(priority_level, []):
                if action.get("auto_executable", False):
                    auto_executable_actions.append(action)

        if not auto_executable_actions:
            print("🤖 No auto-executable actions found")
            return

        print(
            f"🤖 Executing {len(auto_executable_actions)} automatic remediation actions..."
        )

        remediation_results = []

        for action in auto_executable_actions[
            :5
        ]:  # Limit to 5 actions per cycle for safety
            try:
                result = await self._execute_remediation_action(action)
                remediation_results.append(result)

                # Store remediation result
                await self._store_remediation_result(action, result)

            except Exception as e:
                print(f"⚠️ Auto-remediation failed for action: {e}")
                remediation_results.append(
                    {"action": action, "success": False, "error": str(e)}
                )

        print(
            f"✅ Auto-remediation complete: {len(remediation_results)} actions processed"
        )

    async def _execute_remediation_action(
        self, action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific remediation action"""
        action_type = action.get("type")

        if action_type == "insight_review":
            insight = action.get("insight", {})
            insight_type = insight.get("type")

            # Handle specific insight types with safe auto-remediation
            if insight_type == "todo_fixme":
                return await self._remediate_todo(insight)
            elif insight_type == "documentation":
                return await self._suggest_documentation(insight)
            else:
                return {"success": False, "reason": "No auto-remediation available"}

        return {"success": False, "reason": "Unknown action type"}

    async def _remediate_todo(self, insight: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-remediate TODO/FIXME items (log for review)"""
        return {
            "success": True,
            "action": "logged_for_review",
            "message": f"TODO in {insight.get('file')} flagged for developer attention",
        }

    async def _suggest_documentation(self, insight: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest documentation improvements"""
        return {
            "success": True,
            "action": "documentation_suggestion",
            "message": f"Documentation suggestion created for {insight.get('file')}",
        }

    async def _store_remediation_result(
        self, action: Dict[str, Any], result: Dict[str, Any]
    ):
        """Store remediation results in memory"""
        try:
            await self.memory_system.store_enhanced_memory(
                content={
                    "action": action,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                },
                context={
                    "type": "auto_remediation",
                    "source": "self_improvement_scheduler",
                },
                tags=["auto_remediation", "autonomous", "self_healing"],
                importance=0.7,
            )

        except Exception as e:
            print(f"⚠️ Failed to store remediation result: {e}")

    async def get_improvement_metrics(self, days_back: int = 7) -> Dict[str, Any]:
        """Get metrics on self-improvement activities"""
        try:
            # Get recent autonomous cycles
            memories = await self.memory_system.get_memories_by_tags(
                ["autonomous", "self_improvement"], limit=50
            )

            recent_cycles = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for memory in memories:
                created_at = memory.get("created_at", "")
                if created_at:
                    try:
                        memory_date = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )
                        if memory_date > cutoff_date:
                            recent_cycles.append(memory)
                    except ValueError:
                        continue

            # Calculate metrics
            total_cycles = len(recent_cycles)
            total_insights = sum(
                memory.get("content", {}).get("insights_count", 0)
                for memory in recent_cycles
            )
            total_files_analyzed = sum(
                memory.get("content", {}).get("files_analyzed", 0)
                for memory in recent_cycles
            )

            return {
                "period_days": days_back,
                "total_cycles": total_cycles,
                "total_insights": total_insights,
                "total_files_analyzed": total_files_analyzed,
                "avg_insights_per_cycle": total_insights / max(total_cycles, 1),
                "improvement_trend": "stable",  # TODO: Calculate actual trend
                "last_cycle": recent_cycles[0].get("created_at")
                if recent_cycles
                else None,
            }

        except Exception as e:
            print(f"⚠️ Failed to calculate improvement metrics: {e}")
            return {"error": str(e)}


# Main function for plugin interface
async def main(input_data: Any, **kwargs) -> Dict[str, Any]:
    """Main entry point for scheduler plugin"""
    workspace_path = kwargs.get("workspace_path", ".")
    memory_system = kwargs.get("memory_system")

    if not memory_system:
        return {"error": "Memory system required for autonomous operation"}

    scheduler = SelfImprovementScheduler(workspace_path, memory_system)

    # Handle different input commands
    if isinstance(input_data, dict):
        command = input_data.get("command", "run_cycle")
    else:
        command = str(input_data) if input_data else "run_cycle"

    if command == "start_autonomous":
        # Note: This starts the cycle but doesn't block
        asyncio.create_task(scheduler.start_autonomous_cycle())
        return {"success": True, "message": "Autonomous cycle started"}
    elif command == "stop_autonomous":
        await scheduler.stop_autonomous_cycle()
        return {"success": True, "message": "Autonomous cycle stopped"}
    elif command == "metrics":
        metrics = await scheduler.get_improvement_metrics()
        return {"success": True, "metrics": metrics}
    else:
        # Default: run manual introspection
        results = await scheduler.run_manual_introspection()
        return {"success": True, "results": results}
