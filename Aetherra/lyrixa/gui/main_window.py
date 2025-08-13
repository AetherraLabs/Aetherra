#!/usr/bin/env python3
"""
🎙️ Lyrixa Hybrid Window - Phase 1
==================================

PySide6 + Embedded Web Hybrid UI for Lyrixa AI Operating System
Combines native Qt performance with beautiful web-styled panels
matching the Aetherra.dev aesthetic.

Architecture:
- Base: PySide6 QMainWindow for native performance
- Panels: QWebEngineView embedding HTML panels styled like Aetherra.dev
- Communication: QWebChannel for bidirectional Python ↔ JavaScript
- Styling: Authentic Aetherra colors and effects
"""

import asyncio
import json
import logging
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Qt, QTimer, QUrl, Signal, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# Phase 3: Auto-Generation System
from .phase3_auto_generator import Phase3AutoGenerator

# Phase 4: Cognitive UI Integration
from .phase4_cognitive_ui import CognitiveStateMonitor

# Phase 5: Plugin-Driven UI System
from .phase5_plugin_ui import PluginUIManager

# Phase 6: Full GUI Personality + State Memory
from .phase6_personality import GUIPersonalityManager

# Import Unicode-safe logger
try:
    # Try to import from project root
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from unicode_logger import get_safe_logger

    logger = get_safe_logger(__name__)
    print(f"✅ Unicode logger successfully imported for {__name__}")
except ImportError as e:
    # Fallback to regular logger if unicode_logger not available
    print(f"❌ Unicode logger import failed: {e}, falling back to standard logger")
    import logging

    logger = logging.getLogger(__name__)


