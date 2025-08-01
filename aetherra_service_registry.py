#!/usr/bin/env python3
"""
🌐 Aetherra Service Registry
============================
Live service registration and inter-component communication system.

Enables all Aetherra components to discover, communicate, and coordinate
with each other in real-time.
"""

import asyncio
import logging
import weakref
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

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
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


class AetherraServiceRegistry:
    """
    🌐 Central Service Registry

    Manages service discovery, health monitoring, and inter-service communication
    for all Aetherra components.
    """

    def __init__(self):
        self._services: Dict[str, ServiceInfo] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._heartbeat_task = None

    async def start(self):
        """🚀 Start the service registry."""
        logger.info("🌐 Starting Aetherra Service Registry...")
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        logger.info("✅ Service Registry is now online")

    async def stop(self):
        """🛑 Stop the service registry."""
        logger.info("🛑 Stopping Service Registry...")
        self._running = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # Notify all services of shutdown
        await self._broadcast_event("system.shutdown", {})

        logger.info("✅ Service Registry stopped")

    async def register_service(
        self,
        name: str,
        instance: Any,
        metadata: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
    ) -> bool:
        """
        📝 Register a service with the registry.

        Args:
            name: Unique service name
            instance: Service instance
            metadata: Service metadata (version, description, etc.)
            dependencies: List of service names this service depends on

        Returns:
            True if registration successful
        """
        try:
            if name in self._services:
                logger.warning(f"⚠️ Service {name} already registered, updating...")

            service_info = ServiceInfo(
                name=name,
                instance=instance,
                metadata=metadata or {},
                dependencies=dependencies or [],
            )

            self._services[name] = service_info

            logger.info(f"✅ Service '{name}' registered successfully")

            # Broadcast registration event
            await self._broadcast_event(
                "service.registered", {"service_name": name, "metadata": metadata}
            )

            # Check if this registration satisfies any pending dependencies
            await self._check_dependencies()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to register service '{name}': {e}")
            return False

    async def unregister_service(self, name: str) -> bool:
        """
        🗑️ Unregister a service from the registry.

        Args:
            name: Service name to unregister

        Returns:
            True if unregistration successful
        """
        try:
            if name not in self._services:
                logger.warning(f"⚠️ Service '{name}' not found for unregistration")
                return False

            # Update status to stopping
            self._services[name].status = ServiceStatus.STOPPING

            # Broadcast unregistration event
            await self._broadcast_event("service.unregistering", {"service_name": name})

            # Remove from registry
            del self._services[name]

            logger.info(f"✅ Service '{name}' unregistered successfully")

            # Broadcast completion
            await self._broadcast_event("service.unregistered", {"service_name": name})

            return True

        except Exception as e:
            logger.error(f"❌ Failed to unregister service '{name}': {e}")
            return False

    def get_service(self, name: str) -> Optional[Any]:
        """
        🔍 Get a service instance by name.

        Args:
            name: Service name

        Returns:
            Service instance or None if not found
        """
        service_info = self._services.get(name)
        if service_info and service_info.status == ServiceStatus.HEALTHY:
            return service_info.instance
        return None

    def get_service_info(self, name: str) -> Optional[ServiceInfo]:
        """
        📋 Get service information by name.

        Args:
            name: Service name

        Returns:
            ServiceInfo or None if not found
        """
        return self._services.get(name)

    def list_services(
        self, status_filter: Optional[ServiceStatus] = None
    ) -> Dict[str, ServiceInfo]:
        """
        📜 List all registered services.

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
        self, name: str, status: ServiceStatus, metadata: Optional[Dict] = None
    ):
        """
        📊 Update service status and metadata.

        Args:
            name: Service name
            status: New status
            metadata: Optional metadata updates
        """
        if name not in self._services:
            logger.warning(f"⚠️ Cannot update status for unknown service '{name}'")
            return

        old_status = self._services[name].status
        self._services[name].status = status
        self._services[name].last_heartbeat = datetime.now()

        if metadata:
            self._services[name].metadata.update(metadata)

        if old_status != status:
            logger.info(
                f"📊 Service '{name}' status: {old_status.value} → {status.value}"
            )

            # Broadcast status change
            await self._broadcast_event(
                "service.status_changed",
                {
                    "service_name": name,
                    "old_status": old_status.value,
                    "new_status": status.value,
                    "metadata": metadata,
                },
            )

    async def send_message(
        self, target_service: str, message_type: str, data: Any
    ) -> bool:
        """
        📤 Send a message to a specific service.

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
                    f"⚠️ Cannot send message to unknown service '{target_service}'"
                )
                return False

            # Check if service has message handler
            if hasattr(service, "handle_message"):
                await service.handle_message(message_type, data)
                return True
            elif hasattr(service, "on_message"):
                await service.on_message(message_type, data)
                return True
            else:
                logger.warning(f"⚠️ Service '{target_service}' has no message handler")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to send message to '{target_service}': {e}")
            return False

    async def broadcast_message(
        self, message_type: str, data: Any, exclude: Optional[List[str]] = None
    ):
        """
        📢 Broadcast a message to all services.

        Args:
            message_type: Type of message
            data: Message data
            exclude: Optional list of service names to exclude
        """
        exclude = exclude or []

        for service_name, service_info in self._services.items():
            if service_name in exclude or service_info.status != ServiceStatus.HEALTHY:
                continue

            try:
                await self.send_message(service_name, message_type, data)
            except Exception as e:
                logger.error(f"❌ Failed to broadcast to '{service_name}': {e}")

    def subscribe_to_events(self, event_type: str, handler: Callable):
        """
        🔔 Subscribe to registry events.

        Args:
            event_type: Event type to subscribe to
            handler: Event handler function
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []

        self._event_handlers[event_type].append(handler)
        logger.debug(f"🔔 Subscribed to event '{event_type}'")

    def unsubscribe_from_events(self, event_type: str, handler: Callable):
        """
        🔕 Unsubscribe from registry events.

        Args:
            event_type: Event type to unsubscribe from
            handler: Event handler function to remove
        """
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
                logger.debug(f"🔕 Unsubscribed from event '{event_type}'")
            except ValueError:
                logger.warning(f"⚠️ Handler not found for event '{event_type}'")

    async def _broadcast_event(self, event_type: str, event_data: Dict[str, Any]):
        """📢 Broadcast an event to all subscribers."""
        if event_type not in self._event_handlers:
            return

        for handler in self._event_handlers[event_type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as e:
                logger.error(f"❌ Event handler error for '{event_type}': {e}")

    async def _heartbeat_monitor(self):
        """💓 Monitor service heartbeats and health."""
        while self._running:
            try:
                current_time = datetime.now()

                for service_name, service_info in self._services.items():
                    # Check for stale heartbeats (no update in 5 minutes)
                    if (current_time - service_info.last_heartbeat).seconds > 300:
                        if service_info.status == ServiceStatus.HEALTHY:
                            logger.warning(
                                f"⚠️ Service '{service_name}' heartbeat stale, marking as degraded"
                            )
                            await self.update_service_status(
                                service_name, ServiceStatus.DEGRADED
                            )

                    # Check if service instance is still alive
                    if hasattr(service_info.instance, "is_alive"):
                        try:
                            if not service_info.instance.is_alive():
                                logger.error(
                                    f"❌ Service '{service_name}' is no longer alive, marking as failed"
                                )
                                await self.update_service_status(
                                    service_name, ServiceStatus.FAILED
                                )
                        except Exception:
                            pass

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"❌ Heartbeat monitor error: {e}")
                await asyncio.sleep(60)

    async def _check_dependencies(self):
        """🔗 Check if service dependencies are satisfied."""
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

    def get_registry_status(self) -> Dict[str, Any]:
        """📊 Get overall registry status."""
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
                }
                for name, info in self._services.items()
            },
        }


# Global service registry instance
_service_registry: Optional[AetherraServiceRegistry] = None


async def get_service_registry() -> AetherraServiceRegistry:
    """🌐 Get the global service registry instance."""
    global _service_registry
    if _service_registry is None:
        _service_registry = AetherraServiceRegistry()
        await _service_registry.start()
    return _service_registry


async def register_service(name: str, instance: Any, **kwargs) -> bool:
    """📝 Register a service with the global registry."""
    registry = await get_service_registry()
    return await registry.register_service(name, instance, **kwargs)


async def get_service(name: str) -> Optional[Any]:
    """🔍 Get a service from the global registry."""
    registry = await get_service_registry()
    return registry.get_service(name)


async def shutdown_service_registry():
    """🛑 Shutdown the global service registry."""
    global _service_registry
    if _service_registry:
        await _service_registry.stop()
        _service_registry = None


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
        print("✅ Service registry test completed")

    asyncio.run(test_registry())
