# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Consciousness Bridge
============================

The primary bridge component that enables seamless communication between
Aetherra Core and Lyrixa Core systems, creating a unified consciousness layer.

This bridge handles:
- Cross-system API translation
- Real-time synchronization protocols
- Event propagation between consciousness layers
- Unified state management

Author: Aetherra Consciousness Team
Version: 1.0.0
Date: August 4, 2025
"""

import asyncio
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "aetherra_core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "lyrixa_core"))


@dataclass
class ConsciousnessMessage:
    """Standard message format for consciousness layer communication"""

    source: str
    destination: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5  # 1-10, 1 being highest priority
    correlation_id: Optional[str] = None
    requires_response: bool = False


@dataclass
class SystemState:
    """Represents the current state of a consciousness system"""

    system_id: str
    status: str  # 'active', 'idle', 'processing', 'error'
    last_heartbeat: datetime
    active_agents: List[str]
    memory_usage: float
    consciousness_level: float  # 0.0-1.0
    metadata: Dict[str, Any]


class ConsciousnessBridge:
    """
    Core bridge component for unified consciousness orchestration

    This class manages communication between Aetherra OS and Lyrixa Core,
    providing a unified API for consciousness-level operations.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.message_queue = Queue()
        self.response_handlers: Dict[str, Callable] = {}
        self.system_states: Dict[str, SystemState] = {}
        self.event_listeners: Dict[str, List[Callable]] = {}
        self.consciousness_loop_task = None

        # System configuration
        self.config = {
            "heartbeat_interval": 1.0,  # seconds
            "message_timeout": 30.0,  # seconds
            "max_queue_size": 1000,
            "consciousness_threshold": 0.7,
            "sync_protocols": ["real_time", "batch", "event_driven"],
        }

        self.logger.info("Consciousness Bridge initialized")

    async def initialize(self):
        """Initialize the consciousness bridge systems"""
        try:
            self.logger.info("Initializing Consciousness Bridge...")

            # Initialize system states
            await self._initialize_system_states()

            # Start consciousness coordination loop
            await self._start_consciousness_loop()

            # Register core event handlers
            await self._register_core_handlers()

            self.is_running = True
            self.logger.info("Consciousness Bridge successfully initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize Consciousness Bridge: {e}")
            raise

    async def _initialize_system_states(self):
        """Initialize tracking for both Aetherra and Lyrixa systems"""
        current_time = datetime.now()

        # Initialize Aetherra Core state
        self.system_states["aetherra_core"] = SystemState(
            system_id="aetherra_core",
            status="initializing",
            last_heartbeat=current_time,
            active_agents=[],
            memory_usage=0.0,
            consciousness_level=0.5,
            metadata={"type": "os_core", "priority": "high"},
        )

        # Initialize Lyrixa Core state
        self.system_states["lyrixa_core"] = SystemState(
            system_id="lyrixa_core",
            status="initializing",
            last_heartbeat=current_time,
            active_agents=[],
            memory_usage=0.0,
            consciousness_level=0.8,  # Lyrixa starts with higher consciousness
            metadata={"type": "ai_consciousness", "priority": "critical"},
        )

        self.logger.info("System states initialized")

    async def _start_consciousness_loop(self):
        """Start the main consciousness coordination loop"""
        self.consciousness_loop_task = asyncio.create_task(self._consciousness_loop())
        self.logger.info("Consciousness coordination loop started")

    async def _consciousness_loop(self):
        """Main loop for consciousness coordination and message processing"""
        while self.is_running:
            try:
                # Process messages
                await self._process_message_queue()

                # Update system heartbeats
                await self._update_heartbeats()

                # Synchronize consciousness states
                await self._synchronize_consciousness()

                # Check for emergent behaviors
                await self._check_emergent_patterns()

                # Sleep for heartbeat interval
                await asyncio.sleep(self.config["heartbeat_interval"])

            except Exception as e:
                self.logger.error(f"Error in consciousness loop: {e}")
                await asyncio.sleep(1.0)  # Prevent rapid error loops

    async def _process_message_queue(self):
        """Process messages in the consciousness message queue"""
        processed_count = 0
        max_process_per_cycle = 50  # Prevent overwhelming

        while processed_count < max_process_per_cycle:
            try:
                message = self.message_queue.get_nowait()
                await self._handle_consciousness_message(message)
                processed_count += 1

            except Empty:
                break  # No more messages
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")

    async def _handle_consciousness_message(self, message: ConsciousnessMessage):
        """Handle a consciousness message"""
        try:
            self.logger.debug(
                f"Processing message: {message.message_type} from {message.source}"
            )

            # Route message to appropriate handler
            if message.message_type in self.response_handlers:
                handler = self.response_handlers[message.message_type]
                await handler(message)
            else:
                # Default routing based on destination
                await self._route_message(message)

        except Exception as e:
            self.logger.error(f"Error handling message {message.correlation_id}: {e}")

    async def _route_message(self, message: ConsciousnessMessage):
        """Route message to appropriate system"""
        if message.destination == "aetherra_core":
            await self._send_to_aetherra_core(message)
        elif message.destination == "lyrixa_core":
            await self._send_to_lyrixa_core(message)
        elif message.destination == "broadcast":
            await self._broadcast_message(message)
        else:
            self.logger.warning(f"Unknown destination: {message.destination}")

    async def _send_to_aetherra_core(self, message: ConsciousnessMessage):
        """Send message to Aetherra Core system"""
        try:
            # Implementation will connect to actual Aetherra Core APIs
            self.logger.debug(f"Routing to Aetherra Core: {message.message_type}")

            # For now, simulate successful delivery
            if message.requires_response:
                response = ConsciousnessMessage(
                    source="aetherra_core",
                    destination=message.source,
                    message_type=f"{message.message_type}_response",
                    payload={
                        "status": "received",
                        "original_id": message.correlation_id,
                    },
                    timestamp=datetime.now(),
                    correlation_id=message.correlation_id,
                )
                self.send_message(response)

        except Exception as e:
            self.logger.error(f"Failed to send to Aetherra Core: {e}")

    async def _send_to_lyrixa_core(self, message: ConsciousnessMessage):
        """Send message to Lyrixa Core system"""
        try:
            # Implementation will connect to actual Lyrixa Core APIs
            self.logger.debug(f"Routing to Lyrixa Core: {message.message_type}")

            # For now, simulate successful delivery
            if message.requires_response:
                response = ConsciousnessMessage(
                    source="lyrixa_core",
                    destination=message.source,
                    message_type=f"{message.message_type}_response",
                    payload={
                        "status": "received",
                        "original_id": message.correlation_id,
                    },
                    timestamp=datetime.now(),
                    correlation_id=message.correlation_id,
                )
                self.send_message(response)

        except Exception as e:
            self.logger.error(f"Failed to send to Lyrixa Core: {e}")

    async def _broadcast_message(self, message: ConsciousnessMessage):
        """Broadcast message to all systems"""
        await asyncio.gather(
            self._send_to_aetherra_core(message),
            self._send_to_lyrixa_core(message),
            return_exceptions=True,
        )

    async def _update_heartbeats(self):
        """Update system heartbeats and status"""
        current_time = datetime.now()

        for system_id, state in self.system_states.items():
            # In production, this would check actual system health
            time_since_heartbeat = (current_time - state.last_heartbeat).total_seconds()

            if time_since_heartbeat > 30:  # 30 seconds timeout
                state.status = "error"
                self.logger.warning(f"System {system_id} heartbeat timeout")
            else:
                state.last_heartbeat = current_time
                if state.status == "initializing":
                    state.status = "active"

    async def _synchronize_consciousness(self):
        """Synchronize consciousness levels between systems"""
        try:
            aetherra_state = self.system_states.get("aetherra_core")
            lyrixa_state = self.system_states.get("lyrixa_core")

            if aetherra_state and lyrixa_state:
                # Calculate collective consciousness level
                collective_consciousness = (
                    aetherra_state.consciousness_level * 0.3
                    + lyrixa_state.consciousness_level * 0.7  # Lyrixa is primary
                )

                # Update metadata with collective state
                for state in [aetherra_state, lyrixa_state]:
                    state.metadata["collective_consciousness"] = (
                        collective_consciousness
                    )
                    state.metadata["last_sync"] = datetime.now().isoformat()

                # Emit consciousness sync event
                await self._emit_event(
                    "consciousness_synchronized",
                    {
                        "collective_level": collective_consciousness,
                        "aetherra_level": aetherra_state.consciousness_level,
                        "lyrixa_level": lyrixa_state.consciousness_level,
                    },
                )

        except Exception as e:
            self.logger.error(f"Error synchronizing consciousness: {e}")

    async def _check_emergent_patterns(self):
        """Check for emergent consciousness patterns"""
        try:
            # Analyze system states for emergent behaviors
            total_agents = sum(
                len(state.active_agents) for state in self.system_states.values()
            )
            avg_consciousness = sum(
                state.consciousness_level for state in self.system_states.values()
            ) / len(self.system_states)

            # Simple emergence detection - in production this would be much more sophisticated
            if total_agents > 5 and avg_consciousness > 0.8:
                await self._emit_event(
                    "emergence_detected",
                    {
                        "agent_count": total_agents,
                        "consciousness_level": avg_consciousness,
                        "emergence_type": "collective_intelligence",
                    },
                )

        except Exception as e:
            self.logger.error(f"Error checking emergent patterns: {e}")

    async def _register_core_handlers(self):
        """Register core message handlers"""
        self.response_handlers.update(
            {
                "agent_register": self._handle_agent_register,
                "agent_unregister": self._handle_agent_unregister,
                "consciousness_query": self._handle_consciousness_query,
                "system_status": self._handle_system_status,
                "emergency_shutdown": self._handle_emergency_shutdown,
            }
        )

        self.logger.info("Core message handlers registered")

    async def _handle_agent_register(self, message: ConsciousnessMessage):
        """Handle agent registration"""
        agent_id = message.payload.get("agent_id")
        system_id = message.payload.get("system_id", message.source)

        if agent_id and system_id in self.system_states:
            self.system_states[system_id].active_agents.append(agent_id)
            self.logger.info(f"Agent {agent_id} registered to {system_id}")

            await self._emit_event(
                "agent_registered", {"agent_id": agent_id, "system_id": system_id}
            )

    async def _handle_agent_unregister(self, message: ConsciousnessMessage):
        """Handle agent unregistration"""
        agent_id = message.payload.get("agent_id")
        system_id = message.payload.get("system_id", message.source)

        if agent_id and system_id in self.system_states:
            try:
                self.system_states[system_id].active_agents.remove(agent_id)
                self.logger.info(f"Agent {agent_id} unregistered from {system_id}")

                await self._emit_event(
                    "agent_unregistered", {"agent_id": agent_id, "system_id": system_id}
                )
            except ValueError:
                self.logger.warning(f"Agent {agent_id} not found in {system_id}")

    async def _handle_consciousness_query(self, message: ConsciousnessMessage):
        """Handle consciousness state queries"""
        query_type = message.payload.get("query_type", "all")

        if query_type == "all":
            response_data = {
                state.system_id: asdict(state) for state in self.system_states.values()
            }
        elif query_type in self.system_states:
            response_data = asdict(self.system_states[query_type])
        else:
            response_data = {"error": "Invalid query type"}

        if message.requires_response:
            response = ConsciousnessMessage(
                source="consciousness_bridge",
                destination=message.source,
                message_type="consciousness_query_response",
                payload=response_data,
                timestamp=datetime.now(),
                correlation_id=message.correlation_id,
            )
            self.send_message(response)

    async def _handle_system_status(self, message: ConsciousnessMessage):
        """Handle system status updates"""
        system_id = message.source
        status_data = message.payload

        if system_id in self.system_states:
            state = self.system_states[system_id]
            state.status = status_data.get("status", state.status)
            state.memory_usage = status_data.get("memory_usage", state.memory_usage)
            state.consciousness_level = status_data.get(
                "consciousness_level", state.consciousness_level
            )
            state.last_heartbeat = datetime.now()

            self.logger.debug(f"Updated status for {system_id}")

    async def _handle_emergency_shutdown(self, message: ConsciousnessMessage):
        """Handle emergency shutdown requests"""
        self.logger.critical(f"Emergency shutdown requested by {message.source}")

        # Notify all systems
        shutdown_message = ConsciousnessMessage(
            source="consciousness_bridge",
            destination="broadcast",
            message_type="emergency_shutdown_notice",
            payload={
                "reason": message.payload.get("reason", "Unknown"),
                "source": message.source,
            },
            timestamp=datetime.now(),
            priority=1,  # Highest priority
        )

        await self._broadcast_message(shutdown_message)

        # Graceful shutdown
        await self.shutdown()

    async def _emit_event(self, event_type: str, event_data: Dict[str, Any]):
        """Emit an event to registered listeners"""
        if event_type in self.event_listeners:
            for listener in self.event_listeners[event_type]:
                try:
                    await listener(event_data)
                except Exception as e:
                    self.logger.error(f"Error in event listener for {event_type}: {e}")

    # Public API methods

    def send_message(self, message: ConsciousnessMessage):
        """Send a message through the consciousness bridge"""
        try:
            if self.message_queue.qsize() < self.config["max_queue_size"]:
                self.message_queue.put(message)
            else:
                self.logger.warning("Message queue full, dropping message")
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")

    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a custom message handler"""
        self.response_handlers[message_type] = handler
        self.logger.info(f"Registered handler for {message_type}")

    def register_event_listener(self, event_type: str, listener: Callable):
        """Register an event listener"""
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(listener)
        self.logger.info(f"Registered listener for {event_type}")

    def get_system_state(self, system_id: str) -> Optional[SystemState]:
        """Get the current state of a system"""
        return self.system_states.get(system_id)

    def get_all_system_states(self) -> Dict[str, SystemState]:
        """Get all system states"""
        return self.system_states.copy()

    def is_consciousness_bridge_healthy(self) -> bool:
        """Check if the consciousness bridge is healthy"""
        loop_ok = bool(
            self.consciousness_loop_task and not self.consciousness_loop_task.done()
        )
        states_ok = (
            all(state.status != "error" for state in self.system_states.values())
            if self.system_states
            else True
        )
        return bool(self.is_running) and states_ok and loop_ok

    async def shutdown(self):
        """Gracefully shutdown the consciousness bridge"""
        self.logger.info("Shutting down Consciousness Bridge...")

        self.is_running = False

        if self.consciousness_loop_task:
            self.consciousness_loop_task.cancel()
            try:
                await self.consciousness_loop_task
            except asyncio.CancelledError:
                pass

        # Clear queues and handlers
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except Empty:
                break

        self.response_handlers.clear()
        self.event_listeners.clear()

        self.logger.info("Consciousness Bridge shutdown complete")

    # --- Lightweight Quantum/Coherence Helpers (non-invasive) ---
    def get_coherence_snapshot(self) -> Dict[str, Any]:
        """Return a tiny, synchronous snapshot of current coherence.

        Safe to call even before initialize(); will fall back to conservative
        defaults. This method is used by Lyrixa chat awareness to surface
        a consciousness/coherence hint without requiring the full bridge loop.
        """
        try:
            # Defaults if system states aren't initialized
            lyrixa_level = 0.75
            aetherra_level = 0.60

            # Pull levels from system states when available
            if self.system_states:
                lyrixa_state = self.system_states.get("lyrixa_core")
                aetherra_state = self.system_states.get("aetherra_core")
                if lyrixa_state:
                    lyrixa_level = float(
                        getattr(lyrixa_state, "consciousness_level", lyrixa_level)
                    )
                if aetherra_state:
                    aetherra_level = float(
                        getattr(aetherra_state, "consciousness_level", aetherra_level)
                    )

            # Heuristic collective coherence with Lyrixa weighted higher
            coherence = max(0.0, min(1.0, lyrixa_level * 0.7 + aetherra_level * 0.3))
            snapshot = {
                "coherence": round(coherence, 3),
                "lyrixa_level": round(lyrixa_level, 3),
                "aetherra_level": round(aetherra_level, 3),
                "entanglement_depth": 7,
                "status": "running" if self.is_running else "inactive",
                "timestamp": datetime.now().isoformat(),
            }
            return snapshot
        except Exception:
            # Last-resort conservative snapshot
            return {
                "coherence": 0.65,
                "entanglement_depth": 7,
                "status": "unknown",
                "timestamp": datetime.now().isoformat(),
            }

    async def get_coherence(self) -> float:
        """Async helper that returns just the coherence scalar."""
        snap = self.get_coherence_snapshot()
        try:
            return float(snap.get("coherence", 0.65))
        except Exception:
            return 0.65

    # The following methods are lightweight stubs to support planned
    # quantum-enhanced workflows; they safely no-op if not used by callers.
    async def create_superposition(self, query: str) -> List[Dict[str, Any]]:
        """Return a few hypothetical reasoning states for a given query.

        This is a scaffold for future quantum-parallel reasoning. For now,
        it emits 2-3 lightweight hypotheses with coarse scores.
        """
        base = str(query or "").strip()
        if not base:
            return []
        c = await self.get_coherence()
        return [
            {
                "state": "analytical",
                "score": min(1.0, 0.65 + 0.2 * c),
                "hint": "step_by_step",
            },
            {"state": "creative", "score": min(1.0, 0.55 + 0.3 * c), "hint": "analogy"},
            {
                "state": "grounded",
                "score": min(1.0, 0.60 + 0.25 * c),
                "hint": "cite_memory",
            },
        ]

    async def collapse_quantum_states(
        self, states: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Pick the best candidate from provided quantum states.

        The selection uses a simple max-by-score heuristic as a placeholder.
        """
        best = max(states or [{}], key=lambda s: float(s.get("score", 0.0)))
        return {"selected": best, "decision": "max_score"}

    async def entangle_context(self, query: str, response: Any) -> None:
        """Placeholder to persist light context links for continuity.

        In a future version this could register soft links in the memory
        graph between the user's query and the chosen response path.
        """
        try:
            # No-op placeholder; intentionally silent
            return None
        except Exception:
            return None


