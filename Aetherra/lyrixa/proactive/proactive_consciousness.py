#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Proactive Consciousness for Lyrixa Chat
=======================================

Monitors user and system state to provide anticipatory assistance.
This is a lightweight, non-blocking service that integrates with the
chat service to surface hints.
"""

from __future__ import annotations

# Standard library imports
import asyncio
from collections import deque
from typing import Any, Deque, Dict, List, Optional

# Use the same chat-focused bridge as the main service
try:
    # Aetherra imports
    from Aetherra.quantum.chat_consciousness_bridge import (
        ChatConsciousnessBridge as QuantumChatBridge,
    )
except Exception:
    QuantumChatBridge = None  # type: ignore

# Use the kernel event bus for system-wide events
try:
    # Aetherra imports
    from aetherra_event_bus import get_event_bus
except Exception:
    get_event_bus = None


class ProactiveConsciousness:
    def __init__(
        self,
        bridge: Optional[QuantumChatBridge] = None,
        config: Optional[Dict[str, Any]] = None,
        service_registry=None,
    ):
        self._config = config or {}
        self._bridge = (
            bridge if bridge else (QuantumChatBridge() if QuantumChatBridge else None)
        )
        self._event_bus = None
        self._service_registry = service_registry
        self._monitor_task: Optional[asyncio.Task] = None
        self._last_suggestions: List[Dict[str, Any]] = []
        self._recent_events: Deque[Dict[str, Any]] = deque(maxlen=50)
        self._coherence_history: Deque[float] = deque(maxlen=10)

    async def start_monitoring(self):
        """Start the background monitoring task and subscribe to events."""
        if not self._bridge or self._monitor_task:
            return

        if get_event_bus and self._service_registry:
            try:
                self._event_bus = await get_event_bus(self._service_registry)
                # Subscribe to relevant topics
                await self._event_bus.subscribe(
                    "workspace.file.modified", "proactive_consciousness"
                )
                await self._event_bus.subscribe(
                    "terminal.command.executed", "proactive_consciousness"
                )
                await self._event_bus.subscribe(
                    "test.run.completed", "proactive_consciousness"
                )
            except Exception:
                self._event_bus = None  # Degrade gracefully

        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self):
        """Stop the background monitoring task."""
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        self._monitor_task = None

    async def handle_event(self, event: Dict[str, Any]):
        """Handle an incoming event from the event bus."""
        self._recent_events.append(event)

    async def get_proactive_suggestions(self) -> List[Dict[str, Any]]:
        """Return the latest cached proactive suggestions."""
        return self._last_suggestions

    async def _monitor_loop(self):
        """Periodically check for proactive opportunities."""
        interval = int(self._config.get("proactive_check_interval_sec", 30))
        while True:
            try:
                await self._run_proactive_checks()
            except Exception:
                # Never let the monitor loop die
                pass
            await asyncio.sleep(interval)

    async def _run_proactive_checks(self):
        """Run all proactive checks and update cached suggestions."""
        if not self._bridge:
            return

        # 1. Quantum Field Monitoring (Coherence Trend)
        field_hints = await self._monitor_quantum_field()

        # 2. Consciousness Check-in (Suggest optimizations)
        check_in_hints = await self._consciousness_check_in()

        # 3. Analyze recent user intent from events
        intent_hints = await self._analyze_user_intent()

        # Combine and cache, removing duplicates
        all_hints = field_hints + check_in_hints + intent_hints
        unique_hints = []
        seen_titles = set()
        for hint in all_hints:
            if hint.get("title") not in seen_titles:
                unique_hints.append(hint)
                seen_titles.add(hint.get("title"))
        self._last_suggestions = unique_hints

    async def _monitor_quantum_field(self) -> List[Dict[str, Any]]:
        """
        Analyzes coherence trends to predict user needs.
        """
        if not self._bridge:
            return []

        try:
            snap = await self._bridge.synchronize_consciousness()
            coherence = snap.get("coherence", 0.7) if snap else 0.7
            self._coherence_history.append(coherence)

            if len(self._coherence_history) < 5:
                return []  # Not enough data for a trend

            # Simple trend detection: check if the last 3 values are lower than the average of the last 10
            avg_coherence = sum(self._coherence_history) / len(self._coherence_history)
            recent_slice = list(self._coherence_history)[-3:]

            if all(c < avg_coherence * 0.9 for c in recent_slice):  # 10% drop
                return [
                    {
                        "type": "proactive_assistance",
                        "source": "quantum_field_monitor",
                        "title": "Declining Coherence Detected",
                        "suggestion": f"System coherence is trending down (current: {coherence:.2f}, avg: {avg_coherence:.2f}). This can happen when switching contexts frequently. Consider focusing on a single task to improve performance.",
                        "confidence": 0.85,
                    }
                ]
        except Exception:
            return []
        return []

    async def _consciousness_check_in(self) -> List[Dict[str, Any]]:
        """
        Suggests optimizations based on (simulated) usage patterns.
        """
        # This is a placeholder. A real implementation would analyze logs
        # or memory patterns.
        return [
            {
                "type": "proactive_assistance",
                "source": "consciousness_check_in",
                "title": "Optimization Suggestion",
                "suggestion": "I've noticed we often work with '.py' files. Would you like to run the 'Aether Verify' task to check for issues?",
                "confidence": 0.75,
                "action": {
                    "type": "run_task",
                    "task_id": "Aether Verify (Quick, Test Profile)",
                },
            }
        ]

    async def _analyze_user_intent(self) -> List[Dict[str, Any]]:
        """
        Analyzes recent events from the event bus to infer intent.
        """
        if not self._recent_events:
            return []

        suggestions = []

        # Check for recent test runs
        test_events = [
            e for e in self._recent_events if e.get("topic") == "test.run.completed"
        ]
        if test_events:
            last_test = test_events[-1]
            status = last_test.get("data", {}).get("status", "unknown")
            suggestion_text = f"I noticed a test run completed with status: {status}. "
            if status == "passed":
                suggestion_text += "Ready to commit the changes?"
                actions = [
                    {
                        "label": "Commit Changes",
                        "type": "command",
                        "command_id": "git.commit",
                    }
                ]
            else:
                suggestion_text += (
                    "Would you like to view the test logs or re-run the failed tests?"
                )
                actions = [
                    {
                        "label": "View Logs",
                        "type": "command",
                        "command_id": "testing.showoutput",
                    },
                    {
                        "label": "Re-run Failed",
                        "type": "command",
                        "command_id": "testing.rerunFailed",
                    },
                ]

            suggestions.append(
                {
                    "type": "proactive_assistance",
                    "source": "user_intent_analyzer",
                    "title": "Testing Workflow Detected",
                    "suggestion": suggestion_text,
                    "confidence": 0.9,
                    "actions": actions,
                }
            )

        # Check for file modifications followed by related commands
        py_mods = [
            e
            for e in self._recent_events
            if e.get("topic") == "workspace.file.modified"
            and e.get("data", {}).get("path", "").endswith(".py")
        ]
        if py_mods:
            suggestions.append(
                {
                    "type": "proactive_assistance",
                    "source": "user_intent_analyzer",
                    "title": "Code Change Detected",
                    "suggestion": f"I see you've modified {py_mods[-1].get('data', {}).get('path')}. Would you like to run associated tests or lint the file?",
                    "confidence": 0.8,
                    "actions": [
                        {
                            "label": "Run Tests",
                            "type": "command",
                            "command_id": "testing.runAll",
                        },
                        {
                            "label": "Lint File",
                            "type": "command",
                            "command_id": "eslint.executeAutofix",
                        },
                    ],
                }
            )

        # Clear events after processing to avoid re-suggesting
        self._recent_events.clear()

        return suggestions
