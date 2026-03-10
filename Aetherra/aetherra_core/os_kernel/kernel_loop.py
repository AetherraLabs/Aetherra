# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Forwarder to the current OS kernel loop implementation.

This preserves public APIs while we incrementally migrate implementation files.
"""

# Aetherra imports
from aetherra_kernel_loop import (
    AetherraKernelLoop,  # type: ignore
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
]