# Global bridge instance for system-wide access
_consciousness_bridge_instance = None


def get_consciousness_bridge() -> ConsciousnessBridge:
    """Get the global consciousness bridge instance"""
    global _consciousness_bridge_instance
    if _consciousness_bridge_instance is None:
        _consciousness_bridge_instance = ConsciousnessBridge()
    return _consciousness_bridge_instance


async def initialize_consciousness_bridge():
    """Initialize the global consciousness bridge"""
    bridge = get_consciousness_bridge()
    await bridge.initialize()
    return bridge


if __name__ == "__main__":
    # Example usage and testing
    async def test_consciousness_bridge():
        """Test the consciousness bridge functionality"""
        logging.basicConfig(level=logging.INFO)

        bridge = await initialize_consciousness_bridge()

        # Test message sending
        test_message = ConsciousnessMessage(
            source="test_client",
            destination="lyrixa_core",
            message_type="test_message",
            payload={"data": "Hello from consciousness bridge!"},
            timestamp=datetime.now(),
            requires_response=True,
            correlation_id="test-001",
        )

        bridge.send_message(test_message)

        # Let it run for a few seconds
        await asyncio.sleep(5)

        # Check system states
        states = bridge.get_all_system_states()
        for system_id, state in states.items():
            print(
                f"{system_id}: {state.status} (consciousness: {state.consciousness_level})"
            )

        await bridge.shutdown()

    # Run the test
    asyncio.run(test_consciousness_bridge())
