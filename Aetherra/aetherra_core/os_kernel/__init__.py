# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Core OS Kernel Package
--------------------------------

Thin compatibility layer that exposes the OS kernel loop and HMR controller
from their current top-level modules. This enables modular imports like:

    from Aetherra.aetherra_core.os_kernel import AetherraKernelLoop, get_kernel
    from Aetherra.aetherra_core.os_kernel import HMRController, get_hmr_controller

without relocating files immediately. Later, implementations can be moved here
with no public API change.
"""

from .hmr_controller import HMRController, get_hmr_controller
from .kernel_loop import (
    AetherraKernelLoop,
    get_kernel,
    kernel_loop,
    shutdown_kernel,
    start_kernel,
)

__all__ = [
    "AetherraKernelLoop",
    "start_kernel",
    "shutdown_kernel",
    "get_kernel",
    "kernel_loop",
    "HMRController",
    "get_hmr_controller",
]
