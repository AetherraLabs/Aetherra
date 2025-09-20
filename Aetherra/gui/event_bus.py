#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🚌 EventBus - Unified GUI Event System
======================================

Bridges Qt signals with async messaging for unified event handling.
Implements the communication backbone for the GUI architecture.

Key Features:
- Qt signal to async event bridging
- Type-safe event definitions
- Subscription management with weak references
- Event filtering and transformation
- Performance monitoring and debugging
"""

from __future__ import annotations

# Standard library imports
import asyncio
import logging
import weakref
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from types import MethodType
from typing import Any, Protocol
from uuid import uuid4

# Third party imports
from PySide6.QtCore import QObject, Signal, Slot

logger = logging.getLogger(__name__)


class _ConnectableSignal(Protocol):
    def connect(self, slot: Callable[..., Any]) -> Any:
        ...


class EventPriority(Enum):
    """Event priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """Base event class with common attributes."""

    id: str
    type: str
    source: str
    timestamp: float
    priority: EventPriority = EventPriority.NORMAL
    data: dict[str, Any] | None = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class LayoutEvent(Event):
    """Layout-related events."""

    zone_id: str | None = None
    layout_mode: str | None = None


@dataclass
class PluginEvent(Event):
    """Plugin-related events."""

    # Default provided to satisfy dataclass ordering (base class has defaulted fields).
    plugin_id: str = ""
    state: str | None = None
    error: str | None = None


@dataclass
class ChatEvent(Event):
    """Chat-related events."""

    message: str | None = None
    user_id: str | None = None
    thread_id: str | None = None


@dataclass
class PerformanceEvent(Event):
    """Performance monitoring events."""

    # Defaults added to satisfy dataclass field ordering after base class defaults.
    metric_name: str = ""
    value: float = 0.0
    unit: str = "ms"


class EventSubscription:
    """Manages event subscription with weak references."""

    def __init__(
        self,
        event_type: type[Event],
        callback: Callable,
        filter_func: Callable | None = None,
    ):
        self.id = str(uuid4())
        self.event_type = event_type
        self.filter_func = filter_func
        # Use weak reference to prevent memory leaks
        if isinstance(callback, MethodType):
            # Bound method - store weak reference to object and method name
            self.obj_ref = weakref.ref(callback.__self__)
            self.method_name = callback.__name__
            self.callback = None
        else:
            # Function or other callable - attempt weak reference, fallback to strong reference wrapper
            self.obj_ref = None
            self.method_name = None
            try:
                self.callback = weakref.ref(callback)  # type: ignore[arg-type]
            except TypeError:
                # Fallback strong reference via closure when weakref is not supported
                self.callback = lambda: callback

    def is_alive(self) -> bool:
        """Check if the subscription is still valid."""
        if self.obj_ref:
            return self.obj_ref() is not None
        if self.callback:
            try:
                return self.callback() is not None
            except TypeError:
                # If callback is a direct function (strong ref), consider it alive
                return True
        return False

    def get_callback(self) -> Callable | None:
        """Get the actual callback function."""
        if self.obj_ref:
            obj = self.obj_ref()
            if obj and self.method_name is not None:
                # self.method_name is guaranteed to be str in this branch
                return getattr(obj, self.method_name)
            return None
        if self.callback:
            return self.callback()
        return None

    def matches(self, event: Event) -> bool:
        """Check if this subscription should receive the event."""
        if not isinstance(event, self.event_type):
            return False

        if self.filter_func:
            try:
                return self.filter_func(event)
            except Exception as e:
                logger.warning(f"Event filter error: {e}")
                return False

        return True


class QtSignalBridge(QObject):
    """Bridges Qt signals to the event bus."""

    # Generic signal for all events
    event_emitted = Signal(object)  # Event

    def __init__(self, event_bus: EventBus):
        super().__init__()
        self.event_bus = event_bus

    def emit_event(self, event: Event) -> None:
        """Emit an event via Qt signal."""
        self.event_emitted.emit(event)

    def bridge_signal(
        self, qt_signal: _ConnectableSignal, event_factory: Callable[..., Event]
    ) -> None:
        """Bridge a Qt signal (any object with a connect() method) to create events."""

        def signal_handler(*args):
            try:
                event = event_factory(*args)
                # Forward to bus (which will also emit back to Qt via emit_event)
                self.event_bus.publish(event)
            except Exception as e:
                logger.error(f"Signal bridge error: {e}")

        qt_signal.connect(signal_handler)


