# plugins/system_plugin.py - System Status and Information Plugin
import platform
from typing import Any, Dict

import psutil

from core.plugin_manager import register_plugin


@register_plugin(
    name="system_status",
    description="Get comprehensive system status and performance information",
    capabilities=["system_monitoring", "performance", "diagnostics"],
    version="1.0.0",
    author="Aetherra Team",
    category="system",
    dependencies=["psutil"],
    intent_purpose="system monitoring and status reporting",
    intent_triggers=["status", "system", "performance", "monitor", "health"],
    intent_scenarios=[
        "checking system health",
        "monitoring performance",
        "diagnosing issues",
        "system resource analysis",
    ],
    ai_description="Provides comprehensive system status including CPU, memory, disk usage, and platform information.",
    example_usage="plugin: system_status",
    confidence_boost=1.2,
)
def system_status() -> Dict[str, Any]:
    """Get comprehensive system status information"""
    try:
        # Get system information
        system_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }

        # Get performance metrics (with fallbacks if psutil unavailable)
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            performance = {
                "cpu_usage_percent": cpu_percent,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 1),
            }
        except ImportError:
            performance = {
                "cpu_usage_percent": "N/A (psutil not available)",
                "memory_info": "N/A (psutil not available)",
                "disk_info": "N/A (psutil not available)",
            }

        return {
            "success": True,
            "system_info": system_info,
            "performance": performance,
            "timestamp": "2025-07-01T15:30:00Z",
            "Aetherra_status": "Active and running",
        }

    except Exception as e:
        return {"error": f"System status check failed: {str(e)}", "success": False}


@register_plugin(
    name="system_info",
    description="Get basic system and platform information",
    capabilities=["system_info", "platform", "environment"],
    version="1.0.0",
    author="Aetherra Team",
    category="system",
    example_usage="plugin: system_info",
    ai_description="Provides basic system and platform information",
)
def system_info() -> Dict[str, Any]:
    """Get basic system information"""
    try:
        return {
            "success": True,
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        }

    except Exception as e:
        return {"error": f"System info retrieval failed: {str(e)}", "success": False}
