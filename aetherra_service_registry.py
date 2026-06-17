#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
[REGISTRY] Aetherra Service Registry
============================
Live service registration and inter-component communication system.

Enables all Aetherra components to discover, communicate, and coordinate
with each other in real-time.
"""

# Standard library imports
import asyncio
import logging
import os
import time
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status enumeration."""

    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPING = "stopping"


@dataclass
class ServiceInfo:
    """Information about a registered service."""

    name: str
    instance: Any
    status: ServiceStatus = ServiceStatus.STARTING
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(
        default_factory=dict
    )  # may include 'self_heartbeat': bool
    dependencies: list[str] = field(default_factory=list)


class AetherraServiceRegistry:
    """
    [REGISTRY] Central Service Registry

    Manages service discovery, health monitoring, and inter-service communication
    for all Aetherra components.
    """

    def __init__(self):
        self._services: dict[str, ServiceInfo] = {}
        self._event_handlers: dict[str, list[Callable]] = {}
        self._running = False
        self._heartbeat_task = None
        # Heartbeat + staleness configuration
        # Heartbeat monitor runs every 60s today; we allow future tuning via env.
        # Stale threshold defaults to 3x declared heartbeat interval (safe early warning)
        try:
            self._heartbeat_interval_sec = int(
                os.environ.get("AETHERRA_REGISTRY_HEARTBEAT_SEC", "60") or 60
            )
        except Exception:
            self._heartbeat_interval_sec = 60
        try:
            self._stale_sec = int(
                os.environ.get(
                    "AETHERRA_REGISTRY_STALE_SEC",
                    str(self._heartbeat_interval_sec * 3),
                )
            )
        except Exception:
            self._stale_sec = self._heartbeat_interval_sec * 3
        # Canonical naming with legacy alias support
        # Legacy names map to professional canonical names
        self._legacy_alias_map: dict[str, str] = {
            "quantum_consciousness": "quantum_cognition",
            "cosmic_consciousness": "universal_cognition",
            "beyond_transcendence": "meta_cognition",
        }
        # Warning controls: by default, suppress repeated "no handler" warnings.
        # Set AETHERRA_REGISTRY_WARN_NO_HANDLER=1 to emit a warning once per service.
        self._warn_no_handler_once = (
            os.environ.get("AETHERRA_REGISTRY_WARN_NO_HANDLER", "0") == "1"
        )
        self._no_handler_warned: set[str] = set()
        # Additional noise controls:
        # - AETHERRA_REGISTRY_NO_HANDLER_SILENT=1 -> never log these lines
        # - AETHERRA_REGISTRY_NO_HANDLER_RATE_SEC=N -> rate-limit logs per service
        self._no_handler_silent = (
            os.environ.get("AETHERRA_REGISTRY_NO_HANDLER_SILENT", "0") == "1"
        )
        try:
            self._no_handler_rate_sec = int(
                os.environ.get("AETHERRA_REGISTRY_NO_HANDLER_RATE_SEC", "0") or 0
            )
        except Exception:
            self._no_handler_rate_sec = 0
        self._no_handler_last_log: dict[str, float] = {}

    def _canonical(self, name: str) -> str:
        try:
            # Allow disabling aliasing via env if needed
            if os.environ.get("AETHERRA_DISABLE_LEGACY_ALIASES", "0") == "1":
                return name
            return self._legacy_alias_map.get(name, name)
        except Exception:
            return name

    def _guardian_requester(self, metadata: dict[str, Any] | None = None) -> str:
        metadata = metadata or {}
        requester = metadata.get("guardian_requester") or metadata.get("requester")
        return str(requester or "service_registry").strip() or "service_registry"

    def _service_instance_type(self, instance: Any) -> str:
        cls = instance.__class__
        module = getattr(cls, "__module__", "") or "unknown"
        name = getattr(cls, "__name__", "") or "unknown"
        return f"{module}.{name}"

    def _registry_capability_checker(self, requester: str, capability: str) -> bool:
        if requester == "service_registry" and capability in {
            "registry:register",
            "registry:unregister",
            "registry:status",
            "registry:heartbeat",
            "registry:message",
            "registry:broadcast",
            "registry:subscribe",
        }:
            return True
        from Aetherra.security.capabilities import has_capability

        return has_capability(requester, capability)

    def _guardian_preflight(
        self,
        *,
        requester: str,
        action: str,
        service_name: str,
        purpose: str,
        capabilities: tuple[str, ...],
        reversible: bool,
        rollback_plan: str,
        metadata: dict[str, Any],
    ) -> None:
        from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

        decision = evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="service_registry",
                action=action,
                target="service_registry:service",
                purpose=purpose,
                capabilities=capabilities,
                evidence=(f"service_name:{service_name}",),
                reversible=reversible,
                rollback_plan=rollback_plan,
                metadata=metadata,
            ),
            capability_checker=self._registry_capability_checker,
        )
        if decision.status not in {
            GuardianStatus.ALLOW,
            GuardianStatus.ALLOW_LIMITED,
        }:
            raise PermissionError(
                f"Guardian denied service registry action {action}: {decision.reason}"
            )

    def _message_metadata(self, data: Any) -> dict[str, Any]:
        if isinstance(data, dict):
            return {
                "data_type": "dict",
                "data_keys": tuple(sorted(str(key) for key in data)),
                "data_size": len(data),
            }
        if isinstance(data, list | tuple | set):
            return {
                "data_type": type(data).__name__,
                "data_size": len(data),
            }
        return {
            "data_type": type(data).__name__,
            "data_size": 0 if data is None else len(str(data)),
        }

    def _handler_type(self, handler: Callable) -> str:
        module = getattr(handler, "__module__", "") or "unknown"
        name = getattr(handler, "__qualname__", None) or getattr(
            handler, "__name__", "unknown"
        )
        return f"{module}.{name}"

    def _should_log_no_handler(self, service_name: str) -> bool:
        if self._no_handler_silent:
            return False
        if self._warn_no_handler_once:
            # If warn-once is enabled, we log warning only once via _log_no_handler
            return service_name not in self._no_handler_warned
        # Otherwise, check rate-limit for debug logging
        if self._no_handler_rate_sec <= 0:
            return True
        now = time.time()
        last = self._no_handler_last_log.get(service_name, 0.0)
        return (now - last) >= max(1, self._no_handler_rate_sec)

    def _log_no_handler(self, service_name: str) -> None:
        if self._no_handler_silent:
            return
        if self._warn_no_handler_once:
            if service_name not in self._no_handler_warned:
                logger.warning(
                    f"[WARN] Service '{service_name}' has no message handler"
                )
                self._no_handler_warned.add(service_name)
                self._no_handler_last_log[service_name] = time.time()
            else:
                # Do not log repeated warnings when warn-once mode is on
                pass
            return
        # Default: debug log (suppressed) with optional rate limiting
        if self._should_log_no_handler(service_name):
            logger.debug(
                f"Service '{service_name}' has no message handler (suppressed)"
            )
            self._no_handler_last_log[service_name] = time.time()

    async def start(self):
        """[START] Start the service registry."""
        logger.info("[REGISTRY] Starting Aetherra Service Registry...")
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        logger.info("[OK] Service Registry is now online")

    async def stop(self):
        """[STOP] Stop the service registry."""
        logger.info("[STOP] Stopping Service Registry...")
        self._running = False

        if self._heartbeat_task:
            heartbeat_task = self._heartbeat_task
            self._heartbeat_task = None
            task_loop = heartbeat_task.get_loop()
            if not task_loop.is_closed():
                heartbeat_task.cancel()
                with suppress(asyncio.CancelledError):
                    await heartbeat_task

        # Notify all services of shutdown
        await self._broadcast_event("system.shutdown", {})

        logger.info("[OK] Service Registry stopped")

    async def register_service(
        self,
        name: str,
        instance: Any,
        metadata: dict[str, Any] | None = None,
        dependencies: list[str] | None = None,
    ) -> bool:
        """
        [REGISTER] Register a service with the registry.

        Args:
            name: Unique service name
            instance: Service instance
            metadata: Service metadata (version, description, etc.)
            dependencies: List of service names this service depends on

        Returns:
            True if registration successful
        """
        try:
            cname = self._canonical(name)
            md = metadata or {}
            self._guardian_preflight(
                requester=self._guardian_requester(md),
                action="service_registry.register",
                service_name=cname,
                purpose=f"Register service {cname}",
                capabilities=("registry:register",),
                reversible=True,
                rollback_plan="unregister the service or restore the previous registration",
                metadata={
                    "service_name": cname,
                    "already_registered": cname in self._services,
                    "metadata_keys": tuple(sorted(str(key) for key in md)),
                    "dependency_names": tuple(sorted(str(dep) for dep in dependencies or [])),
                    "instance_type": self._service_instance_type(instance),
                },
            )
            if cname in self._services:
                logger.warning(f"[WARN] Service {name} already registered, updating...")

            # Normalize explicit self-heartbeat flag to bool if present
            if "self_heartbeat" in md:
                with suppress(Exception):
                    md["self_heartbeat"] = bool(md.get("self_heartbeat"))

            service_info = ServiceInfo(
                name=cname,
                instance=instance,
                metadata=md,
                dependencies=dependencies or [],
            )

            self._services[cname] = service_info

            # If no dependencies are declared, mark service healthy immediately
            if not service_info.dependencies:
                service_info.status = ServiceStatus.HEALTHY

            logger.info(f"[OK] Service '{cname}' registered successfully")

            # Forward to shared registry daemon if configured
            try:
                # Aetherra imports
                from aetherra_registry_client import http_register_service

                # Extract endpoints from metadata if present
                endpoints = md.get("endpoints", {})
                http_register_service(
                    cname,
                    status=service_info.status.value,
                    metadata=md,
                    endpoints=endpoints if isinstance(endpoints, dict) else {},
                )
            except Exception as exc:
                logger.debug("Shared registry forward failed for %s: %s", cname, exc)

            # Broadcast registration event
            await self._broadcast_event(
                "service.registered",
                {"service_name": cname, "metadata": md},
            )

            # Check if this registration satisfies any pending dependencies
            await self._check_dependencies()

            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to register service '{name}': {e}")
            return False

    async def unregister_service(self, name: str) -> bool:
        """
        [UNREGISTER] Unregister a service from the registry.

        Args:
            name: Service name to unregister

        Returns:
            True if unregistration successful
        """
        try:
            cname = self._canonical(name)
            if cname not in self._services:
                logger.warning(f"[WARN] Service '{name}' not found for unregistration")
                return False

            service_info = self._services[cname]
            self._guardian_preflight(
                requester=self._guardian_requester(service_info.metadata),
                action="service_registry.unregister",
                service_name=cname,
                purpose=f"Unregister service {cname}",
                capabilities=("registry:unregister",),
                reversible=True,
                rollback_plan="re-register the service with its previous instance and metadata",
                metadata={
                    "service_name": cname,
                    "status": service_info.status.value,
                    "metadata_keys": tuple(sorted(str(key) for key in service_info.metadata)),
                    "dependency_names": tuple(sorted(str(dep) for dep in service_info.dependencies)),
                    "instance_type": self._service_instance_type(service_info.instance),
                },
            )

            # Update status to stopping
            service_info.status = ServiceStatus.STOPPING

            # Broadcast unregistration event
            await self._broadcast_event(
                "service.unregistering", {"service_name": cname}
            )

            # Remove from registry
            del self._services[cname]

            logger.info(f"[OK] Service '{cname}' unregistered successfully")

            # Broadcast completion
            await self._broadcast_event("service.unregistered", {"service_name": cname})

            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to unregister service '{name}': {e}")
            return False

    def get_service(self, name: str) -> Any | None:
        """
        [GET] Get a service instance by name.

        Args:
            name: Service name

        Returns:
            Service instance or None if not found
        """
        service_info = self._services.get(self._canonical(name))
        if service_info and service_info.status == ServiceStatus.HEALTHY:
            return service_info.instance
        return None

    def get_service_info(self, name: str) -> ServiceInfo | None:
        """
        [INFO] Get service information by name.

        Args:
            name: Service name

        Returns:
            ServiceInfo or None if not found
        """
        return self._services.get(self._canonical(name))

    def list_services(
        self, status_filter: ServiceStatus | None = None
    ) -> dict[str, ServiceInfo]:
        """
        [LIST] List all registered services.

        Args:
            status_filter: Optional status filter

        Returns:
            Dictionary of service name to ServiceInfo
        """
        if status_filter:
            return {
                name: info
                for name, info in self._services.items()
                if info.status == status_filter
            }
        return self._services.copy()

    async def update_service_status(
        self, name: str, status: ServiceStatus, metadata: dict | None = None
    ):
        """
        [STATUS] Update service status and metadata.

        Args:
            name: Service name
            status: New status
            metadata: Optional metadata updates
        """
        cname = self._canonical(name)
        if cname not in self._services:
            logger.warning(f"[WARN] Cannot update status for unknown service '{name}'")
            return

        service_info = self._services[cname]
        old_status = service_info.status
        metadata = metadata or {}
        self._guardian_preflight(
            requester=self._guardian_requester(metadata),
            action="service_registry.status_update",
            service_name=cname,
            purpose=f"Update service {cname} status",
            capabilities=("registry:status",),
            reversible=True,
            rollback_plan="restore the previous service status and metadata snapshot",
            metadata={
                "service_name": cname,
                "old_status": old_status.value,
                "new_status": status.value,
                "metadata_keys": tuple(sorted(str(key) for key in metadata)),
                "instance_type": self._service_instance_type(service_info.instance),
            },
        )
        service_info.status = status
        service_info.last_heartbeat = datetime.now()

        if metadata:
            service_info.metadata.update(metadata)

        if old_status != status:
            logger.info(
                f"[STATUS] Service '{cname}' status: {old_status.value} -> {status.value}"
            )

            # Broadcast status change
            await self._broadcast_event(
                "service.status_changed",
                {
                    "service_name": cname,
                    "old_status": old_status.value,
                    "new_status": status.value,
                    "metadata": metadata,
                },
            )

    async def update_heartbeat(self, name: str, requester: str | None = None):
        """[HEARTBEAT] Update service heartbeat timestamp."""
        cname = self._canonical(name)
        if cname not in self._services:
            logger.warning(
                f"[WARN] Cannot update heartbeat for unknown service '{name}'"
            )
            return

        service_info = self._services[cname]
        self._guardian_preflight(
            requester=str(requester or "service_registry").strip() or "service_registry",
            action="service_registry.heartbeat_update",
            service_name=cname,
            purpose=f"Update heartbeat for service {cname}",
            capabilities=("registry:heartbeat",),
            reversible=True,
            rollback_plan="restore the previous heartbeat timestamp from registry state",
            metadata={
                "service_name": cname,
                "status": service_info.status.value,
                "self_heartbeat": bool(service_info.metadata.get("self_heartbeat")),
                "instance_type": self._service_instance_type(service_info.instance),
            },
        )
        service_info.last_heartbeat = datetime.now()
        logger.debug(f"[HEARTBEAT] Heartbeat updated for service '{cname}'")

    # ---- Self-heartbeat API ----
    def mark_service_self_heartbeat(
        self, name: str, enabled: bool = True, requester: str | None = None
    ) -> bool:
        """Mark/unmark a service as self-heartbeating (registry won't passively refresh it).

        Returns True if the service metadata was updated.
        """
        cname = self._canonical(name)
        svc = self._services.get(cname)
        if not svc:
            return False
        try:
            self._guardian_preflight(
                requester=str(requester or "service_registry").strip() or "service_registry",
                action="service_registry.self_heartbeat_flag",
                service_name=cname,
                purpose=f"Update self-heartbeat flag for service {cname}",
                capabilities=("registry:heartbeat",),
                reversible=True,
                rollback_plan="restore the previous self-heartbeat metadata flag",
                metadata={
                    "service_name": cname,
                    "enabled": bool(enabled),
                    "previous_enabled": bool(svc.metadata.get("self_heartbeat")),
                    "instance_type": self._service_instance_type(svc.instance),
                },
            )
            svc.metadata["self_heartbeat"] = bool(enabled)
            return True
        except Exception:
            return False

    def is_self_heartbeating(self, name: str) -> bool:
        cname = self._canonical(name)
        svc = self._services.get(cname)
        if not svc:
            return False
        try:
            return bool(svc.metadata.get("self_heartbeat"))
        except Exception:
            return False

    async def send_message(
        self,
        target_service: str,
        message_type: str,
        data: Any,
        requester: str | None = None,
    ) -> bool:
        """
        [SEND] Send a message to a specific service.

        Args:
            target_service: Target service name
            message_type: Type of message
            data: Message data

        Returns:
            True if message was delivered
        """
        try:
            service = self.get_service(target_service)
            if not service:
                logger.warning(
                    f"[WARN] Cannot send message to unknown service '{target_service}'"
                )
                return False
            cname = self._canonical(target_service)
            service_info = self._services[cname]
            self._guardian_preflight(
                requester=str(requester or "service_registry").strip()
                or "service_registry",
                action="service_registry.send_message",
                service_name=cname,
                purpose=f"Dispatch registry message {message_type} to service {cname}",
                capabilities=("registry:message",),
                reversible=False,
                rollback_plan="message delivery cannot be automatically undone; handler must provide compensation if needed",
                metadata={
                    "service_name": cname,
                    "message_type": str(message_type),
                    "status": service_info.status.value,
                    "instance_type": self._service_instance_type(service_info.instance),
                    **self._message_metadata(data),
                },
            )

            # Check if service has message handler
            if hasattr(service, "handle_message"):
                await service.handle_message(message_type, data)
                return True
            if hasattr(service, "on_message"):
                await service.on_message(message_type, data)
                return True
            # Centralized no-handler logging
            self._log_no_handler(target_service)
            return False

        except Exception as e:
            logger.error(f"[ERROR] Failed to send message to '{target_service}': {e}")
            return False

    async def broadcast_message(
        self,
        message_type: str,
        data: Any,
        exclude: list[str] | None = None,
        requester: str | None = None,
    ):
        """
        [BROADCAST] Broadcast a message to all services.

        Args:
            message_type: Type of message
            data: Message data
            exclude: Optional list of service names to exclude
        """
        exclude = exclude or []
        self._guardian_preflight(
            requester=str(requester or "service_registry").strip() or "service_registry",
            action="service_registry.broadcast_message",
            service_name="*",
            purpose=f"Broadcast registry message {message_type}",
            capabilities=("registry:broadcast",),
            reversible=False,
            rollback_plan="broadcast delivery cannot be automatically undone; receivers must provide compensation if needed",
            metadata={
                "message_type": str(message_type),
                "exclude_count": len(exclude),
                "healthy_target_count": sum(
                    1
                    for name, info in self._services.items()
                    if name not in exclude and info.status == ServiceStatus.HEALTHY
                ),
                **self._message_metadata(data),
            },
        )

        for service_name, service_info in self._services.items():
            if service_name in exclude or service_info.status != ServiceStatus.HEALTHY:
                continue

            try:
                # Skip broadcast attempts for services that clearly don't support messaging
                inst = service_info.instance
                if not hasattr(inst, "handle_message") and not hasattr(
                    inst, "on_message"
                ):
                    # Centralized no-handler logging
                    self._log_no_handler(service_name)
                    continue
                await self.send_message(
                    service_name,
                    message_type,
                    data,
                    requester=requester,
                )
            except Exception as e:
                logger.error(f"[ERROR] Failed to broadcast to '{service_name}': {e}")

    def subscribe_to_events(
        self, event_type: str, handler: Callable, requester: str | None = None
    ):
        """
        [SUBSCRIBE] Subscribe to registry events.

        Args:
            event_type: Event type to subscribe to
            handler: Event handler function
        """
        self._guardian_preflight(
            requester=str(requester or "service_registry").strip() or "service_registry",
            action="service_registry.subscribe",
            service_name="event_bus",
            purpose=f"Subscribe handler to registry event {event_type}",
            capabilities=("registry:subscribe",),
            reversible=True,
            rollback_plan="unsubscribe the handler from the registry event",
            metadata={
                "event_type": str(event_type),
                "handler_type": self._handler_type(handler),
                "existing_handler_count": len(self._event_handlers.get(event_type, [])),
            },
        )
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []

        self._event_handlers[event_type].append(handler)
        logger.debug(f"[SUBSCRIBE] Subscribed to event '{event_type}'")

    def unsubscribe_from_events(
        self, event_type: str, handler: Callable, requester: str | None = None
    ):
        """
        [UNSUBSCRIBE] Unsubscribe from registry events.

        Args:
            event_type: Event type to unsubscribe from
            handler: Event handler function to remove
        """
        self._guardian_preflight(
            requester=str(requester or "service_registry").strip() or "service_registry",
            action="service_registry.unsubscribe",
            service_name="event_bus",
            purpose=f"Unsubscribe handler from registry event {event_type}",
            capabilities=("registry:subscribe",),
            reversible=True,
            rollback_plan="re-subscribe the handler to the registry event",
            metadata={
                "event_type": str(event_type),
                "handler_type": self._handler_type(handler),
                "existing_handler_count": len(self._event_handlers.get(event_type, [])),
            },
        )
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
                logger.debug(f"[UNSUBSCRIBE] Unsubscribed from event '{event_type}'")
            except ValueError:
                logger.warning(f"[WARN] Handler not found for event '{event_type}'")

    async def _broadcast_event(self, event_type: str, event_data: dict[str, Any]):
        """[BROADCAST] Broadcast an event to all subscribers."""
        if event_type not in self._event_handlers:
            return

        for handler in self._event_handlers[event_type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as e:
                logger.error(f"[ERROR] Event handler error for '{event_type}': {e}")

    async def _heartbeat_monitor(self):
        """[MONITOR] Monitor service heartbeats and health."""
        while self._running:
            try:
                current_time = datetime.now()

                for service_name, service_info in self._services.items():
                    # Check for stale heartbeats (no update in configured window)
                    if (
                        current_time - service_info.last_heartbeat
                    ).total_seconds() > self._stale_sec and service_info.status == ServiceStatus.HEALTHY:
                        logger.warning(
                            f"[WARN] Service '{service_name}' heartbeat stale (> {self._stale_sec}s), marking as degraded"
                        )
                        await self.update_service_status(
                            service_name, ServiceStatus.DEGRADED
                        )

                    # Check if service instance is still alive
                    if hasattr(service_info.instance, "is_alive"):
                        try:
                            if not service_info.instance.is_alive():
                                logger.error(
                                    f"[ERROR] Service '{service_name}' is no longer alive, marking as failed"
                                )
                                await self.update_service_status(
                                    service_name, ServiceStatus.FAILED
                                )
                        except Exception as exc:
                            logger.debug(
                                "Service liveness check failed for %s: %s",
                                service_name,
                                exc,
                            )

                await asyncio.sleep(self._heartbeat_interval_sec)

            except Exception as e:
                logger.error(f"[ERROR] Heartbeat monitor error: {e}")
                await asyncio.sleep(60)

    async def _check_dependencies(self):
        """[DEPS] Check if service dependencies are satisfied."""
        for service_name, service_info in self._services.items():
            if not service_info.dependencies:
                continue

            all_deps_satisfied = True
            for dep_name in service_info.dependencies:
                dep_service = self.get_service_info(dep_name)
                if not dep_service or dep_service.status != ServiceStatus.HEALTHY:
                    all_deps_satisfied = False
                    break

            # Update service status based on dependencies
            if all_deps_satisfied and service_info.status == ServiceStatus.STARTING:
                await self.update_service_status(service_name, ServiceStatus.HEALTHY)
            elif (
                not all_deps_satisfied and service_info.status == ServiceStatus.HEALTHY
            ):
                await self.update_service_status(service_name, ServiceStatus.DEGRADED)

    def get_registry_status(self) -> dict[str, Any]:
        """[STATUS] Get overall registry status."""
        service_count_by_status = {}
        for status in ServiceStatus:
            service_count_by_status[status.value] = len(
                [s for s in self._services.values() if s.status == status]
            )

        return {
            "running": self._running,
            "total_services": len(self._services),
            "service_count_by_status": service_count_by_status,
            "services": {
                name: {
                    "status": info.status.value,
                    "registered_at": info.registered_at.isoformat(),
                    "last_heartbeat": info.last_heartbeat.isoformat(),
                    "dependencies": info.dependencies,
                    "self_heartbeat": bool(info.metadata.get("self_heartbeat")),
                }
                for name, info in self._services.items()
            },
        }


# Global service registry instance
_service_registry: AetherraServiceRegistry | None = None


async def get_service_registry() -> AetherraServiceRegistry:
    """[GLOBAL] Get the global service registry instance."""
    global _service_registry
    if _service_registry is None:
        _service_registry = AetherraServiceRegistry()
        await _service_registry.start()
    return _service_registry


async def register_service(name: str, instance: Any, **kwargs) -> bool:
    """[REGISTER] Register a service with the global registry."""
    registry = await get_service_registry()
    return await registry.register_service(name, instance, **kwargs)


async def get_service(name: str) -> Any | None:
    """[GET] Get a service from the global registry."""
    registry = await get_service_registry()
    return registry.get_service(name)


async def update_heartbeat(name: str, requester: str | None = None):
    """[HEARTBEAT] Update service heartbeat in the global registry."""
    registry = await get_service_registry()
    await registry.update_heartbeat(name, requester=requester)


async def shutdown_service_registry():
    """[SHUTDOWN] Shutdown the global service registry."""
    global _service_registry
    if _service_registry:
        await _service_registry.stop()
        _service_registry = None


# Backwards compatibility alias
ServiceRegistry = AetherraServiceRegistry

if __name__ == "__main__":
    # Test the service registry
    async def test_registry():
        registry = AetherraServiceRegistry()
        await registry.start()

        # Test service registration
        class TestService:
            def __init__(self, name):
                self.name = name

            async def handle_message(self, msg_type, data):
                print(f"Service {self.name} received: {msg_type} - {data}")

        service1 = TestService("test1")
        service2 = TestService("test2")

        await registry.register_service("test1", service1, metadata={"version": "1.0"})
        await registry.register_service("test2", service2, dependencies=["test1"])

        # Update statuses
        await registry.update_service_status("test1", ServiceStatus.HEALTHY)
        await registry.update_service_status("test2", ServiceStatus.HEALTHY)

        # Test messaging
        await registry.send_message("test1", "hello", {"from": "test"})
        await registry.broadcast_message("broadcast", {"message": "Hello all!"})

        # Check status
        status = registry.get_registry_status()
        print(f"Registry status: {status}")

        await registry.stop()
        print("[OK] Service registry test completed")

    asyncio.run(test_registry())
