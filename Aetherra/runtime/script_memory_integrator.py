# Aetherra Script Memory Integration
# Exports script metadata to memory for smart recommendations

from datetime import datetime
from typing import Any, Dict, List


class ScriptMemoryIntegrator:
    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self.script_profiles = {}

    def export_script_metadata(self, script_registry: Dict[str, Any]) -> bool:
        """Export script metadata to memory system"""
        try:
            scripts = script_registry.get("scripts", {})

            for script_name, script_data in scripts.items():
                # Create script profile for memory
                script_profile = {
                    "type": "script_profile",
                    "name": script_name,
                    "display_name": script_data.get("name", script_name),
                    "category": script_data.get("category", "unknown"),
                    "description": script_data.get("description", ""),
                    "tags": script_data.get("tags", []),
                    "commands": script_data.get("commands", []),
                    "use_cases": script_data.get("use_cases", []),
                    "complexity": script_data.get("complexity", "unknown"),
                    "execution_time": script_data.get("execution_time", "unknown"),
                    "path": script_data.get("path", ""),
                    "status": script_data.get("status", "unknown"),
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                }

                # Add scheduling info if available
                if "scheduling" in script_data:
                    script_profile["scheduling"] = script_data["scheduling"]

                # Add safety info if available
                if "safety_level" in script_data:
                    script_profile["safety_level"] = script_data["safety_level"]

                # Store in memory if memory system is available
                if self.memory_system:
                    self.memory_system.store(script_profile)
                else:
                    # Store locally if no memory system
                    self.script_profiles[script_name] = script_profile

            print(f"✅ Exported {len(scripts)} script profiles to memory")
            return True

        except Exception as e:
            print(f"❌ Failed to export script metadata: {e}")
            return False

    def get_script_recommendations(
        self, goal: str, context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Get script recommendations based on goal and context"""
        recommendations = []

        if not self.script_profiles:
            return recommendations

        goal_lower = goal.lower()

        for script_name, profile in self.script_profiles.items():
            score = 0

            # Check tags
            for tag in profile.get("tags", []):
                if tag.lower() in goal_lower:
                    score += 3

            # Check description
            description = profile.get("description", "").lower()
            if any(word in description for word in goal_lower.split()):
                score += 2

            # Check commands
            for command in profile.get("commands", []):
                if command.lower() in goal_lower:
                    score += 4

            # Check use cases
            for use_case in profile.get("use_cases", []):
                if any(word in use_case.lower() for word in goal_lower.split()):
                    score += 1

            # Consider context if provided
            if context:
                # Boost score for scripts in same category as recent activity
                if context.get("recent_category") == profile.get("category"):
                    score += 1

                # Boost score for scripts with matching complexity preference
                if context.get("complexity_preference") == profile.get("complexity"):
                    score += 1

            if score > 0:
                recommendations.append(
                    {
                        "script_name": script_name,
                        "profile": profile,
                        "relevance_score": score,
                    }
                )

        # Sort by relevance score
        recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)

        return recommendations[:5]  # Return top 5 recommendations

    def create_script_usage_memory(
        self, script_name: str, execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create memory entry for script usage"""
        usage_memory = {
            "type": "script_usage",
            "script_name": script_name,
            "timestamp": datetime.now().isoformat(),
            "execution_result": execution_result,
            "success": execution_result.get("success", False),
            "execution_time": execution_result.get("execution_time", 0),
            "output_summary": execution_result.get("output_summary", ""),
            "errors": execution_result.get("errors", []),
            "tags": ["script_execution", "automation", script_name],
        }

        # Store in memory if available
        if self.memory_system:
            self.memory_system.store(usage_memory)

        return usage_memory

    def get_script_usage_history(
        self, script_name: str = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get script usage history from memory"""
        if not self.memory_system:
            return []

        # Query memory for script usage
        query = {"type": "script_usage"}
        if script_name:
            query["script_name"] = script_name

        try:
            history = self.memory_system.query(query, limit=limit)
            return history
        except Exception as e:
            print(f"❌ Failed to get script usage history: {e}")
            return []

    def generate_script_insights(self) -> Dict[str, Any]:
        """Generate insights about script usage patterns"""
        insights = {
            "total_scripts": len(self.script_profiles),
            "by_category": {},
            "by_complexity": {},
            "most_used_scripts": [],
            "least_used_scripts": [],
            "success_rate": 0.0,
            "average_execution_time": 0.0,
        }

        # Categorize scripts
        for script_name, profile in self.script_profiles.items():
            category = profile.get("category", "unknown")
            complexity = profile.get("complexity", "unknown")

            insights["by_category"][category] = (
                insights["by_category"].get(category, 0) + 1
            )
            insights["by_complexity"][complexity] = (
                insights["by_complexity"].get(complexity, 0) + 1
            )

        # Get usage statistics if memory system is available
        if self.memory_system:
            usage_history = self.get_script_usage_history(limit=100)

            if usage_history:
                successful_executions = sum(
                    1 for entry in usage_history if entry.get("success", False)
                )
                insights["success_rate"] = (
                    successful_executions / len(usage_history) * 100
                )

                execution_times = [
                    entry.get("execution_time", 0) for entry in usage_history
                ]
                insights["average_execution_time"] = sum(execution_times) / len(
                    execution_times
                )

                # Count script usage frequency
                script_usage_count = {}
                for entry in usage_history:
                    script_name = entry.get("script_name", "unknown")
                    script_usage_count[script_name] = (
                        script_usage_count.get(script_name, 0) + 1
                    )

                # Sort by usage frequency
                sorted_usage = sorted(
                    script_usage_count.items(), key=lambda x: x[1], reverse=True
                )
                insights["most_used_scripts"] = sorted_usage[:5]
                insights["least_used_scripts"] = sorted_usage[-5:]

        return insights


# Initialize global script memory integrator
script_memory_integrator = ScriptMemoryIntegrator()
