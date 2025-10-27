# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Consciousness Core Configuration
================================

Runtime parameters for the always-on consciousness loop.
Tuned for real-time awareness without overwhelming the system.
"""

import os

# Tick rate: 5–10 Hz typical; adaptive under load
TICK_HZ: float = float(os.getenv("AETHERRA_CONSCIOUSNESS_HZ", "5.0"))

# Working memory: max events to retain in recent buffer
MAX_WORKING_MEMORY: int = int(os.getenv("AETHERRA_WM_SIZE", "2048"))

# Attention: max focuses per tick
MAX_FOCUSES: int = int(os.getenv("AETHERRA_MAX_FOCUSES", "5"))

# Qualia decay factor (per tick)
QUALIA_DECAY: float = float(os.getenv("AETHERRA_QUALIA_DECAY", "0.95"))

# Autonomy mode: observe | assist | autopilot | emergency
AUTONOMY_MODE: str = os.getenv("AETHERRA_AUTONOMY_MODE", "observe")

# Narrative retention: max moments to keep in thread
MAX_NARRATIVE_MOMENTS: int = int(os.getenv("AETHERRA_NARRATIVE_SIZE", "1000"))

# Perception bus drain limit per tick
PERCEPTION_DRAIN_LIMIT: int = int(os.getenv("AETHERRA_PERCEPTION_DRAIN", "256"))

# Intent expiration: auto-expire intents after this many seconds if not executed
INTENT_DEFAULT_DEADLINE_S: int = int(os.getenv("AETHERRA_INTENT_DEADLINE", "600"))  # 10 minutes

# Reflection cycle: micro-reflection every tick, macro-reflection every N ticks
MACRO_REFLECTION_INTERVAL: int = int(
    os.getenv("AETHERRA_MACRO_REFLECT_INTERVAL", "1200")
)  # ~4 min at 5 Hz

# QFAC integration: store episodic moments to QFAC
ENABLE_QFAC_PERSISTENCE: bool = os.getenv("AETHERRA_QFAC_PERSISTENCE", "1") == "1"

# Telemetry: emit metrics to observability stack
ENABLE_TELEMETRY: bool = os.getenv("AETHERRA_CONSCIOUSNESS_TELEMETRY", "1") == "1"

# Safety envelope: always active, but can be in read-only mode
SAFETY_ENVELOPE_ENABLED: bool = os.getenv("AETHERRA_SAFETY_ENVELOPE", "1") == "1"

# Debug: verbose consciousness logging
DEBUG_CONSCIOUSNESS: bool = os.getenv("AETHERRA_DEBUG_CONSCIOUSNESS", "0") == "1"
