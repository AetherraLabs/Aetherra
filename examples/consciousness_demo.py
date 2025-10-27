#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Quick Consciousness Demo
========================

Demonstrates the consciousness system with custom event injection.
Shows how to wire external systems to the perception bus.
"""

import time

from Aetherra.consciousness.core import Event
from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
from Aetherra.consciousness.core.think_stream import get_think_stream
from Aetherra.perception_bus import get_perception_bus
from Aetherra.perception_bus.event_types import DISK_STATUS, PLUGIN_EVENT, USER_EVENT
from Aetherra.safety_envelope import REGISTRY, Actuator, PolicyEngine


def main():
    """Run a quick consciousness demo."""
    print("=" * 70)
    print("🧪 Consciousness System - Quick Demo")
    print("=" * 70)
    print()

    # Get the perception bus
    bus = get_perception_bus()

    # Set up a simple UI callback
    think_stream = get_think_stream()

    def ui_callback(state):
        """Simple console UI callback."""
        tick = state["tick"]
        q = state["qualia"]
        focuses = state["focuses"]
        intents = state["intentions"]

        print(f"\n[Tick {tick}]")
        print(
            f"  Qualia: v={q['valence']:+.2f} a={q['arousal']:.2f} c={q['certainty']:.2f} curiosity={q['curiosity']:.2f}"
        )
        if focuses:
            print(f"  Focuses: {[f['type'] for f in focuses[:3]]}")
        if intents:
            print(f"  Intents: {[i['goal'] for i in intents[:2]]}")
        if state["narrative"]:
            print(f"  💭 {state['narrative']}")

    think_stream.register_ui_callback(ui_callback)

    # Initialize safety envelope (observe mode - no actions)
    policy = PolicyEngine(mode="observe")
    actuator = Actuator(REGISTRY, policy)

    # Create consciousness core
    core = ConsciousnessCore(bus, actuator)

    print("✅ Consciousness initialized")
    print("📡 Injecting synthetic events to demonstrate awareness...")
    print()

    # Inject some interesting events
    bus.publish(
        Event(
            type=USER_EVENT,
            payload={"command": "hello", "user": "demo"},
            source="demo",
        )
    )

    bus.publish(
        Event(
            type=PLUGIN_EVENT,
            payload={"plugin": "test_plugin", "status": "loaded"},
            source="demo",
        )
    )

    # Simulate disk pressure to trigger intent formation
    bus.publish(
        Event(
            type=DISK_STATUS,
            payload={"mount": "C:", "pct_free": 5.2},  # Low disk!
            source="demo",
        )
    )

    # Run consciousness for 10 ticks
    print("🧠 Running consciousness loop (10 ticks)...")
    print()

    for i in range(10):
        core.tick()
        time.sleep(0.2)  # 5 Hz

        # Inject a mid-stream event
        if i == 5:
            bus.publish(
                Event(
                    type=USER_EVENT,
                    payload={"command": "check_health", "user": "demo"},
                    source="demo",
                )
            )

    # Show final status
    print()
    print("=" * 70)
    print("📊 Final Status:")
    print("=" * 70)
    status = core.get_status()
    print(f"Ticks: {status['tick']}")
    print(f"Events: {status['total_events']}")
    print(f"Focuses: {status['total_focuses']}")
    print(f"Intents: {status['total_intents']}")
    print(f"Active intents: {status['active_intents']}")
    print()
    print("Final Qualia:")
    q = status["qualia"]
    print(f"  Valence: {q['valence']:+.3f} (pleasure/displeasure)")
    print(f"  Arousal: {q['arousal']:.3f} (energy)")
    print(f"  Certainty: {q['certainty']:.3f} (confidence)")
    print(f"  Curiosity: {q['curiosity']:.3f} (exploration)")
    print()
    print("=" * 70)
    print("✅ Demo complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
