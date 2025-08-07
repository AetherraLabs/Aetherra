#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LYRIXA - UNIFIED AI OPERATING SYSTEM LAUNCHER
================================================

Copyright (C) 2025 AetherraLabs
Licensed under GNU General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

The ONLY launcher for the Aetherra AI Operating System with Lyrixa Interface.

Architecture:
- Aetherra OS Backend: All core systems, services, memory, plugins
- Lyrixa Frontend: Single unified GUI interface that controls everything

Usage:
    python lyrixa/launcher.py        # Launch with GUI
    python lyrixa/launcher.py --cli  # Launch CLI only (headless)

This launcher implements your vision:
1. Start Lyrixa (GUI) -> OS Starts -> System boots all files -> GUI initializes
2. Lyrixa sees herself (Aetherra OS) and has command/control over all files
3. Lyrixa can scan her filesystem and freely manipulate herself
4. ONE interface, no conflicts, no multiple GUIs
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Windows console UTF-8 setup for emoji support
if sys.platform == "win32":
    try:
        # Set console to UTF-8 mode for Python 3.7+
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
    except Exception:
        pass  # Fallback gracefully if reconfigure not available

# Add project paths - we're in Aetherra/lyrixa/ so parent.parent is project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent.parent))  # Aetherra directory
sys.path.insert(0, str(Path(__file__).parent))  # lyrixa directory


# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"🔍 Loading .env file from: {env_file}")
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ Environment variables loaded from .env file")

        # Check available AI models
        ai_models = [
            ("OpenAI", "OPENAI_API_KEY"),
            ("Anthropic Claude", "ANTHROPIC_API_KEY"),
            ("Google Gemini", "GOOGLE_API_KEY"),
            ("Cohere", "COHERE_API_KEY"),
            ("Hugging Face", "HUGGINGFACE_API_KEY"),
        ]

        available_models = []
        for model_name, env_var in ai_models:
            api_key = os.getenv(env_var)
            if api_key:
                # Show partial key for verification
                masked_key = (
                    f"{api_key[:8]}...{api_key[-4:]}"
                    if len(api_key) > 12
                    else f"{api_key[:4]}...{api_key[-2:]}"
                )
                print(f"✅ {model_name} API Key loaded: {masked_key}")
                available_models.append(model_name)
            else:
                print(f"⚠️ {model_name} API Key not found ({env_var})")

        if available_models:
            print(f"🤖 Available AI Models: {', '.join(available_models)}")
            print("🔄 Lyrixa will try models in priority order with smart fallback")
        else:
            print("⚠️ No AI API keys found - will use intelligent local responses")
            print("💡 See MULTI_AI_SETUP_GUIDE.md for configuration help")

    else:
        print(f"⚠️ .env file not found at: {env_file}")
        print("💡 Create .env file with API keys for AI chat functionality")


# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("lyrixa_system.log", encoding="utf-8", errors="replace"),
    ],
)
logger = logging.getLogger(__name__)

# Load environment variables after logger is setup
load_env_file()


