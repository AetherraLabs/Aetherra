#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧬 Aetherra Homeostasis System
==============================

Autonomous system stability and equilibrium control for Aetherra OS.
Maintains all systems running and performing optimally through continuous
monitoring, feedback control, and adaptive corrections.

This system implements:
- Continuous sensing of system health metrics
- PID-based control loops for stability
- Automated actuations for drift correction
- Runlevel supervision for system availability
- Policy-based safety guardrails

Components:
- stability_metrics: Collects and aggregates system health signals
- homeostasis_core: PID controllers and control loop logic
- homeostasis_actuators: Idempotent system adjustment operations
- system_supervisor: Runlevel management and service monitoring
- Configurations: setpoints.yaml and homeostasis_policy.yaml

Author: Aetherra Labs
Copyright (C) 2025 AetherraLabs
Licensed under GNU General Public License v3.0
"""

from .homeostasis_actuators import HomeostasisActuators
from .homeostasis_core import HomeostasisController
from .diagnosis import build_diagnosis_report
from .learning import build_learning_report
from .observation import build_observation_report
from .recommendation import build_recommendation_report
from .stability_metrics import StabilityMetrics
from .system_supervisor import SystemSupervisor

__version__ = "1.0.0"
__all__ = [
    "HomeostasisController",
    "StabilityMetrics",
    "SystemSupervisor",
    "HomeostasisActuators",
    "build_diagnosis_report",
    "build_learning_report",
    "build_observation_report",
    "build_recommendation_report",
]
