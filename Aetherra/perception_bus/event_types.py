# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Perception Bus Event Types
==========================

Canonical event type constants for the perception system.
All types follow namespace.category pattern.
"""

# System health & services
SVC_HEALTH = "svc.health"
PROC_SNAPSHOT = "proc.snapshot"
FS_CHANGE = "fs.change"
NET_STATUS = "net.status"
DISK_STATUS = "disk.status"
ERR_LOG = "err.log"

# Aetherra internal
MEMORY_METRIC = "aeth.mem"
PLUGIN_EVENT = "aeth.plugin"
POLICY_EVENT = "aeth.policy"
CONSCIOUSNESS_EVENT = "aeth.consciousness"
SAFETY_EVENT = "aeth.safety"

# User interaction
USER_EVENT = "user.event"
USER_COMMAND = "user.command"

# Sensor health
SENSOR_OFFLINE = "sensor.offline"
SENSOR_ONLINE = "sensor.online"

# Performance metrics
PERF_CPU = "perf.cpu"
PERF_MEMORY = "perf.memory"
PERF_IO = "perf.io"
PERF_NETWORK = "perf.network"