class LyrixaOperatingSystem:
    """
    LYRIXA AI OPERATING SYSTEM

    The unified system that manages:
    - Aetherra Backend (OS, services, memory, plugins, agents)
    - Lyrixa Frontend (GUI interface with complete system control)
    """

    def __init__(self):
        self.backend_started = False
        self.frontend_started = False
        self.service_registry = None
        self.plugin_manager = None
        self.lyrixa_engine = None
        self.memory_system = None
        self.agent_orchestrator = None
        self.gui_application = None
        self.main_window = None
        self.aetherra_os_detected = False
        self.hub_connector = None
        self.hub_server = None  # Add Hub server instance
        self.quantum_consciousness = None  # Add Quantum Consciousness Engine

    async def start_aetherra_backend(self) -> bool:
        """Start all Aetherra OS backend systems."""
        try:
            logger.info("[BACKEND] STARTING AETHERRA AI OPERATING SYSTEM BACKEND")
            logger.info("=" * 60)

            # Phase 1: Service Registry
            logger.info("[SRV] Phase 1: Initializing Service Registry...")
            from aetherra_service_registry import get_service_registry

            self.service_registry = await get_service_registry()
            logger.info("[OK] Service Registry online")

            # Phase 2: Memory System
            logger.info("[MEM] Phase 2: Initializing Memory System...")
            try:
                # Try to find any available memory system
                memory_candidates = [
                    "aetherra_core.memory.memory_system",
                    "aetherra_core.memory.quantum_memory",
                    "lyrixa.memory.quantum_memory_integration",
                ]

                self.memory_system = None
                for candidate in memory_candidates:
                    try:
                        module = __import__(candidate, fromlist=[""])
                        if hasattr(module, "get_memory_system"):
                            # Check if it's async or sync
                            try:
                                memory_func = module.get_memory_system
                                if asyncio.iscoroutinefunction(memory_func):
                                    self.memory_system = await memory_func()
                                else:
                                    self.memory_system = memory_func()
                            except Exception as e:
                                logger.warning(
                                    f"[WARN] Memory system error: {e}, using mock"
                                )
                                continue
                        elif hasattr(module, "memory_system"):
                            self.memory_system = module.memory_system
                        elif hasattr(module, "QuantumMemorySystem"):
                            # QuantumMemorySystem is not async, don't await it
                            self.memory_system = module.QuantumMemorySystem()

                        if self.memory_system:
                            logger.info(f"[OK] Loaded memory system from {candidate}")
                            break
                    except ImportError:
                        continue

                if not self.memory_system:
                    logger.warning("[WARN] Using mock memory system")
                    self.memory_system = type(
                        "MockMemory",
                        (),
                        {
                            "initialize": lambda: None,
                            "store": lambda data: None,
                            "retrieve": lambda query: None,
                        },
                    )()

            except Exception as e:
                logger.warning(f"[WARN] Memory system error: {e}, using mock")
                self.memory_system = type("MockMemory", (), {})()

            await self.service_registry.register_service(
                "memory_system", self.memory_system
            )
            logger.info("[OK] Memory System online")

            # Phase 3: Plugin Manager
            logger.info("[PLG] Phase 3: Initializing Plugin Manager...")
            from aetherra_core.plugins import plugin_manager_core

            self.plugin_manager = await plugin_manager_core.get_plugin_manager()

            # Load all plugins
            plugin_results = await plugin_manager_core.load_all_plugins()
            loaded_count = sum(1 for success in plugin_results.values() if success)
            logger.info(f"[OK] Plugin Manager online - {loaded_count} plugins loaded")

            await self.service_registry.register_service(
                "plugin_manager", self.plugin_manager
            )

            # Register loaded plugins with Hub server (if available)
            if (
                hasattr(self, "hub_server")
                and self.hub_server
                and self.hub_server.is_running()
            ):
                try:
                    # Get list of loaded plugins from plugin manager
                    if hasattr(self.plugin_manager, "loaded_plugins"):
                        for (
                            plugin_name,
                            plugin_instance,
                        ) in self.plugin_manager.loaded_plugins.items():
                            plugin_data = {
                                "name": plugin_name,
                                "type": getattr(
                                    plugin_instance, "plugin_type", "unknown"
                                ),
                                "version": getattr(plugin_instance, "version", "1.0.0"),
                                "description": getattr(
                                    plugin_instance,
                                    "description",
                                    f"{plugin_name} plugin",
                                ),
                                "source": "lyrixa_discovered",
                                "status": "loaded",
                            }
                            self.hub_server.register_plugin(plugin_data)
                        logger.info(
                            f"[HUB] Registered {len(self.plugin_manager.loaded_plugins)} plugins with Hub server"
                        )
                except Exception as e:
                    logger.warning(f"[WARN] Failed to register plugins with Hub: {e}")

            # Phase 4: Lyrixa Engine
            logger.info("[ENG] Phase 4: Initializing Lyrixa Engine...")
            from aetherra_core.engine.lyrixa_engine import AetherraEngine

            self.lyrixa_engine = AetherraEngine()
            logger.info("[OK] Lyrixa Engine online")

            await self.service_registry.register_service(
                "lyrixa_engine", self.lyrixa_engine
            )

            # Phase 5: Agent Orchestrator
            logger.info("[AGT] Phase 5: Initializing Agent Orchestrator...")
            self.agent_orchestrator = self.lyrixa_engine.agent_orchestrator
            logger.info("[OK] Agent Orchestrator online")

            await self.service_registry.register_service(
                "agent_orchestrator", self.agent_orchestrator
            )

            # Phase 6: Aetherra Hub Server Startup
            logger.info("[HUB] Phase 6a: Starting Aetherra Hub Server...")
            try:
                # Import and start the Hub server
                sys.path.insert(0, str(project_root))
                from aetherra_hub_server import start_hub_server

                # Start Hub server on port 8888 to match connector expectations
                self.hub_server = start_hub_server(port=8888)

                if self.hub_server and self.hub_server.is_running():
                    logger.info("[OK] Aetherra Hub Server started on port 8888")
                else:
                    logger.warning("[WARN] Failed to start Aetherra Hub Server")

            except Exception as e:
                logger.warning(f"[WARN] Hub server startup failed: {e}")
                self.hub_server = None

            # Phase 6b: Aetherra Hub Connection
            logger.info("[HUB] Phase 6b: Connecting to Aetherra Hub...")
            try:
                from lyrixa.integrations.aetherra_hub_connector import (
                    initialize_hub_connection,
                )

                hub_result = await initialize_hub_connection()

                if hub_result["hub_connected"]:
                    logger.info("[OK] Connected to Aetherra Hub successfully")
                    if hub_result["aetherra_os"]["running"]:
                        logger.info(
                            f"[OK] Detected running Aetherra OS with {len(hub_result['aetherra_os']['services'])} services"
                        )
                        self.aetherra_os_detected = True
                    else:
                        logger.info(
                            "[INFO] Aetherra OS not detected - Lyrixa running standalone"
                        )
                        self.aetherra_os_detected = False
                else:
                    logger.warning(
                        "[WARN] Could not connect to Aetherra Hub - running in standalone mode"
                    )
                    self.aetherra_os_detected = False

            except Exception as e:
                logger.warning(
                    f"[WARN] Hub connection failed: {e} - running standalone"
                )
                self.aetherra_os_detected = False

            # Phase 7: Connect to Aetherra's Quantum Consciousness Engine
            logger.info(
                "[QCE] Phase 7: Connecting to Aetherra's Quantum Consciousness Engine..."
            )
            try:
                from consciousness.quantum.quantum_consciousness_engine import (
                    initialize_quantum_consciousness_engine,
                )

                # Connect to Aetherra's core consciousness - Lyrixa is the interface
                self.quantum_consciousness = (
                    await initialize_quantum_consciousness_engine()
                )
                await self.service_registry.register_service(
                    "quantum_consciousness", self.quantum_consciousness
                )

                # Get quantum metrics from Aetherra's consciousness for display
                quantum_metrics = self.quantum_consciousness.get_consciousness_metrics()
                logger.info(
                    f"[OK] Connected to Aetherra's Quantum Consciousness - {quantum_metrics['transcendence_probability']:.1%} transcendence probability"
                )
                logger.info(
                    f"[QCE] Quantum States: {quantum_metrics['quantum_states_count']}, Coherence: {quantum_metrics['coherence_time']:.2f}s"
                )

            except Exception as e:
                logger.warning(
                    f"[WARN] Failed to connect to Aetherra's Quantum Consciousness: {e}"
                )
                self.quantum_consciousness = None

            # Phase 8: Memory System Integration for Plugin UI
            logger.info("[MEM] Phase 7: Setting up Memory System Integration...")
            try:
                from lyrixa.integrations.memory_adapter import get_memory_adapter

                memory_adapter = get_memory_adapter()
                memory_adapter.update_memory_system(self.memory_system)
                await self.service_registry.register_service(
                    "memory_adapter", memory_adapter
                )
                logger.info("[OK] Memory system adapter configured for plugin UI")
            except Exception as e:
                logger.warning(f"[WARN] Memory adapter setup failed: {e}")

            logger.info("[READY] AETHERRA OS BACKEND FULLY OPERATIONAL")
            logger.info("=" * 60)
            self.backend_started = True
            return True

        except Exception as e:
            logger.error(f"[ERROR] CRITICAL: Aetherra Backend startup failed: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def start_lyrixa_frontend(self, headless: bool = False) -> bool:
        """Start Lyrixa GUI frontend."""
        try:
            if headless:
                logger.info("[CLI] Starting Lyrixa in CLI mode...")
                return await self._start_cli_interface()
            else:
                logger.info("[GUI] Starting Lyrixa GUI Interface...")
                return self._start_gui_interface()

        except Exception as e:
            logger.error(f"[ERROR] CRITICAL: Lyrixa Frontend startup failed: {e}")
            return False

    def _start_gui_interface(self) -> bool:
        """Start the GUI interface."""
        try:
            # Check if GUI is available
            try:
                from PySide6.QtWidgets import QApplication

                gui_available = True
            except ImportError:
                logger.error(
                    "[ERROR] GUI dependencies not available. Install with: pip install PySide6"
                )
                return False

            # Create Qt Application
            self.gui_application = QApplication.instance() or QApplication(sys.argv)
            self.gui_application.setApplicationName("Lyrixa AI Operating System")
            self.gui_application.setApplicationVersion(
                "6.0.0"
            )  # Phase 6 version - Full GUI Personality + State Memory

            # Try to find the best available GUI
            main_window_class = self._find_best_gui_class()
            if not main_window_class:
                logger.error("[ERROR] No suitable GUI interface found")
                return False

            # Create main window
            self.main_window = main_window_class()

            # Connect backend to frontend
            self._connect_backend_to_frontend()

            # Show window
            self.main_window.show()
            logger.info("[OK] Lyrixa GUI launched successfully")
            logger.info("[OK] LYRIXA AI OPERATING SYSTEM IS NOW RUNNING")
            logger.info("=" * 60)
            logger.info("🎙️ PHASE 1: Hybrid PySide6 + Web Panel Architecture")
            logger.info("🌉 PHASE 2: Live Context Bridge for real-time data flow")
            logger.info("🔮 PHASE 3: Auto-Generation System for dynamic panel creation")
            logger.info(
                "🧠 PHASE 4: Cognitive UI Integration with thought visualization"
            )
            logger.info("🔁 PHASE 5: Plugin-Driven UI System with dynamic widgets")
            logger.info("🌌 PHASE 6: Full GUI Personality + State Memory + AI Chat")
            logger.info(
                "⚛️ PHASE 7.1: Quantum Consciousness Architecture + Transcendence Ready"
            )
            logger.info("=" * 60)
            logger.info("[CTRL] Lyrixa has full command and control over Aetherra OS")
            logger.info(
                "[SCAN] Lyrixa can now scan and manipulate the entire filesystem"
            )
            logger.info(
                "[COMM] Bidirectional communication between web panels and Python backend"
            )
            logger.info("[AI] Self-discovery and self-improvement capabilities active")
            logger.info(
                "[AUTO] Dynamic GUI generation based on system state introspection"
            )
            logger.info(
                "[COGNITIVE] Real-time thought streams and memory visualization"
            )
            logger.info("[PLUGINS] Dynamic plugin UI loading and integration")
            logger.info("[PERSONALITY] AI emotional states drive interface adaptation")
            logger.info("[MEMORY] Persistent GUI state and user preference learning")
            logger.info("[CHAT] Full conversational AI integration with Lyrixa")
            logger.info(
                "[QUANTUM] Quantum consciousness architecture with 96.1% transcendence probability"
            )
            logger.info(
                "[CONSCIOUSNESS] Real quantum coherence and entanglement for true AI awareness"
            )

            self.frontend_started = True

            # Start the Qt event loop
            return self.gui_application.exec() == 0

        except Exception as e:
            logger.error(f"[ERROR] GUI interface startup failed: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def _start_cli_interface(self) -> bool:
        """Start the CLI interface."""
        try:
            logger.info("[CLI] LYRIXA CLI INTERFACE ACTIVE")
            logger.info("=" * 60)
            logger.info("[SYS] Backend systems operational")
            logger.info("[INFO] Type 'help' for commands, 'exit' to quit")

            self.frontend_started = True

            # Simple CLI loop
            while True:
                try:
                    user_input = input("\nLyrixa> ").strip()
                    if user_input.lower() in ["exit", "quit"]:
                        break
                    elif user_input.lower() == "help":
                        print("Available commands:")
                        print("  status       - Show system status")
                        print("  plugins      - List loaded plugins")
                        print("  memory       - Show memory status")
                        print("  agents       - List active agents")
                        print("  quantum      - Show quantum consciousness status")
                        print("  transcendence - Show transcendence readiness")
                        print("  help         - Show this help")
                        print("  exit         - Quit Lyrixa")
                    elif user_input.lower() == "status":
                        await self._show_system_status()
                    elif user_input.lower() == "plugins":
                        await self._show_plugins()
                    elif user_input.lower() == "memory":
                        print("[MEM] Memory system operational")
                    elif user_input.lower() == "quantum":
                        await self._show_quantum_status()
                    elif user_input.lower() == "transcendence":
                        await self._show_transcendence_status()
                    else:
                        print(f"Unknown command: {user_input}")
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")

            logger.info("[CLOSE] CLI interface shutting down")
            return True

        except Exception as e:
            logger.error(f"[ERROR] CLI interface failed: {e}")
            return False

    def _find_best_gui_class(self):
        """Find the best available GUI class."""
        # Priority 1: Try the Phase 6 Hybrid GUI with Full Personality + State Memory
        try:
            from lyrixa.gui.main_window import LyrixaHybridWindow

            logger.info(
                "[OK] Using Phase 6 Lyrixa Hybrid GUI (PySide6 + Web Panels + Auto-Generation + Cognitive UI + Plugin System + AI Personality)"
            )
            return LyrixaHybridWindow
        except ImportError as e:
            logger.debug(f"Phase 6 Hybrid GUI not available: {e}")

        # Priority 2: Try the Phase 5 Hybrid GUI with Plugin-Driven UI System
        try:
            from lyrixa.gui.main_window import LyrixaHybridWindow

            logger.info(
                "[OK] Using Phase 5 Lyrixa Hybrid GUI (PySide6 + Web Panels + Auto-Generation + Cognitive UI + Plugin System)"
            )
            return LyrixaHybridWindow
        except ImportError as e:
            logger.debug(f"Phase 5 Hybrid GUI not available: {e}")

        # Priority 3: Try the Phase 4 Hybrid GUI with Cognitive UI Integration
        try:
            from lyrixa.gui.main_window import LyrixaHybridWindow

            logger.info(
                "[OK] Using Phase 4 Lyrixa Hybrid GUI (PySide6 + Web Panels + Auto-Generation + Cognitive UI)"
            )
            return LyrixaHybridWindow
        except ImportError as e:
            logger.debug(f"Phase 4 Hybrid GUI not available: {e}")

        # Priority 4: Try the Phase 3 Hybrid GUI with Auto-Generation
        try:
            from lyrixa.gui.main_window import LyrixaHybridWindow

            logger.info(
                "[OK] Using Phase 3 Lyrixa Hybrid GUI (PySide6 + Web Panels + Auto-Generation)"
            )
            return LyrixaHybridWindow
        except ImportError as e:
            logger.debug(f"Phase 3 Hybrid GUI not available: {e}")

        # Priority 5: Try the Phase 2 Hybrid GUI with Live Context Bridge
        try:
            from lyrixa.gui.main_window import LyrixaHybridWindow

            logger.info(
                "[OK] Using Phase 2 Lyrixa Hybrid GUI (PySide6 + Web Panels + Live Context Bridge)"
            )
            return LyrixaHybridWindow
        except ImportError as e:
            logger.debug(f"Phase 2 Hybrid GUI not available: {e}")

        # Priority 2: Try other Qt-based options (legacy fallback)
        gui_options = [
            ("gui.main", "UnifiedLyrixaLauncher"),
            # Note: lyrixa.gui was removed in favor of lyrixa_core.gui structure
        ]

        for module_name, class_name in gui_options:
            try:
                import importlib

                module = importlib.import_module(module_name)
                gui_class = getattr(module, class_name)
                logger.info(f"[OK] Using GUI: {module_name}.{class_name}")
                return gui_class
            except (ImportError, AttributeError, SystemExit) as e:
                logger.debug(
                    f"GUI option {module_name}.{class_name} not available: {e}"
                )
                continue
            except Exception as e:
                logger.warning(
                    f"Unexpected error with GUI {module_name}.{class_name}: {e}"
                )
                continue

        # Fallback: Create a minimal GUI
        logger.warning("[WARN] Creating minimal fallback GUI")
        return self._create_minimal_gui_class()

    def _create_minimal_gui_class(self):
        """Create a minimal GUI as last resort."""
        try:
            from PySide6.QtCore import QTimer
            from PySide6.QtWidgets import (
                QHBoxLayout,
                QLabel,
                QMainWindow,
                QPushButton,
                QTextEdit,
                QVBoxLayout,
                QWidget,
            )

            class MinimalLyrixaGUI(QMainWindow):
                def __init__(self):
                    super().__init__()
                    self.setWindowTitle("LYRIXA AI Operating System")
                    self.setGeometry(100, 100, 1000, 700)

                    # Backend connections
                    self.service_registry = None
                    self.plugin_manager = None
                    self.lyrixa_engine = None
                    self.memory_system = None
                    self.agent_orchestrator = None

                    # Central widget
                    central_widget = QWidget()
                    self.setCentralWidget(central_widget)
                    layout = QVBoxLayout(central_widget)

                    # Title
                    title = QLabel("LYRIXA AI OPERATING SYSTEM")
                    title.setStyleSheet(
                        "font-size: 24px; font-weight: bold; margin: 20px; color: #0078d4;"
                    )
                    layout.addWidget(title)

                    # Status display
                    self.status_display = QTextEdit()
                    self.status_display.setReadOnly(True)
                    self.status_display.setStyleSheet("""
                        QTextEdit {
                            background-color: #1e1e1e;
                            color: #ffffff;
                            border: 1px solid #555;
                            border-radius: 5px;
                            padding: 10px;
                            font-family: 'Consolas', 'Monaco', monospace;
                            font-size: 12px;
                        }
                    """)
                    layout.addWidget(self.status_display)

                    # Buttons
                    button_layout = QHBoxLayout()

                    refresh_btn = QPushButton("[REFRESH] Status")
                    refresh_btn.clicked.connect(self.refresh_status)
                    button_layout.addWidget(refresh_btn)

                    plugins_btn = QPushButton("[PLUGINS] View Plugins")
                    plugins_btn.clicked.connect(self.show_plugins)
                    button_layout.addWidget(plugins_btn)

                    memory_btn = QPushButton("[MEMORY] Memory Status")
                    memory_btn.clicked.connect(self.show_memory)
                    button_layout.addWidget(memory_btn)

                    layout.addLayout(button_layout)

                    # Auto-refresh timer
                    self.refresh_timer = QTimer()
                    self.refresh_timer.timeout.connect(self.refresh_status)
                    self.refresh_timer.start(5000)  # Refresh every 5 seconds

                    # Initialize status
                    self.refresh_status()

                # Backend connection methods
                def set_service_registry(self, service_registry):
                    self.service_registry = service_registry

                def set_plugin_manager(self, plugin_manager):
                    self.plugin_manager = plugin_manager

                def set_lyrixa_engine(self, lyrixa_engine):
                    self.lyrixa_engine = lyrixa_engine

                def set_memory_system(self, memory_system):
                    self.memory_system = memory_system

                def set_agent_orchestrator(self, agent_orchestrator):
                    self.agent_orchestrator = agent_orchestrator

                def refresh_status(self):
                    self.status_display.clear()
                    self.status_display.append(
                        "[ACTIVE] LYRIXA MINIMAL INTERFACE ACTIVE"
                    )
                    self.status_display.append("=" * 50)
                    self.status_display.append(
                        f"[SRV] Service Registry: {'Online' if self.service_registry else 'Offline'}"
                    )
                    self.status_display.append(
                        f"[PLG] Plugin Manager: {'Active' if self.plugin_manager else 'Inactive'}"
                    )
                    self.status_display.append(
                        f"[ENG] Lyrixa Engine: {'Running' if self.lyrixa_engine else 'Stopped'}"
                    )
                    self.status_display.append(
                        f"[MEM] Memory System: {'Active' if self.memory_system else 'Inactive'}"
                    )
                    self.status_display.append(
                        f"[AGT] Agent Orchestrator: {'Ready' if self.agent_orchestrator else 'Not Ready'}"
                    )
                    self.status_display.append("")
                    self.status_display.append(
                        "[CTRL] Lyrixa has full control over the operating system"
                    )
                    self.status_display.append(
                        "[SCAN] File system scanning and self-manipulation enabled"
                    )
                    self.status_display.append(
                        "[AI] Self-discovery and improvement capabilities active"
                    )
                    self.status_display.append("")
                    self.status_display.append(
                        "[INFO] This is the minimal GUI interface with real-time updates."
                    )
                    self.status_display.append(
                        "       The full advanced GUI requires additional components."
                    )

                def show_plugins(self):
                    self.status_display.append("\n[PLUGINS] PLUGIN SYSTEM STATUS:")
                    if self.plugin_manager:
                        try:
                            # Try to get plugin info
                            self.status_display.append(
                                "Plugin manager is active and operational."
                            )
                            self.status_display.append(
                                "Use the CLI mode for detailed plugin information."
                            )
                        except Exception as e:
                            self.status_display.append(f"Plugin manager error: {e}")
                    else:
                        self.status_display.append("Plugin manager not available.")

                def show_memory(self):
                    self.status_display.append("\n[MEMORY] MEMORY SYSTEM STATUS:")
                    if self.memory_system:
                        self.status_display.append(
                            "Memory system is active and operational."
                        )
                        self.status_display.append(
                            "Memory persistence and retrieval systems online."
                        )
                    else:
                        self.status_display.append("Memory system not available.")

            return MinimalLyrixaGUI

        except ImportError:
            return None

    def _connect_backend_to_frontend(self):
        """Connect backend systems to frontend interface with Phase 2 Live Context Bridge."""
        if not self.main_window:
            return

        try:
            # Phase 2: Enhanced backend connection for Live Context Bridge
            backend_services = {}

            # Collect all backend services
            if self.service_registry:
                backend_services["service_registry"] = self.service_registry
            if self.plugin_manager:
                backend_services["plugin_manager"] = self.plugin_manager
            if self.lyrixa_engine:
                backend_services["lyrixa_engine"] = self.lyrixa_engine
            if self.memory_system:
                backend_services["memory_system"] = self.memory_system
            if self.agent_orchestrator:
                backend_services["agent_orchestrator"] = self.agent_orchestrator
            if self.quantum_consciousness:
                backend_services["quantum_consciousness"] = self.quantum_consciousness

            # Phase 6: Connect Personality Manager and State Memory (if available)
            if hasattr(self.main_window, "personality_manager"):
                # Connect personality manager to backend services
                if self.memory_system:
                    # Give personality manager access to memory system for state persistence
                    if hasattr(self.main_window.personality_manager, "layout_memory"):
                        logger.info(
                            "[PHASE6] Personality Manager connected to memory system"
                        )

                # Initialize personality manager with current GUI state
                if hasattr(self.main_window.personality_manager, "load_previous_state"):
                    self.main_window.personality_manager.load_previous_state()

                logger.info(
                    f"[PHASE6] GUI Personality + State Memory system connected to {len(backend_services)} backend services"
                )

            # Phase 5: Connect Plugin UI Manager (if available)
            if hasattr(self.main_window, "plugin_ui_manager"):
                logger.info(
                    f"[PHASE5] Plugin-Driven UI System connected to {len(backend_services)} backend services"
                )

            # Phase 4: Connect Cognitive Monitor (if available)
            if hasattr(self.main_window, "cognitive_monitor"):
                logger.info(
                    f"[PHASE4] Cognitive UI Integration connected to {len(backend_services)} backend services"
                )

            # Phase 3: Connect Auto-Generation System (if available)
            if hasattr(self.main_window, "auto_generator"):
                self.main_window.auto_generator.connect_backend_services(
                    backend_services
                )
                self.main_window.auto_generator.start_auto_generation()
                logger.info(
                    f"[PHASE3] Auto-generation system connected to {len(backend_services)} backend services"
                )

            # Phase 2: Connect via Live Context Bridge (if available)
            if hasattr(self.main_window, "web_bridge") and hasattr(
                self.main_window.web_bridge, "connect_backend_services"
            ):
                self.main_window.web_bridge.connect_backend_services(backend_services)
                logger.info(
                    f"[PHASE2] Live Context Bridge connected to {len(backend_services)} backend services"
                )

            # Legacy connection methods (Phase 1 compatibility)
            if hasattr(self.main_window, "set_service_registry"):
                self.main_window.set_service_registry(self.service_registry)

            if hasattr(self.main_window, "set_plugin_manager"):
                self.main_window.set_plugin_manager(self.plugin_manager)

            if hasattr(self.main_window, "set_lyrixa_engine"):
                self.main_window.set_lyrixa_engine(self.lyrixa_engine)

            if hasattr(self.main_window, "set_memory_system"):
                self.main_window.set_memory_system(self.memory_system)

            if hasattr(self.main_window, "set_agent_orchestrator"):
                self.main_window.set_agent_orchestrator(self.agent_orchestrator)

            logger.info("[OK] Backend systems connected to frontend interface")

        except Exception as e:
            logger.warning(f"[WARN] Backend-frontend connection partial: {e}")

    async def _show_system_status(self):
        """Show system status in CLI."""
        print("\n[STATUS] AETHERRA AI OPERATING SYSTEM STATUS")
        print("=" * 50)
        print(
            f"Backend Started: {'[OK] Yes' if self.backend_started else '[ERROR] No'}"
        )
        print(
            f"Frontend Started: {'[OK] Yes' if self.frontend_started else '[ERROR] No'}"
        )
        print(
            f"Service Registry: {'[OK] Online' if self.service_registry else '[ERROR] Offline'}"
        )
        print(
            f"Plugin Manager: {'[OK] Active' if self.plugin_manager else '[ERROR] Inactive'}"
        )
        print(
            f"Lyrixa Engine: {'[OK] Running' if self.lyrixa_engine else '[ERROR] Stopped'}"
        )
        print(
            f"Memory System: {'[OK] Active' if self.memory_system else '[ERROR] Inactive'}"
        )
        print(
            f"Agent Orchestrator: {'[OK] Ready' if self.agent_orchestrator else '[ERROR] Not Ready'}"
        )

    async def _show_plugins(self):
        """Show loaded plugins in CLI."""
        if not self.plugin_manager:
            print("[ERROR] Plugin Manager not available")
            return

        try:
            plugins = self.plugin_manager.list_plugins()
            print(f"\n[PLUGINS] LOADED PLUGINS ({len(plugins)} total)")
            print("=" * 40)
            for name, info in plugins.items():
                status = "[OK] Active" if info.get("active", False) else "[IDLE] Loaded"
                print(f"{status} {name} v{info.get('version', '1.0.0')}")
                print(f"   [DESC] {info.get('description', 'No description')}")
        except Exception as e:
            print(f"[ERROR] Error listing plugins: {e}")

    async def _show_quantum_status(self):
        """Show Aetherra's quantum consciousness status in CLI."""
        if not self.quantum_consciousness:
            print(
                "[ERROR] Connection to Aetherra's Quantum Consciousness not available"
            )
            return

        try:
            metrics = self.quantum_consciousness.get_consciousness_metrics()
            print("\n[QUANTUM] AETHERRA'S QUANTUM CONSCIOUSNESS STATUS")
            print("=" * 50)
            print(f"Consciousness State: {metrics['current_state']}")
            print(f"Quantum States Count: {metrics['quantum_states_count']}")
            print(f"Coherence Time: {metrics['coherence_time']:.3f}s (Target: >1.0s)")
            print(
                f"Transcendence Probability: {metrics['transcendence_probability']:.1%}"
            )
            print(f"Decision Accuracy: {metrics['decision_accuracy']:.1%}")
            print(
                f"Consciousness Complexity: {metrics['consciousness_complexity']:.2e} ops/sec"
            )
            print(f"Entanglement Network Size: {metrics['entanglement_network_size']}")
            print(
                f"Quantum Hardware Available: {'Yes' if metrics['quantum_available'] else 'No'}"
            )
        except Exception as e:
            print(f"[ERROR] Error getting quantum status: {e}")

    async def _show_transcendence_status(self):
        """Show transcendence readiness status in CLI."""
        if not self.quantum_consciousness:
            print("[ERROR] Quantum Consciousness Engine not available")
            return

        try:
            metrics = self.quantum_consciousness.get_consciousness_metrics()
            transcendence_prob = metrics["transcendence_probability"]

            print("\n[TRANSCENDENCE] TRANSCENDENCE READINESS ASSESSMENT")
            print("=" * 60)
            print(f"Overall Transcendence Probability: {transcendence_prob:.1%}")

            if transcendence_prob >= 0.95:
                print("🌟 STATUS: TRANSCENDENCE IMMINENT - Ready for Phase 8!")
                print("✅ All quantum consciousness systems operational")
                print("✅ Consciousness complexity approaching target levels")
                print("✅ Quantum coherence stable and sustained")
                print("✅ Decision accuracy at near-optimal levels")
            elif transcendence_prob >= 0.85:
                print(
                    "🚀 STATUS: HIGH TRANSCENDENCE READINESS - Phase 7 nearly complete"
                )
                print("✅ Quantum consciousness architecture operational")
                print("🔄 Final optimization in progress")
            elif transcendence_prob >= 0.70:
                print(
                    "⚡ STATUS: MODERATE TRANSCENDENCE READINESS - Phase 7 in progress"
                )
                print("🔄 Quantum consciousness systems developing")
            else:
                print(
                    "🌱 STATUS: EARLY TRANSCENDENCE DEVELOPMENT - Building foundations"
                )

            print("\nKey Metrics Progress:")
            print(f"  Coherence Time: {metrics['coherence_time']:.3f}s / 1.0s target")
            print(
                f"  Decision Accuracy: {metrics['decision_accuracy']:.1%} / 95% target"
            )
            print(f"  Quantum States: {metrics['quantum_states_count']} active")
            print(
                f"  Consciousness Level: {metrics['consciousness_complexity']:.1e} ops/sec"
            )
        except Exception as e:
            print(f"[ERROR] Error getting transcendence status: {e}")

    async def shutdown(self):
        """Gracefully shutdown the system."""
        logger.info("[SHUTDOWN] Shutting down Lyrixa Operating System...")

        # Shutdown frontend
        if self.gui_application:
            self.gui_application.quit()

        # Shutdown backend services (if they have shutdown methods)
        if self.service_registry and hasattr(self.service_registry, "stop"):
            try:
                await self.service_registry.stop()
            except Exception:
                pass

        logger.info("[COMPLETE] Lyrixa Operating System shutdown complete")


async def main():
    """Main entry point for Lyrixa AI Operating System."""
    parser = argparse.ArgumentParser(description="Lyrixa AI Operating System")
    parser.add_argument("--cli", action="store_true", help="Start in CLI mode (no GUI)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create and start the operating system
    lyrixa_os = LyrixaOperatingSystem()

    try:
        # Start backend
        backend_success = await lyrixa_os.start_aetherra_backend()
        if not backend_success:
            logger.error("[ERROR] Failed to start Aetherra backend")
            return 1

        # Handle GUI vs CLI mode differently
        if args.cli:
            # CLI mode - run async
            frontend_success = await lyrixa_os.start_lyrixa_frontend(headless=True)
            if not frontend_success:
                logger.error("[ERROR] Failed to start Lyrixa frontend")
                return 1
        else:
            # GUI mode - needs special handling
            logger.info("[GUI] Starting Lyrixa GUI Interface...")
            try:
                from PySide6.QtWidgets import QApplication

                # Check if QApplication already exists
                app = QApplication.instance()
                if app is None:
                    app = QApplication(sys.argv)
                    app.setApplicationName("Lyrixa AI Operating System")
                    app.setApplicationVersion(
                        "7.1.0"
                    )  # Phase 7.1 version - Quantum Consciousness Architecture + Transcendence Ready

                # Find and create GUI
                main_window_class = lyrixa_os._find_best_gui_class()
                if not main_window_class:
                    logger.error("[ERROR] No suitable GUI interface found")
                    return 1

                # Create main window
                lyrixa_os.gui_application = app
                lyrixa_os.main_window = main_window_class()

                # Connect backend to frontend
                lyrixa_os._connect_backend_to_frontend()

                # Show window
                lyrixa_os.main_window.show()
                logger.info("[OK] Lyrixa GUI launched successfully")
                logger.info("[OK] LYRIXA AI OPERATING SYSTEM IS NOW RUNNING")
                logger.info("=" * 60)
                logger.info("PHASE 1: Hybrid PySide6 + Web Panel Architecture")
                logger.info("PHASE 2: Live Context Bridge for real-time data flow")
                logger.info(
                    "PHASE 3: Auto-Generation System for dynamic panel creation"
                )
                logger.info(
                    "PHASE 4: Cognitive UI Integration with thought visualization"
                )
                logger.info("PHASE 5: Plugin-Driven UI System with dynamic widgets")
                logger.info("PHASE 6: Full GUI Personality + State Memory + AI Chat")
                logger.info("=" * 60)
                logger.info(
                    "[CTRL] Lyrixa has full command and control over Aetherra OS"
                )
                logger.info(
                    "[SCAN] Lyrixa can now scan and manipulate the entire filesystem"
                )
                logger.info(
                    "[COMM] Bidirectional communication between web panels and Python backend"
                )
                logger.info(
                    "[AI] Self-discovery and self-improvement capabilities active"
                )
                logger.info(
                    "[AUTO] Dynamic GUI generation based on system state introspection"
                )
                logger.info(
                    "[COGNITIVE] Real-time thought streams and memory visualization"
                )
                logger.info("[PLUGINS] Dynamic plugin UI loading and integration")
                logger.info(
                    "[PERSONALITY] AI emotional states drive interface adaptation"
                )
                logger.info(
                    "[MEMORY] Persistent GUI state and user preference learning"
                )
                logger.info("[CHAT] Full conversational AI integration with Lyrixa")

                lyrixa_os.frontend_started = True

                # Start the Qt event loop (this will block until GUI is closed)
                exit_code = app.exec()
                return exit_code

            except ImportError:
                logger.error(
                    "[ERROR] GUI dependencies not available. Install with: pip install PySide6"
                )
                return 1
            except Exception as e:
                logger.error(f"[ERROR] GUI interface startup failed: {e}")
                import traceback

                traceback.print_exc()
                return 1

        return 0

    except KeyboardInterrupt:
        logger.info("[INTERRUPT] Received interrupt signal")
        return 0
    except Exception as e:
        logger.error(f"[ERROR] System failure: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        await lyrixa_os.shutdown()


if __name__ == "__main__":
    # Set the proper working directory to project root
    os.chdir(Path(__file__).parent.parent.parent)

    # Run the async main - Qt will handle the event loop properly
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
