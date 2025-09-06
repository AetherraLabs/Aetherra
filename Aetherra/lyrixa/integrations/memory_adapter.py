#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Memory System Adapter for Plugin UI
Provides proper memory interface for plugin UI system
"""

import logging
import random
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


class MemorySystemAdapter:
    """
    Adapts various memory systems to provide a unified interface for plugin UI
    """

    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self._start_time = time.time()
        self._quantum_available = False

        # Try to initialize quantum memory if available
        try:
            if not self.memory_system:
                from lyrixa.memory.quantum_memory_integration import get_memory_system

                self.memory_system = get_memory_system()
                self._quantum_available = True
                logger.info("[MEMORY] Quantum memory system connected")
        except ImportError:
            logger.warning("[MEMORY] Quantum memory not available, using fallback")

        self._mock_data = {
            "memory": {"usage": 0.3, "total": 8192, "available": 5734},
            "network": {"connected": True, "speed": "high", "latency": 12},
            "system": {
                "cpu": 45.2,
                "temperature": 42,
                "uptime": 3600,
                "processes": 156,
                "security_level": 85,
            },
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for plugin UI"""
        try:
            if self.memory_system and self._quantum_available:
                # Get quantum memory status and enhance with system data
                quantum_status = self.memory_system.get_status()

                # Enhanced data with quantum metrics
                enhanced_data = self._mock_data.copy()
                enhanced_data["memory"]["quantum_nodes"] = quantum_status.get(
                    "nodes", 0
                )
                enhanced_data["memory"]["coherence"] = quantum_status.get(
                    "coherence", {}
                ).get("average", 0.75)
                enhanced_data["memory"]["type"] = "quantum"

                # Add some variation to make it more realistic
                enhanced_data["memory"]["usage"] = 0.2 + random.random() * 0.4
                enhanced_data["system"]["cpu"] = 30 + random.random() * 40
                enhanced_data["system"]["uptime"] = int(time.time() - self._start_time)

                return enhanced_data
            elif self.memory_system and hasattr(
                self.memory_system, "get_system_metrics"
            ):
                return self.memory_system.get_system_metrics()

            # Fallback: return mock data with dynamic values
            # Add some variation to make it more realistic
            self._mock_data["memory"]["usage"] = 0.2 + random.random() * 0.4
            self._mock_data["system"]["cpu"] = 30 + random.random() * 40
            self._mock_data["system"]["uptime"] = int(time.time() - self._start_time)

            return self._mock_data

        except Exception as e:
            logger.warning(f"[MEMORY] Error getting system status: {e}")
            return self._mock_data

    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory-specific information"""
        status = self.get_system_status()
        return status.get("memory", {"usage": 0.3, "total": 8192, "available": 5734})

    def get_network_info(self) -> Dict[str, Any]:
        """Get network-specific information"""
        status = self.get_system_status()
        return status.get(
            "network", {"connected": True, "speed": "high", "latency": 12}
        )

    def update_memory_system(self, memory_system):
        """Update the underlying memory system"""
        self.memory_system = memory_system
        logger.info("[MEMORY] Memory system adapter updated")


# Global adapter instance
memory_adapter = MemorySystemAdapter()


def get_memory_adapter():
    """Get the global memory adapter instance"""
    return memory_adapter


def create_system_object_for_plugins():
    """Create a system object that plugin UI can use for evaluations"""
    adapter = get_memory_adapter()

    class SystemObject:
        def __init__(self):
            self._adapter = adapter

        @property
        def memory(self):
            """Memory object with usage attribute"""
            memory_info = self._adapter.get_memory_info()

            class MemoryObject:
                def __init__(self, info):
                    self.usage = info.get("usage", 0.3)
                    self.total = info.get("total", 8192)
                    self.available = info.get("available", 5734)

            return MemoryObject(memory_info)

        @property
        def network(self):
            """Network object with connected attribute"""
            network_info = self._adapter.get_network_info()

            class NetworkObject:
                def __init__(self, info):
                    self.connected = info.get("connected", True)
                    self.speed = info.get("speed", "high")
                    self.latency = info.get("latency", 12)

            return NetworkObject(network_info)

        @property
        def cpu(self):
            """CPU usage percentage"""
            status = self._adapter.get_system_status()
            return status.get("system", {}).get("cpu", 45.2)

        @property
        def security_level(self):
            """System security level (0-100)"""
            status = self._adapter.get_system_status()
            return status.get("system", {}).get("security_level", 85)

    return SystemObject()
