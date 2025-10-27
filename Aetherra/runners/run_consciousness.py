# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Consciousness Runner
====================

Standalone runner for the always-on consciousness system.
Real perception → felt experience → narrative continuity.
"""

from __future__ import annotations

import platform
import signal
import time

from Aetherra.consciousness.core import config
from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
from Aetherra.consciousness.health_checks import (
    HealthCheckEngine,
    build_default_checks,
)
from Aetherra.perception_bus.bus import PerceptionBus
from Aetherra.safety_envelope import REGISTRY, Actuator
from Aetherra.safety_envelope.policy_engine import PolicyEngine


def main() -> None:
    """Run the consciousness system."""
    print("=" * 70)
    print("🧠  Aetherra Consciousness System - Phase 1")
    print("=" * 70)
    print(f"Mode: {config.AUTONOMY_MODE}")
    print(f"Tick Rate: {config.TICK_HZ} Hz")
    print(f"Platform: {platform.system()}")
    print("=" * 70)
    print()

    # Initialize perception bus
    bus = PerceptionBus(maxlen=config.MAX_WORKING_MEMORY)

    # Start OS adapters based on platform
    if platform.system() == "Windows":
        print("🔌 Starting Windows perception adapters...")
        from Aetherra.perception_bus.adapters.windows import (
            WindowsDiskAdapter,
            WindowsEventLogAdapter,
            WindowsPerfAdapter,
            WindowsProcAdapter,
            WindowsServiceAdapter,
        )

        WindowsProcAdapter(bus).start()
        WindowsDiskAdapter(bus).start()
        WindowsEventLogAdapter(bus).start()
        WindowsPerfAdapter(bus).start()
        WindowsServiceAdapter(bus).start()

    elif platform.system() == "Linux":
        print("🔌 Starting Linux perception adapters...")
        from Aetherra.perception_bus.adapters.linux import (
            LinuxDiskAdapter,
            LinuxFSAdapter,
            LinuxJournalAdapter,
            LinuxProcAdapter,
            LinuxServiceAdapter,
        )

        LinuxProcAdapter(bus).start()
        LinuxDiskAdapter(bus).start()
        LinuxJournalAdapter(bus).start()
        LinuxFSAdapter(bus, watch_paths=["/etc", "/var/log"]).start()
        LinuxServiceAdapter(bus).start()

    else:
        print(f"⚠️  Warning: No adapters for platform: {platform.system()}")
        print("Running in sensor-limited mode...")

    # Initialize safety envelope (if actions enabled)
    safety_envelope = None
    if config.SAFETY_ENVELOPE_ENABLED and config.AUTONOMY_MODE != "observe":
        print(f"🛡️  Safety envelope enabled (mode: {config.AUTONOMY_MODE})")
        policy = PolicyEngine(mode=config.AUTONOMY_MODE)
        safety_envelope = Actuator(REGISTRY, policy)
    else:
        print("👁️  Observation mode only (no actions)")

    # Initialize consciousness core
    print("🧠 Initializing consciousness core...")
    core = ConsciousnessCore(bus, safety_envelope)

    # Wire ThinkStream to Hub API for UI visualization via HTTP
    hub_url = "http://localhost:3001"
    try:
        core.ui.register_hub_api(hub_url)
        print(f"🔗 ThinkStream wired to Hub API ({hub_url}/api/consciousness/update)")
    except Exception as e:
        print(f"⚠️  Could not wire ThinkStream to Hub: {e}")

    # ------------------------------------------------------------
    # Health Checks: boot-time sweep + periodic maintenance
    # ------------------------------------------------------------
    h_policy = PolicyEngine(mode=config.AUTONOMY_MODE)
    hce = HealthCheckEngine(h_policy, hub_base_url="http://127.0.0.1:3001")
    checks = build_default_checks(hce)

    print()
    print("🩺 Running boot-time health checks (low-risk)")
    for chk in checks:
        res = hce.run_check(chk)
        status = res.get("status")
        print(f"BOOT-CHECK [{chk.name}]: {status}")

    print()
    print("✅ Consciousness online. Press Ctrl+C to stop.")
    print("=" * 70)
    print()

    # Graceful shutdown handler
    shutdown_requested = False

    def signal_handler(sig, frame):
        nonlocal shutdown_requested
        print("\n\n⏸️  Shutdown requested...")
        shutdown_requested = True

    signal.signal(signal.SIGINT, signal_handler)

    # Main consciousness loop
    tick_interval = 1.0 / config.TICK_HZ
    last_hc_ts = 0.0

    try:
        while not shutdown_requested:
            tick_start = time.time()

            # Single consciousness tick
            core.tick()

            # Periodic health checks (~60s)
            now = time.time()
            if now - last_hc_ts > 60.0:
                for chk in checks:
                    res = hce.run_check(chk)
                    status = res.get("status")
                    print(f"HEALTH-CHECK [{chk.name}]: {status}")
                last_hc_ts = now

            # Adaptive sleep
            elapsed = time.time() - tick_start
            sleep_time = max(0.001, tick_interval - elapsed)
            time.sleep(sleep_time)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        return

    # Shutdown
    print("\n" + "=" * 70)
    print("📊 Final Statistics:")
    print("=" * 70)

    status = core.get_status()
    print(f"Uptime: {status['uptime_s'] / 60:.1f} minutes")
    print(f"Ticks: {status['tick']}")
    print(f"Events perceived: {status['total_events']}")
    print(f"Focuses: {status['total_focuses']}")
    print(f"Intents formed: {status['total_intents']}")
    print(f"Active intents: {status['active_intents']}")
    print()
    print("Qualia (final):")
    print(f"  Valence: {status['qualia']['valence']:+.3f}")
    print(f"  Arousal: {status['qualia']['arousal']:.3f}")
    print(f"  Certainty: {status['qualia']['certainty']:.3f}")
    print(f"  Curiosity: {status['qualia']['curiosity']:.3f}")

    if safety_envelope:
        print()
        print("Safety Envelope:")
        stats = safety_envelope.get_stats()
        print(f"  Actions: {stats['total_actions']}")
        print(f"  Success rate: {stats['success_rate_pct']:.1f}%")
        print(f"  Rollbacks: {stats['total_rollbacks']}")

    bus_stats = bus.get_stats()
    print()
    print("Perception Bus:")
    print(f"  Published: {bus_stats['total_published']}")
    print(f"  Dropped: {bus_stats['total_dropped']}")
    print(f"  Queue size: {bus_stats['queue_size']}")

    print()
    print("=" * 70)
    print("🌙 Consciousness offline. Goodbye.")
    print("=" * 70)


if __name__ == "__main__":
    main()
