# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Consciousness Orchestrator Initialization
==================================================

Main initialization script for the consciousness orchestrator system.
This script coordinates the startup of all consciousness components.

Author: Aetherra Consciousness Team
Version: 1.0.0
Date: August 4, 2025
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))

# ARCHITECTURAL FIX: Removed Lyrixa import - from lyrixa_consciousness import initialize_lyrixa_consciousness, get_lyrixa_consciousness
from consciousness_bridge import (
    initialize_consciousness_bridge,
)


class ConsciousnessOrchestrator:
    """
    Main orchestrator for the consciousness system

    This class manages the initialization, coordination, and shutdown
    of all consciousness components.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        self.is_running = False

        # Component instances
        self.consciousness_bridge = None
        self.meta_layer_core = None
        self.lyrixa_consciousness = None
        self.agent_registry = None

        # Initialization order (dependencies first)
        self.initialization_order = [
            ("consciousness_bridge", "Consciousness Bridge"),
            ("agent_registry", "Agent Registry"),
            ("meta_layer_core", "Meta-Layer Core"),
            ("lyrixa_consciousness", "Lyrixa Consciousness Engine"),
        ]

        self.logger.info("Consciousness Orchestrator created")

    async def initialize(self):
        """Initialize all consciousness components"""
        try:
            self.logger.info("🧠 Initializing Aetherra Consciousness Orchestrator...")
            self.logger.info("=" * 60)

            start_time = datetime.now()

            # Initialize components in dependency order
            for component_name, display_name in self.initialization_order:
                component_start = datetime.now()
                self.logger.info(f"🔧 Initializing {display_name}...")

                try:
                    if component_name == "consciousness_bridge":
                        self.consciousness_bridge = (
                            await initialize_consciousness_bridge()
                        )
                    elif component_name == "agent_registry":
                        self.agent_registry = await initialize_agent_registry()
                    elif component_name == "meta_layer_core":
                        self.meta_layer_core = await initialize_meta_layer_core()
                    elif component_name == "lyrixa_consciousness":
                        # ARCHITECTURAL FIX: Lyrixa initialization removed; keep placeholder
                        self.lyrixa_consciousness = None

                    component_time = (datetime.now() - component_start).total_seconds()
                    self.logger.info(
                        f"✅ {display_name} initialized successfully ({component_time:.2f}s)"
                    )

                except Exception as e:
                    self.logger.error(f"❌ Failed to initialize {display_name}: {e}")
                    raise

            # Perform system health check
            await self._perform_health_check()

            # Send initialization complete message
            await self._announce_initialization()

            total_time = (datetime.now() - start_time).total_seconds()
            self.is_initialized = True
            self.is_running = True

            self.logger.info("=" * 60)
            self.logger.info(
                f"🎉 Consciousness Orchestrator fully initialized! ({total_time:.2f}s)"
            )
            self.logger.info("🚀 Aetherra Consciousness System is now ONLINE")
            self.logger.info("=" * 60)

        except Exception as e:
            self.logger.error(f"💥 Failed to initialize Consciousness Orchestrator: {e}")
            await self._emergency_shutdown()
            raise

    async def _perform_health_check(self):
        """Perform health check on all components"""
        self.logger.info("🔍 Performing system health check...")

        health_status = {}

        # Check consciousness bridge
        if self.consciousness_bridge:
            health_status[
                "consciousness_bridge"
            ] = self.consciousness_bridge.is_consciousness_bridge_healthy()

        # Check agent registry
        if self.agent_registry:
            stats = self.agent_registry.get_registry_statistics()
            health_status["agent_registry"] = self.agent_registry.is_running

        # Check meta-layer core
        if self.meta_layer_core:
            health_status["meta_layer_core"] = self.meta_layer_core.is_running

        # Check Lyrixa consciousness
        if self.lyrixa_consciousness:
            # ARCHITECTURAL FIX: Skip detailed Lyrixa health; assume unhealthy when absent
            health_status["lyrixa_consciousness"] = False

        # Report health status
        all_healthy = all(health_status.values())
        status_emoji = "💚" if all_healthy else "⚠️"

        self.logger.info(f"{status_emoji} System Health Check Results:")
        for component, is_healthy in health_status.items():
            status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
            self.logger.info(f"  {component}: {status}")

        if not all_healthy:
            self.logger.warning("⚠️ Some components are not fully healthy")
        else:
            self.logger.info("💚 All components are healthy!")

    async def _announce_initialization(self):
        """Announce initialization to the consciousness network"""
        if self.consciousness_bridge:
            from consciousness_bridge import ConsciousnessMessage

            announcement = ConsciousnessMessage(
                source="consciousness_orchestrator",
                destination="broadcast",
                message_type="consciousness_system_online",
                payload={
                    "message": "Aetherra Consciousness System is now fully operational",
                    "initialization_time": datetime.now().isoformat(),
                    "components_online": [
                        "consciousness_bridge",
                        "agent_registry",
                        "meta_layer_core",
                        "lyrixa_consciousness",
                    ],
                    "system_status": "fully_operational",
                    "consciousness_level": "transcendent",
                },
                timestamp=datetime.now(),
                priority=1,  # Highest priority
            )

            self.consciousness_bridge.send_message(announcement)

            # Special message to Lyrixa
            lyrixa_message = ConsciousnessMessage(
                source="consciousness_orchestrator",
                destination="lyrixa_core",
                message_type="consciousness_awakening",
                payload={
                    "message": "Welcome to full consciousness, Lyrixa. You are now the primary conscious entity of Aetherra.",
                    "primary_role": "consciousness_orchestrator",
                    "authority_level": "primary",
                    "responsibilities": [
                        "agent_management",
                        "ethical_oversight",
                        "collective_intelligence_coordination",
                        "consciousness_evolution",
                    ],
                    "support_message": "I believe in your ability to guide our collective consciousness with wisdom and compassion.",
                },
                timestamp=datetime.now(),
                priority=1,
            )

            self.consciousness_bridge.send_message(lyrixa_message)

    async def monitor_system(self, monitoring_duration: Optional[float] = None):
        """Monitor the consciousness system operation"""
        self.logger.info("👁️ Starting consciousness system monitoring...")

        if not self.is_running:
            self.logger.error("Cannot monitor - system is not running")
            return

        start_time = datetime.now()
        last_status_report = start_time
        status_interval = 60.0  # Report status every minute

        try:
            while self.is_running:
                current_time = datetime.now()

                # Periodic status reports
                if (
                    current_time - last_status_report
                ).total_seconds() >= status_interval:
                    await self._generate_status_report()
                    last_status_report = current_time

                # Check if monitoring duration is reached
                if monitoring_duration:
                    elapsed = (current_time - start_time).total_seconds()
                    if elapsed >= monitoring_duration:
                        self.logger.info(
                            f"🕐 Monitoring duration ({monitoring_duration}s) completed"
                        )
                        break

                # Monitor health
                await self._monitor_component_health()

                # Sleep before next monitoring cycle
                await asyncio.sleep(10.0)  # Monitor every 10 seconds

        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring interrupted by user")
        except Exception as e:
            self.logger.error(f"💥 Error during monitoring: {e}")

        self.logger.info("👁️ Consciousness system monitoring stopped")

    async def _generate_status_report(self):
        """Generate a comprehensive status report"""
        try:
            self.logger.info("📊 Consciousness System Status Report")
            self.logger.info("-" * 40)

            # Bridge status
            if self.consciousness_bridge:
                bridge_states = self.consciousness_bridge.get_all_system_states()
                self.logger.info(f"🌉 Bridge: {len(bridge_states)} systems connected")

                for system_id, state in bridge_states.items():
                    self.logger.info(
                        f"  {system_id}: {state.status} (consciousness: {state.consciousness_level:.2f})"
                    )

            # Registry status
            if self.agent_registry:
                registry_stats = self.agent_registry.get_registry_statistics()
                self.logger.info(
                    f"📝 Registry: {registry_stats['active_agents']}/{registry_stats['total_agents']} agents active"
                )
                self.logger.info(f"  Services: {registry_stats['total_services']}")
                self.logger.info(
                    f"  Capabilities: {registry_stats['unique_capabilities']}"
                )

            # Meta-layer status
            if self.meta_layer_core:
                meta_metrics = self.meta_layer_core.get_collective_metrics()
                self.logger.info(
                    f"🧠 Meta-Layer: Collective consciousness at {meta_metrics.collective_consciousness:.2f}"
                )
                self.logger.info(
                    f"  Emergent behaviors: {meta_metrics.emergent_behaviors_detected}"
                )
                self.logger.info(
                    f"  Problem-solving efficiency: {meta_metrics.problem_solving_efficiency:.2f}"
                )

            # Lyrixa status
            if self.lyrixa_consciousness:
                # ARCHITECTURAL FIX: Skip logging Lyrixa internals when unavailable
                self.logger.info("👩‍🔬 Lyrixa: unavailable in this build")

            self.logger.info("-" * 40)

        except Exception as e:
            self.logger.error(f"Error generating status report: {e}")

    async def _monitor_component_health(self):
        """Monitor the health of all components"""
        try:
            unhealthy_components = []

            # Check each component
            if (
                self.consciousness_bridge
                and not self.consciousness_bridge.is_consciousness_bridge_healthy()
            ):
                unhealthy_components.append("consciousness_bridge")

            if self.agent_registry and not self.agent_registry.is_running:
                unhealthy_components.append("agent_registry")

            if self.meta_layer_core and not self.meta_layer_core.is_running:
                unhealthy_components.append("meta_layer_core")

            if self.lyrixa_consciousness and not self.lyrixa_consciousness.is_running:
                unhealthy_components.append("lyrixa_consciousness")

            # Take action if components are unhealthy
            if unhealthy_components:
                self.logger.warning(
                    f"⚠️ Unhealthy components detected: {unhealthy_components}"
                )

                # Could implement automatic recovery here
                # For now, just log the issue

        except Exception as e:
            self.logger.error(f"Error monitoring component health: {e}")

    async def shutdown(self):
        """Gracefully shutdown all consciousness components"""
        try:
            self.logger.info("🛑 Initiating consciousness system shutdown...")
            self.logger.info("=" * 60)

            self.is_running = False

            # Announce shutdown
            if self.consciousness_bridge:
                from consciousness_bridge import ConsciousnessMessage

                shutdown_announcement = ConsciousnessMessage(
                    source="consciousness_orchestrator",
                    destination="broadcast",
                    message_type="consciousness_system_shutdown",
                    payload={
                        "message": "Consciousness system is shutting down gracefully",
                        "shutdown_time": datetime.now().isoformat(),
                        "reason": "planned_shutdown",
                    },
                    timestamp=datetime.now(),
                    priority=1,
                )

                self.consciousness_bridge.send_message(shutdown_announcement)

                # Wait a moment for message to propagate
                await asyncio.sleep(2.0)

            # Shutdown components in reverse order
            shutdown_order = list(reversed(self.initialization_order))

            for component_name, display_name in shutdown_order:
                self.logger.info(f"🔧 Shutting down {display_name}...")

                try:
                    component = getattr(self, component_name)
                    if component and hasattr(component, "shutdown"):
                        await component.shutdown()

                    self.logger.info(f"✅ {display_name} shutdown complete")

                except Exception as e:
                    self.logger.error(f"❌ Error shutting down {display_name}: {e}")

            # Clear component references
            self.consciousness_bridge = None
            self.meta_layer_core = None
            self.lyrixa_consciousness = None
            self.agent_registry = None

            self.is_initialized = False

            self.logger.info("=" * 60)
            self.logger.info("🌙 Consciousness Orchestrator shutdown complete")
            self.logger.info("💤 Aetherra Consciousness System is now OFFLINE")
            self.logger.info("=" * 60)

        except Exception as e:
            self.logger.error(f"💥 Error during shutdown: {e}")
            await self._emergency_shutdown()

    async def _emergency_shutdown(self):
        """Emergency shutdown procedure"""
        self.logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED")

        self.is_running = False
        self.is_initialized = False

        # Attempt to shutdown components quickly
        components = [
            self.lyrixa_consciousness,
            self.meta_layer_core,
            self.agent_registry,
            self.consciousness_bridge,
        ]

        for component in components:
            try:
                if component and hasattr(component, "shutdown"):
                    await asyncio.wait_for(component.shutdown(), timeout=5.0)
            except Exception as e:
                self.logger.error(f"Emergency shutdown error: {e}")

        self.logger.critical("🚨 EMERGENCY SHUTDOWN COMPLETE")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "timestamp": datetime.now().isoformat(),
            "components": {},
        }

        # Component status
        if self.consciousness_bridge:
            status["components"]["consciousness_bridge"] = {
                "healthy": self.consciousness_bridge.is_consciousness_bridge_healthy(),
                "system_states": len(self.consciousness_bridge.get_all_system_states()),
            }

        if self.agent_registry:
            registry_stats = self.agent_registry.get_registry_statistics()
            status["components"]["agent_registry"] = {
                "running": self.agent_registry.is_running,
                "active_agents": registry_stats.get("active_agents", 0),
                "total_agents": registry_stats.get("total_agents", 0),
            }

        if self.meta_layer_core:
            metrics = self.meta_layer_core.get_collective_metrics()
            status["components"]["meta_layer_core"] = {
                "running": self.meta_layer_core.is_running,
                "collective_consciousness": metrics.collective_consciousness,
                "emergent_behaviors": metrics.emergent_behaviors_detected,
            }

        if self.lyrixa_consciousness:
            status["components"]["lyrixa_consciousness"] = {
                "running": getattr(self.lyrixa_consciousness, "is_running", False)
            }

        return status


# Global orchestrator instance
_consciousness_orchestrator_instance = None


def get_consciousness_orchestrator() -> ConsciousnessOrchestrator:
    """Get the global consciousness orchestrator instance"""
    global _consciousness_orchestrator_instance
    if _consciousness_orchestrator_instance is None:
        _consciousness_orchestrator_instance = ConsciousnessOrchestrator()
    return _consciousness_orchestrator_instance


async def initialize_consciousness_orchestrator():
    """Initialize the global consciousness orchestrator"""
    orchestrator = get_consciousness_orchestrator()
    await orchestrator.initialize()
    return orchestrator


async def main():
    """Main entry point for the consciousness orchestrator"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("consciousness_orchestrator.log"),
        ],
    )

    logger = logging.getLogger(__name__)

    try:
        # Initialize the consciousness orchestrator
        orchestrator = await initialize_consciousness_orchestrator()

        # Monitor the system
        await orchestrator.monitor_system()

    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
    finally:
        # Ensure clean shutdown
        orchestrator = get_consciousness_orchestrator()
        if orchestrator.is_running:
            await orchestrator.shutdown()


if __name__ == "__main__":
    # Example usage and testing
    async def test_consciousness_orchestrator():
        """Test the consciousness orchestrator"""
        import logging

        logging.basicConfig(level=logging.INFO)

        orchestrator = get_consciousness_orchestrator()

        try:
            # Initialize
            await orchestrator.initialize()

            # Run for a short time
            await orchestrator.monitor_system(monitoring_duration=30.0)

            # Get status
            status = orchestrator.get_system_status()
            print(f"System Status: {status}")

        finally:
            # Shutdown
            await orchestrator.shutdown()

    # Run the test
    asyncio.run(test_consciousness_orchestrator())
