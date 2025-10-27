#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🎯 Aetherra System Supervisor
=============================

Implements runlevel management and service health monitoring for the homeostasis system.
Ensures "all systems are running" by maintaining service availability and coordinating
system state transitions.

The supervisor implements:
- Runlevel state machine (BOOTING → DEGRADED → ONLINE → DRAINING → OFFLINE)
- Service health monitoring and automatic restart
- System readiness validation
- Integration with homeostasis for stability decisions
- Health state publishing to Lyrixa dashboards

Runlevels:
- BOOTING: System starting up, services initializing
- DEGRADED: Some services unhealthy but core functions available
- ONLINE: All required services healthy and operating normally
- DRAINING: Graceful shutdown in progress
- OFFLINE: System stopped or critical failure

Author: Aetherra Labs
"""

# Standard library imports
import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Third party imports
import yaml

# Aetherra imports
from aetherra_service_registry import ServiceStatus, get_service_registry

logger = logging.getLogger(__name__)


class SystemRunlevel(Enum):
    """System runlevel states."""

    BOOTING = "BOOTING"
    DEGRADED = "DEGRADED"
    ONLINE = "ONLINE"
    DRAINING = "DRAINING"
    OFFLINE = "OFFLINE"
    FAILED = "FAILED"


class ServiceCriticality(Enum):
    """Service criticality levels."""

    CRITICAL = "critical"  # System cannot function without this
    IMPORTANT = "important"  # Significant degradation without this
    OPTIONAL = "optional"  # Nice to have but not essential


@dataclass
class ServiceHealth:
    """Health status of a service."""

    service_name: str
    status: ServiceStatus
    criticality: ServiceCriticality
    last_heartbeat: float
    restart_count: int = 0
    last_restart: Optional[float] = None
    error_count: int = 0
    uptime: float = 0.0


@dataclass
class RunlevelTransition:
    """Information about a runlevel transition."""

    from_level: SystemRunlevel
    to_level: SystemRunlevel
    timestamp: float
    reason: str
    triggered_by: str


class SystemSupervisor:
    """
    System supervisor for runlevel management and service health monitoring.

    Maintains system availability by monitoring service health, managing
    runlevel transitions, and coordinating with homeostasis for stability.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the system supervisor."""
        self.config_path = config_path or "Aetherra/homeostasis/configs/setpoints.yaml"
        self.config = self._load_config()

        # Current system state
        self.current_runlevel = SystemRunlevel.OFFLINE
        self.target_runlevel = SystemRunlevel.ONLINE
        self.boot_start_time: Optional[float] = None
        self.online_since: Optional[float] = None

        # Service tracking
        self.service_health: Dict[str, ServiceHealth] = {}
        self.required_services: Set[str] = set()
        self.service_dependencies: Dict[str, List[str]] = {}

        # Monitoring configuration
        self.heartbeat_timeout = 30.0  # seconds
        self.max_restart_attempts = 3
        self.restart_cooldown = 300.0  # seconds
        self.health_check_interval = 10.0  # seconds

        # Runlevel history
        self.runlevel_history: List[RunlevelTransition] = []
        self.stability_metrics: Dict[str, Any] = {}

        # Control flags
        self.running = False
        self.maintenance_mode = False

        # Load service configuration
        self._initialize_service_config()

        logger.info("🎯 System supervisor initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                return {}
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return {}

    def _initialize_service_config(self):
        """Initialize service configuration and criticality mapping."""
        # Define critical services that must be running for ONLINE state
        self.required_services = {
            "aetherra_engine",
            "kernel_loop",  # actual name is "kernel_loop", not "aetherra_kernel"
            "memory_system",
        }

        # Define service criticality
        critical_services = {
            "aetherra_engine": ServiceCriticality.CRITICAL,
            "kernel_loop": ServiceCriticality.CRITICAL,  # updated name
            "memory_system": ServiceCriticality.CRITICAL,
        }

        important_services = {
            "aetherra_hub": ServiceCriticality.IMPORTANT,
            "lyrixa_chat": ServiceCriticality.IMPORTANT,  # actual name is "lyrixa_chat"
            "plugin_manager": ServiceCriticality.IMPORTANT,  # actual name is "plugin_manager"
        }

        # Update service health tracking
        all_services = {**critical_services, **important_services}

        for service_name, criticality in all_services.items():
            if service_name not in self.service_health:
                self.service_health[service_name] = ServiceHealth(
                    service_name=service_name,
                    status=ServiceStatus.STARTING,  # Will be updated in first health check
                    criticality=criticality,
                    last_heartbeat=time.time(),
                )

        # Define basic service dependencies
        self.service_dependencies = {
            "aetherra_engine": [],  # Core engine has minimal dependencies
            "kernel_loop": ["aetherra_engine", "memory_system"],  # updated name
            "memory_system": [],  # Core memory system
            "aetherra_hub": ["aetherra_engine"],
            "lyrixa_chat": ["aetherra_engine", "memory_system"],  # updated name
            "plugin_manager": ["aetherra_hub"],  # updated name
        }

        logger.debug(f"Initialized tracking for {len(all_services)} services")

    async def start(self):
        """Start the system supervisor."""
        if self.running:
            logger.warning("System supervisor is already running")
            return

        self.running = True
        self.boot_start_time = time.time()

        # Transition to BOOTING state
        await self._transition_runlevel(SystemRunlevel.BOOTING, "System supervisor started")

        logger.info("🚀 System supervisor started")

        # Wait for other systems to stabilize before starting aggressive monitoring
        startup_delay = 10.0  # 10 seconds
        logger.info(f"⏱️ Waiting {startup_delay}s for system stabilization...")
        await asyncio.sleep(startup_delay)

        # Do an initial health check to get current state
        await self._update_service_health()
        logger.info("📊 Initial health assessment complete")

        # Main supervision loop
        while self.running:
            try:
                await self._supervision_cycle()
                await asyncio.sleep(self.health_check_interval)

            except asyncio.CancelledError:
                logger.info("🛑 System supervisor stopped")
                break
            except Exception as e:
                logger.error(f"Error in supervision cycle: {e}")
                await asyncio.sleep(self.health_check_interval)

    def stop(self):
        """Stop the system supervisor."""
        self.running = False
        logger.info("🛑 System supervisor stopping")

    async def _supervision_cycle(self):
        """Execute one supervision cycle."""
        # Update service health
        await self._update_service_health()

        # Perform system verification (Phase 2 requirement)
        verification_result = await self.verify_all_systems_active()

        # Log corrective actions if any were taken
        if verification_result.get("corrective_actions"):
            for action in verification_result["corrective_actions"]:
                logger.info(f"🔧 Corrective action: {action}")

        # Check for required runlevel transitions
        await self._check_runlevel_transitions()

        # Restart failed services if needed
        await self._manage_service_recovery()

        # Send heartbeats to all services (Phase 2 requirement)
        await self.heartbeat_all()

        # Update stability metrics
        self._update_stability_metrics()

        # Log periodic status
        self._log_periodic_status()

    async def _update_service_health(self):
        """Update health status for all tracked services."""
        try:
            registry = await get_service_registry()
            if not registry:
                logger.warning("Service registry not available for health check")
                return

            current_time = time.time()

            # Update health for each tracked service
            for service_name in self.service_health:
                service_info = registry.get_service_info(service_name)
                health = self.service_health[service_name]

                if service_info:
                    # Update from registry
                    old_status = health.status
                    health.status = service_info.status
                    health.last_heartbeat = current_time

                    # Calculate uptime - use simple timestamp difference
                    health.uptime = current_time - health.last_heartbeat

                    # Log status changes
                    if old_status != health.status:
                        logger.info(
                            f"📊 Service {service_name}: {old_status.value} → {health.status.value}"
                        )

                        # Reset error count on recovery
                        if health.status == ServiceStatus.HEALTHY:
                            health.error_count = 0
                        elif health.status in [ServiceStatus.FAILED, ServiceStatus.DEGRADED]:
                            health.error_count += 1

                else:
                    # Service not found in registry - could be name mismatch
                    # Only mark as failed if it's been missing for a while and we haven't already
                    # reached max restart attempts (indicates non-restartable service)
                    if health.restart_count < self.max_restart_attempts:
                        if health.status != ServiceStatus.FAILED:
                            logger.warning(f"⚠️ Service {service_name} not found in registry")
                            health.status = ServiceStatus.FAILED
                            health.error_count += 1
                    else:
                        # Service can't be restarted, mark as degraded to avoid restart loops
                        if health.status == ServiceStatus.FAILED:
                            health.status = ServiceStatus.DEGRADED
                            logger.debug(
                                f"🟡 Service {service_name} marked degraded (not restartable)"
                            )

                    # Check for stale heartbeat only if service was previously healthy
                    if (
                        current_time - health.last_heartbeat > self.heartbeat_timeout
                        and health.status not in [ServiceStatus.FAILED, ServiceStatus.DEGRADED]
                    ):
                        logger.warning(f"💔 Service {service_name} heartbeat timeout")
                        health.status = ServiceStatus.FAILED
                        health.error_count += 1

        except Exception as e:
            logger.error(f"Error updating service health: {e}")

    async def _check_runlevel_transitions(self):
        """Check if runlevel transitions are needed."""
        current_health = self._assess_system_health()
        new_runlevel = self._determine_target_runlevel(current_health)

        if new_runlevel != self.current_runlevel:
            reason = self._get_transition_reason(current_health, new_runlevel)
            await self._transition_runlevel(new_runlevel, reason)

    def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health."""
        health_summary: Dict[str, Any] = {
            "total_services": len(self.service_health),
            "healthy_services": 0,
            "degraded_services": 0,
            "failed_services": 0,
            "critical_services_healthy": 0,
            "critical_services_total": 0,
            "important_services_healthy": 0,
            "important_services_total": 0,
        }

        for health in self.service_health.values():
            # Count by status
            if health.status == ServiceStatus.HEALTHY:
                health_summary["healthy_services"] += 1
            elif health.status == ServiceStatus.DEGRADED:
                health_summary["degraded_services"] += 1
            elif health.status == ServiceStatus.FAILED:
                health_summary["failed_services"] += 1

            # Count by criticality - treat DEGRADED as functional for critical systems
            # (since degraded usually just means missing heartbeats, not actual failure)
            if health.criticality == ServiceCriticality.CRITICAL:
                health_summary["critical_services_total"] += 1
                if health.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                    health_summary["critical_services_healthy"] += 1
            elif health.criticality == ServiceCriticality.IMPORTANT:
                health_summary["important_services_total"] += 1
                if health.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                    health_summary["important_services_healthy"] += 1

        # Calculate health percentages - count DEGRADED as partially healthy
        if health_summary["total_services"] > 0:
            # Count healthy as 100%, degraded as 75%, failed as 0%
            weighted_health = (
                health_summary["healthy_services"] * 1.0
                + health_summary["degraded_services"] * 0.75
                + health_summary["failed_services"] * 0.0
            )
            health_summary["health_percentage"] = (
                weighted_health / health_summary["total_services"]
            ) * 100.0
        else:
            health_summary["health_percentage"] = 0.0

        if health_summary["critical_services_total"] > 0:
            health_summary["critical_health_percentage"] = (
                health_summary["critical_services_healthy"]
                / health_summary["critical_services_total"]
            ) * 100.0
        else:
            health_summary["critical_health_percentage"] = 100.0

        return health_summary

    def _determine_target_runlevel(self, health_summary: Dict[str, Any]) -> SystemRunlevel:
        """Determine the appropriate runlevel based on system health."""
        critical_health = health_summary["critical_health_percentage"]
        overall_health = health_summary["health_percentage"]

        # Check for critical failures - only fail if critical services are actually FAILED
        # (not just degraded due to missing heartbeats)
        actual_failed = health_summary["failed_services"]
        if actual_failed > 0 and critical_health < 25.0:
            return SystemRunlevel.FAILED

        # Check for offline conditions - be more lenient
        if critical_health == 0.0 or overall_health < 10.0:
            return SystemRunlevel.OFFLINE

        # Check for degraded conditions - allow degraded services to still be functional
        if critical_health < 80.0 or overall_health < 60.0:
            # If we were ONLINE and now degraded, go to DEGRADED
            # If we were starting up, might still be BOOTING
            if self.current_runlevel == SystemRunlevel.ONLINE:
                return SystemRunlevel.DEGRADED
            elif self.current_runlevel == SystemRunlevel.BOOTING:
                # Continue booting if we're making progress
                if critical_health > 50.0:
                    return SystemRunlevel.DEGRADED
                else:
                    return SystemRunlevel.BOOTING
            else:
                return SystemRunlevel.DEGRADED

        # Check for online conditions - allow some degraded services
        if critical_health >= 80.0 and overall_health >= 60.0:
            return SystemRunlevel.ONLINE

        # Default to current state if unclear
        return self.current_runlevel

    def _get_transition_reason(
        self, health_summary: Dict[str, Any], new_runlevel: SystemRunlevel
    ) -> str:
        """Get human-readable reason for runlevel transition."""
        critical_health = health_summary["critical_health_percentage"]
        overall_health = health_summary["health_percentage"]
        failed_services = health_summary["failed_services"]
        degraded_services = health_summary["degraded_services"]

        if new_runlevel == SystemRunlevel.ONLINE:
            return f"All critical services healthy, overall health {overall_health:.1f}%"
        elif new_runlevel == SystemRunlevel.DEGRADED:
            if degraded_services > 0 and failed_services == 0:
                return f"Services degraded (likely heartbeat issues), critical health {critical_health:.1f}%"
            else:
                return (
                    f"Critical health {critical_health:.1f}%, overall health {overall_health:.1f}%"
                )
        elif new_runlevel == SystemRunlevel.FAILED:
            return f"Critical system failure, {failed_services} services actually failed"
        elif new_runlevel == SystemRunlevel.OFFLINE:
            return f"System offline, critical health {critical_health:.1f}%"
        else:
            return f"System state change, health {overall_health:.1f}%"

    async def _transition_runlevel(self, new_runlevel: SystemRunlevel, reason: str):
        """Transition to a new runlevel."""
        old_runlevel = self.current_runlevel

        # Record transition
        transition = RunlevelTransition(
            from_level=old_runlevel,
            to_level=new_runlevel,
            timestamp=time.time(),
            reason=reason,
            triggered_by="supervisor",
        )

        self.runlevel_history.append(transition)
        self.current_runlevel = new_runlevel

        # Update timestamps
        if new_runlevel == SystemRunlevel.ONLINE and old_runlevel != SystemRunlevel.ONLINE:
            self.online_since = time.time()
        elif new_runlevel != SystemRunlevel.ONLINE:
            self.online_since = None

        # Log transition
        logger.info(f"🎯 Runlevel transition: {old_runlevel.value} → {new_runlevel.value}")
        logger.info(f"📝 Reason: {reason}")

        # Perform runlevel-specific actions
        await self._handle_runlevel_actions(old_runlevel, new_runlevel)

    async def _handle_runlevel_actions(self, old_level: SystemRunlevel, new_level: SystemRunlevel):
        """Handle actions specific to runlevel transitions."""
        if new_level == SystemRunlevel.ONLINE and old_level != SystemRunlevel.ONLINE:
            logger.info("✅ System is now ONLINE - all critical services healthy")
            await self._publish_health_state("healthy")

        elif new_level == SystemRunlevel.DEGRADED:
            logger.warning("⚠️ System is DEGRADED - some services unhealthy")
            await self._publish_health_state("degraded")

        elif new_level == SystemRunlevel.FAILED:
            logger.error("🚨 System FAILED - critical services down")
            await self._publish_health_state("failed")

        elif new_level == SystemRunlevel.OFFLINE:
            logger.warning("📴 System OFFLINE")
            await self._publish_health_state("offline")

    async def _publish_health_state(self, state: str):
        """Publish health state to Lyrixa and other interested systems."""
        try:
            registry = await get_service_registry()
            if registry:
                # Broadcast health state to all services
                health_data = {
                    "runlevel": self.current_runlevel.value,
                    "health_state": state,
                    "timestamp": time.time(),
                    "online_since": self.online_since,
                    "services_summary": self._get_services_summary(),
                }

                await registry.broadcast_message("system_health_update", health_data)
                logger.debug(f"📡 Published health state: {state}")

        except Exception as e:
            logger.error(f"Failed to publish health state: {e}")

    async def _manage_service_recovery(self):
        """Manage automatic service recovery and restarts."""
        current_time = time.time()

        for service_name, health in self.service_health.items():
            # Skip if service is healthy
            if health.status == ServiceStatus.HEALTHY:
                continue

            # Check if service needs restart
            if self._should_restart_service(health, current_time):
                await self._restart_service(service_name, health)

    def _should_restart_service(self, health: ServiceHealth, current_time: float) -> bool:
        """Determine if a service should be restarted."""
        # Don't restart if already at max attempts
        if health.restart_count >= self.max_restart_attempts:
            return False

        # Don't restart if in cooldown period
        if health.last_restart and (current_time - health.last_restart) < self.restart_cooldown:
            return False

        # Restart failed critical services immediately
        if (
            health.criticality == ServiceCriticality.CRITICAL
            and health.status == ServiceStatus.FAILED
        ):
            return True

        # Restart failed important services with delay
        return (
            health.criticality == ServiceCriticality.IMPORTANT
            and health.status == ServiceStatus.FAILED
        )

    async def _restart_service(self, service_name: str, health: ServiceHealth):
        """Attempt to restart a service."""
        try:
            logger.info(f"🔄 Attempting to restart service: {service_name}")

            registry = await get_service_registry()
            if not registry:
                logger.error("Cannot restart service: registry not available")
                return

            service_info = registry.get_service_info(service_name)
            if service_info and hasattr(service_info.instance, "restart"):
                # Attempt restart
                await service_info.instance.restart()

                # Update restart tracking
                health.restart_count += 1
                health.last_restart = time.time()

                logger.info(
                    f"✅ Service restart initiated: {service_name} (attempt {health.restart_count})"
                )

                # Wait a moment for restart to take effect
                await asyncio.sleep(2.0)

            else:
                logger.warning(f"⚠️ Service {service_name} does not support restart")

                # Mark as maximum attempts to prevent further restart attempts
                health.restart_count = self.max_restart_attempts
                health.last_restart = time.time()

                # If it's not critical, mark as degraded instead of failed to avoid restart loops
                if health.criticality != ServiceCriticality.CRITICAL:
                    health.status = ServiceStatus.DEGRADED
                    logger.info(
                        f"🟡 Service {service_name} marked as degraded (no restart support)"
                    )

        except Exception as e:
            logger.error(f"Failed to restart service {service_name}: {e}")
            health.error_count += 1

            # Also increment restart count to prevent immediate retry
            health.restart_count += 1
            health.last_restart = time.time()

    def _update_stability_metrics(self):
        """Update stability metrics for reporting."""
        current_time = time.time()

        # Calculate uptime
        boot_uptime = current_time - self.boot_start_time if self.boot_start_time else 0.0
        online_uptime = current_time - self.online_since if self.online_since else 0.0

        # Count service statistics
        service_stats = {
            "total": len(self.service_health),
            "healthy": sum(
                1 for h in self.service_health.values() if h.status == ServiceStatus.HEALTHY
            ),
            "degraded": sum(
                1 for h in self.service_health.values() if h.status == ServiceStatus.DEGRADED
            ),
            "failed": sum(
                1 for h in self.service_health.values() if h.status == ServiceStatus.FAILED
            ),
        }

        # Calculate restart statistics
        restart_stats = {
            "total_restarts": sum(h.restart_count for h in self.service_health.values()),
            "services_restarted": sum(
                1 for h in self.service_health.values() if h.restart_count > 0
            ),
        }

        self.stability_metrics = {
            "runlevel": self.current_runlevel.value,
            "boot_uptime": boot_uptime,
            "online_uptime": online_uptime,
            "service_stats": service_stats,
            "restart_stats": restart_stats,
            "runlevel_changes": len(self.runlevel_history),
            "last_update": current_time,
        }

    async def verify_all_systems_active(self) -> Dict[str, Any]:
        """
        Verify all critical systems are active and performing their tasks.

        This is the core self-verification method from Phase 2 of the roadmap.
        Returns comprehensive verification results.
        """
        verification_results: Dict[str, Any] = {
            "timestamp": time.time(),
            "overall_status": "unknown",
            "systems": {},
            "vital_checks": {},
            "corrective_actions": [],
        }

        try:
            # 1. Memory coherence check
            memory_result = await self._verify_memory_coherence()
            verification_results["vital_checks"]["memory_coherence"] = memory_result

            # 2. Plugin queue drain check
            plugin_result = await self._verify_plugin_queue_health()
            verification_results["vital_checks"]["plugin_queue"] = plugin_result

            # 3. Lyrixa heartbeat check
            lyrixa_result = await self._verify_lyrixa_heartbeat()
            verification_results["vital_checks"]["lyrixa_heartbeat"] = lyrixa_result

            # 4. Hub link check
            hub_result = await self._verify_hub_connectivity()
            verification_results["vital_checks"]["hub_link"] = hub_result

            # 5. Service health verification
            service_result = await self._verify_service_health()
            verification_results["systems"] = service_result

            # Determine overall status
            all_vital_healthy = all(
                check.get("status") == "healthy"
                for check in verification_results["vital_checks"].values()
            )
            critical_services_healthy = service_result.get("critical_services_healthy", 0)
            total_critical = service_result.get("critical_services_total", 1)

            if all_vital_healthy and critical_services_healthy == total_critical:
                verification_results["overall_status"] = "healthy"
            elif critical_services_healthy > 0:
                verification_results["overall_status"] = "degraded"
            else:
                verification_results["overall_status"] = "failed"

            # Log verification results
            status = verification_results["overall_status"]
            logger.info(f"🔍 System verification complete: {status.upper()}")

            if status != "healthy":
                failed_checks = [
                    name
                    for name, check in verification_results["vital_checks"].items()
                    if check.get("status") != "healthy"
                ]
                if failed_checks:
                    logger.warning(f"⚠️ Failed vital checks: {', '.join(failed_checks)}")

        except Exception as e:
            logger.error(f"❌ System verification failed: {e}")
            verification_results["overall_status"] = "error"
            verification_results["error"] = str(e)

        return verification_results

    async def _verify_memory_coherence(self) -> Dict[str, Any]:
        """Verify memory system coherence."""
        try:
            registry = await get_service_registry()
            if not registry:
                logger.debug("[HEALTH] Memory coherence check: registry unavailable")
                return {"status": "failed", "reason": "registry_unavailable"}

            memory_service = registry.get_service_info("memory_system")
            if not memory_service:
                logger.debug("[HEALTH] Memory coherence check: service not found")
                return {"status": "failed", "reason": "service_not_found"}

            # Check basic memory service health
            if memory_service.status.value != "healthy":
                logger.debug(
                    f"[HEALTH] Memory coherence check: service status={memory_service.status.value}"
                )
                return {"status": "degraded", "reason": f"status_{memory_service.status.value}"}

            # If the memory service has a coherence check method, use it
            if hasattr(memory_service.instance, "check_coherence"):
                coherence_ok = await memory_service.instance.check_coherence()
                if not coherence_ok:
                    logger.debug("[HEALTH] Memory coherence check: coherence check failed")
                    return {"status": "degraded", "reason": "coherence_check_failed"}

            return {"status": "healthy", "uptime": getattr(memory_service, "uptime", 0)}

        except Exception as e:
            logger.warning(f"[HEALTH] Memory coherence check exception: {e}", exc_info=True)
            return {"status": "error", "reason": str(e)}

    async def _verify_plugin_queue_health(self) -> Dict[str, Any]:
        """Verify plugin system queue is draining properly."""
        try:
            registry = await get_service_registry()
            if not registry:
                logger.debug("[HEALTH] Plugin queue check: registry unavailable")
                return {"status": "failed", "reason": "registry_unavailable"}

            plugin_service = registry.get_service_info("plugin_manager")
            if not plugin_service:
                logger.debug("[HEALTH] Plugin queue check: service not found")
                return {"status": "failed", "reason": "service_not_found"}

            # Check plugin manager health
            if plugin_service.status.value not in ["healthy", "starting"]:
                logger.debug(
                    f"[HEALTH] Plugin queue check: service status={plugin_service.status.value}"
                )
                return {"status": "degraded", "reason": f"status_{plugin_service.status.value}"}

            # If plugin manager has queue health check, use it
            if hasattr(plugin_service.instance, "get_queue_health"):
                queue_health = await plugin_service.instance.get_queue_health()
                if queue_health.get("status") != "healthy":
                    logger.debug(f"[HEALTH] Plugin queue check: queue unhealthy: {queue_health}")
                    return {
                        "status": "degraded",
                        "reason": "queue_unhealthy",
                        "details": queue_health,
                    }

            return {"status": "healthy", "service_status": plugin_service.status.value}

        except Exception as e:
            logger.warning(f"[HEALTH] Plugin queue check exception: {e}", exc_info=True)
            return {"status": "error", "reason": str(e)}

    async def _verify_lyrixa_heartbeat(self) -> Dict[str, Any]:
        """Verify Lyrixa system heartbeat."""
        try:
            registry = await get_service_registry()
            if not registry:
                return {"status": "failed", "reason": "registry_unavailable"}

            lyrixa_service = registry.get_service_info("lyrixa_chat")
            if not lyrixa_service:
                return {"status": "failed", "reason": "service_not_found"}

            # Check Lyrixa service health
            if lyrixa_service.status.value not in ["healthy", "starting"]:
                return {"status": "degraded", "reason": f"status_{lyrixa_service.status.value}"}

            # Check heartbeat timing
            current_time = time.time()
            service_health = self.service_health.get("lyrixa_chat")
            if service_health:
                heartbeat_age = current_time - service_health.last_heartbeat
                if heartbeat_age > self.heartbeat_timeout:
                    return {"status": "degraded", "reason": "heartbeat_stale", "age": heartbeat_age}

            return {"status": "healthy", "service_status": lyrixa_service.status.value}

        except Exception as e:
            return {"status": "error", "reason": str(e)}

    async def _verify_hub_connectivity(self) -> Dict[str, Any]:
        """Verify Hub connectivity."""
        try:
            registry = await get_service_registry()
            if not registry:
                logger.debug("[HEALTH] Hub connectivity check: registry unavailable")
                return {"status": "failed", "reason": "registry_unavailable"}

            hub_service = registry.get_service_info("aetherra_hub")
            if not hub_service:
                logger.debug("[HEALTH] Hub connectivity check: service not found")
                return {"status": "failed", "reason": "service_not_found"}

            # Check Hub service health
            if hub_service.status.value not in ["healthy", "starting"]:
                logger.debug(
                    f"[HEALTH] Hub connectivity check: service status={hub_service.status.value}"
                )
                return {"status": "degraded", "reason": f"status_{hub_service.status.value}"}

            # Additional connectivity check - try to ping hub if possible
            if hasattr(hub_service.instance, "ping"):
                ping_result = await hub_service.instance.ping()
                if not ping_result:
                    logger.debug("[HEALTH] Hub connectivity check: ping failed")
                    return {"status": "degraded", "reason": "ping_failed"}

            return {"status": "healthy", "service_status": hub_service.status.value}

        except Exception as e:
            logger.warning(f"[HEALTH] Hub connectivity check exception: {e}", exc_info=True)
            return {"status": "error", "reason": str(e)}

    async def _verify_service_health(self) -> Dict[str, Any]:
        """Verify overall service health status."""
        health_summary = self._assess_system_health()

        return {
            "total_services": health_summary["total_services"],
            "healthy_services": health_summary["healthy_services"],
            "degraded_services": health_summary["degraded_services"],
            "failed_services": health_summary["failed_services"],
            "critical_services_healthy": health_summary["critical_services_healthy"],
            "critical_services_total": health_summary["critical_services_total"],
            "health_percentage": health_summary["health_percentage"],
            "critical_health_percentage": health_summary["critical_health_percentage"],
        }

    async def heartbeat_all(self):
        """
        Send periodic liveness pings to each subsystem.

        This ensures timely detection of silent failures as recommended
        in the roadmap.
        """
        try:
            registry = await get_service_registry()
            if not registry:
                logger.warning("⚠️ Cannot send heartbeats: registry unavailable")
                return

            heartbeat_results = {}
            current_time = time.time()

            for service_name in self.service_health:
                try:
                    service_info = registry.get_service_info(service_name)
                    if service_info and hasattr(service_info.instance, "heartbeat"):
                        # Send heartbeat ping
                        response = await service_info.instance.heartbeat()
                        heartbeat_results[service_name] = {
                            "status": "success" if response else "failed",
                            "timestamp": current_time,
                        }

                        # Update our tracking
                        self.service_health[service_name].last_heartbeat = current_time

                    else:
                        # Service doesn't support heartbeat, just update timestamp based on registry
                        if service_info:
                            heartbeat_results[service_name] = {
                                "status": "registry_based",
                                "timestamp": current_time,
                            }
                            self.service_health[service_name].last_heartbeat = current_time

                except Exception as e:
                    logger.debug(f"Heartbeat failed for {service_name}: {e}")
                    heartbeat_results[service_name] = {
                        "status": "error",
                        "error": str(e),
                        "timestamp": current_time,
                    }

            logger.debug(f"💓 Heartbeat complete: {len(heartbeat_results)} services pinged")

        except Exception as e:
            logger.error(f"❌ Heartbeat operation failed: {e}")

    def _log_periodic_status(self):
        """Log periodic status information."""
        # Log detailed status every 5 minutes
        if hasattr(self, "_last_detailed_log") and time.time() - self._last_detailed_log < 300.0:
            return

        self._last_detailed_log = time.time()

        health_summary = self._assess_system_health()

        logger.info(f"🎯 System Status: {self.current_runlevel.value}")
        logger.info(
            f"📊 Health: {health_summary['health_percentage']:.1f}% "
            f"({health_summary['healthy_services']}/{health_summary['total_services']} services)"
        )
        logger.info(
            f"🔥 Critical: {health_summary['critical_health_percentage']:.1f}% "
            f"({health_summary['critical_services_healthy']}/{health_summary['critical_services_total']} services)"
        )

        if self.online_since:
            online_duration = time.time() - self.online_since
            logger.info(f"⏱️ Online for: {timedelta(seconds=int(online_duration))}")

    def _get_services_summary(self) -> Dict[str, Any]:
        """Get summary of all services for reporting."""
        summary = {}

        for service_name, health in self.service_health.items():
            summary[service_name] = {
                "status": health.status.value,
                "criticality": health.criticality.value,
                "uptime": health.uptime,
                "restart_count": health.restart_count,
                "error_count": health.error_count,
            }

        return summary

    # Public Interface Methods

    def get_runlevel(self) -> SystemRunlevel:
        """Get current system runlevel."""
        return self.current_runlevel

    def is_system_online(self) -> bool:
        """Check if system is in ONLINE runlevel."""
        return self.current_runlevel == SystemRunlevel.ONLINE

    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        health_summary = self._assess_system_health()

        return {
            "runlevel": self.current_runlevel.value,
            "online": self.is_system_online(),
            "online_since": self.online_since,
            "boot_time": self.boot_start_time,
            "health_summary": health_summary,
            "services": self._get_services_summary(),
            "stability_metrics": self.stability_metrics,
            "recent_transitions": self.runlevel_history[-5:] if self.runlevel_history else [],
        }

    def get_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get health information for a specific service."""
        if service_name not in self.service_health:
            return None

        health = self.service_health[service_name]
        return {
            "service_name": service_name,
            "status": health.status.value,
            "criticality": health.criticality.value,
            "last_heartbeat": health.last_heartbeat,
            "uptime": health.uptime,
            "restart_count": health.restart_count,
            "last_restart": health.last_restart,
            "error_count": health.error_count,
        }

    def force_runlevel_transition(
        self, target_level: SystemRunlevel, reason: str = "Manual override"
    ):
        """Force a runlevel transition (use with caution)."""
        if target_level != self.current_runlevel:
            logger.warning(f"🔧 Forcing runlevel transition to {target_level.value}: {reason}")
            self.target_runlevel = target_level
            # The next supervision cycle will handle the transition

    def enter_maintenance_mode(self):
        """Enter maintenance mode (reduces automatic actions)."""
        self.maintenance_mode = True
        logger.info("🔧 Entered maintenance mode")

    def exit_maintenance_mode(self):
        """Exit maintenance mode."""
        self.maintenance_mode = False
        logger.info("✅ Exited maintenance mode")

    def get_supervisor_status(self) -> Dict[str, Any]:
        """Get comprehensive supervisor status."""
        return {
            "running": self.running,
            "current_runlevel": self.current_runlevel.value,
            "target_runlevel": self.target_runlevel.value,
            "maintenance_mode": self.maintenance_mode,
            "boot_start_time": self.boot_start_time,
            "online_since": self.online_since,
            "services_tracked": len(self.service_health),
            "required_services": list(self.required_services),
            "runlevel_transitions": len(self.runlevel_history),
            "health_check_interval": self.health_check_interval,
        }


# Global instance for easy access
_system_supervisor: Optional[SystemSupervisor] = None


def get_system_supervisor() -> SystemSupervisor:
    """Get the global system supervisor instance."""
    global _system_supervisor
    if _system_supervisor is None:
        _system_supervisor = SystemSupervisor()
    return _system_supervisor


if __name__ == "__main__":
    # Test the system supervisor
    import asyncio

    async def test_supervisor():
        supervisor = SystemSupervisor()
        print(f"Supervisor status: {supervisor.get_supervisor_status()}")
        print(f"System health: {supervisor.get_system_health()}")

    asyncio.run(test_supervisor())
