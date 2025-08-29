"""Forwarder to the current OS kernel loop implementation.

This preserves public APIs while we incrementally migrate implementation files.
"""

from aetherra_kernel_loop import (  # type: ignore
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
]
