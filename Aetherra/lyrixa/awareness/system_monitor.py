#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
System Monitor - Real-time Aetherra OS Status Tracker

Provides comprehensive system state snapshots for Lyrixa's awareness layer.
Queries the service registry and individual components to build a rich
picture of what's available, healthy, and capable.
"""

from __future__ import annotations

from typing import Any


class SystemMonitor:
    """Tracks and reports Aetherra OS system state for Lyrixa"""

    def __init__(self, service_registry=None):
        self.registry = service_registry
        self._cache: dict[str, Any] = {}
        self._cache_timestamp: float = 0.0

    async def get_comprehensive_status(self, cache_ttl: float = 10.0) -> dict[str, Any]:
        """
        Get comprehensive system status from all registered services.

        Args:
            cache_ttl: Cache validity in seconds (default 10s)

        Returns:
            Dict with status of all major subsystems
        """
        import time

        now = time.time()
        if self._cache and (now - self._cache_timestamp) < cache_ttl:
            return self._cache

        status = {
            "timestamp": now,
            "services": {},
            "capabilities": [],
            "health_summary": "unknown",
        }

        if not self.registry:
            return status

        try:
            # Get all registered services
            registry_status = self.registry.get_registry_status()
            services_info = registry_status.get("services", {})

            healthy_count = 0
            degraded_count = 0
            offline_count = 0

            for service_name, info in services_info.items():
                svc_status = info.get("status", "unknown")
                status["services"][service_name] = {
                    "status": svc_status,
                    "type": info.get("type", "unknown"),
                    "dependencies": info.get("dependencies", []),
                }

                if svc_status == "healthy":
                    healthy_count += 1
                elif svc_status in ("degraded", "starting"):
                    degraded_count += 1
                else:
                    offline_count += 1

            # Determine overall health
            total = len(services_info)
            if total == 0:
                status["health_summary"] = "no_services"
            elif offline_count > total / 2:
                status["health_summary"] = "critical"
            elif degraded_count > total / 3:
                status["health_summary"] = "degraded"
            elif healthy_count >= total * 0.8:
                status["health_summary"] = "healthy"
            else:
                status["health_summary"] = "partial"

            # Extract capabilities from service types
            status["capabilities"] = self._extract_capabilities(services_info)

        except Exception:
            status["health_summary"] = "error"

        self._cache = status
        self._cache_timestamp = now
        return status

    def _extract_capabilities(self, services: dict[str, Any]) -> list[str]:
        """Extract capability descriptions from registered services"""
        capabilities = []

        # Map service types to user-friendly capabilities
        capability_map = {
            "memory_system": "Quantum-enhanced memory storage and retrieval",
            "memory_extension": "QFAC quantum memory compression",
            "persistent_memory": "Cross-session memory persistence",
            "plugin_manager": "Plugin discovery and execution",
            "marketplace": "Plugin marketplace (Aetherra Hub)",
            "script_interpreter": "Aether workflow execution",
            "self_maintenance": "Autonomous self-improvement",
            "autonomous_evolution": "Code discovery and integration",
            "native_engine": "Core execution engine",
            "consciousness": "Quantum consciousness integration",
            "assistant": "Intelligent conversational interface",
            "orchestration": "Task scheduling and coordination",
            "adaptive_behavior": "Continuous learning from interactions",
        }

        for service_name, info in services.items():
            svc_type = info.get("type", "")
            status = info.get("status", "")

            # Only include healthy or starting services
            if status not in ("healthy", "starting", "degraded"):
                continue

            if svc_type in capability_map:
                capabilities.append(capability_map[svc_type])
            elif "memory" in service_name:
                capabilities.append(f"Memory system: {service_name}")
            elif "consciousness" in service_name:
                capabilities.append(f"Consciousness layer: {service_name}")

        return capabilities

    def get_service_status(self, service_name: str) -> dict[str, Any] | None:
        """Get status for a specific service"""
        if not self.registry:
            return None

        try:
            info = self.registry.get_service_info(service_name)
            if not info:
                return None

            return {
                "name": service_name,
                "status": info.status.value if hasattr(info.status, "value") else str(info.status),
                "type": info.metadata.get("type") if info.metadata else "unknown",
                "dependencies": info.dependencies or [],
            }
        except Exception:
            return None

    async def build_awareness_context(self) -> dict[str, Any]:
        """Build a compact awareness context for chat prompts"""
        status = await self.get_comprehensive_status()

        context = {
            "system_health": status.get("health_summary", "unknown"),
            "active_services": len(
                [s for s in status.get("services", {}).values() if s.get("status") == "healthy"]
            ),
            "total_services": len(status.get("services", {})),
            "key_capabilities": status.get("capabilities", [])[:6],  # Top 6
        }

        # Add specific system flags for quick checks
        services = status.get("services", {})
        context["has_memory"] = any("memory" in name for name in services.keys())
        context["has_plugins"] = "plugin_manager" in services
        context["has_consciousness"] = any(
            "consciousness" in name or "cognition" in name for name in services.keys()
        )
        context["has_hub"] = "aetherra_hub" in services
        context["has_homeostasis"] = "homeostasis_system" in services

        return context
