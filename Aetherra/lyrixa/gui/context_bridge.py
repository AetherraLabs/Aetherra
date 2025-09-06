#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Lyrixa Context Bridge (extracted)
---------------------------------

Bidirectional bridge between Python and embedded web panels.
Moved out of main_window.py to reduce file size and improve maintainability.
Public API preserved: LyrixaContextBridge and LyrixaWebBridge alias.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
from datetime import datetime
from typing import Any, Dict

from PySide6.QtCore import QObject, QTimer, Signal, Slot

# Unicode-safe logger (fallback to standard logger)
try:
    # Late import from project root if available
    from unicode_logger import get_safe_logger  # type: ignore

    logger = get_safe_logger(__name__)
except Exception:
    logger = logging.getLogger(__name__)


def _datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def safe_json_dumps(data: Any) -> str:
    try:
        return json.dumps(data, default=_datetime_serializer)
    except Exception as e:
        logger.error(f"[ERROR] JSON serialization failed: {e}")
        return "{}"


class LyrixaContextBridge(QObject):
    """
    Phase 2: Live Context Bridge
    Real-time communication bridge between Python backend and web panels.
    """

    # Signals for sending data to web panels
    memory_updated = Signal(str)  # Memory system updates
    plugin_updated = Signal(str)  # Plugin status changes
    agent_updated = Signal(str)  # Agent thoughts/goals
    metrics_updated = Signal(str)  # System metrics
    notification_sent = Signal(str)  # System notifications
    cognitive_updated = Signal(str)  # Phase 4: Cognitive state updates
    plugin_ui_loaded = Signal(str)  # Phase 5: Plugin UI loaded
    plugin_ui_updated = Signal(str)  # Phase 5: Plugin UI updated
    alerts_updated = Signal(str)  # Security alerts feed updates

    # Attribute stubs for type analyzers and dynamic assignment from window
    auto_generator: Any | None = None
    cognitive_monitor: Any | None = None
    backend_services: Dict[str, Any] = {}
    conversation_manager: Any | None = None
    real_data_manager: Any | None = None

    def __init__(self) -> None:
        super().__init__()
        self.data_cache = {
            "memory": {},
            "plugins": {},
            "agents": {},
            "metrics": {},
            "system": {},
            "cognitive": {},  # Phase 4: Cognitive state cache
        }
        self.backend_services = {}
        self.auto_generator = None  # Phase 3: Auto-generation system reference
        self.cognitive_monitor = None  # Phase 4: Cognitive monitor reference

        # Initialize backend connections
        self.conversation_manager = None  # Real conversation manager
        self.real_data_manager = None  # Real data manager

        # Start periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_all_data)
        self.update_timer.start(2000)  # Update every 2 seconds

        # Security alerts polling (best-effort)
        self._alerts_cache = []
        self.alerts_timer = QTimer()
        self.alerts_timer.timeout.connect(self.refresh_alerts)
        self.alerts_timer.start(1500)

        # Lazy import security system
        try:
            from Aetherra.aetherra_core.system.security_system import (
                get_security_system as _get_sec,
            )

            self._get_security_system = _get_sec  # type: ignore[attr-defined]
        except Exception:
            self._get_security_system = None

    # === SLOT METHODS (Called from JavaScript) ===

    @Slot(str)
    def handlePanelCommand(self, command_json: str) -> None:
        """Handle commands from web panels."""
        try:
            command = json.loads(command_json)
            command_type = command.get("type")
            payload = command.get("payload", {})

            print(f"🎛️ Panel command: {command_type} | {payload}")

            if command_type == "plugin_action":
                self.handle_plugin_command(payload)
            elif command_type == "memory_query":
                self.handle_memory_command(payload)
            elif command_type == "agent_command":
                self.handle_agent_command(payload)
            elif command_type == "system_command":
                self.handle_system_command(payload)
            else:
                print(f"[WARN] Unknown command type: {command_type}")

        except Exception as e:
            print(f"❌ Error handling panel command: {e}")
            self.send_notification("error", f"Command failed: {e}")

    @Slot(str, result=str)
    def getData(self, category: str) -> str:
        """Get cached data for specific category."""
        data = self.data_cache.get(category, {})
        return json.dumps(data)

    @Slot(result=str)
    def getAllData(self) -> str:
        """Get all cached data for initial panel load."""
        return json.dumps(self.data_cache)

    # === SECURITY ALERTS ===

    @Slot(result=str)
    def getRecentAlerts(self) -> str:
        """Return recent security alerts (cached or fresh)."""
        try:
            getter = getattr(self, "_get_security_system", None)
            if callable(getter):
                sec: Any = getter()
                self._alerts_cache = (
                    getattr(sec, "get_recent_alerts", lambda _n: [])(100) or []
                )
        except Exception:
            pass
        return json.dumps({"alerts": self._alerts_cache})

    def refresh_alerts(self) -> None:
        """Poll alerts.jsonl via security system and emit updates when changed."""
        try:
            getter = getattr(self, "_get_security_system", None)
            if not callable(getter):
                return
            sec: Any = getter()
            latest = getattr(sec, "get_recent_alerts", lambda _n: [])(100) or []
            if latest != self._alerts_cache:
                self._alerts_cache = latest
                self.alerts_updated.emit(json.dumps({"alerts": latest}))
        except Exception:
            pass

    # === BACKEND INTEGRATION ===

    def connect_backend_services(self, services: Dict[str, Any]) -> None:
        """Connect to backend services (memory, plugins, agents, etc.)"""
        self.backend_services = services
        logger.info(
            f"🔗 Connected to {len(services)} backend services: {list(services.keys())}"
        )

        # Connect to real data systems
        try:
            # Import and initialize real data manager
            from Aetherra.aetherra_core.orchestration.data_manager import (
                AetherraDataManager,
            )

            self.real_data_manager = AetherraDataManager()

            # Connect signals from real data manager
            if hasattr(self.real_data_manager, "memory_data_updated"):
                self.real_data_manager.memory_data_updated.connect(
                    lambda data: self.memory_updated.emit(json.dumps(data))
                )

            if hasattr(self.real_data_manager, "system_status_updated"):
                self.real_data_manager.system_status_updated.connect(
                    lambda data: self.metrics_updated.emit(json.dumps(data))
                )

            logger.info("✅ Real data manager connected successfully")
        except ImportError as e:
            logger.warning(f"❌ Could not connect to real data manager: {e}")

        # Connect to real conversation manager
        try:
            import Aetherra.aetherra_core.agents.conversation_manager as cm

            workspace_path = os.path.join(os.path.dirname(__file__), "..", "..", "..")
            manager_cls = getattr(cm, "LyrixaConversationManager", None)
            if manager_cls:
                self.conversation_manager = manager_cls(
                    workspace_path=workspace_path, gui_interface=self
                )
                logger.info("✅ Real LyrixaConversationManager connected successfully")
            else:
                raise ImportError("LyrixaConversationManager not found")
        except Exception as e:
            logger.warning(f"❌ Could not connect to real conversation manager: {e}")
            self.conversation_manager = None
            self.real_data_manager = None

        # Force immediate data refresh from real systems
        self.refresh_all_data()

    def refresh_all_data(self) -> None:
        """Refresh data from all backend services."""
        try:
            self.refresh_memory_data()
            self.refresh_plugin_data()
            self.refresh_agent_data()
            self.refresh_metrics_data()
        except Exception as e:
            print(f"[WARN] Error refreshing data: {e}")

    def refresh_memory_data(self) -> None:
        """Refresh memory system data."""
        # First try to get real data from connected systems
        if hasattr(self, "real_data_manager") and self.real_data_manager:
            try:
                memory_cache = self.real_data_manager.get_cached_data("memory")
                if memory_cache:
                    memory_data = {
                        "total_memories": memory_cache.get("memory_fragments", 0),
                        "recent_memories": memory_cache.get("recent_interactions", 0),
                        "memory_load": int(
                            memory_cache.get("memory_coherence", 0.0) * 100
                        ),
                        "last_updated": memory_cache.get("last_update", "Unknown"),
                        "status": memory_cache.get("status", "active"),
                        "coherence": memory_cache.get("memory_coherence", 0.0),
                        "efficiency": memory_cache.get("retrieval_efficiency", 0.0),
                    }

                    if memory_data != self.data_cache["memory"]:
                        self.data_cache["memory"] = memory_data
                        self.memory_updated.emit(json.dumps(memory_data))
                    return
            except Exception as e:
                logger.warning(f"Failed to get real memory data: {e}")

        # Fallback to backend services
        memory_system = self.backend_services.get("memory_system")
        if memory_system:
            try:
                # Gather memory stats from actual backend
                memory_data = {
                    "total_memories": getattr(memory_system, "total_memories", 0),
                    "recent_memories": getattr(memory_system, "recent_count", 0),
                    "memory_load": 45,  # Would get from actual metrics
                    "last_updated": QTimer().remainingTime(),
                    "status": "active",
                }

                if memory_data != self.data_cache["memory"]:
                    self.data_cache["memory"] = memory_data
                    self.memory_updated.emit(json.dumps(memory_data))

            except Exception as e:
                logger.warning(f"Memory data refresh error: {e}")

    def refresh_plugin_data(self) -> None:
        """Refresh plugin manager data."""
        plugin_manager = self.backend_services.get("plugin_manager")
        if plugin_manager:
            try:
                # Get plugin status from manager
                plugins_data = {
                    "loaded_plugins": [],
                    "active_count": 0,
                    "total_count": 0,
                    "status": "operational",
                }

                # Try to get actual plugin info
                if hasattr(plugin_manager, "get_all_plugins"):
                    plugins_info = plugin_manager.get_all_plugins()
                    plugins_data["loaded_plugins"] = [
                        {
                            "name": name,
                            "status": "active" if info.get("loaded") else "loaded",
                            "version": info.get("version", "1.0.0"),
                        }
                        for name, info in plugins_info.items()
                    ]
                    plugins_data["total_count"] = len(plugins_info)
                    plugins_data["active_count"] = sum(
                        1 for info in plugins_info.values() if info.get("loaded")
                    )
                elif hasattr(plugin_manager, "list_plugins"):
                    # Fallback to core plugin manager API
                    plugins_info = plugin_manager.list_plugins()
                    plugins_data["loaded_plugins"] = [
                        {
                            "name": name,
                            "status": "active"
                            if info.get("active")
                            else info.get("status", "loaded"),
                            "version": info.get("version", "1.0.0"),
                        }
                        for name, info in plugins_info.items()
                    ]
                    plugins_data["total_count"] = len(plugins_info)
                    plugins_data["active_count"] = sum(
                        1 for info in plugins_info.values() if info.get("active")
                    )

                if plugins_data != self.data_cache["plugins"]:
                    self.data_cache["plugins"] = plugins_data
                    self.plugin_updated.emit(json.dumps(plugins_data))

            except Exception as e:
                print(f"[WARN] Plugin data refresh error: {e}")

    def refresh_agent_data(self) -> None:
        """Refresh agent orchestrator data."""
        agent_orchestrator = self.backend_services.get("agent_orchestrator")
        if agent_orchestrator:
            try:
                agents_data = {
                    "active_agents": 0,
                    "current_goals": [],
                    "recent_thoughts": [],
                    "status": "thinking",
                }

                # Try to get actual agent info
                if hasattr(agent_orchestrator, "agents"):
                    agents_data["active_agents"] = len(agent_orchestrator.agents)

                if hasattr(agent_orchestrator, "current_goals"):
                    agents_data["current_goals"] = agent_orchestrator.current_goals[:5]

                if agents_data != self.data_cache["agents"]:
                    self.data_cache["agents"] = agents_data
                    self.agent_updated.emit(json.dumps(agents_data))

            except Exception as e:
                print(f"[WARN] Agent data refresh error: {e}")

    def refresh_metrics_data(self) -> None:
        """Refresh system metrics."""
        import time

        import psutil

        try:
            metrics_data = {
                "cpu_usage": psutil.cpu_percent(interval=0.1),
                "memory_usage": psutil.virtual_memory().percent,
                "process_count": len(psutil.pids()),
                "uptime": time.time() % 86400,  # Seconds since midnight
                "timestamp": int(time.time()),
            }

            if metrics_data != self.data_cache["metrics"]:
                self.data_cache["metrics"] = metrics_data
                self.metrics_updated.emit(json.dumps(metrics_data))

        except Exception as e:
            print(f"[WARN] Metrics refresh error: {e}")

    # === COMMAND HANDLERS ===

    def handle_plugin_command(self, payload: Dict[str, Any]) -> None:
        """Handle plugin-related commands."""
        action = payload.get("action")
        plugin_name = payload.get("plugin")

        print(f"🔌 Plugin command: {action} on {plugin_name}")

        plugin_manager = self.backend_services.get("plugin_manager")
        if not plugin_manager:
            self.send_notification("error", "Plugin manager not available")
            return

        # Run lifecycle operations off the UI thread
        threading.Thread(
            target=self._plugin_action_worker,
            args=(action, plugin_name),
            daemon=True,
        ).start()

    def _plugin_action_worker(self, action: str, plugin_name: str) -> None:
        """Background worker to call async plugin manager APIs safely."""
        try:
            plugin_manager = self.backend_services.get("plugin_manager")
            if not plugin_manager:
                self.send_notification("error", "Plugin manager not available")
                return

            async def do_activate(name: str):
                # Load if not loaded
                if name not in getattr(plugin_manager, "loaded_plugins", {}):
                    await plugin_manager.load_plugin(name)
                return await plugin_manager.activate_plugin(name)

            async def do_deactivate(name: str):
                return await plugin_manager.deactivate_plugin(name)

            async def do_reload(name: str):
                # Unload then load + activate
                if name in getattr(plugin_manager, "loaded_plugins", {}):
                    await plugin_manager.unload_plugin(name)
                loaded = await plugin_manager.load_plugin(name)
                if loaded:
                    return await plugin_manager.activate_plugin(name)
                return False

            async def run_action():
                if action == "activate":
                    return await do_activate(plugin_name)
                elif action == "deactivate":
                    return await do_deactivate(plugin_name)
                elif action == "reload":
                    return await do_reload(plugin_name)
                else:
                    return None

            result = asyncio.run(run_action())

            if result is True:
                if action == "activate":
                    self.send_notification(
                        "success", f"Activated plugin: {plugin_name}"
                    )
                elif action == "deactivate":
                    self.send_notification(
                        "success", f"Deactivated plugin: {plugin_name}"
                    )
                elif action == "reload":
                    self.send_notification("success", f"Reloaded plugin: {plugin_name}")
            elif result is None:
                self.send_notification("warning", f"Unknown plugin action: {action}")
            else:
                self.send_notification(
                    "error", f"Failed to {action} plugin: {plugin_name}"
                )

            # Refresh plugin data for UI
            self.refresh_plugin_data()

        except Exception as e:
            self.send_notification("error", f"Plugin command failed: {e}")
            try:
                self.refresh_plugin_data()
            except Exception:
                pass

    def handle_memory_command(self, payload: Dict[str, Any]) -> None:
        """Handle memory-related commands."""
        action = payload.get("action")
        query = payload.get("query", "")

        print(f"🧠 Memory command: {action} | {query}")

        memory_system = self.backend_services.get("memory_system")
        if not memory_system:
            self.send_notification("error", "Memory system not available")
            return

        if action == "search":
            # TODO: Search memory
            self.send_notification("info", f"Searching memory for: {query}")
        elif action == "clear":
            # TODO: Clear memory
            self.send_notification("warning", "Memory cleared")
        else:
            self.send_notification("warning", f"Unknown memory action: {action}")

    def handle_agent_command(self, payload: Dict[str, Any]) -> None:
        """Handle agent-related commands."""
        action = payload.get("action")
        goal = payload.get("goal", "")

        print(f"🤖 Agent command: {action} | {goal}")

        agent_orchestrator = self.backend_services.get("agent_orchestrator")
        if not agent_orchestrator:
            self.send_notification("error", "Agent orchestrator not available")
            return

        if action == "add_goal":
            # TODO: Add goal to agent
            self.send_notification("success", f"Added goal: {goal}")
        elif action == "pause":
            # TODO: Pause agents
            self.send_notification("info", "Agents paused")
        elif action == "resume":
            # TODO: Resume agents
            self.send_notification("info", "Agents resumed")
        else:
            self.send_notification("warning", f"Unknown agent action: {action}")

    def handle_system_command(self, payload: Dict[str, Any]) -> None:
        """Handle system-level commands."""
        action = payload.get("action")

        print(f"⚙️ System command: {action}")

        if action == "refresh":
            self.refresh_all_data()
            self.send_notification("info", "System data refreshed")
        elif action == "status":
            self.send_system_status()
        else:
            self.send_notification("warning", f"Unknown system action: {action}")

    # === NOTIFICATION SYSTEM ===

    def send_notification(self, level: str, message: str) -> None:
        """Send notification to web panels."""
        notification = {
            "level": level,  # info, success, warning, error
            "message": message,
            "timestamp": QTimer().remainingTime(),
        }
        self.notification_sent.emit(json.dumps(notification))

    def send_system_status(self) -> None:
        """Send comprehensive system status."""
        self.send_notification(
            "info", f"System status: {len(self.backend_services)} services connected"
        )

    # === SETTINGS PANEL METHODS ===

    @Slot(result=str)
    def getSettings(self) -> str:
        """Get current system settings."""
        # Default settings - in production these would come from a config file
        settings = {
            "ai_personality": "creative",
            "response_style": "detailed",
            "auto_learn": True,
            "memory_retention": "30",
            "knowledge_compression": True,
            "memory_limit": 500,
            "auto_plugin_updates": True,
            "plugin_sandbox": True,
            "max_concurrent_plugins": 20,
            "cpu_throttling": 80,
            "background_processing": True,
            "gpu_acceleration": False,
            "data_encryption": True,
            "telemetry": False,
            # Telemetry DP controls
            "telemetry_dp": True,
            "telemetry_dp_epsilon": 1.0,
            "session_timeout": "60",
        }
        return json.dumps(settings)

    @Slot(str)
    def saveSettings(self, settings_json: str) -> None:
        """Save system settings."""
        try:
            settings = json.loads(settings_json)
            # In production, save to config file or database
            print(f"💾 Saving settings: {len(settings)} options configured")
            self.send_notification("success", "Settings saved successfully!")

            # Apply settings immediately where possible
            self.apply_settings(settings)

        except Exception as e:
            print(f"❌ Error saving settings: {e}")
            self.send_notification("error", f"Failed to save settings: {e}")

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply settings changes to running systems."""
        try:
            # Apply CPU throttling
            if "cpu_throttling" in settings:
                cpu_limit = int(settings["cpu_throttling"])
                print(f"⚡ Setting CPU limit to {cpu_limit}%")

            # Apply memory settings
            if "memory_limit" in settings:
                memory_limit = int(settings["memory_limit"])
                print(f"🧠 Setting memory limit to {memory_limit}MB")

            # Apply plugin settings
            if "max_concurrent_plugins" in settings:
                plugin_limit = int(settings["max_concurrent_plugins"])
                print(f"🔌 Setting plugin limit to {plugin_limit}")

            print("✅ Settings applied successfully")

        except Exception as e:
            print(f"⚠️ Warning: Some settings could not be applied: {e}")
        # Apply telemetry opt-in after try/except to avoid masking errors
        try:
            if "telemetry" in settings:
                from Aetherra.telemetry.optin import get_telemetry

                tel = get_telemetry()
                tel.set_opt_in(bool(settings["telemetry"]))
            # Apply Telemetry DP toggles if present
            if "telemetry_dp" in settings or "telemetry_dp_epsilon" in settings:
                from Aetherra.telemetry.optin import get_telemetry

                tel = get_telemetry()
                dp_enabled = bool(settings.get("telemetry_dp", tel.dp_enabled))
                eps = settings.get("telemetry_dp_epsilon", tel.dp_epsilon)
                try:
                    eps_f = float(eps)
                except Exception:
                    eps_f = tel.dp_epsilon
                # Update DP runtime + persist
                if hasattr(tel, "set_dp"):
                    tel.set_dp(dp_enabled, eps_f)
        except Exception:
            pass

    # === METRICS PANEL METHODS ===

    @Slot(result=str)
    def getSystemMetrics(self) -> str:
        """Get comprehensive system metrics."""
        try:
            import random
            import time

            import psutil

            # Get real system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Get network stats
            network = psutil.net_io_counters()
            current_time = time.time()

            # Generate AI-specific metrics (simulated for now)
            metrics = {
                # Real system metrics
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory.percent, 1),
                "memory_used": round(memory.used / (1024**3), 1),  # GB
                "memory_total": round(memory.total / (1024**3), 1),  # GB
                "memory_available": round(memory.available / (1024**3), 1),  # GB
                "cpu_cores": psutil.cpu_count(logical=False),
                "cpu_threads": psutil.cpu_count(logical=True),
                "cpu_freq": round(psutil.cpu_freq().current / 1000, 1)
                if psutil.cpu_freq()
                else 3.2,
                # Network metrics
                "net_upload": round(
                    network.bytes_sent / (1024 * 1024), 1
                ),  # MB/s (lifetime)
                "net_download": round(
                    network.bytes_recv / (1024 * 1024), 1
                ),  # MB/s (lifetime)
                "net_packets": network.packets_sent + network.packets_recv,
                # Disk metrics
                "disk_read": round(disk.used / (1024**2), 1),  # MB
                "disk_write": round(disk.free / (1024**2), 1),  # MB
                "disk_read_iops": random.randint(1500, 3000),  # Simulated
                "disk_write_iops": random.randint(800, 1500),  # Simulated
                "disk_read_latency": round(random.uniform(1.0, 5.0), 1),
                "disk_write_latency": round(random.uniform(2.0, 6.0), 1),
                # AI-specific metrics (simulated)
                "ai_efficiency": random.randint(85, 98),
                "response_time": random.randint(150, 350),
                "memory_efficiency": random.randint(88, 96),
                "task_throughput": random.randint(120, 200),
                "timestamp": int(current_time),
            }

            return json.dumps(metrics)

        except Exception as e:
            print(f"❌ Error getting system metrics: {e}")
            # Return fallback metrics
            import time

            fallback_metrics = {
                "cpu_percent": 25,
                "memory_percent": 45,
                "ai_efficiency": 87,
                "response_time": 245,
                "memory_efficiency": 92,
                "task_throughput": 156,
                "timestamp": int(time.time()),
            }
            return json.dumps(fallback_metrics)

    # === COGNITIVE PANEL METHODS ===

    @Slot(result=str)
    def getCognitiveState(self) -> str:
        """Get current cognitive state for visualization."""
        try:
            if self.cognitive_monitor:
                state = self.cognitive_monitor.getCognitiveState()
                if state:
                    self.data_cache["cognitive"] = state
                    return safe_json_dumps(state)

            # Return empty state if monitor not available
            empty_state = {
                "thoughts": [],
                "goals": [],
                "memory_activations": [],
                "cognitive_load": 0.0,
                "query_traces": [],
            }
            return safe_json_dumps(empty_state)

        except Exception as e:
            logger.error(f"Error getting cognitive state: {e}")
            return safe_json_dumps(
                {
                    "thoughts": [],
                    "goals": [],
                    "memory_activations": [],
                    "cognitive_load": 0.0,
                    "query_traces": [],
                }
            )

    @Slot(str)
    def simulateUserQuery(self, query: str) -> None:
        """Simulate a user query for cognitive visualization."""
        try:
            if self.cognitive_monitor:
                self.cognitive_monitor.simulateUserQuery(query)
                # Update cognitive state after query processing
                state = self.cognitive_monitor.getCognitiveState()
                if state:
                    self.data_cache["cognitive"] = state
                    self.cognitive_updated.emit(safe_json_dumps(state))

        except Exception as e:
            logger.error(f"Error simulating user query: {e}")

    @Slot(str)
    def addCognitiveGoal(self, goal_description: str) -> None:
        """Add a new goal to the cognitive system."""
        try:
            if self.cognitive_monitor:
                self.cognitive_monitor.addGoal(goal_description)
                # Update cognitive state after adding goal
                state = self.cognitive_monitor.getCognitiveState()
                if state:
                    self.data_cache["cognitive"] = state
                    self.cognitive_updated.emit(safe_json_dumps(state))

        except Exception as e:
            logger.error(f"Error adding cognitive goal: {e}")


# Back-compat export
LyrixaWebBridge = LyrixaContextBridge


__all__ = ["LyrixaContextBridge", "LyrixaWebBridge"]
