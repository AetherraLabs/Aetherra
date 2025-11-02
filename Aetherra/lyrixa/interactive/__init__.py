#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
🌟 Lyrixa Interactive Module
============================

Isolated interactive behavior layer for Lyrixa.
Provides expression management, emotion mapping, and reactive behaviors
without coupling to core intelligence/cognition systems.

This module enables Lyrixa to express herself dynamically based on system
health while keeping her intelligence evolution separate from her expressions.

Core Components:
- ExpressionManager: FSM for visual/audio expression states
- InteractiveLoop: Health sampling and emotion event publishing
- StateMapper: Signal → emotion mapping from state_map.json

Integration:
- Subscribes to KEB topics for system signals
- Publishes lyrixa.expression events for UI/plugins
- Registers as background service with restart-on-crash
- Hooks into Maintenance System for degraded-mode behavior

Configuration:
- state_map.json: All mapping rules and thresholds
- Feature flag: AETHERRA_INTERACTIVE (default: 1, enabled for development)
- Can be disabled with AETHERRA_INTERACTIVE=0 if needed for debugging
"""

from .expression_manager import ExpressionManager, ExpressionState
from .integration import InteractiveSystem, get_interactive_system
from .interactive_loop import InteractiveLoop
from .state_mapper import StateMapper, get_state_mapper

__all__ = [
    "ExpressionManager",
    "ExpressionState",
    "InteractiveLoop",
    "InteractiveSystem",
    "StateMapper",
    "get_state_mapper",
    "initialize_interactive_system",
    "get_interactive_system",
]


async def initialize_interactive_system(event_bus, service_registry, config=None):
    """
    Initialize and start the Interactive Lyrixa system.

    This is the primary entry point for OS launcher integration.

    Args:
        event_bus: Kernel Event Bus instance
        service_registry: Service registry for component discovery
        config: Optional configuration overrides

    Returns:
        InteractiveSystem instance
    """
    system = await get_interactive_system(
        event_bus=event_bus, service_registry=service_registry, config=config
    )
    await system.initialize()
    await system.start()

    return system
