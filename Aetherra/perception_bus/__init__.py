# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Perception Bus Module
====================

Real-world sensory substrate for consciousness.
No simulation—only actual OS telemetry.
"""

from .bus import PerceptionBus, get_perception_bus
from .event_types import (
    CONSCIOUSNESS_EVENT,
    DISK_STATUS,
    ERR_LOG,
    FS_CHANGE,
    MEMORY_METRIC,
    NET_STATUS,
    PERF_CPU,
    PERF_IO,
    PERF_MEMORY,
    PERF_NETWORK,
    PLUGIN_EVENT,
    POLICY_EVENT,
    PROC_SNAPSHOT,
    SAFETY_EVENT,
    SENSOR_OFFLINE,
    SENSOR_ONLINE,
    SVC_HEALTH,
    USER_COMMAND,
    USER_EVENT,
)

__all__ = [
    "PerceptionBus",
    "get_perception_bus",
    # Event types
    "CONSCIOUSNESS_EVENT",
    "DISK_STATUS",
    "ERR_LOG",
    "FS_CHANGE",
    "MEMORY_METRIC",
    "NET_STATUS",
    "PERF_CPU",
    "PERF_IO",
    "PERF_MEMORY",
    "PERF_NETWORK",
    "PLUGIN_EVENT",
    "POLICY_EVENT",
    "PROC_SNAPSHOT",
    "SAFETY_EVENT",
    "SENSOR_OFFLINE",
    "SENSOR_ONLINE",
    "SVC_HEALTH",
    "USER_COMMAND",
    "USER_EVENT",
]
