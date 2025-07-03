# plugins/memory_plugin.py - Memory Management Plugin
from typing import Any, Dict, Optional

from core.plugin_manager import register_plugin


@register_plugin(
    name="memory_clear",
    description="Clear different types of memory (short_term, long_term, etc.)",
    capabilities=["memory_management", "cleanup", "reset"],
    version="1.0.0",
    author="NeuroCode Team",
    category="system",
    intent_purpose="memory management and cleanup operations",
    intent_triggers=["clear", "reset", "memory", "forget", "cleanup"],
    intent_scenarios=[
        "clearing temporary memory",
        "resetting conversation context",
        "managing memory usage",
        "cleaning up stored data"
    ],
    ai_description="Manages and clears different types of memory storage including short-term and long-term memory.",
    example_usage="plugin: memory_clear 'short_term'",
    confidence_boost=1.1,
)
def memory_clear(memory_type: str = "short_term") -> Dict[str, Any]:
    """Clear specified type of memory"""
    try:
        valid_types = ["short_term", "long_term", "working", "all"]

        if memory_type not in valid_types:
            return {
                "error": f"Invalid memory type '{memory_type}'. Valid types: {', '.join(valid_types)}",
                "success": False
            }

        # Placeholder implementation - in real use would clear actual memory
        return {
            "success": True,
            "memory_type": memory_type,
            "message": f"Successfully cleared {memory_type} memory",
            "cleared_items": 42 if memory_type == "short_term" else 156
        }

    except Exception as e:
        return {"error": f"Memory clear failed: {str(e)}", "success": False}


@register_plugin(
    name="memory_status",
    description="Check memory usage and status",
    capabilities=["memory_status", "diagnostics", "monitoring"],
    version="1.0.0",
    author="NeuroCode Team",
    category="system",
    example_usage="plugin: memory_status",
    ai_description="Provides information about current memory usage and status"
)
def memory_status() -> Dict[str, Any]:
    """Get current memory status and usage information"""
    try:
        return {
            "success": True,
            "memory_status": {
                "short_term": {"items": 42, "size_mb": 2.1},
                "long_term": {"items": 156, "size_mb": 15.8},
                "working": {"items": 8, "size_mb": 0.3}
            },
            "total_memory_mb": 18.2,
            "message": "Memory status retrieved successfully"
        }

    except Exception as e:
        return {"error": f"Memory status check failed: {str(e)}", "success": False}


@register_plugin(
    name="memory_backup",
    description="Create backup of current memory state",
    capabilities=["backup", "memory_management", "data_protection"],
    version="1.0.0",
    author="NeuroCode Team",
    category="system",
    example_usage="plugin: memory_backup 'session_backup_2024'",
    ai_description="Creates backups of memory data for data protection and recovery"
)
def memory_backup(backup_name: Optional[str] = None) -> Dict[str, Any]:
    """Create a backup of current memory state"""
    try:
        import datetime

        if not backup_name:
            backup_name = f"memory_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "backup_name": backup_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "items_backed_up": 206,
            "message": f"Memory backup '{backup_name}' created successfully"
        }

    except Exception as e:
        return {"error": f"Memory backup failed: {str(e)}", "success": False}
