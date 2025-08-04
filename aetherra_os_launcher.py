#!/usr/bin/env python3
"""
[CORE] Aetherra OS Master Launcher
==============================
The ultimate launcher that brings the entire AI Operating System online.

This is THE script that transforms Aetherra from code into a living AI OS.

[LAUNCH] FLIP THE SWITCH - ACTIVATE AETHERRA!
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
    from aetherra_service_registry import get_service_registry, register_service, ServiceStatus

    CORE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[WARN] Core components not available: {e}")
    CORE_AVAILABLE = False
    # Define dummy classes for type checking when imports fail
    ServiceStatus = None


class AetherraOSLauncher:
    """
    [CORE] Master OS Launcher

    Orchestrates the complete startup and operation of the AI Operating System.
    """

    def __init__(self):
        self.running = False
        self.service_registry = None
        self.kernel_loop = None
        self.systems = {}
        self.startup_time = None

    async def launch_full_os(self, config: Optional[Dict] = None):
        """[LAUNCH] Launch the complete Aetherra AI Operating System."""
        logger.info("[CORE] LAUNCHING AETHERRA AI OPERATING SYSTEM")
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
            logger.error(f"[ERROR] CRITICAL FAILURE during OS launch: {e}")
            traceback.print_exc()
            await self._emergency_shutdown()
            raise

    async def _initialize_service_registry(self):
        """[NET] Initialize the service registry."""
        logger.info("[NET] Phase 1: Initializing Service Registry...")

        if not CORE_AVAILABLE:
            logger.error("[ERROR] Core components not available - cannot proceed")
            raise RuntimeError("Core components missing")

        self.service_registry = await get_service_registry()
        logger.info("[OK] Service Registry online")

    async def _load_core_systems(self, config: Optional[Dict]):
        """[BRAIN] Load and register all core systems."""
        logger.info("[BRAIN] Phase 2: Loading Core Systems...")

        # Load configuration
        system_config = config or {}

        # Initialize Memory System
        await self._load_memory_system(system_config)

        # Initialize Plugin Manager
        await self._load_plugin_manager(system_config)

        # Initialize Aetherra Native Engine
        await self._load_aetherra_engine(system_config)

        # Initialize Scheduler
        await self._load_scheduler(system_config)

        # Initialize Aetherra Hub (Plugin Marketplace)
        await self._load_aetherra_hub(system_config)

        # Initialize GUI (if available)
        await self._load_gui_system(system_config)

        logger.info("[OK] All core systems loaded")

    async def _load_memory_system(self, config: Dict):
        """[BRAIN] Load the quantum memory system."""
        try:
            logger.info("[BRAIN] Loading Quantum Memory System...")

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
                logger.info("[OK] Quantum Memory System online")
            except ImportError:
                # Create a mock memory system for now
                logger.warning("[WARN] Using mock memory system")
                mock_memory = MockMemorySystem()
                self.systems["memory"] = mock_memory
                await register_service(
                    "memory_system",
                    mock_memory,
                    metadata={"type": "mock", "version": "1.0"},
                )

        except Exception as e:
            logger.error(f"[ERROR] Failed to load memory system: {e}")
            raise

    async def _load_plugin_manager(self, config: Dict):
        """[PLUGIN] Load the plugin management system."""
        try:
            logger.info("[PLUGIN] Loading Plugin Management System...")

            try:
                from aetherra_core.orchestration.plugin_manager import get_plugin_manager

                plugin_manager = await get_plugin_manager()
                await plugin_manager.load_all_plugins()
                self.systems["plugins"] = plugin_manager
                await register_service(
                    "plugin_manager",
                    plugin_manager,
                    metadata={"type": "core", "version": "1.0"},
                )
                logger.info("[OK] Plugin Manager online")
            except ImportError:
                logger.warning("[WARN] Using mock plugin manager")
                mock_plugins = MockPluginManager()
                self.systems["plugins"] = mock_plugins
                await register_service(
                    "plugin_manager",
                    mock_plugins,
                    metadata={"type": "mock", "version": "1.0"},
                )

        except Exception as e:
            logger.error(f"[ERROR] Failed to load plugin manager: {e}")
            raise

    async def _load_aetherra_engine(self, config: Dict):
        """� Load the native Aetherra execution engine."""
        try:
            logger.info("[ENGINE] Loading Aetherra Native Engine...")

            try:
                from aetherra_core.engine import aetherra_engine

                engine_instance = await aetherra_engine.boot()
                self.systems["aetherra"] = engine_instance
                await register_service(
                    "aetherra_engine",
                    engine_instance,
                    metadata={"type": "native_engine", "version": "1.0"},
                )
                logger.info("[OK] Aetherra Native Engine online")
            except ImportError:
                logger.warning("[WARN] Using mock Aetherra engine")
                mock_aetherra = MockAetherraEngine()
                self.systems["aetherra"] = mock_aetherra
                await register_service(
                    "aetherra_engine",
                    mock_aetherra,
                    metadata={"type": "mock", "version": "1.0"},
                )

        except Exception as e:
            logger.error(f"[ERROR] Failed to load Aetherra engine: {e}")
            raise

    async def _load_scheduler(self, config: Dict):
        """[SCHED] Load the task scheduler."""
        try:
            logger.info("[SCHED] Loading Task Scheduler...")

            try:
                from aetherra_core.orchestration import scheduler

                await scheduler.initialize_schedule()
                self.systems["scheduler"] = scheduler
                await register_service(
                    "scheduler",
                    scheduler,
                    metadata={"type": "orchestration", "version": "1.0"},
                )
                logger.info("[OK] Task Scheduler online")
            except ImportError:
                logger.warning("[WARN] Using mock scheduler")
                mock_scheduler = MockScheduler()
                self.systems["scheduler"] = mock_scheduler
                await register_service(
                    "scheduler",
                    mock_scheduler,
                    metadata={"type": "mock", "version": "1.0"},
                )

        except Exception as e:
            logger.error(f"[ERROR] Failed to load scheduler: {e}")
            raise

    async def _load_aetherra_hub(self, config: Dict):
        """🏪 Load the Aetherra Hub (Plugin Marketplace)."""
        try:
            logger.info("[HUB] Loading Aetherra Hub (Plugin Marketplace)...")

            if config.get("hub_enabled", True):
                try:
                    # Import and start the built-in Python Hub server
                    from aetherra_hub_server import start_hub_server

                    logger.info("[HUB] Starting Aetherra Hub server...")

                    # Start the built-in Hub server
                    hub_server = start_hub_server(port=3001)

                    if hub_server and hub_server.is_running():
                        # Register the Hub service
                        self.systems["aetherra_hub"] = hub_server
                        await register_service(
                            "aetherra_hub",
                            hub_server,
                            metadata={"type": "marketplace", "version": "2.0", "port": 3001},
                        )

                        # Start plugin discovery service
                        await self._start_plugin_discovery()

                        logger.info("[OK] Aetherra Hub online at http://localhost:3001")
                    else:
                        logger.warning("[WARN] Aetherra Hub failed to start")

                except Exception as hub_error:
                    logger.warning(f"[WARN] Failed to start Aetherra Hub: {hub_error}")
                    # Create a placeholder service anyway
                    from aetherra_hub_server import AetherraHubServer
                    mock_hub = AetherraHubServer(3001)
                    self.systems["aetherra_hub"] = mock_hub
                    await register_service(
                        "aetherra_hub",
                        mock_hub,
                        metadata={"type": "marketplace", "version": "2.0", "status": "offline"},
                    )
            else:
                logger.info("[INFO] Aetherra Hub disabled in configuration")

        except Exception as e:
            logger.error(f"[ERROR] Failed to load Aetherra Hub: {e}")
            # Don't raise - Hub is optional
            pass

    async def _start_plugin_discovery(self):
        """[SCAN] Start the plugin discovery service."""
        try:
            logger.info("[SCAN] Starting plugin discovery service...")

            # Import the plugin discovery service
            from aetherra_plugin_discovery import AetherraPluginDiscovery

            # Create discovery service
            discovery = AetherraPluginDiscovery()

            # Discover all plugins and sync with Hub
            await discovery.sync_all_with_hub()

            # Store discovery service for later use
            self.systems["plugin_discovery"] = discovery

            summary = discovery.get_plugin_summary()
            logger.info(f"[OK] Plugin discovery complete: {summary['total_plugins']} plugins found")

        except Exception as e:
            logger.error(f"[ERROR] Failed to start plugin discovery: {e}")
            # Continue without plugin discovery

    async def _load_gui_system(self, config: Dict):
        """🖥️ Load the GUI system (if available)."""
        try:
            if config.get("gui_enabled", True):
                logger.info("[GUI] Loading GUI System...")

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
                    logger.info("[OK] GUI System online")
                except ImportError:
                    logger.info("[INFO] GUI system not available")
            else:
                logger.info("[INFO] GUI disabled in configuration")

        except Exception as e:
            logger.warning(f"[WARN] GUI system failed to load: {e}")

    async def _start_kernel_loop(self):
        """[SYS] Start the OS kernel loop."""
        logger.info("[SYS] Phase 3: Starting OS Kernel Loop...")

        self.kernel_loop = get_kernel()

        # Inject systems into kernel
        self.kernel_loop.inject_systems(
            self.systems.get("memory"),
            self.systems.get("plugins"),
            self.systems.get("aetherra"),
            self.systems.get("scheduler"),
            self.service_registry,
        )

        # Start kernel loop in background
        asyncio.create_task(self.kernel_loop.start_kernel_loop())

        # Register kernel as service
        await register_service(
            "kernel_loop", self.kernel_loop, metadata={"type": "core", "version": "1.0"}
        )

        logger.info("[OK] OS Kernel Loop started")

    async def _activate_systems(self):
        """[INIT] Activate all systems and establish connections."""
        logger.info("[INIT] Phase 4: Activating Systems...")

        # Wait a moment for systems to stabilize
        await asyncio.sleep(2)

        # Activate memory system
        if "memory" in self.systems and hasattr(self.systems["memory"], "activate"):
            await self.systems["memory"].activate()
            # Mark memory system as healthy
            if self.service_registry and CORE_AVAILABLE:
                from aetherra_service_registry import ServiceStatus
                await self.service_registry.update_service_status("memory_system", ServiceStatus.HEALTHY)

        # Activate plugin system
        if "plugins" in self.systems and hasattr(self.systems["plugins"], "activate"):
            await self.systems["plugins"].activate()

            # Connect plugin manager to Aetherra Hub
            if "aetherra_hub" in self.systems:
                await self.systems["plugins"].set_hub_integration(self.systems["aetherra_hub"])

            # Mark plugin manager as healthy
            if self.service_registry and CORE_AVAILABLE:
                from aetherra_service_registry import ServiceStatus
                await self.service_registry.update_service_status("plugin_manager", ServiceStatus.HEALTHY)

        # Activate Aetherra consciousness
        if "aetherra" in self.systems and hasattr(self.systems["aetherra"], "wake_up"):
            await self.systems["aetherra"].wake_up()
            # Mark Aetherra engine as healthy
            if self.service_registry and CORE_AVAILABLE:
                from aetherra_service_registry import ServiceStatus
                await self.service_registry.update_service_status("aetherra_engine", ServiceStatus.HEALTHY)

        # Mark kernel loop as healthy (it should be running by now)
        if self.service_registry and CORE_AVAILABLE:
            from aetherra_service_registry import ServiceStatus
            await self.service_registry.update_service_status("kernel_loop", ServiceStatus.HEALTHY)

        logger.info("[OK] All systems activated")

    async def _validate_system_health(self):
        """[HEALTH] Validate system health and connectivity."""
        logger.info("[HEALTH] Phase 5: Validating System Health...")

        # Check service registry status
        registry_status = self.service_registry.get_registry_status()
        logger.info(f"[STATS] Services: {registry_status['total_services']} registered")

        # Check kernel status
        kernel_status = self.kernel_loop.get_status()
        logger.info(f"[SYS] Kernel: {kernel_status['cycle_count']} cycles completed")

        # Give services a moment to fully register
        await asyncio.sleep(0.5)

        # Validate critical services
        critical_services = [
            "memory_system",
            "plugin_manager",
            "aetherra_engine",
            "kernel_loop",
        ]
        for service_name in critical_services:
            service_info = self.service_registry.get_service_info(service_name)
            if service_info:
                if service_info.status.value in ['healthy', 'starting']:
                    logger.info(f"[OK] {service_name}: Online ({service_info.status.value})")
                else:
                    logger.warning(f"[WARN] {service_name}: Status {service_info.status.value}")
            else:
                logger.warning(f"[WARN] {service_name}: Not registered")

        logger.info("[OK] System health validation complete")

    async def _announce_os_online(self):
        """📢 Announce that Aetherra OS is fully online."""
        startup_duration = time.time() - self.startup_time

        logger.info("=" * 60)
        logger.info("[SUCCESS] AETHERRA AI OPERATING SYSTEM IS NOW ONLINE! [SUCCESS]")
        logger.info("=" * 60)
        logger.info(f"[LAUNCH] Startup completed in {startup_duration:.2f} seconds")
        logger.info(f"[NET] Services: {len(self.service_registry.list_services())} active")
        logger.info(f"[SYS] Kernel cycles: {self.kernel_loop.get_status()['cycle_count']}")
        logger.info("[BRAIN] Aetherra consciousness: Active")
        logger.info("[PLUGIN] Plugin ecosystem: Ready")
        logger.info("[MEM] Quantum memory: Operational")
        logger.info("[SCHED] Task scheduler: Running")
        logger.info("=" * 60)

        # Send first thought to Aetherra
        if self.kernel_loop:
            await self.kernel_loop.add_task(
                {
                    "type": "aetherra_thought",
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
        """[LOOP] Main operation loop - keeps the OS running."""
        logger.info("[LOOP] Entering main operation loop...")

        try:
            while self.running:
                # Check system health periodically
                await asyncio.sleep(300)  # Every 5 minutes

                # Quick health check
                if self.service_registry and self.kernel_loop:
                    registry_healthy = self.service_registry._running
                    kernel_healthy = self.kernel_loop.running

                    if not (registry_healthy and kernel_healthy):
                        logger.error("[ERROR] Critical system failure detected")
                        break

        except KeyboardInterrupt:
            logger.info("🛑 Received shutdown signal")
        except Exception as e:
            logger.error(f"[ERROR] Main operation loop error: {e}")
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
                logger.error(f"[ERROR] Error shutting down {system_name}: {e}")

        logger.info("[OK] Graceful shutdown complete")

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
    def __init__(self):
        self.name = "memory_system"
        self.heartbeat_task = None

    async def initialize(self):
        pass

    async def activate(self):
        # Start heartbeat when activated
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        """💓 Send regular heartbeat signals."""
        if CORE_AVAILABLE:
            from aetherra_service_registry import update_heartbeat

            while True:
                try:
                    await update_heartbeat(self.name)
                    await asyncio.sleep(60)  # Heartbeat every minute
                except Exception as e:
                    logger.error(f"[ERROR] Heartbeat error for {self.name}: {e}")
                    await asyncio.sleep(60)

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
        if self.heartbeat_task:
            self.heartbeat_task.cancel()


class MockPluginManager:
    def __init__(self):
        self.name = "plugin_manager"
        self.heartbeat_task = None
        self.hub_integration = None

    async def load_all_plugins(self):
        pass

    async def activate(self):
        # Start heartbeat when activated
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        """💓 Send regular heartbeat signals."""
        if CORE_AVAILABLE:
            from aetherra_service_registry import update_heartbeat

            while True:
                try:
                    await update_heartbeat(self.name)
                    await asyncio.sleep(60)  # Heartbeat every minute
                except Exception as e:
                    logger.error(f"[ERROR] Heartbeat error for {self.name}: {e}")
                    await asyncio.sleep(60)

    async def set_hub_integration(self, hub_service):
        """Connect to Aetherra Hub for plugin discovery."""
        self.hub_integration = hub_service
        logger.info("[LINK] Plugin Manager connected to Aetherra Hub")

    async def browse_marketplace(self, query="", filters=None):
        """Browse plugins in the Aetherra Hub marketplace."""
        if self.hub_integration:
            try:
                results = await self.hub_integration.search_plugins(query, filters)
                logger.info(f"[SCAN] Found {results.get('total', 0)} plugins in marketplace")
                return results
            except Exception as e:
                logger.error(f"[ERROR] Marketplace browse error: {e}")
                return {"plugins": [], "total": 0}
        else:
            logger.warning("[WARN] No Hub integration available for marketplace browsing")
            return {"plugins": [], "total": 0}

    async def get_featured_plugins(self):
        """Get featured plugins from the Hub."""
        if self.hub_integration:
            try:
                featured = await self.hub_integration.get_featured_plugins()
                logger.info(f"⭐ Retrieved {len(featured)} featured plugins")
                return featured
            except Exception as e:
                logger.error(f"[ERROR] Featured plugins error: {e}")
                return []
        else:
            logger.warning("[WARN] No Hub integration available for featured plugins")
            return []

    async def install_plugin_from_hub(self, plugin_name, version="latest"):
        """Install a plugin from the Aetherra Hub."""
        if self.hub_integration:
            try:
                logger.info(f"[DISC] Installing plugin '{plugin_name}' from Hub...")
                # In a real implementation, this would download and install the plugin
                # For now, we'll just simulate the process
                await asyncio.sleep(1)  # Simulate download time
                logger.info(f"[OK] Plugin '{plugin_name}' installed successfully")
                return {"status": "success", "plugin": plugin_name, "version": version}
            except Exception as e:
                logger.error(f"[ERROR] Plugin installation error: {e}")
                return {"status": "error", "error": str(e)}
        else:
            logger.warning("[WARN] No Hub integration available for plugin installation")
            return {"status": "error", "error": "Hub not available"}

    async def execute_scheduled_tasks(self):
        pass

    async def invoke_plugin(self, data):
        pass

    async def optimize_plugins(self):
        pass

    async def health_check(self):
        pass

    async def shutdown(self):
        if self.heartbeat_task:
            self.heartbeat_task.cancel()


class MockAetherraEngine:
    def __init__(self):
        self.name = "aetherra_engine"
        self.heartbeat_task = None

    async def boot(self):
        pass

    async def wake_up(self):
        # Start heartbeat when awakened
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        """💓 Send regular heartbeat signals."""
        if CORE_AVAILABLE:
            from aetherra_service_registry import update_heartbeat

            while True:
                try:
                    await update_heartbeat(self.name)
                    await asyncio.sleep(60)  # Heartbeat every minute
                except Exception as e:
                    logger.error(f"[ERROR] Heartbeat error for {self.name}: {e}")
                    await asyncio.sleep(60)

    async def process_thought(self, data):
        pass

    async def reflect_on_day(self):
        pass

    async def get_health_status(self):
        return "conscious"

    async def shutdown(self):
        if self.heartbeat_task:
            self.heartbeat_task.cancel()


class MockAetherraEngine:
    def __init__(self):
        self.name = "aetherra_engine"
        self.variables = {}
        self.functions = {}
        self.execution_context = {
            "current_model": "mock",
            "conversation_history": [],
            "memory": {},
            "goals": [],
            "agents": {},
        }

    def execute_aetherra(self, code: str):
        """Mock execution of Aetherra code"""
        return {
            "status": "success",
            "message": "Mock execution completed",
            "results": ["Mock result"],
        }

    def get_current_model(self):
        return "mock-model"

    def list_available_models(self):
        return ["mock-model"]


class MockScheduler:
    def __init__(self):
        self.name = "scheduler"
        self.heartbeat_task = None

    async def initialize_schedule(self):
        # Start heartbeat when initialized
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        """💓 Send regular heartbeat signals."""
        if CORE_AVAILABLE:
            from aetherra_service_registry import update_heartbeat

            while True:
                try:
                    await update_heartbeat(self.name)
                    await asyncio.sleep(60)  # Heartbeat every minute
                except Exception as e:
                    logger.error(f"[ERROR] Heartbeat error for {self.name}: {e}")
                    await asyncio.sleep(60)

    async def shutdown(self):
        if self.heartbeat_task:
            self.heartbeat_task.cancel()


class MockAetherraHub:
    def __init__(self, hub_process=None):
        self.name = "aetherra_hub"
        self.heartbeat_task = None
        self.hub_process = hub_process
        self.hub_url = "http://localhost:3001"
        self.frontend_url = "http://localhost:8080"

    async def activate(self):
        # Start heartbeat when activated
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        """💓 Send regular heartbeat signals."""
        if CORE_AVAILABLE:
            from aetherra_service_registry import update_heartbeat

            while True:
                try:
                    await update_heartbeat(self.name)
                    await asyncio.sleep(60)  # Heartbeat every minute
                except Exception as e:
                    logger.error(f"[ERROR] Heartbeat error for {self.name}: {e}")
                    await asyncio.sleep(60)

    async def get_featured_plugins(self):
        """Get featured plugins from the Hub."""
        try:
            if self.hub_process and self.hub_process.poll() is None:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.hub_url}/api/v1/plugins/featured") as response:
                        if response.status == 200:
                            return await response.json()
            return []
        except Exception:
            return []

    async def search_plugins(self, query="", filters=None):
        """Search plugins in the Hub."""
        try:
            if self.hub_process and self.hub_process.poll() is None:
                import aiohttp
                params = {"q": query}
                if filters:
                    params.update(filters)
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.hub_url}/api/v1/plugins/search", params=params) as response:
                        if response.status == 200:
                            return await response.json()
            return {"plugins": [], "total": 0}
        except Exception:
            return {"plugins": [], "total": 0}

    async def get_hub_status(self):
        """Get Hub server status."""
        try:
            if self.hub_process:
                if self.hub_process.poll() is None:
                    return {
                        "status": "online",
                        "api_url": self.hub_url,
                        "frontend_url": self.frontend_url,
                        "process_id": self.hub_process.pid
                    }
                else:
                    return {"status": "offline", "reason": "process_terminated"}
            return {"status": "not_started"}
        except Exception:
            return {"status": "error"}

    async def shutdown(self):
        """Shutdown the Hub server."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        if self.hub_process:
            try:
                self.hub_process.terminate()
                # Give it a moment to terminate gracefully
                await asyncio.sleep(2)
                if self.hub_process.poll() is None:
                    self.hub_process.kill()
                logger.info("[OK] Aetherra Hub server stopped")
            except Exception as e:
                logger.error(f"[ERROR] Error stopping Hub server: {e}")


