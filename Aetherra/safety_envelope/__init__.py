# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Safety Envelope Module
======================

The gatekeeper between consciousness and world-changing actions.
Policy → Capabilities → Audit.
"""

from .actuator import Actuator
from .capability_registry import REGISTRY, Capability, CapabilityRegistry
from .policy_engine import PolicyDecision, PolicyEngine

__all__ = [
    "Actuator",
    "Capability",
    "CapabilityRegistry",
    "REGISTRY",
    "PolicyDecision",
    "PolicyEngine",
]