class EventBus(QObject):
    """
    Unified event bus for GUI communication.

    Bridges Qt signals with async messaging for seamless integration
    between synchronous Qt widgets and asynchronous backend services.
    """

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self._subscriptions: dict[type[Event], list[EventSubscription]] = {}
        self._event_queue: asyncio.Queue[Event] | None = None
        self._stats = {
            "events_emitted": 0,
            "events_processed": 0,
            "subscription_count": 0,
        }

        # Qt signal bridge
        self._qt_bridge = QtSignalBridge(self)
        self._qt_bridge.event_emitted.connect(self._on_qt_event)

        logger.info("EventBus initialized")

    def publish(self, event: Event) -> None:
        """Publish (emit) an event to all subscribers (renamed from 'emit' to avoid QObject.emit override)."""
        logger.debug(f"Emitting event: {event.type} from {event.source}")
        self._stats["events_emitted"] += 1

        # Process subscriptions
        subscriptions = self._subscriptions.get(type(event), [])

        # Remove dead subscriptions
        live_subscriptions = []
        for sub in subscriptions:
            if sub.is_alive():
                live_subscriptions.append(sub)
            else:
                logger.debug(f"Removing dead subscription: {sub.id}")

        self._subscriptions[type(event)] = live_subscriptions

        # Notify subscribers
        for sub in live_subscriptions:
            if sub.matches(event):
                callback = sub.get_callback()
                if callback:
                    try:
                        callback(event)
                        self._stats["events_processed"] += 1
                    except Exception as e:
                        logger.error(f"Event callback error: {e}")

        # Bridge to Qt signals
        self._qt_bridge.emit_event(event)

        # Add to async queue if available
        if self._event_queue:
            try:
                self._event_queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning("Event queue full, dropping event")

    def subscribe(
        self,
        event_type: type[Event],
        callback: Callable,
        filter_func: Callable | None = None,
    ) -> str:
        """Subscribe to events of a specific type."""
        subscription = EventSubscription(event_type, callback, filter_func)

        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []

        self._subscriptions[event_type].append(subscription)
        self._stats["subscription_count"] += 1

        logger.debug(f"Added subscription for {event_type.__name__}: {subscription.id}")
        return subscription.id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove a subscription by ID."""
        for _event_type, subscriptions in self._subscriptions.items():
            for i, sub in enumerate(subscriptions):
                if sub.id == subscription_id:
                    subscriptions.pop(i)
                    self._stats["subscription_count"] -= 1
                    logger.debug(f"Removed subscription: {subscription_id}")
                    return True
        return False

    def subscribe_qt_signal(
        self, qt_signal: _ConnectableSignal, event_factory: Callable[..., Event]
    ) -> None:
        """Subscribe a Qt signal (any object with connect()) to emit events."""
        self._qt_bridge.bridge_signal(qt_signal, event_factory)
        logger.debug("Bridged Qt signal to event factory")

    def enable_async_queue(self, maxsize: int = 1000) -> None:
        """Enable async event queue for coroutine integration."""
        self._event_queue = asyncio.Queue(maxsize=maxsize)
        logger.info(f"Enabled async event queue (maxsize={maxsize})")

    async def get_event(self) -> Event:
        """Get the next event from the async queue."""
        if not self._event_queue:
            raise RuntimeError("Async queue not enabled")
        return await self._event_queue.get()

    def get_stats(self) -> dict[str, Any]:
        """Get event bus statistics."""
        return self._stats.copy()

    def clear_subscriptions(self) -> None:
        """Clear all subscriptions (useful for testing)."""
        self._subscriptions.clear()
        self._stats["subscription_count"] = 0
        logger.info("Cleared all subscriptions")

    @Slot(object)
    def _on_qt_event(self, event: Event) -> None:
        """Handle events from Qt signals."""
        logger.debug(f"Received Qt event: {event.type}")


class EventFactory:
    """Factory for creating common event types."""

    @staticmethod
    def layout_changed(zone_id: str, source: str = "zone_manager") -> LayoutEvent:
        """Create a layout change event."""
        return LayoutEvent(
            id=str(uuid4()),
            type="layout_changed",
            source=source,
            timestamp=asyncio.get_event_loop().time(),
            zone_id=zone_id,
        )

    @staticmethod
    def layout_mode_changed(mode: str, source: str = "zone_manager") -> LayoutEvent:
        """Create a layout mode change event."""
        return LayoutEvent(
            id=str(uuid4()),
            type="layout_mode_changed",
            source=source,
            timestamp=asyncio.get_event_loop().time(),
            layout_mode=mode,
        )

    @staticmethod
    def plugin_loaded(plugin_id: str, source: str = "plugin_manager") -> PluginEvent:
        """Create a plugin loaded event."""
        return PluginEvent(
            id=str(uuid4()),
            type="plugin_loaded",
            source=source,
            timestamp=asyncio.get_event_loop().time(),
            plugin_id=plugin_id,
            state="loaded",
        )

    @staticmethod
    def plugin_error(
        plugin_id: str, error: str, source: str = "plugin_manager"
    ) -> PluginEvent:
        """Create a plugin error event."""
        return PluginEvent(
            id=str(uuid4()),
            type="plugin_error",
            source=source,
            timestamp=asyncio.get_event_loop().time(),
            priority=EventPriority.HIGH,
            plugin_id=plugin_id,
            error=error,
        )

    @staticmethod
    def chat_message(
        message: str,
        user_id: str | None = None,
        thread_id: str | None = None,
        source: str = "chat",
    ) -> ChatEvent:
        """Create a chat message event."""
        return ChatEvent(
            id=str(uuid4()),
            type="chat_message",
            source=source,
            timestamp=asyncio.get_event_loop().time(),
            message=message,
            user_id=user_id,
            thread_id=thread_id,
        )

    @staticmethod
    def performance_metric(
        metric_name: str, value: float, unit: str = "ms", source: str = "performance"
    ) -> PerformanceEvent:
        """Create a performance metric event."""
        return PerformanceEvent(
            id=str(uuid4()),
            type="performance_metric",
            source=source,
            timestamp=asyncio.get_event_loop().time(),
            metric_name=metric_name,
            value=value,
            unit=unit,
        )


# Global event bus instance
_global_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def emit_event(event: Event) -> None:
    """Convenience function to emit an event on the global bus."""
    get_event_bus().publish(event)


def subscribe_event(
    event_type: type[Event], callback: Callable, filter_func: Callable | None = None
) -> str:
    """Convenience function to subscribe to events on the global bus."""
    return get_event_bus().subscribe(event_type, callback, filter_func)
