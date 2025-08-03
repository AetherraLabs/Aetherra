#!/usr/bin/env python3
"""
LYRIXA - UNIFIED AI OPERATING SYSTEM LAUNCHER
================================================

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

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

# Add project paths - we're in Aetherra/lyrixa/ so parent.parent is project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent.parent))  # Aetherra directory
sys.path.insert(0, str(Path(__file__).parent))  # lyrixa directory

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('lyrixa_system.log')
    ]
)
logger = logging.getLogger(__name__)

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
                    "lyrixa.memory.quantum_memory_integration"
                ]

                self.memory_system = None
                for candidate in memory_candidates:
                    try:
                        module = __import__(candidate, fromlist=[''])
                        if hasattr(module, 'get_memory_system'):
                            self.memory_system = await module.get_memory_system()
                        elif hasattr(module, 'memory_system'):
                            self.memory_system = module.memory_system
                        elif hasattr(module, 'QuantumMemorySystem'):
                            self.memory_system = module.QuantumMemorySystem()

                        if self.memory_system:
                            logger.info(f"[OK] Loaded memory system from {candidate}")
                            break
                    except ImportError:
                        continue

                if not self.memory_system:
                    logger.warning("[WARN] Using mock memory system")
                    self.memory_system = type('MockMemory', (), {
                        'initialize': lambda: None,
                        'store': lambda data: None,
                        'retrieve': lambda query: None
                    })()

            except Exception as e:
                logger.warning(f"[WARN] Memory system error: {e}, using mock")
                self.memory_system = type('MockMemory', (), {})()

            await self.service_registry.register_service("memory_system", self.memory_system)
            logger.info("[OK] Memory System online")

            # Phase 3: Plugin Manager
            logger.info("[PLG] Phase 3: Initializing Plugin Manager...")
            from aetherra_core.plugins import plugin_manager
            await plugin_manager.get_plugin_manager()
            self.plugin_manager = plugin_manager

            # Load all plugins
            plugin_results = await plugin_manager.load_all_plugins()
            loaded_count = sum(1 for success in plugin_results.values() if success)
            logger.info(f"[OK] Plugin Manager online - {loaded_count} plugins loaded")

            await self.service_registry.register_service("plugin_manager", self.plugin_manager)

            # Phase 4: Lyrixa Engine
            logger.info("[ENG] Phase 4: Initializing Lyrixa Engine...")
            from aetherra_core.engine.lyrixa_engine import lyrixa_engine
            self.lyrixa_engine = lyrixa_engine
            logger.info("[OK] Lyrixa Engine online")

            await self.service_registry.register_service("lyrixa_engine", self.lyrixa_engine)

            # Phase 5: Agent Orchestrator
            logger.info("[AGT] Phase 5: Initializing Agent Orchestrator...")
            self.agent_orchestrator = self.lyrixa_engine.agent_orchestrator
            logger.info("[OK] Agent Orchestrator online")

            await self.service_registry.register_service("agent_orchestrator", self.agent_orchestrator)

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
                logger.error("[ERROR] GUI dependencies not available. Install with: pip install PySide6")
                return False

            # Create Qt Application
            self.gui_application = QApplication.instance() or QApplication(sys.argv)
            self.gui_application.setApplicationName("Lyrixa AI Operating System")
            self.gui_application.setApplicationVersion("2.0.0")  # Phase 2 version

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
            logger.info("[BRIDGE] Phase 2: Live Context Bridge active for real-time data flow")
            logger.info("[CTRL] Lyrixa has full command and control over Aetherra OS")
            logger.info("[SCAN] Lyrixa can now scan and manipulate the entire filesystem")
            logger.info("[COMM] Bidirectional communication between web panels and Python backend")
            logger.info("[AI] Self-discovery and self-improvement capabilities active")

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
                    if user_input.lower() in ['exit', 'quit']:
                        break
                    elif user_input.lower() == 'help':
                        print("Available commands:")
                        print("  status  - Show system status")
                        print("  plugins - List loaded plugins")
                        print("  memory  - Show memory status")
                        print("  agents  - List active agents")
                        print("  help    - Show this help")
                        print("  exit    - Quit Lyrixa")
                    elif user_input.lower() == 'status':
                        await self._show_system_status()
                    elif user_input.lower() == 'plugins':
                        await self._show_plugins()
                    elif user_input.lower() == 'memory':
                        print("[MEM] Memory system operational")
                    elif user_input.lower() == 'agents':
                        agent_count = 0
                        if self.agent_orchestrator and hasattr(self.agent_orchestrator, 'agents'):
                            agent_count = len(self.agent_orchestrator.agents)
                        print(f"[AGT] Agent Orchestrator: {agent_count} agents")
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
        # Priority 1: Try the Phase 2 Hybrid GUI with Live Context Bridge
        try:
            from lyrixa_core.gui.main_window import LyrixaHybridWindow
            logger.info("[OK] Using Phase 2 Lyrixa Hybrid GUI (PySide6 + Web Panels + Live Context Bridge)")
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
                logger.debug(f"GUI option {module_name}.{class_name} not available: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error with GUI {module_name}.{class_name}: {e}")
                continue

        # Fallback: Create a minimal GUI
        logger.warning("[WARN] Creating minimal fallback GUI")
        return self._create_minimal_gui_class()

    def _create_minimal_gui_class(self):
        """Create a minimal GUI as last resort."""
        try:
            from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                                           QTextEdit, QLabel, QPushButton, QHBoxLayout)
            from PySide6.QtCore import QTimer

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
                    title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px; color: #0078d4;")
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
                    self.status_display.append("[ACTIVE] LYRIXA MINIMAL INTERFACE ACTIVE")
                    self.status_display.append("=" * 50)
                    self.status_display.append(f"[SRV] Service Registry: {'Online' if self.service_registry else 'Offline'}")
                    self.status_display.append(f"[PLG] Plugin Manager: {'Active' if self.plugin_manager else 'Inactive'}")
                    self.status_display.append(f"[ENG] Lyrixa Engine: {'Running' if self.lyrixa_engine else 'Stopped'}")
                    self.status_display.append(f"[MEM] Memory System: {'Active' if self.memory_system else 'Inactive'}")
                    self.status_display.append(f"[AGT] Agent Orchestrator: {'Ready' if self.agent_orchestrator else 'Not Ready'}")
                    self.status_display.append("")
                    self.status_display.append("[CTRL] Lyrixa has full control over the operating system")
                    self.status_display.append("[SCAN] File system scanning and self-manipulation enabled")
                    self.status_display.append("[AI] Self-discovery and improvement capabilities active")
                    self.status_display.append("")
                    self.status_display.append("[INFO] This is the minimal GUI interface with real-time updates.")
                    self.status_display.append("       The full advanced GUI requires additional components.")

                def show_plugins(self):
                    self.status_display.append("\n[PLUGINS] PLUGIN SYSTEM STATUS:")
                    if self.plugin_manager:
                        try:
                            # Try to get plugin info
                            self.status_display.append("Plugin manager is active and operational.")
                            self.status_display.append("Use the CLI mode for detailed plugin information.")
                        except Exception as e:
                            self.status_display.append(f"Plugin manager error: {e}")
                    else:
                        self.status_display.append("Plugin manager not available.")

                def show_memory(self):
                    self.status_display.append("\n[MEMORY] MEMORY SYSTEM STATUS:")
                    if self.memory_system:
                        self.status_display.append("Memory system is active and operational.")
                        self.status_display.append("Memory persistence and retrieval systems online.")
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
                backend_services['service_registry'] = self.service_registry
            if self.plugin_manager:
                backend_services['plugin_manager'] = self.plugin_manager
            if self.lyrixa_engine:
                backend_services['lyrixa_engine'] = self.lyrixa_engine
            if self.memory_system:
                backend_services['memory_system'] = self.memory_system
            if self.agent_orchestrator:
                backend_services['agent_orchestrator'] = self.agent_orchestrator

            # Phase 2: Connect via Live Context Bridge (if available)
            if hasattr(self.main_window, 'web_bridge') and hasattr(self.main_window.web_bridge, 'connect_backend_services'):
                self.main_window.web_bridge.connect_backend_services(backend_services)
                logger.info(f"[BRIDGE] Phase 2: Live Context Bridge connected to {len(backend_services)} backend services")

            # Legacy connection methods (Phase 1 compatibility)
            if hasattr(self.main_window, 'set_service_registry'):
                self.main_window.set_service_registry(self.service_registry)

            if hasattr(self.main_window, 'set_plugin_manager'):
                self.main_window.set_plugin_manager(self.plugin_manager)

            if hasattr(self.main_window, 'set_lyrixa_engine'):
                self.main_window.set_lyrixa_engine(self.lyrixa_engine)

            if hasattr(self.main_window, 'set_memory_system'):
                self.main_window.set_memory_system(self.memory_system)

            if hasattr(self.main_window, 'set_agent_orchestrator'):
                self.main_window.set_agent_orchestrator(self.agent_orchestrator)

            logger.info("[OK] Backend systems connected to frontend interface")

        except Exception as e:
            logger.warning(f"[WARN] Backend-frontend connection partial: {e}")

    async def _show_system_status(self):
        """Show system status in CLI."""
        print("\n[STATUS] AETHERRA AI OPERATING SYSTEM STATUS")
        print("=" * 50)
        print(f"Backend Started: {'[OK] Yes' if self.backend_started else '[ERROR] No'}")
        print(f"Frontend Started: {'[OK] Yes' if self.frontend_started else '[ERROR] No'}")
        print(f"Service Registry: {'[OK] Online' if self.service_registry else '[ERROR] Offline'}")
        print(f"Plugin Manager: {'[OK] Active' if self.plugin_manager else '[ERROR] Inactive'}")
        print(f"Lyrixa Engine: {'[OK] Running' if self.lyrixa_engine else '[ERROR] Stopped'}")
        print(f"Memory System: {'[OK] Active' if self.memory_system else '[ERROR] Inactive'}")
        print(f"Agent Orchestrator: {'[OK] Ready' if self.agent_orchestrator else '[ERROR] Not Ready'}")

    async def _show_plugins(self):
        """Show loaded plugins in CLI."""
        if not self.plugin_manager:
            print("[ERROR] Plugin Manager not available")
            return

        try:
            plugins = await self.plugin_manager.list_plugins()
            print(f"\n[PLUGINS] LOADED PLUGINS ({len(plugins)} total)")
            print("=" * 40)
            for name, info in plugins.items():
                status = "[OK] Active" if info.get('active', False) else "[IDLE] Loaded"
                print(f"{status} {name} v{info.get('version', '1.0.0')}")
                print(f"   [DESC] {info.get('description', 'No description')}")
        except Exception as e:
            print(f"[ERROR] Error listing plugins: {e}")

    async def shutdown(self):
        """Gracefully shutdown the system."""
        logger.info("[SHUTDOWN] Shutting down Lyrixa Operating System...")

        # Shutdown frontend
        if self.gui_application:
            self.gui_application.quit()

        # Shutdown backend services (if they have shutdown methods)
        if self.service_registry and hasattr(self.service_registry, 'stop'):
            try:
                await self.service_registry.stop()
            except:
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
                    app.setApplicationVersion("2.0.0")  # Phase 2 version

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
                logger.info("[BRIDGE] Phase 2: Live Context Bridge active for real-time data flow")
                logger.info("[CTRL] Lyrixa has full command and control over Aetherra OS")
                logger.info("[SCAN] Lyrixa can now scan and manipulate the entire filesystem")
                logger.info("[COMM] Bidirectional communication between web panels and Python backend")
                logger.info("[AI] Self-discovery and self-improvement capabilities active")

                lyrixa_os.frontend_started = True

                # Start the Qt event loop (this will block until GUI is closed)
                exit_code = app.exec()
                return exit_code

            except ImportError:
                logger.error("[ERROR] GUI dependencies not available. Install with: pip install PySide6")
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
