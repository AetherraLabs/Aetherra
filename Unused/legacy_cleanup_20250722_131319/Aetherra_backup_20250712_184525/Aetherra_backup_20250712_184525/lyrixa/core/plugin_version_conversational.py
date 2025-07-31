#!/usr/bin/env python3
"""
🗣️ LYRIXA PLUGIN VERSION CONTROL CONVERSATIONAL INTERFACE
=========================================================

Conversational interface for Lyrixa to interact with the plugin version control system.
Enables natural language commands for:
- Viewing plugin history
- Rolling back plugins
- Comparing versions
- Managing snapshots

Examples:
- "Show me all previous versions of DataAnalyzer"
- "Rollback OptimizerPlugin to the version from yesterday"
- "Compare the current version of CleanerPlugin to last week's"
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Note: dateutil not available, using basic date parsing
# from dateutil import parser as date_parser
from .plugin_version_control import PluginVersionControl


class PluginVersionConversationalInterface:
    """Conversational interface for plugin version control"""

    def __init__(self, plugin_manager, version_control: PluginVersionControl):
        self.plugin_manager = plugin_manager
        self.version_control = version_control

        # Command patterns for natural language processing
        self.command_patterns = {
            "list_versions": [
                r"show.*version.*of\s+(\w+)",
                r"list.*history.*(\w+)",
                r"what versions.*(\w+)",
                r"(\w+).*version.*history",
                r"previous versions.*(\w+)",
            ],
            "rollback": [
                r"rollback\s+(\w+)\s+to\s+(.+)",
                r"restore\s+(\w+)\s+to\s+(.+)",
                r"revert\s+(\w+)\s+to\s+(.+)",
                r"go back.*(\w+).*to\s+(.+)",
            ],
            "compare_versions": [
                r"compare\s+(\w+)\s+(.+)\s+(?:with|to|and)\s+(.+)",
                r"diff.*(\w+).*between\s+(.+)\s+and\s+(.+)",
                r"show.*difference.*(\w+).*(.+).*(.+)",
            ],
            "create_snapshot": [
                r"snapshot\s+(\w+)",
                r"backup\s+(\w+)",
                r"save.*version.*(\w+)",
                r"create.*backup.*(\w+)",
            ],
            "plugin_stats": [
                r"stats.*(\w+)",
                r"statistics.*(\w+)",
                r"info.*(\w+).*version",
                r"(\w+).*version.*info",
            ],
            "cleanup": [
                r"cleanup.*(\w+)",
                r"clean.*old.*versions.*(\w+)",
                r"remove.*old.*(\w+)",
            ],
        }

    async def process_command(self, user_input: str) -> Dict[str, Any]:
        """
        Process a natural language command for plugin version control

        Args:
            user_input: Natural language command from user

        Returns:
            Dictionary with response and action details
        """
        user_input = user_input.lower().strip()

        # Try to match command patterns
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_input)
                if match:
                    return await self._execute_command(command_type, match, user_input)

        # If no pattern matches, provide suggestions
        return {
            "success": False,
            "response": "I didn't understand that version control command. Try:\n"
            "• 'Show versions of PluginName'\n"
            "• 'Rollback PluginName to yesterday'\n"
            "• 'Compare PluginName version A with version B'\n"
            "• 'Create snapshot of PluginName'\n"
            "• 'Show stats for PluginName'",
            "suggestions": [
                "Show versions of DataAnalyzer",
                "Rollback OptimizerPlugin to last week",
                "Compare FileManager current with previous",
                "Create snapshot of WebSearchPlugin",
            ],
        }

    async def _execute_command(
        self, command_type: str, match, user_input: str
    ) -> Dict[str, Any]:
        """Execute a specific command type"""
        try:
            if command_type == "list_versions":
                return await self._handle_list_versions(match)
            elif command_type == "rollback":
                return await self._handle_rollback(match, user_input)
            elif command_type == "compare_versions":
                return await self._handle_compare_versions(match)
            elif command_type == "create_snapshot":
                return await self._handle_create_snapshot(match)
            elif command_type == "plugin_stats":
                return await self._handle_plugin_stats(match)
            elif command_type == "cleanup":
                return await self._handle_cleanup(match)
            else:
                return {"success": False, "response": "Unknown command type"}

        except Exception as e:
            return {
                "success": False,
                "response": f"Error executing command: {e}",
                "error": str(e),
            }

    async def _handle_list_versions(self, match) -> Dict[str, Any]:
        """Handle listing plugin versions"""
        plugin_name = match.group(1)

        # Validate plugin exists
        if not self._plugin_exists(plugin_name):
            return {
                "success": False,
                "response": f"Plugin '{plugin_name}' not found. Available plugins: {self._get_available_plugins()}",
            }

        # Get version history
        history = self.plugin_manager.get_plugin_version_history(plugin_name)

        if not history:
            return {
                "success": True,
                "response": f"No version history found for {plugin_name}. This might be a new plugin.",
                "plugin_name": plugin_name,
                "versions": [],
            }

        # Format response
        response = f"📋 Version History for {plugin_name}:\n\n"

        for i, version in enumerate(history[:10]):  # Show latest 10 versions
            timestamp = version["timestamp"]
            confidence = version["confidence_score"]
            size = version.get("size", 0)

            # Format timestamp
            try:
                dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                time_ago = self._time_ago(dt)
            except Exception:
                formatted_time = timestamp
                time_ago = "unknown"

            response += f"{i + 1}. {formatted_time} ({time_ago})\n"
            response += f"   📊 Confidence: {confidence:.2f}, Size: {size} bytes\n"

            metadata = version.get("metadata", {})
            if metadata.get("description"):
                response += f"   📝 {metadata['description']}\n"
            response += "\n"

        if len(history) > 10:
            response += f"... and {len(history) - 10} more versions\n"

        return {
            "success": True,
            "response": response,
            "plugin_name": plugin_name,
            "versions": history,
            "total_count": len(history),
        }

    async def _handle_rollback(self, match, user_input: str) -> Dict[str, Any]:
        """Handle plugin rollback"""
        plugin_name = match.group(1)
        time_reference = match.group(2)

        # Validate plugin exists
        if not self._plugin_exists(plugin_name):
            return {"success": False, "response": f"Plugin '{plugin_name}' not found."}

        # Parse time reference to find appropriate version
        target_timestamp = self._parse_time_reference(plugin_name, time_reference)

        if not target_timestamp:
            return {
                "success": False,
                "response": f"Could not find a version matching '{time_reference}' for {plugin_name}. "
                f"Try 'show versions of {plugin_name}' to see available versions.",
            }

        # Perform rollback
        success = self.plugin_manager.rollback_plugin(plugin_name, target_timestamp)

        if success:
            return {
                "success": True,
                "response": f"✅ Successfully rolled back {plugin_name} to version {target_timestamp}.\n"
                f"The plugin has been restored and a backup of the current version was created.",
                "plugin_name": plugin_name,
                "timestamp": target_timestamp,
                "action": "rollback",
            }
        else:
            return {
                "success": False,
                "response": f"❌ Failed to rollback {plugin_name}. Check the console for details.",
                "plugin_name": plugin_name,
                "timestamp": target_timestamp,
            }

    async def _handle_compare_versions(self, match) -> Dict[str, Any]:
        """Handle version comparison"""
        plugin_name = match.group(1)
        version1_ref = match.group(2)
        version2_ref = match.group(3)

        # Validate plugin exists
        if not self._plugin_exists(plugin_name):
            return {"success": False, "response": f"Plugin '{plugin_name}' not found."}

        # Parse version references
        timestamp1 = self._parse_time_reference(plugin_name, version1_ref)
        timestamp2 = self._parse_time_reference(plugin_name, version2_ref)

        if not timestamp1 or not timestamp2:
            return {
                "success": False,
                "response": f"Could not find versions matching '{version1_ref}' and '{version2_ref}' for {plugin_name}.",
            }

        # Generate diff
        diff = self.plugin_manager.diff_plugin_versions(
            plugin_name, timestamp1, timestamp2
        )

        if diff.startswith("❌"):
            return {"success": False, "response": diff}

        # Summarize diff
        lines = diff.split("\n")
        added_lines = len([line for line in lines if line.startswith("+")])
        removed_lines = len([line for line in lines if line.startswith("-")])

        summary = (
            f"📊 Comparison: {plugin_name} versions {timestamp1} vs {timestamp2}\n\n"
        )
        summary += f"📈 Added lines: {added_lines}\n"
        summary += f"📉 Removed lines: {removed_lines}\n\n"
        summary += "💡 Use the GUI diff viewer for detailed visual comparison."

        return {
            "success": True,
            "response": summary,
            "plugin_name": plugin_name,
            "version1": timestamp1,
            "version2": timestamp2,
            "diff": diff,
            "stats": {"added_lines": added_lines, "removed_lines": removed_lines},
        }

    async def _handle_create_snapshot(self, match) -> Dict[str, Any]:
        """Handle snapshot creation"""
        plugin_name = match.group(1)

        # Validate plugin exists
        if not self._plugin_exists(plugin_name):
            return {"success": False, "response": f"Plugin '{plugin_name}' not found."}

        # Create snapshot
        success = self.plugin_manager.create_plugin_snapshot(
            plugin_name, 0.7, "Manual snapshot via conversation", "user"
        )

        if success:
            return {
                "success": True,
                "response": f"✅ Snapshot created for {plugin_name}.\n"
                f"This version is now safely backed up and can be restored later.",
                "plugin_name": plugin_name,
                "action": "snapshot_created",
            }
        else:
            return {
                "success": False,
                "response": f"❌ Failed to create snapshot for {plugin_name}.",
                "plugin_name": plugin_name,
            }

    async def _handle_plugin_stats(self, match) -> Dict[str, Any]:
        """Handle plugin statistics"""
        plugin_name = match.group(1)

        # Validate plugin exists
        if not self._plugin_exists(plugin_name):
            return {"success": False, "response": f"Plugin '{plugin_name}' not found."}

        # Get stats
        stats = self.plugin_manager.get_plugin_version_stats(plugin_name)

        if not stats:
            return {
                "success": True,
                "response": f"No version statistics available for {plugin_name}.",
                "plugin_name": plugin_name,
            }

        # Format stats
        response = f"📊 Version Statistics for {plugin_name}:\n\n"
        response += f"📋 Total Snapshots: {stats.get('total_snapshots', 0)}\n"
        response += f"📅 Recent Activity: {stats.get('recent_snapshots', 0)} snapshots in last 7 days\n"
        response += f"🎯 Average Confidence: {stats.get('average_confidence', 0):.2f}\n"
        response += f"🏆 Max Confidence: {stats.get('max_confidence', 0):.2f}\n"
        response += f"📈 Size Trend: {stats.get('size_trend', 'unknown')}\n"

        return {
            "success": True,
            "response": response,
            "plugin_name": plugin_name,
            "stats": stats,
        }

    async def _handle_cleanup(self, match) -> Dict[str, Any]:
        """Handle cleanup of old versions"""
        plugin_name = match.group(1)

        # Validate plugin exists
        if not self._plugin_exists(plugin_name):
            return {"success": False, "response": f"Plugin '{plugin_name}' not found."}

        # Perform cleanup
        removed_count = self.plugin_manager.cleanup_plugin_versions(plugin_name, 10)

        return {
            "success": True,
            "response": f"🧹 Cleanup complete for {plugin_name}.\n"
            f"Removed {removed_count} old snapshots, keeping the 10 most recent.",
            "plugin_name": plugin_name,
            "removed_count": removed_count,
        }

    def _plugin_exists(self, plugin_name: str) -> bool:
        """Check if a plugin exists"""
        return plugin_name in self.plugin_manager.plugin_info

    def _get_available_plugins(self) -> str:
        """Get list of available plugins"""
        plugins = list(self.plugin_manager.plugin_info.keys())
        return ", ".join(plugins[:5]) + ("..." if len(plugins) > 5 else "")

    def _parse_time_reference(self, plugin_name: str, time_ref: str) -> Optional[str]:
        """Parse time reference to find matching version timestamp"""
        time_ref = time_ref.lower().strip()

        # Get version history
        history = self.plugin_manager.get_plugin_version_history(plugin_name)
        if not history:
            return None

        # Handle relative time references
        now = datetime.now()

        if "yesterday" in time_ref:
            target_date = now - timedelta(days=1)
        elif "last week" in time_ref or "week ago" in time_ref:
            target_date = now - timedelta(weeks=1)
        elif "last month" in time_ref or "month ago" in time_ref:
            target_date = now - timedelta(days=30)
        elif "latest" in time_ref or "current" in time_ref or "newest" in time_ref:
            return history[0]["timestamp"] if history else None
        elif "previous" in time_ref or "last" in time_ref:
            return history[1]["timestamp"] if len(history) > 1 else None
        else:
            # Try to parse as basic date format (simplified without dateutil)
            try:
                # Simple date parsing - just try common formats
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y%m%d"]:
                    try:
                        target_date = datetime.strptime(time_ref, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError("No matching date format")
            except Exception:
                # If all else fails, try to match by timestamp directly
                for version in history:
                    if time_ref in version["timestamp"]:
                        return version["timestamp"]
                return None

        # Find closest version to target date
        best_match = None
        best_diff = float("inf")

        for version in history:
            try:
                version_dt = datetime.strptime(version["timestamp"], "%Y%m%d_%H%M%S")
                diff = abs((version_dt - target_date).total_seconds())

                if diff < best_diff:
                    best_diff = diff
                    best_match = version["timestamp"]
            except Exception:
                continue

        return best_match

    def _time_ago(self, timestamp: datetime) -> str:
        """Calculate human-readable time ago"""
        now = datetime.now()
        diff = now - timestamp

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"


# Integration function for Lyrixa's main conversation handler
async def handle_version_control_query(
    plugin_manager, user_input: str
) -> Optional[Dict[str, Any]]:
    """
    Handle version control queries in Lyrixa's main conversation flow

    Returns None if the query is not version control related,
    otherwise returns the response from the version control interface.
    """
    # Check if the input is related to version control
    version_keywords = [
        "version",
        "rollback",
        "snapshot",
        "backup",
        "history",
        "revert",
        "restore",
        "compare",
        "diff",
        "previous",
    ]

    if not any(keyword in user_input.lower() for keyword in version_keywords):
        return None

    # Create interface and process command
    interface = PluginVersionConversationalInterface(
        plugin_manager, plugin_manager.version_control
    )

    return await interface.process_command(user_input)
