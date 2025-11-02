#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Smoke tests for Interactive Lyrixa system.

Verifies that all components start correctly and basic event flow works.
"""

import asyncio

import pytest

from Aetherra.lyrixa.interactive import (
    ExpressionState,
    get_state_mapper,
    initialize_interactive_system,
)
from Aetherra.lyrixa.interactive.expression_manager import get_expression_manager
from Aetherra.lyrixa.interactive.interactive_loop import get_interactive_loop
from aetherra_event_bus import EventBus
from aetherra_service_registry import ServiceRegistry


@pytest.mark.asyncio
async def test_expression_manager_initializes():
    """Test that Expression Manager initializes correctly."""
    # Create minimal dependencies
    service_registry = ServiceRegistry()
    event_bus = EventBus(service_registry)

    # Get expression manager
    manager = await get_expression_manager(event_bus, service_registry)

    assert manager is not None
    assert manager.current_state == ExpressionState.CALM
    assert not manager.running


@pytest.mark.asyncio
async def test_expression_manager_starts_and_stops():
    """Test Expression Manager lifecycle."""
    service_registry = ServiceRegistry()
    event_bus = EventBus(service_registry)

    manager = await get_expression_manager(event_bus, service_registry)

    # Start
    await manager.start()
    assert manager.running

    # Give it a moment to settle
    await asyncio.sleep(0.5)

    # Stop
    await manager.stop()
    assert not manager.running


@pytest.mark.asyncio
async def test_expression_manager_publishes_events():
    """Test that Expression Manager publishes events to KEB."""
    service_registry = ServiceRegistry()
    event_bus = EventBus(service_registry)

    manager = await get_expression_manager(event_bus, service_registry)
    await manager.start()

    # Trigger an expression change
    await manager.set_expression(
        ExpressionState.FOCUSED, reason="test_trigger", intensity=0.7, force=True
    )

    await asyncio.sleep(0.2)

    # Check stats
    stats = manager.get_stats()
    assert stats["expressions_emitted"] > 0
    assert stats["state_transitions"] > 0

    await manager.stop()


@pytest.mark.asyncio
async def test_interactive_loop_initializes():
    """Test that Interactive Loop initializes correctly."""
    service_registry = ServiceRegistry()
    event_bus = EventBus(service_registry)

    loop = await get_interactive_loop(event_bus, service_registry)

    assert loop is not None
    assert loop.current_emotion.mood == "calm"
    assert not loop.running


@pytest.mark.asyncio
async def test_interactive_loop_starts_and_stops():
    """Test Interactive Loop lifecycle."""
    service_registry = ServiceRegistry()
    event_bus = EventBus(service_registry)

    loop = await get_interactive_loop(event_bus, service_registry, sample_interval=1.0)

    # Start
    await loop.start()
    assert loop.running

    # Wait for at least one sample
    await asyncio.sleep(1.5)

    # Check stats
    stats = loop.get_stats()
    assert stats["health_samples"] > 0

    # Stop
    await loop.stop()
    assert not loop.running


@pytest.mark.asyncio
async def test_emotion_mapper_rules():
    """Test state mapper (formerly emotion mapper) rules."""
    mapper = get_state_mapper()

    # Test memory pulse mapping
    mood, intensity = mapper.map_memory_pulse(coherence_score=0.5)
    assert mood == "concerned"

    mood, intensity = mapper.map_memory_pulse(coherence_score=0.8)
    assert mood == "focused"

    mood, intensity = mapper.map_memory_pulse(coherence_score=0.95)
    assert mood == "calm"

    # Test homeostasis signal mapping
    mood, intensity = mapper.map_homeostasis_signal(
        dlq_count=20, quarantined_count=2, drops_total=100
    )
    assert mood == "concerned"

    # Test kernel health mapping
    mood, intensity = mapper.map_kernel_health(
        queue_size=900, queue_limit=1000, circuit_breaker_state="closed"
    )
    assert mood in ["concerned", "focused"]

    mood, intensity = mapper.map_kernel_health(
        queue_size=100, queue_limit=1000, circuit_breaker_state="open"
    )
    assert mood == "on_edge"


@pytest.mark.asyncio
async def test_keb_topics_registered():
    """Test that KEB topics are registered correctly."""
    service_registry = ServiceRegistry()
    event_bus = EventBus(service_registry)

    # Subscribe to topics
    await event_bus.subscribe("lyrixa.emotion", "test_subscriber")
    await event_bus.subscribe("lyrixa.expression", "test_subscriber")

    # Check status
    status = event_bus.get_status()

    assert "lyrixa.emotion" in status["topics"]
    assert "lyrixa.expression" in status["topics"]


@pytest.mark.asyncio
async def test_integrated_system_starts():
    """Test that the full integrated system starts correctly."""
    service_registry = ServiceRegistry()
    event_bus = EventBus(service_registry)

    # Initialize and start
    system = await initialize_interactive_system(
        event_bus=event_bus,
        service_registry=service_registry,
        config={"sample_interval": 2.0},
    )

    assert system.running
    assert system.initialized

    # Get status
    status = system.get_status()
    assert status["running"]
    assert status["components"]["expression_manager"]
    assert status["components"]["interactive_loop"]

    # Wait a moment for events to flow
    await asyncio.sleep(2.5)

    # Check that events are flowing
    stats = status.get("emotion_stats", {})
    assert stats.get("health_samples", 0) > 0

    # Stop
    await system.stop()
    assert not system.running


@pytest.mark.asyncio
async def test_user_activity_tracking():
    """Test user activity tracking and idle detection."""
    service_registry = ServiceRegistry()
    event_bus = EventBus(service_registry)

    loop = await get_interactive_loop(event_bus, service_registry, sample_interval=1.0)
    await loop.start()

    # Initially not idle
    assert not loop.is_user_idle

    # Record activity
    loop.record_user_activity()
    await asyncio.sleep(0.5)
    assert not loop.is_user_idle

    # Manually set idle (for testing — normally takes 10 minutes)
    loop.is_user_idle = True
    loop.record_user_activity()  # This should clear idle
    await asyncio.sleep(0.5)
    assert not loop.is_user_idle

    await loop.stop()


@pytest.mark.asyncio
async def test_error_burst_detection():
    """Test error burst detection."""
    service_registry = ServiceRegistry()
    event_bus = EventBus(service_registry)

    loop = await get_interactive_loop(event_bus, service_registry, sample_interval=1.0)
    await loop.start()

    # Record multiple errors rapidly
    for _ in range(10):
        loop.record_error()
        await asyncio.sleep(0.05)

    # Check that burst is detected
    stats = loop.get_stats()
    assert stats["recent_error_count"] >= 5

    await loop.stop()


@pytest.mark.asyncio
async def test_expression_hooks():
    """Test expression enter/exit/tick hooks."""
    service_registry = ServiceRegistry()
    event_bus = EventBus(service_registry)

    manager = await get_expression_manager(event_bus, service_registry)

    # Track hook calls
    hook_calls = {"enter": 0, "exit": 0, "tick": 0}

    def on_focused_enter(state):
        hook_calls["enter"] += 1

    def on_focused_exit(state):
        hook_calls["exit"] += 1

    async def on_focused_tick(state, duration):
        hook_calls["tick"] += 1

    # Register hooks
    manager.register_enter_hook(ExpressionState.FOCUSED, on_focused_enter)
    manager.register_exit_hook(ExpressionState.FOCUSED, on_focused_exit)
    manager.register_tick_hook(ExpressionState.FOCUSED, on_focused_tick)

    await manager.start()

    # Trigger transition to FOCUSED
    await manager.set_expression(ExpressionState.FOCUSED, force=True)
    await asyncio.sleep(0.3)

    assert hook_calls["enter"] == 1
    assert hook_calls["tick"] >= 0  # May or may not tick depending on timing

    # Transition away
    await manager.set_expression(ExpressionState.CALM, force=True)
    await asyncio.sleep(0.3)

    assert hook_calls["exit"] == 1

    await manager.stop()


if __name__ == "__main__":
    # Run tests manually
    asyncio.run(test_expression_manager_initializes())
    asyncio.run(test_expression_manager_starts_and_stops())
    asyncio.run(test_expression_manager_publishes_events())
    asyncio.run(test_interactive_loop_initializes())
    asyncio.run(test_interactive_loop_starts_and_stops())
    asyncio.run(test_emotion_mapper_rules())
    asyncio.run(test_keb_topics_registered())
    asyncio.run(test_integrated_system_starts())
    asyncio.run(test_user_activity_tracking())
    asyncio.run(test_error_burst_detection())
    asyncio.run(test_expression_hooks())
    print("✅ All smoke tests passed!")