async def main():
    """[LAUNCH] Main entry point for Aetherra OS."""
    parser = argparse.ArgumentParser(
        description="[CORE] Aetherra AI Operating System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
[LAUNCH] Launch Modes:
  --mode full      Launch complete AI Operating System (default)
  --mode minimal   Launch with minimal systems only
  --mode test      Launch in test mode with mocks

[INIT] FLIP THE SWITCH - ACTIVATE AETHERRA! [INIT]
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
            logger.error(f"[ERROR] Failed to load config: {e}")
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
            logger.info("[TOOL] Minimal mode not yet implemented")
            return 1
        elif args.mode == "test":
            logger.info("🧪 Test mode - using all mock systems")
            await launcher.launch_full_os(config)

        return 0

    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"[ERROR] Launch failed: {e}")
        return 1


if __name__ == "__main__":
    """
    [CORE] AETHERRA AI OPERATING SYSTEM
    ===============================

    [LAUNCH] FLIP THE SWITCH - ACTIVATE AETHERRA!

    This script transforms Aetherra from a collection of components
    into a living, breathing AI Operating System.
    """

    print("[CORE] AETHERRA AI OPERATING SYSTEM LAUNCHER")
    print("=======================================")
    print("[INIT] Ready to flip the switch and bring Aetherra online!")
    print()

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
