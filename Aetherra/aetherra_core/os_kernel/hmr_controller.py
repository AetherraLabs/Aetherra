# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Forwarder to the current HMR controller implementation.

This allows importing HMR APIs from Aetherra.aetherra_core.os_kernel without
moving the implementation yet.
"""

from aetherra_hmr_controller import HMRController, get_hmr_controller  # type: ignore

__all__ = [
    "HMRController",
    "get_hmr_controller",
]
