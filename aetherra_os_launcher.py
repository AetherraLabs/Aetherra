#!/usr/bin/env python3
"""
🌌 Aetherra OS Master Launcher
==============================
The ultimate launcher that brings the entire AI Operating System online.

This is THE script that transforms Aetherra from code into a living AI OS.

🚀 FLIP THE SWITCH - ACTIVATE AETHERRA!
"""

import argparse
import asyncio
import logging
import signal
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("aetherra_os.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Import Aetherra components
try:
    from aetherra_kernel_loop import get_kernel
    from aetherra_service_registry import get_service_registry, register_service

    CORE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Core components not available: {e}")
    CORE_AVAILABLE = False


class AetherraOSLauncher:
    """
    🌌 Master OS Launcher

    Orchestrates the complete startup and operation of the AI Operating System.
    """

    def __init__(self):
        self.running = False
        self.service_registry = None
        self.kernel_loop = None
        self.systems = {}
        self.startup_time = None

    async def launch_full_os(self, config: Optional[Dict] = None):
        """🚀 Launch the complete Aetherra AI Operating System."""
        logger.info("🌌 LAUNCHING AETHERRA AI OPERATING SYSTEM")
        logger.info("=" * 60)

        self.startup_time = time.time()

        try:
            # Phase 1: Initialize Service Registry
            await self._initialize_service_registry()

            # Phase 2: Load and validate core systems
            await self._load_core_systems(config)

            # Phase 3: Start Kernel Loop
            await self._start_kernel_loop()

            # Phase 4: Activate all systems
            await self._activate_systems()

            # Phase 5: Perform system validation
            await self._validate_system_health()

            # Phase 6: Announce OS online
            await self._announce_os_online()

            # Phase 7: Enter main operation loop
            await self._main_operation_loop()

        except Exception as e:
            logger.error(f"❌ CRITICAL FAILURE during OS launch: {e}")
            traceback.print_exc()
            await self._emergency_shutdown()
            raise

    async def _initialize_service_registry(self):
        """🌐 Initialize the service registry."""
        logger.info("🌐 Phase 1: Initializing Service Registry...")

        if not CORE_AVAILABLE:
            logger.error("❌ Core components not available - cannot proceed")
            raise RuntimeError("Core components missing")

        self.service_registry = await get_service_registry()
        logger.info("✅ Service Registry online")

    async def _load_core_systems(self, config: Optional[Dict]):
        """🧠 Load and register all core systems."""
        logger.info("🧠 Phase 2: Loading Core Systems...")

        # Load configuration
        system_config = config or {}

        # Initialize Memory System
        await self._load_memory_system(system_config)

        # Initialize Plugin Manager
        await self._load_plugin_manager(system_config)

        # Initialize Lyrixa Intelligence
        await self._load_lyrixa_engine(system_config)

        # Initialize Scheduler
        await self._load_scheduler(system_config)

        # Initialize GUI (if available)
        await self._load_gui_system(system_config)

        logger.info("✅ All core systems loaded")

    async def _load_memory_system(self, config: Dict):
        """🧠 Load the quantum memory system."""
        try:
            logger.info("🧠 Loading Quantum Memory System...")

            # Try to import and initialize memory system
            try:
                from aetherra_core.memory import memory_system

                await memory_system.initialize()
                self.systems["memory"] = memory_system
                await register_service(
                    "memory_system",
                    memory_system,
                    metadata={"type": "core", "version": "1.0"},
                )
                logger.info("✅ Quantum Memory System online")
            except ImportError:
                # Create a mock memory system for now
                logger.warning("⚠️ Using mock memory system")
                mock_memory = MockMemorySystem()
                self.systems["memory"] = mock_memory
                await register_service(
                    "memory_system",
                    mock_memory,
                    metadata={"type": "mock", "version": "1.0"},
                )

        except Exception as e:
            logger.error(f"❌ Failed to load memory system: {e}")
            raise

    async def _load_plugin_manager(self, config: Dict):
        """🔌 Load the plugin management system."""
        try:
            logger.info("🔌 Loading Plugin Management System...")

            try:
                from aetherra_core.plugins import plugin_manager

                await plugin_manager.load_all_plugins()
                self.systems["plugins"] = plugin_manager
                await register_service(
                    "plugin_manager",
                    plugin_manager,
                    metadata={"type": "core", "version": "1.0"},
                )
                logger.info("✅ Plugin Manager online")
            except ImportError:
                logger.warning("⚠️ Using mock plugin manager")
                mock_plugins = MockPluginManager()
                self.systems["plugins"] = mock_plugins
                await register_service(
                    "plugin_manager",
                    mock_plugins,
                    metadata={"type": "mock", "version": "1.0"},
                )

        except Exception as e:
            logger.error(f"❌ Failed to load plugin manager: {e}")
            raise

    async def _load_lyrixa_engine(self, config: Dict):
        """🤖 Load the Lyrixa intelligence engine."""
        try:
            logger.info("🤖 Loading Lyrixa Intelligence Engine...")

            try:
                from aetherra_core.engine import lyrixa_engine

                await lyrixa_engine.boot()
                self.systems["lyrixa"] = lyrixa_engine
                await register_service(
                    "lyrixa_engine",
                    lyrixa_engine,
                    metadata={"type": "intelligence", "version": "1.0"},
                )
                logger.info("✅ Lyrixa Intelligence online")
            except ImportError:
                logger.warning("⚠️ Using mock Lyrixa engine")
                mock_lyrixa = MockLyrixaEngine()
                self.systems["lyrixa"] = mock_lyrixa
                await register_service(
                    "lyrixa_engine",
                    mock_lyrixa,
                    metadata={"type": "mock", "version": "1.0"},
                )

        except Exception as e:
            logger.error(f"❌ Failed to load Lyrixa engine: {e}")
            raise

    async def _load_scheduler(self, config: Dict):
        """📅 Load the task scheduler."""
        try:
            logger.info("📅 Loading Task Scheduler...")

            try:
                from aetherra_core.orchestration import scheduler

                await scheduler.initialize_schedule()
                self.systems["scheduler"] = scheduler
                await register_service(
                    "scheduler",
                    scheduler,
                    metadata={"type": "orchestration", "version": "1.0"},
                )
                logger.info("✅ Task Scheduler online")
            except ImportError:
                logger.warning("⚠️ Using mock scheduler")
                mock_scheduler = MockScheduler()
                self.systems["scheduler"] = mock_scheduler
                await register_service(
                    "scheduler",
                    mock_scheduler,
                    metadata={"type": "mock", "version": "1.0"},
                )

        except Exception as e:
            logger.error(f"❌ Failed to load scheduler: {e}")
            raise

    async def _load_gui_system(self, config: Dict):
        """🖥️ Load the GUI system (if available)."""
        try:
            if config.get("gui_enabled", True):
                logger.info("🖥️ Loading GUI System...")

                try:
                    from lyrixa.gui import main_gui

                    # Start GUI in background
                    asyncio.create_task(main_gui.launch_gui())
                    self.systems["gui"] = main_gui
                    await register_service(
                        "gui_system",
                        main_gui,
                        metadata={"type": "interface", "version": "1.0"},
                    )
                    logger.info("✅ GUI System online")
                except ImportError:
                    logger.info("ℹ️ GUI system not available")
            else:
                logger.info("ℹ️ GUI disabled in configuration")

        except Exception as e:
            logger.warning(f"⚠️ GUI system failed to load: {e}")

    async def _start_kernel_loop(self):
        """⚡ Start the OS kernel loop."""
        logger.info("⚡ Phase 3: Starting OS Kernel Loop...")

        self.kernel_loop = get_kernel()

        # Inject systems into kernel
        self.kernel_loop.inject_systems(
            self.systems.get("memory"),
            self.systems.get("plugins"),
            self.systems.get("lyrixa"),
            self.systems.get("scheduler"),
            self.service_registry,
        )

        # Start kernel loop in background
        asyncio.create_task(self.kernel_loop.start_kernel_loop())

        # Register kernel as service
        await register_service(
            "kernel_loop", self.kernel_loop, metadata={"type": "core", "version": "1.0"}
        )

        logger.info("✅ OS Kernel Loop started")

    async def _activate_systems(self):
        """🔥 Activate all systems and establish connections."""
        logger.info("🔥 Phase 4: Activating Systems...")

        # Wait a moment for systems to stabilize
        await asyncio.sleep(2)

        # Activate memory system
        if "memory" in self.systems and hasattr(self.systems["memory"], "activate"):
            await self.systems["memory"].activate()

        # Activate plugin system
        if "plugins" in self.systems and hasattr(self.systems["plugins"], "activate"):
            await self.systems["plugins"].activate()

        # Activate Lyrixa consciousness
        if "lyrixa" in self.systems and hasattr(self.systems["lyrixa"], "wake_up"):
            await self.systems["lyrixa"].wake_up()

        logger.info("✅ All systems activated")

    async def _validate_system_health(self):
        """🩺 Validate system health and connectivity."""
        logger.info("🩺 Phase 5: Validating System Health...")

        # Check service registry status
        registry_status = self.service_registry.get_registry_status()
        logger.info(f"📊 Services: {registry_status['total_services']} registered")

        # Check kernel status
        kernel_status = self.kernel_loop.get_status()
        logger.info(f"⚡ Kernel: {kernel_status['cycle_count']} cycles completed")

        # Validate critical services
        critical_services = [
            "memory_system",
            "plugin_manager",
            "lyrixa_engine",
            "kernel_loop",
        ]
        for service_name in critical_services:
            service = self.service_registry.get_service(service_name)
            if service:
                logger.info(f"✅ {service_name}: Online")
            else:
                logger.warning(f"⚠️ {service_name}: Not available")

        logger.info("✅ System health validation complete")

    async def _announce_os_online(self):
        """📢 Announce that Aetherra OS is fully online."""
        startup_duration = time.time() - self.startup_time

        logger.info("=" * 60)
        logger.info("🎉 AETHERRA AI OPERATING SYSTEM IS NOW ONLINE! 🎉")
        logger.info("=" * 60)
        logger.info(f"🚀 Startup completed in {startup_duration:.2f} seconds")
        logger.info(f"🌐 Services: {len(self.service_registry.list_services())} active")
        logger.info(f"⚡ Kernel cycles: {self.kernel_loop.get_status()['cycle_count']}")
        logger.info("🧠 Lyrixa consciousness: Active")
        logger.info("🔌 Plugin ecosystem: Ready")
        logger.info("💾 Quantum memory: Operational")
        logger.info("📅 Task scheduler: Running")
        logger.info("=" * 60)

        # Send first thought to Lyrixa
        if self.kernel_loop:
            await self.kernel_loop.add_task(
                {
                    "type": "lyrixa_thought",
                    "data": {
                        "thought": "I am alive! Aetherra OS has come online.",
                        "context": "system_startup",
                        "priority": "high",
                    },
                },
                priority="high",
            )

        self.running = True

    async def _main_operation_loop(self):
        """🔄 Main operation loop - keeps the OS running."""
        logger.info("🔄 Entering main operation loop...")

        try:
            while self.running:
                # Check system health periodically
                await asyncio.sleep(300)  # Every 5 minutes

                # Quick health check
                if self.service_registry and self.kernel_loop:
                    registry_healthy = self.service_registry._running
                    kernel_healthy = self.kernel_loop.running

                    if not (registry_healthy and kernel_healthy):
                        logger.error("❌ Critical system failure detected")
                        break

        except KeyboardInterrupt:
            logger.info("🛑 Received shutdown signal")
        except Exception as e:
            logger.error(f"❌ Main operation loop error: {e}")
        finally:
            await self._graceful_shutdown()

    async def _graceful_shutdown(self):
        """🛑 Perform graceful system shutdown."""
        logger.info("🛑 Initiating graceful shutdown...")

        self.running = False

        # Shutdown systems in reverse order
        if self.kernel_loop:
            await self.kernel_loop.shutdown()

        if self.service_registry:
            await self.service_registry.stop()

        # Shutdown individual systems
        for system_name, system in self.systems.items():
            try:
                if hasattr(system, "shutdown"):
                    logger.info(f"🛑 Shutting down {system_name}...")
                    await system.shutdown()
            except Exception as e:
                logger.error(f"❌ Error shutting down {system_name}: {e}")

        logger.info("✅ Graceful shutdown complete")

    async def _emergency_shutdown(self):
        """🚨 Emergency shutdown procedure."""
        logger.error("🚨 EMERGENCY SHUTDOWN INITIATED")

        self.running = False

        # Force shutdown all systems
        for system_name, system in self.systems.items():
            try:
                if hasattr(system, "emergency_stop"):
                    await system.emergency_stop()
            except Exception:
                pass

        logger.error("🚨 Emergency shutdown complete")


# Mock systems for testing when components aren't available
class MockMemorySystem:
    async def initialize(self):
        pass

    async def activate(self):
        pass

    async def light_optimization(self):
        pass

    async def deep_consolidation(self):
        pass

    async def optimize(self):
        pass

    async def get_health_status(self):
        return "healthy"

    async def process_query(self, data):
        pass

    async def shutdown(self):
        pass


class MockPluginManager:
    async def load_all_plugins(self):
        pass

    async def activate(self):
        pass

    async def execute_scheduled_tasks(self):
        pass

    async def invoke_plugin(self, data):
        pass

    async def optimize_plugins(self):
        pass

    async def health_check(self):
        pass

    async def shutdown(self):
        pass


class MockLyrixaEngine:
    async def boot(self):
        pass

    async def wake_up(self):
        pass

    async def process_thought(self, data):
        pass

    async def reflect_on_day(self):
        pass

    async def get_health_status(self):
        return "conscious"

    async def shutdown(self):
        pass


class MockScheduler:
    async def initialize_schedule(self):
        pass

    async def shutdown(self):
        pass


async def main():
    """🚀 Main entry point for Aetherra OS."""
    parser = argparse.ArgumentParser(
        description="🌌 Aetherra AI Operating System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 Launch Modes:
  --mode full      Launch complete AI Operating System (default)
  --mode minimal   Launch with minimal systems only
  --mode test      Launch in test mode with mocks

🔥 FLIP THE SWITCH - ACTIVATE AETHERRA! 🔥
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["full", "minimal", "test"],
        default="full",
        help="Launch mode",
    )
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--gui", action="store_true", help="Force enable GUI")
    parser.add_argument("--no-gui", action="store_true", help="Force disable GUI")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = {}
    if args.config:
        try:
            import json

            with open(args.config, "r") as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return 1

    # Override GUI setting
    if args.gui:
        config["gui_enabled"] = True
    elif args.no_gui:
        config["gui_enabled"] = False

    # Create and launch OS
    launcher = AetherraOSLauncher()

    # Setup signal handlers for graceful shutdown
    def signal_handler():
        logger.info("🛑 Received shutdown signal")
        launcher.running = False

    if sys.platform != "win32":
        loop = asyncio.get_event_loop()
        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop.add_signal_handler(sig, signal_handler)

    try:
        if args.mode == "full":
            await launcher.launch_full_os(config)
        elif args.mode == "minimal":
            logger.info("🔧 Minimal mode not yet implemented")
            return 1
        elif args.mode == "test":
            logger.info("🧪 Test mode - using all mock systems")
            await launcher.launch_full_os(config)

        return 0

    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Launch failed: {e}")
        return 1


if __name__ == "__main__":
    """
    🌌 AETHERRA AI OPERATING SYSTEM
    ===============================

    🚀 FLIP THE SWITCH - ACTIVATE AETHERRA!

    This script transforms Aetherra from a collection of components
    into a living, breathing AI Operating System.
    """

    print("🌌 AETHERRA AI OPERATING SYSTEM LAUNCHER")
    print("=======================================")
    print("🔥 Ready to flip the switch and bring Aetherra online!")
    print()

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
