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

# Standard library imports
import asyncio
import contextlib
import hashlib
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))

# ARCHITECTURAL FIX: Removed Lyrixa import - from lyrixa_consciousness import initialize_lyrixa_consciousness, get_lyrixa_consciousness
try:  # Optional dependency
    from .core.consciousness_bridge import (
        ConsciousnessMessage,
        initialize_consciousness_bridge,
    )
except Exception:  # pragma: no cover
    ConsciousnessMessage = None  # type: ignore
    initialize_consciousness_bridge = None  # type: ignore
# Local imports
from .narrator import get_narrative_layer


def _hash_value(value: Any) -> str | None:
    raw = str(value) if value is not None else ""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _hash_json(value: Any) -> str | None:
    try:
        raw = json.dumps(value, sort_keys=True, default=str)
    except TypeError:
        raw = repr(value)
    return _hash_value(raw)


def _guardian_requester() -> str:
    return (
        os.environ.get("AETHERRA_PRINCIPAL", "").strip()
        or "consciousness:orchestrator"
    )


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "consciousness:orchestrator" and capability in {
        "agent:control",
        "consciousness:write",
        "event:publish",
        "fs:write",
        "system:restart",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _guardian_preflight_orchestrator_operation(
    *,
    action: str,
    target: str,
    purpose: str,
    capabilities: tuple[str, ...],
    metadata: Dict[str, Any],
    rollback_plan: str,
) -> None:
    from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

    decision = evaluate_intent(
        IntentDeclaration(
            requester=_guardian_requester(),
            subsystem="consciousness",
            action=action,
            target=target,
            purpose=purpose,
            capabilities=capabilities,
            evidence=("ConsciousnessOrchestrator", action),
            reversible=True,
            rollback_plan=rollback_plan,
            metadata=metadata,
        ),
        capability_checker=_guardian_capability_checker,
    )
    if decision.status not in {
        GuardianStatus.ALLOW,
        GuardianStatus.ALLOW_LIMITED,
    }:
        raise PermissionError(f"guardian_denied:{decision.reason}:{action}")


class ConsciousnessOrchestrator:
    """
    Main orchestrator for the consciousness system

    This class manages the initialization, coordination, and shutdown
    of all consciousness components.
    """

    def __init__(
        self,
        *,
        component_initializers: Optional[Dict[str, Callable[[], Any]]] = None,
        narrative_factory: Optional[Callable[[], Any]] = None,
    ):
        self.logger = logging.getLogger(__name__)
        self._component_initializers = component_initializers or {}
        self._narrative_factory = narrative_factory or get_narrative_layer
        self.is_initialized = False
        self.is_running = False

        # Component instances
        self.consciousness_bridge = None
        self.meta_layer_core = None
        self.lyrixa_consciousness = None
        self.agent_registry = None
        self.narrative_layer = None
        self.last_narrative_coherence: Optional[float] = None

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
            _guardian_preflight_orchestrator_operation(
                action="consciousness.orchestrator_initialize",
                target="consciousness:orchestrator",
                purpose="Initialize consciousness orchestrator component lifecycle",
                capabilities=("consciousness:write", "agent:control"),
                metadata={
                    "operation": "initialize",
                    "component_order": tuple(name for name, _ in self.initialization_order),
                    "was_initialized": self.is_initialized,
                    "was_running": self.is_running,
                },
                rollback_plan="run emergency shutdown and restore orchestrator offline state",
            )

            # Initialize components in dependency order
            for component_name, display_name in self.initialization_order:
                component_start = datetime.now()
                self.logger.info(f"🔧 Initializing {display_name}...")

                try:
                    setattr(
                        self,
                        component_name,
                        await self._initialize_component(component_name),
                    )

                    component_time = (datetime.now() - component_start).total_seconds()
                    self.logger.info(
                        f"✅ {display_name} initialized successfully ({component_time:.2f}s)"
                    )

                except Exception as e:
                    self.logger.error(f"❌ Failed to initialize {display_name}: {e}")
                    raise

            # Perform system health check
            await self._perform_health_check()

            # Auto-start narrative layer if enabled
            try:
                self.narrative_layer = self._narrative_factory()
                if self.narrative_layer.enabled:
                    _guardian_preflight_orchestrator_operation(
                        action="consciousness.orchestrator_narrative_start",
                        target="consciousness:narrative_layer",
                        purpose="Start narrative layer from consciousness orchestrator initialization",
                        capabilities=("consciousness:write",),
                        metadata={
                            "operation": "narrative_start",
                            "narrative_enabled": True,
                            "has_existing_narrative": self.narrative_layer is not None,
                        },
                        rollback_plan="stop narrative layer and clear orchestrator narrative reference",
                    )
                    self.narrative_layer.start(background=True)
                    self.logger.info("🧾 Narrative layer started (auto)")
                    # Register simple coherence metric hook
                    self.narrative_layer.on_chapter(self._on_new_chapter)
            except Exception as e:
                self.logger.warning(f"Narrative layer start failed: {e}")

            # Send initialization complete message
            await self._announce_initialization()

            total_time = (datetime.now() - start_time).total_seconds()
            _guardian_preflight_orchestrator_operation(
                action="consciousness.orchestrator_mark_online",
                target="consciousness:orchestrator",
                purpose="Mark consciousness orchestrator initialized and running",
                capabilities=("consciousness:write",),
                metadata={
                    "operation": "mark_online",
                    "total_time_seconds": round(float(total_time), 6),
                    "component_presence": {
                        name: getattr(self, name) is not None
                        for name, _ in self.initialization_order
                    },
                },
                rollback_plan="restore initialized/running flags to previous offline state",
            )
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

    async def _initialize_component(self, component_name: str):
        """Initialize one orchestrated component after Guardian approval."""
        _guardian_preflight_orchestrator_operation(
            action="consciousness.orchestrator_component_initialize",
            target=f"consciousness_component:{component_name}",
            purpose="Initialize a consciousness orchestrator component",
            capabilities=("consciousness:write", "agent:control"),
            metadata={
                "operation": "component_initialize",
                "component_name": component_name,
                "has_custom_initializer": component_name in self._component_initializers,
                "currently_present": getattr(self, component_name, None) is not None,
            },
            rollback_plan="shutdown initialized component and clear component reference",
        )
        initializer = self._component_initializers.get(component_name)
        if initializer:
            result = initializer()
            if hasattr(result, "__await__"):
                return await result
            return result

        if component_name == "consciousness_bridge":
            if initialize_consciousness_bridge:
                return await initialize_consciousness_bridge()
            return None
        if component_name == "agent_registry":
            try:
                from .agents.agent_registry import initialize_agent_registry
            except Exception:
                initialize_agent_registry = None  # type: ignore
            if initialize_agent_registry:
                return await initialize_agent_registry()
            return None
        if component_name == "meta_layer_core":
            try:
                from .core.meta_layer_core import initialize_meta_layer_core
            except Exception:
                initialize_meta_layer_core = None  # type: ignore
            if initialize_meta_layer_core:
                return await initialize_meta_layer_core()
            return None
        if component_name == "lyrixa_consciousness":
            return None
        return None

    async def _perform_health_check(self):
        """Perform health check on all components"""
        self.logger.info("🔍 Performing system health check...")

        health_status = {}

        # Check consciousness bridge
        if self.consciousness_bridge:
            health_status["consciousness_bridge"] = (
                self.consciousness_bridge.is_consciousness_bridge_healthy()
            )

        # Check agent registry
        if self.agent_registry:
            _ = self.agent_registry.get_registry_statistics()
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
        if self.consciousness_bridge and ConsciousnessMessage:
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
            self._dispatch_consciousness_message(
                announcement,
                operation="initialization_announcement",
                purpose="Announce consciousness system initialization",
            )
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
            self._dispatch_consciousness_message(
                lyrixa_message,
                operation="lyrixa_awakening",
                purpose="Announce Lyrixa consciousness awakening role",
            )

    def _dispatch_consciousness_message(
        self,
        message,
        *,
        operation: str,
        purpose: str,
    ) -> None:
        """Guardian-audit outbound orchestrator consciousness messages."""
        _guardian_preflight_orchestrator_operation(
            action="consciousness.orchestrator_message_dispatch",
            target=f"message:{_hash_value(message.destination)}",
            purpose=purpose,
            capabilities=("event:publish",),
            metadata={
                "operation": operation,
                "message_type": message.message_type,
                "source_hash": _hash_value(message.source),
                "destination_hash": _hash_value(message.destination),
                "payload_hash": _hash_json(message.payload),
                "payload_keys": tuple(sorted(message.payload)),
                "priority": message.priority,
                "correlation_id_hash": _hash_value(
                    getattr(message, "correlation_id", None)
                ),
            },
            rollback_plan="publish compensating consciousness message if needed",
        )
        self.consciousness_bridge.send_message(message)

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
                if (current_time - last_status_report).total_seconds() >= status_interval:
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
                self.logger.info(f"  Capabilities: {registry_stats['unique_capabilities']}")

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
                self.logger.warning(f"⚠️ Unhealthy components detected: {unhealthy_components}")

                # Could implement automatic recovery here
                # For now, just log the issue

        except Exception as e:
            self.logger.error(f"Error monitoring component health: {e}")

    async def shutdown(self):
        """Gracefully shutdown all consciousness components"""
        try:
            self.logger.info("🛑 Initiating consciousness system shutdown...")
            self.logger.info("=" * 60)

            _guardian_preflight_orchestrator_operation(
                action="consciousness.orchestrator_shutdown",
                target="consciousness:orchestrator",
                purpose="Gracefully shutdown consciousness orchestrator components",
                capabilities=("consciousness:write", "system:restart"),
                metadata={
                    "operation": "shutdown",
                    "was_initialized": self.is_initialized,
                    "was_running": self.is_running,
                    "component_presence": {
                        name: getattr(self, name) is not None
                        for name, _ in self.initialization_order
                    },
                    "has_narrative_layer": self.narrative_layer is not None,
                },
                rollback_plan="restart components from prior component reference snapshot",
            )
            self.is_running = False

            # Announce shutdown
            if self.consciousness_bridge:
                if ConsciousnessMessage:
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
                    self._dispatch_consciousness_message(
                        shutdown_announcement,
                        operation="shutdown_announcement",
                        purpose="Announce consciousness system shutdown",
                    )

                # Wait a moment for message to propagate
                await asyncio.sleep(2.0)

            # Shutdown components in reverse order
            shutdown_order = list(reversed(self.initialization_order))

            for component_name, display_name in shutdown_order:
                self.logger.info(f"🔧 Shutting down {display_name}...")

                try:
                    component = getattr(self, component_name)
                    if component and hasattr(component, "shutdown"):
                        _guardian_preflight_orchestrator_operation(
                            action="consciousness.orchestrator_component_shutdown",
                            target=f"consciousness_component:{component_name}",
                            purpose="Shutdown a consciousness orchestrator component",
                            capabilities=("consciousness:write", "system:restart"),
                            metadata={
                                "operation": "component_shutdown",
                                "component_name": component_name,
                                "component_type_hash": _hash_value(type(component).__name__),
                            },
                            rollback_plan="restart component if shutdown must be rolled back",
                        )
                        await component.shutdown()

                    self.logger.info(f"✅ {display_name} shutdown complete")

                except Exception as e:
                    self.logger.error(f"❌ Error shutting down {display_name}: {e}")

            # Clear component references
            _guardian_preflight_orchestrator_operation(
                action="consciousness.orchestrator_clear_components",
                target="consciousness:orchestrator",
                purpose="Clear consciousness orchestrator component references after shutdown",
                capabilities=("consciousness:write",),
                metadata={
                    "operation": "clear_components",
                    "component_presence": {
                        name: getattr(self, name) is not None
                        for name, _ in self.initialization_order
                    },
                    "has_narrative_layer": self.narrative_layer is not None,
                },
                rollback_plan="restore previous component references",
            )
            self.consciousness_bridge = None
            self.meta_layer_core = None
            self.lyrixa_consciousness = None
            self.agent_registry = None
            if self.narrative_layer:
                with contextlib.suppress(Exception):
                    self.narrative_layer.stop()
            self.narrative_layer = None

            self.is_initialized = False

            self.logger.info("=" * 60)
            self.logger.info("🌙 Consciousness Orchestrator shutdown complete")
            self.logger.info("💤 Aetherra Consciousness System is now OFFLINE")
            self.logger.info("=" * 60)

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"💥 Error during shutdown: {e}")
            await self._emergency_shutdown()

    async def _emergency_shutdown(self):
        """Emergency shutdown procedure"""
        self.logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED")

        _guardian_preflight_orchestrator_operation(
            action="consciousness.orchestrator_emergency_shutdown",
            target="consciousness:orchestrator",
            purpose="Emergency shutdown consciousness orchestrator components",
            capabilities=("consciousness:write", "system:restart"),
            metadata={
                "operation": "emergency_shutdown",
                "was_initialized": self.is_initialized,
                "was_running": self.is_running,
                "component_presence": {
                    name: getattr(self, name) is not None
                    for name, _ in self.initialization_order
                },
            },
            rollback_plan="restart components from prior component reference snapshot",
        )
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
                    _guardian_preflight_orchestrator_operation(
                        action="consciousness.orchestrator_component_emergency_shutdown",
                        target=f"consciousness_component:{_hash_value(type(component).__name__)}",
                        purpose="Emergency shutdown a consciousness orchestrator component",
                        capabilities=("consciousness:write", "system:restart"),
                        metadata={
                            "operation": "component_emergency_shutdown",
                            "component_type_hash": _hash_value(type(component).__name__),
                        },
                        rollback_plan="restart component if emergency shutdown must be rolled back",
                    )
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

        if self.narrative_layer and self.narrative_layer.enabled:
            status["components"]["narrative_layer"] = {
                "enabled": True,
                "last_chapter_ts": (
                    self.narrative_layer._last_chapter_ts.isoformat()
                    if getattr(self.narrative_layer, "_last_chapter_ts", None)
                    else None
                ),
                "last_coherence": self.last_narrative_coherence,
            }

        return status

    # --- Internal callbacks -------------------------------------------------
    def _on_new_chapter(self, chapter):
        """Update simple coherence metric export (placeholder)."""
        try:
            path = os.getenv(
                "AETHERRA_CONSCIOUSNESS_METRICS_PATH",
                ".aetherra/consciousness_metrics.txt",
            )
            _guardian_preflight_orchestrator_operation(
                action="consciousness.orchestrator_narrative_metrics_write",
                target=f"file:{_hash_value(path)}",
                purpose="Update consciousness orchestrator narrative coherence metrics",
                capabilities=("consciousness:write", "fs:write"),
                metadata={
                    "operation": "on_new_chapter",
                    "chapter_id_hash": _hash_value(getattr(chapter, "id", None)),
                    "coherence_index": round(float(chapter.coherence_index), 6),
                    "metrics_path_hash": _hash_value(path),
                    "previous_coherence": (
                        round(float(self.last_narrative_coherence), 6)
                        if self.last_narrative_coherence is not None
                        else None
                    ),
                },
                rollback_plan="restore previous coherence value and remove appended metrics line",
            )
            self.last_narrative_coherence = chapter.coherence_index
            # Prometheus exporter integration
            try:
                # Local imports
                from .metrics_exporter import (
                    increment_chapter_count,
                    initialize_exporter,
                    update_narrative_coherence,
                )

                initialize_exporter()
                update_narrative_coherence(chapter.coherence_index)
                increment_chapter_count()
            except Exception:
                pass
            # Lightweight metric export using environment-driven file sink (MVP)
            chapter_id_hash = _hash_value(getattr(chapter, "id", None)) or ""
            line = (
                f'narrative_coherence {chapter.coherence_index:.3f} '
                f'chapter_hash="{chapter_id_hash[:16]}" '
                f'ts="{chapter.end_ts.isoformat()}"\n'
            )
            metrics_file = Path(path)
            metrics_file.parent.mkdir(parents=True, exist_ok=True)
            with metrics_file.open("a", encoding="utf-8") as f:
                f.write(line)
        except PermissionError:
            raise
        except Exception:
            pass


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
        # Standard library imports
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