def datetime_serializer(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def safe_json_dumps(data):
    """Safely dump data to JSON with datetime handling"""
    try:
        return json.dumps(data, default=datetime_serializer)
    except Exception as e:
        logger.error(f"[ERROR] JSON serialization failed: {e}")
        return "{}"


class LyrixaContextBridge(QObject):
    """
    🌉 Phase 2: Live Context Bridge
    ===============================

    Real-time bidirectional communication bridge between Python backend
    and embedded web panels. Handles:
    - Memory stats and updates
    - Plugin status and controls
    - Agent goals and thoughts
    - System metrics and notifications
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

    def __init__(self):
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
        self.auto_generator: Optional[Any] = (
            None  # Phase 3: Auto-generation system reference
        )
        self.cognitive_monitor: Optional[Any] = (
            None  # Phase 4: Cognitive monitor reference
        )

        # Initialize backend connections
        self.conversation_manager: Optional[Any] = None  # Real conversation manager
        self.real_data_manager: Optional[Any] = None  # Real data manager

        # Start periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_all_data)
        self.update_timer.start(2000)  # Update every 2 seconds

    # === SLOT METHODS (Called from JavaScript) ===

    @Slot(str)
    def handlePanelCommand(self, command_json):
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
    def getData(self, category):
        """Get cached data for specific category."""
        data = self.data_cache.get(category, {})
        return json.dumps(data)

    @Slot(result=str)
    def getAllData(self):
        """Get all cached data for initial panel load."""
        return json.dumps(self.data_cache)

    # === BACKEND INTEGRATION ===

    def connect_backend_services(self, services: Dict[str, Any]):
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

    def refresh_all_data(self):
        """Refresh data from all backend services."""
        try:
            self.refresh_memory_data()
            self.refresh_plugin_data()
            self.refresh_agent_data()
            self.refresh_metrics_data()
        except Exception as e:
            print(f"[WARN] Error refreshing data: {e}")

    def refresh_memory_data(self):
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

    def refresh_plugin_data(self):
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

    def refresh_agent_data(self):
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
                    agents_data["current_goals"] = agent_orchestrator.current_goals[
                        :5
                    ]  # Last 5

                if agents_data != self.data_cache["agents"]:
                    self.data_cache["agents"] = agents_data
                    self.agent_updated.emit(json.dumps(agents_data))

            except Exception as e:
                print(f"[WARN] Agent data refresh error: {e}")

    def refresh_metrics_data(self):
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

    def handle_plugin_command(self, payload):
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

    def _plugin_action_worker(self, action: str, plugin_name: str):
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

    def handle_memory_command(self, payload):
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

    def handle_agent_command(self, payload):
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

    def handle_system_command(self, payload):
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

    def send_notification(self, level: str, message: str):
        """Send notification to web panels."""
        notification = {
            "level": level,  # info, success, warning, error
            "message": message,
            "timestamp": QTimer().remainingTime(),
        }
        self.notification_sent.emit(json.dumps(notification))

    def send_system_status(self):
        """Send comprehensive system status."""
        self.send_notification(
            "info", f"System status: {len(self.backend_services)} services connected"
        )

    # === SETTINGS PANEL METHODS ===

    @Slot(result=str)
    def getSettings(self):
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
            "session_timeout": "60",
        }
        return json.dumps(settings)

    @Slot(str)
    def saveSettings(self, settings_json):
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

    def apply_settings(self, settings):
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

    # === METRICS PANEL METHODS ===

    @Slot(result=str)
    def getSystemMetrics(self):
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
    def getCognitiveState(self):
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
    def simulateUserQuery(self, query):
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
    def addCognitiveGoal(self, goal_description):
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


# Maintain backward compatibility
LyrixaWebBridge = LyrixaContextBridge


class LyrixaHybridWindow(QMainWindow):
    """
    🎙️ Lyrixa Hybrid Window - PySide6 + Web Panel Integration

    Features:
    - Native Qt controls for performance-critical operations
    - Beautiful web panels matching Aetherra.dev styling
    - Dynamic panel loading and switching
    - Real-time data synchronization
    """

    def __init__(self):
        super().__init__()
        self.web_bridge = LyrixaWebBridge()
        self.web_panels = {}
        self.current_panel = None

        # Backend connections (will be set by launcher)
        self.service_registry = None
        self.plugin_manager = None
        self.lyrixa_engine = None
        self.memory_system = None
        self.agent_orchestrator = None

        # Real backend system connections
        self.conversation_manager = None
        self.real_data_manager = None

        # Phase 3: Auto-Generation System
        gui_dir = Path(__file__).parent
        self.auto_generator = Phase3AutoGenerator(gui_dir)
        self.auto_generated_panels = {}

        # Phase 4: Cognitive UI Integration
        self.cognitive_monitor = CognitiveStateMonitor()
        self.cognitive_timer = QTimer()

        # Phase 5: Plugin-Driven UI System
        self.plugin_ui_manager = PluginUIManager()
        self.plugin_panels = {}

        # Phase 6: Full GUI Personality + State Memory
        self.personality_manager = GUIPersonalityManager()
        self.chat_interface = None

        # Consciousness Integration
        self.consciousness_integrator = None

        self.setupUI()
        self.setupWebChannel()
        self.setupTimers()
        self.setupPhase3Integration()
        self.setupPhase4Integration()
        self.setupPhase5Integration()
        self.setupPhase6Integration()
        self.applyAetherraTheme()

    def setupUI(self):
        """Setup the main UI structure."""
        self.setWindowTitle("🎙️ Lyrixa AI Operating System")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Left panel - Native controls
        self.left_panel = self.createLeftPanel()
        self.splitter.addWidget(self.left_panel)

        # Center panel - Web view
        self.center_panel = self.createCenterPanel()
        self.splitter.addWidget(self.center_panel)

        # Right panel - Status and metrics
        self.right_panel = self.createRightPanel()
        self.splitter.addWidget(self.right_panel)

        # Set splitter proportions (20% : 60% : 20%)
        self.splitter.setSizes([280, 840, 280])

        # Menu bar
        self.createMenuBar()

        # Status bar
        self.createStatusBar()

        # Load default panel
        QTimer.singleShot(
            100, lambda: self.loadPanel("dashboard")
        )  # Small delay to ensure web channel is ready

    def createLeftPanel(self) -> QWidget:
        """Create the left native control panel."""
        panel = QFrame()
        panel.setFixedWidth(280)
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("🎙️ LYRIXA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #00ff88;
                padding: 20px;
                background: rgba(26, 26, 26, 0.8);
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Navigation buttons
        nav_buttons = [
            ("🧠 Neural Interface", "dashboard"),
            ("🔌 Plugin Manager", "plugins"),
            ("📈 Metrics", "metrics"),
            ("💭 Memory", "memory"),
            ("🧠 Cognitive UI", "cognitive"),
            ("⚛️ Consciousness", "consciousness"),  # New consciousness panel
            ("🔁 Plugin Demo", "plugin_demo"),
            ("💬 Chat with Lyrixa", "chat"),
            ("⚙️ Settings", "settings"),
        ]

        for text, panel_id in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName(f"nav_{panel_id}")
            btn.clicked.connect(lambda checked, pid=panel_id: self.loadPanel(pid))
            btn.setStyleSheet(self.getButtonStyle())
            layout.addWidget(btn)

        # Spacer
        layout.addStretch()

        # System status
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)

        self.status_label = QLabel("🌟 All Systems Online")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-weight: bold;
                padding: 10px;
                background: rgba(0, 255, 136, 0.1);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 6px;
            }
        """)
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_frame)

        return panel

    def createCenterPanel(self) -> QWidget:
        """Create the center web panel area."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Web engine view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        return panel

    def createRightPanel(self) -> QWidget:
        """Create the right metrics/status panel."""
        panel = QFrame()
        panel.setFixedWidth(280)
        layout = QVBoxLayout(panel)

        # Quick stats
        stats_title = QLabel("📊 Live Metrics")
        stats_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #00ff88;
                padding: 15px;
                background: rgba(26, 26, 26, 0.8);
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(stats_title)

        # Metrics widgets
        self.metrics_widgets = {}
        metrics = [
            ("Memory Load", "45%", "#00ff88"),
            ("CPU Usage", "23%", "#0078d4"),
            ("Agents Active", "7", "#ff6b00"),
            ("Plugins Loaded", "12", "#9d4edd"),
        ]

        for name, value, color in metrics:
            metric_widget = self.createMetricWidget(name, value, color)
            layout.addWidget(metric_widget)
            self.metrics_widgets[name] = metric_widget

        layout.addStretch()

        return panel

    def createMetricWidget(self, name: str, value: str, color: str) -> QWidget:
        """Create a metric display widget."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: rgba(26, 26, 26, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 10px;
                margin: 5px 0;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)

        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")

        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"color: {color}; font-size: 18px; font-weight: bold;"
        )

        layout.addWidget(name_label)
        layout.addWidget(value_label)

        return widget

    def createMenuBar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&New Project")
        file_menu.addAction("&Open Project")
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction("&Dashboard", lambda: self.loadPanel("dashboard"))
        view_menu.addAction("&Plugins", lambda: self.loadPanel("plugins"))
        view_menu.addAction("&Memory", lambda: self.loadPanel("memory"))

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("&Plugin Manager")
        tools_menu.addAction("&Memory Browser")
        tools_menu.addAction("&System Diagnostics")

    def createStatusBar(self):
        """Create the status bar."""
        status_bar = self.statusBar()
        status_bar.showMessage("🌟 Lyrixa AI Operating System - Ready")
        status_bar.setStyleSheet("""
            QStatusBar {
                background: #1a1a1a;
                color: #00ff88;
                border-top: 1px solid rgba(0, 255, 136, 0.3);
            }
        """)

    def setupWebChannel(self):
        """Setup QWebChannel for Python ↔ JavaScript communication."""
        self.web_channel = QWebChannel()
        self.web_channel.registerObject("pybridge", self.web_bridge)

        # Phase 4: Register cognitive monitor
        if hasattr(self, "cognitive_monitor"):
            self.web_channel.registerObject("cognitiveMonitor", self.cognitive_monitor)

        # Phase 5: Register plugin UI manager
        if hasattr(self, "plugin_ui_manager"):
            self.web_channel.registerObject("pluginManager", self.plugin_ui_manager)

        # Phase 6: Register personality manager
        if hasattr(self, "personality_manager"):
            self.web_channel.registerObject(
                "personality_manager", self.personality_manager
            )

            # Also register chat interface if available
            if hasattr(self.personality_manager, "chat_interface"):
                self.web_channel.registerObject(
                    "chat_interface", self.personality_manager.chat_interface
                )

        self.web_view.page().setWebChannel(self.web_channel)

    def _recreateWebView(self):
        """Recreate the web view when it's been deleted."""
        try:
            logger.debug("Recreating web view due to deletion")

            # Get the center panel layout
            if not hasattr(self, "center_panel") or not self.center_panel:
                logger.error("No center panel found to recreate web view")
                return False

            layout = self.center_panel.layout()
            if not layout:
                logger.error("No layout found in center panel")
                return False

            # Remove old web view if it exists
            if hasattr(self, "web_view"):
                try:
                    layout.removeWidget(self.web_view)
                    self.web_view.deleteLater()
                except Exception as e:
                    logger.debug(f"Error removing old web view: {e}")

            # Create new web view
            self.web_view = QWebEngineView()
            layout.addWidget(self.web_view)

            # Re-setup web channel - this is crucial!
            if hasattr(self, "web_channel"):
                self.web_view.page().setWebChannel(self.web_channel)
                logger.debug("Web channel re-established for new web view")

            logger.info("Successfully recreated web view")
            return True

        except Exception as e:
            logger.error(f"Failed to recreate web view: {e}")
            return False

    def setupTimers(self):
        """Setup periodic timers for live updates."""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.updateStatus)
        self.status_timer.start(2000)  # Update every 2 seconds

        # Metrics update timer
        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self.updateMetrics)
        self.metrics_timer.start(5000)  # Update every 5 seconds

    def setupPhase3Integration(self):
        """Setup Phase 3: Auto-Generation System integration."""
        try:
            # Connect Phase 3 signals to handlers
            self.auto_generator.panels_generated.connect(self.on_panels_auto_generated)
            self.auto_generator.layout_changed.connect(self.on_layout_auto_changed)

            # Connect auto-generator to web bridge
            self.web_bridge.auto_generator = self.auto_generator

            logger.info("[PHASE3] Auto-Generation System integrated successfully")

        except Exception as e:
            logger.error(f"[ERROR] Phase 3 integration failed: {e}")

    @Slot(str)
    def on_panels_auto_generated(self, panels_data_json: str):
        """Handle auto-generated panels from Phase 3"""
        try:
            panels_data = json.loads(panels_data_json)
            panels = panels_data.get("panels", [])

            # Store auto-generated panels
            for panel_info in panels:
                panel_id = panel_info["id"]
                self.auto_generated_panels[panel_id] = panel_info

            # Update navigation to include auto-generated panels
            self.update_navigation_with_auto_panels(panels)

            # If no current panel is loaded, load the first auto-generated one
            if not self.current_panel and panels:
                first_panel = panels[0]
                self.load_auto_generated_panel(first_panel["id"])

            # Update status
            self.statusBar().showMessage(
                f"[AUTO] Auto-generated {len(panels)} panels from system state"
            )
            logger.info(f"[GENERATE] Loaded {len(panels)} auto-generated panels")

        except Exception as e:
            logger.error(f"[ERROR] Failed to handle auto-generated panels: {e}")

    @Slot(str)
    def on_layout_auto_changed(self, layout_json: str):
        """Handle layout changes from Phase 3"""
        try:
            layout = json.loads(layout_json)
            logger.info(
                f"[LAYOUT] Auto-layout updated: {layout.get('total_panels', 0)} panels in {len(layout.get('sections', []))} sections"
            )

            # Could update UI layout here if needed

        except Exception as e:
            logger.error(f"[ERROR] Failed to handle layout change: {e}")

    def setupPhase4Integration(self):
        """Setup Phase 4: Cognitive UI Integration."""
        try:
            # Connect cognitive monitor to web bridge
            self.web_bridge.cognitive_monitor = self.cognitive_monitor

            # Setup cognitive state monitoring timer
            self.cognitive_timer.timeout.connect(self.update_cognitive_state)
            self.cognitive_timer.start(500)  # Update every 500ms

            # Couple cognitive signals to personality manager (bridge Phase 4 -> Phase 6)
            if hasattr(self, "personality_manager") and self.personality_manager:
                # Cognitive load drives energy/focus, depth maps to analytical mood
                self.cognitive_monitor.cognitive_load_changed.connect(
                    self._on_cognitive_load_changed
                )
                # Thoughts and goals nudge traits subtly
                self.cognitive_monitor.thought_generated.connect(
                    self._on_thought_generated
                )
                self.cognitive_monitor.goal_updated.connect(self._on_goal_updated)

            logger.info("[PHASE4] Cognitive UI Integration setup successfully")

        except Exception as e:
            logger.error(f"[ERROR] Phase 4 integration failed: {e}")

    @Slot(str)
    def _on_cognitive_load_changed(self, cognitive_json: str):
        """Map cognitive metrics to personality state and theme updates."""
        try:
            data = json.loads(cognitive_json)
            load = float(data.get("load", 0.3))
            depth = float(data.get("depth", 0.5))
            freq = float(data.get("frequency", 1.0))

            pm = getattr(self, "personality_manager", None)
            if not pm or not hasattr(pm, "ai"):
                return

            # Clamp helper
            def clamp(v: float) -> float:
                return max(0.0, min(1.0, v))

            # Update levels based on cognitive state
            ps = pm.ai.personality_state
            ps.energy_level = clamp(0.35 + 0.6 * load)
            ps.focus_level = clamp(0.3 + 0.7 * depth)
            ps.creativity_level = clamp(0.4 + 0.15 * min(freq, 4.0))

            # Adjust emotional state heuristically
            try:
                from .phase6_personality import EmotionalState

                if depth > 0.75:
                    ps.emotional_state = EmotionalState.ANALYTICAL
                elif load > 0.85:
                    ps.emotional_state = EmotionalState.EXCITED
                elif load < 0.25 and freq < 1.2:
                    ps.emotional_state = EmotionalState.CALM
                # else: keep current
            except Exception:
                pass

            # Emit updates (will also regenerate theme)
            pm.update_personality_state()

        except Exception as e:
            logger.debug(f"[PHASE4→6] Cognitive load coupling error: {e}")

    @Slot(str)
    def _on_thought_generated(self, thought_json: str):
        """Use thought type to gently influence personality dimensions."""
        try:
            data = json.loads(thought_json)
            thought_type = data.get("thought_type", "")
            pm = getattr(self, "personality_manager", None)
            if not pm or not hasattr(pm, "ai"):
                return
            ps = pm.ai.personality_state

            # Small nudges based on thought type
            if "reasoning" in thought_type:
                ps.focus_level = min(1.0, ps.focus_level + 0.02)
            elif "goal_planning" in thought_type:
                ps.focus_level = min(1.0, ps.focus_level + 0.03)
            elif "memory_recall" in thought_type:
                # contemplative nudge
                try:
                    from .phase6_personality import EmotionalState

                    ps.emotional_state = EmotionalState.CONTEMPLATIVE
                except Exception:
                    pass
            elif "response_generation" in thought_type:
                ps.creativity_level = min(1.0, ps.creativity_level + 0.03)

            pm.update_personality_state()
        except Exception as e:
            logger.debug(f"[PHASE4→6] Thought coupling error: {e}")

    @Slot(str)
    def _on_goal_updated(self, goal_json: str):
        """Map goal status to emotion/energy adjustments."""
        try:
            data = json.loads(goal_json)
            status = data.get("status", "")
            pm = getattr(self, "personality_manager", None)
            if not pm or not hasattr(pm, "ai"):
                return

            ps = pm.ai.personality_state
            try:
                from .phase6_personality import EmotionalState

                if status == "completed":
                    ps.energy_level = min(1.0, ps.energy_level + 0.05)
                    ps.emotional_state = EmotionalState.ENERGETIC
                elif status == "blocked":
                    ps.focus_level = max(0.0, ps.focus_level - 0.05)
                    ps.emotional_state = EmotionalState.ANXIOUS
                elif status == "planning":
                    ps.emotional_state = EmotionalState.CONTEMPLATIVE
            except Exception:
                pass

            pm.update_personality_state()
        except Exception as e:
            logger.debug(f"[PHASE4→6] Goal coupling error: {e}")

    def setupPhase5Integration(self):
        """Setup Phase 5: Plugin-Driven UI System integration."""
        try:
            # Connect plugin UI manager signals
            if self.plugin_ui_manager:
                self.plugin_ui_manager.plugin_ui_loaded.connect(self.onPluginUILoaded)
                self.plugin_ui_manager.plugin_ui_unloaded.connect(
                    self.onPluginUIUnloaded
                )
                self.plugin_ui_manager.plugin_ui_updated.connect(self.onPluginUIUpdated)
                self.plugin_ui_manager.plugin_ui_error.connect(self.onPluginUIError)

                # Start plugin scanning and monitoring
                self.plugin_ui_manager.scan_for_plugins()

                logger.info("[PHASE5] Plugin-Driven UI System setup successfully")

        except Exception as e:
            logger.error(f"[ERROR] Phase 5 integration failed: {e}")

    @Slot(str, str)
    def onPluginUILoaded(self, plugin_id: str, panel_html: str):
        """Handle plugin UI loaded signal"""
        try:
            logger.info(f"[PHASE5] Plugin UI loaded: {plugin_id}")
            # Store plugin panel HTML
            self.plugin_panels[plugin_id] = panel_html

            # Emit signal to web bridge for UI integration
            if hasattr(self.web_bridge, "plugin_ui_loaded"):
                self.web_bridge.plugin_ui_loaded.emit(
                    safe_json_dumps(
                        {
                            "plugin_id": plugin_id,
                            "panel_html": panel_html,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )

        except Exception as e:
            logger.error(f"[PHASE5] Error handling plugin UI loaded: {e}")

    @Slot(str)
    def onPluginUIUnloaded(self, plugin_id: str):
        """Handle plugin UI unloaded signal"""
        try:
            logger.info(f"[PHASE5] Plugin UI unloaded: {plugin_id}")
            if plugin_id in self.plugin_panels:
                del self.plugin_panels[plugin_id]

        except Exception as e:
            logger.error(f"[PHASE5] Error handling plugin UI unloaded: {e}")

    @Slot(str, str)
    def onPluginUIUpdated(self, plugin_id: str, updated_data: str):
        """Handle plugin UI updated signal"""
        try:
            # Forward update to web interface
            if hasattr(self.web_bridge, "plugin_ui_updated"):
                self.web_bridge.plugin_ui_updated.emit(
                    safe_json_dumps(
                        {
                            "plugin_id": plugin_id,
                            "data": updated_data,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )

        except Exception as e:
            logger.error(f"[PHASE5] Error handling plugin UI updated: {e}")

    @Slot(str, str)
    def onPluginUIError(self, plugin_id: str, error_message: str):
        """Handle plugin UI error signal"""
        logger.error(f"[PHASE5] Plugin UI error in {plugin_id}: {error_message}")

    def update_cognitive_state(self):
        """Update cognitive state for Phase 4 visualization."""
        try:
            # Update cognitive monitor with current AI state
            if self.cognitive_monitor:
                # Trigger monitoring update
                self.cognitive_monitor.monitor_cognitive_state()

                # Get cognitive state and emit update
                cognitive_data = self.cognitive_monitor.getCognitiveState()
                if cognitive_data:
                    # Use safe JSON dumps to handle datetime objects
                    cognitive_json = safe_json_dumps(cognitive_data)
                    self.web_bridge.cognitive_updated.emit(cognitive_json)
                    self.web_bridge.data_cache["cognitive"] = cognitive_data

        except Exception as e:
            logger.error(f"[ERROR] Failed to update cognitive state: {e}")

    def get_recent_thoughts(self):
        """Get recent AI thoughts for cognitive visualization."""
        # Placeholder - would integrate with actual AI reasoning system
        return []

    def get_current_goals(self):
        """Get current goals for cognitive visualization."""
        # Placeholder - would integrate with actual goal management system
        return []

    def get_memory_activations(self):
        """Get memory activations for cognitive visualization."""
        # Placeholder - would integrate with actual memory system
        return []

    def update_navigation_with_auto_panels(self, panels: List[Dict[str, Any]]):
        """Update navigation to include auto-generated panels"""
        try:
            # Get the left panel navigation
            left_panel = self.findChild(QWidget, "left_panel")
            if left_panel:
                layout = left_panel.layout()

                # Ensure we have a QVBoxLayout
                if isinstance(layout, QVBoxLayout):
                    # Add separator for auto-generated panels
                    if panels and not hasattr(self, "_auto_panels_separator_added"):
                        separator = QFrame()
                        separator.setFrameShape(QFrame.Shape.HLine)
                        separator.setStyleSheet(
                            "border: 1px solid rgba(0, 255, 136, 0.3); margin: 10px 0;"
                        )
                        layout.insertWidget(
                            layout.count() - 2, separator
                        )  # Before spacer and status

                        auto_label = QLabel("[AUTO] Auto-Generated")
                        auto_label.setStyleSheet("""
                            QLabel {
                                color: #00ff88;
                                font-weight: bold;
                                font-size: 12px;
                                margin: 5px 0;
                            }
                        """)
                        layout.insertWidget(layout.count() - 2, auto_label)
                        self._auto_panels_separator_added = True

                    # Add buttons for auto-generated panels
                    for panel_info in panels[
                        :5
                    ]:  # Limit to 5 auto panels in navigation
                        panel_id = panel_info["id"]
                        panel_title = panel_info.get("title", panel_id)

                        # Check if button already exists
                        existing_btn = self.findChild(
                            QPushButton, f"auto_nav_{panel_id}"
                        )
                        if not existing_btn:
                            btn = QPushButton(f"[AUTO] {panel_title}")
                            btn.setObjectName(f"auto_nav_{panel_id}")
                            btn.clicked.connect(
                                lambda checked,
                                pid=panel_id: self.load_auto_generated_panel(pid)
                            )
                            btn.setStyleSheet(
                                self.getButtonStyle()
                                + """
                                QPushButton {
                                    background: rgba(0, 255, 136, 0.1);
                                    border-left: 3px solid #00ff88;
                                }
                            """
                            )
                            layout.insertWidget(layout.count() - 2, btn)

        except Exception as e:
            logger.warning(f"Failed to update navigation with auto panels: {e}")

    def load_auto_generated_panel(self, panel_id: str):
        """Load an auto-generated panel"""
        try:
            if panel_id in self.auto_generated_panels:
                panel_info = self.auto_generated_panels[panel_id]

                # Get the HTML file path
                panel_file = (
                    Path(__file__).parent
                    / "web_panels"
                    / "auto_generated"
                    / f"{panel_id}.html"
                )

                if panel_file.exists():
                    self.web_view.load(QUrl.fromLocalFile(str(panel_file.absolute())))
                    self.current_panel = panel_id
                    self.statusBar().showMessage(
                        f"🔮 Loaded auto-generated panel: {panel_info.get('title', panel_id)}"
                    )
                else:
                    logger.warning(f"Auto-generated panel file not found: {panel_file}")
            else:
                logger.warning(f"Auto-generated panel not found: {panel_id}")

        except Exception as e:
            logger.error(f"❌ Failed to load auto-generated panel {panel_id}: {e}")

    def setupPhase6Integration(self):
        """Setup Phase 6: Full GUI Personality + State Memory integration."""
        try:
            # Connect personality manager signals
            if self.personality_manager:
                self.personality_manager.personality_changed.connect(
                    self.onPersonalityChanged
                )
                self.personality_manager.theme_updated.connect(self.onThemeUpdated)
                self.personality_manager.layout_adapted.connect(self.onLayoutAdapted)
                self.personality_manager.chat_message.connect(self.onChatMessage)
                self.personality_manager.gui_state_saved.connect(self.onGUIStateSaved)

                # Set up current panel tracking
                if hasattr(self, "current_panel"):
                    self.personality_manager.update_current_panel(
                        self.current_panel or "dashboard"
                    )

                logger.info(
                    "[PHASE6] GUI Personality + State Memory setup successfully"
                )

        except Exception as e:
            logger.error(f"[ERROR] Phase 6 integration failed: {e}")

    @Slot(str)
    def onPersonalityChanged(self, personality_json: str):
        """Handle personality state changes"""
        try:
            personality_data = json.loads(personality_json)
            logger.info(
                f"[PHASE6] Personality changed: {personality_data.get('emotional_state', 'unknown')}"
            )

            # Forward to web interface
            if hasattr(self.web_bridge, "agent_updated"):
                self.web_bridge.agent_updated.emit(
                    safe_json_dumps(
                        {
                            "type": "personality_update",
                            "personality": personality_data,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )

        except Exception as e:
            logger.error(f"[PHASE6] Error handling personality change: {e}")

    @Slot(str)
    def onThemeUpdated(self, theme_css: str):
        """Handle dynamic theme updates"""
        try:
            logger.info("[PHASE6] Theme updated based on personality state")

            # Apply theme to the interface (inject CSS) with object validation
            if (
                hasattr(self, "web_view")
                and self.web_view
                and not self._is_web_view_deleted()
            ):
                # Use style manager for safe CSS injection
                try:
                    from Aetherra.lyrixa.integrations.style_manager import (
                        JavaScriptStyleManager,
                    )

                    style_manager = JavaScriptStyleManager()
                    safe_js = style_manager.create_safe_style_injection(
                        theme_css, "phase6-theme"
                    )
                    self.web_view.page().runJavaScript(safe_js)
                except ImportError:
                    # Fallback to direct injection with improved safety
                    if not self._is_web_view_deleted():
                        # Sanitize CSS and inject safely
                        sanitized_css = theme_css.replace('"', '\\"').replace(
                            "\n", "\\n"
                        )
                        safe_js = f'''
                        (function() {{
                            try {{
                                var style = document.getElementById('phase6-theme');
                                if (!style) {{
                                    style = document.createElement('style');
                                    style.id = 'phase6-theme';
                                    document.head.appendChild(style);
                                }}
                                style.textContent = "{sanitized_css}";
                            }} catch(e) {{
                                console.log('Theme injection failed:', e);
                            }}
                        }})();
                        '''
                        self.web_view.page().runJavaScript(safe_js)

        except Exception as e:
            logger.error(f"[PHASE6] Error handling theme update: {e}")

    def cleanupConsciousnessPanel(self):
        """Clean up consciousness panel to prepare for switching to web panels."""
        try:
            if (
                hasattr(self, "consciousness_widget")
                and self.consciousness_widget is not None
            ):
                # Get reference before removing
                widget = self.consciousness_widget

                # Hide the consciousness widget
                widget.hide()

                # Remove from layout if it's in there
                center_layout = self.center_panel.layout()
                if center_layout and center_layout.indexOf(widget) != -1:
                    center_layout.removeWidget(widget)

                # Clean up the widget
                widget.deleteLater()
                self.consciousness_widget = None

                logger.debug("Consciousness panel cleaned up successfully")

        except Exception as e:
            logger.error(f"Error cleaning up consciousness panel: {e}")

    def _is_web_view_deleted(self):
        """Check if web view object has been deleted"""
        try:
            if not hasattr(self, "web_view"):
                logger.debug("No web_view attribute found")
                return True
            if not self.web_view:
                logger.debug("web_view is None")
                return True
            # Try to access a simple property to check if object is still valid
            # Use a more reliable check than objectName()
            try:
                _ = self.web_view.isVisible()  # This should work if object is valid
                return False
            except RuntimeError as re:
                logger.debug(f"RuntimeError accessing web_view: {re}")
                return True
        except Exception as e:
            logger.debug(f"Exception in _is_web_view_deleted: {e}")
            return True

    @Slot(str)
    def onLayoutAdapted(self, layout_json: str):
        """Handle layout adaptations based on AI state"""
        try:
            layout_data = json.loads(layout_json)
            logger.info(f"[PHASE6] Layout adapted: {layout_data}")

        except Exception as e:
            logger.error(f"[PHASE6] Error handling layout adaptation: {e}")

    @Slot(str)
    def onChatMessage(self, message_json: str):
        """Handle chat messages with real conversation manager"""
        try:
            message_data = json.loads(message_json)
            user_message = message_data.get("message", "")

            if (
                user_message
                and hasattr(self, "conversation_manager")
                and self.conversation_manager
            ):
                # Process message through real conversation manager
                try:
                    # Generate response using real AI conversation system
                    response = self.conversation_manager.generate_response_sync(
                        user_message
                    )

                    # Send response back to chat interface
                    if (
                        hasattr(self.personality_manager, "chat_interface")
                        and self.personality_manager.chat_interface
                    ):
                        self.personality_manager.chat_interface.responseReady.emit(
                            response
                        )

                    logger.info(
                        f"[PHASE6] Real chat response generated: {len(response)} chars"
                    )

                except Exception as conv_error:
                    logger.error(f"[PHASE6] Conversation manager error: {conv_error}")
                    # Fallback response
                    fallback_response = f"I understand you said: '{user_message}'. I'm currently experiencing some technical difficulties but I'm working on it!"
                    if (
                        hasattr(self.personality_manager, "chat_interface")
                        and self.personality_manager.chat_interface
                    ):
                        self.personality_manager.chat_interface.responseReady.emit(
                            fallback_response
                        )
            else:
                logger.warning("[PHASE6] No conversation manager available for chat")

        except Exception as e:
            logger.error(f"[PHASE6] Error handling chat message: {e}")

    @Slot(str)
    def onGUIStateSaved(self, state_json: str):
        """Handle GUI state saving"""
        try:
            state_data = json.loads(state_json)
            logger.info(
                f"[PHASE6] GUI state saved for panel: {state_data.get('current_panel', 'unknown')}"
            )

        except Exception as e:
            logger.error(f"[PHASE6] Error handling GUI state save: {e}")

    def loadPanel(self, panel_id: str):
        """Enhanced loadPanel with Phase 6 personality integration"""
        try:
            logger.debug(f"Attempting to load panel: {panel_id}")

            # Check if web view exists - be more permissive
            if not hasattr(self, "web_view"):
                logger.error(f"❌ Cannot load panel {panel_id}: No web_view attribute")
                return

            if not self.web_view:
                logger.error(f"❌ Cannot load panel {panel_id}: web_view is None")
                return

            # Only do the deletion check if absolutely necessary
            web_view_deleted = self._is_web_view_deleted()
            logger.debug(f"Web view deleted check result: {web_view_deleted}")

            if web_view_deleted:
                logger.warning(
                    f"⚠️ Web view deleted for panel {panel_id}, attempting recreation..."
                )
                if self._recreateWebView():
                    logger.info(
                        f"✅ Web view successfully recreated for panel {panel_id}"
                    )
                else:
                    logger.error(
                        f"❌ Cannot load panel {panel_id}: Failed to recreate web view"
                    )
                    return

            # Track panel change with personality manager
            if hasattr(self, "personality_manager") and self.personality_manager:
                self.personality_manager.update_current_panel(panel_id)

            # Handle Phase 6 chat panel
            if panel_id == "chat":
                panel_file = Path(__file__).parent / "web_panels" / "phase6_chat.html"
                if panel_file.exists():
                    self.web_view.load(QUrl.fromLocalFile(str(panel_file.absolute())))
                    self.current_panel = panel_id
                    self.statusBar().showMessage(
                        "💬 Chat with Lyrixa - AI conversation interface"
                    )
                    return
                else:
                    logger.warning(f"Chat panel file not found: {panel_file}")

            # Handle consciousness panel
            if panel_id == "consciousness":
                self.loadConsciousnessPanel()
                return

            # Special handling for Phase 5 plugin demo
            if panel_id == "plugin_demo":
                panel_path = (
                    Path(__file__).parent / "web_panels" / "phase5_plugin_demo.html"
                )
            else:
                panel_path = (
                    Path(__file__).parent / "web_panels" / f"{panel_id}_panel.html"
                )

            if not panel_path.exists():
                # Create default panel if it doesn't exist
                self.createDefaultPanel(panel_id, panel_path)

            # Clean up consciousness panel if switching from it
            self.cleanupConsciousnessPanel()

            # Ensure web view is visible
            if (
                hasattr(self, "web_view")
                and self.web_view
                and not self.web_view.isVisible()
            ):
                self.web_view.show()

            # Load the panel
            logger.debug(f"Loading panel from: {panel_path}")
            self.web_view.load(QUrl.fromLocalFile(str(panel_path.absolute())))
            self.current_panel = panel_id
            self.statusBar().showMessage(f"🌟 Loaded {panel_id.title()} Panel")
            logger.info(f"[CHECK] Successfully loaded panel: {panel_id}")

        except Exception as e:
            logger.error(f"❌ Error loading panel {panel_id}: {e}")
            import traceback

            logger.debug(f"Full traceback: {traceback.format_exc()}")

    def loadConsciousnessPanel(self):
        """Load the consciousness integration panel."""
        try:
            logger.debug("Attempting to load consciousness panel")

            # Try to import consciousness panel
            try:
                from .consciousness_panel import create_consciousness_panel

                logger.debug("Successfully imported consciousness_panel")
            except ImportError as e:
                logger.warning(f"Could not import consciousness_panel: {e}")
                # Fallback to web-based panel
                self.loadWebConsciousnessPanel()
                return

            # Create consciousness panel with current integrator
            try:
                consciousness_panel = create_consciousness_panel(
                    self.consciousness_integrator, self
                )
                logger.debug("Successfully created consciousness panel")
            except Exception as e:
                logger.warning(f"Failed to create consciousness panel: {e}")
                # Fallback to web-based panel
                self.loadWebConsciousnessPanel()
                return

            # Instead of replacing layout, hide web view and add consciousness panel
            if hasattr(self, "center_panel") and self.center_panel:
                layout = self.center_panel.layout()
                if layout and hasattr(self, "web_view") and self.web_view:
                    # Hide the web view but keep it in the layout
                    self.web_view.hide()

                    # Clean up any existing consciousness widget
                    self.cleanupConsciousnessPanel()

                    # Add consciousness panel to existing layout
                    self.consciousness_widget = consciousness_panel
                    layout.addWidget(consciousness_panel)

                    self.current_panel = "consciousness"
                    self.statusBar().showMessage(
                        "⚛️ Consciousness Interface - Phase 1-5 Integration"
                    )

                    logger.info("[CHECK] Consciousness panel loaded successfully")
                else:
                    logger.error(
                        "Cannot load consciousness panel: No valid center panel layout"
                    )
            else:
                logger.error("❌ Center panel not found")
                # Fallback to web-based panel
                self.loadWebConsciousnessPanel()

        except Exception as e:
            logger.error(f"❌ Failed to load consciousness panel: {e}")
            import traceback

            logger.debug(f"Full traceback: {traceback.format_exc()}")
            # Fallback to web-based panel
            self.loadWebConsciousnessPanel()

    def loadWebConsciousnessPanel(self):
        """Fallback: Load web-based consciousness panel."""
        try:
            logger.debug("Loading web-based consciousness panel as fallback")

            # Check if web view is available - more permissive than before
            if not hasattr(self, "web_view") or not self.web_view:
                logger.warning(
                    "⚠️ Web view not available for consciousness panel, attempting recreation..."
                )
                if self._recreateWebView():
                    logger.info(
                        "✅ Web view successfully recreated for consciousness panel"
                    )
                else:
                    logger.error(
                        "❌ Cannot load web consciousness panel: Failed to recreate web view"
                    )
                    return

            # Check if recreated web view is still deleted
            if self._is_web_view_deleted():
                logger.warning(
                    "⚠️ Web view still deleted after recreation attempt, trying once more..."
                )
                if self._recreateWebView():
                    logger.info("✅ Web view successfully recreated on second attempt")
                else:
                    logger.error(
                        "❌ Cannot load web consciousness panel: Web view recreation failed"
                    )
                    return

            panel_path = (
                Path(__file__).parent / "web_panels" / "consciousness_panel.html"
            )

            if not panel_path.exists():
                logger.debug("Creating consciousness web panel HTML file")
                self.createConsciousnessWebPanel(panel_path)

            # Try to load the panel
            logger.debug(f"Loading web consciousness panel from: {panel_path}")
            self.web_view.load(QUrl.fromLocalFile(str(panel_path.absolute())))
            self.current_panel = "consciousness"
            self.statusBar().showMessage("⚛️ Consciousness Interface (Web Mode)")
            logger.info("[CHECK] Web consciousness panel loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load web consciousness panel: {e}")
            import traceback

            logger.debug(f"Full traceback: {traceback.format_exc()}")

    def createConsciousnessWebPanel(self, path: Path):
        """Create a basic consciousness web panel."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Consciousness Interface</title>
            <style>
                body {
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                    color: #e0e0e0;
                    font-family: 'Segoe UI', sans-serif;
                    margin: 0;
                    padding: 20px;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .header h1 {
                    color: #00d4ff;
                    font-size: 2.5em;
                    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
                }
                .status {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(0, 212, 255, 0.3);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚛️ Consciousness Interface</h1>
                <p>Phase 1-5 Integration</p>
            </div>
            <div class="status">
                <h3>System Status</h3>
                <p>Consciousness integration is being initialized...</p>
                <p>Please wait for backend connection.</p>
            </div>
        </body>
        </html>
        """

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html_content, encoding="utf-8")
            logger.debug(f"Created consciousness web panel at: {path}")
        except Exception as e:
            logger.error(f"❌ Failed to create consciousness web panel: {e}")

    def createDefaultPanel(self, panel_id: str, path: Path):
        """Create a default panel if it doesn't exist."""
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{panel_id.title()} Panel</title>
            <link rel="stylesheet" href="../assets/style.css">
        </head>
        <body>
            <div class="panel-container" data-panel="{panel_id}">
                <div class="panel-header">
                    <h1>🎙️ {panel_id.title()} Panel</h1>
                </div>
                <div class="panel-content">
                    <div class="placeholder">
                        <div class="glow-orb"></div>
                        <p>Panel coming in Phase 2...</p>
                    </div>
                </div>
            </div>
            <script src="../assets/effects.js"></script>
        </body>
        </html>
        '''

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html_content, encoding="utf-8")

    def applyAetherraTheme(self):
        """Apply the Aetherra color scheme and styling."""
        self.setStyleSheet("""
            QMainWindow {
                background: #0a0a0a;
                color: #ffffff;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }

            QFrame {
                background: rgba(26, 26, 26, 0.8);
                border-radius: 8px;
            }

            QMenuBar {
                background: #1a1a1a;
                color: #ffffff;
                border-bottom: 1px solid rgba(0, 255, 136, 0.3);
            }

            QMenuBar::item {
                background: transparent;
                padding: 8px 16px;
            }

            QMenuBar::item:selected {
                background: rgba(0, 255, 136, 0.2);
                border-radius: 4px;
            }
        """)

    def getButtonStyle(self) -> str:
        """Get the Aetherra-themed button style."""
        return """
            QPushButton {
                background: rgba(26, 26, 26, 0.8);
                color: #ffffff;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: bold;
                margin: 4px 0;
                text-align: left;
            }

            QPushButton:hover {
                background: rgba(0, 255, 136, 0.1);
                border-color: rgba(0, 255, 136, 0.6);
                /* box-shadow removed for Qt compatibility */
            }

            QPushButton:pressed {
                background: rgba(0, 255, 136, 0.2);
            }
        """

    def updateStatus(self):
        """Update system status display."""
        # This will be connected to real backend data in later phases
        if self.service_registry:
            self.status_label.setText("🌟 All Systems Online")
        else:
            self.status_label.setText("[WARN] Connecting...")

    def updateMetrics(self):
        """Update metrics display."""
        # This will be connected to real backend metrics in later phases
        import random

        # Simulate live metrics for now
        metrics_data = {
            "memory_load": random.randint(30, 70),
            "cpu_usage": random.randint(10, 40),
            "agents_active": random.randint(5, 12),
            "plugins_loaded": 12,
        }

        # Update web bridge data
        self.web_bridge.data_cache["metrics"] = metrics_data
        self.web_bridge.metrics_updated.emit(json.dumps(metrics_data))

    # Backend connection methods (called by launcher)
    def set_service_registry(self, service_registry):
        """Connect service registry."""
        self.service_registry = service_registry
        self._update_backend_services()

    def set_plugin_manager(self, plugin_manager):
        """Connect plugin manager."""
        self.plugin_manager = plugin_manager
        self._update_backend_services()

    def set_lyrixa_engine(self, lyrixa_engine):
        """Connect Lyrixa engine."""
        self.lyrixa_engine = lyrixa_engine
        self._update_backend_services()

    def set_memory_system(self, memory_system):
        """Connect memory system."""
        self.memory_system = memory_system
        self._update_backend_services()

    def set_agent_orchestrator(self, agent_orchestrator):
        """Connect agent orchestrator."""
        self.agent_orchestrator = agent_orchestrator
        self._update_backend_services()

    def set_consciousness_integrator(self, consciousness_integrator):
        """Connect consciousness integrator."""
        self.consciousness_integrator = consciousness_integrator
        self._update_backend_services()
        logger.info("✅ Consciousness integrator connected to GUI")

    def _update_backend_services(self):
        """Update the context bridge with current backend services."""
        services = {}

        if hasattr(self, "service_registry") and self.service_registry:
            services["service_registry"] = self.service_registry

        if hasattr(self, "plugin_manager") and self.plugin_manager:
            services["plugin_manager"] = self.plugin_manager

        if hasattr(self, "lyrixa_engine") and self.lyrixa_engine:
            services["lyrixa_engine"] = self.lyrixa_engine

        if hasattr(self, "memory_system") and self.memory_system:
            services["memory_system"] = self.memory_system

        if hasattr(self, "agent_orchestrator") and self.agent_orchestrator:
            services["agent_orchestrator"] = self.agent_orchestrator

        if hasattr(self, "consciousness_integrator") and self.consciousness_integrator:
            services["consciousness_integrator"] = self.consciousness_integrator

        # Connect services to the context bridge
        self.web_bridge.connect_backend_services(services)

        # Connect real conversation manager for the main window too
        try:
            import Aetherra.aetherra_core.agents.conversation_manager as cm

            workspace_path = os.path.join(os.path.dirname(__file__), "..", "..", "..")
            manager_cls = getattr(cm, "LyrixaConversationManager", None)
            if manager_cls:
                self.conversation_manager = manager_cls(
                    workspace_path=workspace_path, gui_interface=self
                )
                logger.info("✅ LyrixaHybridWindow conversation manager connected")
            else:
                raise ImportError("LyrixaConversationManager not found")
        except Exception as e:
            logger.warning(
                f"❌ Failed to connect conversation manager to main window: {e}"
            )
            self.conversation_manager = None

        # Phase 3: Connect auto-generator to backend services and start introspection
        if services and hasattr(self, "auto_generator"):
            self.auto_generator.connect_backend_services(services)
            # Start auto-generation after a short delay to allow services to settle
            QTimer.singleShot(1000, self.auto_generator.start_auto_generation)


def main():
    """Standalone launcher for testing."""
    app = QApplication(sys.argv)
    app.setApplicationName("Lyrixa Hybrid UI")

    window = LyrixaHybridWindow()
    window.show()

    sys.exit(app.exec())


# Export MainWindow as alias for LyrixaHybridWindow for external imports
MainWindow = LyrixaHybridWindow

# Export classes for external use
__all__ = ["LyrixaHybridWindow", "MainWindow"]


if __name__ == "__main__":
    main()
